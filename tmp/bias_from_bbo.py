#!/usr/bin/env python3
"""
Quantify first_price bias using BBO data.
For each ticker in BBO file, compare:
- first BBO mid (what analyses currently use via historical_events first_price proxy)
- BBO mid at T-4h, T-2h, T-1h, T-15min before last observation
  (proxies for where bot would enter during pregame)
- VWAP-equivalent: average mid across late pregame snapshots

Only processes first 10M rows for speed (covers ~2 days of data).
"""
import gzip, csv, json, os
from collections import defaultdict
from datetime import datetime, timezone, timedelta

BASE_DIR = "/root/Omi-Workspace/arb-executor"
BBO_GZ = "/tmp/bbo_log_v4.csv.gz"
OUT_DIR = "/tmp/per_cell_verification"
ET = timezone(timedelta(hours=-4))

with open(os.path.join(BASE_DIR, "config/deploy_v4.json")) as f:
    cfg = json.load(f)
active_cells = cfg.get("active_cells", {})
ALL_CELLS = {}
for cell, params in active_cells.items():
    ALL_CELLS[cell] = params.get("exit_cents", 0)
DISABLED_EXITS = {
    "ATP_MAIN_underdog_40-44": 9, "ATP_CHALL_underdog_30-34": 15,
    "ATP_MAIN_leader_75-79": 14, "ATP_CHALL_underdog_25-29": 21,
    "ATP_MAIN_underdog_35-39": 12, "ATP_CHALL_leader_60-64": 6,
    "ATP_MAIN_leader_60-64": 15, "ATP_MAIN_underdog_25-29": 22,
    "ATP_CHALL_underdog_15-19": 31, "WTA_MAIN_leader_55-59": 10,
    "WTA_MAIN_underdog_40-44": 5, "WTA_MAIN_underdog_30-34": 16,
    "WTA_MAIN_underdog_35-39": 11, "ATP_MAIN_leader_55-59": 13,
    "ATP_MAIN_underdog_20-24": 25, "WTA_MAIN_leader_60-64": 8,
    "WTA_MAIN_underdog_15-19": 31, "WTA_MAIN_underdog_20-24": 22,
}
for cell, exit_c in DISABLED_EXITS.items():
    ALL_CELLS[cell] = exit_c

def classify_cell(tier, price):
    d = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, d, bs, bs + 4)

def get_tier(tk):
    if "KXATPMATCH" in tk and "CHALL" not in tk: return "ATP_MAIN"
    if "KXWTAMATCH" in tk and "CHALL" not in tk: return "WTA_MAIN"
    if "KXATPCHALL" in tk: return "ATP_CHALL"
    if "KXWTACHALL" in tk: return "WTA_CHALL"
    return None

# Stream BBO, collect per-ticker price paths (full file)
# Store: first_mid, mid at various time offsets from last observation
# Using inline tracking: per ticker, store first_mid and sample at percentiles of lifetime

print("Streaming BBO file (full)...", flush=True)
import time
start = time.time()

ticker_data = {}  # ticker -> {"first_mid", "first_bid", "samples": [(ts_str, mid, bid)], "last_ts_str"}

rows = 0
last_report = time.time()
with gzip.open(BBO_GZ, "rt") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        rows += 1
        if rows % 10000000 == 0:
            elapsed = time.time() - last_report
            rate = 10000000 / elapsed if elapsed else 0
            active = len(ticker_data)
            print("  %dM rows, %d tickers, %.0f/s" % (rows//1000000, active, rate), flush=True)
            last_report = time.time()

        if len(row) < 4: continue
        ts_str, tk, bid_s, ask_s = row[0], row[1], row[2], row[3]
        try:
            bid = int(float(bid_s))
            ask = int(float(ask_s))
        except: continue
        if bid <= 0 or ask >= 100 or bid >= ask: continue
        mid = (bid + ask) / 2.0

        if tk not in ticker_data:
            ticker_data[tk] = {
                "first_mid": mid, "first_bid": bid, "first_ask": ask,
                "first_ts": ts_str, "last_ts": ts_str, "last_mid": mid,
                "last_bid": bid, "count": 1,
                # Sample at sparse intervals to avoid memory explosion
                "samples": [(ts_str, mid, bid)],
                "next_sample": 100,  # sample every 100th row per ticker
            }
        else:
            td = ticker_data[tk]
            td["last_ts"] = ts_str
            td["last_mid"] = mid
            td["last_bid"] = bid
            td["count"] += 1
            td["next_sample"] -= 1
            if td["next_sample"] <= 0:
                td["samples"].append((ts_str, mid, bid))
                td["next_sample"] = 100
                # Cap samples at 200 per ticker
                if len(td["samples"]) > 200:
                    td["samples"] = td["samples"][-200:]

elapsed = time.time() - start
print("Done. %d rows, %d tickers, %.0f min" % (rows, len(ticker_data), elapsed/60))

# For each ticker: compute bias metrics
def parse_ts(ts_str):
    try:
        dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(tzinfo=ET)
        return dt.timestamp()
    except:
        return 0

print("Computing bias metrics...", flush=True)

results = []
for tk, td in ticker_data.items():
    tier = get_tier(tk)
    if not tier: continue
    if td["count"] < 50: continue

    first_mid = td["first_mid"]
    first_bid = td["first_bid"]
    cell = classify_cell(tier, first_mid)
    if cell not in ALL_CELLS: continue

    # Parse timestamps for samples
    first_epoch = parse_ts(td["first_ts"])
    last_epoch = parse_ts(td["last_ts"])
    if first_epoch == 0 or last_epoch == 0: continue

    total_dur = last_epoch - first_epoch
    if total_dur < 3600: continue  # skip < 1h events

    # Find mid at various time points before last observation
    # T-4h, T-2h, T-1h, T-15min
    targets = {
        "T_minus_4h": last_epoch - 4*3600,
        "T_minus_2h": last_epoch - 2*3600,
        "T_minus_1h": last_epoch - 1*3600,
        "T_minus_15m": last_epoch - 900,
    }

    sample_epochs = [(parse_ts(s[0]), s[1], s[2]) for s in td["samples"]]
    sample_epochs = [(e, m, b) for e, m, b in sample_epochs if e > 0]
    if not sample_epochs: continue

    found = {}
    for label, target_epoch in targets.items():
        # Find closest sample to target
        best = None
        best_dist = float("inf")
        for ep, m, b in sample_epochs:
            dist = abs(ep - target_epoch)
            if dist < best_dist:
                best_dist = dist
                best = (m, b, dist)
        if best and best[2] < 1800:  # within 30 min of target
            found[label] = best

    # Late pregame average: samples from T-4h to T-15min
    late_pregame = [(m, b) for ep, m, b in sample_epochs
                    if last_epoch - 4*3600 <= ep <= last_epoch - 900]
    avg_late_mid = sum(m for m, b in late_pregame) / len(late_pregame) if late_pregame else None
    avg_late_bid = sum(b for m, b in late_pregame) / len(late_pregame) if late_pregame else None

    r = {
        "ticker": tk, "cell": cell, "first_mid": first_mid, "first_bid": first_bid,
        "n_bbo_rows": td["count"], "duration_h": total_dur/3600,
    }
    for label in ["T_minus_4h", "T_minus_2h", "T_minus_1h", "T_minus_15m"]:
        if label in found:
            r[label+"_mid"] = found[label][0]
            r[label+"_bid"] = found[label][1]
        else:
            r[label+"_mid"] = None
            r[label+"_bid"] = None
    r["avg_late_pregame_mid"] = avg_late_mid
    r["avg_late_pregame_bid"] = avg_late_bid
    r["n_late_pregame_samples"] = len(late_pregame)
    results.append(r)

print("Results: %d tickers" % len(results))

# Write per-ticker CSV
with open(os.path.join(OUT_DIR, "entry_price_bias.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ticker","cell","first_mid","first_bid","n_bbo_rows","duration_h",
                "T_minus_4h_mid","T_minus_2h_mid","T_minus_1h_mid","T_minus_15m_mid",
                "T_minus_4h_bid","T_minus_2h_bid","T_minus_1h_bid","T_minus_15m_bid",
                "avg_late_pregame_mid","avg_late_pregame_bid","n_late_pregame_samples",
                "bias_first_vs_late_mid","bias_first_vs_T2h_mid"])
    for r in sorted(results, key=lambda x: x["cell"]):
        bias_late = (r["first_mid"] - r["avg_late_pregame_mid"]) if r["avg_late_pregame_mid"] else ""
        bias_t2h = (r["first_mid"] - r["T_minus_2h_mid"]) if r["T_minus_2h_mid"] else ""
        w.writerow([r["ticker"], r["cell"], "%.1f"%r["first_mid"], r["first_bid"],
                     r["n_bbo_rows"], "%.1f"%r["duration_h"],
                     "%.1f"%r["T_minus_4h_mid"] if r["T_minus_4h_mid"] else "",
                     "%.1f"%r["T_minus_2h_mid"] if r["T_minus_2h_mid"] else "",
                     "%.1f"%r["T_minus_1h_mid"] if r["T_minus_1h_mid"] else "",
                     "%.1f"%r["T_minus_15m_mid"] if r["T_minus_15m_mid"] else "",
                     r["T_minus_4h_bid"] if r["T_minus_4h_bid"] else "",
                     r["T_minus_2h_bid"] if r["T_minus_2h_bid"] else "",
                     r["T_minus_1h_bid"] if r["T_minus_1h_bid"] else "",
                     r["T_minus_15m_bid"] if r["T_minus_15m_bid"] else "",
                     "%.1f"%r["avg_late_pregame_mid"] if r["avg_late_pregame_mid"] else "",
                     "%.1f"%r["avg_late_pregame_bid"] if r["avg_late_pregame_bid"] else "",
                     r["n_late_pregame_samples"],
                     "%.1f"%bias_late if bias_late != "" else "",
                     "%.1f"%bias_t2h if bias_t2h != "" else ""])

# Per-cell summary
cell_biases = defaultdict(lambda: {"first_vs_late": [], "first_vs_t2h": []})
for r in results:
    if r["avg_late_pregame_mid"] is not None:
        cell_biases[r["cell"]]["first_vs_late"].append(r["first_mid"] - r["avg_late_pregame_mid"])
    if r["T_minus_2h_mid"] is not None:
        cell_biases[r["cell"]]["first_vs_t2h"].append(r["first_mid"] - r["T_minus_2h_mid"])

with open(os.path.join(OUT_DIR, "entry_price_bias_by_cell.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","N_late","mean_bias_first_vs_late_mid","stddev","median",
                "pct_within_3c","pct_within_5c",
                "N_T2h","mean_bias_first_vs_T2h","stddev_T2h"])
    for cell in sorted(cell_biases.keys()):
        d = cell_biases[cell]
        bl = d["first_vs_late"]
        bt = d["first_vs_t2h"]
        if len(bl) < 3: continue
        mean_l = sum(bl)/len(bl)
        std_l = (sum((x-mean_l)**2 for x in bl)/len(bl))**0.5
        med_l = sorted(bl)[len(bl)//2]
        w3 = sum(1 for x in bl if abs(x) <= 3)/len(bl)*100
        w5 = sum(1 for x in bl if abs(x) <= 5)/len(bl)*100
        mean_t = sum(bt)/len(bt) if bt else 0
        std_t = (sum((x-mean_t)**2 for x in bt)/len(bt))**0.5 if len(bt)>1 else 0
        w.writerow([cell, len(bl), "%.1f"%mean_l, "%.1f"%std_l, "%.1f"%med_l,
                     "%.0f"%w3, "%.0f"%w5, len(bt), "%.1f"%mean_t, "%.1f"%std_t])

# Print summary
print("\n=== OVERALL BIAS SUMMARY ===")
all_late = []
all_t2h = []
for d in cell_biases.values():
    all_late.extend(d["first_vs_late"])
    all_t2h.extend(d["first_vs_t2h"])

if all_late:
    avg = sum(all_late)/len(all_late)
    std = (sum((x-avg)**2 for x in all_late)/len(all_late))**0.5
    med = sorted(all_late)[len(all_late)//2]
    print("first_mid vs avg_late_pregame_mid: N=%d, mean=%+.1fc, std=%.1fc, median=%+.1fc" % (
        len(all_late), avg, std, med))
    print("  within 3c: %.0f%%, within 5c: %.0f%%" % (
        sum(1 for x in all_late if abs(x)<=3)/len(all_late)*100,
        sum(1 for x in all_late if abs(x)<=5)/len(all_late)*100))

if all_t2h:
    avg = sum(all_t2h)/len(all_t2h)
    std = (sum((x-avg)**2 for x in all_t2h)/len(all_t2h))**0.5
    print("first_mid vs T-2h mid: N=%d, mean=%+.1fc, std=%.1fc" % (len(all_t2h), avg, std))

print("\nDone. Files in %s/" % OUT_DIR)
