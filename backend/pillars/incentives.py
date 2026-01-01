"""
Pillar 2: Incentives & Strategic Behavior
Weight: 0.15

Measures: Motivation asymmetries between teams
- Playoff positioning (fighting for spot vs clinched)
- Tank scenarios (eliminated teams may rest players)
- Rivalry games (heightened motivation)
"""
from datetime import datetime
import logging

from data_sources.espn import espn_client

logger = logging.getLogger(__name__)

RIVALRIES = {
    "NFL": [
        ("Dallas Cowboys", "Washington Commanders"),
        ("Green Bay Packers", "Chicago Bears"),
        ("New England Patriots", "New York Jets"),
        ("Pittsburgh Steelers", "Baltimore Ravens"),
        ("San Francisco 49ers", "Seattle Seahawks"),
        ("Kansas City Chiefs", "Las Vegas Raiders"),
    ],
    "NBA": [
        ("Los Angeles Lakers", "Boston Celtics"),
        ("Los Angeles Lakers", "Los Angeles Clippers"),
        ("New York Knicks", "Brooklyn Nets"),
        ("Golden State Warriors", "Cleveland Cavaliers"),
        ("Miami Heat", "Boston Celtics"),
    ],
    "NHL": [
        ("Boston Bruins", "Montreal Canadiens"),
        ("Chicago Blackhawks", "Detroit Red Wings"),
        ("Pittsburgh Penguins", "Philadelphia Flyers"),
        ("Colorado Avalanche", "Detroit Red Wings"),
    ],
    "NCAAF": [
        ("Ohio State Buckeyes", "Michigan Wolverines"),
        ("Alabama Crimson Tide", "Auburn Tigers"),
        ("USC Trojans", "UCLA Bruins"),
        ("Texas Longhorns", "Oklahoma Sooners"),
    ],
    "NCAAB": [
        ("Duke Blue Devils", "North Carolina Tar Heels"),
        ("Kentucky Wildcats", "Louisville Cardinals"),
        ("Kansas Jayhawks", "Missouri Tigers"),
    ],
}


def is_rivalry_game(sport: str, team1: str, team2: str) -> bool:
    """Check if this matchup is a known rivalry."""
    sport_rivalries = RIVALRIES.get(sport, [])
    for r1, r2 in sport_rivalries:
        if (team1.lower() in r1.lower() or r1.lower() in team1.lower()) and \
           (team2.lower() in r2.lower() or r2.lower() in team2.lower()):
            return True
        if (team2.lower() in r1.lower() or r1.lower() in team2.lower()) and \
           (team1.lower() in r2.lower() or r2.lower() in team1.lower()):
            return True
    return False


def calculate_incentives_score(
    sport: str,
    home_team: str,
    away_team: str,
    game_time: datetime
) -> dict:
    """
    Calculate Pillar 2: Incentives & Strategic Behavior score.
    
    A score > 0.5 means AWAY team has motivation advantage
    A score < 0.5 means HOME team has motivation advantage
    A score = 0.5 means balanced motivation
    """
    home_incentive = espn_client.get_team_incentive_score(sport, home_team)
    away_incentive = espn_client.get_team_incentive_score(sport, away_team)
    
    home_motivation = home_incentive["motivation_score"]
    away_motivation = away_incentive["motivation_score"]
    
    rivalry = is_rivalry_game(sport, home_team, away_team)
    rivalry_boost = 0.1 if rivalry else 0.0
    
    if rivalry:
        home_motivation = min(1.0, home_motivation + rivalry_boost)
        away_motivation = min(1.0, away_motivation + rivalry_boost)
    
    motivation_differential = away_motivation - home_motivation
    
    tank_alert = False
    rest_alert = False
    
    if home_incentive["playoff_status"] == "eliminated" and away_incentive["playoff_status"] == "contending":
        tank_alert = True
        motivation_differential += 0.15
    elif away_incentive["playoff_status"] == "eliminated" and home_incentive["playoff_status"] == "contending":
        tank_alert = True
        motivation_differential -= 0.15
    
    if home_incentive["playoff_status"] == "clinched":
        rest_alert = True
        motivation_differential += 0.1
    if away_incentive["playoff_status"] == "clinched":
        rest_alert = True
        motivation_differential -= 0.1
    
    base_score = 0.5
    score = base_score + (motivation_differential * 0.5)
    score = max(0.0, min(1.0, score))
    
    reasoning_parts = []
    
    if rivalry:
        reasoning_parts.append("Rivalry game: heightened motivation for both teams")
    
    if tank_alert:
        reasoning_parts.append("Tank/elimination scenario detected")
    
    if rest_alert:
        reasoning_parts.append("Clinched team may rest players")
    
    if home_incentive["playoff_status"] == "contending":
        reasoning_parts.append(f"{home_team} fighting for playoff spot ({home_incentive['games_back']} GB)")
    
    if away_incentive["playoff_status"] == "contending":
        reasoning_parts.append(f"{away_team} fighting for playoff spot ({away_incentive['games_back']} GB)")
    
    if abs(motivation_differential) < 0.1 and not reasoning_parts:
        reasoning_parts.append("No significant motivation asymmetry")
    
    return {
        "score": round(score, 3),
        "home_motivation": round(home_motivation, 3),
        "away_motivation": round(away_motivation, 3),
        "is_rivalry": rivalry,
        "breakdown": {
            "home_incentive": home_incentive,
            "away_incentive": away_incentive,
            "motivation_differential": round(motivation_differential, 3),
            "tank_alert": tank_alert,
            "rest_alert": rest_alert
        },
        "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Balanced motivation levels"
    }


def get_incentive_edge_direction(score: float) -> str:
    """Interpret the incentives score."""
    if score < 0.45:
        return "home_edge"
    elif score > 0.55:
        return "away_edge"
    return "neutral"