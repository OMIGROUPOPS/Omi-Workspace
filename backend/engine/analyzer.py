"""
OMI Edge Analysis Engine

The core engine that:
1. Fetches data from all sources
2. Calculates all 5 pillar scores
3. Computes composite score and edge percentage
4. Determines confidence rating
"""
from datetime import datetime, timezone
from typing import Optional
import logging

from config import PILLAR_WEIGHTS, EDGE_THRESHOLDS
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
        query_result = db.client.table("line_snapshots").select(
            "line, snapshot_time"
        ).eq(
            "game_id", game_id
        ).eq(
            "market_type", "spread"
        ).eq(
            "market_period", "full"
        ).order(
            "snapshot_time", desc=False
        ).execute()

        snapshots = query_result.data or []

        if snapshots:
            # Opening line = earliest snapshot
            result["opening_line"] = snapshots[0].get("line")

            # Current line = most recent snapshot
            result["current_line"] = snapshots[-1].get("line")

            # Build line_snapshots list for shocks/flow pillars
            # Format: list of {timestamp, line} dicts
            result["line_snapshots"] = [
                {
                    "timestamp": snap.get("snapshot_time"),
                    "line": snap.get("line")
                }
                for snap in snapshots
                if snap.get("line") is not None
            ]

            logger.info(f"  Line context for {game_id}: opening={result['opening_line']}, "
                       f"current={result['current_line']}, {len(result['line_snapshots'])} snapshots")
        else:
            logger.debug(f"  No line snapshots found for {game_id}")

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


def calculate_composite_score(pillar_scores: dict) -> float:
    """Calculate weighted composite score from all pillars."""
    composite = 0.0
    total_weight = 0.0
    
    for pillar, weight in PILLAR_WEIGHTS.items():
        if pillar in pillar_scores:
            composite += pillar_scores[pillar] * weight
            total_weight += weight
    
    if total_weight == 0:
        return 0.5
    
    return composite / total_weight * (sum(PILLAR_WEIGHTS.values()) / total_weight)


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
    """Full analysis of a single game using all 5 pillars."""
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

    execution = calculate_execution_score(
        sport=sport,
        home_team=home_team,
        away_team=away_team,
        game_time=game_time,
        venue=venue
    )
    
    incentives = calculate_incentives_score(
        sport=sport,
        home_team=home_team,
        away_team=away_team,
        game_time=game_time
    )
    
    # Calculate consensus odds (now includes extended markets)
    consensus = odds_client.calculate_consensus_odds(game)
    current_line = None
    if consensus.get("spreads", {}).get("home"):
        current_line = consensus["spreads"]["home"]["line"]
    
    shocks = calculate_shocks_score(
        sport=sport,
        home_team=home_team,
        away_team=away_team,
        game_time=game_time,
        current_line=current_line,
        opening_line=opening_line,
        line_movement_history=line_snapshots
    )
    
    time_decay = calculate_time_decay_score(
        sport=sport,
        home_team=home_team,
        away_team=away_team,
        game_time=game_time
    )
    
    flow = calculate_flow_score(
        game=game,
        opening_line=opening_line,
        line_snapshots=line_snapshots
    )

    # Game Environment (for totals analysis)
    # Fetch sport-specific stats
    game_env = None
    nhl_stats = None
    total_line = None

    # Get total line from consensus
    if consensus.get("totals", {}).get("over"):
        total_line = consensus["totals"]["over"].get("line")

    if sport == "icehockey_nhl":
        # Fetch NHL stats for environment calculation
        # Extract team abbreviations from team names
        home_abbr = _extract_team_abbr(home_team, "NHL")
        away_abbr = _extract_team_abbr(away_team, "NHL")

        if home_abbr and away_abbr:
            nhl_stats = fetch_nhl_game_stats_sync(home_abbr, away_abbr)

        game_env = calculate_game_environment_score(
            sport="NHL",
            home_team=home_team,
            away_team=away_team,
            total_line=total_line,
            nhl_stats=nhl_stats,
        )
        logger.info(f"  Game Environment: {game_env['score']:.3f} - {game_env.get('reasoning', 'N/A')}")

    elif sport == "americanfootball_nfl":
        # NFL game environment with weather
        game_env = calculate_game_environment_score(
            sport="NFL",
            home_team=home_team,
            away_team=away_team,
            total_line=total_line,
            game_time=game_time,
        )
        logger.info(f"  Game Environment: {game_env['score']:.3f} - {game_env.get('reasoning', 'N/A')}")

    pillar_scores = {
        "execution": execution["score"],
        "incentives": incentives["score"],
        "shocks": shocks["score"],
        "time_decay": time_decay["score"],
        "flow": flow["score"],
    }

    # Debug: Log pillar scores and reasoning
    logger.info(f"  Pillar scores for {home_team}:")
    logger.info(f"    Execution: {execution['score']:.3f} - {execution.get('reasoning', 'N/A')}")
    logger.info(f"    Incentives: {incentives['score']:.3f} - {incentives.get('reasoning', 'N/A')}")
    logger.info(f"    Shocks: {shocks['score']:.3f} - {shocks.get('reasoning', 'N/A')}")
    logger.info(f"    Time Decay: {time_decay['score']:.3f} - {time_decay.get('reasoning', 'N/A')}")
    logger.info(f"    Flow: {flow['score']:.3f} - {flow.get('reasoning', 'N/A')}")

    composite = calculate_composite_score(pillar_scores)
    
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
    
    # Build pillars dict
    pillars_dict = {
        "execution": execution,
        "incentives": incentives,
        "shocks": shocks,
        "time_decay": time_decay,
        "flow": flow,
    }
    # Add game_env if calculated (NHL, NBA)
    if game_env:
        pillars_dict["game_environment"] = game_env

    return {
        "game_id": game_id,
        "sport": sport,
        "home_team": home_team,
        "away_team": away_team,
        "commence_time": game_time.isoformat(),
        "pillars": pillars_dict,
        "pillar_scores": pillar_scores,
        "pillar_weights": PILLAR_WEIGHTS,
        "composite_score": round(composite, 3),
        "consensus_odds": consensus,
        "edges": edges,
        "best_bet": best_bet,
        "best_edge": best_edge,
        "overall_confidence": get_confidence_rating(best_edge, composite) if best_bet else "PASS",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
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