Build a Python script called `espn_scraper.py` in the project root. This is for our Pendulum Phase 2 system — it pulls ESPN game data (win probability, scoring timelines, metadata) for every game that was on Kalshi from March 4-8, 2026.

## What the script does

Two-step process per sport per date:
1. Hit ESPN's scoreboard endpoint to discover all game/event IDs for that date
2. Hit ESPN's summary endpoint for each completed game to pull win probability, scoring plays, play-by-play, and linescores

## ESPN API endpoints (undocumented, no auth needed)

**Scoreboard** (get game IDs per date):
```
GET https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard?dates=YYYYMMDD
```

**Summary** (get full game detail including win probability):
```
GET https://site.web.api.espn.com/apis/site/v2/sports/{sport}/{league}/summary?event={EVENT_ID}
```

**Probabilities** (dedicated win prob endpoint, sometimes more granular than summary):
```
GET https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/events/{EVENT_ID}/competitions/{EVENT_ID}/probabilities?limit=1000
```

## Sport/league path mappings

```python
SPORT_CONFIGS = {
    "nba":    {"sport": "basketball", "league": "nba"},
    "nhl":    {"sport": "hockey",     "league": "nhl"},
    "ncaamb": {"sport": "basketball", "league": "mens-college-basketball",
               "scoreboard_params": {"groups": "50", "limit": "400"}},  # needed to get all D1 games
    "mlb":    {"sport": "baseball",   "league": "mlb"},
    "atp":    {"sport": "tennis",     "league": "atp"},
    "wta":    {"sport": "tennis",     "league": "wta"},
    "ufc":    {"sport": "mma",        "league": "ufc"},
}
```

Note: ESPN does NOT have win probability data for tennis (atp/wta) or UFC. The summary endpoint will still return scoring/round data for those sports, just no `winprobability` key. The script should handle this gracefully.

## Data to extract per game

From the **scoreboard** response:
- `event.id` — the ESPN event ID (string)
- `event.name`, `event.shortName`, `event.date`
- `event.competitions[0].competitors[]` — home/away teams with `team.abbreviation`, `team.displayName`, `team.id`, `score`, `winner`, `homeAway`
- `event.competitions[0].odds[0]` — pre-game spread and over/under if available
- `event.competitions[0].venue.fullName`
- `event.status.type.name`, `.completed`

From the **summary** response:
- `summary.winprobability[]` — array of objects with `homeWinPercentage`, `secondsLeft`, `playId`, `tiePercentage`
- `summary.scoringPlays[]` — each has `id`, `type.text`, `text`, `homeScore`, `awayScore`, `period.number`, `clock.displayValue`, `team.abbreviation`
- `summary.plays[]` — full play-by-play, each has `id`, `sequenceNumber`, `type.text`, `text`, `homeScore`, `awayScore`, `period.number`, `clock.displayValue`, `wallclock`, `scoringPlay`, `scoreValue`
- `summary.header.competitions[0].competitors[].linescores[]` — period-by-period scoring

From the **probabilities** endpoint (for NBA/NHL/NCAAMB/MLB only):
- `items[]` with `homeWinPercentage`, `awayWinPercentage`, `tiePercentage`, `secondsLeft`, `playId`
- Use this as a fallback/supplement if it returns more data points than `summary.winprobability`

## Output format

**Per-date JSON files**: `espn_data/espn_games_YYYYMMDD.json`
**Combined JSON**: `espn_data/espn_all_games.json`
**Optional flat CSV**: `espn_data/espn_timeline_flat.csv` (one row per win_prob observation or scoring play, with game metadata repeated)

Each game object in JSON should look like:
```json
{
  "event_id": "401703456",
  "sport": "nba",
  "league": "NBA",
  "name": "Philadelphia 76ers at Atlanta Hawks",
  "short_name": "PHI @ ATL",
  "date": "2026-03-07T00:00Z",
  "status": "STATUS_FINAL",
  "completed": true,
  "home_team": {
    "id": "1", "name": "Hawks", "abbreviation": "ATL",
    "display_name": "Atlanta Hawks", "score": "112", "winner": true, "home_away": "home"
  },
  "away_team": { ... },
  "final_score": {"home": 112, "away": 108},
  "winner": "home",
  "venue": "State Farm Arena",
  "odds": {"spread": "ATL -3.5", "over_under": 224.5, "provider": "ESPN BET"},
  "win_probability": [
    {"home_win_pct": 0.5, "away_win_pct": 0.5, "tie_pct": 0, "seconds_left": 2880, "play_id": "..."},
    ...
  ],
  "scoring_plays": [
    {"play_id": "...", "type": "Three Point Jumper", "text": "Tyrese Maxey makes...",
     "home_score": 0, "away_score": 3, "period": 1, "clock": "11:22",
     "team_id": "20", "team_abbr": "PHI", "team_name": "Philadelphia 76ers"},
    ...
  ],
  "all_plays": [ ... ],  // full PBP with wallclock timestamps
  "linescores": {"ATL": ["28", "30", "25", "29"], "PHI": ["24", "32", "27", "25"]}
}
```

The critical metadata for joining with our BBO data is: `sport` + `date` + team abbreviations. We use these to match to Kalshi tickers like `KXNBAGAME-26MAR07PHIATL-PHI`.

## CLI interface

```
python3 espn_scraper.py                      # scrape all dates (March 4-8, 2026), all sports
python3 espn_scraper.py --dates 20260304     # single date
python3 espn_scraper.py --sports nba nhl     # specific sports only
python3 espn_scraper.py --output data/       # custom output dir
python3 espn_scraper.py --csv                # also write flat CSV
python3 espn_scraper.py --delay 0.3          # custom rate limit delay (default 0.5s)
python3 espn_scraper.py --skip-plays         # skip full PBP to reduce file size
```

## Implementation requirements

- Use `requests` with a `Session` (reuse connections). Set a browser-like User-Agent header.
- Rate limit: default 0.5s between requests. Configurable via `--delay`.
- Retry logic: 3 retries with backoff. Handle 404 (return None), 429 (wait 5s * attempt), timeouts (15s).
- Skip games with status `STATUS_SCHEDULED`, `STATUS_POSTPONED`, `STATUS_CANCELED` — don't hit summary for those.
- For the probabilities endpoint, only hit it for sports that have win prob (nba, nhl, ncaamb, mlb) and only for completed games.
- Log to stdout with timestamps: which sport/date is being scraped, how many events found, per-game progress (win_prob count, scoring count, play count).
- Print a summary table at the end: per sport — total games, completed, with win_prob, with scoring.
- Handle ESPN's inconsistent response shapes gracefully — lots of `.get()` with defaults, nested dicts that may or may not exist.
- For UFC, competitors might be under `athlete` instead of `team` in the scoreboard response. Handle both.
- Only dependency is `requests`. No other pip packages needed.
- The output dir should be created automatically if it doesn't exist.

## File location
Place the script at the project root: `espn_scraper.py`
