#!/usr/bin/env python3
"""
betexplorer.py — Scrape ATP/WTA Challenger match odds from BetExplorer.

Continuous sidecar: scrapes every 10 minutes, stores de-vigged FV in
betexplorer_staging, then matches to Kalshi events and flows into
book_prices with book_key='betexplorer'.
"""

import re, json, requests, sqlite3, time, os, base64, traceback
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv

ET = ZoneInfo("America/New_York")
DB_PATH = str(Path(__file__).resolve().parent / "tennis.db")
POLL_INTERVAL = 600  # 10 minutes

def _write_heartbeat(name, **extra):
    hb = {"ts": int(time.time()), "name": name, "status": "ok", **extra}
    try:
        with open("/tmp/heartbeat_%s.json" % name, "w") as f:
            json.dump(hb, f)
    except Exception:
        pass

load_dotenv(Path(__file__).resolve().parent / ".env")
_api_key = os.getenv("KALSHI_API_KEY")
_pk = serialization.load_pem_private_key(
    (Path(__file__).resolve().parent / "kalshi.pem").read_bytes(),
    password=None, backend=default_backend())
_BASE = "https://api.elections.kalshi.com"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

CHALLENGER_URLS = [
    ("Gwangju", "https://www.betexplorer.com/tennis/challenger-men-singles/gwangju/"),
    ("Savannah", "https://www.betexplorer.com/tennis/challenger-men-singles/savannah/"),
    ("Shymkent", "https://www.betexplorer.com/tennis/challenger-men-singles/shymkent/"),
    ("Abidjan", "https://www.betexplorer.com/tennis/challenger-men-singles/abidjan/"),
    ("Rome", "https://www.betexplorer.com/tennis/challenger-men-singles/rome/"),
    ("Busan", "https://www.betexplorer.com/tennis/challenger-men-singles/busan/"),
    ("Oeiras", "https://www.betexplorer.com/tennis/challenger-men-singles/oeiras/"),
]

# WTA Challenger (challenger-women-singles) — the women's slug was never registered
# (ATP_CHALL used challenger-men-singles only): the WTA_CHALL FV gap root-caused in
# fv_overlap_join_v1_run_summary. WTA 125s rotate weekly, so rather than hardcode (the
# latent staleness in the men's static list above) we DISCOVER the currently-active
# women's challengers by cross-referencing the betexplorer index against open Kalshi
# WTA events. The name resolver (match_player) is already gender-agnostic and
# fetch_kalshi_challenger_events() already pulls KXWTACHALLENGERMATCH — so only the
# tournament URLs were missing. Refreshed ~hourly; the small matched set scraped each cycle.
WOMEN_INDEX_URL = "https://www.betexplorer.com/tennis/challenger-women-singles/"
WOMEN_REFRESH_EVERY = 6          # re-discover active women's tournaments every 6 cycles (~hourly)
_women_active = []               # cached [(name, url)] of women's challengers w/ current Kalshi coverage
_women_cycle = 0


def fetch_tournament(url):
    """Fetch tournament page and extract matches with odds."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            return []
        html = r.text
    except Exception as e:
        print("  Error fetching %s: %s" % (url, e))
        return []

    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL)
    matches = []
    for row in rows:
        odds = re.findall(r'data-odd="([0-9.]+)"', row)
        if len(odds) < 2:
            continue
        text = re.sub(r"<[^>]+>", " ", row)
        text = re.sub(r"\s+", " ", text).strip()
        # Match "LastName F. - LastName F." pattern
        m = re.search(r"([A-Z][a-z]+(?: [A-Z][a-z]+)*(?: [A-Z]\.?)+)\s*-\s*([A-Z][a-z]+(?: [A-Z][a-z]+)*(?: [A-Z]\.?)+)", text)
        if not m:
            # Try simpler pattern: "Word W. - Word W."
            m = re.search(r"(\w+ \w\.)\s*-\s*(\w+ \w\.)", text)
        if not m:
            continue
        p1, p2 = m.group(1).strip(), m.group(2).strip()
        try:
            o1, o2 = float(odds[0]), float(odds[1])
        except:
            continue
        if o1 <= 1 or o2 <= 1:
            continue
        r1, r2 = 1.0 / o1, 1.0 / o2
        total = r1 + r2
        fv1 = round(r1 / total * 100, 1)
        fv2 = round(r2 / total * 100, 1)
        vig = round((total - 1) * 100, 2)
        matches.append({
            "p1_name": p1, "p2_name": p2,
            "p1_fv": fv1, "p2_fv": fv2,
            "raw_o1": o1, "raw_o2": o2,
            "vig_pct": vig,
        })
    return matches


def store_matches(matches, source_url, tournament):
    """Insert matches into betexplorer_staging table."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cur = conn.cursor()
    now = datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""CREATE TABLE IF NOT EXISTS betexplorer_staging (
        p1_name TEXT, p2_name TEXT,
        p1_fv_cents REAL, p2_fv_cents REAL,
        raw_odds_p1 REAL, raw_odds_p2 REAL,
        vig_pct REAL,
        tournament TEXT,
        source_url TEXT,
        scraped_at TEXT,
        PRIMARY KEY (p1_name, p2_name, scraped_at)
    )""")

    for m in matches:
        cur.execute("""INSERT OR REPLACE INTO betexplorer_staging VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (m["p1_name"], m["p2_name"], m["p1_fv"], m["p2_fv"],
             m["raw_o1"], m["raw_o2"], m["vig_pct"], tournament, source_url, now))
    conn.commit()
    conn.close()
    return len(matches)


def _kalshi_sign(method, path):
    ts = str(int(time.time() * 1000))
    msg = ts + method + path
    sig = _pk.sign(msg.encode(), padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": _api_key,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
            "KALSHI-ACCESS-TIMESTAMP": ts}


def fetch_kalshi_challenger_events():
    """Fetch all active Kalshi Challenger events for matching."""
    kalshi_events = {}
    for series in ["KXATPCHALLENGERMATCH", "KXWTACHALLENGERMATCH"]:
        path = "/trade-api/v2/markets"
        url = _BASE + path + "?series_ticker=%s&status=open&limit=500" % series
        try:
            r = requests.get(url, headers=_kalshi_sign("GET", path), timeout=15)
            for m in r.json().get("markets", []):
                et = m.get("event_ticker", "")
                yst = m.get("yes_sub_title", "")
                ticker = m.get("ticker", "")
                exp = m.get("expected_expiration_time", "")
                if not et or not yst:
                    continue
                if et not in kalshi_events:
                    kalshi_events[et] = {"players": [], "commence": exp}
                existing = [p[0] for p in kalshi_events[et]["players"]]
                if ticker not in existing:
                    kalshi_events[et]["players"].append((ticker, yst))
        except Exception as e:
            print("  Kalshi fetch error (%s): %s" % (series, e))
    return kalshi_events


def parse_bx_name(bx_name):
    """Parse BetExplorer name format -> (last_name, first_initial)."""
    name = bx_name.strip().rstrip(".")
    parts = name.split()
    if len(parts) < 2:
        return None, None
    initial_idx = None
    for i, p in enumerate(parts):
        cleaned = p.rstrip(".")
        if len(cleaned) == 1 and cleaned.isalpha():
            initial_idx = i
            break
    if initial_idx is None or initial_idx == 0:
        return None, None
    last = " ".join(parts[:initial_idx]).upper()
    initial = parts[initial_idx].rstrip(".").upper()
    return last, initial


def match_player(bx_name, kalshi_players):
    """Match BetExplorer name to Kalshi player list."""
    bx_last, bx_initial = parse_bx_name(bx_name)
    if not bx_last or not bx_initial:
        return None
    for ticker, yst in kalshi_players:
        yst_parts = yst.strip().split()
        if len(yst_parts) < 2:
            continue
        ka_first = yst_parts[0].upper()
        ka_last = " ".join(yst_parts[1:]).upper()
        if bx_last != ka_last:
            bx_tail = bx_last.split()[-1]
            ka_tail = ka_last.split()[-1]
            if bx_tail != ka_tail:
                continue
            bx_tokens = set(bx_last.split())
            ka_tokens = set(ka_last.split())
            if not (bx_tokens & ka_tokens):
                continue
        if not ka_first.startswith(bx_initial):
            continue
        return (ticker, yst)
    return None


def match_and_insert(kalshi_events):
    """Match betexplorer_staging rows to Kalshi events, insert into book_prices."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cur = conn.cursor()
    cur.execute("SELECT p1_name, p2_name, p1_fv_cents, p2_fv_cents, raw_odds_p1, raw_odds_p2, vig_pct, source_url, scraped_at FROM betexplorer_staging ORDER BY scraped_at DESC")
    staging = cur.fetchall()
    matched = 0
    for row in staging:
        p1_name, p2_name, p1_fv, p2_fv, o1, o2, vig, url, scraped = row
        for event_ticker, info in kalshi_events.items():
            players = info["players"]
            p1_match = match_player(p1_name, players)
            p2_match = match_player(p2_name, players)
            if p1_match and p2_match and p1_match[0] != p2_match[0]:
                cur.execute("INSERT OR REPLACE INTO book_prices VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (event_ticker, "betexplorer",
                     p1_match[1], p2_match[1],
                     p1_fv, p2_fv, o1, o2, vig,
                     "betexplorer_challenger", info["commence"], scraped))
                matched += 1
                break
    conn.commit()
    conn.close()
    return matched


def discover_active_women_urls(kalshi_events):
    """Return [(name, url)] for challenger-women-singles tournaments that currently have
    a match joining an open Kalshi WTA event. Cross-reference (not hardcoded) so it
    auto-tracks weekly WTA 125 rotation. Empty on fetch failure (men-only fallback,
    no regression)."""
    wta = {e: i for e, i in kalshi_events.items() if "KXWTACHALLENGER" in e}
    if not wta:
        return []
    try:
        h = requests.get(WOMEN_INDEX_URL, headers={"User-Agent": UA}, timeout=20).text
    except Exception as e:
        print("  women index fetch error: %s" % e)
        return []
    slugs = sorted(set(re.findall(r"/tennis/challenger-women-singles/([a-z0-9-]+)/", h)))
    active = []
    for s in slugs:
        url = WOMEN_INDEX_URL + s + "/"
        ms = fetch_tournament(url)
        if any(match_player(m["p1_name"], i["players"]) and match_player(m["p2_name"], i["players"])
               for m in ms for i in wta.values()):
            active.append((s.replace("-", " ").title(), url))
        time.sleep(0.3)
    return active


def poll_cycle():
    """One full scrape + match cycle."""
    global _women_active, _women_cycle
    now_et = datetime.now(ET)
    kalshi_events = fetch_kalshi_challenger_events()
    # Discover active women's challengers (~hourly), then scrape men (static) + women (dynamic).
    if _women_cycle % WOMEN_REFRESH_EVERY == 0:
        _women_active = discover_active_women_urls(kalshi_events)
        print("  [women discovery] active WTA challenger tournaments: %s" % [a[0] for a in _women_active])
    _women_cycle += 1

    total_scraped = 0
    for tournament, url in list(CHALLENGER_URLS) + _women_active:
        matches = fetch_tournament(url)
        if matches:
            n = store_matches(matches, url, tournament)
            total_scraped += n
        time.sleep(1)

    matched = match_and_insert(kalshi_events)

    print("[%s] Scraped %d matches, matched %d to Kalshi (%d Kalshi events; %d women's tourn)" % (
        now_et.strftime("%I:%M:%S %p ET"), total_scraped, matched, len(kalshi_events), len(_women_active)))
    _write_heartbeat("betexplorer", matches_scraped=total_scraped, matched_to_kalshi=matched)


if __name__ == "__main__":
    print("BetExplorer Challenger Sidecar — polling every %ds" % POLL_INTERVAL)
    print("=" * 50)
    while True:
        try:
            poll_cycle()
        except Exception as e:
            print("Error: %s" % e)
            traceback.print_exc()
        time.sleep(POLL_INTERVAL)
