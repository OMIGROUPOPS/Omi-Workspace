#!/usr/bin/env python3
"""Verify ATP_CHALL_underdog_40-44: genuine bounce vs settlement artifact."""
import csv, os
from pathlib import Path

FACTS_PATH = "/root/Omi-Workspace/arb-executor/analysis/match_facts.csv"
TICKS_DIR = "/root/Omi-Workspace/arb-executor/analysis/match_ticks_full"
DAYS = 28; CT = 10

# Load matches for this cell
matches = []
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        if r["category"] != "ATP_CHALL" or r["side"] != "underdog":
            continue
        entry = float(r["entry_mid"])
        bucket = int(entry / 5) * 5
        if bucket != 40:
            continue
        matches.append({
            "ticker": r["ticker_id"],
            "entry_mid": entry,
            "max_bounce": float(r["max_bounce_from_entry"]),
            "result": r["match_result"],
        })

print("ATP_CHALL_underdog_40-44: %d matches" % len(matches))

# For each match, load ticks and classify the +45c "hit"
EXIT = 45

print("\n" + "=" * 110)
print("STEP 1: CLASSIFY EACH +45c HIT")
print("=" * 110)

cat_a = []  # genuine bounce
cat_b = []  # settlement walk
misses = []

print("\n%-45s %5s %5s %6s %8s %8s %6s %s" % (
    "TICKER", "ENTRY", "TGTC", "RESULT", "HIT_IDX", "TOT_TKS", "RETR?", "CLASS"))
print("-" * 110)

for m in matches:
    ticks_path = os.path.join(TICKS_DIR, "%s.csv" % m["ticker"])
    if not os.path.exists(ticks_path):
        continue

    ticks = []
    with open(ticks_path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 4:
                ticks.append((int(row[0]), float(row[3])))

    if not ticks:
        continue

    entry = m["entry_mid"]
    target = entry + EXIT
    total_ticks = len(ticks)

    # Find first tick where mid >= target
    hit_idx = None
    hit_ts = None
    hit_mid = None
    for i, (ts, mid) in enumerate(ticks):
        if mid >= target:
            hit_idx = i
            hit_ts = ts
            hit_mid = mid
            break

    if hit_idx is None:
        misses.append(m)
        print("%-45s %4.0fc %4.0fc %-6s %8s %8d %6s MISS" % (
            m["ticker"][:45], entry, target, m["result"], "-", total_ticks, "-"))
        continue

    # Classify: check price AFTER hit
    # If price retreats >10c below target within next 20% of remaining ticks = genuine bounce
    # If price stays near/above target until settlement = settlement walk
    remaining = ticks[hit_idx:]
    min_after = min(mid for _, mid in remaining) if remaining else hit_mid
    max_after = max(mid for _, mid in remaining) if remaining else hit_mid
    retreat = hit_mid - min_after

    # Also check: did hit happen in last 5% of ticks? (settlement zone)
    position_pct = 100 * hit_idx / total_ticks
    in_settlement_zone = position_pct > 90

    # Category determination
    if retreat > 10 and not in_settlement_zone:
        category = "A:BOUNCE"
        cat_a.append(m)
    elif in_settlement_zone or (max_after > 95 and retreat < 5):
        category = "B:SETTLE"
        cat_b.append(m)
    elif retreat > 5:
        category = "A:BOUNCE"
        cat_a.append(m)
    else:
        category = "B:SETTLE"
        cat_b.append(m)

    print("%-45s %4.0fc %4.0fc %-6s %7d %8d %+5.0fc %s (hit@%.0f%%, retr=%.0fc, final=%.0fc)" % (
        m["ticker"][:45], entry, target, m["result"],
        hit_idx, total_ticks, -retreat, category,
        position_pct, retreat, ticks[-1][1]))

print("\n--- CLASSIFICATION SUMMARY ---")
print("Total matches: %d" % len(matches))
print("Hits at +45c: %d (%.0f%%)" % (len(cat_a) + len(cat_b), 100*(len(cat_a)+len(cat_b))/len(matches)))
print("  Category A (genuine bounce): %d" % len(cat_a))
print("  Category B (settlement walk): %d" % len(cat_b))
print("Misses: %d" % len(misses))

# Detail on category B
if cat_b:
    print("\nCategory B matches (settlement-walk 'hits'):")
    for m in cat_b:
        print("  %s entry=%.0fc result=%s bounce=%.0fc" % (
            m["ticker"][:45], m["entry_mid"], m["result"], m["max_bounce"]))

# ============================================================
print("\n" + "=" * 80)
print("STEP 2: RECOMPUTE EV UNDER TWO SCENARIOS")
print("=" * 80)

# Scenario 1: +10c scalp
total_10 = 0
hits_10 = 0
for m in matches:
    if m["max_bounce"] >= 10:
        total_10 += 10 * CT
        hits_10 += 1
    else:
        settle = 99.5 if m["result"] == "win" else 0.5
        total_10 += (settle - m["entry_mid"]) * CT

ev_10 = total_10 / len(matches) / 100.0
dpd_10 = ev_10 * len(matches) / DAYS

# Scenario 2: +45c wide (current)
total_45 = 0
hits_45 = 0
for m in matches:
    if m["max_bounce"] >= 45:
        total_45 += 45 * CT
        hits_45 += 1
    else:
        settle = 99.5 if m["result"] == "win" else 0.5
        total_45 += (settle - m["entry_mid"]) * CT

ev_45 = total_45 / len(matches) / 100.0
dpd_45 = ev_45 * len(matches) / DAYS

# Scenario 3: +45c but ONLY count genuine bounces (Category A hits)
# Category B hits revert to settlement outcome
total_45_honest = 0
for m in matches:
    if m in cat_a:
        total_45_honest += 45 * CT  # genuine exit fill
    elif m in cat_b:
        settle = 99.5 if m["result"] == "win" else 0.5
        total_45_honest += (settle - m["entry_mid"]) * CT  # settlement, not exit
    else:
        settle = 99.5 if m["result"] == "win" else 0.5
        total_45_honest += (settle - m["entry_mid"]) * CT

ev_45h = total_45_honest / len(matches) / 100.0
dpd_45h = ev_45h * len(matches) / DAYS

# Scenario 4: Hold to settlement (no exit at all)
total_hold = 0
for m in matches:
    settle = 99.5 if m["result"] == "win" else 0.5
    total_hold += (settle - m["entry_mid"]) * CT

ev_hold = total_hold / len(matches) / 100.0
dpd_hold = ev_hold * len(matches) / DAYS

win_rate = sum(1 for m in matches if m["result"] == "win") / len(matches)

print("\nN=%d, avg_entry=%.0fc, win_rate=%.0f%%" % (
    len(matches),
    sum(m["entry_mid"] for m in matches) / len(matches),
    100 * win_rate))

print("\n%-30s %5s %7s %7s" % ("SCENARIO", "HITS", "EV/tr$", "$/DAY"))
print("-" * 55)
print("%-30s %4d $%+5.3f $%+5.2f" % ("+10c scalp", hits_10, ev_10, dpd_10))
print("%-30s %4d $%+5.3f $%+5.2f" % ("+45c (backtest=all hits)", hits_45, ev_45, dpd_45))
print("%-30s %4d $%+5.3f $%+5.2f" % ("+45c (genuine bounces only)", len(cat_a), ev_45h, dpd_45h))
print("%-30s %4s $%+5.3f $%+5.2f" % ("Hold to settlement", "-", ev_hold, dpd_hold))

print("\n--- KEY FINDING ---")
if len(cat_b) > len(cat_a):
    print("MAJORITY of +45c 'hits' (%d/%d = %.0f%%) are settlement walks, not tradeable bounces." % (
        len(cat_b), len(cat_a)+len(cat_b), 100*len(cat_b)/(len(cat_a)+len(cat_b))))
    print("+45c exit is MOSTLY a hold-to-settle strategy disguised as a target exit.")
else:
    print("MAJORITY of +45c hits (%d/%d = %.0f%%) are genuine mid-match bounces." % (
        len(cat_a), len(cat_a)+len(cat_b), 100*len(cat_a)/(len(cat_a)+len(cat_b))))
    print("+45c exit IS a tradeable target that fires during live play.")

# Show example matches
print("\n" + "=" * 80)
print("STEP 3: EXAMPLE MATCHES — PRICE PATH DETAILS")
print("=" * 80)

# Show 3 Category A and 3 Category B with price path
for label, group in [("CATEGORY A (genuine bounce)", cat_a[:3]), ("CATEGORY B (settlement walk)", cat_b[:3])]:
    print("\n--- %s ---" % label)
    for m in group:
        ticks_path = os.path.join(TICKS_DIR, "%s.csv" % m["ticker"])
        ticks = []
        with open(ticks_path) as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) >= 4:
                    ticks.append((int(row[0]), float(row[3])))

        entry = m["entry_mid"]
        target = entry + EXIT
        n = len(ticks)

        # Sample price path at 10 points
        sample_indices = [int(n * p / 10) for p in range(11)]
        print("\n  %s  entry=%.0fc  target=%.0fc  result=%s" % (
            m["ticker"][:45], entry, target, m["result"]))
        print("  Price path (0%% to 100%% of match):")
        path_str = "  "
        for idx in sample_indices:
            if idx < n:
                pct = 100 * idx / n
                mid = ticks[idx][1]
                path_str += "%.0f%%:%.0fc  " % (pct, mid)
        print(path_str)

print("\nDONE")
