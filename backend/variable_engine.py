"""
OMI Terminal Variable Engine
63 variables across 6 pillars + CEQ layer
Each variable returns a normalized score (0.0 to 1.0) and raw value

Phase 1: Architecture + variables implementable with existing data.
Includes official catalog variables (FDR, SRI, LSI, TSM, WXS, SLD, EWE, EDL, JFI, PTI, HCA)
with specific market-inefficiency theses.
Importable by composite_tracker and analyzer.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime, timezone, timedelta
import logging
import math

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# DATACLASSES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class VariableResult:
    """Result of a single variable calculation"""
    code: str           # e.g., "FDR", "SRI", "DPP"
    name: str           # e.g., "Fourth Quarter Differential Rating"
    pillar: str         # e.g., "EXECUTION", "INCENTIVES"
    raw_value: float    # Raw calculated value
    normalized: float   # 0.0 to 1.0 normalized score
    confidence: float   # 0.0 to 1.0 how confident we are in this data
    available: bool     # Whether we had data to calculate this
    source: str         # Data source used


@dataclass
class PillarScore:
    """Aggregated pillar score from multiple variables"""
    pillar: str
    score: float        # 0.0 to 1.0
    weight: float       # Dynamic weight for this game context
    variables: List[VariableResult] = field(default_factory=list)


@dataclass
class GameContext:
    """Context for dynamic weight calculation"""
    sport: str          # NBA, NCAAB, NFL, NHL, EPL
    market: str         # spread, total, ml
    significance: str   # regular, rivalry, playoff, elimination
    time_to_game_hours: float
    is_nationally_televised: bool
    conference_tier: str  # power5, mid_major, etc.
    has_exchange_data: bool
    has_weather_data: bool


# ═══════════════════════════════════════════════════════════════════════
# DYNAMIC WEIGHT ENGINE
# ═══════════════════════════════════════════════════════════════════════

# Base weights by sport (sum to 1.0 each)
SPORT_BASE_WEIGHTS = {
    "NBA":   {"EXECUTION": 0.25, "INCENTIVES": 0.05, "SHOCKS": 0.20, "TIME_DECAY": 0.10, "FLOW": 0.30, "GAME_ENV": 0.10},
    "NCAAB": {"EXECUTION": 0.20, "INCENTIVES": 0.10, "SHOCKS": 0.30, "TIME_DECAY": 0.10, "FLOW": 0.15, "GAME_ENV": 0.15},
    "NFL":   {"EXECUTION": 0.20, "INCENTIVES": 0.15, "SHOCKS": 0.25, "TIME_DECAY": 0.10, "FLOW": 0.20, "GAME_ENV": 0.10},
    "NCAAF": {"EXECUTION": 0.20, "INCENTIVES": 0.15, "SHOCKS": 0.25, "TIME_DECAY": 0.10, "FLOW": 0.20, "GAME_ENV": 0.10},
    "NHL":   {"EXECUTION": 0.20, "INCENTIVES": 0.10, "SHOCKS": 0.25, "TIME_DECAY": 0.10, "FLOW": 0.25, "GAME_ENV": 0.10},
    "EPL":   {"EXECUTION": 0.20, "INCENTIVES": 0.15, "SHOCKS": 0.20, "TIME_DECAY": 0.10, "FLOW": 0.25, "GAME_ENV": 0.10},
}


def _load_db_weights(sport: str) -> Optional[Dict[str, float]]:
    """Load raw learned pillar weights from calibration_config.
    Returns UPPERCASE-keyed dict or None on miss/error.
    Uses _fetch_db_weights (not get_effective_weights) to avoid double-applying
    market/period adjustments — variable_engine applies its own context multipliers."""
    try:
        from engine.weight_calculator import _fetch_db_weights
        db_weights = _fetch_db_weights(sport)
        if db_weights:
            # weight_calculator uses lowercase keys; variable_engine uses UPPERCASE
            mapped = {k.upper(): v for k, v in db_weights.items()}
            # Rename game_environment → GAME_ENV to match our convention
            if "GAME_ENVIRONMENT" in mapped:
                mapped["GAME_ENV"] = mapped.pop("GAME_ENVIRONMENT")
            # Validate all 6 keys present
            required = {"EXECUTION", "INCENTIVES", "SHOCKS", "TIME_DECAY", "FLOW", "GAME_ENV"}
            if required.issubset(mapped.keys()):
                logger.debug(f"[VarEngine] Using DB-backed weights for {sport}: {mapped}")
                return mapped
    except Exception as e:
        logger.debug(f"[VarEngine] DB weight lookup failed for {sport}: {e}")
    return None


def calculate_dynamic_weights(context: GameContext) -> Dict[str, float]:
    """Calculate context-sensitive pillar weights.
    Loads learned weights from DB first; falls back to hardcoded SPORT_BASE_WEIGHTS."""
    # Try DB-backed weights first (written by feedback loop)
    db_weights = _load_db_weights(context.sport)
    base = db_weights if db_weights else SPORT_BASE_WEIGHTS.get(context.sport, SPORT_BASE_WEIGHTS["NBA"])
    weights = base.copy()

    # Market type adjustments
    if context.market == "total":
        weights["GAME_ENV"] *= 1.5    # Weather/pace matters more for totals
        weights["FLOW"] *= 0.8
    elif context.market == "ml":
        weights["EXECUTION"] *= 1.3   # Form matters most for outright winner

    # Game significance
    if context.significance == "playoff":
        weights["INCENTIVES"] *= 2.0
        weights["TIME_DECAY"] *= 0.5
    elif context.significance == "rivalry":
        weights["INCENTIVES"] *= 1.5
    elif context.significance == "elimination":
        weights["INCENTIVES"] *= 2.5
        weights["EXECUTION"] *= 1.3

    # Time to game
    if context.time_to_game_hours < 3:
        weights["SHOCKS"] *= 1.5      # Late shocks matter more close to game
        weights["TIME_DECAY"] *= 0.3
    elif context.time_to_game_hours > 72:
        weights["TIME_DECAY"] *= 2.0  # Early lines have more decay

    # Data availability
    if context.has_exchange_data:
        weights["FLOW"] *= 1.2
    else:
        weights["FLOW"] *= 0.7

    if context.has_weather_data:
        weights["GAME_ENV"] *= 1.3

    # Conference tier (NCAAB specific)
    if context.sport == "NCAAB" and context.conference_tier == "mid_major":
        weights["SHOCKS"] *= 1.3      # One injury destroys a small roster
        weights["FLOW"] *= 0.5        # No sharp money on these games

    # Normalize to sum to 1.0
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


# ═══════════════════════════════════════════════════════════════════════
# VARIABLE DEFINITIONS — 63 variables across 6 pillars
# ═══════════════════════════════════════════════════════════════════════

# Each variable is defined with:
#   code, name, pillar, calculator function name, data source

VARIABLE_REGISTRY: List[Dict] = [
    # ─── EXECUTION (9 variables) ───
    {"code": "HIJ", "name": "Home Injury Impact",         "pillar": "EXECUTION",  "source": "espn_injuries"},
    {"code": "AIJ", "name": "Away Injury Impact",         "pillar": "EXECUTION",  "source": "espn_injuries"},
    {"code": "QBS", "name": "Quarterback Status",         "pillar": "EXECUTION",  "source": "espn_injuries"},
    {"code": "TSH", "name": "Team Strength Home",         "pillar": "EXECUTION",  "source": "team_stats"},
    {"code": "TSA", "name": "Team Strength Away",         "pillar": "EXECUTION",  "source": "team_stats"},
    {"code": "SKH", "name": "Streak Home",                "pillar": "EXECUTION",  "source": "team_stats"},
    {"code": "SKA", "name": "Streak Away",                "pillar": "EXECUTION",  "source": "team_stats"},
    {"code": "FRM", "name": "Form Rating",                "pillar": "EXECUTION",  "source": "team_stats"},
    {"code": "DPT", "name": "Roster Depth",               "pillar": "EXECUTION",  "source": "espn_injuries"},
    {"code": "FDR", "name": "Fourth Quarter Differential Rating", "pillar": "EXECUTION", "source": "espn_scores"},

    # ─── INCENTIVES (12 variables) ───
    {"code": "MTH", "name": "Motivation Home",            "pillar": "INCENTIVES", "source": "espn_standings"},
    {"code": "MTA", "name": "Motivation Away",            "pillar": "INCENTIVES", "source": "espn_standings"},
    {"code": "RIV", "name": "Rivalry Factor",             "pillar": "INCENTIVES", "source": "hardcoded_rivalries"},
    {"code": "CHP", "name": "Championship Significance",  "pillar": "INCENTIVES", "source": "espn_standings"},
    {"code": "PLF", "name": "Playoff Position",           "pillar": "INCENTIVES", "source": "espn_standings"},
    {"code": "TNK", "name": "Tank/Rest Alert",            "pillar": "INCENTIVES", "source": "espn_standings"},
    {"code": "SST", "name": "Season Stage",               "pillar": "INCENTIVES", "source": "game_time"},
    {"code": "UDG", "name": "Underdog Motivation",        "pillar": "INCENTIVES", "source": "consensus_odds"},
    {"code": "DVR", "name": "Divisional Rivalry",         "pillar": "INCENTIVES", "source": "hardcoded_rivalries"},
    {"code": "SRI", "name": "Schedule Rest Inequity",    "pillar": "INCENTIVES", "source": "espn_schedule"},
    {"code": "LSI", "name": "Letdown Spot Index",        "pillar": "INCENTIVES", "source": "espn_schedule"},
    {"code": "TSM", "name": "Trap Spot Multiplier",      "pillar": "INCENTIVES", "source": "cached_odds"},

    # ─── SHOCKS (9 variables) ───
    {"code": "LMM", "name": "Line Movement Magnitude",    "pillar": "SHOCKS",     "source": "line_snapshots"},
    {"code": "LMV", "name": "Line Movement Velocity",     "pillar": "SHOCKS",     "source": "line_snapshots"},
    {"code": "STM", "name": "Steam Move Detection",       "pillar": "SHOCKS",     "source": "line_snapshots"},
    {"code": "TMF", "name": "Time Factor",                "pillar": "SHOCKS",     "source": "line_snapshots"},
    {"code": "VOL", "name": "Volatility",                 "pillar": "SHOCKS",     "source": "line_snapshots"},
    {"code": "SHD", "name": "Shock Direction",            "pillar": "SHOCKS",     "source": "line_snapshots"},
    {"code": "OLN", "name": "Opening Line Displacement",  "pillar": "SHOCKS",     "source": "line_snapshots"},
    {"code": "LRS", "name": "Late Room Shopping",         "pillar": "SHOCKS",     "source": "line_snapshots"},
    {"code": "WXS", "name": "Weather Extreme Score",     "pillar": "SHOCKS",     "source": "open_meteo"},

    # ─── TIME_DECAY (10 variables) ───
    {"code": "HRD", "name": "Home Rest Days",             "pillar": "TIME_DECAY", "source": "espn_schedule"},
    {"code": "ARD", "name": "Away Rest Days",             "pillar": "TIME_DECAY", "source": "espn_schedule"},
    {"code": "B2B", "name": "Back-to-Back",               "pillar": "TIME_DECAY", "source": "espn_schedule"},
    {"code": "T3F", "name": "Third-in-Four",              "pillar": "TIME_DECAY", "source": "espn_schedule"},
    {"code": "TRV", "name": "Travel Distance",            "pillar": "TIME_DECAY", "source": "stadium_coords"},
    {"code": "HFA", "name": "Home Field Advantage",       "pillar": "TIME_DECAY", "source": "sport_config"},
    {"code": "MWK", "name": "Midweek Fatigue",            "pillar": "TIME_DECAY", "source": "game_time"},
    {"code": "MOM", "name": "Momentum Trend",             "pillar": "TIME_DECAY", "source": "team_stats"},
    {"code": "SLD", "name": "Stale Line Detector",       "pillar": "TIME_DECAY", "source": "line_snapshots"},
    {"code": "EWE", "name": "Early Week Edge",           "pillar": "TIME_DECAY", "source": "line_snapshots"},

    # ─── FLOW (11 variables) ───
    {"code": "PND", "name": "Pinnacle Divergence",        "pillar": "FLOW",       "source": "cached_odds"},
    {"code": "RTC", "name": "Retail Consensus",           "pillar": "FLOW",       "source": "cached_odds"},
    {"code": "BAG", "name": "Book Agreement",             "pillar": "FLOW",       "source": "cached_odds"},
    {"code": "RLM", "name": "Reverse Line Movement",      "pillar": "FLOW",       "source": "line_snapshots"},
    {"code": "FLM", "name": "Flow Line Movement",         "pillar": "FLOW",       "source": "line_snapshots"},
    {"code": "PDV", "name": "Price Divergence",           "pillar": "FLOW",       "source": "cached_odds"},
    {"code": "FVL", "name": "Flow Velocity",              "pillar": "FLOW",       "source": "line_snapshots"},
    {"code": "EXS", "name": "Exchange Signal",            "pillar": "FLOW",       "source": "exchange_data"},
    {"code": "SHP", "name": "Sharp Money Indicator",      "pillar": "FLOW",       "source": "cached_odds"},
    {"code": "EDL", "name": "Exchange-to-Book Lead Time","pillar": "FLOW",       "source": "exchange_data"},
    {"code": "JFI", "name": "Juice Flow Indicator",      "pillar": "FLOW",       "source": "cached_odds"},

    # ─── GAME_ENV (11 variables) ───
    {"code": "EXT", "name": "Expected Total",             "pillar": "GAME_ENV",   "source": "team_stats"},
    {"code": "PAC", "name": "Pace Factor",                "pillar": "GAME_ENV",   "source": "team_stats"},
    {"code": "ORT", "name": "Offensive Rating",           "pillar": "GAME_ENV",   "source": "team_stats"},
    {"code": "DRT", "name": "Defensive Rating",           "pillar": "GAME_ENV",   "source": "team_stats"},
    {"code": "SPT", "name": "Special Teams",              "pillar": "GAME_ENV",   "source": "team_stats"},
    {"code": "WTH", "name": "Weather Impact",             "pillar": "GAME_ENV",   "source": "open_meteo"},
    {"code": "PPG", "name": "Points Per Game Average",    "pillar": "GAME_ENV",   "source": "team_stats"},
    {"code": "VEN", "name": "Venue Factor",               "pillar": "GAME_ENV",   "source": "sport_config"},
    {"code": "GLS", "name": "Goals For/Against Rate",     "pillar": "GAME_ENV",   "source": "team_stats"},
    {"code": "PTI", "name": "Pace/Tempo Interaction",    "pillar": "GAME_ENV",   "source": "team_stats"},
    {"code": "HCA", "name": "Home Court Advantage",      "pillar": "GAME_ENV",   "source": "team_stats"},
]

assert len(VARIABLE_REGISTRY) == 63, f"Expected 63 variables, got {len(VARIABLE_REGISTRY)}"


# ═══════════════════════════════════════════════════════════════════════
# NORMALIZATION HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def _normalize_win_pct(win_pct: float) -> float:
    """Normalize win% (0-1 range already) — shift so .500 = 0.5."""
    return _clamp(win_pct)


def _normalize_streak(streak: int) -> float:
    """Normalize streak: +10 → 1.0, -10 → 0.0, 0 → 0.5."""
    return _clamp(0.5 + streak / 20.0)


def _normalize_rest_days(days: int, sport: str) -> float:
    """More rest → higher score. Sport-specific optimal rest."""
    if sport in ("NBA", "NCAAB", "NHL"):
        # 1 day = 0.2, 2 = 0.5, 3+ = 0.8+
        return _clamp(days / 5.0)
    else:
        # NFL/NCAAF: 7 = baseline, 10+ = advantage, <5 = short week
        return _clamp((days - 3) / 10.0)


def _normalize_injury_impact(impact: float) -> float:
    """Injury impact 0 = healthy, higher = more impacted.
    Invert so higher normalized = healthier team."""
    return _clamp(1.0 - impact)


def _normalize_line_movement(magnitude: float, sport: str) -> float:
    """Normalize line movement magnitude. Sport-specific thresholds."""
    thresholds = {
        "NBA": 3.0, "NCAAB": 4.0, "NFL": 3.0, "NCAAF": 3.5,
        "NHL": 1.0, "EPL": 0.5,
    }
    cap = thresholds.get(sport, 3.0)
    return _clamp(magnitude / cap)


def _normalize_velocity(velocity: float) -> float:
    """Velocity (pts/hr). >1.0 pts/hr is steam territory."""
    return _clamp(velocity / 2.0)


def _normalize_book_agreement(agreement: float) -> float:
    """Book agreement 0-1 already normalized."""
    return _clamp(agreement)


def _normalize_divergence(divergence: float) -> float:
    """Pinnacle divergence from consensus. Centered at 0.5, ±0.5 scale."""
    return _clamp(0.5 + divergence / 4.0)


def _normalize_pace(pace: float, sport: str) -> float:
    """Pace normalized relative to league average."""
    league_avg = {"NBA": 100.0, "NCAAB": 68.0}
    avg = league_avg.get(sport, 100.0)
    # ±15 range maps to 0-1
    return _clamp(0.5 + (pace - avg) / 30.0)


def _normalize_rating(rating: float, sport: str) -> float:
    """Offensive/defensive rating normalized."""
    league_avg = {"NBA": 112.0, "NCAAB": 100.0}
    avg = league_avg.get(sport, 110.0)
    return _clamp(0.5 + (rating - avg) / 20.0)


def _normalize_ppg(ppg: float, sport: str) -> float:
    """Points per game normalized relative to league average."""
    league_avg = {
        "NBA": 114.0, "NCAAB": 74.0, "NFL": 22.0,
        "NCAAF": 28.0, "NHL": 3.1, "EPL": 1.4,
    }
    ranges = {
        "NBA": 20.0, "NCAAB": 15.0, "NFL": 10.0,
        "NCAAF": 12.0, "NHL": 1.5, "EPL": 0.8,
    }
    avg = league_avg.get(sport, 22.0)
    rng = ranges.get(sport, 10.0)
    return _clamp(0.5 + (ppg - avg) / (2 * rng))


# ═══════════════════════════════════════════════════════════════════════
# VARIABLE CALCULATORS
# ═══════════════════════════════════════════════════════════════════════

def _stub_variable(code: str, name: str, pillar: str, source: str) -> VariableResult:
    """Return a neutral stub for variables we can't yet calculate."""
    return VariableResult(
        code=code, name=name, pillar=pillar,
        raw_value=0.0, normalized=0.5, confidence=0.0,
        available=False, source=source,
    )


def calculate_execution_variables(
    execution_result: dict,
    team_stats: Optional[dict] = None,
    sport: str = "NBA",
) -> List[VariableResult]:
    """Extract EXECUTION variables from existing execution pillar result."""
    variables = []

    # HIJ — Home Injury Impact
    hij_raw = execution_result.get("home_injury_impact", 0.0)
    variables.append(VariableResult(
        code="HIJ", name="Home Injury Impact", pillar="EXECUTION",
        raw_value=hij_raw, normalized=_normalize_injury_impact(hij_raw),
        confidence=0.7, available=True, source="espn_injuries",
    ))

    # AIJ — Away Injury Impact
    aij_raw = execution_result.get("away_injury_impact", 0.0)
    variables.append(VariableResult(
        code="AIJ", name="Away Injury Impact", pillar="EXECUTION",
        raw_value=aij_raw, normalized=_normalize_injury_impact(aij_raw),
        confidence=0.7, available=True, source="espn_injuries",
    ))

    # QBS — Quarterback Status (NFL/NCAAF only)
    if sport in ("NFL", "NCAAF"):
        breakdown = execution_result.get("breakdown", {})
        qb_impact = breakdown.get("qb_impact", 0.0) if breakdown else 0.0
        variables.append(VariableResult(
            code="QBS", name="Quarterback Status", pillar="EXECUTION",
            raw_value=qb_impact,
            normalized=_clamp(0.5 + qb_impact),  # qb_impact is a delta around 0
            confidence=0.8 if qb_impact != 0.0 else 0.3,
            available=qb_impact != 0.0, source="espn_injuries",
        ))
    else:
        variables.append(_stub_variable("QBS", "Quarterback Status", "EXECUTION", "espn_injuries"))

    # TSH — Team Strength Home (win%)
    home_stats = (team_stats or {}).get("home", {})
    away_stats = (team_stats or {}).get("away", {})

    home_wp = home_stats.get("win_pct")
    if home_wp is not None:
        variables.append(VariableResult(
            code="TSH", name="Team Strength Home", pillar="EXECUTION",
            raw_value=float(home_wp), normalized=_normalize_win_pct(float(home_wp)),
            confidence=0.8, available=True, source="team_stats",
        ))
    else:
        variables.append(_stub_variable("TSH", "Team Strength Home", "EXECUTION", "team_stats"))

    # TSA — Team Strength Away (win%)
    away_wp = away_stats.get("win_pct")
    if away_wp is not None:
        variables.append(VariableResult(
            code="TSA", name="Team Strength Away", pillar="EXECUTION",
            raw_value=float(away_wp), normalized=_normalize_win_pct(float(away_wp)),
            confidence=0.8, available=True, source="team_stats",
        ))
    else:
        variables.append(_stub_variable("TSA", "Team Strength Away", "EXECUTION", "team_stats"))

    # SKH — Streak Home
    home_streak = home_stats.get("streak")
    if home_streak is not None:
        streak_val = int(home_streak)
        variables.append(VariableResult(
            code="SKH", name="Streak Home", pillar="EXECUTION",
            raw_value=float(streak_val), normalized=_normalize_streak(streak_val),
            confidence=0.6, available=True, source="team_stats",
        ))
    else:
        variables.append(_stub_variable("SKH", "Streak Home", "EXECUTION", "team_stats"))

    # SKA — Streak Away
    away_streak = away_stats.get("streak")
    if away_streak is not None:
        streak_val = int(away_streak)
        variables.append(VariableResult(
            code="SKA", name="Streak Away", pillar="EXECUTION",
            raw_value=float(streak_val), normalized=_normalize_streak(streak_val),
            confidence=0.6, available=True, source="team_stats",
        ))
    else:
        variables.append(_stub_variable("SKA", "Streak Away", "EXECUTION", "team_stats"))

    # FRM — Form Rating (derived from execution score itself)
    exec_score = execution_result.get("score", 0.5)
    variables.append(VariableResult(
        code="FRM", name="Form Rating", pillar="EXECUTION",
        raw_value=exec_score, normalized=_clamp(exec_score),
        confidence=0.6, available=True, source="execution_pillar",
    ))

    # DPT — Roster Depth (stub — need deeper injury data)
    variables.append(_stub_variable("DPT", "Roster Depth", "EXECUTION", "espn_injuries"))

    # FDR — Fourth Quarter Differential Rating
    # Thesis: Q4 scoring differential reveals clutch execution ability.
    # Needs ESPN quarter-by-quarter scores from game_results — stub for now.
    variables.append(_stub_variable("FDR", "Fourth Quarter Differential Rating", "EXECUTION", "espn_scores"))

    return variables


def calculate_incentives_variables(
    incentives_result: dict,
    sport: str = "NBA",
    time_decay_result: Optional[dict] = None,
    current_spread: Optional[float] = None,
) -> List[VariableResult]:
    """Extract INCENTIVES variables from existing incentives pillar result."""
    variables = []
    breakdown = incentives_result.get("breakdown", {}) or {}

    # MTH — Motivation Home
    mth_raw = incentives_result.get("home_motivation", 0.5)
    variables.append(VariableResult(
        code="MTH", name="Motivation Home", pillar="INCENTIVES",
        raw_value=mth_raw, normalized=_clamp(mth_raw),
        confidence=0.6, available=True, source="espn_standings",
    ))

    # MTA — Motivation Away
    mta_raw = incentives_result.get("away_motivation", 0.5)
    variables.append(VariableResult(
        code="MTA", name="Motivation Away", pillar="INCENTIVES",
        raw_value=mta_raw, normalized=_clamp(mta_raw),
        confidence=0.6, available=True, source="espn_standings",
    ))

    # RIV — Rivalry Factor
    is_rivalry = incentives_result.get("is_rivalry", False)
    variables.append(VariableResult(
        code="RIV", name="Rivalry Factor", pillar="INCENTIVES",
        raw_value=1.0 if is_rivalry else 0.0,
        normalized=0.8 if is_rivalry else 0.5,
        confidence=0.9, available=True, source="hardcoded_rivalries",
    ))

    # CHP — Championship Significance
    is_champ = incentives_result.get("is_championship", False)
    variables.append(VariableResult(
        code="CHP", name="Championship Significance", pillar="INCENTIVES",
        raw_value=1.0 if is_champ else 0.0,
        normalized=0.9 if is_champ else 0.5,
        confidence=0.9, available=True, source="espn_standings",
    ))

    # PLF — Playoff Position
    playoff_bonus = breakdown.get("playoff_bonus", 0.0)
    variables.append(VariableResult(
        code="PLF", name="Playoff Position", pillar="INCENTIVES",
        raw_value=playoff_bonus,
        normalized=_clamp(0.5 + playoff_bonus),
        confidence=0.7 if playoff_bonus != 0.0 else 0.3,
        available=playoff_bonus != 0.0, source="espn_standings",
    ))

    # TNK — Tank/Rest Alert
    tank_alert = breakdown.get("tank_rest_alert", 0.0)
    variables.append(VariableResult(
        code="TNK", name="Tank/Rest Alert", pillar="INCENTIVES",
        raw_value=tank_alert,
        normalized=_clamp(0.5 - tank_alert * 0.3),  # Tank = lower motivation
        confidence=0.6, available=True, source="espn_standings",
    ))

    # SST — Season Stage
    stage_boost = breakdown.get("season_stage_boost", 0.0)
    variables.append(VariableResult(
        code="SST", name="Season Stage", pillar="INCENTIVES",
        raw_value=stage_boost,
        normalized=_clamp(0.5 + stage_boost),
        confidence=0.8, available=True, source="game_time",
    ))

    # UDG — Underdog Motivation
    underdog_boost = breakdown.get("underdog_boost", 0.0)
    variables.append(VariableResult(
        code="UDG", name="Underdog Motivation", pillar="INCENTIVES",
        raw_value=underdog_boost,
        normalized=_clamp(0.5 + underdog_boost),
        confidence=0.5, available=underdog_boost != 0.0, source="consensus_odds",
    ))

    # DVR — Divisional Rivalry
    div_rival = breakdown.get("divisional_rivalry", 0.0)
    variables.append(VariableResult(
        code="DVR", name="Divisional Rivalry", pillar="INCENTIVES",
        raw_value=div_rival,
        normalized=_clamp(0.5 + div_rival * 0.3),
        confidence=0.7, available=True, source="hardcoded_rivalries",
    ))

    # SRI — Schedule Rest Inequity
    # Thesis: Rest advantage is systematically underpriced, especially in NBA/NHL.
    # SRI = home_rest - away_rest. +3 days = 1.0, 0 = 0.5, -3 = 0.0
    td = time_decay_result or {}
    home_rest = td.get("home_rest_days")
    away_rest = td.get("away_rest_days")
    if home_rest is not None and away_rest is not None:
        sri_raw = float(home_rest) - float(away_rest)
        variables.append(VariableResult(
            code="SRI", name="Schedule Rest Inequity", pillar="INCENTIVES",
            raw_value=sri_raw,
            normalized=_clamp(0.5 + sri_raw / 6.0),  # ±3 days = full range
            confidence=0.8, available=True, source="espn_schedule",
        ))
    else:
        variables.append(_stub_variable("SRI", "Schedule Rest Inequity", "INCENTIVES", "espn_schedule"))

    # LSI — Letdown Spot Index
    # Thesis: Teams underperform after high-intensity games (rivalry wins,
    # blowout wins, nationally-televised games). Needs previous game context.
    # Stub for now — Phase 2 will query game_results for prior game metadata.
    variables.append(_stub_variable("LSI", "Letdown Spot Index", "INCENTIVES", "espn_schedule"))

    # TSM — Trap Spot Multiplier
    # Thesis: Heavy favorites sandwiched between marquee games, or road games
    # after dominant home wins, underperform the spread.
    # Conditions: heavy favorite (spread > 7), road, etc.
    if current_spread is not None:
        spread_abs = abs(current_spread)
        trap_score = 0.0
        # Heavy favorite adds to trap risk
        if spread_abs > 7.0:
            trap_score += 0.3
        if spread_abs > 10.0:
            trap_score += 0.2
        # Rivalry just before → letdown compounds trap
        if is_rivalry:
            trap_score += 0.15
        # Road + heavy favorite = classic trap
        # (we don't have home/away indicator directly, but spread sign tells us)
        # Negative spread = home favored, so if away favored by >7 = road trap
        if current_spread > 7.0:  # Away favored = road favorite = trap
            trap_score += 0.15
        variables.append(VariableResult(
            code="TSM", name="Trap Spot Multiplier", pillar="INCENTIVES",
            raw_value=trap_score,
            normalized=_clamp(0.5 - trap_score),  # Max trap = 0.0 (fade), no trap = 0.5
            confidence=0.5 if spread_abs > 7.0 else 0.2,
            available=True, source="cached_odds",
        ))
    else:
        variables.append(_stub_variable("TSM", "Trap Spot Multiplier", "INCENTIVES", "cached_odds"))

    return variables


def calculate_shocks_variables(
    shocks_result: dict,
    opening_line: Optional[float] = None,
    current_line: Optional[float] = None,
    sport: str = "NBA",
) -> List[VariableResult]:
    """Extract SHOCKS variables from existing shocks pillar result."""
    variables = []
    breakdown = shocks_result.get("breakdown", {}) or {}
    has_data = shocks_result.get("line_movement", 0.0) != 0.0 or shocks_result.get("shock_detected", False)

    # LMM — Line Movement Magnitude
    lmm_raw = abs(shocks_result.get("line_movement", 0.0))
    variables.append(VariableResult(
        code="LMM", name="Line Movement Magnitude", pillar="SHOCKS",
        raw_value=lmm_raw, normalized=_normalize_line_movement(lmm_raw, sport),
        confidence=0.8 if has_data else 0.1, available=has_data, source="line_snapshots",
    ))

    # LMV — Line Movement Velocity
    lmv_raw = breakdown.get("velocity", 0.0)
    variables.append(VariableResult(
        code="LMV", name="Line Movement Velocity", pillar="SHOCKS",
        raw_value=lmv_raw, normalized=_normalize_velocity(lmv_raw),
        confidence=0.7 if has_data else 0.1, available=has_data, source="line_snapshots",
    ))

    # STM — Steam Move Detection
    is_steam = shocks_result.get("shock_detected", False)
    variables.append(VariableResult(
        code="STM", name="Steam Move Detection", pillar="SHOCKS",
        raw_value=1.0 if is_steam else 0.0,
        normalized=0.9 if is_steam else 0.5,
        confidence=0.8 if has_data else 0.1, available=has_data, source="line_snapshots",
    ))

    # TMF — Time Factor (how recently did the line move)
    tmf_raw = breakdown.get("time_factor", 0.5)
    variables.append(VariableResult(
        code="TMF", name="Time Factor", pillar="SHOCKS",
        raw_value=tmf_raw, normalized=_clamp(tmf_raw),
        confidence=0.6 if has_data else 0.1, available=has_data, source="line_snapshots",
    ))

    # VOL — Volatility
    vol_raw = breakdown.get("volatility", 0.0)
    variables.append(VariableResult(
        code="VOL", name="Volatility", pillar="SHOCKS",
        raw_value=vol_raw, normalized=_clamp(vol_raw / 3.0),
        confidence=0.6 if has_data else 0.1, available=has_data, source="line_snapshots",
    ))

    # SHD — Shock Direction
    shock_dir = shocks_result.get("shock_direction", "neutral")
    dir_map = {"home": 0.8, "away": 0.2, "neutral": 0.5}
    variables.append(VariableResult(
        code="SHD", name="Shock Direction", pillar="SHOCKS",
        raw_value=dir_map.get(shock_dir, 0.5),
        normalized=dir_map.get(shock_dir, 0.5),
        confidence=0.7 if is_steam else 0.3, available=has_data, source="line_snapshots",
    ))

    # OLN — Opening Line Displacement
    if opening_line is not None and current_line is not None:
        oln_raw = current_line - opening_line
        variables.append(VariableResult(
            code="OLN", name="Opening Line Displacement", pillar="SHOCKS",
            raw_value=oln_raw,
            normalized=_clamp(0.5 + oln_raw / 6.0),  # ±3 pts = full range
            confidence=0.8, available=True, source="line_snapshots",
        ))
    else:
        variables.append(_stub_variable("OLN", "Opening Line Displacement", "SHOCKS", "line_snapshots"))

    # LRS — Late Room Shopping (stub — needs real-time book tracking)
    variables.append(_stub_variable("LRS", "Late Room Shopping", "SHOCKS", "line_snapshots"))

    # WXS — Weather Extreme Score
    # Thesis: Extreme weather (wind >20mph, temp <20F, heavy precip) depresses
    # scoring and creates totals value. Needs weather API integration.
    # Stub — Phase 2 will integrate Open-Meteo for outdoor NFL/NCAAF venues.
    variables.append(_stub_variable("WXS", "Weather Extreme Score", "SHOCKS", "open_meteo"))

    return variables


def calculate_time_decay_variables(
    time_decay_result: dict,
    sport: str = "NBA",
    opening_line: Optional[float] = None,
    current_line: Optional[float] = None,
    shocks_result: Optional[dict] = None,
) -> List[VariableResult]:
    """Extract TIME_DECAY variables from existing time_decay pillar result."""
    variables = []
    breakdown = time_decay_result.get("breakdown", {}) or {}

    # HRD — Home Rest Days
    hrd_raw = time_decay_result.get("home_rest_days", 3)
    variables.append(VariableResult(
        code="HRD", name="Home Rest Days", pillar="TIME_DECAY",
        raw_value=float(hrd_raw), normalized=_normalize_rest_days(hrd_raw, sport),
        confidence=0.8, available=True, source="espn_schedule",
    ))

    # ARD — Away Rest Days
    ard_raw = time_decay_result.get("away_rest_days", 3)
    variables.append(VariableResult(
        code="ARD", name="Away Rest Days", pillar="TIME_DECAY",
        raw_value=float(ard_raw), normalized=_normalize_rest_days(ard_raw, sport),
        confidence=0.8, available=True, source="espn_schedule",
    ))

    # B2B — Back-to-Back
    home_fatigue = time_decay_result.get("home_fatigue", 0.5)
    away_fatigue = time_decay_result.get("away_fatigue", 0.5)
    b2b_raw = max(home_fatigue, away_fatigue)
    is_b2b = breakdown.get("back_to_back", False)
    variables.append(VariableResult(
        code="B2B", name="Back-to-Back", pillar="TIME_DECAY",
        raw_value=b2b_raw,
        normalized=_clamp(1.0 - b2b_raw),  # Higher score = less fatigue
        confidence=0.8, available=True, source="espn_schedule",
    ))

    # T3F — Third-in-Four (stub — partially captured in fatigue)
    t3f_val = breakdown.get("third_in_four", 0.0)
    variables.append(VariableResult(
        code="T3F", name="Third-in-Four", pillar="TIME_DECAY",
        raw_value=t3f_val,
        normalized=_clamp(1.0 - t3f_val * 0.5),
        confidence=0.5, available=t3f_val != 0.0, source="espn_schedule",
    ))

    # TRV — Travel Distance
    travel = breakdown.get("travel_distance", 0.0)
    variables.append(VariableResult(
        code="TRV", name="Travel Distance", pillar="TIME_DECAY",
        raw_value=travel,
        normalized=_clamp(1.0 - travel / 3000.0),  # 3000mi = max penalty
        confidence=0.7 if travel > 0 else 0.3,
        available=travel > 0, source="stadium_coords",
    ))

    # HFA — Home Field Advantage
    hfa_raw = breakdown.get("home_field_advantage", 0.0)
    variables.append(VariableResult(
        code="HFA", name="Home Field Advantage", pillar="TIME_DECAY",
        raw_value=hfa_raw, normalized=_clamp(0.5 + hfa_raw),
        confidence=0.7, available=True, source="sport_config",
    ))

    # MWK — Midweek Fatigue (soccer)
    if sport == "EPL":
        mwk_raw = breakdown.get("midweek_factor", 0.0)
        variables.append(VariableResult(
            code="MWK", name="Midweek Fatigue", pillar="TIME_DECAY",
            raw_value=mwk_raw, normalized=_clamp(0.5 - mwk_raw * 0.3),
            confidence=0.6, available=True, source="game_time",
        ))
    else:
        variables.append(_stub_variable("MWK", "Midweek Fatigue", "TIME_DECAY", "game_time"))

    # MOM — Momentum Trend
    mom_raw = breakdown.get("momentum", 0.0)
    variables.append(VariableResult(
        code="MOM", name="Momentum Trend", pillar="TIME_DECAY",
        raw_value=mom_raw, normalized=_clamp(0.5 + mom_raw),
        confidence=0.5, available=mom_raw != 0.0, source="team_stats",
    ))

    # SLD — Stale Line Detector
    # Thesis: Lines that haven't moved in 6+ hours despite new information
    # (exchange price shifts, injury news) represent stale pricing → opportunity.
    # Uses velocity from shocks: if velocity ≈ 0 but exchange signal ≠ 0, line is stale.
    shk = shocks_result or {}
    shk_breakdown = shk.get("breakdown", {}) or {}
    velocity = shk_breakdown.get("velocity", 0.0)
    time_factor = shk_breakdown.get("time_factor", 0.5)
    # Low velocity + high time_factor (recent window) = stale
    if velocity is not None and time_factor is not None:
        # Staleness: inverse of velocity, scaled by recency
        # Very stale (vel=0, recent) = 1.0, active movement = 0.0
        staleness = (1.0 - min(velocity / 0.5, 1.0)) * time_factor
        variables.append(VariableResult(
            code="SLD", name="Stale Line Detector", pillar="TIME_DECAY",
            raw_value=staleness,
            normalized=_clamp(staleness),  # 1.0 = very stale (opportunity)
            confidence=0.5, available=velocity != 0.0 or time_factor != 0.5,
            source="line_snapshots",
        ))
    else:
        variables.append(_stub_variable("SLD", "Stale Line Detector", "TIME_DECAY", "line_snapshots"))

    # EWE — Early Week Edge
    # Thesis: Large opening-to-current movement reveals where early sharp bettors
    # captured value. Magnitude indicates information already priced in.
    if opening_line is not None and current_line is not None:
        ewe_raw = abs(current_line - opening_line)
        variables.append(VariableResult(
            code="EWE", name="Early Week Edge", pillar="TIME_DECAY",
            raw_value=ewe_raw,
            normalized=_normalize_line_movement(ewe_raw, sport),  # Large movement = 1.0
            confidence=0.7, available=True, source="line_snapshots",
        ))
    else:
        variables.append(_stub_variable("EWE", "Early Week Edge", "TIME_DECAY", "line_snapshots"))

    return variables


def calculate_flow_variables(
    flow_result: dict,
    sport: str = "NBA",
) -> List[VariableResult]:
    """Extract FLOW variables from existing flow pillar result."""
    variables = []
    breakdown = flow_result.get("breakdown", {}) or {}
    has_data = flow_result.get("book_agreement", 0.0) > 0

    # PND — Pinnacle Divergence
    pnd_raw = breakdown.get("pinnacle_divergence", 0.0)
    variables.append(VariableResult(
        code="PND", name="Pinnacle Divergence", pillar="FLOW",
        raw_value=pnd_raw, normalized=_normalize_divergence(pnd_raw),
        confidence=0.8 if pnd_raw != 0.0 else 0.2,
        available=pnd_raw != 0.0, source="cached_odds",
    ))

    # RTC — Retail Consensus
    rtc_raw = breakdown.get("retail_consensus", 0.5)
    variables.append(VariableResult(
        code="RTC", name="Retail Consensus", pillar="FLOW",
        raw_value=rtc_raw, normalized=_clamp(rtc_raw),
        confidence=0.6, available=has_data, source="cached_odds",
    ))

    # BAG — Book Agreement
    bag_raw = flow_result.get("book_agreement", 0.0)
    variables.append(VariableResult(
        code="BAG", name="Book Agreement", pillar="FLOW",
        raw_value=bag_raw, normalized=_normalize_book_agreement(bag_raw),
        confidence=0.8, available=has_data, source="cached_odds",
    ))

    # RLM — Reverse Line Movement
    rlm_raw = breakdown.get("rlm_signal", 0.0)
    variables.append(VariableResult(
        code="RLM", name="Reverse Line Movement", pillar="FLOW",
        raw_value=rlm_raw, normalized=_clamp(0.5 + rlm_raw),
        confidence=0.7 if rlm_raw != 0.0 else 0.2,
        available=rlm_raw != 0.0, source="line_snapshots",
    ))

    # FLM — Flow Line Movement
    flm_raw = breakdown.get("line_movement", 0.0)
    variables.append(VariableResult(
        code="FLM", name="Flow Line Movement", pillar="FLOW",
        raw_value=flm_raw, normalized=_normalize_line_movement(abs(flm_raw), sport),
        confidence=0.7 if has_data else 0.2, available=has_data, source="line_snapshots",
    ))

    # PDV — Price Divergence
    pdv_raw = breakdown.get("price_divergence", 0.0)
    variables.append(VariableResult(
        code="PDV", name="Price Divergence", pillar="FLOW",
        raw_value=pdv_raw, normalized=_clamp(pdv_raw / 2.0),
        confidence=0.6 if has_data else 0.2, available=has_data, source="cached_odds",
    ))

    # FVL — Flow Velocity
    fvl_raw = breakdown.get("velocity", 0.0)
    variables.append(VariableResult(
        code="FVL", name="Flow Velocity", pillar="FLOW",
        raw_value=fvl_raw, normalized=_normalize_velocity(fvl_raw),
        confidence=0.6 if has_data else 0.2, available=has_data, source="line_snapshots",
    ))

    # EXS — Exchange Signal
    exs_raw = breakdown.get("exchange_signal", 0.0)
    variables.append(VariableResult(
        code="EXS", name="Exchange Signal", pillar="FLOW",
        raw_value=exs_raw, normalized=_clamp(0.5 + exs_raw),
        confidence=0.7 if exs_raw != 0.0 else 0.1,
        available=exs_raw != 0.0, source="exchange_data",
    ))

    # SHP — Sharp Money Indicator (composite of PND + RLM + BAG)
    shp_raw = (pnd_raw * 0.4 + rlm_raw * 0.4 + (bag_raw - 0.5) * 0.2)
    variables.append(VariableResult(
        code="SHP", name="Sharp Money Indicator", pillar="FLOW",
        raw_value=shp_raw, normalized=_clamp(0.5 + shp_raw),
        confidence=0.6 if has_data else 0.1, available=has_data, source="cached_odds",
    ))

    # EDL — Exchange-to-Book Lead Time
    # Thesis: When exchange prices move before book lines adjust, the lead time
    # measures how much alpha remains. >30min lead = strong signal (1.0).
    # Needs timestamp-level comparison between exchange_data and line_snapshots.
    # Stub — Phase 2 will cross-reference exchange vs book move timestamps.
    variables.append(_stub_variable("EDL", "Exchange-to-Book Lead Time", "FLOW", "exchange_data"))

    # JFI — Juice Flow Indicator
    # Thesis: Vig/juice changes without line movement reveal book exposure.
    # e.g., -110/-110 → -115/-105 with no spread move = one side is getting
    # heavy action. Direction of juice shift = book's liability side.
    # Stub — Phase 2 will track odds changes independent of spread changes.
    variables.append(_stub_variable("JFI", "Juice Flow Indicator", "FLOW", "cached_odds"))

    return variables


def calculate_game_env_variables(
    game_env_result: dict,
    team_stats: Optional[dict] = None,
    sport: str = "NBA",
) -> List[VariableResult]:
    """Extract GAME_ENV variables from existing game_environment pillar result."""
    variables = []
    breakdown = game_env_result.get("breakdown", {}) or {}
    home_stats = (team_stats or {}).get("home", {})
    away_stats = (team_stats or {}).get("away", {})

    # EXT — Expected Total
    ext_raw = game_env_result.get("expected_total")
    if ext_raw is not None:
        variables.append(VariableResult(
            code="EXT", name="Expected Total", pillar="GAME_ENV",
            raw_value=float(ext_raw), normalized=_normalize_ppg(float(ext_raw), sport),
            confidence=0.7, available=True, source="team_stats",
        ))
    else:
        variables.append(_stub_variable("EXT", "Expected Total", "GAME_ENV", "team_stats"))

    # PAC — Pace Factor
    home_pace = home_stats.get("pace")
    away_pace = away_stats.get("pace")
    if home_pace is not None and away_pace is not None:
        avg_pace = (float(home_pace) + float(away_pace)) / 2
        variables.append(VariableResult(
            code="PAC", name="Pace Factor", pillar="GAME_ENV",
            raw_value=avg_pace, normalized=_normalize_pace(avg_pace, sport),
            confidence=0.8, available=True, source="team_stats",
        ))
    else:
        variables.append(_stub_variable("PAC", "Pace Factor", "GAME_ENV", "team_stats"))

    # ORT — Offensive Rating (average of both teams)
    home_ort = home_stats.get("offensive_rating")
    away_ort = away_stats.get("offensive_rating")
    if home_ort is not None and away_ort is not None:
        avg_ort = (float(home_ort) + float(away_ort)) / 2
        variables.append(VariableResult(
            code="ORT", name="Offensive Rating", pillar="GAME_ENV",
            raw_value=avg_ort, normalized=_normalize_rating(avg_ort, sport),
            confidence=0.8, available=True, source="team_stats",
        ))
    else:
        variables.append(_stub_variable("ORT", "Offensive Rating", "GAME_ENV", "team_stats"))

    # DRT — Defensive Rating (average of both teams, inverted: lower = better defense)
    home_drt = home_stats.get("defensive_rating")
    away_drt = away_stats.get("defensive_rating")
    if home_drt is not None and away_drt is not None:
        avg_drt = (float(home_drt) + float(away_drt)) / 2
        # Lower defensive rating = better defense = higher score
        variables.append(VariableResult(
            code="DRT", name="Defensive Rating", pillar="GAME_ENV",
            raw_value=avg_drt,
            normalized=_clamp(1.0 - _normalize_rating(avg_drt, sport)),
            confidence=0.8, available=True, source="team_stats",
        ))
    else:
        variables.append(_stub_variable("DRT", "Defensive Rating", "GAME_ENV", "team_stats"))

    # SPT — Special Teams (NHL: PP% + PK%)
    if sport == "NHL":
        spt_raw = breakdown.get("special_teams_score", 0.0)
        variables.append(VariableResult(
            code="SPT", name="Special Teams", pillar="GAME_ENV",
            raw_value=spt_raw, normalized=_clamp(spt_raw),
            confidence=0.7 if spt_raw > 0 else 0.2,
            available=spt_raw > 0, source="team_stats",
        ))
    else:
        variables.append(_stub_variable("SPT", "Special Teams", "GAME_ENV", "team_stats"))

    # WTH — Weather Impact (NFL/NCAAF only)
    if sport in ("NFL", "NCAAF"):
        wth_raw = breakdown.get("weather_impact", 0.0)
        variables.append(VariableResult(
            code="WTH", name="Weather Impact", pillar="GAME_ENV",
            raw_value=wth_raw, normalized=_clamp(0.5 + wth_raw),
            confidence=0.7 if wth_raw != 0.0 else 0.2,
            available=wth_raw != 0.0, source="open_meteo",
        ))
    else:
        variables.append(_stub_variable("WTH", "Weather Impact", "GAME_ENV", "open_meteo"))

    # PPG — Points Per Game Average
    home_ppg = home_stats.get("points_per_game")
    away_ppg = away_stats.get("points_per_game")
    if home_ppg is not None and away_ppg is not None:
        avg_ppg = (float(home_ppg) + float(away_ppg)) / 2
        variables.append(VariableResult(
            code="PPG", name="Points Per Game Average", pillar="GAME_ENV",
            raw_value=avg_ppg, normalized=_normalize_ppg(avg_ppg, sport),
            confidence=0.8, available=True, source="team_stats",
        ))
    else:
        variables.append(_stub_variable("PPG", "Points Per Game Average", "GAME_ENV", "team_stats"))

    # VEN — Venue Factor (stub — need venue-specific data)
    variables.append(_stub_variable("VEN", "Venue Factor", "GAME_ENV", "sport_config"))

    # GLS — Goals For/Against Rate (NHL/EPL)
    if sport in ("NHL", "EPL"):
        gls_raw = breakdown.get("goals_per_game", 0.0)
        variables.append(VariableResult(
            code="GLS", name="Goals For/Against Rate", pillar="GAME_ENV",
            raw_value=gls_raw, normalized=_normalize_ppg(gls_raw, sport),
            confidence=0.7 if gls_raw > 0 else 0.2,
            available=gls_raw > 0, source="team_stats",
        ))
    else:
        variables.append(_stub_variable("GLS", "Goals For/Against Rate", "GAME_ENV", "team_stats"))

    # PTI — Pace/Tempo Interaction
    # Thesis: Expected pace when two specific teams meet predicts totals better
    # than league averages. Fast-fast matchups systematically go over.
    home_pace = home_stats.get("pace")
    away_pace = away_stats.get("pace")
    if home_pace is not None and away_pace is not None and sport in ("NBA", "NCAAB"):
        # Interaction: geometric mean of both teams' paces relative to league avg
        h_pace = float(home_pace)
        a_pace = float(away_pace)
        league_avg_pace = {"NBA": 100.0, "NCAAB": 68.0}.get(sport, 100.0)
        # How much faster/slower than average this matchup will play
        matchup_pace = (h_pace + a_pace) / 2
        pti_raw = matchup_pace - league_avg_pace
        variables.append(VariableResult(
            code="PTI", name="Pace/Tempo Interaction", pillar="GAME_ENV",
            raw_value=pti_raw,
            normalized=_clamp(0.5 + pti_raw / 20.0),  # ±10 = full range
            confidence=0.8, available=True, source="team_stats",
        ))
    else:
        variables.append(_stub_variable("PTI", "Pace/Tempo Interaction", "GAME_ENV", "team_stats"))

    # HCA — Home Court Advantage (Dynamic)
    # Thesis: Team-specific current-season HCA varies dramatically from the
    # league average. Teams with strong HCA are underpriced at home.
    # Use home win% vs away win% differential from team_stats.
    home_wp = home_stats.get("win_pct")
    home_wins = home_stats.get("wins")
    home_losses = home_stats.get("losses")
    if home_wp is not None and home_wins is not None and home_losses is not None:
        # Overall win% is a proxy; true HCA needs home-only record.
        # For now: teams with win% > 0.6 at home get boosted.
        # Sport-average HCA baselines
        hca_baseline = {"NBA": 0.58, "NCAAB": 0.60, "NFL": 0.57, "NHL": 0.55, "EPL": 0.46}.get(sport, 0.55)
        wp = float(home_wp)
        hca_raw = wp - hca_baseline  # Positive = above-average HCA
        variables.append(VariableResult(
            code="HCA", name="Home Court Advantage", pillar="GAME_ENV",
            raw_value=hca_raw,
            normalized=_clamp(0.5 + hca_raw * 2.0),  # ±0.25 = full range
            confidence=0.6, available=True, source="team_stats",
        ))
    else:
        variables.append(_stub_variable("HCA", "Home Court Advantage", "GAME_ENV", "team_stats"))

    return variables


# ═══════════════════════════════════════════════════════════════════════
# ORCHESTRATOR — Calculate all 63 variables for a game
# ═══════════════════════════════════════════════════════════════════════

def calculate_all_variables(
    pillar_results: dict,
    sport: str,
    team_stats: Optional[dict] = None,
    opening_line: Optional[float] = None,
    current_line: Optional[float] = None,
) -> Dict[str, List[VariableResult]]:
    """
    Calculate all 63 variables from existing pillar results.

    Args:
        pillar_results: dict with keys execution, incentives, shocks,
                        time_decay, flow, game_environment — each a pillar result dict
        sport: e.g. "NBA", "NFL"
        team_stats: optional {home: {...}, away: {...}} from team_stats table
        opening_line: opening spread line
        current_line: current spread line

    Returns:
        dict mapping pillar name → list of VariableResult
    """
    time_decay_result = pillar_results.get("time_decay", {})
    shocks_result = pillar_results.get("shocks", {})

    return {
        "EXECUTION": calculate_execution_variables(
            pillar_results.get("execution", {}), team_stats, sport,
        ),
        "INCENTIVES": calculate_incentives_variables(
            pillar_results.get("incentives", {}), sport,
            time_decay_result=time_decay_result,
            current_spread=current_line,
        ),
        "SHOCKS": calculate_shocks_variables(
            shocks_result, opening_line, current_line, sport,
        ),
        "TIME_DECAY": calculate_time_decay_variables(
            time_decay_result, sport,
            opening_line=opening_line,
            current_line=current_line,
            shocks_result=shocks_result,
        ),
        "FLOW": calculate_flow_variables(
            pillar_results.get("flow", {}), sport,
        ),
        "GAME_ENV": calculate_game_env_variables(
            pillar_results.get("game_environment", {}), team_stats, sport,
        ),
    }


def aggregate_pillar_scores(
    all_variables: Dict[str, List[VariableResult]],
    context: GameContext,
) -> List[PillarScore]:
    """
    Aggregate variable-level scores into pillar-level scores using
    dynamic weights.

    Within each pillar, available variables are confidence-weighted averaged.
    Across pillars, dynamic context weights are applied.
    """
    dynamic_weights = calculate_dynamic_weights(context)
    pillar_scores = []

    for pillar_name, var_list in all_variables.items():
        # Confidence-weighted average of available variables
        weighted_sum = 0.0
        weight_total = 0.0
        for v in var_list:
            if v.available:
                weighted_sum += v.normalized * v.confidence
                weight_total += v.confidence

        score = weighted_sum / weight_total if weight_total > 0 else 0.5
        pillar_weight = dynamic_weights.get(pillar_name, 0.1)

        pillar_scores.append(PillarScore(
            pillar=pillar_name,
            score=score,
            weight=pillar_weight,
            variables=var_list,
        ))

    return pillar_scores


def calculate_variable_composite(pillar_scores: List[PillarScore]) -> float:
    """
    Calculate the final composite from variable-engine pillar scores.
    Returns 0.0 to 1.0.
    """
    weighted_sum = sum(ps.score * ps.weight for ps in pillar_scores)
    weight_total = sum(ps.weight for ps in pillar_scores)
    return weighted_sum / weight_total if weight_total > 0 else 0.5


# ═══════════════════════════════════════════════════════════════════════
# DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════

def get_variable_summary(all_variables: Dict[str, List[VariableResult]]) -> dict:
    """Return a summary for logging/debugging."""
    total = 0
    available = 0
    by_pillar = {}

    for pillar, var_list in all_variables.items():
        avail = sum(1 for v in var_list if v.available)
        total += len(var_list)
        available += avail
        by_pillar[pillar] = {
            "total": len(var_list),
            "available": avail,
            "avg_confidence": (
                sum(v.confidence for v in var_list if v.available) / avail
                if avail > 0 else 0.0
            ),
        }

    return {
        "total_variables": total,
        "available_variables": available,
        "coverage_pct": round(available / total * 100, 1) if total > 0 else 0,
        "by_pillar": by_pillar,
    }
