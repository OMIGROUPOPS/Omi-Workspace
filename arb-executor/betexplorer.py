#!/usr/bin/env python3
"""
betexplorer.py — Scrape ATP/WTA Challenger match odds from BetExplorer.

Extracts no-vig FV for every match in a Challenger tournament page.
Writes to tennis.db betexplorer_staging table.
"""

import re, requests, sqlite3, time
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
DB_PATH = str(Path(__file__).resolve().parent / "tennis.db")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Known Challenger tournament URLs
CHALLENGER_URLS = [
    ("Gwangju", "https://www.betexplorer.com/tennis/challenger-men-singles/gwangju/"),
    ("Savannah", "https://www.betexplorer.com/tennis/challenger-men-singles/savannah/"),
    ("Shymkent", "https://www.betexplorer.com/tennis/challenger-men-singles/shymkent/"),
    ("Abidjan", "https://www.betexplorer.com/tennis/challenger-men-singles/abidjan/"),
    ("Rome", "https://www.betexplorer.com/tennis/challenger-men-singles/rome/"),
    ("Busan", "https://www.betexplorer.com/tennis/challenger-men-singles/busan/"),
    ("Oeiras", "https://www.betexplorer.com/tennis/challenger-men-singles/oeiras/"),
]


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
    conn = sqlite3.connect(DB_PATH)
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


if __name__ == "__main__":
    print("BetExplorer Challenger Scraper")
    print("=" * 50)
    total = 0
    for tournament, url in CHALLENGER_URLS:
        matches = fetch_tournament(url)
        if matches:
            n = store_matches(matches, url, tournament)
            print("%s: %d matches" % (tournament, len(matches)))
            for m in matches:
                print("  %-20s vs %-20s | %.2f / %.2f | FV: %.1fc / %.1fc | vig: %.1f%%" % (
                    m["p1_name"][:20], m["p2_name"][:20],
                    m["raw_o1"], m["raw_o2"],
                    m["p1_fv"], m["p2_fv"], m["vig_pct"]))
            total += n
        else:
            print("%s: 0 matches (page empty or error)" % tournament)
        time.sleep(1)
    print()
    print("Total: %d matches stored in betexplorer_staging" % total)
