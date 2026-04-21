#!/usr/bin/env python3
"""intel_distribution.py — Population analysis of intelligence scoring across all discovered events."""

import sys, os, json, sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from intelligence import confidence_score, _conn, CONFIG_PATH

ET = ZoneInfo("America/New_York")
DB_PATH = str(Path(__file__).resolve().parent / "tennis.db")


def main():
    now = datetime.now(ET)
    now_str = now.strftime("%Y-%m-%d %I:%M:%S %p ET")

    conn = sqlite3.connect(DB_PATH, timeout=10)
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT kps.event_ticker, kps.ticker, kps.series_ticker
        FROM kalshi_price_snapshots kps
        INNER JOIN (
            SELECT ticker, MAX(polled_at) as mp
            FROM kalshi_price_snapshots
            GROUP BY ticker
        ) latest ON kps.ticker = latest.ticker AND kps.polled_at = latest.mp
        ORDER BY kps.event_ticker
    """)
    all_tickers = cur.fetchall()
    conn.close()

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    print("=" * 100)
    print("INTELLIGENCE DISTRIBUTION @ %s" % now_str)
    print("=" * 100)
    print("\nScoring %d tickers..." % len(all_tickers))

    tier_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "SKIP": 0}
    anchor_counts = {"fv": 0, "kalshi": 0}
    series_tiers = defaultdict(lambda: {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "SKIP": 0})
    cell_counts = defaultdict(int)
    flag_counts = defaultdict(int)
    score_buckets = defaultdict(int)  # 0-9, 10-19, ..., 90-100

    for et, tk, series in all_tickers:
        if "KXATPCHALLENGER" in et:
            cat = "ATP_CHALL"
        elif "KXWTACHALLENGER" in et:
            cat = "WTA_CHALL"
        elif "KXATPMATCH" in et:
            cat = "ATP_MAIN"
        elif "KXWTAMATCH" in et:
            cat = "WTA_MAIN"
        else:
            cat = "OTHER"

        try:
            cs = confidence_score(et, tk)
        except Exception as e:
            tier_counts["SKIP"] = tier_counts.get("SKIP", 0) + 1
            series_tiers[cat]["SKIP"] += 1
            continue

        grade = cs.get("grade", "SKIP")
        tier_counts[grade] = tier_counts.get(grade, 0) + 1
        series_tiers[cat][grade] += 1
        anchor_counts[cs.get("anchor_mode", "fv")] += 1

        bucket = min(cs.get("score", 0) // 10 * 10, 90)
        score_buckets[bucket] += 1

        for flag in cs.get("flags", []):
            if flag.startswith("CELL_DISABLED_"):
                flag_counts["CELL_DISABLED"] += 1
            else:
                flag_counts[flag] += 1

        comps = cs.get("components", {})
        if "cell_fit" in comps or "cell_fit_kalshi" in comps:
            pass

    total = sum(tier_counts.values())

    # Tier distribution
    print("\nTIER DISTRIBUTION:")
    print("  %-8s %6s %6s  %s" % ("TIER", "COUNT", "PCT", "BAR"))
    print("  " + "-" * 60)
    for grade in ["HIGH", "MEDIUM", "LOW", "SKIP"]:
        n = tier_counts[grade]
        pct = n / total * 100 if total > 0 else 0
        bar = "#" * int(pct / 2)
        print("  %-8s %6d %5.1f%%  %s" % (grade, n, pct, bar))
    print("  %-8s %6d %5s" % ("TOTAL", total, ""))

    # Anchor distribution
    print("\nANCHOR MODE:")
    for mode, cnt in sorted(anchor_counts.items()):
        pct = cnt / total * 100 if total > 0 else 0
        print("  %-10s %5d (%5.1f%%)" % (mode, cnt, pct))

    # Per-series breakdown
    print("\nPER-SERIES BREAKDOWN:")
    print("  %-12s %5s %5s %5s %5s %5s" % ("SERIES", "HIGH", "MED", "LOW", "SKIP", "TOTAL"))
    print("  " + "-" * 50)
    for cat in ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL", "OTHER"]:
        t = series_tiers.get(cat)
        if not t:
            continue
        s_total = sum(t.values())
        print("  %-12s %5d %5d %5d %5d %5d" % (
            cat, t["HIGH"], t["MEDIUM"], t["LOW"], t["SKIP"], s_total))

    # Score distribution histogram
    print("\nSCORE DISTRIBUTION:")
    for bucket in range(0, 100, 10):
        n = score_buckets.get(bucket, 0)
        pct = n / total * 100 if total > 0 else 0
        bar = "#" * int(pct)
        print("  %2d-%2d: %4d (%5.1f%%) %s" % (bucket, bucket + 9, n, pct, bar))

    # Flags
    print("\nFLAG FREQUENCY:")
    for flag, cnt in sorted(flag_counts.items(), key=lambda x: -x[1])[:15]:
        print("  %-30s %5d" % (flag, cnt))

    # Unreachable analysis
    skip_count = tier_counts["SKIP"]
    tradeable = total - skip_count
    print("\nTRADEABILITY:")
    print("  Total discovered: %d" % total)
    print("  Tradeable (HIGH+MEDIUM+LOW): %d (%.1f%%)" % (tradeable, tradeable / total * 100 if total > 0 else 0))
    print("  Unreachable (SKIP): %d (%.1f%%)" % (skip_count, skip_count / total * 100 if total > 0 else 0))
    print("  FV-anchored: %d  Kalshi-anchored: %d" % (anchor_counts["fv"], anchor_counts["kalshi"]))


if __name__ == "__main__":
    main()
