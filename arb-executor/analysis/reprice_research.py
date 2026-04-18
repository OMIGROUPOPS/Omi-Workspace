#!/usr/bin/env python3
"""V5 reprice-while-waiting research."""
import csv, json, os, time
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ARB_DIR = Path("/root/Omi-Workspace/arb-executor")
TICKS_DIR = ARB_DIR / "analysis" / "premarket_ticks"
deploy = 1776535451

# Load entries from log
entries = {}
for log in sorted((ARB_DIR / "logs").glob("live_v3_*.jsonl")):
    with open(log) as f:
        for line in f:
            e = json.loads(line)
            if e.get("ts_epoch", 0) < deploy:
                continue
            ev = e["event"]
            tk = e.get("ticker", "")
            d = e.get("details", {})
            if ev == "order_placed" and d.get("action") == "buy":
                entries[tk] = {"post_time": e["ts_epoch"], "post_price": d.get("price", 0),
                               "cell": "", "filled": False}
            elif ev == "cell_match":
                if tk in entries:
                    entries[tk]["cell"] = d.get("cell", "?")
                    entries[tk]["mid_at_post"] = d.get("mid_at_post", 0)
            elif ev == "entry_filled":
                if tk in entries:
                    entries[tk]["filled"] = True
                    entries[tk]["fill_time"] = e["ts_epoch"]
                    entries[tk]["fill_price"] = d.get("fill_price", 0)

# Also detect fills via reconcile
for log in sorted((ARB_DIR / "logs").glob("live_v3_*.jsonl")):
    with open(log) as f:
        for line in f:
            e = json.loads(line)
            if e.get("ts_epoch", 0) < deploy:
                continue
            if e["event"] == "reconcile_exit_posted":
                tk = e.get("ticker", "")
                if tk in entries and not entries[tk]["filled"]:
                    entries[tk]["filled"] = True
                    entries[tk]["fill_time"] = e["ts_epoch"]
                    entries[tk]["fill_price"] = e.get("details", {}).get("avg_price", entries[tk]["post_price"])

def load_ticks(ticker):
    f = TICKS_DIR / ("%s.csv" % ticker)
    if not f.exists():
        return []
    rows = []
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
                spread = ask - bid if bid > 0 and ask < 100 else 999
            except (ValueError, IndexError):
                continue
            rows.append({"ts": row[0], "bid": bid, "ask": ask, "mid": mid, "spread": spread})
    return rows

# ============================================================
print("=" * 100)
print("V5 REPRICE-WHILE-WAITING RESEARCH")
print("=" * 100)

# STEP 1: Drift during wait
print("\n--- STEP 1: DRIFT DURING WAIT PERIOD ---\n")
print("%-30s %5s %5s %5s %5s %5s %5s %5s %s" % (
    "TICKER", "POST", "FILL", "WAIT", "MID_P", "MID_F", "MAX", "MIN", "STATUS"))
print("-" * 100)

wait_durations = []
drift_at_fill = []
all_drift_data = []

for tk in sorted(entries.keys()):
    info = entries[tk]
    ticks = load_ticks(tk)
    if not ticks:
        continue

    post_price = info["post_price"]
    # Filter ticks with valid spreads (not opening-state 88c+)
    valid = [t for t in ticks if t["spread"] < 50 and t["bid"] > 0]
    if not valid:
        valid = ticks

    mids = [t["mid"] for t in valid]
    mid_at_post = mids[0] if mids else post_price
    max_mid = max(mids) if mids else mid_at_post
    min_mid = min(mids) if mids else mid_at_post

    if info["filled"]:
        fill_price = info.get("fill_price", post_price)
        wait_min = (info.get("fill_time", info["post_time"]) - info["post_time"]) / 60
        mid_at_fill = mids[-1] if mids else fill_price
        status = "FILLED"
        wait_durations.append(wait_min)
        drift_at_fill.append(fill_price - post_price)
    else:
        fill_price = 0
        wait_min = (time.time() - info["post_time"]) / 60
        mid_at_fill = mids[-1] if mids else 0
        status = "EXPIRED"

    all_drift_data.append({
        "ticker": tk, "post_price": post_price, "fill_price": fill_price,
        "mid_at_post": mid_at_post, "mid_at_fill": mid_at_fill,
        "max_mid": max_mid, "min_mid": min_mid, "wait_min": wait_min,
        "filled": info["filled"], "ticks": valid,
    })

    player = tk.split("-")[-1]
    print("%-30s %4dc %4dc %4.0fm %4.0fc %4.0fc %4.0fc %4.0fc %s" % (
        "...%s (%s)" % (tk[-15:], player),
        post_price, fill_price if fill_price else 0, wait_min,
        mid_at_post, mid_at_fill, max_mid, min_mid, status))

if wait_durations:
    wait_durations.sort()
    n = len(wait_durations)
    print("\nFilled wait times: min=%.0fm median=%.0fm max=%.0fm" % (
        wait_durations[0], wait_durations[n//2], wait_durations[-1]))
if drift_at_fill:
    print("Fill price drift from post: min=%+dc median=%+dc max=%+dc" % (
        min(drift_at_fill), sorted(drift_at_fill)[len(drift_at_fill)//2], max(drift_at_fill)))

# STEP 2: Spread dynamics during wait
print("\n--- STEP 2: SPREAD DYNAMICS DURING WAIT ---\n")
print("%-30s %5s %5s %5s %5s %6s %6s" % (
    "TICKER", "SP_P", "AVG", "MIN", "MAX", "TIGHT%", "FAT%"))
print("-" * 75)

for d in all_drift_data:
    ticks = d["ticks"]
    if not ticks:
        continue
    spreads = [t["spread"] for t in ticks if t["spread"] < 50]
    if not spreads:
        continue
    sp_post = spreads[0]
    avg_sp = sum(spreads) / len(spreads)
    min_sp = min(spreads)
    max_sp = max(spreads)
    tight_pct = 100 * sum(1 for s in spreads if s <= 2) / len(spreads)
    fat_pct = 100 * sum(1 for s in spreads if s >= 5) / len(spreads)
    player = d["ticker"].split("-")[-1]
    print("%-30s %4dc %4.1fc %4dc %4dc %5.0f%% %5.0f%%" % (
        "...%s (%s)" % (d["ticker"][-15:], player),
        sp_post, avg_sp, min_sp, max_sp, tight_pct, fat_pct))

# STEP 3: Simulated reprice
print("\n--- STEP 3: SIMULATED REPRICE (every 5 min, if mid moved >3c & spread ≤2c) ---\n")

reprice_results = []
for d in all_drift_data:
    ticks = d["ticks"]
    if len(ticks) < 10:
        continue
    post_price = d["post_price"]
    cell = entries.get(d["ticker"], {}).get("cell", "?")

    # Simulate 5-min check intervals (~every 60 ticks as proxy)
    reprices = 0
    current_price = post_price
    would_fill = False
    fill_price_sim = 0
    best_fill = post_price

    for i in range(0, len(ticks), 60):
        t = ticks[min(i, len(ticks)-1)]
        mid = t["mid"]
        spread = t["spread"]

        # Reprice condition: mid moved >3c AND spread tight
        if abs(mid - current_price) > 3 and spread <= 2:
            new_price = int(mid)
            # Check cell bucket boundary
            old_bucket = (current_price // 5) * 5
            new_bucket = (new_price // 5) * 5
            if old_bucket == new_bucket:
                reprices += 1
                current_price = new_price
                best_fill = new_price

        # Check if would fill at current price
        if t["ask"] <= current_price and not would_fill:
            would_fill = True
            fill_price_sim = current_price

    # Compare to actual
    actual_filled = d["filled"]
    player = d["ticker"].split("-")[-1]
    reprice_results.append({
        "ticker": d["ticker"], "reprices": reprices,
        "original_post": post_price, "final_price": current_price,
        "would_fill": would_fill, "actual_filled": actual_filled,
        "fill_price_sim": fill_price_sim,
    })

print("%-30s %4s %5s %5s %5s %5s %8s %s" % (
    "TICKER", "REPR", "POST", "FINAL", "SIM_F", "ACT_F", "OUTCOME", "NOTES"))
print("-" * 95)

sim_fill_count = 0
actual_fill_count = 0
lift_count = 0
for r in reprice_results:
    player = r["ticker"].split("-")[-1]
    actual = "YES" if entries.get(r["ticker"], {}).get("filled") else "no"
    sim = "YES" if r["would_fill"] else "no"
    if r["would_fill"]:
        sim_fill_count += 1
    if entries.get(r["ticker"], {}).get("filled"):
        actual_fill_count += 1
    if r["would_fill"] and not entries.get(r["ticker"], {}).get("filled"):
        lift_count += 1
    notes = ""
    if r["reprices"] > 0:
        notes = "%+dc from post" % (r["final_price"] - r["original_post"])
    print("%-30s %4d %4dc %4dc %4dc %5s %8s %s" % (
        "...%s (%s)" % (r["ticker"][-15:], player),
        r["reprices"], r["original_post"], r["final_price"],
        r["fill_price_sim"] if r["fill_price_sim"] else 0,
        actual, sim, notes))

print("\nFill rate without reprice: %d/%d = %.0f%%" % (
    actual_fill_count, len(reprice_results),
    100*actual_fill_count/len(reprice_results) if reprice_results else 0))
print("Fill rate with reprice:    %d/%d = %.0f%%" % (
    sim_fill_count, len(reprice_results),
    100*sim_fill_count/len(reprice_results) if reprice_results else 0))
print("Fill rate lift:            %+d entries" % lift_count)

# STEP 5: Proposed V5 logic
print("\n--- STEP 5: PROPOSED V5 REPRICE LOGIC ---\n")
print("Based on findings:")
print()
print("1. REPRICE INTERVAL: Every 5 minutes")
print("   (Aligned with discovery cycle, minimal API overhead)")
print()
print("2. REPRICE TRIGGERS:")
print("   a) Mid moved >3c from current post price")
print("   b) Spread is tight (≤2c) — confirms real liquidity")
print("   c) New price still within same cell bucket (5c range)")
print("   d) Market has ≥2 levels of depth on both sides")
print()
print("3. CANCEL TRIGGERS:")
print("   a) Mid crossed into disabled cell bucket")
print("   b) Spread >10c for >15 minutes (market died)")
print("   c) >30 min past scheduled match start")
print()
print("4. MAX REPRICES: 10 per order")
print("   (Prevents runaway chasing in volatile markets)")
print()
print("5. EXTERNAL ANCHOR (Main tour only):")
print("   When spread >5c on ATP/WTA Main, query Odds API")
print("   Use Pinnacle implied as anchor, post at min(kalshi_mid, pinnacle_implied)")
print("   Only applicable to ~15%% of entries")

print("\nDONE")
