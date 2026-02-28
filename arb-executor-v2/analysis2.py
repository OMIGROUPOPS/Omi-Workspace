import json
from collections import Counter

# Archive only
with open("trades_archive_feb8-21.json") as f:
    archive = json.load(f)

# Current only
with open("trades.json") as f:
    current = json.load(f)

print("=" * 60)
print("ARCHIVE (Feb 8-21): {} trades".format(len(archive)))
print("=" * 60)
statuses = Counter(t.get("status","?") for t in archive)
for s, c in statuses.most_common():
    print("  {}: {} ({:.1f}%)".format(s, c, c/len(archive)*100))

archive_nf = [t for t in archive if t.get("status") == "PM_NO_FILL"]
archive_nf_spreads = [t.get("spread_cents", 0) or 0 for t in archive_nf]
if archive_nf_spreads:
    print("No-fill avg spread: {:.1f}c".format(sum(archive_nf_spreads)/len(archive_nf_spreads)))
    
    # Distribution of spreads
    buckets = {"3-5c": 0, "6-10c": 0, "11-15c": 0, "16-20c": 0, "21-30c": 0, "30c+": 0}
    for s in archive_nf_spreads:
        if s <= 5: buckets["3-5c"] += 1
        elif s <= 10: buckets["6-10c"] += 1
        elif s <= 15: buckets["11-15c"] += 1
        elif s <= 20: buckets["16-20c"] += 1
        elif s <= 30: buckets["21-30c"] += 1
        else: buckets["30c+"] += 1
    print("No-fill spread distribution:")
    for b, c in buckets.items():
        print("  {}: {} ({:.1f}%)".format(b, c, c/len(archive_nf_spreads)*100))

# Archive success trades
archive_success = [t for t in archive if t.get("status") == "SUCCESS"]
print("Success avg spread: {:.1f}c".format(sum(t.get("spread_cents",0) or 0 for t in archive_success)/max(len(archive_success),1)))
# Direction breakdown
for d in ["BUY_PM_SELL_K", "BUY_K_SELL_PM"]:
    dt = [t for t in archive if t.get("direction") == d]
    ds = [t for t in dt if t.get("status") == "SUCCESS"]
    dn = [t for t in dt if t.get("status") == "PM_NO_FILL"]
    print("  {} fill rate: {}/{} ({:.1f}%)".format(d, len(ds), len(dt), len(ds)/max(len(dt),1)*100))

print()
print("=" * 60)
print("CURRENT (Feb 21+): {} trades".format(len(current)))
print("=" * 60)
statuses = Counter(t.get("status","?") for t in current)
for s, c in statuses.most_common():
    print("  {}: {} ({:.1f}%)".format(s, c, c/len(current)*100))

current_nf = [t for t in current if t.get("status") == "PM_NO_FILL"]
current_nf_spreads = [t.get("spread_cents", 0) or 0 for t in current_nf]
if current_nf_spreads:
    print("No-fill avg spread: {:.1f}c".format(sum(current_nf_spreads)/len(current_nf_spreads)))
    
    buckets = {"3-5c": 0, "6-10c": 0, "11-15c": 0, "16-20c": 0, "21-30c": 0, "30c+": 0}
    for s in current_nf_spreads:
        if s <= 5: buckets["3-5c"] += 1
        elif s <= 10: buckets["6-10c"] += 1
        elif s <= 15: buckets["11-15c"] += 1
        elif s <= 20: buckets["16-20c"] += 1
        elif s <= 30: buckets["21-30c"] += 1
        else: buckets["30c+"] += 1
    print("No-fill spread distribution:")
    for b, c in buckets.items():
        print("  {}: {} ({:.1f}%)".format(b, c, c/len(current_nf_spreads)*100))

current_success = [t for t in current if t.get("status") == "SUCCESS"]
print("Success avg spread: {:.1f}c".format(sum(t.get("spread_cents",0) or 0 for t in current_success)/max(len(current_success),1)))
for d in ["BUY_PM_SELL_K", "BUY_K_SELL_PM"]:
    dt = [t for t in current if t.get("direction") == d]
    ds = [t for t in dt if t.get("status") == "SUCCESS"]
    print("  {} fill rate: {}/{} ({:.1f}%)".format(d, len(ds), len(dt), len(ds)/max(len(dt),1)*100))

# Missed money analysis
print()
print("=" * 60)
print("MISSED MONEY ANALYSIS")
print("=" * 60)
archive_missed = sum(t.get("profit_dollars", 0) or 0 for t in archive if t.get("status") == "PM_NO_FILL")
current_missed = sum(t.get("profit_dollars", 0) or 0 for t in current if t.get("status") == "PM_NO_FILL")
archive_earned = sum(t.get("profit_dollars", 0) or 0 for t in archive if t.get("status") == "SUCCESS")
current_earned = sum(t.get("profit_dollars", 0) or 0 for t in current if t.get("status") == "SUCCESS")
print("Archive: Earned ${:.2f}, Missed ${:.2f} (capture rate: {:.1f}%)".format(
    archive_earned, archive_missed, archive_earned/(archive_earned+archive_missed)*100 if (archive_earned+archive_missed) > 0 else 0))
print("Current: Earned ${:.2f}, Missed ${:.2f} (capture rate: {:.1f}%)".format(
    current_earned, current_missed, current_earned/(current_earned+current_missed)*100 if (current_earned+current_missed) > 0 else 0))
