"""
OMI Edge Analysis Engine

The core engine that:
1. Fetches data from all sources
2. Calculates all 6 pillar scores (execution, incentives, shocks, time_decay, flow, game_environment)
3. Computes market-specific and period-specific composite scores (3 markets x 7 periods = 21 combinations)
4. Determines confidence rating based on composite and edge percentage
"""
from datetime import datetime, timezone
from typing import Optional
import logging
import json

from config import SPORT_WEIGHTS, DEFAULT_WEIGHTS, PILLAR_WEIGHTS, EDGE_THRESHOLDS
from data_sources.odds_api import odds_client
from data_sources.espn import espn_client
from pillars import (
    calculate_execution_score,
    calculate_incentives_score,
    calculate_shocks_score,
    calculate_time_decay_score,
    calculate_flow_score,
    calculate_game_environment_score,
    fetch_nhl_game_stats_sync,
)
from engine.weight_calculator import calculate_all_composites

logger = logging.getLogger(__name__)


def fetch_line_context(game_id: str, sport_key: str) -> dict:
    """
    Fetch opening line, current line, and line movement history from database.

    Args:
        game_id: The game identifier
        sport_key: The sport key (can be lowercase like 'americanfootball_nfl')

    Returns:
        dict with:
            - opening_line: float or None (earliest spread line)
            - current_line: float or None (most recent spread line)
            - line_snapshots: list of {timestamp, line} dicts for shocks/flow pillars
    """
    from database import db

    result = {
        "opening_line": None,
        "current_line": None,
        "line_snapshots": []
    }

    if not db._is_connected():
        logger.warning("Database not connected, cannot fetch line context")
        return result

    try:
        # Query line_snapshots for spread market, full game
        # Note: game_id is unique across sports from Odds API, so no sport_key filter needed
        # Don't filter by outcome_type — spread snapshots were saved without it
        query_result = db.client.table("line_snapshots").select(
            "line, snapshot_time, book_key"
        ).eq(
            "game_id", game_id
        ).eq(
            "market_type", "spread"
        ).eq(
            "market_period", "full"
        ).order(
            "snapshot_time", desc=False
        ).execute()

        raw_snapshots = query_result.data or []

        if raw_snapshots:
            # Deduplicate: median line per snapshot_time (across books)
            import statistics as _stats
            from collections import defaultdict
            by_time: dict = defaultdict(list)
            for snap in raw_snapshots:
                t = snap.get("snapshot_time")
                line_val = snap.get("line")
                if t and line_val is not None:
                    by_time[t].append(line_val)

            # Build deduplicated list sorted by time
            deduped = sorted(
                [{"timestamp": t, "line": _stats.median(lines)} for t, lines in by_time.items()],
                key=lambda x: x["timestamp"]
            )

            if deduped:
                result["opening_line"] = deduped[0]["line"]
                result["current_line"] = deduped[-1]["line"]
                result["line_snapshots"] = deduped

            logger.info(f"  Line context for {game_id}: opening={result['opening_line']}, "
                       f"current={result['current_line']}, {len(deduped)} unique timestamps "
                       f"({len(raw_snapshots)} raw snapshots across books)")
        else:
            logger.warning(f"  WARNING: No line snapshots found for {game_id} — Shocks and Flow will return default 0.5")
            logger.warning(f"  This means 50% of the composite (Shocks 25% + Flow 25%) is fake/neutral")

    except Exception as e:
        logger.error(f"Error fetching line context for {game_id}: {e}")

    return result

# Team name to abbreviation mappings
NHL_TEAM_ABBR = {
    "anaheim ducks": "ANA", "arizona coyotes": "ARI", "boston bruins": "BOS",
    "buffalo sabres": "BUF", "calgary flames": "CGY", "carolina hurricanes": "CAR",
    "chicago blackhawks": "CHI", "colorado avalanche": "COL", "columbus blue jackets": "CBJ",
    "dallas stars": "DAL", "detroit red wings": "DET", "edmonton oilers": "EDM",
    "florida panthers": "FLA", "los angeles kings": "LAK", "minnesota wild": "MIN",
    "montreal canadiens": "MTL", "nashville predators": "NSH", "new jersey devils": "NJD",
    "new york islanders": "NYI", "new york rangers": "NYR", "ottawa senators": "OTT",
    "philadelphia flyers": "PHI", "pittsburgh penguins": "PIT", "san jose sharks": "SJS",
    "seattle kraken": "SEA", "st. louis blues": "STL", "st louis blues": "STL",
    "tampa bay lightning": "TBL", "toronto maple leafs": "TOR", "utah hockey club": "UTA",
    "vancouver canucks": "VAN", "vegas golden knights": "VGK", "washington capitals": "WSH",
    "winnipeg jets": "WPG",
}


def _extract_team_abbr(team_name: str, sport: str) -> str:
    """Extract team abbreviation from full team name."""
    if not team_name:
        return ""

    team_lower = team_name.lower().strip()

    if sport == "NHL":
        # Direct lookup
        if team_lower in NHL_TEAM_ABBR:
            return NHL_TEAM_ABBR[team_lower]

        # Partial match (e.g., "Bruins" -> "BOS")
        for full_name, abbr in NHL_TEAM_ABBR.items():
            # Check if any word in full_name is in team_lower
            for word in full_name.split():
                if len(word) > 3 and word in team_lower:
                    return abbr

    return ""


SPORT_KEY_TO_LEAGUE = {
    # Lowercase Odds API format
    "basketball_nba": "NBA",
    "basketball_ncaab": "NCAAB",
    "americanfootball_nfl": "NFL",
    "americanfootball_ncaaf": "NCAAF",
    "icehockey_nhl": "NHL",
    "soccer_epl": "EPL",
    # Uppercase short format (used by scheduler)
    "NBA": "NBA",
    "NCAAB": "NCAAB",
    "NFL": "NFL",
    "NCAAF": "NCAAF",
    "NHL": "NHL",
    "EPL": "EPL",
    # Uppercase Odds API format
    "BASKETBALL_NBA": "NBA",
    "BASKETBALL_NCAAB": "NCAAB",
    "AMERICANFOOTBALL_NFL": "NFL",
    "AMERICANFOOTBALL_NCAAF": "NCAAF",
    "ICEHOCKEY_NHL": "NHL",
    "SOCCER_EPL": "EPL",
}


def fetch_team_environment_stats(
    home_team: str, away_team: str, sport_key: str
) -> Optional[dict]:
    """
    Fetch team stats from Supabase team_stats table for game environment pillar.

    Returns dict:
        {"home": {pace, offensive_rating, defensive_rating, points_per_game, ...},
         "away": {pace, offensive_rating, defensive_rating, points_per_game, ...}}
    or None if fetch fails / no data.
    """
    from database import db

    if not db._is_connected():
        logger.debug("Database not connected, skipping team_environment stats fetch")
        return None

    league = SPORT_KEY_TO_LEAGUE.get(sport_key, "")
    if not league:
        return None

    try:
        # Fetch stats filtered by league
        result = db.client.table("team_stats").select(
            "team_name, team_abbrev, pace, offensive_rating, defensive_rating, "
            "points_per_game, points_allowed_per_game, net_rating, wins, losses, "
            "win_pct, streak"
        ).eq(
            "league", league
        ).execute()

        rows = result.data or []
        if not rows:
            logger.info(f"CALIBRATION_DEBUG: game_environment no team_stats rows for league={league}")
            return None

        # Build lookup by lowercase team name + abbreviation
        lookup: dict[str, dict] = {}
        for row in rows:
            name = row.get("team_name", "").lower()
            abbr = (row.get("team_abbrev") or "").lower()
            if name:
                lookup[name] = row
            if abbr:
                lookup[abbr] = row
            # Also index by nickname (last word)
            words = name.split()
            if len(words) > 1 and len(words[-1]) > 3:
                nickname = words[-1]
                if nickname not in lookup:
                    lookup[nickname] = row

        # Match home team
        home_key = home_team.lower()
        home_row = lookup.get(home_key)
        if not home_row:
            for k, v in lookup.items():
                if home_key in k or k in home_key:
                    home_row = v
                    break

        # Match away team
        away_key = away_team.lower()
        away_row = lookup.get(away_key)
        if not away_row:
            for k, v in lookup.items():
                if away_key in k or k in away_key:
                    away_row = v
                    break

        if not home_row and not away_row:
            logger.info(
                f"CALIBRATION_DEBUG: game_environment no match for "
                f"home='{home_team}' away='{away_team}' league={league} "
                f"(db has {len(rows)} teams)"
            )
            return None

        if not home_row:
            logger.info(f"CALIBRATION_DEBUG: game_environment home NOT FOUND: '{home_team}' league={league}")
        if not away_row:
            logger.info(f"CALIBRATION_DEBUG: game_environment away NOT FOUND: '{away_team}' league={league}")

        stats = {
            "home": home_row or {},
            "away": away_row or {},
        }

        logger.info(
            f"CALIBRATION_DEBUG: game_environment fetched stats for "
            f"{home_team}: pace={home_row.get('pace') if home_row else None}, "
            f"off_rtg={home_row.get('offensive_rating') if home_row else None}, "
            f"ppg={home_row.get('points_per_game') if home_row else None} | "
            f"{away_team}: pace={away_row.get('pace') if away_row else None}, "
            f"off_rtg={away_row.get('offensive_rating') if away_row else None}, "
            f"ppg={away_row.get('points_per_game') if away_row else None}"
        )

        return stats

    except Exception as e:
        logger.error(f"Error fetching team_environment stats: {e}")
        return None


def american_to_implied_prob(odds: int) -> float:
    """Convert American odds to implied probability."""
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)


def implied_prob_to_american(prob: float) -> int:
    """Convert implied probability to American odds."""
    if prob <= 0 or prob >= 1:
        return 0
    if prob >= 0.5:
        return int(-100 * prob / (1 - prob))
    else:
        return int(100 * (1 - prob) / prob)


def _compress_pillar(score: float) -> float:
    """Compress extreme pillar values to prevent single pillar domination.

    Scores beyond [0.15, 0.85] are compressed by 70%, reducing the impact
    of any single runaway pillar on the composite.
    Effect: pillar at 1.0 → 0.895, pillar at 0.0 → 0.105.
    """
    if score > 0.85:
        return 0.85 + (score - 0.85) * 0.3
    if score < 0.15:
        return 0.15 - (0.15 - score) * 0.3
    return score


def calculate_composite_score(pillar_scores: dict, sport: str = "NBA") -> float:
    """Calculate weighted composite score from all pillars using sport-specific weights."""
    # Normalize sport key to uppercase short format
    sport_upper = sport.upper()
    sport_normalized = SPORT_KEY_TO_LEAGUE.get(sport, sport_upper)

    # Get sport-specific weights, fall back to default
    weights = SPORT_WEIGHTS.get(sport_normalized, DEFAULT_WEIGHTS)

    logger.info(f"  CALIBRATION_DEBUG: Using {sport_normalized} weights: {weights}")

    composite = 0.0
    total_weight = 0.0

    for pillar, weight in weights.items():
        if pillar in pillar_scores:
            compressed = _compress_pillar(pillar_scores[pillar])
            composite += compressed * weight
            total_weight += weight

    if total_weight == 0:
        return 0.5

    return composite / total_weight * (sum(weights.values()) / total_weight)


def calculate_edge_percentage(
    composite_score: float,
    book_implied_prob: float,
    side: str = "home"
) -> float:
    """Calculate edge percentage based on composite score and book odds."""
    adjustment = (composite_score - 0.5) * 0.2
    
    if side == "home":
        our_true_prob = book_implied_prob - adjustment
    else:
        our_true_prob = book_implied_prob + adjustment
    
    our_true_prob = max(0.01, min(0.99, our_true_prob))
    edge = (our_true_prob - book_implied_prob) * 100
    
    return round(edge, 2)


def get_confidence_rating(edge_pct: float, composite_score: float) -> str:
    """
    Determine confidence rating based on composite score AND actual edge percentage.

    Primary tier selection (from composite score):
    - 86%+ = RARE (exceptional opportunity)
    - 76-85% = STRONG (high confidence)
    - 66-75% = EDGE (actionable)
    - 56-65% = WATCH (monitor for movement)
    - <56% = PASS (no actionable edge)

    Secondary adjustments (from edge_pct):
    - If abs(edge_pct) < 0.5: cap at WATCH max (market already priced it in)
    - If abs(edge_pct) < 1.0: downgrade by one tier
    """
    # Convert 0-1 scale to 0-100 percentage
    composite_pct = composite_score * 100

    # Primary tier from composite score
    if composite_pct >= 86:
        tier = "RARE"
    elif composite_pct >= 76:
        tier = "STRONG"
    elif composite_pct >= 66:
        tier = "EDGE"
    elif composite_pct >= 56:
        tier = "WATCH"
    else:
        return "PASS"  # Can't downgrade below PASS

    # Secondary check: edge_pct magnitude
    abs_edge = abs(edge_pct)

    # If edge is negligible (<0.5%), cap at WATCH regardless of composite
    if abs_edge < 0.5:
        if tier in ("RARE", "STRONG", "EDGE"):
            return "WATCH"
        return tier

    # If edge is small (<1.0%), downgrade by one tier
    if abs_edge < 1.0:
        downgrade_map = {
            "RARE": "STRONG",
            "STRONG": "EDGE",
            "EDGE": "WATCH",
            "WATCH": "WATCH",  # Can't go below WATCH via this rule
        }
        return downgrade_map.get(tier, tier)

    return tier


def analyze_game(
    game: dict,
    sport: str,
    opening_line: Optional[float] = None,
    line_snapshots: Optional[list] = None
) -> dict:
    """Full analysis of a single game using all 6 pillars.

    Returns pillars_by_market with market-specific AND period-specific composites.
    """
    parsed = odds_client.parse_game_odds(game)

    home_team = parsed["home_team"]
    away_team = parsed["away_team"]
    game_time = parsed["commence_time"]
    game_id = parsed["game_id"]

    logger.info(f"Analyzing: {away_team} @ {home_team}")
    logger.info(f"  Sport: {sport}, Home: '{home_team}', Away: '{away_team}'")

    # Fetch line context from database if not provided
    # This powers the Shocks (0.25 weight) and Flow (0.25 weight) pillars
    if opening_line is None or line_snapshots is None:
        line_context = fetch_line_context(game_id, sport)
        if opening_line is None:
            opening_line = line_context.get("opening_line")
        if line_snapshots is None:
            line_snapshots = line_context.get("line_snapshots", [])

    venue = None

    # Neutral fallback for any pillar that crashes (score=0.5, all markets=0.5)
    _NEUTRAL_PILLAR = {
        "score": 0.5,
        "market_scores": {"spread": 0.5, "moneyline": 0.5, "totals": 0.5},
        "breakdown": {},
        "reasoning": "Pillar returned neutral (data unavailable or error)",
    }

    try:
        execution = calculate_execution_score(
            sport=sport,
            home_team=home_team,
            away_team=away_team,
            game_time=game_time,
            venue=venue
        )
    except Exception as e:
        logger.error(f"[Analyzer] Execution pillar crashed for {away_team}@{home_team} ({sport}): {e}")
        execution = {**_NEUTRAL_PILLAR, "home_injury_impact": 0, "away_injury_impact": 0, "weather_factor": 0, "soccer_adjustment": 0}

    try:
        incentives = calculate_incentives_score(
            sport=sport,
            home_team=home_team,
            away_team=away_team,
            game_time=game_time
        )
    except Exception as e:
        logger.error(f"[Analyzer] Incentives pillar crashed for {away_team}@{home_team} ({sport}): {e}")
        incentives = {**_NEUTRAL_PILLAR, "home_motivation": 0.5, "away_motivation": 0.5, "is_rivalry": False, "is_championship": False, "soccer_motivation_adjustment": 0}

    # Calculate consensus odds (now includes extended markets)
    consensus = odds_client.calculate_consensus_odds(game)
    current_line = None
    if consensus.get("spreads", {}).get("home"):
        current_line = consensus["spreads"]["home"]["line"]

    try:
        shocks = calculate_shocks_score(
            sport=sport,
            home_team=home_team,
            away_team=away_team,
            game_time=game_time,
            current_line=current_line,
            opening_line=opening_line,
            line_movement_history=line_snapshots
        )
    except Exception as e:
        logger.error(f"[Analyzer] Shocks pillar crashed for {away_team}@{home_team} ({sport}): {e}")
        shocks = {**_NEUTRAL_PILLAR, "line_movement": 0, "shock_detected": False, "shock_direction": "neutral"}

    try:
        time_decay = calculate_time_decay_score(
            sport=sport,
            home_team=home_team,
            away_team=away_team,
            game_time=game_time
        )
    except Exception as e:
        logger.error(f"[Analyzer] TimeDecay pillar crashed for {away_team}@{home_team} ({sport}): {e}")
        time_decay = {**_NEUTRAL_PILLAR, "home_fatigue": 0.5, "away_fatigue": 0.5, "home_rest_days": 3, "away_rest_days": 3}

    try:
        flow = calculate_flow_score(
            game=game,
            opening_line=opening_line,
            line_snapshots=line_snapshots
        )
    except Exception as e:
        logger.error(f"[Analyzer] Flow pillar crashed for {away_team}@{home_team} ({sport}): {e}")
        flow = {**_NEUTRAL_PILLAR, "spread_variance": 0, "consensus_line": 0, "sharpest_line": 0, "book_agreement": 0}

    # Game Environment (for totals analysis and composite)
    # Now included in 6-pillar composite calculation
    try:
        nhl_stats = None
        total_line = None

        # Get total line from consensus
        if consensus.get("totals", {}).get("over"):
            total_line = consensus["totals"]["over"].get("line")

        # Fetch team stats from Supabase for environment analysis
        env_team_stats = fetch_team_environment_stats(home_team, away_team, sport)

        # Sport key sets - accept both short format (NBA) and Odds API format (basketball_nba)
        NHL_KEYS = {"NHL", "icehockey_nhl", "ICEHOCKEY_NHL"}
        NFL_KEYS = {"NFL", "americanfootball_nfl", "AMERICANFOOTBALL_NFL"}
        NCAAF_KEYS = {"NCAAF", "americanfootball_ncaaf", "AMERICANFOOTBALL_NCAAF"}
        NBA_KEYS = {"NBA", "basketball_nba", "BASKETBALL_NBA"}
        NCAAB_KEYS = {"NCAAB", "basketball_ncaab", "BASKETBALL_NCAAB"}
        EPL_KEYS = {"EPL", "soccer_epl", "SOCCER_EPL"}

        if sport in NHL_KEYS:
            # Try NHL-specific API first, fall back to Supabase team_stats
            home_abbr = _extract_team_abbr(home_team, "NHL")
            away_abbr = _extract_team_abbr(away_team, "NHL")

            if home_abbr and away_abbr:
                try:
                    nhl_stats = fetch_nhl_game_stats_sync(home_abbr, away_abbr)
                except Exception as e:
                    logger.warning(f"NHL stats API failed ({e}), using Supabase fallback")

            game_env = calculate_game_environment_score(
                sport="NHL",
                home_team=home_team,
                away_team=away_team,
                total_line=total_line,
                nhl_stats=nhl_stats,
                team_stats=env_team_stats,
            )

        elif sport in NFL_KEYS or sport in NCAAF_KEYS:
            # NFL/NCAAF game environment with weather + team scoring stats
            game_env = calculate_game_environment_score(
                sport="NFL" if sport in NFL_KEYS else "NCAAF",
                home_team=home_team,
                away_team=away_team,
                total_line=total_line,
                game_time=game_time,
                team_stats=env_team_stats,
            )

        elif sport in NBA_KEYS or sport in NCAAB_KEYS:
            # NBA/NCAAB - pace, offensive/defensive ratings from Supabase
            game_env = calculate_game_environment_score(
                sport="NBA" if sport in NBA_KEYS else "NCAAB",
                home_team=home_team,
                away_team=away_team,
                total_line=total_line,
                team_stats=env_team_stats,
            )

        elif sport in EPL_KEYS:
            # EPL - goals per game from Football-Data.org via team_stats
            game_env = calculate_game_environment_score(
                sport="EPL",
                home_team=home_team,
                away_team=away_team,
                total_line=total_line,
                team_stats=env_team_stats,
            )

        else:
            # Tennis, other sports without team_stats data
            game_env = {
                "score": 0.5,
                "expected_total": None,
                "breakdown": {},
                "reasoning": "No sport-specific environment data available"
            }
    except Exception as e:
        logger.error(f"[Analyzer] GameEnvironment pillar crashed for {away_team}@{home_team} ({sport}): {e}")
        game_env = {**_NEUTRAL_PILLAR, "expected_total": None}

    logger.info(f"  Game Environment: {game_env['score']:.3f} - {game_env.get('reasoning', 'N/A')}")

    pillar_scores = {
        "execution": execution["score"],
        "incentives": incentives["score"],
        "shocks": shocks["score"],
        "time_decay": time_decay["score"],
        "flow": flow["score"],
        "game_environment": game_env["score"],
    }

    # Extract market-specific pillar scores from each pillar
    # Each pillar now returns market_scores: {spread: x, totals: y, moneyline: z}
    pillar_market_scores = {
        "execution": execution.get("market_scores", {"spread": execution["score"], "totals": execution["score"], "moneyline": execution["score"]}),
        "incentives": incentives.get("market_scores", {"spread": incentives["score"], "totals": incentives["score"], "moneyline": incentives["score"]}),
        "shocks": shocks.get("market_scores", {"spread": shocks["score"], "totals": shocks["score"], "moneyline": shocks["score"]}),
        "time_decay": time_decay.get("market_scores", {"spread": time_decay["score"], "totals": time_decay["score"], "moneyline": time_decay["score"]}),
        "flow": flow.get("market_scores", {"spread": flow["score"], "totals": flow["score"], "moneyline": flow["score"]}),
        "game_environment": game_env.get("market_scores", {"spread": game_env["score"], "totals": game_env["score"], "moneyline": game_env["score"]}),
    }

    # Log market-specific pillar scores for debugging
    logger.info(f"  Market-specific pillar scores:")
    for pillar, ms in pillar_market_scores.items():
        logger.info(f"    {pillar}: spread={ms.get('spread', 'N/A'):.3f}, totals={ms.get('totals', 'N/A'):.3f}")

    # Calculate all market/period composite combinations (3 markets x 7 periods = up to 21)
    # Now uses market-specific pillar scores for different pillar values per market
    pillars_by_market = calculate_all_composites(pillar_scores, sport, pillar_market_scores)
    logger.info(f"  Generated {sum(len(p) for p in pillars_by_market.values())} market/period composites")

    # Debug: Log pillar scores and reasoning
    logger.info(f"  Pillar scores for {home_team}:")
    logger.info(f"    Execution: {execution['score']:.3f} - {execution.get('reasoning', 'N/A')}")
    logger.info(f"    Incentives: {incentives['score']:.3f} - {incentives.get('reasoning', 'N/A')}")
    logger.info(f"    Shocks: {shocks['score']:.3f} - {shocks.get('reasoning', 'N/A')}")
    logger.info(f"    Time Decay: {time_decay['score']:.3f} - {time_decay.get('reasoning', 'N/A')}")
    logger.info(f"    Flow: {flow['score']:.3f} - {flow.get('reasoning', 'N/A')}")
    logger.info(f"    Game Environment: {game_env['score']:.3f} - {game_env.get('reasoning', 'N/A')}")

    composite = calculate_composite_score(pillar_scores, sport)
    
    edges = {}
    
    if consensus.get("h2h"):
        home_odds = consensus["h2h"].get("home")
        away_odds = consensus["h2h"].get("away")
        
        if home_odds:
            home_prob = american_to_implied_prob(home_odds)
            home_edge = calculate_edge_percentage(composite, home_prob, "home")
            edges["ml_home"] = {
                "odds": home_odds,
                "implied_prob": round(home_prob, 4),
                "edge_pct": home_edge,
                "confidence": get_confidence_rating(home_edge, composite)
            }
        
        if away_odds:
            away_prob = american_to_implied_prob(away_odds)
            away_edge = calculate_edge_percentage(composite, away_prob, "away")
            edges["ml_away"] = {
                "odds": away_odds,
                "implied_prob": round(away_prob, 4),
                "edge_pct": away_edge,
                "confidence": get_confidence_rating(away_edge, composite)
            }
    
    if consensus.get("spreads"):
        home_spread = consensus["spreads"].get("home", {})
        away_spread = consensus["spreads"].get("away", {})
        
        if home_spread:
            spread_prob = american_to_implied_prob(home_spread.get("odds", -110))
            home_spread_edge = calculate_edge_percentage(composite, spread_prob, "home")
            edges["spread_home"] = {
                "line": home_spread.get("line"),
                "odds": home_spread.get("odds"),
                "implied_prob": round(spread_prob, 4),
                "edge_pct": home_spread_edge,
                "confidence": get_confidence_rating(home_spread_edge, composite)
            }
        
        if away_spread:
            spread_prob = american_to_implied_prob(away_spread.get("odds", -110))
            away_spread_edge = calculate_edge_percentage(composite, spread_prob, "away")
            edges["spread_away"] = {
                "line": away_spread.get("line"),
                "odds": away_spread.get("odds"),
                "implied_prob": round(spread_prob, 4),
                "edge_pct": away_spread_edge,
                "confidence": get_confidence_rating(away_spread_edge, composite)
            }
    
    if consensus.get("totals"):
        over = consensus["totals"].get("over", {})
        under = consensus["totals"].get("under", {})

        # Enhanced totals composite using game environment if available
        if game_env and game_env.get("score") is not None:
            # Weight: 40% game_env, 30% flow, 20% shocks, 10% time_decay
            totals_composite = (
                game_env["score"] * 0.4 +
                flow["score"] * 0.3 +
                shocks["score"] * 0.2 +
                time_decay["score"] * 0.1
            )
            logger.info(f"  Totals composite (with game_env): {totals_composite:.3f}")
        else:
            totals_composite = (flow["score"] * 0.5 + shocks["score"] * 0.3 + time_decay["score"] * 0.2)

        if over:
            over_prob = american_to_implied_prob(over.get("odds", -110))
            over_edge = (totals_composite - 0.5) * 10
            edges["total_over"] = {
                "line": over.get("line"),
                "odds": over.get("odds"),
                "implied_prob": round(over_prob, 4),
                "edge_pct": round(over_edge, 2),
                "confidence": get_confidence_rating(over_edge, totals_composite)
            }
            # Add expected total from game_env if available
            if game_env and game_env.get("expected_total"):
                edges["total_over"]["expected_total"] = game_env["expected_total"]

        if under:
            under_prob = american_to_implied_prob(under.get("odds", -110))
            under_edge = (0.5 - totals_composite) * 10
            edges["total_under"] = {
                "line": under.get("line"),
                "odds": under.get("odds"),
                "implied_prob": round(under_prob, 4),
                "edge_pct": round(under_edge, 2),
                "confidence": get_confidence_rating(under_edge, totals_composite)
            }
            if game_env and game_env.get("expected_total"):
                edges["total_under"]["expected_total"] = game_env["expected_total"]
    
    best_bet = None
    best_edge = 0
    
    for market_key, edge_data in edges.items():
        if edge_data["confidence"] in ["EDGE", "STRONG", "RARE"]:
            if abs(edge_data["edge_pct"]) > abs(best_edge):
                best_edge = edge_data["edge_pct"]
                best_bet = market_key
    
    # Build pillars dict (all 6 pillars)
    pillars_dict = {
        "execution": execution,
        "incentives": incentives,
        "shocks": shocks,
        "time_decay": time_decay,
        "flow": flow,
        "game_environment": game_env,
    }

    overall_confidence = get_confidence_rating(best_edge, composite) if best_bet else "PASS"
    analyzed_at = datetime.now(timezone.utc).isoformat()

    # === CALIBRATION LOG ===
    # JSON-formatted single-line output for batch analysis of score distributions
    calibration_data = {
        "game_id": game_id,
        "sport": sport,
        "composite": round(composite, 3),
        "confidence": overall_confidence,
        "edge_pct": best_edge,
        "pillars": {
            "execution": round(execution["score"], 3),
            "incentives": round(incentives["score"], 3),
            "shocks": round(shocks["score"], 3),
            "time_decay": round(time_decay["score"], 3),
            "flow": round(flow["score"], 3),
            "game_environment": round(game_env["score"], 3),
        },
        "timestamp": analyzed_at,
    }
    logger.info(f"CALIBRATION: {json.dumps(calibration_data)}")

    # Get sport-specific weights for return value
    sport_normalized = SPORT_KEY_TO_LEAGUE.get(sport, sport.upper())
    sport_weights = SPORT_WEIGHTS.get(sport_normalized, DEFAULT_WEIGHTS)

    return {
        "game_id": game_id,
        "sport": sport,
        "home_team": home_team,
        "away_team": away_team,
        "commence_time": game_time.isoformat(),
        "pillars": pillars_dict,
        "pillar_scores": pillar_scores,
        "pillar_weights": sport_weights,
        "pillars_by_market": pillars_by_market,  # Market×Period specific composites
        "composite_score": round(composite, 3),
        "consensus_odds": consensus,
        "edges": edges,
        "best_bet": best_bet,
        "best_edge": best_edge,
        "overall_confidence": overall_confidence,
        "analyzed_at": analyzed_at,
    }


def analyze_all_games(sport: str) -> list[dict]:
    """Analyze all upcoming games for a sport with ALL markets (including extended)."""
    # Use get_all_markets() instead of get_upcoming_games() to include extended markets
    all_markets_data = odds_client.get_all_markets(sport)
    games = all_markets_data.get("games", [])
    
    logger.info(f"Analyzing {len(games)} games for {sport} with extended markets")
    
    analyses = []
    for game in games:
        try:
            analysis = analyze_game(game, sport)
            analyses.append(analysis)
        except Exception as e:
            logger.error(f"Error analyzing game {game.get('id')}: {e}")
            continue
    
    return analyses


def analyze_all_sports() -> dict[str, list[dict]]:
    """Analyze all upcoming games across all sports."""
    from config import ODDS_API_SPORTS
    
    all_analyses = {}
    for sport in ODDS_API_SPORTS.keys():
        logger.info(f"Analyzing {sport}...")
        analyses = analyze_all_games(sport)
        all_analyses[sport] = analyses
        logger.info(f"Completed {len(analyses)} games for {sport}")
    
    return all_analyses