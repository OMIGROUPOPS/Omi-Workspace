#!/usr/bin/env python3
"""Reframed parionssport analysis: cell assignment, MAE subsets, bias, live test."""
import csv, json, os, math, requests
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ANALYSIS = "/root/Omi-Workspace/arb-executor/analysis"
CACHE_PATH = os.path.join(ANALYSIS, "pinnacle_cache.json")
FACTS_PATH = os.path.join(ANALYSIS, "match_facts.csv")
CONFIG_PATH = "/root/Omi-Workspace/arb-executor/config/deploy_v3.json"
ODDS_KEY = "936fff28812c240d8bb6c96a63387295"

config = json.load(open(CONFIG_PATH))

with open(CACHE_PATH) as f:
    raw = json.load(f)
cache = {}
for k, v in raw.items():
    cache[tuple(k.split("|"))] = v

facts = {}
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        if r["category"] in ("ATP_MAIN", "WTA_MAIN"):
            facts[r["ticker_id"]] = r

def remove_vig(o1, o2):
    p1 = 1.0/o1; p2 = 1.0/o2
    t = p1+p2
    return p1/t, p2/t

def name_matches_code(full_name, code):
    for w in full_name.upper().split():
        if w.startswith(code.upper()):
            return True
    return False

def get_cell(cat, mid):
    direction = "leader" if mid > 50 else "underdog"
    bucket = int(mid / 5) * 5
    name = "%s_%s_%d-%d" % (cat, direction, bucket, bucket + 4)
    cfg = config["active_cells"].get(name)
    disabled = name in config["disabled_cells"]
    return name, cfg, disabled

def extract_ps_signals():
    signals = []
    for tk, f in facts.items():
        player_code = tk.split("-")[-1]
        parts = tk.split("-")
        date_part = parts[1][:7]
        try:
            yr = 2000 + int(date_part[:2])
            mon = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
                   "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}[date_part[2:5]]
            day = int(date_part[5:7])
            dt_early = "%04d-%02d-%02dT06:00:00Z" % (yr, mon, day)
        except:
            continue
        cat = f["category"]
        skeys = ["tennis_atp_miami_open","tennis_atp_monte_carlo_masters",
                 "tennis_atp_barcelona_open","tennis_atp_munich",
                 "tennis_atp_indian_wells","tennis_atp_dubai"] if cat == "ATP_MAIN" else \
                ["tennis_wta_miami_open","tennis_wta_charleston_open",
                 "tennis_wta_indian_wells","tennis_wta_dubai","tennis_wta_stuttgart_open"]
        ps_implied = None
        for sk in skeys:
            matches = cache.get((dt_early, sk), [])
            for m in matches:
                for book in m.get("bookmakers", []):
                    if book["key"] != "parionssport_fr":
                        continue
                    outcomes = book.get("markets", [{}])[0].get("outcomes", [])
                    if len(outcomes) < 2:
                        continue
                    for o in outcomes:
                        if name_matches_code(o["name"], player_code):
                            other = [x for x in outcomes if x != o]
                            if other:
                                p, _ = remove_vig(o["price"], other[0]["price"])
                                ps_implied = round(p * 100, 1)
                            break
            if ps_implied is not None:
                break
        if ps_implied is None:
            continue
        kalshi_close = float(f["entry_mid"])
        max_bounce = float(f["max_bounce_from_entry"])
        signals.append({
            "ticker": tk, "category": cat, "side": f["side"],
            "kalshi_close": kalshi_close, "ps_implied": ps_implied,
            "max_bounce": max_bounce, "result": f["match_result"],
        })
    return signals

signals = extract_ps_signals()
print("Parionssport-matched signals: %d" % len(signals))

# ============================================================
print("\n" + "=" * 80)
print("TASK A: CELL-ASSIGNMENT COMPARISON")
print("=" * 80)

salvaged = []
tighter_hit = []
wider_miss = []
both_hit = 0
both_miss = 0
k_only_hit = 0
ps_only_hit = 0
k_eligible = 0
ps_eligible = 0

print("\n%-40s %-22s %-22s %-5s %-5s %s" % (
    "TICKER", "KALSHI_CELL", "PS_CELL", "K_HIT", "P_HIT", "NOTE"))

for s in signals:
    cat = s["category"]
    k_cell, k_cfg, k_disabled = get_cell(cat, s["kalshi_close"])
    p_cell, p_cfg, p_disabled = get_cell(cat, s["ps_implied"])

    k_exit = k_cfg["exit_cents"] if k_cfg else 0
    p_exit = p_cfg["exit_cents"] if p_cfg else 0

    k_hit = s["max_bounce"] >= k_exit if k_exit > 0 else None
    p_hit = s["max_bounce"] >= p_exit if p_exit > 0 else None

    note = ""
    if k_cell != p_cell:
        if k_disabled and p_cfg:
            note = "SALVAGE (K disabled, PS active)"
            salvaged.append(s)
        elif p_exit > 0 and k_exit > 0:
            if p_exit < k_exit and p_hit and not k_hit:
                note = "PS tighter, hit when K missed"
                tighter_hit.append(s)
            elif p_exit > k_exit and not p_hit and k_hit:
                note = "PS wider, missed when K hit"
                wider_miss.append(s)

    if k_exit > 0:
        k_eligible += 1
    if p_exit > 0:
        ps_eligible += 1
    if k_hit and p_hit:
        both_hit += 1
    elif not k_hit and not p_hit and k_exit > 0 and p_exit > 0:
        both_miss += 1
    elif k_hit and not p_hit:
        k_only_hit += 1
    elif p_hit and not k_hit:
        ps_only_hit += 1

    if note or k_cell != p_cell:
        k_hit_str = "HIT" if k_hit else ("miss" if k_hit is not None else "n/a")
        p_hit_str = "HIT" if p_hit else ("miss" if p_hit is not None else "n/a")
        print("%-40s %-22s %-22s %-5s %-5s %s" % (
            s["ticker"][:40], k_cell[:22], p_cell[:22], k_hit_str, p_hit_str, note))

print("\nSummary:")
print("  Same cell assignment: %d / %d" % (
    sum(1 for s in signals if get_cell(s["category"], s["kalshi_close"])[0] ==
        get_cell(s["category"], s["ps_implied"])[0]), len(signals)))
print("  Different cell: %d" % (len(signals) - sum(1 for s in signals
    if get_cell(s["category"], s["kalshi_close"])[0] == get_cell(s["category"], s["ps_implied"])[0])))
print()
print("  Kalshi-cell eligible: %d, hit: %d (%.0f%%)" % (
    k_eligible, both_hit + k_only_hit,
    100*(both_hit+k_only_hit)/k_eligible if k_eligible else 0))
print("  PS-cell eligible: %d, hit: %d (%.0f%%)" % (
    ps_eligible, both_hit + ps_only_hit,
    100*(both_hit+ps_only_hit)/ps_eligible if ps_eligible else 0))
print()
print("  Salvaged (K disabled, PS active): %d" % len(salvaged))
for s in salvaged:
    p_cell, p_cfg, _ = get_cell(s["category"], s["ps_implied"])
    p_exit = p_cfg["exit_cents"] if p_cfg else 0
    p_hit = s["max_bounce"] >= p_exit if p_exit > 0 else False
    print("    %s  ps_cell=%s  exit=%dc  bounce=%.0fc  %s" % (
        s["ticker"][:40], p_cell, p_exit, s["max_bounce"], "HIT" if p_hit else "miss"))
print("  PS tighter, hit when K missed: %d" % len(tighter_hit))
print("  PS wider, missed when K hit: %d" % len(wider_miss))

# ============================================================
print("\n" + "=" * 80)
print("TASK B: MAE STABILITY SUBSETS")
print("=" * 80)

def compute_mae(subset):
    if not subset:
        return 0, 0
    errs = [abs(s["ps_implied"] - s["kalshi_close"]) for s in subset]
    return sum(errs)/len(errs), len(errs)

# By tour
for tour in ["ATP_MAIN", "WTA_MAIN"]:
    sub = [s for s in signals if s["category"] == tour]
    mae, n = compute_mae(sub)
    print("  %-12s N=%3d  MAE=%.1fc" % (tour, n, mae))

# By price range
print()
for label, lo, hi in [("favorite >60c", 60, 100), ("mid 40-60c", 40, 60), ("underdog <40c", 0, 40)]:
    sub = [s for s in signals if lo <= s["kalshi_close"] < hi]
    mae, n = compute_mae(sub)
    print("  %-18s N=%3d  MAE=%.1fc" % (label, n, mae))

# By gap size
print()
for label, lo, hi in [("gap <3c (agree)", 0, 3), ("gap 3-5c", 3, 5), ("gap >5c (disagree)", 5, 100)]:
    sub = [s for s in signals if lo <= abs(s["ps_implied"] - s["kalshi_close"]) < hi]
    mae, n = compute_mae(sub)
    print("  %-22s N=%3d  MAE=%.1fc" % (label, n, mae))

# Best subset
print("\nBest subsets (MAE < 4c):")
for tour in ["ATP_MAIN", "WTA_MAIN"]:
    for label, lo, hi in [("fav>60", 60, 100), ("mid40-60", 40, 60), ("dog<40", 0, 40)]:
        sub = [s for s in signals if s["category"] == tour and lo <= s["kalshi_close"] < hi]
        if sub:
            mae, n = compute_mae(sub)
            if mae < 4:
                print("  %s + %s: N=%d MAE=%.1fc ***" % (tour, label, n, mae))

# ============================================================
print("\n" + "=" * 80)
print("TASK C: BIAS CHECK")
print("=" * 80)

signed = [s["ps_implied"] - s["kalshi_close"] for s in signals]
print("\nSigned error (ps - kalshi), all %d:" % len(signed))
print("  Mean: %+.1fc  Median: %+.1fc" % (
    sum(signed)/len(signed), sorted(signed)[len(signed)//2]))

for side in ["leader", "underdog"]:
    sub = [s["ps_implied"] - s["kalshi_close"] for s in signals if s["side"] == side]
    if sub:
        print("  %s (N=%d): Mean=%+.1fc  Median=%+.1fc" % (
            side, len(sub), sum(sub)/len(sub), sorted(sub)[len(sub)//2]))

# By tour + side
for tour in ["ATP_MAIN", "WTA_MAIN"]:
    for side in ["leader", "underdog"]:
        sub = [s["ps_implied"] - s["kalshi_close"] for s in signals
               if s["category"] == tour and s["side"] == side]
        if sub:
            print("  %s %s (N=%d): Mean=%+.1fc" % (tour, side, len(sub), sum(sub)/len(sub)))

# ============================================================
print("\n" + "=" * 80)
print("TASK D: LIVE API TEST")
print("=" * 80)

url = "https://api.the-odds-api.com/v4/sports/tennis_atp_barcelona_open/odds"
params = {"apiKey": ODDS_KEY, "regions": "eu", "bookmakers": "parionssport_fr", "markets": "h2h"}
r = requests.get(url, params=params, timeout=15)
print("\nStatus: %d" % r.status_code)
print("Quota used: %s  Remaining: %s" % (
    r.headers.get("x-requests-used","?"), r.headers.get("x-requests-remaining","?")))

data = r.json()
print("Matches returned: %d" % len(data))
for m in data:
    home = m.get("home_team", "?")
    away = m.get("away_team", "?")
    commence = m.get("commence_time", "?")[:19]
    for book in m.get("bookmakers", []):
        if book["key"] == "parionssport_fr":
            last_update = book.get("last_update", "?")[:19]
            outcomes = book["markets"][0]["outcomes"]
            odds = [(o["name"], o["price"]) for o in outcomes]
            p1, p2 = remove_vig(outcomes[0]["price"], outcomes[1]["price"])
            print("  %s vs %s  commence=%s" % (home, away, commence))
            print("    parionssport: %s  updated=%s" % (odds, last_update))
            print("    implied: %.0fc / %.0fc (vig-removed)" % (p1*100, p2*100))

# ============================================================
print("\n" + "=" * 80)
print("TASK E: PREMARKET COLLECTION STATUS")
print("=" * 80)
print()
print("Forward premarket tick collection started Apr 17 2026 at 06:41 PM ET.")
print("Full premarket paths available for matches discovered Apr 18 2026 onward.")
print("Previously-open markets missed 1-10 hours of premarket ticks.")
print()
print("After 30 days (~May 17 2026), we will have:")
print("  - ~500+ ticker premarket paths (ATP Main + WTA Main + ATP Chall)")
print("  - Full market-open to pregame-close BBO history")
print("  - Basis for proper premarket drift + convergence testing")
print()
print("Until then: no action on the parionssport drift thesis.")
print("The cell-assignment and MAE findings above are still valid")
print("because they use pregame-close data which we have.")

print("\nDONE")
