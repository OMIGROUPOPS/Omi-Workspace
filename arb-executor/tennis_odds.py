#!/usr/bin/env python3
"""
Tennis Odds Collector — Phase 1
Polls The Odds API for Pinnacle fair values, matches to Kalshi tickers,
calculates edge, stores in tennis.db, logs for tennis_v4.py to read.
"""

import json, time, os, re, sqlite3, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
import requests

# ── Config ──
ODDS_API_KEY = "936fff28812c240d8bb6c96a63387295"
ODDS_API_BASE = "https://api.the-odds-api.com/v4"
DB_PATH = str(Path(__file__).resolve().parent / "tennis.db")
POLL_INTERVAL = 900  # 15 minutes

# All tennis sport keys on The Odds API
TENNIS_SPORTS = [
    "tennis_atp_barcelona_open", "tennis_atp_munich", "tennis_wta_stuttgart_open",
    "tennis_atp_aus_open_singles", "tennis_atp_canadian_open",
    "tennis_atp_china_open", "tennis_atp_cincinnati_open",
    "tennis_atp_dubai", "tennis_atp_french_open",
    "tennis_atp_indian_wells", "tennis_atp_italian_open",
    "tennis_atp_madrid_open", "tennis_atp_miami_open",
    "tennis_atp_monte_carlo_masters", "tennis_atp_paris_masters",
    "tennis_atp_qatar_open", "tennis_atp_shanghai_masters",
    "tennis_atp_us_open", "tennis_atp_wimbledon",
    "tennis_wta_aus_open_singles", "tennis_wta_canadian_open",
    "tennis_wta_charleston_open", "tennis_wta_china_open",
    "tennis_wta_cincinnati_open", "tennis_wta_dubai",
    "tennis_wta_french_open", "tennis_wta_indian_wells",
    "tennis_wta_italian_open", "tennis_wta_madrid_open",
    "tennis_wta_miami_open", "tennis_wta_qatar_open",
    "tennis_wta_us_open", "tennis_wta_wimbledon",
    "tennis_wta_wuhan_open",
]

SHARP_BOOKS = ["pinnacle", "betfair_ex_eu", "matchbook"]

ET = timezone(timedelta(hours=-4))
LOG_FILE = "/tmp/tennis_odds.log"
_log_file = None

def log(msg):
    global _log_file
    ts = datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    print(line, flush=True)
    if _log_file is None:
        _log_file = open(LOG_FILE, "a", buffering=1)
    _log_file.write(line + "\n")


def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS edge_scores (
        event_ticker TEXT PRIMARY KEY,
        player1_name TEXT,
        player2_name TEXT,
        pinnacle_p1 REAL,
        pinnacle_p2 REAL,
        kalshi_p1 INTEGER,
        kalshi_p2 INTEGER,
        edge_p1 REAL,
        edge_p2 REAL,
        grade TEXT,
        sport_key TEXT,
        commence_time TEXT,
        updated_at TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS name_cache (
        odds_api_name TEXT PRIMARY KEY,
        kalshi_code TEXT,
        confidence REAL,
        updated_at TEXT
    )""")
    conn.commit()
    return conn


def get_kalshi_books():
    """Read current BBO data from tennis_v4's websocket books.
    Falls back to checking recent log entries for PICK_SIDE prices."""
    # We'll read the Kalshi API directly for active market prices
    import base64
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.backends import default_backend
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")
    api_key = os.getenv("KALSHI_API_KEY")
    pk = serialization.load_pem_private_key(
        (Path(__file__).resolve().parent / "kalshi.pem").read_bytes(),
        password=None, backend=default_backend())
    BASE = "https://api.elections.kalshi.com/trade-api/v2"

    def sign(method, path):
        ts = str(int(time.time() * 1000))
        sp = "/trade-api/v2" + path.split("?")[0]
        msg = ts + method + sp
        sig = pk.sign(msg.encode(), padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
        return {"KALSHI-ACCESS-KEY": api_key,
                "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
                "KALSHI-ACCESS-TIMESTAMP": ts}

    # Get all active tennis markets with prices
    kalshi_markets = {}
    for series in ["KXATPMATCH", "KXWTAMATCH", "KXATPCHALLENGERMATCH", "KXWTACHALLENGERMATCH"]:
        try:
            r = requests.get(BASE + "/markets?series_ticker=%s&status=open&limit=500" % series,
                           headers=sign("GET", "/markets"), timeout=15)
            if r.status_code == 200:
                for m in r.json().get("markets", []):
                    ticker = m.get("ticker", "")
                    event = m.get("event_ticker", "")
                    yes_bid = m.get("yes_bid_dollars", "0")
                    title = m.get("title", "")
                    side = ticker.split("-")[-1] if "-" in ticker else ""
                    if event not in kalshi_markets:
                        kalshi_markets[event] = {}
                    last_price = m.get("last_price_dollars", m.get("last_price", "0"))
                    kalshi_markets[event][side] = {
                        "ticker": ticker,
                        "bid": int(float(yes_bid) * 100) if yes_bid else 0,
                        "last_trade_price": int(float(last_price) * 100) if last_price and float(last_price) > 0 else 0,
                        "title": title,
                    }
        except Exception as e:
            log("[KALSHI_ERR] %s: %s" % (series, e))
    return kalshi_markets


def fuzzy_match_name(odds_name, kalshi_sides, name_cache):
    """Match an Odds API player name to a Kalshi side code.
    Requires first+last name agreement to prevent last-name collisions.
    Returns (side_code, confidence) or (None, 0)."""

    if odds_name in name_cache:
        return name_cache[odds_name], 1.0

    odds_parts = odds_name.split()
    if len(odds_parts) < 2:
        return None, 0  # single word too ambiguous

    odds_first = odds_parts[0].upper()
    odds_last = odds_parts[-1].upper()
    odds_full = odds_name.upper()

    best_match = None
    best_score = 0

    for side_code, side_info in kalshi_sides.items():
        title = side_info.get("title", "")
        title_clean = title.replace("Will ", "").split(" win ")[0].strip()
        title_upper = title_clean.upper()

        has_last = odds_last in title_upper
        has_first = odds_first in title_upper

        # REJECT: last name matches but first name doesn't
        # Prevents Lloyd Harris -> Billy Harris collisions
        if has_last and not has_first:
            continue

        # Both first and last present
        if has_first and has_last:
            if odds_full in title_upper:
                best_match = side_code
                best_score = 1.0
                break
            ratio = SequenceMatcher(None, odds_full, title_upper).ratio()
            if ratio > best_score and ratio > 0.75:
                best_match = side_code
                best_score = ratio
            elif best_score < 0.9:
                best_match = side_code
                best_score = 0.9

    if best_match and best_score >= 0.75:
        name_cache[odds_name] = best_match
        return best_match, best_score

    return None, 0


def calc_no_vig(odds1, odds2):
    """Calculate no-vig fair probabilities from decimal odds."""
    if odds1 <= 1 or odds2 <= 1:
        return None, None
    raw1 = 1.0 / odds1
    raw2 = 1.0 / odds2
    total = raw1 + raw2
    return raw1 / total, raw2 / total


def grade_edge(edge_cents):
    """Grade the edge in cents."""
    if edge_cents >= 5: return "A"
    if edge_cents >= 2: return "B"
    if edge_cents >= -2: return "C"
    if edge_cents >= -5: return "D"
    return "F"


def poll_odds(conn, name_cache):
    """Single poll cycle: fetch odds, match, calculate edges."""
    log("[POLL] Starting odds poll...")

    # Get active sports first
    try:
        r = requests.get(ODDS_API_BASE + "/sports", params={"apiKey": ODDS_API_KEY}, timeout=15)
        all_sports = r.json() if r.status_code == 200 else []
        active = set(s["key"] for s in all_sports if s.get("active"))
        active_tennis = [s for s in TENNIS_SPORTS if s in active]
    except Exception as e:
        log("[ERR] Sports fetch: %s" % e)
        return

    if not active_tennis:
        log("[POLL] No active tennis tournaments")
        return

    log("[POLL] Active tournaments: %s" % ", ".join(active_tennis))

    # Get Kalshi markets for matching
    kalshi_markets = get_kalshi_books()
    log("[KALSHI] %d active events" % len(kalshi_markets))

    # Poll each active tournament
    total_matched = 0
    total_unmatched = 0
    cur = conn.cursor()

    for sport_key in active_tennis:
        try:
            r = requests.get(ODDS_API_BASE + "/sports/%s/odds" % sport_key, params={
                "apiKey": ODDS_API_KEY,
                "regions": "eu,us",
                "markets": "h2h",
                "oddsFormat": "decimal",
            }, timeout=15)
            if r.status_code != 200:
                log("[ERR] %s: HTTP %d" % (sport_key, r.status_code))
                continue
            remaining = r.headers.get("x-requests-remaining", "?")
            events = r.json()
        except Exception as e:
            log("[ERR] %s: %s" % (sport_key, e))
            continue

        for event in events:
            home = event.get("home_team", "")
            away = event.get("away_team", "")
            commence = event.get("commence_time", "")

            # Find Pinnacle odds (primary), fall back to other sharp books
            pin_home = pin_away = 0
            for bk in event.get("bookmakers", []):
                if bk["key"] in SHARP_BOOKS:
                    for mkt in bk.get("markets", []):
                        if mkt["key"] == "h2h":
                            outcomes = dict((o["name"], o["price"]) for o in mkt.get("outcomes", []))
                            h = outcomes.get(home, 0)
                            a = outcomes.get(away, 0)
                            if h > 0 and a > 0 and bk["key"] == "pinnacle":
                                pin_home = h
                                pin_away = a
                            elif h > 0 and a > 0 and pin_home == 0:
                                pin_home = h
                                pin_away = a

            if pin_home == 0 or pin_away == 0:
                continue

            fair_home, fair_away = calc_no_vig(pin_home, pin_away)
            if not fair_home:
                continue

            # Match to Kalshi event
            matched_event = None
            home_code = away_code = None
            kalshi_home_bid = kalshi_away_bid = 0

            for event_ticker, sides in kalshi_markets.items():
                if len(sides) < 2:
                    continue
                h_match, h_conf = fuzzy_match_name(home, sides, name_cache)
                a_match, a_conf = fuzzy_match_name(away, sides, name_cache)

                if h_match and a_match and h_match != a_match:
                    if h_match not in sides or a_match not in sides:
                        continue
                    matched_event = event_ticker
                    home_code = h_match
                    away_code = a_match
                    kalshi_home_bid = sides[home_code]["bid"]
                    kalshi_away_bid = sides[away_code]["bid"]
                    kalshi_home_lt = sides[home_code].get("last_trade_price", 0)
                    kalshi_away_lt = sides[away_code].get("last_trade_price", 0)
                    break

            if matched_event:
                total_matched += 1

                # Capture ALL books' no-vig FV
                books_data = []
                for bk in event.get("bookmakers", []):
                    for mkt in bk.get("markets", []):
                        if mkt["key"] == "h2h":
                            outcomes = dict((o["name"], o["price"]) for o in mkt.get("outcomes", []))
                            h = outcomes.get(home, 0)
                            a = outcomes.get(away, 0)
                            if h > 0 and a > 0:
                                bk_fair_h, bk_fair_a = calc_no_vig(h, a)
                                if bk_fair_h:
                                    raw_sum = (1.0/h) + (1.0/a)
                                    vig = round((raw_sum - 1.0) * 100, 2)
                                    books_data.append({
                                        "book_key": bk["key"],
                                        "raw_odds_p1": h, "raw_odds_p2": a,
                                        "book_p1_fv_cents": round(bk_fair_h * 100, 1),
                                        "book_p2_fv_cents": round(bk_fair_a * 100, 1),
                                        "vig_pct": vig,
                                    })

                now = datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S")

                # Insert ALL books into book_prices
                for bd in books_data:
                    cur.execute("INSERT OR REPLACE INTO book_prices VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (matched_event, bd["book_key"], home, away,
                         bd["book_p1_fv_cents"], bd["book_p2_fv_cents"],
                         bd["raw_odds_p1"], bd["raw_odds_p2"], bd["vig_pct"],
                         sport_key, commence, now))

                if not books_data:
                    log("[SKIP] %s vs %s — no books with odds" % (home[:20], away[:20]))
                    continue

                # Pinnacle-first, else aggregate
                pinnacle = next((b for b in books_data if b["book_key"] == "pinnacle"), None)
                if pinnacle:
                    chosen_p1 = pinnacle["book_p1_fv_cents"]
                    chosen_p2 = pinnacle["book_p2_fv_cents"]
                    fv_tier = 1
                    fv_source = "pinnacle"
                    num_books = 1
                else:
                    chosen_p1 = round(sum(b["book_p1_fv_cents"] for b in books_data) / len(books_data), 1)
                    chosen_p2 = round(sum(b["book_p2_fv_cents"] for b in books_data) / len(books_data), 1)
                    fv_tier = 2
                    fv_source = "aggregate_%d_books" % len(books_data)
                    num_books = len(books_data)

                # Edge against Kalshi last-traded
                if kalshi_home_lt == 0 or kalshi_away_lt == 0:
                    log("[SKIP] %s vs %s — no real Kalshi trades yet (books=%d)" % (home[:20], away[:20], num_books))
                    # Still store book_prices but skip edge calculation
                    continue

                edge_home = chosen_p1 - kalshi_home_lt
                edge_away = chosen_p2 - kalshi_away_lt
                leader_edge = edge_home if kalshi_home_bid >= kalshi_away_bid else edge_away
                grade = grade_edge(leader_edge)

                cur.execute("INSERT OR REPLACE INTO edge_scores VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (matched_event, home, away,
                     chosen_p1, chosen_p2,
                     kalshi_home_lt, kalshi_away_lt,
                     round(edge_home, 1), round(edge_away, 1),
                     grade, sport_key, commence, now,
                     fv_tier, fv_source, num_books))

                log("[EDGE] %s vs %s | fv=%s (tier %d) | p1/p2=%.1fc/%.1fc | lt=%dc/%dc | edge=%+.1fc/%+.1fc | books=%d | %s" % (
                    home[:20], away[:20],
                    fv_source, fv_tier,
                    chosen_p1, chosen_p2,
                    kalshi_home_lt, kalshi_away_lt,
                    edge_home, edge_away,
                    num_books, matched_event[:40]))
            else:
                total_unmatched += 1
                log("[UNMATCHED] %s vs %s (no Kalshi match)" % (home[:25], away[:25]))

    conn.commit()

    # Save name cache
    for name, code in name_cache.items():
        cur.execute("INSERT OR REPLACE INTO name_cache VALUES (?,?,?,?)",
                    (name, code, 1.0, datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

    log("[POLL] Done: %d matched, %d unmatched, API remaining: %s" % (
        total_matched, total_unmatched, remaining))


def main():
    log("=" * 60)
    log("Tennis Odds Collector — Phase 1")
    log("Polling every %ds for %d tournament keys" % (POLL_INTERVAL, len(TENNIS_SPORTS)))
    log("=" * 60)

    init_db()

    # Load name cache from DB
    name_cache = {}
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        cur = conn.cursor()
        cur.execute("SELECT odds_api_name, kalshi_code FROM name_cache")
        for row in cur.fetchall():
            name_cache[row[0]] = row[1]
        conn.close()
        log("[INIT] Loaded %d cached name mappings" % len(name_cache))
    except:
        pass

    # Initial poll immediately
    conn = sqlite3.connect(DB_PATH, timeout=30)
    poll_odds(conn, name_cache)
    conn.close()

    # Then loop with priority-based cadence
    last_poll = time.time()
    while True:
        # Priority polling: check if any urgent events need faster refresh
        now = time.time()
        elapsed = now - last_poll

        # Default: 900s. But if we know urgent events exist, poll faster.
        interval = POLL_INTERVAL  # default 900s
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30)
            cur = conn.cursor()
            cur.execute("SELECT commence_time FROM edge_scores WHERE commence_time != ''")
            for row in cur.fetchall():
                try:
                    ct = datetime.fromisoformat(row[0].replace("Z", "+00:00"))
                    time_to_start = (ct - datetime.now(timezone.utc)).total_seconds()
                    if time_to_start < 7200:   # < 2 hours
                        interval = min(interval, 90)
                    elif time_to_start < 21600: # < 6 hours
                        interval = min(interval, 300)
                except:
                    pass
            conn.close()
        except:
            pass

        if elapsed < interval:
            time.sleep(min(30, interval - elapsed))
            continue

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30)
            poll_odds(conn, name_cache)
            last_poll = time.time()
        except Exception as e:
            log("[ERR] Poll failed: %s" % e)
            import traceback
            traceback.print_exc()
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass


if __name__ == "__main__":
    main()
