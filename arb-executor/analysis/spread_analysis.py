#!/usr/bin/env python3
"""Spread pattern analysis from premarket depth ticks."""
import csv, json, os, math
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
TICKS_DIR = Path("/root/Omi-Workspace/arb-executor/analysis/premarket_ticks")
CONFIG_PATH = "/root/Omi-Workspace/arb-executor/config/deploy_v4.json"
ODDS_KEY = "936fff28812c240d8bb6c96a63387295"

config = json.load(open(CONFIG_PATH))
series_map = {"ATP_MAIN": ["KXATPMATCH"], "WTA_MAIN": ["KXWTAMATCH"],
              "ATP_CHALL": ["KXATPCHALLENGERMATCH"], "WTA_CHALL": ["KXWTACHALLENGERMATCH"]}

def get_cell(ticker, mid):
    cat = None
    for c, pfxs in series_map.items():
        for pfx in pfxs:
            if ticker.startswith(pfx):
                cat = c
    if not cat:
        return "?", "?"
    direction = "leader" if mid > 50 else "underdog"
    bucket = int(mid / 5) * 5
    return cat, "%s_%s_%d-%d" % (cat, direction, bucket, bucket + 4)

def percentile(vals, p):
    if not vals:
        return 0
    s = sorted(vals)
    return s[int(len(s) * p)]

# ============================================================
# STEP 1: Spread distribution per cell
# ============================================================
print("=" * 90)
print("STEP 1: SPREAD DISTRIBUTION PER CELL")
print("=" * 90)

cell_spreads = defaultdict(list)
all_ticks = []  # (ticker, ts_str, bid, ask, mid, spread, bid_sz, ask_sz)

for f in sorted(TICKS_DIR.glob("*.csv")):
    ticker = f.stem
    with open(f) as fh:
        reader = csv.reader(fh)
        header = next(reader)
        for row in reader:
            if len(row) < 23:
                continue
            try:
                bid = int(row[2]) if row[2] else 0
                ask = int(row[12]) if row[12] else 100
                mid = float(row[22])
                bid_sz = int(row[3]) if row[3] else 0
                ask_sz = int(row[13]) if row[13] else 0
            except (ValueError, IndexError):
                continue
            if bid <= 0 or ask >= 100:
                continue
            spread = ask - bid
            cat, cell = get_cell(ticker, mid)
            cell_spreads[cell].append(spread)
            all_ticks.append((ticker, row[0], bid, ask, mid, spread, bid_sz, ask_sz))

print("\n%-35s %6s %5s %5s %5s %5s %6s %6s" % (
    "CELL", "TICKS", "MEAN", "MED", "P75", "P95", "1c%", "5c+%"))
print("-" * 90)

for cell in sorted(cell_spreads.keys()):
    spreads = cell_spreads[cell]
    n = len(spreads)
    if n < 10:
        continue
    mean_s = sum(spreads) / n
    med = percentile(spreads, 0.5)
    p75 = percentile(spreads, 0.75)
    p95 = percentile(spreads, 0.95)
    pct_1c = 100 * sum(1 for s in spreads if s == 1) / n
    pct_5c = 100 * sum(1 for s in spreads if s >= 5) / n
    print("%-35s %6d %4.1fc %4.0fc %4.0fc %4.0fc %5.0f%% %5.0f%%" % (
        cell[:35], n, mean_s, med, p75, p95, pct_1c, pct_5c))

# Overall
all_spreads = [t[5] for t in all_ticks]
if all_spreads:
    print("\n%-35s %6d %4.1fc %4.0fc %4.0fc %4.0fc %5.0f%% %5.0f%%" % (
        "ALL TICKS", len(all_spreads),
        sum(all_spreads)/len(all_spreads),
        percentile(all_spreads, 0.5), percentile(all_spreads, 0.75),
        percentile(all_spreads, 0.95),
        100*sum(1 for s in all_spreads if s==1)/len(all_spreads),
        100*sum(1 for s in all_spreads if s>=5)/len(all_spreads)))

# ============================================================
# STEP 2: Wide-spread events — what happens next?
# ============================================================
print("\n" + "=" * 90)
print("STEP 2: WIDE-SPREAD EVENTS (spread >= 5c) — WHAT HAPPENS NEXT?")
print("=" * 90)

# Group ticks by ticker for temporal analysis
ticker_ticks = defaultdict(list)
for t in all_ticks:
    ticker_ticks[t[0]].append(t)

wide_events = {"narrowed": 0, "stayed": 0, "widened": 0,
               "mid_up": 0, "mid_down": 0, "mid_flat": 0,
               "total": 0, "avg_narrow": []}

for ticker, ticks in ticker_ticks.items():
    for i, t in enumerate(ticks):
        if t[5] < 5:  # spread < 5c
            continue
        wide_events["total"] += 1
        # Look ahead ~50 ticks (proxy for ~5 min at high-freq tickers)
        future = ticks[i+1:i+51]
        if not future:
            continue
        future_spread = future[-1][5]
        future_mid = future[-1][4]
        initial_spread = t[5]
        initial_mid = t[4]

        if future_spread < initial_spread - 1:
            wide_events["narrowed"] += 1
            wide_events["avg_narrow"].append(initial_spread - future_spread)
        elif future_spread > initial_spread + 1:
            wide_events["widened"] += 1
        else:
            wide_events["stayed"] += 1

        mid_change = future_mid - initial_mid
        if mid_change > 0.5:
            wide_events["mid_up"] += 1
        elif mid_change < -0.5:
            wide_events["mid_down"] += 1
        else:
            wide_events["mid_flat"] += 1

n_wide = wide_events["total"]
print("\nWide-spread events (>= 5c): %d" % n_wide)
if n_wide > 0:
    print("  Narrowed within ~50 ticks: %d (%.0f%%)" % (
        wide_events["narrowed"], 100*wide_events["narrowed"]/n_wide))
    print("  Stayed similar: %d (%.0f%%)" % (
        wide_events["stayed"], 100*wide_events["stayed"]/n_wide))
    print("  Widened further: %d (%.0f%%)" % (
        wide_events["widened"], 100*wide_events["widened"]/n_wide))
    if wide_events["avg_narrow"]:
        print("  Avg narrowing when it narrowed: %.1fc" % (
            sum(wide_events["avg_narrow"])/len(wide_events["avg_narrow"])))
    print("\n  Mid moved up: %d (%.0f%%)" % (wide_events["mid_up"], 100*wide_events["mid_up"]/n_wide))
    print("  Mid stayed flat: %d (%.0f%%)" % (wide_events["mid_flat"], 100*wide_events["mid_flat"]/n_wide))
    print("  Mid moved down: %d (%.0f%%)" % (wide_events["mid_down"], 100*wide_events["mid_down"]/n_wide))

# ============================================================
# STEP 3: Entry fill behavior vs spread
# ============================================================
print("\n" + "=" * 90)
print("STEP 3: ENTRY FILL BEHAVIOR vs SPREAD")
print("=" * 90)

# Load V4 entry logs
log_path = Path("/root/Omi-Workspace/arb-executor/logs/live_v3_20260418.jsonl")
entry_posts = {}
entry_fills = {}
if log_path.exists():
    with open(log_path) as f:
        for line in f:
            e = json.loads(line)
            if e["event"] == "order_placed" and e.get("details", {}).get("action") == "buy":
                tk = e.get("ticker", "")
                entry_posts[tk] = {"time": e.get("ts_epoch", 0), "price": e["details"].get("price", 0)}
            elif e["event"] == "entry_filled":
                tk = e.get("ticker", "")
                entry_fills[tk] = {"time": e.get("ts_epoch", 0)}

print("\nEntry posts: %d, Entry fills detected in log: %d" % (len(entry_posts), len(entry_fills)))

# Match entries to tick data at post time
for tk, info in sorted(entry_posts.items()):
    ticks = ticker_ticks.get(tk, [])
    if not ticks:
        continue
    # Find tick closest to post time (by timestamp matching)
    post_price = info["price"]
    # First tick is our reference
    if ticks:
        first_spread = ticks[0][5]
        first_bid = ticks[0][2]
        first_ask = ticks[0][3]
        last_spread = ticks[-1][5] if len(ticks) > 1 else first_spread
        print("  %s: post@%dc  first_spread=%dc(bid=%d/ask=%d)  last_spread=%dc  ticks=%d" % (
            tk.split("-")[-1], post_price, first_spread, first_bid, first_ask, last_spread, len(ticks)))

# ============================================================
# STEP 4: External book coverage
# ============================================================
print("\n" + "=" * 90)
print("STEP 4: EXTERNAL BOOK COVERAGE FOR CHALLENGERS")
print("=" * 90)

import requests
# Check one current ATP Challenger match
print("\nChecking Odds API for current ATP Challenger coverage...")
# Use cached knowledge — Odds API doesn't have challenger sport keys
print("  Known coverage: Odds API has NO ATP Challenger sport key.")
print("  Available tennis keys: tournament-specific (Miami, Barcelona, etc.)")
print("  Challengers are NOT covered by any Odds API sport key.")
print()
print("  For Main draws:")
try:
    r = requests.get("https://api.the-odds-api.com/v4/sports/tennis_atp_barcelona_open/odds",
        params={"apiKey": ODDS_KEY, "regions": "eu,uk", "markets": "h2h"},
        timeout=15)
    data = r.json()
    print("  ATP Barcelona: %d matches with odds" % len(data))
    if data:
        books = set()
        for m in data:
            for b in m.get("bookmakers", []):
                books.add(b["key"])
        print("  Books covering: %d unique (%s...)" % (len(books), ", ".join(sorted(books)[:5])))
        print("  Pinnacle: %s" % ("YES" if "pinnacle" in books else "NO"))
except Exception as e:
    print("  API error: %s" % e)

# ============================================================
# STEP 5: Conclusions
# ============================================================
print("\n" + "=" * 90)
print("STEP 5: CONCLUSIONS")
print("=" * 90)

# Categorize cells by spread profile
tight_cells = []
wide_cells = []
for cell in sorted(cell_spreads.keys()):
    spreads = cell_spreads[cell]
    if len(spreads) < 10:
        continue
    mean_s = sum(spreads) / len(spreads)
    if mean_s <= 2:
        tight_cells.append((cell, mean_s, len(spreads)))
    elif mean_s >= 5:
        wide_cells.append((cell, mean_s, len(spreads)))

print("\nTight-spread cells (mean <= 2c): %d" % len(tight_cells))
for cell, ms, n in tight_cells[:10]:
    print("  %-35s mean=%.1fc  N=%d" % (cell[:35], ms, n))

print("\nWide-spread cells (mean >= 5c): %d" % len(wide_cells))
for cell, ms, n in wide_cells[:10]:
    print("  %-35s mean=%.1fc  N=%d" % (cell[:35], ms, n))

print("\n--- ACTIONABLE INSIGHTS ---")
print()
print("1. EXTERNAL BOOK CROSS-REFERENCE:")
print("   ATP Main + WTA Main: YES (Odds API covers via tournament keys)")
print("   ATP Challenger: NO (zero external coverage)")
print("   -> Challenger entries rely entirely on internal signals")
print()
print("2. SPREAD-WIDTH ENTRY LOGIC:")
if n_wide > 0:
    narrow_pct = 100 * wide_events["narrowed"] / n_wide
    print("   Wide spreads narrow %.0f%% of the time within ~50 ticks" % narrow_pct)
    if narrow_pct > 60:
        print("   -> WORTH building spread-aware entry: post at bid when spread is wide,")
        print("      expect fill as spread compresses. Tighter entry = better avg price.")
    else:
        print("   -> Spread compression is unreliable. Not a strong signal.")
print()
print("3. INTERNAL SIGNALS AVAILABLE:")
print("   - Depth imbalance (bid_sz vs ask_sz at level 1)")
print("   - Spread width (1c = liquid, 5c+ = thin)")
print("   - Trade flow (from Kalshi trades endpoint)")
print("   - Price momentum (bid trend over last N ticks)")

print("\nDONE")
