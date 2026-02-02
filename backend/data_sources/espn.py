"""
ESPN API Data Source
Fetches injuries, standings, schedules, and team info from ESPN's free API.
No API key required.
"""
import httpx
from datetime import datetime, timezone, timedelta
from typing import Optional
import logging

from config import ESPN_API_BASE, ESPN_API_BASE_V2, ESPN_SPORTS

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

    def _request_standings(self, endpoint: str, cache_key: str = None) -> Optional[dict]:
        """Make a request to ESPN v2 API (for standings) with optional caching."""
        if cache_key and cache_key in self._cache:
            cached_at, data = self._cache[cache_key]
            if (datetime.now() - cached_at).seconds < self._cache_ttl:
                return data

        # Use the v2 base URL for standings
        url = f"{ESPN_API_BASE_V2}/{endpoint}"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            data = response.json()

            if cache_key:
                self._cache[cache_key] = (datetime.now(), data)

            return data
        except httpx.HTTPError as e:
            logger.error(f"ESPN v2 API error: {e}")
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

        # Debug: log top-level keys
        logger.info(f"[ESPN Injuries] Top-level keys: {list(data.keys())}")

        # ESPN API can return injuries in different structures
        # Structure 1: {"injuries": [{"team": {...}, "injuries": [...]}]}
        # Structure 2: Direct list at top level
        injury_list = data.get("injuries", data if isinstance(data, list) else [])

        for item in injury_list:
            # Debug first item structure
            if not injuries:
                logger.info(f"[ESPN Injuries] First item keys: {list(item.keys()) if isinstance(item, dict) else 'not a dict'}")

            # Try different structures
            team_info = item.get("team", {})
            team_id = team_info.get("id")
            team_name = team_info.get("displayName") or team_info.get("name") or team_info.get("shortDisplayName")

            # If no team info at this level, the item itself might be an injury record
            team_injuries = item.get("injuries", [item] if "athlete" in item else [])

            # If still no team name, check if it's nested differently
            if not team_name and "team" not in item:
                # Try to get team from athlete
                athlete = item.get("athlete", {})
                team_info = athlete.get("team", {})
                team_name = team_info.get("displayName") or team_info.get("name")
                team_id = team_info.get("id")

            for injury in team_injuries:
                athlete = injury.get("athlete", {})
                player_name = athlete.get("displayName") or athlete.get("fullName") or athlete.get("name")

                # Try to get team from athlete if not available at parent level
                if not team_name:
                    athlete_team = athlete.get("team", {})
                    team_name = athlete_team.get("displayName") or athlete_team.get("name")
                    team_id = athlete_team.get("id")

                injuries.append({
                    "team_id": team_id,
                    "team_name": team_name,
                    "player_name": player_name,
                    "position": athlete.get("position", {}).get("abbreviation") if isinstance(athlete.get("position"), dict) else athlete.get("position"),
                    "status": injury.get("status"),
                    "injury_type": injury.get("type", {}).get("text", "") if isinstance(injury.get("type"), dict) else injury.get("type", ""),
                    "details": injury.get("details", {}).get("detail", "") if isinstance(injury.get("details"), dict) else injury.get("details", "")
                })

        # Debug: log sample
        if injuries:
            logger.info(f"[ESPN Injuries] Sample injury: {injuries[0]}")

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
            logger.info(f"[ESPN] No team name provided for injury check")
            return default_response

        injuries = self.get_injuries(sport)
        logger.info(f"[ESPN] Found {len(injuries)} total injuries for {sport}")

        # Try to match team name
        team_injuries = [i for i in injuries if i.get("team_name") and team_name.lower() in i["team_name"].lower()]
        logger.info(f"[ESPN] Matching '{team_name}' - found {len(team_injuries)} injuries")

        # Debug: show available team names if no match
        if not team_injuries and injuries:
            available_teams = set(i.get("team_name", "?") for i in injuries[:20])
            logger.info(f"[ESPN] Available teams (sample): {list(available_teams)[:5]}")

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

        # Standings require the v2 API endpoint (not site/v2)
        data = self._request_standings(f"{sport_type}/{league}/standings", f"standings_{sport}")
        if not data:
            logger.warning(f"[ESPN Standings] No data returned for {sport}")
            return []

        # Debug: log top-level keys
        logger.info(f"[ESPN Standings] Top-level keys: {list(data.keys())}")

        standings = []

        # ESPN standings can have different structures:
        # Structure 1: {"children": [{"standings": {"entries": [...]}}]}
        # Structure 2: {"standings": {"entries": [...]}}
        # Structure 3: Direct entries list

        # Try to find the entries in various locations
        def extract_entries(obj, depth=0):
            """Recursively find standings entries."""
            entries = []
            if depth > 5:  # Prevent infinite recursion
                return entries

            if isinstance(obj, list):
                for item in obj:
                    entries.extend(extract_entries(item, depth + 1))
            elif isinstance(obj, dict):
                # Check for direct entries
                if "entries" in obj:
                    for entry in obj["entries"]:
                        entries.append(entry)

                # Check common nested paths
                for key in ["children", "standings", "groups"]:
                    if key in obj:
                        entries.extend(extract_entries(obj[key], depth + 1))

            return entries

        all_entries = extract_entries(data)
        logger.info(f"[ESPN Standings] Found {len(all_entries)} entries")

        if all_entries and len(all_entries) > 0:
            logger.info(f"[ESPN Standings] First entry keys: {list(all_entries[0].keys()) if isinstance(all_entries[0], dict) else 'not a dict'}")

        for entry in all_entries:
            if not isinstance(entry, dict):
                continue

            team = entry.get("team", {})
            team_name = team.get("displayName") or team.get("name") or team.get("shortDisplayName")
            team_id = team.get("id")

            # Parse stats - can be list of dicts or direct values
            stats_list = entry.get("stats", [])
            if isinstance(stats_list, list):
                stats = {}
                for s in stats_list:
                    if isinstance(s, dict) and "name" in s:
                        stats[s["name"]] = s.get("value", s.get("displayValue", 0))
            else:
                stats = stats_list if isinstance(stats_list, dict) else {}

            # Handle note for clinched/eliminated
            note_obj = entry.get("note")
            if isinstance(note_obj, dict):
                note = note_obj.get("description", "").lower()
            elif isinstance(note_obj, str):
                note = note_obj.lower()
            else:
                note = ""

            clinched = "clinched" in note
            eliminated = "eliminated" in note

            # Parse numeric values safely
            def safe_int(val, default=0):
                try:
                    return int(float(val)) if val else default
                except (ValueError, TypeError):
                    return default

            def safe_float(val, default=0.0):
                try:
                    return float(val) if val else default
                except (ValueError, TypeError):
                    return default

            standings.append({
                "team_id": team_id,
                "team_name": team_name,
                "wins": safe_int(stats.get("wins")),
                "losses": safe_int(stats.get("losses")),
                "win_pct": safe_float(stats.get("winPercent", stats.get("winPct", 0))),
                "playoff_seed": safe_int(stats.get("playoffSeed")) or None,
                "games_back": safe_float(stats.get("gamesBehind", stats.get("gamesBack", 0))),
                "streak": stats.get("streak", ""),
                "clinched_playoff": clinched,
                "eliminated": eliminated
            })

        # Debug: log sample
        if standings:
            logger.info(f"[ESPN Standings] Sample: {standings[0]}")

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
        logger.info(f"[ESPN] Got {len(standings)} teams in standings for {sport}")

        team_standing = None
        for s in standings:
            if s.get("team_name") and team_name.lower() in s["team_name"].lower():
                team_standing = s
                logger.info(f"[ESPN] Matched '{team_name}' to '{s.get('team_name')}' - W:{s.get('wins')} L:{s.get('losses')}")
                break

        if not team_standing:
            # Debug: show available team names
            if standings:
                available = [s.get("team_name", "?") for s in standings[:5]]
                logger.info(f"[ESPN] No match for '{team_name}'. Available: {available}")
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

        # Determine playoff status based on actual position
        playoff_status = "contending"
        if team_standing["clinched_playoff"]:
            playoff_status = "clinched"
        elif team_standing["eliminated"]:
            playoff_status = "eliminated"
        elif team_standing["games_back"] > 5:
            # More than 5 GB = effectively out of playoff race (but not mathematically eliminated)
            playoff_status = "out_of_race"
        
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


    def get_team_scoring_stats(self, sport: str, team_name: str) -> dict:
        """
        Get team scoring statistics from ESPN scoreboard data.

        Returns points per game, rebounds, assists for pace analysis.
        """
        default = {
            "points_per_game": None,
            "rebounds_per_game": None,
            "assists_per_game": None,
            "field_goal_pct": None,
        }

        sport_type, league = self._get_sport_path(sport)
        if not sport_type:
            return default

        # Get scoreboard which includes team stats
        data = self._request(f"{sport_type}/{league}/scoreboard", f"scoreboard_{sport}_stats")
        if not data:
            return default

        # Search for team in any game
        for event in data.get("events", []):
            for comp in event.get("competitions", []):
                for competitor in comp.get("competitors", []):
                    team_info = competitor.get("team", {})
                    team_display = team_info.get("displayName", "")

                    if team_name and team_name.lower() in team_display.lower():
                        stats = competitor.get("statistics", [])
                        result = default.copy()

                        for stat in stats:
                            name = stat.get("name", "")
                            value = stat.get("displayValue", "0")

                            try:
                                if name == "avgPoints":
                                    result["points_per_game"] = float(value)
                                elif name == "avgRebounds":
                                    result["rebounds_per_game"] = float(value)
                                elif name == "avgAssists" or name == "assistsPerGame":
                                    result["assists_per_game"] = float(value)
                                elif name == "fieldGoalPct":
                                    result["field_goal_pct"] = float(value)
                            except (ValueError, TypeError):
                                pass

                        return result

        return default


espn_client = ESPNClient()