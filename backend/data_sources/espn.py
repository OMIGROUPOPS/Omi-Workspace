"""
ESPN API Data Source
Fetches injuries, standings, schedules, and team info from ESPN's free API.
No API key required.
"""
import httpx
from datetime import datetime, timezone, timedelta
from typing import Optional
import logging

from config import ESPN_API_BASE, ESPN_SPORTS

logger = logging.getLogger(__name__)


class ESPNClient:
    """Client for ESPN's free API endpoints."""
    
    def __init__(self):
        self.base_url = ESPN_API_BASE
        self.client = httpx.Client(timeout=30.0)
        self._cache = {}
        self._cache_ttl = 300
    
    def _get_sport_path(self, sport: str) -> tuple[str, str]:
        """Get ESPN sport/league path for a sport key."""
        return ESPN_SPORTS.get(sport, (None, None))
    
    def _request(self, endpoint: str, cache_key: str = None) -> Optional[dict]:
        """Make a request to ESPN API with optional caching."""
        if cache_key and cache_key in self._cache:
            cached_at, data = self._cache[cache_key]
            if (datetime.now() - cached_at).seconds < self._cache_ttl:
                return data
        
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if cache_key:
                self._cache[cache_key] = (datetime.now(), data)
            
            return data
        except httpx.HTTPError as e:
            logger.error(f"ESPN API error: {e}")
            return None
    
    def get_injuries(self, sport: str) -> list[dict]:
        """Get injury report for a sport."""
        sport_type, league = self._get_sport_path(sport)
        if not sport_type:
            return []
        
        data = self._request(f"{sport_type}/{league}/injuries", f"injuries_{sport}")
        if not data:
            return []
        
        injuries = []
        for team in data.get("injuries", []):
            team_info = team.get("team", {})
            team_id = team_info.get("id")
            team_name = team_info.get("displayName")
            
            for injury in team.get("injuries", []):
                athlete = injury.get("athlete", {})
                injuries.append({
                    "team_id": team_id,
                    "team_name": team_name,
                    "player_name": athlete.get("displayName"),
                    "position": athlete.get("position", {}).get("abbreviation"),
                    "status": injury.get("status"),
                    "injury_type": injury.get("type", {}).get("text", ""),
                    "details": injury.get("details", {}).get("detail", "")
                })
        
        return injuries
    
    def get_team_injury_impact(self, sport: str, team_name: str) -> dict:
        """Calculate injury impact score for a team."""
        default_response = {
            "impact_score": 0.0,
            "out_count": 0,
            "questionable_count": 0,
            "key_players_out": []
        }
        
        if not team_name:
            return default_response
        
        injuries = self.get_injuries(sport)
        team_injuries = [i for i in injuries if i.get("team_name") and team_name.lower() in i["team_name"].lower()]
        
        if not team_injuries:
            return default_response
        
        status_weights = {"Out": 1.0, "Doubtful": 0.8, "Questionable": 0.4, "Probable": 0.1}
        position_importance = {
            "QB": 3.0, "RB": 1.5, "WR": 1.2, "TE": 1.0, "OL": 1.0, "DL": 1.0, "LB": 1.0, "CB": 1.2, "S": 1.0,
            "PG": 2.0, "SG": 1.5, "SF": 1.5, "PF": 1.5, "C": 1.8,
            "G": 3.0, "D": 1.5, "LW": 1.2, "RW": 1.2,
        }
        
        total_impact = 0.0
        out_count = 0
        questionable_count = 0
        key_players = []
        
        for injury in team_injuries:
            status = injury.get("status", "")
            pos = injury.get("position", "")
            
            status_weight = status_weights.get(status, 0.5)
            pos_weight = position_importance.get(pos, 1.0)
            
            impact = status_weight * pos_weight
            total_impact += impact
            
            if status == "Out":
                out_count += 1
                if pos_weight >= 2.0 and injury.get("player_name"):
                    key_players.append(injury["player_name"])
            elif status in ["Questionable", "Doubtful"]:
                questionable_count += 1
        
        normalized_impact = min(total_impact / 10.0, 1.0)
        
        return {
            "impact_score": round(normalized_impact, 3),
            "out_count": out_count,
            "questionable_count": questionable_count,
            "key_players_out": key_players
        }
    
    def get_standings(self, sport: str) -> list[dict]:
        """Get current standings for a sport."""
        sport_type, league = self._get_sport_path(sport)
        if not sport_type:
            return []
        
        data = self._request(f"{sport_type}/{league}/standings", f"standings_{sport}")
        if not data:
            return []
        
        standings = []
        for group in data.get("children", []):
            for subgroup in group.get("standings", {}).get("entries", []):
                team = subgroup.get("team", {})
                stats = {s["name"]: s["value"] for s in subgroup.get("stats", [])}
                
                note = subgroup.get("note", {}).get("description", "").lower() if subgroup.get("note") else ""
                clinched = "clinched" in note
                eliminated = "eliminated" in note
                
                standings.append({
                    "team_id": team.get("id"),
                    "team_name": team.get("displayName"),
                    "wins": int(stats.get("wins", 0)),
                    "losses": int(stats.get("losses", 0)),
                    "win_pct": float(stats.get("winPercent", 0)),
                    "playoff_seed": int(stats.get("playoffSeed", 0)) or None,
                    "games_back": float(stats.get("gamesBehind", 0)),
                    "streak": stats.get("streak", ""),
                    "clinched_playoff": clinched,
                    "eliminated": eliminated
                })
        
        return standings
    
    def get_team_incentive_score(self, sport: str, team_name: str) -> dict:
        """Calculate incentive/motivation score for a team."""
        default_response = {
            "motivation_score": 0.5,
            "playoff_status": "unknown",
            "games_back": 0,
            "reasoning": "Team not found in standings"
        }
        
        if not team_name:
            return default_response
        
        standings = self.get_standings(sport)
        team_standing = None
        for s in standings:
            if s.get("team_name") and team_name.lower() in s["team_name"].lower():
                team_standing = s
                break
        
        if not team_standing:
            return default_response
        
        motivation = 0.5
        reasoning = []
        
        if team_standing["clinched_playoff"]:
            motivation -= 0.15
            reasoning.append("Already clinched - may rest players")
        elif team_standing["eliminated"]:
            motivation -= 0.25
            reasoning.append("Eliminated from playoff contention")
        elif team_standing["games_back"] <= 2:
            motivation += 0.2
            reasoning.append(f"In playoff race ({team_standing['games_back']} GB)")
        elif team_standing["games_back"] <= 5:
            motivation += 0.1
            reasoning.append(f"Still in contention ({team_standing['games_back']} GB)")
        
        streak = team_standing.get("streak", "")
        if streak and "W" in str(streak):
            try:
                win_streak = int(str(streak).replace("W", ""))
                if win_streak >= 5:
                    motivation += 0.1
                    reasoning.append(f"Hot streak ({streak})")
            except ValueError:
                pass
        elif streak and "L" in str(streak):
            try:
                loss_streak = int(str(streak).replace("L", ""))
                if loss_streak >= 5:
                    motivation += 0.05
                    reasoning.append(f"Cold streak - desperate ({streak})")
            except ValueError:
                pass
        
        motivation = max(0.0, min(1.0, motivation))
        
        playoff_status = "contending"
        if team_standing["clinched_playoff"]:
            playoff_status = "clinched"
        elif team_standing["eliminated"]:
            playoff_status = "eliminated"
        
        return {
            "motivation_score": round(motivation, 3),
            "playoff_status": playoff_status,
            "games_back": team_standing["games_back"],
            "reasoning": "; ".join(reasoning) if reasoning else "Neutral positioning"
        }
    
    def get_scoreboard(self, sport: str, date: str = None) -> list[dict]:
        """Get games for a given date (or today if not specified)."""
        sport_type, league = self._get_sport_path(sport)
        if not sport_type:
            return []
        
        endpoint = f"{sport_type}/{league}/scoreboard"
        if date:
            endpoint += f"?dates={date}"
        
        data = self._request(endpoint, f"scoreboard_{sport}_{date or 'today'}")
        if not data:
            return []
        
        games = []
        for event in data.get("events", []):
            competition = event.get("competitions", [{}])[0]
            competitors = competition.get("competitors", [])
            
            home = next((c for c in competitors if c.get("homeAway") == "home"), {})
            away = next((c for c in competitors if c.get("homeAway") == "away"), {})
            
            venue = competition.get("venue", {})
            
            event_date = event.get("date", "")
            try:
                start_time = datetime.fromisoformat(event_date.replace("Z", "+00:00"))
            except:
                start_time = datetime.now(timezone.utc)
            
            games.append({
                "game_id": event.get("id"),
                "home_team": home.get("team", {}).get("displayName"),
                "away_team": away.get("team", {}).get("displayName"),
                "home_team_id": home.get("team", {}).get("id"),
                "away_team_id": away.get("team", {}).get("id"),
                "start_time": start_time,
                "status": event.get("status", {}).get("type", {}).get("name"),
                "venue": {
                    "name": venue.get("fullName"),
                    "city": venue.get("address", {}).get("city"),
                    "state": venue.get("address", {}).get("state"),
                    "indoor": venue.get("indoor", True)
                }
            })
        
        return games
    
    def get_team_schedule(self, sport: str, team_id: str, days_back: int = 14) -> list[dict]:
        """Get a team's recent and upcoming games for rest/travel analysis."""
        games = []
        today = datetime.now(timezone.utc)
        
        for day_offset in range(-days_back, 8):
            check_date = today + timedelta(days=day_offset)
            date_str = check_date.strftime("%Y%m%d")
            
            day_games = self.get_scoreboard(sport, date_str)
            for game in day_games:
                if game.get("home_team_id") == team_id or game.get("away_team_id") == team_id:
                    game["team_is_home"] = game.get("home_team_id") == team_id
                    games.append(game)
        
        return sorted(games, key=lambda g: g.get("start_time", datetime.now(timezone.utc)))
    
    def calculate_rest_and_travel(self, sport: str, team_name: str, game_time: datetime) -> dict:
        """Calculate rest days and travel situation for a team."""
        default_response = {
            "days_rest": 3,
            "is_back_to_back": False,
            "is_third_in_four": False,
            "travel_situation": "unknown",
            "fatigue_score": 0.5
        }
        
        if not team_name:
            return default_response
        
        standings = self.get_standings(sport)
        team_id = None
        for s in standings:
            if s.get("team_name") and team_name.lower() in s["team_name"].lower():
                team_id = s["team_id"]
                break
        
        if not team_id:
            return default_response
        
        schedule = self.get_team_schedule(sport, team_id)
        
        past_games = [g for g in schedule if g.get("start_time") and g["start_time"] < game_time]
        past_games = sorted(past_games, key=lambda g: g["start_time"], reverse=True)
        
        if not past_games:
            return {
                "days_rest": 7,
                "is_back_to_back": False,
                "is_third_in_four": False,
                "travel_situation": "unknown",
                "fatigue_score": 0.2
            }
        
        last_game = past_games[0]
        days_rest = (game_time - last_game["start_time"]).days
        
        is_b2b = days_rest <= 1
        
        games_in_4_days = [g for g in past_games[:3] if (game_time - g["start_time"]).days <= 4]
        is_third_in_four = len(games_in_4_days) >= 2
        
        travel_situation = "home_stand"
        if len(past_games) >= 2:
            recent_away = sum(1 for g in past_games[:3] if not g.get("team_is_home", True))
            if recent_away >= 2:
                travel_situation = "road_trip"
            elif recent_away == 1 and not past_games[0].get("team_is_home", True):
                travel_situation = "travel_day"
        
        fatigue = 0.3
        if is_b2b:
            fatigue += 0.35
        elif days_rest == 2:
            fatigue += 0.15
        elif days_rest >= 4:
            fatigue -= 0.15
        
        if is_third_in_four:
            fatigue += 0.15
        
        if travel_situation == "road_trip":
            fatigue += 0.1
        elif travel_situation == "travel_day":
            fatigue += 0.05
        
        fatigue = max(0.0, min(1.0, fatigue))
        
        return {
            "days_rest": days_rest,
            "is_back_to_back": is_b2b,
            "is_third_in_four": is_third_in_four,
            "travel_situation": travel_situation,
            "fatigue_score": round(fatigue, 3)
        }


espn_client = ESPNClient()