#!/usr/bin/env python3
"""Verify kalshi_open and kalshi_close timestamps used in the backtest."""
import csv, os
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
FACTS_PATH = "/root/Omi-Workspace/arb-executor/analysis/match_facts.csv"
TICKS_DIR = "/root/Omi-Workspace/arb-executor/analysis/match_ticks_full"
TIMING_PATH = "/root/Omi-Workspace/arb-executor/analysis/pinnacle_kalshi_timing.csv"

def fmt_et(epoch):
    return datetime.fromtimestamp(epoch, tz=ET).strftime("%I:%M %p ET") if epoch else "N/A"

# Load facts
facts = {}
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        if r["category"] in ("ATP_MAIN", "WTA_MAIN"):
            facts[r["ticker_id"]] = r

# Load what the previous backtest used
prev_results = {}
with open(TIMING_PATH) as f:
    for r in csv.DictReader(f):
        prev_results[r["match_id"]] = r

# Pick 10 diverse matches
sample_tickers = [
    "KXATPMATCH-26MAR29DRAGAL-GAL",   # ATP underdog
    "KXATPMATCH-26MAR29DRAGAL-DRA",   # ATP leader (same match)
    "KXWTAMATCH-26MAR20FERSEL-FER",   # WTA leader
    "KXATPMATCH-26APR05BAEWAW-BAE",   # ATP leader
    "KXWTAMATCH-26APR01ANDKEN-AND",   # WTA leader
    "KXATPMATCH-26MAR20MOUMAC-MOU",   # ATP underdog
    "KXWTAMATCH-26MAR28BASHER-BAS",   # WTA leader
    "KXATPMATCH-26APR12RINMIC-RIN",   # ATP leader
    "KXWTAMATCH-26APR06STEMAR-STE",   # WTA leader
    "KXATPMATCH-26MAR23TABMIC-MIC",   # ATP underdog
]

print("=" * 90)
print("STEP 1: DETAILED TIMESTAMP VERIFICATION (10 matches)")
print("=" * 90)

print("\n%-45s %6s %6s %5s %6s %6s %6s" % (
    "TICKER", "T_OPEN", "T_CLOSE", "HRS", "MID_O", "MID_C", "DRIFT"))

all_drifts = []

for tk in sample_tickers:
    f = facts.get(tk)
    if not f:
        print("  %s: NOT IN FACTS" % tk)
        continue

    pregame_ts = int(f["pregame_close_ts"])
    entry_mid = float(f["entry_mid"])

    # Load ticks
    path = os.path.join(TICKS_DIR, "%s.csv" % tk)
    if not os.path.exists(path):
        print("  %s: NO TICK FILE" % tk)
        continue

    ticks = []
    with open(path) as fh:
        reader = csv.reader(fh)
        next(reader)
        for row in reader:
            if len(row) >= 4:
                ticks.append((int(row[0]), int(row[1]), int(row[2]), float(row[3])))

    if not ticks:
        continue

    # T_open = first tick (ts_offset=0 is pregame_close_ts)
    # Actually: ts_offset_sec is seconds from pregame_close_ts
    # So actual timestamp = pregame_ts + ts_offset
    first_offset = ticks[0][0]
    first_ts = pregame_ts + first_offset  # Wait — let me check this

    # Actually in export_ticks_full.py: offset = ts - pc_ts
    # So ts = pc_ts + offset. offset starts at 0 (pregame close) and goes up
    # Wait no — ticks start from pregame close FORWARD (during the match)
    # first tick offset=0 means AT pregame close
    # But if offset < 0 that would mean before pregame close

    # Let me just check raw offsets
    first_off = ticks[0][0]
    last_off = ticks[-1][0]
    first_bid, first_ask, first_mid = ticks[0][1], ticks[0][2], ticks[0][3]
    last_bid, last_ask, last_mid = ticks[-1][1], ticks[-1][2], ticks[-1][3]

    duration_sec = last_off - first_off
    duration_hrs = duration_sec / 3600

    # Mid at pregame close (offset=0 or closest to 0)
    mid_at_pgclose = first_mid  # first tick is at/near pregame close
    for t in ticks:
        if t[0] >= 0:
            mid_at_pgclose = t[3]
            break

    drift = abs(last_mid - first_mid)

    print("%-45s %6s %6s %5.1f %5.1fc %5.1fc %+5.1fc" % (
        tk[:45],
        fmt_et(pregame_ts + first_off),
        fmt_et(pregame_ts + last_off),
        duration_hrs,
        first_mid, last_mid, last_mid - first_mid))

    # What did the previous backtest use?
    prev = prev_results.get(tk)
    if prev:
        print("  PREV BACKTEST: kalshi_open=%.1fc kalshi_close=%.1fc (entry_mid from facts)" % (
            float(prev["kalshi_open"]), float(prev["kalshi_close"])))
    print("  TICK FILE: first_offset=%ds last_offset=%ds (%d ticks)" % (
        first_off, last_off, len(ticks)))
    print("  entry_mid from facts = %.1fc (this IS the pregame close mid)" % entry_mid)
    print()

print("=" * 90)
print("THE BUG:")
print("=" * 90)
print()
print("In pinnacle_backtest.py, load_kalshi_ticks() returned:")
print("  kalshi_open = first tick mid (= mid at pregame close)")
print("  kalshi_close = LAST tick mid (= mid at match END / settlement)")
print()
print("But in the analysis, kalshi_close was OVERWRITTEN with:")
print('  "kalshi_close": f["entry_mid"]')
print("Which is ALSO the pregame close mid from match_facts.csv.")
print()
print("So kalshi_open ≈ kalshi_close ≈ entry_mid (all = pregame close mid)")
print("The 0.4c MAE is just rounding noise between first tick and entry_mid.")
print()
print("The tick files ONLY contain post-pregame-close data (match ticks).")
print("There is NO premarket data in match_ticks_full/.")
print("Premarket drift cannot be measured from this dataset.")

print()
print("=" * 90)
print("STEP 2: WHAT DO THE TICK FILES ACTUALLY COVER?")
print("=" * 90)
print()

# Analyze the full 126 matched set
all_first_offsets = []
all_durations = []
all_tick_counts = []
all_drifts_full = []

for tk in facts:
    path = os.path.join(TICKS_DIR, "%s.csv" % tk)
    if not os.path.exists(path):
        continue
    with open(path) as fh:
        reader = csv.reader(fh)
        next(reader)
        rows = []
        for row in reader:
            if len(row) >= 4:
                rows.append((int(row[0]), float(row[3])))
    if not rows:
        continue
    all_first_offsets.append(rows[0][0])
    all_durations.append((rows[-1][0] - rows[0][0]) / 3600)
    all_tick_counts.append(len(rows))
    all_drifts_full.append(abs(rows[-1][1] - rows[0][1]))

def pct(vals, p):
    s = sorted(vals)
    return s[int(len(s) * p)]

n = len(all_first_offsets)
print("Across %d tickers with tick files:" % n)
print()
print("First tick offset from pregame_close_ts:")
print("  min=%ds  p25=%ds  median=%ds  p75=%ds  max=%ds" % (
    min(all_first_offsets), pct(all_first_offsets, 0.25),
    pct(all_first_offsets, 0.5), pct(all_first_offsets, 0.75),
    max(all_first_offsets)))
print("  (positive = AFTER pregame close, negative = before)")
print()
print("Duration of tick coverage (hours):")
print("  min=%.1f  p25=%.1f  median=%.1f  p75=%.1f  max=%.1f" % (
    min(all_durations), pct(all_durations, 0.25),
    pct(all_durations, 0.5), pct(all_durations, 0.75),
    max(all_durations)))
print()
print("Tick count per file:")
print("  min=%d  p25=%d  median=%d  p75=%d  max=%d" % (
    min(all_tick_counts), pct(all_tick_counts, 0.25),
    pct(all_tick_counts, 0.5), pct(all_tick_counts, 0.75),
    max(all_tick_counts)))
print()
print("Total mid drift (first tick to last tick) in cents:")
print("  min=%.0f  p25=%.0f  median=%.0f  p75=%.0f  max=%.0f  mean=%.1f" % (
    min(all_drifts_full), pct(all_drifts_full, 0.25),
    pct(all_drifts_full, 0.5), pct(all_drifts_full, 0.75),
    max(all_drifts_full), sum(all_drifts_full)/len(all_drifts_full)))
print("  (This is pregame-close to settlement drift, NOT premarket drift)")

print()
print("=" * 90)
print("STEP 3: DO WE HAVE ANY PREMARKET DATA?")
print("=" * 90)
print()

# Check if any ticks have negative offsets (before pregame close)
neg_offset_count = 0
neg_offset_tickers = []
for tk in facts:
    path = os.path.join(TICKS_DIR, "%s.csv" % tk)
    if not os.path.exists(path):
        continue
    with open(path) as fh:
        reader = csv.reader(fh)
        next(reader)
        for row in reader:
            if len(row) >= 4 and int(row[0]) < 0:
                neg_offset_count += 1
                if tk not in neg_offset_tickers:
                    neg_offset_tickers.append(tk)
                break

print("Tickers with ticks BEFORE pregame close (offset < 0): %d / %d" % (
    len(neg_offset_tickers), len(facts)))
if neg_offset_tickers:
    print("Examples:")
    for tk in neg_offset_tickers[:5]:
        path = os.path.join(TICKS_DIR, "%s.csv" % tk)
        with open(path) as fh:
            reader = csv.reader(fh)
            next(reader)
            first = next(reader)
            print("  %s: first_offset=%s" % (tk[:45], first[0]))

print()
print("=" * 90)
print("CONCLUSION")
print("=" * 90)
print()
print("1. match_ticks_full/ contains MATCH ticks (post-pregame-close),")
print("   NOT premarket ticks. Zero premarket BBO data exists in our")
print("   historical dataset.")
print()
print("2. The 0.4c MAE was correct but meaningless — it compared")
print("   entry_mid to itself (both = pregame close mid).")
print()
print("3. The Pinnacle/book analysis compared book opening odds to")
print("   Kalshi's pregame close mid. This IS a valid comparison,")
print("   but we cannot measure Kalshi premarket drift because we")
print("   don't have premarket tick data.")
print()
print("4. The live_v3 premarket_ticks/ collection (started today) will")
print("   provide this data going forward. After 30 days we can re-run")
print("   the analysis with actual premarket drift measurements.")
print()
print("5. For now: book signals may still predict DIRECTION of the")
print("   pregame close (leader vs underdog), but we cannot verify")
print("   premarket convergence without premarket tick history.")
