"""
OMI Edge - ESPN Score Fetcher & Auto-Grader
Fetches final scores from ESPN (FREE) and auto-grades games
"""

import httpx
from datetime import datetime, timezone, timedelta
from typing import Optional
import re

# ESPN API endpoints (completely free, no auth needed)
ESPN_ENDPOINTS = {
    "NFL": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
    "NBA": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    "NHL": "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard",
    "NCAAF": "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard",
    "NCAAB": "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard",
}

# Team name normalization (ESPN name -> common variations)
TEAM_ALIASES = {
    # NFL
    "Arizona Cardinals": ["Cardinals", "Arizona", "ARI"],
    "Atlanta Falcons": ["Falcons", "Atlanta", "ATL"],
    "Baltimore Ravens": ["Ravens", "Baltimore", "BAL"],
    "Buffalo Bills": ["Bills", "Buffalo", "BUF"],
    "Carolina Panthers": ["Panthers", "Carolina", "CAR"],
    "Chicago Bears": ["Bears", "Chicago", "CHI"],
    "Cincinnati Bengals": ["Bengals", "Cincinnati", "CIN"],
    "Cleveland Browns": ["Browns", "Cleveland", "CLE"],
    "Dallas Cowboys": ["Cowboys", "Dallas", "DAL"],
    "Denver Broncos": ["Broncos", "Denver", "DEN"],
    "Detroit Lions": ["Lions", "Detroit", "DET"],
    "Green Bay Packers": ["Packers", "Green Bay", "GB"],
    "Houston Texans": ["Texans", "Houston", "HOU"],
    "Indianapolis Colts": ["Colts", "Indianapolis", "IND"],
    "Jacksonville Jaguars": ["Jaguars", "Jacksonville", "JAX"],
    "Kansas City Chiefs": ["Chiefs", "Kansas City", "KC"],
    "Las Vegas Raiders": ["Raiders", "Las Vegas", "LV"],
    "Los Angeles Chargers": ["Chargers", "LA Chargers", "LAC"],
    "Los Angeles Rams": ["Rams", "LA Rams", "LAR"],
    "Miami Dolphins": ["Dolphins", "Miami", "MIA"],
    "Minnesota Vikings": ["Vikings", "Minnesota", "MIN"],
    "New England Patriots": ["Patriots", "New England", "NE"],
    "New Orleans Saints": ["Saints", "New Orleans", "NO"],
    "New York Giants": ["Giants", "NY Giants", "NYG"],
    "New York Jets": ["Jets", "NY Jets", "NYJ"],
    "Philadelphia Eagles": ["Eagles", "Philadelphia", "PHI"],
    "Pittsburgh Steelers": ["Steelers", "Pittsburgh", "PIT"],
    "San Francisco 49ers": ["49ers", "San Francisco", "SF"],
    "Seattle Seahawks": ["Seahawks", "Seattle", "SEA"],
    "Tampa Bay Buccaneers": ["Buccaneers", "Tampa Bay", "TB"],
    "Tennessee Titans": ["Titans", "Tennessee", "TEN"],
    "Washington Commanders": ["Commanders", "Washington", "WAS"],
    
    # NBA
    "Atlanta Hawks": ["Hawks", "Atlanta"],
    "Boston Celtics": ["Celtics", "Boston"],
    "Brooklyn Nets": ["Nets", "Brooklyn"],
    "Charlotte Hornets": ["Hornets", "Charlotte"],
    "Chicago Bulls": ["Bulls", "Chicago"],
    "Cleveland Cavaliers": ["Cavaliers", "Cleveland", "Cavs"],
    "Dallas Mavericks": ["Mavericks", "Dallas", "Mavs"],
    "Denver Nuggets": ["Nuggets", "Denver"],
    "Detroit Pistons": ["Pistons", "Detroit"],
    "Golden State Warriors": ["Warriors", "Golden State"],
    "Houston Rockets": ["Rockets", "Houston"],
    "Indiana Pacers": ["Pacers", "Indiana"],
    "LA Clippers": ["Clippers", "Los Angeles Clippers"],
    "Los Angeles Lakers": ["Lakers", "LA Lakers"],
    "Memphis Grizzlies": ["Grizzlies", "Memphis"],
    "Miami Heat": ["Heat", "Miami"],
    "Milwaukee Bucks": ["Bucks", "Milwaukee"],
    "Minnesota Timberwolves": ["Timberwolves", "Minnesota", "Wolves"],
    "New Orleans Pelicans": ["Pelicans", "New Orleans"],
    "New York Knicks": ["Knicks", "New York"],
    "Oklahoma City Thunder": ["Thunder", "Oklahoma City", "OKC"],
    "Orlando Magic": ["Magic", "Orlando"],
    "Philadelphia 76ers": ["76ers", "Philadelphia", "Sixers"],
    "Phoenix Suns": ["Suns", "Phoenix"],
    "Portland Trail Blazers": ["Trail Blazers", "Portland", "Blazers"],
    "Sacramento Kings": ["Kings", "Sacramento"],
    "San Antonio Spurs": ["Spurs", "San Antonio"],
    "Toronto Raptors": ["Raptors", "Toronto"],
    "Utah Jazz": ["Jazz", "Utah"],
    "Washington Wizards": ["Wizards", "Washington"],
    
    # NHL
    "Anaheim Ducks": ["Ducks", "Anaheim"],
    "Arizona Coyotes": ["Coyotes", "Arizona"],
    "Boston Bruins": ["Bruins", "Boston"],
    "Buffalo Sabres": ["Sabres", "Buffalo"],
    "Calgary Flames": ["Flames", "Calgary"],
    "Carolina Hurricanes": ["Hurricanes", "Carolina"],
    "Chicago Blackhawks": ["Blackhawks", "Chicago"],
    "Colorado Avalanche": ["Avalanche", "Colorado"],
    "Columbus Blue Jackets": ["Blue Jackets", "Columbus"],
    "Dallas Stars": ["Stars", "Dallas"],
    "Detroit Red Wings": ["Red Wings", "Detroit"],
    "Edmonton Oilers": ["Oilers", "Edmonton"],
    "Florida Panthers": ["Panthers", "Florida"],
    "Los Angeles Kings": ["Kings", "Los Angeles", "LA Kings"],
    "Minnesota Wild": ["Wild", "Minnesota"],
    "Montreal Canadiens": ["Canadiens", "Montreal"],
    "Nashville Predators": ["Predators", "Nashville"],
    "New Jersey Devils": ["Devils", "New Jersey"],
    "New York Islanders": ["Islanders", "NY Islanders"],
    "New York Rangers": ["Rangers", "NY Rangers"],
    "Ottawa Senators": ["Senators", "Ottawa"],
    "Philadelphia Flyers": ["Flyers", "Philadelphia"],
    "Pittsburgh Penguins": ["Penguins", "Pittsburgh"],
    "San Jose Sharks": ["Sharks", "San Jose"],
    "Seattle Kraken": ["Kraken", "Seattle"],
    "St. Louis Blues": ["Blues", "St. Louis"],
    "Tampa Bay Lightning": ["Lightning", "Tampa Bay"],
    "Toronto Maple Leafs": ["Maple Leafs", "Toronto"],
    "Vancouver Canucks": ["Canucks", "Vancouver"],
    "Vegas Golden Knights": ["Golden Knights", "Vegas"],
    "Washington Capitals": ["Capitals", "Washington"],
    "Winnipeg Jets": ["Jets", "Winnipeg"],
}


def normalize_team_name(name: str) -> str:
    """Normalize team name to a standard format for matching."""
    # Remove common prefixes/suffixes
    name = name.strip()
    name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
    return name.lower()


def teams_match(espn_team: str, our_team: str) -> bool:
    """Check if ESPN team name matches our team name."""
    espn_norm = normalize_team_name(espn_team)
    our_norm = normalize_team_name(our_team)
    
    # Direct match
    if espn_norm == our_norm:
        return True
    
    # Check if one contains the other
    if espn_norm in our_norm or our_norm in espn_norm:
        return True
    
    # Check aliases
    for full_name, aliases in TEAM_ALIASES.items():
        full_norm = normalize_team_name(full_name)
        alias_norms = [normalize_team_name(a) for a in aliases]
        
        # If ESPN matches this team
        if espn_norm == full_norm or espn_norm in alias_norms:
            # Check if our team also matches
            if our_norm == full_norm or our_norm in alias_norms:
                return True
            # Check partial match
            for alias in alias_norms:
                if alias in our_norm or our_norm in alias:
                    return True
    
    return False


class ESPNScoreFetcher:
    def __init__(self):
        self.client = httpx.Client(timeout=30)
    
    def get_scores(self, sport: str, date: Optional[str] = None) -> list[dict]:
        """
        Fetch scores from ESPN for a given sport.
        
        Args:
            sport: One of NFL, NBA, NHL, NCAAF, NCAAB
            date: Optional date string in YYYYMMDD format. Defaults to today.
        
        Returns:
            List of game dicts with home/away teams and scores
        """
        if sport not in ESPN_ENDPOINTS:
            print(f"[ESPN] Unknown sport: {sport}")
            return []
        
        url = ESPN_ENDPOINTS[sport]
        params = {}
        if date:
            params["dates"] = date
        
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"[ESPN] Error fetching {sport} scores: {e}")
            return []
        
        games = []
        events = data.get("events", [])
        
        for event in events:
            try:
                competition = event.get("competitions", [{}])[0]
                status = competition.get("status", {})
                status_type = status.get("type", {}).get("name", "")
                
                # Get competitors
                competitors = competition.get("competitors", [])
                if len(competitors) != 2:
                    continue
                
                home_team = None
                away_team = None
                home_score = None
                away_score = None
                
                for comp in competitors:
                    team_name = comp.get("team", {}).get("displayName", "")
                    score = comp.get("score", "0")
                    is_home = comp.get("homeAway", "") == "home"
                    
                    try:
                        score_int = int(score) if score else 0
                    except ValueError:
                        score_int = 0
                    
                    if is_home:
                        home_team = team_name
                        home_score = score_int
                    else:
                        away_team = team_name
                        away_score = score_int
                
                game_data = {
                    "espn_id": event.get("id"),
                    "sport": sport,
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": home_score,
                    "away_score": away_score,
                    "status": status_type,  # "STATUS_SCHEDULED", "STATUS_IN_PROGRESS", "STATUS_FINAL"
                    "is_final": status_type == "STATUS_FINAL",
                    "start_time": event.get("date"),
                    "venue": competition.get("venue", {}).get("fullName", ""),
                }
                
                games.append(game_data)
                
            except Exception as e:
                print(f"[ESPN] Error parsing game: {e}")
                continue
        
        return games
    
    def get_final_scores(self, sport: str, date: Optional[str] = None) -> list[dict]:
        """Get only completed games."""
        all_games = self.get_scores(sport, date)
        return [g for g in all_games if g["is_final"]]
    
    def find_matching_game(self, sport: str, home_team: str, away_team: str, date: Optional[str] = None) -> Optional[dict]:
        """
        Find a specific game by team names.
        
        Args:
            sport: Sport key
            home_team: Our home team name
            away_team: Our away team name
            date: Optional date in YYYYMMDD format
        
        Returns:
            Game dict if found, None otherwise
        """
        games = self.get_scores(sport, date)
        
        for game in games:
            if teams_match(game["home_team"], home_team) and teams_match(game["away_team"], away_team):
                return game
        
        # Try swapped (in case home/away is different)
        for game in games:
            if teams_match(game["home_team"], away_team) and teams_match(game["away_team"], home_team):
                # Swap the scores to match our perspective
                return {
                    **game,
                    "home_team": game["away_team"],
                    "away_team": game["home_team"],
                    "home_score": game["away_score"],
                    "away_score": game["home_score"],
                    "swapped": True,
                }
        
        return None


class AutoGrader:
    """Automatically grades games using ESPN scores."""
    
    def __init__(self, results_tracker):
        """
        Args:
            results_tracker: Instance of ResultsTracker from backend_results_tracker.py
        """
        self.espn = ESPNScoreFetcher()
        self.tracker = results_tracker
    
    def grade_completed_games(self, sport: Optional[str] = None) -> dict:
        """
        Find and grade all completed games that haven't been graded yet.
        
        Args:
            sport: Optional sport to filter by. If None, checks all sports.
        
        Returns:
            Dict with counts of graded games
        """
        sports_to_check = [sport] if sport else list(ESPN_ENDPOINTS.keys())
        
        results = {
            "checked": 0,
            "graded": 0,
            "already_graded": 0,
            "not_found": 0,
            "errors": 0,
            "details": [],
        }
        
        for sport_key in sports_to_check:
            # Get ungraded games from our database
            ungraded = self._get_ungraded_games(sport_key)
            results["checked"] += len(ungraded)
            
            if not ungraded:
                continue
            
            # Get today's and yesterday's scores from ESPN
            today = datetime.now().strftime("%Y%m%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            
            espn_games_today = self.espn.get_final_scores(sport_key, today)
            espn_games_yesterday = self.espn.get_final_scores(sport_key, yesterday)
            espn_games = espn_games_today + espn_games_yesterday
            
            for game in ungraded:
                game_id = game.get("game_id")
                home_team = game.get("home_team")
                away_team = game.get("away_team")
                
                # Find matching ESPN game
                espn_match = None
                for eg in espn_games:
                    if teams_match(eg["home_team"], home_team) and teams_match(eg["away_team"], away_team):
                        espn_match = eg
                        break
                    # Check swapped
                    if teams_match(eg["home_team"], away_team) and teams_match(eg["away_team"], home_team):
                        espn_match = {
                            **eg,
                            "home_score": eg["away_score"],
                            "away_score": eg["home_score"],
                        }
                        break
                
                if not espn_match:
                    results["not_found"] += 1
                    continue
                
                if not espn_match["is_final"]:
                    continue
                
                # Grade the game
                try:
                    graded = self.tracker.grade_game(
                        game_id,
                        espn_match["home_score"],
                        espn_match["away_score"]
                    )
                    
                    if graded:
                        results["graded"] += 1
                        results["details"].append({
                            "game_id": game_id,
                            "matchup": f"{away_team} @ {home_team}",
                            "score": f"{espn_match['away_score']}-{espn_match['home_score']}",
                            "best_bet_result": graded.get("best_bet_result"),
                        })
                except Exception as e:
                    print(f"[AutoGrader] Error grading {game_id}: {e}")
                    results["errors"] += 1
        
        return results
    
    def _get_ungraded_games(self, sport: str) -> list[dict]:
        """Get games that need grading (have predictions but no final score)."""
        # Games where commence_time is in the past and graded_at is null
        cutoff = datetime.now(timezone.utc).isoformat()
        
        result = self.tracker.client.table("game_results").select("*").eq(
            "sport_key", sport
        ).is_("graded_at", "null").lt("commence_time", cutoff).execute()
        
        return result.data or []
    
    def snapshot_upcoming_games(self, sport: Optional[str] = None, minutes_before: int = 30) -> dict:
        """
        Snapshot predictions for games starting soon.
        
        Args:
            sport: Optional sport filter
            minutes_before: How many minutes before game time to snapshot
        
        Returns:
            Dict with counts
        """
        sports_to_check = [sport] if sport else list(ESPN_ENDPOINTS.keys())
        
        results = {
            "checked": 0,
            "snapshotted": 0,
            "already_exists": 0,
            "errors": 0,
        }
        
        now = datetime.now(timezone.utc)
        window_start = now
        window_end = now + timedelta(minutes=minutes_before)
        
        for sport_key in sports_to_check:
            # Get predictions for games starting soon
            preds = self.tracker.client.table("predictions").select("*").eq(
                "sport_key", sport_key
            ).gte("commence_time", window_start.isoformat()).lte(
                "commence_time", window_end.isoformat()
            ).execute()
            
            predictions = preds.data or []
            results["checked"] += len(predictions)
            
            for pred in predictions:
                game_id = pred.get("game_id")
                
                # Check if already snapshotted
                existing = self.tracker.client.table("game_results").select("game_id").eq(
                    "game_id", game_id
                ).execute()
                
                if existing.data:
                    results["already_exists"] += 1
                    continue
                
                try:
                    self.tracker.snapshot_prediction_at_close(game_id, sport_key)
                    results["snapshotted"] += 1
                except Exception as e:
                    print(f"[AutoGrader] Error snapshotting {game_id}: {e}")
                    results["errors"] += 1
        
        return results


# Add these endpoints to server.py:
"""
from espn_scores import ESPNScoreFetcher, AutoGrader
from results_tracker import ResultsTracker

@app.get("/api/espn/scores/{sport}")
async def get_espn_scores(sport: str, date: str = None):
    '''Get scores from ESPN (free, no API cost)'''
    fetcher = ESPNScoreFetcher()
    scores = fetcher.get_scores(sport.upper(), date)
    return {"sport": sport, "games": scores, "count": len(scores)}

@app.get("/api/espn/final/{sport}")
async def get_espn_final_scores(sport: str, date: str = None):
    '''Get only final scores from ESPN'''
    fetcher = ESPNScoreFetcher()
    scores = fetcher.get_final_scores(sport.upper(), date)
    return {"sport": sport, "games": scores, "count": len(scores)}

@app.post("/api/results/auto-grade")
async def auto_grade_games(sport: str = None):
    '''Automatically grade completed games using ESPN scores'''
    tracker = ResultsTracker()
    grader = AutoGrader(tracker)
    results = grader.grade_completed_games(sport.upper() if sport else None)
    return results

@app.post("/api/results/snapshot-upcoming")
async def snapshot_upcoming(sport: str = None, minutes: int = 30):
    '''Snapshot predictions for games starting soon'''
    tracker = ResultsTracker()
    grader = AutoGrader(tracker)
    results = grader.snapshot_upcoming_games(sport.upper() if sport else None, minutes)
    return results
"""