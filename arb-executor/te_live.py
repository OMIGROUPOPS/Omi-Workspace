#!/usr/bin/env python3
"""
TennisExplorer Live Data Pipeline
- Live scores every 60s
- Bookmaker odds every 5min
- Player profiles once per day
"""

import sqlite3
import requests
import re
import time
import os
import sys
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

DB_PATH = str(Path(__file__).resolve().parent / 'tennis.db')
TE_BASE = 'https://www.tennisexplorer.com'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}
POLL_INTERVAL = 60  # seconds

def get_db():
    return sqlite3.connect(DB_PATH)

def init_tables():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS live_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        te_match_id TEXT,
        player1 TEXT,
        player2 TEXT,
        p1_sets INTEGER DEFAULT 0,
        p2_sets INTEGER DEFAULT 0,
        p1_games TEXT DEFAULT '',
        p2_games TEXT DEFAULT '',
        status TEXT DEFAULT 'live',
        kalshi_ticker TEXT,
        last_updated TEXT,
        UNIQUE(te_match_id)
    )''')
    # [C-RETENTION 2026-07-06] observed true starts: the FIRST in-play row per match,
    # set-once (INSERT OR IGNORE). Additive only -- no existing consumer's read path
    # touched (live_v4 reads book_prices/kalshi_price_snapshots only; grep-proofed).
    # Growth bound: <= global slate (~600-1000 matches/day) x ~120B = <=120KB/day.
    c.execute('''CREATE TABLE IF NOT EXISTS observed_starts (
        te_match_id TEXT PRIMARY KEY,
        player1 TEXT,
        player2 TEXT,
        kalshi_ticker TEXT,
        first_inplay_at TEXT NOT NULL,
        inserted_at TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookmaker_odds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        te_match_id TEXT,
        player1 TEXT,
        player2 TEXT,
        p1_decimal_odds REAL,
        p2_decimal_odds REAL,
        p1_implied_prob REAL,
        p2_implied_prob REAL,
        kalshi_ticker TEXT,
        kalshi_price INTEGER,
        edge_pct REAL,
        scraped_at TEXT,
        UNIQUE(te_match_id, scraped_at)
    )''')
    conn.commit()
    conn.close()
    log('Tables initialized')

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print('[%s] %s' % (ts, msg), flush=True)

# ── STEP 1: LIVE SCORE SCRAPER ──

def scrape_live_scores():
    """Scrape TE results page for all live/recent match scores.
    TE HTML structure: paired <tr> rows per match.
    Row A: time, player1 name, player1 result, set scores, match-detail link
    Row B: player2 name, player2 result, set scores
    Elements appear in sequence: time, name, result, scores, name, result, scores, link
    """
    try:
        r = requests.get(TE_BASE + '/results/', headers=HEADERS, timeout=15)
        if r.status_code != 200:
            log('TE results page: %d' % r.status_code)
            return []
    except Exception as e:
        log('TE error: %s' % str(e)[:60])
        return []

    html = r.text
    matches = []

    # Strategy: extract all key elements in order, then group them.
    # Each match has: time, p1_name, p1_result, match_id, p2_name, p2_result
    # Times appear in "first time" cells, names in "t-name" cells

    # Find all match blocks by splitting on "first time" cells
    time_pattern = r'class="first time"[^>]*>(.*?)</td>'
    time_splits = re.split(time_pattern, html, flags=re.DOTALL)

    # time_splits alternates: [before, time1, after_time1, time2, after_time2, ...]
    for i in range(1, len(time_splits) - 1, 2):
        time_str = re.sub(r'<[^>]+>', '', time_splits[i]).strip()
        block = time_splits[i + 1]

        # Get the block up to the next time cell or end
        # Extract match ID
        mid = re.search(r'match-detail/\?id=(\d+)', block)
        if not mid:
            continue
        match_id = mid.group(1)

        # Extract player names (in order: p1 then p2)
        names = re.findall(r'class="t-name"[^>]*>\s*<a[^>]*>([^<]+)</a>', block)
        if len(names) < 2:
            continue
        p1 = names[0].strip()
        p2 = names[1].strip()

        # Extract set results: "result" class gives total sets won
        results = re.findall(r'class="result">(\d*)</td>', block)
        p1_result = int(results[0]) if results and results[0] else 0
        p2_result = int(results[1]) if len(results) > 1 and results[1] else 0

        # Extract individual set scores from "score" class
        scores = re.findall(r'class="score">(\d+)', block)
        # Scores are: p1_s1, p1_s2, p1_s3, p1_s4, p1_s5, p2_s1, p2_s2, ...
        # Actually they alternate by row. Let's just use the result counts.
        p1_sets = p1_result
        p2_sets = p2_result

        is_live = 'Liv' in time_str
        is_finished = bool(re.search(r'\d{2}:\d{2}', time_str)) and not is_live

        status = 'live' if is_live else ('finished' if is_finished else 'scheduled')

        matches.append({
            'match_id': match_id,
            'player1': p1, 'player2': p2,
            'p1_sets': p1_sets, 'p2_sets': p2_sets,
            'p1_games': '', 'p2_games': '',
            'status': status,
            'time': time_str,
        })

    return matches

def match_to_kalshi(te_name, kalshi_codes):
    """Fuzzy match TE player name to Kalshi ticker code."""
    te_lower = te_name.lower().replace('.', '').replace(',', '').strip()
    best_code = None
    best_score = 0

    for code, kalshi_name in kalshi_codes.items():
        # Try exact code match first (TE often shows last name which matches 3-letter code)
        te_parts = te_lower.split()
        for part in te_parts:
            if len(part) >= 3 and part[:3].upper() == code:
                return code

        # Fuzzy match on full name
        if kalshi_name:
            score = SequenceMatcher(None, te_lower, kalshi_name.lower()).ratio()
            if score > best_score and score > 0.5:
                best_score = score
                best_code = code

    return best_code

def save_live_scores(matches):
    """Save scraped matches to live_scores table."""
    conn = get_db()
    c = conn.cursor()

    # Get Kalshi player names for matching
    c.execute('SELECT kalshi_code, name FROM players WHERE name IS NOT NULL')
    kalshi_codes = {r[0]: r[1] for r in c.fetchall()}

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    saved = 0

    for m in matches:
        # Try to match to Kalshi ticker
        k1 = match_to_kalshi(m['player1'], kalshi_codes)
        k2 = match_to_kalshi(m['player2'], kalshi_codes)
        kalshi_ticker = k1 or k2 or ''

        # [C-RETENTION] bank the observed true start BEFORE the overwrite below
        # erases the in-play transition. Set-once per match; 'live' rows only.
        if m['status'] == 'live':
            c.execute('''INSERT OR IGNORE INTO observed_starts
                (te_match_id, player1, player2, kalshi_ticker, first_inplay_at, inserted_at)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (m['match_id'], m['player1'], m['player2'], kalshi_ticker, now, now))
        c.execute('''INSERT OR REPLACE INTO live_scores
            (te_match_id, player1, player2, p1_sets, p2_sets, p1_games, p2_games,
             status, kalshi_ticker, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (m['match_id'], m['player1'], m['player2'],
             m['p1_sets'], m['p2_sets'], m['p1_games'], m['p2_games'],
             m['status'], kalshi_ticker, now))
        saved += 1

    conn.commit()
    conn.close()
    return saved


def bank_observed_starts():
    """[C-RETENTION-2 2026-07-06] The /results/ page NEVER carries in-play rows
    (0 'Liv' time-cells all-time -- finished matches show their start clock, so
    the 'live' status branch was dead code since April). Live matches live at
    /live/: every match visible there is in-play RIGHT NOW. Bank first sighting
    into observed_starts, set-once. Additive; nothing else touched."""
    try:
        r = requests.get(TE_BASE + '/live/', headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return 0
    except Exception as e:
        log('TE live page error: %s' % str(e)[:60])
        return 0
    pairs = re.findall(r'match-detail/\?id=(\d+)[^>]*>(.*?)</a>', r.text, re.S)
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT kalshi_code, name FROM players WHERE name IS NOT NULL')
    kalshi_codes = {row[0]: row[1] for row in c.fetchall()}
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    banked = 0
    seen = set()
    for mid, txt in pairs:
        if mid in seen:
            continue
        seen.add(mid)
        name = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', txt)).strip()
        if ' - ' not in name:
            continue
        p1, p2 = [x.strip() for x in name.split(' - ', 1)]
        if not p1 or not p2:
            continue
        k = match_to_kalshi(p1, kalshi_codes) or match_to_kalshi(p2, kalshi_codes) or ''
        c.execute("""INSERT OR IGNORE INTO observed_starts
            (te_match_id, player1, player2, kalshi_ticker, first_inplay_at, inserted_at)
            VALUES (?, ?, ?, ?, ?, ?)""", (mid, p1, p2, k, now, now))
        banked += c.rowcount
    conn.commit()
    conn.close()
    return banked


# ── STEP 2: BOOKMAKER ODDS SCRAPER ──

def scrape_match_odds(match_id):
    """Scrape bookmaker odds from a TE match detail page."""
    try:
        url = '%s/match-detail/?id=%s' % (TE_BASE, match_id)
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
    except:
        return None

    html = r.text

    # Extract player names from the match page
    names = re.findall(r'class="t-name"[^>]*>.*?<a[^>]*>([^<]+)</a>', html[:5000], re.DOTALL)
    p1 = names[0].strip() if names else '?'
    p2 = names[1].strip() if len(names) > 1 else '?'

    # Extract decimal odds (format: 1.50, 2.30, etc.)
    odds_values = re.findall(r'(\d+\.\d{2})', html[:15000])

    # Filter to reasonable odds range (1.01 - 20.00)
    valid_odds = [float(o) for o in odds_values if 1.01 <= float(o) <= 20.0]

    if len(valid_odds) >= 2:
        # First pair is usually the main bookmaker
        p1_odds = valid_odds[0]
        p2_odds = valid_odds[1]
        p1_prob = 1 / p1_odds
        p2_prob = 1 / p2_odds

        return {
            'match_id': match_id,
            'player1': p1, 'player2': p2,
            'p1_odds': p1_odds, 'p2_odds': p2_odds,
            'p1_prob': round(p1_prob, 4), 'p2_prob': round(p2_prob, 4),
        }

    return None

def scrape_upcoming_odds():
    """Scrape odds for upcoming matches."""
    try:
        r = requests.get(TE_BASE + '/next/', headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return []
    except:
        return []

    html = r.text
    match_ids = re.findall(r'match-detail/\?id=(\d+)', html)
    unique_ids = list(dict.fromkeys(match_ids))[:20]  # Cap at 20, dedupe

    results = []
    for mid in unique_ids:
        odds = scrape_match_odds(mid)
        if odds:
            results.append(odds)
        time.sleep(1)  # Rate limit

    return results

def save_odds(odds_list):
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    saved = 0

    for o in odds_list:
        c.execute('''INSERT OR IGNORE INTO bookmaker_odds
            (te_match_id, player1, player2, p1_decimal_odds, p2_decimal_odds,
             p1_implied_prob, p2_implied_prob, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (o['match_id'], o['player1'], o['player2'],
             o['p1_odds'], o['p2_odds'], o['p1_prob'], o['p2_prob'], now))
        saved += c.rowcount

    conn.commit()
    conn.close()
    return saved


# ── STEP 3: PLAYER PROFILE SCRAPER ──

def scrape_player_profile(name_slug):
    """Scrape TE player profile for ranking, W/L, surface stats."""
    try:
        url = '%s/player/%s/' % (TE_BASE, name_slug)
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
    except:
        return None

    html = r.text
    result = {'slug': name_slug}

    # Current ranking
    rank_m = re.search(r'Current/Highest ranking.*?<td[^>]*>\s*(\d+)', html, re.DOTALL | re.IGNORECASE)
    if not rank_m:
        rank_m = re.search(r'Ranking.*?(\d+)', html[:3000], re.DOTALL)
    if rank_m:
        result['ranking'] = int(rank_m.group(1))

    # Win/loss from stat tables
    wl_matches = re.findall(r'<td[^>]*>(\d+)</td>\s*<td[^>]*>/</td>\s*<td[^>]*>(\d+)</td>', html[:8000])
    if wl_matches:
        result['wins'] = int(wl_matches[0][0])
        result['losses'] = int(wl_matches[0][1])

    return result

def update_player_profiles():
    """Update top players from TE."""
    conn = get_db()
    c = conn.cursor()

    # Get players with most trades, no recent ranking update
    c.execute('''SELECT p.kalshi_code, p.name FROM players p
                 JOIN matches m ON m.our_side = p.kalshi_code
                 WHERE p.name IS NOT NULL
                 GROUP BY p.kalshi_code
                 HAVING COUNT(*) >= 5
                 ORDER BY COUNT(*) DESC LIMIT 50''')

    players = c.fetchall()
    updated = 0

    for code, name in players:
        if not name:
            continue
        # Convert name to TE slug: "Sinner J." -> "sinner"
        parts = name.lower().replace('.', '').replace(',', '').split()
        if not parts:
            continue
        # Try last name first, then first name
        for slug in [parts[-1], parts[0], '-'.join(parts)]:
            if len(slug) < 3:
                continue
            profile = scrape_player_profile(slug)
            if profile and 'ranking' in profile:
                c.execute('UPDATE players SET ranking = ?, last_updated = date("now") WHERE kalshi_code = ?',
                          (profile['ranking'], code))
                updated += 1
                log('Updated %s (%s): rank=%d' % (code, name, profile['ranking']))
                break
            time.sleep(1)

    conn.commit()
    conn.close()
    return updated


# ── MAIN LOOP ──

def run_once():
    """Single scrape cycle."""
    # Live scores
    matches = scrape_live_scores()
    live = [m for m in matches if m['status'] == 'live']
    finished = [m for m in matches if m['status'] == 'finished']
    saved = save_live_scores(matches)
    banked = bank_observed_starts()
    if banked:
        log('Observed starts banked: %d' % banked)
    log('Scores: %d total (%d live, %d finished), %d saved' % (
        len(matches), len(live), len(finished), saved))

    return len(matches)

def run_odds():
    """Odds scrape cycle (less frequent)."""
    odds = scrape_upcoming_odds()
    saved = save_odds(odds)
    log('Odds: %d matches scraped, %d saved' % (len(odds), saved))

def main():
    init_tables()
    log('TE Live Pipeline starting (poll every %ds)' % POLL_INTERVAL)

    last_odds = 0
    last_profiles = 0
    cycle = 0

    while True:
        try:
            now = time.time()

            # Live scores every cycle
            run_once()

            # Odds every 5 min
            if now - last_odds >= 300:
                run_odds()
                last_odds = now

            # Profiles once per hour
            if now - last_profiles >= 3600:
                updated = update_player_profiles()
                log('Profiles: updated %d players' % updated)
                last_profiles = now

            cycle += 1
            time.sleep(max(1, POLL_INTERVAL - (time.time() - now)))

        except KeyboardInterrupt:
            log('Shutting down')
            break
        except Exception as e:
            log('Error: %s' % str(e)[:80])
            time.sleep(30)

if __name__ == '__main__':
    if '--once' in sys.argv:
        init_tables()
        n = run_once()
        print()
        # Show what we got
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT player1, player2, p1_sets, p2_sets, p1_games, p2_games, status, kalshi_ticker FROM live_scores ORDER BY status, last_updated DESC LIMIT 20')
        print('%-20s %-20s %5s %10s %10s %8s %6s' % ('PLAYER 1', 'PLAYER 2', 'SETS', 'P1 GAMES', 'P2 GAMES', 'STATUS', 'KALSHI'))
        print('-' * 85)
        for p1, p2, s1, s2, g1, g2, status, kt in c.fetchall():
            print('%-20s %-20s %d-%d   %-10s %-10s %-8s %s' % (
                p1[:20], p2[:20], s1, s2, g1, g2, status, kt or '-'))
        conn.close()

        if '--odds' in sys.argv:
            print()
            run_odds()
            conn = get_db()
            c = conn.cursor()
            c.execute('SELECT player1, player2, p1_decimal_odds, p2_decimal_odds, p1_implied_prob FROM bookmaker_odds ORDER BY scraped_at DESC LIMIT 10')
            print()
            print('%-20s %-20s %6s %6s %6s' % ('PLAYER 1', 'PLAYER 2', 'P1_ODD', 'P2_ODD', 'P1_IMP'))
            print('-' * 60)
            for p1, p2, o1, o2, ip in c.fetchall():
                print('%-20s %-20s %6.2f %6.2f %5.0f%%' % (p1[:20], p2[:20], o1, o2, ip*100))
            conn.close()
    else:
        main()
