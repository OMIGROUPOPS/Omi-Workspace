import sqlite3
from collections import defaultdict

conn = sqlite3.connect("/root/Omi-Workspace/arb-executor/tennis.db")
cur = conn.cursor()

# Build per-ticker: first mid, pre-commence max mid, post-commence max mid
cur.execute("""
    SELECT ticker, commence_time, polled_at, bid_cents, ask_cents
    FROM kalshi_price_snapshots
    WHERE commence_time IS NOT NULL AND bid_cents IS NOT NULL AND ask_cents IS NOT NULL
    ORDER BY ticker, polled_at
""")

per_ticker = {}
for ticker, commence, polled, bid, ask in cur.fetchall():
    mid = (bid + ask) / 2.0
    # Normalize commence_time format (has T and Z)
    commence_clean = commence.replace("T", " ").replace("Z", "")

    if ticker not in per_ticker:
        per_ticker[ticker] = {
            "first_mid": mid, "first_ts": polled, "commence": commence_clean,
            "pre_max": mid, "in_max": None, "pre_mids": [mid], "in_mids": []
        }
    else:
        rec = per_ticker[ticker]
        if polled < commence_clean:
            if mid > rec["pre_max"]:
                rec["pre_max"] = mid
            rec["pre_mids"].append(mid)
        else:
            if rec["in_max"] is None or mid > rec["in_max"]:
                rec["in_max"] = mid
            rec["in_mids"].append(mid)

print("Tickers with snapshots: %d" % len(per_ticker))
print("Tickers with in-play data: %d" % sum(1 for v in per_ticker.values() if v["in_max"] is not None))

def cat_from_ticker(ticker):
    if "ATPCHALLENGER" in ticker: return "ATP_CHALL"
    if "ATPMATCH" in ticker: return "ATP_MAIN"
    if "WTACHALLENGER" in ticker: return "WTA_CHALL"
    if "WTAMATCH" in ticker: return "WTA_MAIN"
    return None

# Classify and compute swings
swing_pre = defaultdict(list)
swing_in = defaultdict(list)

for ticker, rec in per_ticker.items():
    cat = cat_from_ticker(ticker)
    if not cat: continue
    entry = rec["first_mid"]
    if entry <= 0 or entry >= 100: continue

    side = "leader" if entry >= 50 else "underdog"
    band = int(entry // 10) * 10
    key = (cat, side, band)

    # Pregame upward swing = pre_max - entry
    pre_swing = rec["pre_max"] - entry
    swing_pre[key].append(pre_swing)

    # In-play upward swing = in_max - entry (if in-play data exists)
    if rec["in_max"] is not None:
        in_swing = rec["in_max"] - entry
        swing_in[key].append(in_swing)

def stats(vals):
    if not vals: return 0, 0, 0, 0
    n = len(vals)
    m = sum(vals) / n
    s = sorted(vals)
    med = s[n // 2]
    p75 = s[int(n * 0.75)]
    p25 = s[int(n * 0.25)]
    return m, med, p25, p75

print()
print("=" * 130)
print("%-12s %-10s %-8s | %5s %8s %8s %8s %8s | %5s %8s %8s %8s %8s" % (
    "category", "side", "band", "N_pre", "mean", "median", "p25", "p75",
    "N_in", "mean", "median", "p25", "p75"))
print("-" * 130)

for cat in ("ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"):
    for side in ("underdog", "leader"):
        for band in range(0, 100, 10):
            key = (cat, side, band)
            pre = swing_pre.get(key, [])
            inp = swing_in.get(key, [])
            if len(pre) < 3 and len(inp) < 3: continue

            pm, pmed, pp25, pp75 = stats(pre)
            im, imed, ip25, ip75 = stats(inp)

            label = "%d-%dc" % (band, band + 9)
            print("%-12s %-10s %-8s | %5d %+7.1fc %+7.1fc %+7.1fc %+7.1fc | %5d %+7.1fc %+7.1fc %+7.1fc %+7.1fc" % (
                cat, side, label, len(pre), pm, pmed, pp25, pp75, len(inp), im, imed, ip25, ip75))
    print()

# Summary: for the SCALPER_EDGE underdog cells, what fraction reach +15c pregame vs in-play?
print("=" * 90)
print("SCALP REACHABILITY at +15c exit target")
print("%-12s %-10s %-8s | %5s %8s %8s | %8s" % (
    "category", "side", "band", "N", "pre>=15", "in>=15", "total>=15"))
print("-" * 90)

for cat in ("ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"):
    for side in ("underdog", "leader"):
        for band in range(0, 100, 10):
            key = (cat, side, band)
            pre = swing_pre.get(key, [])
            inp = swing_in.get(key, [])
            if len(pre) < 3: continue

            n_pre_reach = sum(1 for s in pre if s >= 15)
            n_in_reach = sum(1 for s in inp if s >= 15)
            n_total = len(pre)  # all tickers have pre data
            # For total reachability: ticker reached +15 in either phase
            # Need per-ticker data
            print("%-12s %-10s %-8s | %5d %7.0f%% %7.0f%% |" % (
                cat, side, "%d-%dc" % (band, band+9), n_total,
                n_pre_reach/n_total*100, n_in_reach/len(inp)*100 if inp else 0))
    print()

conn.close()
