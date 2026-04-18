#!/usr/bin/env python3
"""Deep analysis of Pinnacle vs Kalshi using cached data. 0 API calls."""
import csv, json, os, math
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ANALYSIS = "/root/Omi-Workspace/arb-executor/analysis"
CACHE_PATH = os.path.join(ANALYSIS, "pinnacle_cache.json")
CSV_PATH = os.path.join(ANALYSIS, "pinnacle_kalshi_timing.csv")
FACTS_PATH = os.path.join(ANALYSIS, "match_facts.csv")
CONFIG_PATH = "/root/Omi-Workspace/arb-executor/config/deploy_v3.json"
TICKS_DIR = os.path.join(ANALYSIS, "match_ticks_full")

config = json.load(open(CONFIG_PATH))

# Load the 126 matched results
results = []
with open(CSV_PATH) as f:
    for r in csv.DictReader(f):
        for k in ["pinnacle_open","pinnacle_close","kalshi_open","kalshi_close",
                   "max_bounce","entry_mid","cell_exit_cents"]:
            r[k] = float(r[k])
        results.append(r)
print("Loaded %d matched results" % len(results))

# Load full facts for the disabled-cell analysis
facts = {}
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        if r["category"] in ("ATP_MAIN", "WTA_MAIN"):
            facts[r["ticker_id"]] = r

# Load cache for multi-book analysis
with open(CACHE_PATH) as f:
    raw = json.load(f)
cache = {}
for k, v in raw.items():
    cache[tuple(k.split("|"))] = v

def get_cell(cat, mid):
    direction = "leader" if mid > 50 else "underdog"
    bucket = int(mid / 5) * 5
    name = "%s_%s_%d-%d" % (cat, direction, bucket, bucket + 4)
    cfg = config["active_cells"].get(name)
    return name, cfg

def remove_vig(odds1, odds2):
    p1 = 1.0 / odds1
    p2 = 1.0 / odds2
    total = p1 + p2
    return p1 / total, p2 / total

def name_matches_code(full_name, code):
    for word in full_name.upper().split():
        if word.startswith(code.upper()):
            return True
    return False

# ============================================================
print("\n" + "=" * 80)
print("STEP 1: KALSHI → PINNACLE DRIFT MAP")
print("=" * 80)

# Build mapping table
drift_table = defaultdict(lambda: {"n": 0, "k_hits": 0, "p_hits": 0, "k_eligible": 0, "p_eligible": 0})

for r in results:
    k_bucket = int(r["kalshi_open"] / 5) * 5
    p_bucket = int(r["pinnacle_open"] / 5) * 5
    gap = r["kalshi_open"] - r["pinnacle_open"]
    cat = r["tour"]
    direction = r["side"]

    k_cell, k_cfg = get_cell(cat, r["kalshi_open"])
    p_cell, p_cfg = get_cell(cat, r["pinnacle_open"])

    k_exit = k_cfg["exit_cents"] if k_cfg else 0
    p_exit = p_cfg["exit_cents"] if p_cfg else 0

    k_hit = r["max_bounce"] >= k_exit if k_exit > 0 else False
    p_hit = r["max_bounce"] >= p_exit if p_exit > 0 else False

    key = (cat, direction, k_bucket, p_bucket)
    d = drift_table[key]
    d["n"] += 1
    if k_exit > 0:
        d["k_eligible"] += 1
        if k_hit: d["k_hits"] += 1
    if p_exit > 0:
        d["p_eligible"] += 1
        if p_hit: d["p_hits"] += 1

print("\n%-12s %-9s %-8s %-8s %4s  %-15s %-15s %s" % (
    "TOUR", "SIDE", "K_BKTC", "P_BKTC", "N", "K_HIT_RATE", "P_HIT_RATE", "BETTER"))
for key in sorted(drift_table.keys()):
    cat, direction, k_b, p_b = key
    d = drift_table[key]
    k_rate = 100 * d["k_hits"] / d["k_eligible"] if d["k_eligible"] > 0 else -1
    p_rate = 100 * d["p_hits"] / d["p_eligible"] if d["p_eligible"] > 0 else -1
    k_str = "%d/%d=%d%%" % (d["k_hits"], d["k_eligible"], k_rate) if d["k_eligible"] > 0 else "n/a"
    p_str = "%d/%d=%d%%" % (d["p_hits"], d["p_eligible"], p_rate) if d["p_eligible"] > 0 else "n/a"
    better = ""
    if k_rate >= 0 and p_rate >= 0:
        better = "PINNACLE" if p_rate > k_rate else ("KALSHI" if k_rate > p_rate else "TIE")
    print("%-12s %-9s %-8s %-8s %4d  %-15s %-15s %s" % (
        cat, direction, "%d-%dc" % (k_b, k_b+4), "%d-%dc" % (p_b, p_b+4),
        d["n"], k_str, p_str, better))

# Aggregate
k_total_hits = sum(d["k_hits"] for d in drift_table.values())
k_total_elig = sum(d["k_eligible"] for d in drift_table.values())
p_total_hits = sum(d["p_hits"] for d in drift_table.values())
p_total_elig = sum(d["p_eligible"] for d in drift_table.values())
print("\nAggregate:")
print("  Kalshi-cell exits:   %d/%d = %.0f%%" % (k_total_hits, k_total_elig, 100*k_total_hits/k_total_elig if k_total_elig else 0))
print("  Pinnacle-cell exits: %d/%d = %.0f%%" % (p_total_hits, p_total_elig, 100*p_total_hits/p_total_elig if p_total_elig else 0))

# ============================================================
print("\n" + "=" * 80)
print("STEP 2: SALVAGE ANALYSIS FOR DISABLED CELLS")
print("=" * 80)

disabled = [
    "ATP_MAIN_leader_65-69",
    "WTA_MAIN_leader_55-59",
    "WTA_MAIN_leader_60-64",
    "WTA_MAIN_leader_65-69",
    "WTA_MAIN_leader_80-84",
]

for dc in disabled:
    matches = [r for r in results if get_cell(r["tour"], r["kalshi_open"])[0] == dc]
    if not matches:
        print("\n  %s: 0 matches in sample" % dc)
        continue
    print("\n  %s: %d matches" % (dc, len(matches)))
    salvage = 0
    for r in matches:
        p_cell, p_cfg = get_cell(r["tour"], r["pinnacle_open"])
        p_exit = p_cfg["exit_cents"] if p_cfg else 0
        p_hit = r["max_bounce"] >= p_exit if p_exit > 0 else False
        pin_bucket = int(r["pinnacle_open"] / 5) * 5
        print("    %s  kalshi=%.0fc pin=%.0fc pin_cell=%s pin_exit=%dc bounce=%.0fc %s" % (
            r["match_id"][:40], r["kalshi_open"], r["pinnacle_open"],
            p_cell, p_exit, r["max_bounce"],
            "HIT" if p_hit else "miss"))
        if p_hit:
            salvage += 1
    print("  Salvage rate: %d/%d = %.0f%%" % (salvage, len(matches), 100*salvage/len(matches)))

# ============================================================
print("\n" + "=" * 80)
print("STEP 3: MULTI-BOOK COMPARISON")
print("=" * 80)

# Parse all cached responses to get per-book implied probabilities
# Then match to our 126 tickers
book_predictions = defaultdict(list)  # book_key -> [(predicted_cents, kalshi_close)]

for r in results:
    tk = r["match_id"]
    player_code = tk.split("-")[-1]
    parts = tk.split("-")
    date_part = parts[1][:7]
    try:
        yr = 2000 + int(date_part[:2])
        mon = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
               "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}[date_part[2:5]]
        day = int(date_part[5:7])
        dt_str = "%04d-%02d-%02dT06:00:00Z" % (yr, mon, day)
    except:
        continue

    cat = r["tour"]
    sport_keys = ["tennis_atp_miami_open", "tennis_atp_monte_carlo_masters",
                  "tennis_atp_barcelona_open", "tennis_atp_munich",
                  "tennis_atp_indian_wells", "tennis_atp_dubai"] if cat == "ATP_MAIN" else \
                 ["tennis_wta_miami_open", "tennis_wta_charleston_open",
                  "tennis_wta_indian_wells", "tennis_wta_dubai", "tennis_wta_stuttgart_open"]

    for sk in sport_keys:
        matches = cache.get((dt_str, sk), [])
        for m in matches:
            for book in m.get("bookmakers", []):
                outcomes = book.get("markets", [{}])[0].get("outcomes", [])
                if len(outcomes) < 2:
                    continue
                # Find our player
                for o in outcomes:
                    if name_matches_code(o["name"], player_code):
                        other = [x for x in outcomes if x != o]
                        if other:
                            p_fair, _ = remove_vig(o["price"], other[0]["price"])
                            implied_cents = round(p_fair * 100, 1)
                            book_predictions[book["key"]].append((implied_cents, r["kalshi_close"]))
                        break

print("\n%-25s %5s %8s %8s %8s" % ("BOOK", "N", "MAE", "CORR", "BEAT_K%"))
# Also compute kalshi_open MAE for baseline
k_mae_vals = [(abs(r["kalshi_open"] - r["kalshi_close"]), r["kalshi_open"], r["kalshi_close"]) for r in results]
k_mae = sum(v[0] for v in k_mae_vals) / len(k_mae_vals) if k_mae_vals else 0

book_stats = []
for bk, pairs in sorted(book_predictions.items(), key=lambda x: -len(x[1])):
    if len(pairs) < 10:
        continue
    mae = sum(abs(p - k) for p, k in pairs) / len(pairs)
    # Correlation
    n = len(pairs)
    mean_p = sum(p for p, k in pairs) / n
    mean_k = sum(k for p, k in pairs) / n
    cov = sum((p - mean_p) * (k - mean_k) for p, k in pairs) / n
    std_p = math.sqrt(sum((p - mean_p)**2 for p, k in pairs) / n) or 1
    std_k = math.sqrt(sum((k - mean_k)**2 for p, k in pairs) / n) or 1
    corr = cov / (std_p * std_k)
    # Beat kalshi_open baseline
    beat = 0
    for i, (pred, actual) in enumerate(pairs):
        if i < len(results):
            k_open = results[i]["kalshi_open"]
            if abs(pred - actual) < abs(k_open - actual):
                beat += 1
    beat_pct = 100 * beat / len(pairs)
    book_stats.append((bk, len(pairs), mae, corr, beat_pct))
    print("%-25s %5d %8.1fc %8.3f %7.0f%%" % (bk, len(pairs), mae, corr, beat_pct))

print("\nBaseline: Kalshi open MAE = %.1fc" % k_mae)
print("(Beat%%: how often book open predicts kalshi close better than kalshi open)")

# ============================================================
print("\n" + "=" * 80)
print("STEP 4: DIRECTION FLIP CASES")
print("=" * 80)

flips = []
for r in results:
    pin_fav = r["pinnacle_open"] > 50
    kal_fav = r["kalshi_open"] > 50
    if pin_fav != kal_fav:
        # Get both sides
        et = r["match_id"].rsplit("-", 1)[0]
        other_tk = None
        for r2 in results:
            if r2["match_id"].rsplit("-", 1)[0] == et and r2["match_id"] != r["match_id"]:
                other_tk = r2
                break
        flips.append((r, other_tk))

# Deduplicate by event
seen_events = set()
unique_flips = []
for r, other in flips:
    et = r["match_id"].rsplit("-", 1)[0]
    if et in seen_events:
        continue
    seen_events.add(et)
    unique_flips.append((r, other))

print("\nDirection flips: %d unique events" % len(unique_flips))
print()
for r, other in sorted(unique_flips, key=lambda x: -abs(x[0]["pinnacle_open"] - x[0]["kalshi_open"])):
    gap = abs(r["pinnacle_open"] - r["kalshi_open"])
    et = r["match_id"].rsplit("-", 1)[0]
    # Parse tournament from ticker
    date_part = et.split("-")[1][:7]
    player1 = r["match_id"].split("-")[-1]
    player2 = other["match_id"].split("-")[-1] if other else "?"

    pin_suspicious = gap > 40
    flag = " *** LIKELY DATA ISSUE ***" if pin_suspicious else ""

    print("  %s  %s vs %s%s" % (et[:40], player1, player2, flag))
    print("    Pinnacle: %s=%.0fc %s=%.0fc" % (player1, r["pinnacle_open"],
          player2, other["pinnacle_open"] if other else 0))
    print("    Kalshi:   %s=%.0fc %s=%.0fc" % (player1, r["kalshi_open"],
          player2, other["kalshi_open"] if other else 0))
    print("    Gap: %.0fc  Outcome: %s=%s  Bounce: %.0fc" % (
        gap, player1, r["match_result"], r["max_bounce"]))
    if gap <= 20:
        print("    >>> GENUINE MISPRICING CANDIDATE")
    print()

# ============================================================
# Step 5: Save cache in structured format
print("=" * 80)
print("STEP 5: CACHE STATUS")
print("=" * 80)
cache_dir = os.path.join(ANALYSIS, "odds_api_cache")
os.makedirs(cache_dir, exist_ok=True)

# Save per-date-sport files
saved = 0
for (ts, sport), matches in cache.items():
    if not matches:
        continue
    date_str = ts[:10]
    fname = "%s_%s.json" % (date_str, sport)
    fpath = os.path.join(cache_dir, fname)
    if not os.path.exists(fpath):
        with open(fpath, "w") as f:
            json.dump({"date": ts, "sport": sport, "matches": matches}, f)
        saved += 1

print("Cache entries: %d" % len(cache))
print("New files saved to %s: %d" % (cache_dir, saved))
print("Reloadable without API calls: YES")
print("\nDONE")
