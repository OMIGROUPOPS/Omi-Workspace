#!/usr/bin/env python3
"""Tennis match scraper using ESPN API + Klaassen-Magnus win probability model.

ESPN's tennis scoreboard has individual matches with set-by-set linescores
nested in tournament groupings. This scraper discovers matches, extracts
linescores, and computes win probability at each game change using a
hierarchical Markov model (point → game → set → match).

Sofascore (the original plan) is fully blocked by Cloudflare bot protection.
"""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from functools import lru_cache

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TOUR_CONFIGS = {
    "atp": {"sport": "tennis", "league": "atp", "label": "ATP",
            "type_slug": "mens-singles", "default_f": 0.64},
    "wta": {"sport": "tennis", "league": "wta", "label": "WTA",
            "type_slug": "womens-singles", "default_f": 0.56},
}

DEFAULT_DATES = ["20260304", "20260305", "20260306", "20260307", "20260308"]

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/tennis/{league}/scoreboard"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

SKIP_STATUSES = {"STATUS_SCHEDULED", "STATUS_POSTPONED", "STATUS_CANCELED"}

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
    """Fetch URL with retry/backoff."""
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


def player_abbr(name: str) -> str:
    """First 3 letters of last name, uppercased. E.g. 'Jannik Sinner' → 'SIN'."""
    parts = name.strip().split()
    last = parts[-1] if parts else name
    alpha = "".join(c for c in last if c.isalpha())
    return alpha[:3].upper() if len(alpha) >= 3 else alpha.upper()


# ---------------------------------------------------------------------------
# Klaassen-Magnus win probability model
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _point_win_game(pa: int, pb: int, f: float) -> float:
    """Probability server wins the game from point score (pa, pb).

    Points: 0=0, 1=15, 2=30, 3=40.
    At deuce (both >= 3): server needs to go up by 2.
    """
    if pa >= 3 and pb >= 3:
        diff = pa - pb
        if diff >= 2:
            return 1.0
        if diff <= -2:
            return 0.0
        p_deuce = f * f / (f * f + (1 - f) * (1 - f))
        if diff == 0:
            return p_deuce
        if diff == 1:
            return f + (1 - f) * p_deuce
        return f * p_deuce  # diff == -1

    if pa == 4:
        return 1.0
    if pb == 4:
        return 0.0

    return f * _point_win_game(pa + 1, pb, f) + (1 - f) * _point_win_game(pa, pb + 1, f)


def _tb_server(points_played: int, a_started: bool) -> bool:
    """Who serves at a given tiebreak point index. Returns True if A serves."""
    if points_played == 0:
        return a_started
    group = (points_played - 1) // 2
    return a_started if (group % 2 == 1) else (not a_started)


@lru_cache(maxsize=None)
def _point_win_tiebreak(pa: int, pb: int, points_played: int,
                        f_a: float, f_b: float, a_started: bool) -> float:
    """Probability player A wins tiebreak from score (pa, pb).

    First to 7, win by 2. Serve: A serves point 0, then alternate every 2.
    """
    if pa >= 7 and pa - pb >= 2:
        return 1.0
    if pb >= 7 and pb - pa >= 2:
        return 0.0

    # Extended tiebreak deuce (both >= 6, equal): closed-form
    if pa >= 6 and pb >= 6 and pa == pb:
        a_serves_next = _tb_server(points_played, a_started)
        a_serves_after = _tb_server(points_played + 1, a_started)
        p1 = f_a if a_serves_next else (1 - f_b)
        p2 = f_a if a_serves_after else (1 - f_b)
        return p1 * p2 / (p1 * p2 + (1 - p1) * (1 - p2))

    a_serving = _tb_server(points_played, a_started)
    f = f_a if a_serving else (1 - f_b)

    return (f * _point_win_tiebreak(pa + 1, pb, points_played + 1, f_a, f_b, a_started) +
            (1 - f) * _point_win_tiebreak(pa, pb + 1, points_played + 1, f_a, f_b, a_started))


def _set_won(ga: int, gb: int) -> int:
    """Check if a set is decided. Returns 1 if A won, -1 if B won, 0 if ongoing."""
    if ga >= 6 and ga - gb >= 2:
        return 1
    if gb >= 6 and gb - ga >= 2:
        return -1
    # After tiebreak: 7-6 or 6-7
    if ga == 7 and gb == 6:
        return 1
    if ga == 6 and gb == 7:
        return -1
    return 0


@lru_cache(maxsize=None)
def _game_win_set(ga: int, gb: int, a_serving: bool,
                  f_a: float, f_b: float) -> float:
    """Probability player A wins the set from game score (ga, gb)."""
    result = _set_won(ga, gb)
    if result == 1:
        return 1.0
    if result == -1:
        return 0.0

    # Tiebreak at 6-6
    if ga == 6 and gb == 6:
        return _point_win_tiebreak(0, 0, 0, f_a, f_b, a_serving)

    if a_serving:
        p_a_wins_game = _point_win_game(0, 0, f_a)
    else:
        p_a_wins_game = 1 - _point_win_game(0, 0, f_b)

    return (p_a_wins_game * _game_win_set(ga + 1, gb, not a_serving, f_a, f_b) +
            (1 - p_a_wins_game) * _game_win_set(ga, gb + 1, not a_serving, f_a, f_b))


@lru_cache(maxsize=None)
def _set_win_match(sa: int, sb: int, a_serving: bool,
                   f_a: float, f_b: float, sets_to_win: int) -> float:
    """Probability player A wins the match from set score (sa, sb)."""
    if sa >= sets_to_win:
        return 1.0
    if sb >= sets_to_win:
        return 0.0

    p_a_wins_set = _game_win_set(0, 0, a_serving, f_a, f_b)

    return (p_a_wins_set * _set_win_match(sa + 1, sb, not a_serving, f_a, f_b, sets_to_win) +
            (1 - p_a_wins_set) * _set_win_match(sa, sb + 1, not a_serving, f_a, f_b, sets_to_win))


def match_win_prob(
    sets_a: int, sets_b: int,
    games_a: int, games_b: int,
    points_a: int, points_b: int,
    is_a_serving: bool,
    f_a: float = 0.64,
    f_b: float = 0.64,
    best_of: int = 3,
) -> float:
    """Returns probability that player A wins the match from the current state."""
    sets_to_win = (best_of + 1) // 2

    if sets_a >= sets_to_win:
        return 1.0
    if sets_b >= sets_to_win:
        return 0.0

    # If the current set is already decided by the game score, fold it in
    sw = _set_won(games_a, games_b)
    if sw == 1:
        return _set_win_match(sets_a + 1, sets_b, is_a_serving, f_a, f_b, sets_to_win)
    if sw == -1:
        return _set_win_match(sets_a, sets_b + 1, is_a_serving, f_a, f_b, sets_to_win)

    # Tiebreak in progress
    if games_a == 6 and games_b == 6:
        total_tb_points = points_a + points_b
        if total_tb_points == 0:
            a_started = is_a_serving
        else:
            group = (total_tb_points - 1) // 2
            a_started = is_a_serving if (group % 2 == 1) else (not is_a_serving)

        p_a_wins_tb = _point_win_tiebreak(
            points_a, points_b, total_tb_points, f_a, f_b, a_started
        )
        p_match_win = _set_win_match(sets_a + 1, sets_b, not is_a_serving, f_a, f_b, sets_to_win)
        p_match_lose = _set_win_match(sets_a, sets_b + 1, not is_a_serving, f_a, f_b, sets_to_win)
        return p_a_wins_tb * p_match_win + (1 - p_a_wins_tb) * p_match_lose

    # Current game
    if is_a_serving:
        p_a_wins_game = _point_win_game(points_a, points_b, f_a)
    else:
        p_a_wins_game = 1 - _point_win_game(points_b, points_a, f_b)

    p_set_win = _game_win_set(games_a + 1, games_b, not is_a_serving, f_a, f_b)
    p_set_lose = _game_win_set(games_a, games_b + 1, not is_a_serving, f_a, f_b)

    p_a_wins_set = p_a_wins_game * p_set_win + (1 - p_a_wins_game) * p_set_lose

    p_match_win = _set_win_match(sets_a + 1, sets_b, not is_a_serving, f_a, f_b, sets_to_win)
    p_match_lose = _set_win_match(sets_a, sets_b + 1, not is_a_serving, f_a, f_b, sets_to_win)

    return p_a_wins_set * p_match_win + (1 - p_a_wins_set) * p_match_lose


# ---------------------------------------------------------------------------
# Win probability timeline from linescores
# ---------------------------------------------------------------------------

def build_win_prob_timeline(home_linescores: list, away_linescores: list,
                            f_a: float, f_b: float, best_of: int = 3) -> list:
    """Build game-by-game win probability from set linescores.

    Each linescore entry is the final game count for that set.
    We reconstruct the game-by-game progression within each set by
    enumerating all possible orderings consistent with the final score,
    then walking through the most likely path (alternating holds).
    """
    timeline = []
    sets_a, sets_b = 0, 0
    is_a_serving = True  # Assume home serves first
    wp_id = 0

    # Initial state
    wp = match_win_prob(0, 0, 0, 0, 0, 0, True, f_a, f_b, best_of)
    timeline.append({
        "home_win_pct": round(wp, 4),
        "away_win_pct": round(1 - wp, 4),
        "tie_pct": 0,
        "seconds_left": None,
        "play_id": f"wp_{wp_id}",
        "score_state": {"sets": [0, 0], "games": [0, 0], "points": [0, 0],
                        "server": "home"},
    })
    wp_id += 1

    num_sets = min(len(home_linescores), len(away_linescores))

    for set_idx in range(num_sets):
        set_home = int(home_linescores[set_idx])
        set_away = int(away_linescores[set_idx])
        total_games = set_home + set_away

        # Reconstruct game-by-game path within this set.
        # We use the "most likely" path: each server holds until the score
        # diverges from that pattern. For the final result we know who won
        # each game count, so we walk through game by game.
        ga, gb = 0, 0
        serving_a = is_a_serving

        for game_num in range(total_games):
            # Determine who won this game.
            # Strategy: walk to the known final score. At each step,
            # the player who still needs more games wins.
            games_left_a = set_home - ga
            games_left_b = set_away - gb

            if games_left_a > 0 and games_left_b > 0:
                # Both still need games — server holds (most likely)
                if serving_a:
                    ga += 1
                else:
                    gb += 1
            elif games_left_a > 0:
                ga += 1
            else:
                gb += 1

            # After this game, serve switches
            serving_a = not serving_a

            wp = match_win_prob(sets_a, sets_b, ga, gb, 0, 0,
                                serving_a, f_a, f_b, best_of)
            timeline.append({
                "home_win_pct": round(wp, 4),
                "away_win_pct": round(1 - wp, 4),
                "tie_pct": 0,
                "seconds_left": None,
                "play_id": f"wp_{wp_id}",
                "score_state": {"sets": [sets_a, sets_b], "games": [ga, gb],
                                "points": [0, 0],
                                "server": "home" if serving_a else "away"},
            })
            wp_id += 1

        # Set complete — update set score
        if set_home > set_away:
            sets_a += 1
        else:
            sets_b += 1

        # Carry over serve state to next set
        is_a_serving = serving_a

    return timeline


def build_scoring_plays(home_linescores: list, away_linescores: list,
                        home_abbr: str, away_abbr: str,
                        home_name: str, away_name: str) -> list:
    """Build scoring plays from linescores (one entry per set)."""
    plays = []
    sets_a, sets_b = 0, 0
    num_sets = min(len(home_linescores), len(away_linescores))

    for set_idx in range(num_sets):
        h = int(home_linescores[set_idx])
        a = int(away_linescores[set_idx])
        if h > a:
            sets_a += 1
            winner_name = home_name
            winner_abbr = home_abbr
        else:
            sets_b += 1
            winner_name = away_name
            winner_abbr = away_abbr

        plays.append({
            "play_id": f"set_{set_idx + 1}",
            "type": "set_won",
            "text": f"{winner_name} wins set {set_idx + 1} ({h}-{a})",
            "home_score": sets_a,
            "away_score": sets_b,
            "period": set_idx + 1,
            "clock": "",
            "team_id": "",
            "team_abbr": winner_abbr,
            "team_name": winner_name,
        })

    return plays


# ---------------------------------------------------------------------------
# ESPN parsing
# ---------------------------------------------------------------------------

def parse_espn_match(comp: dict, tour: str) -> dict:
    """Parse an ESPN tennis competition (match) into our standard format."""
    cfg = TOUR_CONFIGS[tour]
    competitors = comp.get("competitors", [])

    if len(competitors) < 2:
        return None

    # ESPN tennis uses 'athlete' not 'team'
    home_comp = competitors[0]
    away_comp = competitors[1]

    home_athlete = home_comp.get("athlete", {})
    away_athlete = away_comp.get("athlete", {})

    home_name = home_athlete.get("displayName", "")
    away_name = away_athlete.get("displayName", "")
    home_abbr = player_abbr(home_name)
    away_abbr = player_abbr(away_name)

    # Linescores
    home_ls = [str(int(ls.get("value", 0))) for ls in home_comp.get("linescores", [])]
    away_ls = [str(int(ls.get("value", 0))) for ls in away_comp.get("linescores", [])]

    # Sets won = count of sets where player had more games
    home_sets = sum(1 for h, a in zip(home_ls, away_ls) if int(h) > int(a)) if home_ls else 0
    away_sets = sum(1 for h, a in zip(home_ls, away_ls) if int(a) > int(h)) if away_ls else 0

    # Status
    status_obj = comp.get("status", {}).get("type", {})
    status_name = status_obj.get("name", "")
    completed = status_obj.get("completed", False)

    # Winner
    home_winner = home_comp.get("winner", False)
    away_winner = away_comp.get("winner", False)
    if home_winner:
        winner = "home"
    elif away_winner:
        winner = "away"
    else:
        winner = ""

    # Round info
    round_info = comp.get("round", {})
    round_name = round_info.get("displayName", "")

    # Date
    date_str = comp.get("date", comp.get("startDate", ""))

    # Build linescores dict
    linescores = {}
    if home_ls:
        linescores[home_abbr] = home_ls
        linescores[away_abbr] = away_ls

    return {
        "event_id": str(comp.get("id", "")),
        "sport": tour,
        "league": cfg["label"],
        "name": f"{home_name} vs {away_name}",
        "short_name": f"{home_name.split()[-1] if home_name else ''} vs {away_name.split()[-1] if away_name else ''}",
        "date": date_str,
        "status": status_name,
        "completed": completed,
        "home_team": {
            "id": str(home_athlete.get("id", "")),
            "name": home_name.split()[-1] if home_name else "",
            "abbreviation": home_abbr,
            "display_name": home_name,
            "score": str(home_sets),
            "winner": home_winner,
            "home_away": "home",
        },
        "away_team": {
            "id": str(away_athlete.get("id", "")),
            "name": away_name.split()[-1] if away_name else "",
            "abbreviation": away_abbr,
            "display_name": away_name,
            "score": str(away_sets),
            "winner": away_winner,
            "home_away": "away",
        },
        "final_score": {"home": home_sets, "away": away_sets},
        "winner": winner,
        "venue": "",
        "odds": {},
        "win_probability": [],
        "scoring_plays": [],
        "all_plays": [],
        "linescores": linescores,
        "round": round_name,
        "source": "espn_klaassen_magnus",
        "win_prob_model": "klaassen_magnus",
        "serve_prob_home": cfg["default_f"],
        "serve_prob_away": cfg["default_f"],
    }


# ---------------------------------------------------------------------------
# Scraping logic
# ---------------------------------------------------------------------------

def scrape_all_tennis(session: requests.Session, dates: list, tours: list,
                      delay: float, f_override: float = None) -> dict:
    """Scrape all tennis matches across all dates from ESPN.

    ESPN returns entire tournaments per scoreboard call, so we fetch once
    per league and bin matches by their actual start date.
    Returns dict: {date_str: [matches]}
    """
    # Collect all unique matches across all tournament endpoints
    seen_ids = set()
    all_matches = []

    for tour in tours:
        cfg = TOUR_CONFIGS[tour]
        log(f"Fetching {tour.upper()} tournaments...")

        # ESPN returns the same tournament for any date within its range.
        # Fetch once using the first date — we'll bin by actual match date.
        url = SCOREBOARD_URL.format(league=cfg["league"])
        data = fetch(session, url, params={"dates": dates[0], "limit": "500"}, delay=delay)

        if not data:
            log(f"  No data returned")
            continue

        events = data.get("events", [])
        if not events:
            log(f"  No events")
            continue

        match_count = 0
        for ev in events:
            tournament_name = ev.get("name", "")
            groupings = ev.get("groupings", [])

            for group in groupings:
                # Filter for singles only
                type_info = group.get("competitions", [{}])[0].get("type", {}) if group.get("competitions") else {}
                type_slug = type_info.get("slug", "")

                if type_slug != cfg["type_slug"]:
                    continue

                for comp in group.get("competitions", []):
                    comp_id = str(comp.get("id", ""))
                    if comp_id in seen_ids:
                        continue
                    seen_ids.add(comp_id)

                    match = parse_espn_match(comp, tour)
                    if not match:
                        continue

                    match["venue"] = tournament_name

                    if match["status"] in SKIP_STATUSES:
                        continue

                    # Compute win probability for completed matches with linescores
                    if match["completed"] and match["linescores"]:
                        home_abbr = match["home_team"]["abbreviation"]
                        away_abbr = match["away_team"]["abbreviation"]
                        home_ls = match["linescores"].get(home_abbr, [])
                        away_ls = match["linescores"].get(away_abbr, [])

                        f_a = f_override if f_override else cfg["default_f"]
                        f_b = f_a
                        match["serve_prob_home"] = f_a
                        match["serve_prob_away"] = f_b

                        match["win_probability"] = build_win_prob_timeline(
                            home_ls, away_ls, f_a, f_b, best_of=3
                        )
                        match["scoring_plays"] = build_scoring_plays(
                            home_ls, away_ls,
                            home_abbr, away_abbr,
                            match["home_team"]["display_name"],
                            match["away_team"]["display_name"],
                        )

                    match_count += 1
                    wp_count = len(match["win_probability"])
                    sc_count = len(match["scoring_plays"])
                    if match_count <= 5 or match_count % 20 == 0:
                        log(f"  [{match_count}] {match['short_name']} — wp={wp_count}, scoring={sc_count}")

                    all_matches.append(match)

        log(f"  {tour.upper()}: {match_count} singles matches found")

    # Bin matches by actual date (from match date field)
    date_set = set(dates)
    matches_by_date = {d: [] for d in dates}

    for m in all_matches:
        match_date = m["date"][:10].replace("-", "") if m["date"] else ""
        if match_date in date_set:
            matches_by_date[match_date].append(m)

    # Log date distribution
    for d in dates:
        log(f"  {d}: {len(matches_by_date[d])} matches")

    return matches_by_date


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_json(data, filepath: str):
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log(f"Wrote {filepath}")


def print_summary(all_matches: list):
    """Print summary table."""
    from collections import defaultdict
    stats = defaultdict(lambda: {"total": 0, "completed": 0, "with_wp": 0, "with_scoring": 0})
    for m in all_matches:
        s = stats[m["sport"]]
        s["total"] += 1
        if m["completed"]:
            s["completed"] += 1
        if m["win_probability"]:
            s["with_wp"] += 1
        if m["scoring_plays"]:
            s["with_scoring"] += 1

    print("\n" + "=" * 65)
    print(f"{'Tour':<10} {'Total':>6} {'Completed':>10} {'Win Prob':>10} {'Scoring':>10}")
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
    parser = argparse.ArgumentParser(
        description="Tennis scraper (ESPN + Klaassen-Magnus win prob model)"
    )
    parser.add_argument("--dates", nargs="+", default=DEFAULT_DATES,
                        help="Dates to scrape (YYYYMMDD). Default: March 4-8, 2026")
    parser.add_argument("--tours", nargs="+", default=["atp", "wta"],
                        choices=["atp", "wta"],
                        help="Tours to scrape. Default: atp wta")
    parser.add_argument("--output", default="espn_data",
                        help="Output directory. Default: espn_data")
    parser.add_argument("--serve-prob", type=float, default=None,
                        help="Override default serve probability for win prob model")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Delay between requests in seconds. Default: 0.5")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    session = make_session()

    # Fetch all matches once, then bin by date
    matches_by_date = scrape_all_tennis(
        session, args.dates, args.tours, args.delay, args.serve_prob
    )

    all_matches = []
    for date_str in args.dates:
        date_matches = matches_by_date.get(date_str, [])
        date_file = os.path.join(args.output, f"tennis_matches_{date_str}.json")
        write_json(date_matches, date_file)
        all_matches.extend(date_matches)

    # Write combined file
    combined_file = os.path.join(args.output, "tennis_all_matches.json")
    write_json(all_matches, combined_file)

    print_summary(all_matches)
    log(f"Done. {len(all_matches)} total matches scraped.")


if __name__ == "__main__":
    main()
