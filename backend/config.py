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

# =============================================================================
# ACTIVE SPORTS ONLY - PAUSED sports commented out to reduce API usage
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
    # Basketball - Odds API format
    "BASKETBALL_NBA": "basketball_nba",
    "BASKETBALL_NCAAB": "basketball_ncaab",

    # Hockey - short format
    "NHL": "icehockey_nhl",
    # Hockey - Odds API format
    "ICEHOCKEY_NHL": "icehockey_nhl",

    # Soccer - short format (EPL only)
    "EPL": "soccer_epl",
    # Soccer - Odds API format
    "SOCCER_EPL": "soccer_epl",

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

    # ==========================================================================
    # PAUSED SPORTS - Re-enable when in season or budget allows
    # ==========================================================================

    # PAUSED: Basketball
    # "WNBA": "basketball_wnba",
    # "EUROLEAGUE": "basketball_euroleague",
    # "BASKETBALL_WNBA": "basketball_wnba",
    # "BASKETBALL_EUROLEAGUE": "basketball_euroleague",

    # PAUSED: Hockey
    # "AHL": "icehockey_ahl",
    # "SHL": "icehockey_sweden_hockey_league",
    # "LIIGA": "icehockey_liiga",
    # "ICEHOCKEY_AHL": "icehockey_ahl",
    # "ICEHOCKEY_SWEDEN_HOCKEY_LEAGUE": "icehockey_sweden_hockey_league",
    # "ICEHOCKEY_LIIGA": "icehockey_liiga",

    # PAUSED: Baseball
    # "MLB": "baseball_mlb",
    # "BASEBALL_MLB": "baseball_mlb",

    # PAUSED: Soccer (all except EPL)
    # "MLS": "soccer_usa_mls",
    # "LA_LIGA": "soccer_spain_la_liga",
    # "BUNDESLIGA": "soccer_germany_bundesliga",
    # "SERIE_A": "soccer_italy_serie_a",
    # "LIGUE_1": "soccer_france_ligue_one",
    # "UCL": "soccer_uefa_champs_league",
    # "EUROPA": "soccer_uefa_europa_league",
    # "EFL_CHAMP": "soccer_efl_champ",
    # "EREDIVISIE": "soccer_netherlands_eredivisie",
    # "LIGA_MX": "soccer_mexico_ligamx",
    # "FA_CUP": "soccer_fa_cup",
    # "SOCCER_USA_MLS": "soccer_usa_mls",
    # "SOCCER_SPAIN_LA_LIGA": "soccer_spain_la_liga",
    # "SOCCER_GERMANY_BUNDESLIGA": "soccer_germany_bundesliga",
    # "SOCCER_ITALY_SERIE_A": "soccer_italy_serie_a",
    # "SOCCER_FRANCE_LIGUE_ONE": "soccer_france_ligue_one",
    # "SOCCER_UEFA_CHAMPS_LEAGUE": "soccer_uefa_champs_league",
    # "SOCCER_UEFA_EUROPA_LEAGUE": "soccer_uefa_europa_league",
    # "SOCCER_EFL_CHAMP": "soccer_efl_champ",
    # "SOCCER_NETHERLANDS_EREDIVISIE": "soccer_netherlands_eredivisie",
    # "SOCCER_MEXICO_LIGAMX": "soccer_mexico_ligamx",
    # "SOCCER_FA_CUP": "soccer_fa_cup",
    # "SOCCER_ENGLAND_LEAGUE1": "soccer_england_league1",
    # "SOCCER_ENGLAND_EFL_CUP": "soccer_england_efl_cup",
    # "SOCCER_ENGLAND_LEAGUE2": "soccer_england_league2",
    # "SOCCER_ENGLAND_EFL_CHAMP": "soccer_england_efl_champ",

    # PAUSED: Golf
    # "MASTERS": "golf_masters_tournament_winner",
    # "PGA_CHAMP": "golf_pga_championship_winner",
    # "US_OPEN": "golf_us_open_winner",
    # "THE_OPEN": "golf_the_open_championship_winner",
    # "GOLF_MASTERS_TOURNAMENT_WINNER": "golf_masters_tournament_winner",
    # "GOLF_PGA_CHAMPIONSHIP_WINNER": "golf_pga_championship_winner",
    # "GOLF_US_OPEN_WINNER": "golf_us_open_winner",
    # "GOLF_THE_OPEN_CHAMPIONSHIP_WINNER": "golf_the_open_championship_winner",

    # PAUSED: Combat Sports
    # "MMA": "mma_mixed_martial_arts",
    # "BOXING": "boxing_boxing",
    # "MMA_MIXED_MARTIAL_ARTS": "mma_mixed_martial_arts",
    # "BOXING_BOXING": "boxing_boxing",

    # PAUSED: Other
    # "NRL": "rugbyleague_nrl",
    # "AFL": "aussierules_afl",
    # "IPL": "cricket_ipl",
    # "BIG_BASH": "cricket_big_bash",
    # "RUGBYLEAGUE_NRL": "rugbyleague_nrl",
    # "AUSSIERULES_AFL": "aussierules_afl",
    # "CRICKET_IPL": "cricket_ipl",
    # "CRICKET_BIG_BASH": "cricket_big_bash",
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
    # Additional Odds API format - English lower leagues
    "soccer_england_efl_champ": ("soccer", "eng.2"),  # Championship
    "soccer_england_league1": ("soccer", "eng.3"),
    "soccer_england_league2": ("soccer", "eng.4"),
    "soccer_england_efl_cup": ("soccer", "eng.league_cup"),

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
# PILLAR WEIGHTS - Sport-Specific (will be tuned by accuracy tracking)
# =============================================================================

# Sport-specific pillar weights - each set must sum to 1.0
SPORT_WEIGHTS = {
    "NBA": {
        "execution": 0.20,       # Injuries matter but deep rosters
        "incentives": 0.10,      # Load management, tank positioning
        "shocks": 0.20,          # Line moves meaningful
        "time_decay": 0.20,      # Back-to-backs, travel huge
        "flow": 0.20,            # Sharp action on spreads
        "game_environment": 0.10, # Pace matchups
    },
    "NCAAB": {
        "execution": 0.15,       # Smaller rosters, injuries matter
        "incentives": 0.15,      # Conference play, bubble teams
        "shocks": 0.25,          # Inefficient market, steam moves
        "time_decay": 0.10,      # Less grueling schedule
        "flow": 0.25,            # Public money fades valuable
        "game_environment": 0.10, # Tempo matchups
    },
    "NFL": {
        "execution": 0.15,       # Key injuries (QB) massive
        "incentives": 0.15,      # Playoff seeding, division games
        "shocks": 0.25,          # News breaks, injury reports
        "time_decay": 0.05,      # Weekly schedule, less relevant
        "flow": 0.25,            # Sharp money very meaningful
        "game_environment": 0.15, # Weather, dome vs outdoor
    },
    "NCAAF": {
        "execution": 0.15,       # Transfer portal, key players
        "incentives": 0.15,      # Rivalry games, bowl eligibility
        "shocks": 0.25,          # Injury news, starter changes
        "time_decay": 0.10,      # Bye weeks matter
        "flow": 0.25,            # Public money on big names
        "game_environment": 0.10, # Weather effects
    },
    "NHL": {
        "execution": 0.15,       # Goalie starts crucial
        "incentives": 0.10,      # Playoff races
        "shocks": 0.25,          # Goalie announcements move lines
        "time_decay": 0.15,      # Back-to-backs, travel
        "flow": 0.25,            # Sharp money on totals
        "game_environment": 0.10, # Home ice advantage
    },
    "EPL": {
        "execution": 0.20,       # Squad rotation, injuries
        "incentives": 0.25,      # Relegation, European spots, derbies
        "shocks": 0.20,          # Lineup leaks, manager news
        "time_decay": 0.15,      # Midweek fixtures, cup runs
        "flow": 0.15,            # Less sharp action available
        "game_environment": 0.05, # Weather less impactful
    },
}

# Default fallback for unknown sports (original weights)
DEFAULT_WEIGHTS = {
    "execution": 0.20,
    "incentives": 0.10,
    "shocks": 0.25,
    "time_decay": 0.10,
    "flow": 0.25,
    "game_environment": 0.10,
}

# Legacy alias for backwards compatibility
PILLAR_WEIGHTS = DEFAULT_WEIGHTS

# =============================================================================
# MARKET-SPECIFIC WEIGHT ADJUSTMENTS
# =============================================================================
# Multipliers applied to base SPORT_WEIGHTS for each market type.
# Values > 1.0 increase importance, < 1.0 decrease importance.
# After applying, weights are re-normalized to sum to 1.0.

MARKET_ADJUSTMENTS = {
    "spread": {
        # Spread: Will favorite cover the point spread?
        # Balanced weights, slightly lower game_environment (margin less affected by pace)
        "execution": 1.0,
        "incentives": 1.0,
        "shocks": 1.0,
        "time_decay": 1.0,
        "flow": 1.0,
        "game_environment": 0.8,
    },
    "totals": {
        # Totals: Over or under the total?
        # Game environment is CRITICAL (pace, weather, expected scoring)
        # Execution matters for high-scoring player injuries
        # Incentives/time_decay less relevant to total points
        "execution": 0.8,
        "incentives": 0.6,
        "shocks": 0.9,
        "time_decay": 0.7,
        "flow": 0.8,
        "game_environment": 2.0,  # Highest - pace/weather critical for totals
    },
    "moneyline": {
        # Moneyline: Who wins straight up?
        # Execution amplified (no spread cushion, star injuries more impactful)
        # Game environment less important (just need to win)
        "execution": 1.2,
        "incentives": 1.1,
        "shocks": 1.0,
        "time_decay": 1.0,
        "flow": 1.0,
        "game_environment": 0.7,
    },
}

# =============================================================================
# PERIOD-SPECIFIC WEIGHT ADJUSTMENTS
# =============================================================================
# Multipliers applied to base weights for each game period.
# These capture how pillar importance changes throughout a game.

PERIOD_ADJUSTMENTS = {
    "full": {
        # Full game: baseline weights (no adjustment)
        "execution": 1.0,
        "incentives": 1.0,
        "shocks": 1.0,
        "time_decay": 1.0,
        "flow": 1.0,
        "game_environment": 1.0,
    },
    "h1": {
        # 1st Half: Starters play ~80%, opening schemes matter
        # Execution amplified (schemes, starters), Time decay minimal (fatigue hasn't set in)
        "execution": 1.5,
        "incentives": 0.8,
        "shocks": 0.9,
        "time_decay": 0.5,
        "flow": 0.8,
        "game_environment": 1.0,
    },
    "h2": {
        # 2nd Half: Fatigue compounds, coaching adjustments
        # Shocks higher (halftime adjustments reduce predictability)
        # Time decay higher (fatigue accumulates)
        "execution": 0.8,
        "incentives": 1.2,
        "shocks": 1.3,
        "time_decay": 1.5,
        "flow": 1.2,
        "game_environment": 1.0,
    },
    "q1": {
        # Q1: Highest correlation to talent/starters
        # Execution highest (opening schemes)
        # Time decay minimal, Flow less reliable (not enough data yet)
        "execution": 1.8,
        "incentives": 0.7,
        "shocks": 0.7,
        "time_decay": 0.3,
        "flow": 0.6,
        "game_environment": 1.2,
    },
    "q2": {
        # Q2: Rotation players enter, more variance
        # Execution drops (bench players), adjust for role player injuries
        "execution": 0.9,
        "incentives": 0.8,
        "shocks": 0.9,
        "time_decay": 0.5,
        "flow": 0.7,
        "game_environment": 1.0,
    },
    "q3": {
        # Q3: Halftime adjustments kick in
        # Shocks highest (teams come out differently)
        # Historical Q3 trends per team matter
        "execution": 0.9,
        "incentives": 1.0,
        "shocks": 1.5,
        "time_decay": 1.0,
        "flow": 1.0,
        "game_environment": 1.0,
    },
    "q4": {
        # Q4: Clutch factor, pace changes drastically
        # Incentives highest (desperation), Time decay highest (fatigue)
        # Execution drops if blowout (stars rest)
        # Game env volatile (intentional fouling affects totals)
        "execution": 0.7,
        "incentives": 1.5,
        "shocks": 1.2,
        "time_decay": 1.8,
        "flow": 1.3,
        "game_environment": 1.3,
    },
    # Hockey periods (for NHL)
    "p1": {
        # 1st Period: Similar to Q1
        "execution": 1.6,
        "incentives": 0.8,
        "shocks": 0.8,
        "time_decay": 0.4,
        "flow": 0.7,
        "game_environment": 1.1,
    },
    "p2": {
        # 2nd Period: Middle period, adjustments made
        "execution": 1.0,
        "incentives": 1.0,
        "shocks": 1.2,
        "time_decay": 1.0,
        "flow": 1.0,
        "game_environment": 1.0,
    },
    "p3": {
        # 3rd Period: Clutch, pulling goalies
        "execution": 0.8,
        "incentives": 1.4,
        "shocks": 1.3,
        "time_decay": 1.5,
        "flow": 1.2,
        "game_environment": 1.2,
    },
}

# =============================================================================
# SPORT PERIOD AVAILABILITY
# =============================================================================
# Which periods are valid for each sport (used to generate all combinations)

SPORT_PERIOD_AVAILABILITY = {
    "NBA": ["full", "h1", "h2", "q1", "q2", "q3", "q4"],
    "NCAAB": ["full", "h1", "h2"],  # College basketball uses halves
    "NFL": ["full", "h1", "h2", "q1", "q2", "q3", "q4"],
    "NCAAF": ["full", "h1", "h2", "q1", "q2", "q3", "q4"],
    "NHL": ["full", "p1", "p2", "p3"],  # Hockey uses periods
    "EPL": ["full", "h1", "h2"],  # Soccer uses halves only
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