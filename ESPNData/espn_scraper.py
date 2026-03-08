#!/usr/bin/env python3
"""ESPN game data scraper for Pendulum Phase 2.

Pulls win probability, scoring timelines, metadata for games
from ESPN's undocumented API endpoints.
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SPORT_CONFIGS = {
    "nba":    {"sport": "basketball", "league": "nba"},
    "nhl":    {"sport": "hockey",     "league": "nhl"},
    "ncaamb": {"sport": "basketball", "league": "mens-college-basketball",
               "scoreboard_params": {"groups": "50", "limit": "400"}},
    "mlb":    {"sport": "baseball",   "league": "mlb"},
    "atp":    {"sport": "tennis",     "league": "atp"},
    "wta":    {"sport": "tennis",     "league": "wta"},
    "ufc":    {"sport": "mma",        "league": "ufc"},
}

SPORTS_WITH_WIN_PROB = {"nba", "ncaamb", "mlb"}

# Sports where ESPN summary has no winprobability data at all
SPORTS_NO_WIN_PROB = {"atp", "wta", "ufc", "nhl"}

SKIP_STATUSES = {"STATUS_SCHEDULED", "STATUS_POSTPONED", "STATUS_CANCELED"}

DEFAULT_DATES = ["20260304", "20260305", "20260306", "20260307", "20260308"]

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
SUMMARY_URL = "https://site.web.api.espn.com/apis/site/v2/sports/{sport}/{league}/summary"
PROBABILITIES_URL = (
    "https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}"
    "/events/{event_id}/competitions/{event_id}/probabilities"
)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def fetch(session: requests.Session, url: str, params: dict = None,
          delay: float = 0.5, retries: int = 3, timeout: float = 15.0):
    """Fetch URL with retry/backoff. Returns parsed JSON or None."""
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, params=params, timeout=timeout)
            if resp.status_code == 404:
                return None
            if resp.status_code == 429:
                wait = 5 * attempt
                log(f"  429 rate-limited, waiting {wait}s (attempt {attempt}/{retries})")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            time.sleep(delay)
            return resp.json()
        except requests.exceptions.Timeout:
            log(f"  Timeout (attempt {attempt}/{retries})")
            if attempt < retries:
                time.sleep(2 * attempt)
        except requests.exceptions.RequestException as e:
            log(f"  Request error: {e} (attempt {attempt}/{retries})")
            if attempt < retries:
                time.sleep(2 * attempt)
    return None


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_competitor(comp: dict, sport_key: str) -> dict:
    """Extract team/athlete info from a competitor object."""
    # UFC uses 'athlete' instead of 'team' sometimes
    team = comp.get("team", {})
    if not team and sport_key == "ufc":
        athlete = comp.get("athlete", {})
        team = {
            "id": str(athlete.get("id", "")),
            "abbreviation": athlete.get("shortName", athlete.get("displayName", "")),
            "displayName": athlete.get("displayName", ""),
            "name": athlete.get("shortName", athlete.get("displayName", "")),
        }
    return {
        "id": str(team.get("id", "")),
        "name": team.get("name", team.get("shortName", "")),
        "abbreviation": team.get("abbreviation", ""),
        "display_name": team.get("displayName", ""),
        "score": comp.get("score", ""),
        "winner": comp.get("winner", False),
        "home_away": comp.get("homeAway", ""),
    }


def parse_scoreboard_event(event: dict, sport_key: str) -> dict:
    """Parse a single event from the scoreboard response."""
    competition = {}
    if event.get("competitions"):
        competition = event["competitions"][0]

    competitors = competition.get("competitors", [])
    home_team = {}
    away_team = {}
    for c in competitors:
        parsed = parse_competitor(c, sport_key)
        if parsed["home_away"] == "home":
            home_team = parsed
        else:
            away_team = parsed

    # If no home/away distinction (UFC, tennis), use order
    if not home_team and not away_team and len(competitors) >= 2:
        home_team = parse_competitor(competitors[0], sport_key)
        home_team["home_away"] = "home"
        away_team = parse_competitor(competitors[1], sport_key)
        away_team["home_away"] = "away"

    status_obj = event.get("status", {}).get("type", {})
    status_name = status_obj.get("name", "")
    completed = status_obj.get("completed", False)

    # Odds
    odds = {}
    odds_list = competition.get("odds", [])
    if odds_list:
        o = odds_list[0]
        odds = {
            "spread": o.get("details", ""),
            "over_under": o.get("overUnder"),
            "provider": o.get("provider", {}).get("name", ""),
        }

    # Venue
    venue_name = competition.get("venue", {}).get("fullName", "")

    # Final score
    try:
        home_score = int(home_team.get("score", 0))
    except (ValueError, TypeError):
        home_score = 0
    try:
        away_score = int(away_team.get("score", 0))
    except (ValueError, TypeError):
        away_score = 0

    if home_score > away_score:
        winner = "home"
    elif away_score > home_score:
        winner = "away"
    else:
        winner = "tie"

    return {
        "event_id": str(event.get("id", "")),
        "sport": sport_key,
        "league": SPORT_CONFIGS[sport_key]["league"].upper(),
        "name": event.get("name", ""),
        "short_name": event.get("shortName", ""),
        "date": event.get("date", ""),
        "status": status_name,
        "completed": completed,
        "home_team": home_team,
        "away_team": away_team,
        "final_score": {"home": home_score, "away": away_score},
        "winner": winner,
        "venue": venue_name,
        "odds": odds,
        "win_probability": [],
        "scoring_plays": [],
        "all_plays": [],
        "linescores": {},
    }


def parse_win_probability(wp_list: list) -> list:
    """Parse win probability array from summary."""
    result = []
    for wp in (wp_list or []):
        result.append({
            "home_win_pct": wp.get("homeWinPercentage"),
            "away_win_pct": round(1.0 - (wp.get("homeWinPercentage") or 0.5) - (wp.get("tiePercentage") or 0), 4)
                if wp.get("homeWinPercentage") is not None else None,
            "tie_pct": wp.get("tiePercentage", 0),
            "seconds_left": wp.get("secondsLeft"),
            "play_id": str(wp.get("playId", "")),
        })
    return result


def parse_probabilities_endpoint(data: dict) -> list:
    """Parse the dedicated probabilities endpoint response."""
    result = []
    for item in (data or {}).get("items", []):
        result.append({
            "home_win_pct": item.get("homeWinPercentage"),
            "away_win_pct": item.get("awayWinPercentage"),
            "tie_pct": item.get("tiePercentage", 0),
            "seconds_left": item.get("secondsLeft"),
            "play_id": str(item.get("playId", "")),
        })
    return result


def parse_scoring_plays(plays: list) -> list:
    result = []
    for p in (plays or []):
        team_info = p.get("team", {})
        result.append({
            "play_id": str(p.get("id", "")),
            "type": p.get("type", {}).get("text", ""),
            "text": p.get("text", ""),
            "home_score": p.get("homeScore"),
            "away_score": p.get("awayScore"),
            "period": p.get("period", {}).get("number"),
            "clock": p.get("clock", {}).get("displayValue", ""),
            "team_id": str(team_info.get("id", "")),
            "team_abbr": team_info.get("abbreviation", ""),
            "team_name": team_info.get("displayName", ""),
        })
    return result


def parse_all_plays(plays: list) -> list:
    result = []
    for p in (plays or []):
        result.append({
            "play_id": str(p.get("id", "")),
            "sequence": p.get("sequenceNumber"),
            "type": p.get("type", {}).get("text", ""),
            "text": p.get("text", ""),
            "home_score": p.get("homeScore"),
            "away_score": p.get("awayScore"),
            "period": p.get("period", {}).get("number"),
            "clock": p.get("clock", {}).get("displayValue", ""),
            "wallclock": p.get("wallclock", ""),
            "scoring_play": p.get("scoringPlay", False),
            "score_value": p.get("scoreValue", 0),
        })
    return result


def parse_linescores(header: dict) -> dict:
    """Extract period-by-period linescores from summary header."""
    linescores = {}
    comps = header.get("competitions", [{}])[0].get("competitors", []) if header else []
    for c in comps:
        team = c.get("team", {})
        abbr = team.get("abbreviation", team.get("displayName", ""))
        scores = []
        for ls in c.get("linescores", []):
            scores.append(str(ls.get("displayValue", ls.get("value", ""))))
        if abbr and scores:
            linescores[abbr] = scores
    return linescores


# ---------------------------------------------------------------------------
# Scraping logic
# ---------------------------------------------------------------------------

def scrape_scoreboard(session: requests.Session, sport_key: str, date_str: str,
                      delay: float) -> list:
    """Get all events for a sport on a date."""
    cfg = SPORT_CONFIGS[sport_key]
    url = SCOREBOARD_URL.format(sport=cfg["sport"], league=cfg["league"])
    params = {"dates": date_str}
    extra = cfg.get("scoreboard_params", {})
    params.update(extra)

    data = fetch(session, url, params=params, delay=delay)
    if not data:
        return []

    events = data.get("events", [])
    return events


def scrape_game_detail(session: requests.Session, game: dict, delay: float,
                       skip_plays: bool) -> dict:
    """Fill in win_probability, scoring_plays, all_plays, linescores from summary."""
    sport_key = game["sport"]
    cfg = SPORT_CONFIGS[sport_key]
    event_id = game["event_id"]

    # Hit summary endpoint
    url = SUMMARY_URL.format(sport=cfg["sport"], league=cfg["league"])
    data = fetch(session, url, params={"event": event_id}, delay=delay)

    if data:
        # Win probability from summary
        wp = data.get("winprobability", [])
        game["win_probability"] = parse_win_probability(wp)

        # Scoring plays — ESPN has no top-level scoringPlays key;
        # filter from plays where scoringPlay == true
        all_plays_raw = data.get("plays", [])
        scoring_raw = [p for p in all_plays_raw if p.get("scoringPlay")]
        game["scoring_plays"] = parse_scoring_plays(scoring_raw)

        # All plays (PBP)
        if not skip_plays:
            game["all_plays"] = parse_all_plays(data.get("plays", []))

        # Linescores from header
        game["linescores"] = parse_linescores(data.get("header", {}))

    # Hit probabilities endpoint for applicable sports (supplement/fallback)
    if sport_key in SPORTS_WITH_WIN_PROB and game["completed"]:
        prob_url = PROBABILITIES_URL.format(
            sport=cfg["sport"], league=cfg["league"], event_id=event_id
        )
        prob_data = fetch(session, prob_url, params={"limit": "1000"}, delay=delay)
        if prob_data:
            prob_parsed = parse_probabilities_endpoint(prob_data)
            # Use probabilities endpoint if it has more data points
            if len(prob_parsed) > len(game["win_probability"]):
                game["win_probability"] = prob_parsed

    return game


def scrape_sport_date(session: requests.Session, sport_key: str, date_str: str,
                      delay: float, skip_plays: bool) -> list:
    """Scrape all completed games for one sport on one date."""
    log(f"Scraping {sport_key.upper()} for {date_str}...")
    events = scrape_scoreboard(session, sport_key, date_str, delay)
    log(f"  Found {len(events)} events")

    games = []
    for i, ev in enumerate(events):
        game = parse_scoreboard_event(ev, sport_key)

        if game["status"] in SKIP_STATUSES:
            log(f"  [{i+1}/{len(events)}] {game['short_name']} — skipped ({game['status']})")
            continue

        log(f"  [{i+1}/{len(events)}] {game['short_name']} ({game['status']})")

        # Get detailed data for non-skipped games
        game = scrape_game_detail(session, game, delay, skip_plays)

        wp_count = len(game["win_probability"])
        sc_count = len(game["scoring_plays"])
        play_count = len(game["all_plays"])
        wp_note = " (no ESPN win prob for this sport)" if sport_key in SPORTS_NO_WIN_PROB and wp_count == 0 else ""
        log(f"    win_prob={wp_count}{wp_note}, scoring={sc_count}, plays={play_count}")

        games.append(game)

    return games


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_json(data, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log(f"Wrote {filepath}")


def write_flat_csv(all_games: list, filepath: str):
    """Write a flat CSV with one row per win_prob observation or scoring play."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    rows = []
    for g in all_games:
        base = {
            "event_id": g["event_id"],
            "sport": g["sport"],
            "league": g["league"],
            "name": g["name"],
            "short_name": g["short_name"],
            "date": g["date"],
            "status": g["status"],
            "completed": g["completed"],
            "home_abbr": g["home_team"].get("abbreviation", ""),
            "away_abbr": g["away_team"].get("abbreviation", ""),
            "home_score_final": g["final_score"]["home"],
            "away_score_final": g["final_score"]["away"],
            "winner": g["winner"],
        }
        for wp in g["win_probability"]:
            row = {**base, "row_type": "win_prob"}
            row["home_win_pct"] = wp.get("home_win_pct")
            row["away_win_pct"] = wp.get("away_win_pct")
            row["tie_pct"] = wp.get("tie_pct")
            row["seconds_left"] = wp.get("seconds_left")
            row["play_id"] = wp.get("play_id")
            rows.append(row)
        for sp in g["scoring_plays"]:
            row = {**base, "row_type": "scoring_play"}
            row["play_id"] = sp.get("play_id")
            row["play_type"] = sp.get("type")
            row["play_text"] = sp.get("text")
            row["home_score"] = sp.get("home_score")
            row["away_score"] = sp.get("away_score")
            row["period"] = sp.get("period")
            row["clock"] = sp.get("clock")
            row["team_abbr"] = sp.get("team_abbr")
            rows.append(row)

    if not rows:
        log("No data rows for CSV")
        return

    fieldnames = list(rows[0].keys())
    # Gather all keys across rows
    for r in rows:
        for k in r:
            if k not in fieldnames:
                fieldnames.append(k)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    log(f"Wrote {filepath} ({len(rows)} rows)")


def print_summary(all_games: list):
    """Print summary table at the end."""
    from collections import defaultdict
    stats = defaultdict(lambda: {"total": 0, "completed": 0, "with_wp": 0, "with_scoring": 0})
    for g in all_games:
        s = stats[g["sport"]]
        s["total"] += 1
        if g["completed"]:
            s["completed"] += 1
        if g["win_probability"]:
            s["with_wp"] += 1
        if g["scoring_plays"]:
            s["with_scoring"] += 1

    print("\n" + "=" * 65)
    print(f"{'Sport':<10} {'Total':>6} {'Completed':>10} {'Win Prob':>10} {'Scoring':>10}")
    print("-" * 65)
    totals = {"total": 0, "completed": 0, "with_wp": 0, "with_scoring": 0}
    for sport in sorted(stats.keys()):
        s = stats[sport]
        print(f"{sport.upper():<10} {s['total']:>6} {s['completed']:>10} {s['with_wp']:>10} {s['with_scoring']:>10}")
        for k in totals:
            totals[k] += s[k]
    print("-" * 65)
    print(f"{'TOTAL':<10} {totals['total']:>6} {totals['completed']:>10} {totals['with_wp']:>10} {totals['with_scoring']:>10}")
    print("=" * 65)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ESPN game data scraper for Pendulum Phase 2")
    parser.add_argument("--dates", nargs="+", default=DEFAULT_DATES,
                        help="Dates to scrape (YYYYMMDD). Default: March 4-8, 2026")
    parser.add_argument("--sports", nargs="+", default=list(SPORT_CONFIGS.keys()),
                        choices=list(SPORT_CONFIGS.keys()),
                        help="Sports to scrape. Default: all")
    parser.add_argument("--output", default="espn_data",
                        help="Output directory. Default: espn_data")
    parser.add_argument("--csv", action="store_true",
                        help="Also write flat CSV")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Delay between requests in seconds. Default: 0.5")
    parser.add_argument("--skip-plays", action="store_true",
                        help="Skip full play-by-play to reduce file size")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    session = make_session()
    all_games = []

    for date_str in args.dates:
        log(f"=== Date: {date_str} ===")
        date_games = []
        for sport_key in args.sports:
            games = scrape_sport_date(session, sport_key, date_str, args.delay, args.skip_plays)
            date_games.extend(games)

        # Write per-date file
        date_file = os.path.join(args.output, f"espn_games_{date_str}.json")
        write_json(date_games, date_file)
        all_games.extend(date_games)

    # Write combined file
    combined_file = os.path.join(args.output, "espn_all_games.json")
    write_json(all_games, combined_file)

    # Optional CSV
    if args.csv:
        csv_file = os.path.join(args.output, "espn_timeline_flat.csv")
        write_flat_csv(all_games, csv_file)

    print_summary(all_games)
    log(f"Done. {len(all_games)} total games scraped.")


if __name__ == "__main__":
    main()
