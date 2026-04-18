#!/usr/bin/env python3
"""
Pinnacle vs Kalshi pregame pricing backtest.
Pulls historical Pinnacle odds for ATP_MAIN + WTA_MAIN matches,
compares to Kalshi tick data from match_ticks_full/.
"""

import csv, json, os, time, math, requests
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

KEY = "936fff28812c240d8bb6c96a63387295"
BASE = "https://api.the-odds-api.com/v4"
FACTS_PATH = "/root/Omi-Workspace/arb-executor/analysis/match_facts.csv"
TICKS_DIR = "/root/Omi-Workspace/arb-executor/analysis/match_ticks_full"
OUT_PATH = "/root/Omi-Workspace/arb-executor/analysis/pinnacle_kalshi_timing.csv"
CONFIG_PATH = "/root/Omi-Workspace/arb-executor/config/deploy_v3.json"

# All tournament sport keys that might have been active Mar 18 - Apr 15
ATP_SPORT_KEYS = [
    "tennis_atp_miami_open",
    "tennis_atp_monte_carlo_masters",
    "tennis_atp_barcelona_open",
    "tennis_atp_munich",
    "tennis_atp_indian_wells",
    "tennis_atp_dubai",
]
WTA_SPORT_KEYS = [
    "tennis_wta_miami_open",
    "tennis_wta_charleston_open",
    "tennis_wta_indian_wells",
    "tennis_wta_dubai",
    "tennis_wta_stuttgart_open",
]

def remove_vig(odds1, odds2):
    """Remove vig from decimal odds, return (p1_fair, p2_fair) in [0,1]."""
    p1 = 1.0 / odds1
    p2 = 1.0 / odds2
    total = p1 + p2
    return p1 / total, p2 / total

def load_facts():
    """Load match facts for ATP_MAIN and WTA_MAIN."""
    facts = {}
    with open(FACTS_PATH) as f:
        for r in csv.DictReader(f):
            if r["category"] not in ("ATP_MAIN", "WTA_MAIN"):
                continue
            tk = r["ticker_id"]
            facts[tk] = {
                "category": r["category"],
                "side": r["side"],
                "result": r["match_result"],
                "entry_mid": float(r["entry_mid"]),
                "max_bounce": float(r["max_bounce_from_entry"]),
                "pregame_close_ts": int(r["pregame_close_ts"]),
                "cell_category": r["cell_category"],
                "cell_lo": int(r["cell_price_lo"]) if r["cell_price_lo"] else 0,
                "cell_hi": int(r["cell_price_hi"]) if r["cell_price_hi"] else 0,
            }
    return facts

def load_kalshi_ticks(ticker, pregame_ts):
    """Load ticks, return (open_mid, close_mid) where close is at pregame_close."""
    path = os.path.join(TICKS_DIR, "%s.csv" % ticker)
    if not os.path.exists(path):
        return None, None
    mids = []
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 4:
                continue
            mids.append(float(row[3]))
    if not mids:
        return None, None
    return mids[0], mids[-1]  # first tick = open, last = close (at settlement)

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def get_historical_odds(sport_key, date_str):
    """Fetch historical odds snapshot. Returns list of matches with bookmaker odds."""
    url = "%s/historical/sports/%s/odds?apiKey=%s&regions=eu,uk&markets=h2h&date=%s" % (
        BASE, sport_key, KEY, date_str)
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            data = r.json()
            remaining = r.headers.get("x-requests-remaining", "?")
            return data.get("data", []), remaining
        return [], "?"
    except Exception as e:
        print("  API error: %s" % e)
        return [], "?"

def extract_pinnacle(match_data):
    """Extract Pinnacle odds from a match. Returns {player_name: fair_prob} or None."""
    for book in match_data.get("bookmakers", []):
        if book["key"] == "pinnacle":
            outcomes = book["markets"][0]["outcomes"]
            if len(outcomes) >= 2:
                odds1 = outcomes[0]["price"]
                odds2 = outcomes[1]["price"]
                p1, p2 = remove_vig(odds1, odds2)
                return {
                    outcomes[0]["name"]: round(p1 * 100, 1),
                    outcomes[1]["name"]: round(p2 * 100, 1),
                }
    # Fallback: betfair_ex_eu or betfair_ex_uk
    for bk in ["betfair_ex_eu", "betfair_ex_uk"]:
        for book in match_data.get("bookmakers", []):
            if book["key"] == bk:
                outcomes = book["markets"][0]["outcomes"]
                if len(outcomes) >= 2:
                    odds1 = outcomes[0]["price"]
                    odds2 = outcomes[1]["price"]
                    p1, p2 = remove_vig(odds1, odds2)
                    return {
                        outcomes[0]["name"]: round(p1 * 100, 1),
                        outcomes[1]["name"]: round(p2 * 100, 1),
                    }
    return None

def name_matches_code(full_name, code):
    """Check if 3-letter code matches start of any word in the full name (last name match)."""
    code_upper = code.upper()
    for word in full_name.upper().split():
        if word.startswith(code_upper):
            return True
    return False

# ============================================================
# Main
# ============================================================
print("Loading match facts...", flush=True)
facts = load_facts()
config = load_config()
print("  %d ATP_MAIN + WTA_MAIN tickers" % len(facts), flush=True)

# Group by event (pair both sides)
events = defaultdict(list)
for tk, f in facts.items():
    et = tk.rsplit("-", 1)[0]
    events[et].append((tk, f))

# Extract unique dates
dates = set()
for tk in facts:
    parts = tk.split("-")
    if len(parts) >= 2:
        date_part = parts[1][:7]  # 26MAR20
        try:
            yr = 2000 + int(date_part[:2])
            mon = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
                   "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}[date_part[2:5]]
            day = int(date_part[5:7])
            dates.add(datetime(yr, mon, day, tzinfo=timezone.utc))
        except:
            pass
print("  Date range: %s to %s (%d unique dates)" % (
    min(dates).strftime("%b %d"), max(dates).strftime("%b %d"), len(dates)), flush=True)

# Pull Pinnacle snapshots
# Strategy: for each date, pull 2 snapshots (early morning + late afternoon ET)
# to get "open" and "close" Pinnacle pricing
print("\nFetching Pinnacle historical data...", flush=True)

# Determine which sport keys to query per date
# We'll query all keys for each date — inefficient but ensures coverage
all_sport_keys = ATP_SPORT_KEYS + WTA_SPORT_KEYS

CACHE_PATH = "/root/Omi-Workspace/arb-executor/analysis/pinnacle_cache.json"
pinnacle_cache = {}
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH) as f:
        raw = json.load(f)
        for k, v in raw.items():
            pinnacle_cache[tuple(k.split("|"))] = v
    print("  Loaded %d cached API responses" % len(pinnacle_cache), flush=True)
quota_used = 0

for dt in sorted(dates):
    date_early = dt.strftime("%Y-%m-%dT06:00:00Z")  # 2 AM ET = early morning
    date_late = dt.strftime("%Y-%m-%dT20:00:00Z")   # 4 PM ET = late afternoon

    for sport_key in all_sport_keys:
        for label, ts in [("open", date_early), ("close", date_late)]:
            cache_key = (ts, sport_key)
            if cache_key in pinnacle_cache:
                continue
            matches, remaining = get_historical_odds(sport_key, ts)
            pinnacle_cache[cache_key] = matches
            quota_used += 1
            if matches:
                print("  %s %s @ %s: %d matches (remaining: %s)" % (
                    label, sport_key[:25], ts[:10], len(matches), remaining), flush=True)
            time.sleep(0.1)  # be gentle

    # Progress
    if quota_used % 20 == 0:
        print("  ... %d API calls so far" % quota_used, flush=True)

# Save cache
raw_cache = {"%s|%s" % k: v for k, v in pinnacle_cache.items()}
with open(CACHE_PATH, "w") as f:
    json.dump(raw_cache, f)
print("Total API calls: %d (quota cost: ~%d units)" % (quota_used, quota_used * 10), flush=True)
print("Cache saved: %d entries" % len(pinnacle_cache), flush=True)

# Match Pinnacle data to Kalshi tickers
print("\nMatching Pinnacle to Kalshi tickers...", flush=True)

results = []
matched = 0
unmatched = 0

for et, tickers_facts in events.items():
    for tk, f in tickers_facts:
        # Parse date
        parts = tk.split("-")
        date_part = parts[1][:7]
        try:
            yr = 2000 + int(date_part[:2])
            mon = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
                   "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}[date_part[2:5]]
            day = int(date_part[5:7])
            dt = datetime(yr, mon, day, tzinfo=timezone.utc)
        except:
            continue

        date_early = dt.strftime("%Y-%m-%dT06:00:00Z")
        date_late = dt.strftime("%Y-%m-%dT20:00:00Z")

        # Find Pinnacle odds for this player
        player_code = tk.split("-")[-1]
        pinnacle_open = None
        pinnacle_close = None

        cat_keys = ATP_SPORT_KEYS if f["category"] == "ATP_MAIN" else WTA_SPORT_KEYS

        for sport_key in cat_keys:
            # Open snapshot
            open_matches = pinnacle_cache.get((date_early, sport_key), [])
            for m in open_matches:
                pin = extract_pinnacle(m)
                if pin:
                    for name, prob in pin.items():
                        if name_matches_code(name, player_code):
                            pinnacle_open = prob
                            break

            # Close snapshot
            close_matches = pinnacle_cache.get((date_late, sport_key), [])
            for m in close_matches:
                pin = extract_pinnacle(m)
                if pin:
                    for name, prob in pin.items():
                        if name_matches_code(name, player_code):
                            pinnacle_close = prob
                            break

            if pinnacle_open is not None:
                break

        if pinnacle_open is None:
            unmatched += 1
            continue
        matched += 1

        # Kalshi ticks
        k_open, k_close = load_kalshi_ticks(tk, f["pregame_close_ts"])
        if k_open is None:
            continue

        # Cell exit cents
        cell_name = f["cell_category"]
        exit_cents = 0
        if cell_name != "no_cell":
            full_cell = "%s_%s_%d-%d" % (f["cell_category"], f["side"], f["cell_lo"], f["cell_hi"])
            cell_cfg = config["active_cells"].get(full_cell)
            if cell_cfg:
                exit_cents = cell_cfg["exit_cents"]

        results.append({
            "match_id": tk,
            "tour": f["category"],
            "side": f["side"],
            "pinnacle_open": pinnacle_open,
            "pinnacle_close": pinnacle_close if pinnacle_close else pinnacle_open,
            "kalshi_open": k_open,
            "kalshi_close": f["entry_mid"],
            "max_bounce": f["max_bounce"],
            "entry_mid": f["entry_mid"],
            "match_result": f["result"],
            "cell_exit_cents": exit_cents,
        })

print("Matched: %d, Unmatched: %d" % (matched, unmatched), flush=True)

# Save CSV
with open(OUT_PATH, "w", newline="") as f:
    if results:
        w = csv.DictWriter(f, fieldnames=results[0].keys())
        w.writeheader()
        w.writerows(results)
print("Saved: %s (%d rows)" % (OUT_PATH, len(results)), flush=True)

# ============================================================
# METRICS
# ============================================================
if not results:
    print("\nNo matched results to analyze.")
    exit()

def percentiles(vals):
    s = sorted(vals)
    n = len(s)
    return s[int(n*0.25)], s[int(n*0.5)], s[int(n*0.75)]

print("\n" + "=" * 70)
print("METRIC 1: Pinnacle stability (|close - open|)")
print("=" * 70)
pin_diffs = [abs(r["pinnacle_close"] - r["pinnacle_open"]) for r in results]
p25, p50, p75 = percentiles(pin_diffs)
print("  N=%d  p25=%.1fc  median=%.1fc  p75=%.1fc  mean=%.1fc" % (
    len(pin_diffs), p25, p50, p75, sum(pin_diffs)/len(pin_diffs)))

print("\n" + "=" * 70)
print("METRIC 2: Opening gap (|pinnacle_open - kalshi_open|)")
print("=" * 70)
gaps = [abs(r["pinnacle_open"] - r["kalshi_open"]) for r in results]
p25, p50, p75 = percentiles(gaps)
print("  N=%d  p25=%.1fc  median=%.1fc  p75=%.1fc  mean=%.1fc" % (
    len(gaps), p25, p50, p75, sum(gaps)/len(gaps)))

buckets = {"<2c": 0, "2-5c": 0, "5-10c": 0, ">10c": 0}
for g in gaps:
    if g < 2: buckets["<2c"] += 1
    elif g < 5: buckets["2-5c"] += 1
    elif g < 10: buckets["5-10c"] += 1
    else: buckets[">10c"] += 1
for b, n in buckets.items():
    print("  %5s: %d (%.0f%%)" % (b, n, 100*n/len(gaps)))

print("\n" + "=" * 70)
print("METRIC 3: Kalshi convergence toward Pinnacle open")
print("=" * 70)
big_gap = [(r["pinnacle_open"], r["kalshi_open"], r["kalshi_close"]) for r in results
           if abs(r["pinnacle_open"] - r["kalshi_open"]) > 5]
if big_gap:
    converged = 0
    gap_closed = []
    for pin, k_open, k_close in big_gap:
        initial_gap = pin - k_open
        final_gap = pin - k_close
        if abs(final_gap) < abs(initial_gap):
            converged += 1
            gap_closed.append(abs(initial_gap) - abs(final_gap))
    print("  Matches with gap > 5c: %d" % len(big_gap))
    print("  Kalshi moved toward Pinnacle: %d (%.0f%%)" % (converged, 100*converged/len(big_gap)))
    if gap_closed:
        print("  Mean gap closed: %.1fc" % (sum(gap_closed)/len(gap_closed)))
else:
    print("  No matches with gap > 5c")

print("\n" + "=" * 70)
print("METRIC 4: Conditional exit hit rate by gap bucket")
print("=" * 70)
bucket_hits = {"<2c": [0,0], "2-5c": [0,0], "5-10c": [0,0], ">10c": [0,0]}
for r in results:
    if r["cell_exit_cents"] <= 0:
        continue
    gap = abs(r["pinnacle_open"] - r["kalshi_open"])
    hit = 1 if r["max_bounce"] >= r["cell_exit_cents"] else 0
    if gap < 2: b = "<2c"
    elif gap < 5: b = "2-5c"
    elif gap < 10: b = "5-10c"
    else: b = ">10c"
    bucket_hits[b][0] += hit
    bucket_hits[b][1] += 1
for b in ["<2c", "2-5c", "5-10c", ">10c"]:
    h, n = bucket_hits[b]
    rate = 100*h/n if n > 0 else 0
    print("  %5s: %d/%d = %.0f%% hit rate" % (b, h, n, rate))

print("\n" + "=" * 70)
print("METRIC 5: Direction flips (Pinnacle vs Kalshi favorite disagree)")
print("=" * 70)
flips = []
for r in results:
    pin_fav = r["pinnacle_open"] > 50
    kal_fav = r["kalshi_open"] > 50
    if pin_fav != kal_fav:
        gap = abs(r["pinnacle_open"] - r["kalshi_open"])
        flips.append((r["match_id"], r["pinnacle_open"], r["kalshi_open"], gap, r["match_result"]))
print("  Direction flips: %d / %d (%.1f%%)" % (len(flips), len(results), 100*len(flips)/len(results)))
for tk, pin, kal, gap, result in sorted(flips, key=lambda x: -x[3])[:10]:
    print("  %-45s pin=%.0fc kal=%.0fc gap=%.0fc result=%s" % (tk[:45], pin, kal, gap, result))

print("\n" + "=" * 70)
print("METRIC 6: Breakdown by tour")
print("=" * 70)
for tour in ["ATP_MAIN", "WTA_MAIN"]:
    subset = [r for r in results if r["tour"] == tour]
    if not subset:
        continue
    gaps_t = [abs(r["pinnacle_open"] - r["kalshi_open"]) for r in subset]
    pin_diffs_t = [abs(r["pinnacle_close"] - r["pinnacle_open"]) for r in subset]
    p25g, p50g, p75g = percentiles(gaps_t) if gaps_t else (0,0,0)
    p25p, p50p, p75p = percentiles(pin_diffs_t) if pin_diffs_t else (0,0,0)

    print("\n  %s (N=%d):" % (tour, len(subset)))
    print("    Pinnacle stability: p25=%.1fc median=%.1fc p75=%.1fc" % (p25p, p50p, p75p))
    print("    Opening gap:        p25=%.1fc median=%.1fc p75=%.1fc" % (p25g, p50g, p75g))

    # Hit rate by gap
    bh = {"<2c": [0,0], "2-5c": [0,0], "5-10c": [0,0], ">10c": [0,0]}
    for r in subset:
        if r["cell_exit_cents"] <= 0:
            continue
        gap = abs(r["pinnacle_open"] - r["kalshi_open"])
        hit = 1 if r["max_bounce"] >= r["cell_exit_cents"] else 0
        if gap < 2: b = "<2c"
        elif gap < 5: b = "2-5c"
        elif gap < 10: b = "5-10c"
        else: b = ">10c"
        bh[b][0] += hit
        bh[b][1] += 1
    print("    Hit rate by gap:")
    for b in ["<2c", "2-5c", "5-10c", ">10c"]:
        h, n = bh[b]
        rate = 100*h/n if n > 0 else 0
        print("      %5s: %d/%d = %.0f%%" % (b, h, n, rate))

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
