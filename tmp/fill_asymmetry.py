#!/usr/bin/env python3
"""
Fill asymmetry analysis: correlate live fills with kalshi_price_snapshots
to determine price trajectory before fill.

Uses kalshi_price_snapshots (5-min BBO, Apr 21-28) for pre-fill price path.
"""
import sqlite3, json, csv, os, glob
from collections import defaultdict
from datetime import datetime, timezone, timedelta

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/per_cell_verification"
ET = timezone(timedelta(hours=-4))

# Load live fills
fills = []
for lf in sorted(glob.glob(os.path.join(BASE_DIR, "logs/live_v3_*.jsonl"))):
    with open(lf) as f:
        for line in f:
            try:
                d = json.loads(line.strip())
                if d.get("event") == "entry_filled":
                    det = d.get("details", {})
                    fills.append({
                        "ticker": d.get("ticker", ""),
                        "cell": det.get("cell", ""),
                        "fill_price": det.get("fill_price", 0),
                        "ts": d.get("ts", ""),
                        "ts_epoch": d.get("ts_epoch", 0),
                        "direction": det.get("direction", ""),
                    })
            except:
                pass

print("Live fills loaded: %d" % len(fills))
print("First: %s" % fills[0]["ts"] if fills else "none")
print("Last: %s" % fills[-1]["ts"] if fills else "none")

# Load snapshot data indexed by ticker
conn = sqlite3.connect(os.path.join(BASE_DIR, "tennis.db"))
cur = conn.cursor()

# Build per-ticker snapshot series
cur.execute("""SELECT ticker, polled_at, bid_cents, ask_cents, last_cents
    FROM kalshi_price_snapshots
    WHERE (ticker LIKE 'KXATP%' OR ticker LIKE 'KXWTA%')
    AND bid_cents > 0 AND ask_cents > 0
    ORDER BY ticker, polled_at""")

ticker_snaps = defaultdict(list)
for tk, polled, bid, ask, last in cur.fetchall():
    try:
        dt = datetime.strptime(polled, "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(tzinfo=ET)
        epoch = dt.timestamp()
    except:
        continue
    mid = (bid + ask) / 2.0
    ticker_snaps[tk].append({"epoch": epoch, "mid": mid, "bid": bid, "ask": ask, "spread": ask-bid})

conn.close()
print("Snapshot tickers: %d" % len(ticker_snaps))

# For each fill, find 30-min price path before fill
results = []
for f in fills:
    tk = f["ticker"]
    if tk not in ticker_snaps:
        continue

    snaps = ticker_snaps[tk]
    fill_epoch = f["ts_epoch"]
    if fill_epoch == 0:
        # Parse ts string
        try:
            # Format: "2026-04-24 02:21:26 PM ET"
            ts = f["ts"].replace(" ET", "").replace(" AM", " AM").replace(" PM", " PM")
            dt = datetime.strptime(ts, "%Y-%m-%d %I:%M:%S %p")
            dt = dt.replace(tzinfo=ET)
            fill_epoch = dt.timestamp()
        except:
            continue

    # Find snapshot closest to fill time
    closest_at_fill = None
    closest_dist = float("inf")
    for s in snaps:
        d = abs(s["epoch"] - fill_epoch)
        if d < closest_dist:
            closest_dist = d
            closest_at_fill = s

    if not closest_at_fill or closest_dist > 600:  # within 10 min
        continue

    # Find snapshot ~30 min before fill
    target_30 = fill_epoch - 1800
    closest_30 = None
    closest_30_dist = float("inf")
    for s in snaps:
        d = abs(s["epoch"] - target_30)
        if d < closest_30_dist:
            closest_30_dist = d
            closest_30 = s

    # All snapshots in 30-min window before fill
    window_snaps = [s for s in snaps if fill_epoch - 1800 <= s["epoch"] <= fill_epoch]

    # Determine trend direction
    if len(window_snaps) >= 3:
        mids = [s["mid"] for s in window_snaps]
        # Count sequential up vs down moves
        ups = sum(1 for i in range(1, len(mids)) if mids[i] > mids[i-1])
        downs = sum(1 for i in range(1, len(mids)) if mids[i] < mids[i-1])
        total_moves = ups + downs
        if total_moves == 0:
            direction = "FLAT"
        elif ups > 0.65 * total_moves:
            direction = "TRENDING_UP"
        elif downs > 0.65 * total_moves:
            direction = "TRENDING_DOWN"
        else:
            direction = "OSCILLATING"

        price_change = mids[-1] - mids[0]
        max_mid = max(mids)
        min_mid = min(mids)
        oscillation_range = max_mid - min_mid
    else:
        direction = "INSUFFICIENT_DATA"
        price_change = 0
        oscillation_range = 0

    # Check if inverse side also filled
    # Inverse ticker: same event, other side
    parts = tk.rsplit("-", 1)
    if len(parts) == 2:
        evt_tk = parts[0]
        # Find other fills with same event ticker
        paired = any(of["ticker"].startswith(evt_tk) and of["ticker"] != tk for of in fills)
    else:
        paired = False

    side = f.get("direction", "")
    if not side:
        side = "leader" if "leader" in f["cell"] else "underdog" if "underdog" in f["cell"] else "?"

    results.append({
        "ticker": tk,
        "cell": f["cell"],
        "side": side,
        "fill_price": f["fill_price"],
        "fill_ts": f["ts"],
        "bid_at_fill": closest_at_fill["bid"],
        "ask_at_fill": closest_at_fill["ask"],
        "spread_at_fill": closest_at_fill["spread"],
        "mid_at_fill": closest_at_fill["mid"],
        "mid_30min_before": closest_30["mid"] if closest_30 and closest_30_dist < 2400 else None,
        "price_change_30min": price_change,
        "direction_30min": direction,
        "oscillation_range": oscillation_range,
        "n_window_snaps": len(window_snaps),
        "paired": paired,
    })

print("Results with BBO context: %d" % len(results))

# Write per-fill CSV
with open(os.path.join(OUT_DIR, "fill_asymmetry_per_fill.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ticker","cell","side","fill_price","fill_ts",
                "bid_at_fill","ask_at_fill","spread_at_fill","mid_at_fill",
                "mid_30min_before","price_change_30min","direction_30min",
                "oscillation_range","n_window_snaps","paired"])
    for r in results:
        w.writerow([r["ticker"], r["cell"], r["side"], r["fill_price"], r["fill_ts"],
                     r["bid_at_fill"], r["ask_at_fill"], r["spread_at_fill"],
                     "%.1f" % r["mid_at_fill"],
                     "%.1f" % r["mid_30min_before"] if r["mid_30min_before"] else "",
                     "%.1f" % r["price_change_30min"],
                     r["direction_30min"], "%.1f" % r["oscillation_range"],
                     r["n_window_snaps"], r["paired"]])

# Summary by side
print("\n=== SUMMARY BY SIDE ===")
print("| Side | N fills | Trending UP | Trending DOWN | Oscillating | Flat | Insuff | Avg spread | Paired % |")
print("|---|---|---|---|---|---|---|---|---|")

for side in ["leader", "underdog"]:
    subset = [r for r in results if r["side"] == side]
    n = len(subset)
    if n == 0: continue
    t_up = sum(1 for r in subset if r["direction_30min"] == "TRENDING_UP")
    t_down = sum(1 for r in subset if r["direction_30min"] == "TRENDING_DOWN")
    osc = sum(1 for r in subset if r["direction_30min"] == "OSCILLATING")
    flat = sum(1 for r in subset if r["direction_30min"] == "FLAT")
    insuff = sum(1 for r in subset if r["direction_30min"] == "INSUFFICIENT_DATA")
    avg_spread = sum(r["spread_at_fill"] for r in subset) / n
    paired = sum(1 for r in subset if r["paired"]) / n * 100
    print("| %s | %d | %d (%.0f%%) | %d (%.0f%%) | %d (%.0f%%) | %d (%.0f%%) | %d | %.1fc | %.0f%% |" % (
        side, n, t_up, t_up/n*100, t_down, t_down/n*100,
        osc, osc/n*100, flat, flat/n*100, insuff, avg_spread, paired))

# Also: avg price change by side
print("\n=== PRICE TRAJECTORY BY SIDE ===")
for side in ["leader", "underdog"]:
    subset = [r for r in results if r["side"] == side and r["direction_30min"] != "INSUFFICIENT_DATA"]
    if not subset: continue
    changes = [r["price_change_30min"] for r in subset]
    osc_ranges = [r["oscillation_range"] for r in subset]
    avg_change = sum(changes) / len(changes)
    avg_osc = sum(osc_ranges) / len(osc_ranges)
    print("%s (N=%d):" % (side, len(subset)))
    print("  Avg price change in 30min before fill: %+.1fc" % avg_change)
    print("  Avg oscillation range in 30min: %.1fc" % avg_osc)
    # Directional breakdown
    up_changes = [c for c in changes if c > 0]
    down_changes = [c for c in changes if c < 0]
    print("  Fills after price ROSE: %d (avg rise: +%.1fc)" % (len(up_changes), sum(up_changes)/len(up_changes) if up_changes else 0))
    print("  Fills after price FELL: %d (avg fall: %.1fc)" % (len(down_changes), sum(down_changes)/len(down_changes) if down_changes else 0))

# Write summary CSV
with open(os.path.join(OUT_DIR, "fill_asymmetry_summary.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["side","N","pct_trending_up","pct_trending_down","pct_oscillating",
                "pct_flat","avg_spread","avg_price_change_30min","avg_osc_range","paired_pct"])
    for side in ["leader", "underdog"]:
        subset = [r for r in results if r["side"] == side]
        n = len(subset)
        if n == 0: continue
        valid = [r for r in subset if r["direction_30min"] != "INSUFFICIENT_DATA"]
        nv = len(valid)
        t_up = sum(1 for r in valid if r["direction_30min"] == "TRENDING_UP")
        t_down = sum(1 for r in valid if r["direction_30min"] == "TRENDING_DOWN")
        osc = sum(1 for r in valid if r["direction_30min"] == "OSCILLATING")
        flat = sum(1 for r in valid if r["direction_30min"] == "FLAT")
        avg_spread = sum(r["spread_at_fill"] for r in subset) / n
        avg_change = sum(r["price_change_30min"] for r in valid) / nv if nv else 0
        avg_osc = sum(r["oscillation_range"] for r in valid) / nv if nv else 0
        paired = sum(1 for r in subset if r["paired"]) / n * 100
        w.writerow([side, n, "%.1f"%(t_up/nv*100) if nv else "",
                     "%.1f"%(t_down/nv*100) if nv else "",
                     "%.1f"%(osc/nv*100) if nv else "",
                     "%.1f"%(flat/nv*100) if nv else "",
                     "%.1f"%avg_spread, "%.1f"%avg_change, "%.1f"%avg_osc, "%.0f"%paired])

print("\nWritten: fill_asymmetry_per_fill.csv, fill_asymmetry_summary.csv")
