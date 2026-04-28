#!/usr/bin/env python3
"""
DCA Time-Ordered Analysis v3 — Inline state-machine streaming parse of gzipped BBO.

Architecture: Single-pass with per-ticker state machines. Each (ticker, trigger, combo)
tracks its own DCA state as BBO rows stream in. No buffering needed — O(1) memory per ticker.
Memory target: <100MB peak.
Input: /tmp/bbo_log_v4.csv.gz (515M rows)
Output: /tmp/validation5/per_cell_dca_summary.csv
"""

import gzip, csv, json, os, sys, time, resource
from collections import defaultdict
from datetime import datetime, timezone, timedelta

BASE_DIR = "/root/Omi-Workspace/arb-executor"
BBO_GZ = "/tmp/bbo_log_v4.csv.gz"
OUTPUT_DIR = "/tmp/validation5"
os.makedirs(OUTPUT_DIR, exist_ok=True)

ET = timezone(timedelta(hours=-4))

# Load config
with open(os.path.join(BASE_DIR, "config/deploy_v4.json")) as f:
    cfg = json.load(f)
active_cells = cfg.get("active_cells", {})

# Build ALL cells to test (active + disabled for re-enable analysis)
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

TRIGGERS = [3, 5, 7, 10, 15, 20, 25]

def get_tier(tk):
    if "KXATPMATCH" in tk and "CHALL" not in tk: return "ATP_MAIN"
    if "KXWTAMATCH" in tk and "CHALL" not in tk: return "WTA_MAIN"
    if "KXATPCHALL" in tk: return "ATP_CHALL"
    if "KXWTACHALL" in tk: return "WTA_CHALL"
    return None

def classify_cell(tier, price):
    direction = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, direction, bs, bs + 4)

_ts_cache = {}
def parse_ts_cached(ts_str):
    """Parse timestamp to epoch. Cached — only called during stale sweeps."""
    v = _ts_cache.get(ts_str)
    if v is not None:
        return v
    try:
        y, mo, d = int(ts_str[0:4]), int(ts_str[5:7]), int(ts_str[8:10])
        h, mi, s = int(ts_str[11:13]), int(ts_str[14:16]), int(ts_str[17:19])
        dt = datetime(y, mo, d, h, mi, s, tzinfo=ET)
        v = dt.timestamp()
    except:
        v = 0
    if len(_ts_cache) < 200000:
        _ts_cache[ts_str] = v
    return v

# Per-cell aggregator
agg = defaultdict(lambda: {
    "total": 0, "scalp_pre": 0, "dca_fires": 0, "dca_wins": 0,
    "dca_knife": 0, "no_opp": 0, "pnl_sum": 0,
})

# State: WAIT=0 (watching for scalp or DCA trigger), FIRED=1 (DCA fired, watching for recovery), DONE=2
WAIT, FIRED, DONE = 0, 1, 2

# Per-ticker state machines
# ticker_states[tk] = {
#   "cell": str, "P": int, "n_rows": int,
#   "sims": {(trigger, combo): {"state": 0/1/2, "outcome": str, "exit_target": float, ...}, ...}
# }
ticker_states = {}
ticker_last_seen = {}
tickers_processed = 0

def init_ticker(tk, bid, ask):
    """Initialize DCA state machines for a new ticker."""
    mid = (bid + ask) / 2.0
    tier = get_tier(tk)
    if tier is None:
        return None
    cell = classify_cell(tier, mid)
    if cell not in ALL_CELLS:
        return None
    exit_c = ALL_CELLS[cell]
    if exit_c == 0:
        return None

    P = bid  # maker fills at bid
    sims = {}
    for trigger in TRIGGERS:
        dca_price = P - trigger
        if dca_price < 5:
            continue
        target_A = min(99, P + exit_c)
        new_avg = (10 * P + 5 * dca_price) / 15.0
        target_B = min(99, new_avg + exit_c)

        for combo_name, exit_target in [("A", target_A), ("B", target_B)]:
            sims[(trigger, combo_name)] = {
                "state": WAIT,
                "target_A": target_A,  # pre-DCA scalp target (always original)
                "dca_price": dca_price,
                "exit_target": exit_target,
                "outcome": None,
            }

    if not sims:
        return None

    return {"cell": cell, "P": P, "n_rows": 1, "sims": sims}

def process_row(state, bid, ask):
    """Process one BBO row for all active simulations of a ticker."""
    mid = (bid + ask) / 2.0
    state["n_rows"] += 1

    for key, sim in state["sims"].items():
        if sim["state"] == DONE:
            continue
        if sim["state"] == WAIT:
            if mid >= sim["target_A"]:
                sim["state"] = DONE
                sim["outcome"] = "scalp_pre"
            elif mid <= sim["dca_price"]:
                sim["state"] = FIRED
        elif sim["state"] == FIRED:
            if mid >= sim["exit_target"]:
                sim["state"] = DONE
                sim["outcome"] = "dca_win"

def finalize_ticker(state):
    """Record results for a completed ticker."""
    cell = state["cell"]
    P = state["P"]
    n_rows = state["n_rows"]

    if n_rows < 10:
        return

    for (trigger, combo), sim in state["sims"].items():
        key = (cell, trigger, combo)
        agg[key]["total"] += 1

        dca_price = sim["dca_price"]
        exit_target = sim["exit_target"]

        if sim["outcome"] == "scalp_pre":
            agg[key]["scalp_pre"] += 1
        elif sim["state"] == FIRED and sim["outcome"] is None:
            # DCA fired but never recovered
            agg[key]["dca_knife"] += 1
            agg[key]["dca_fires"] += 1
            pnl = -(10 * P + 5 * dca_price)
            agg[key]["pnl_sum"] += pnl
        elif sim["outcome"] == "dca_win":
            agg[key]["dca_wins"] += 1
            agg[key]["dca_fires"] += 1
            pnl = 10 * (exit_target - P) + 5 * (exit_target - dca_price)
            agg[key]["pnl_sum"] += pnl
        else:
            # Never hit DCA trigger or scalp target
            agg[key]["no_opp"] += 1

# Main streaming loop
print("[%s] Starting streaming parse of %s" % (
    datetime.now(ET).strftime("%I:%M %p"), BBO_GZ), flush=True)

rows_processed = 0
start_time = time.time()
last_report = time.time()

with gzip.open(BBO_GZ, "rt") as f:
    reader = csv.reader(f)
    header = next(reader)

    for row in reader:
        rows_processed += 1

        if rows_processed % 5000000 == 0:
            elapsed = time.time() - last_report
            mem_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
            active_tickers = len(ticker_states)
            rate = 5000000 / elapsed if elapsed > 0 else 0
            eta_min = (515000000 - rows_processed) / rate / 60 if rate > 0 else 0
            print("[%s] %dM rows, %d active tickers, %d processed, %.0f rows/s, ~%.0f min remaining, %.0f MB" % (
                datetime.now(ET).strftime("%I:%M %p"),
                rows_processed // 1000000, active_tickers, tickers_processed,
                rate, eta_min, mem_mb), flush=True)
            last_report = time.time()

        if len(row) < 4:
            continue

        ts_str, tk, bid_s, ask_s = row[0], row[1], row[2], row[3]

        try:
            bid = int(float(bid_s))
            ask = int(float(ask_s))
        except:
            continue

        if bid <= 0 or ask >= 100 or bid >= ask:
            continue

        # Initialize or update ticker state
        if tk not in ticker_states:
            state = init_ticker(tk, bid, ask)
            if state is None:
                ticker_states[tk] = None  # mark as non-tennis/non-cell
            else:
                ticker_states[tk] = state
                ticker_last_seen[tk] = ts_str
        elif ticker_states[tk] is not None:
            process_row(ticker_states[tk], bid, ask)
            ticker_last_seen[tk] = ts_str

        # Sweep stale tickers every 50000 rows (parse timestamps only here)
        if rows_processed % 50000 == 0:
            cur_epoch = parse_ts_cached(ts_str)
            stale = [t for t, last_ts in ticker_last_seen.items()
                     if cur_epoch - parse_ts_cached(last_ts) > 300]
            for t in stale:
                if ticker_states.get(t) is not None:
                    finalize_ticker(ticker_states[t])
                del ticker_states[t]
                del ticker_last_seen[t]
                tickers_processed += 1

# Flush remaining tickers
print("[%s] Flushing %d remaining tickers..." % (
    datetime.now(ET).strftime("%I:%M %p"), len(ticker_states)), flush=True)

for tk, state in ticker_states.items():
    if state is not None:
        finalize_ticker(state)
    tickers_processed += 1

total_time = time.time() - start_time
print("[%s] Complete. %d rows, %d tickers, %.0f minutes." % (
    datetime.now(ET).strftime("%I:%M %p"), rows_processed, tickers_processed,
    total_time / 60), flush=True)

# Write output
output_file = os.path.join(OUTPUT_DIR, "per_cell_dca_summary.csv")
with open(output_file, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["cell", "trigger", "combo", "is_active", "total", "scalp_pre",
                      "dca_fires", "dca_wins", "dca_knife", "no_opp",
                      "fire_rate_pct", "win_rate_pct", "dca_ev_per_fire_c", "cell_roi_delta_pct"])

    for (cell, trigger, combo), data in sorted(agg.items()):
        n = data["total"]
        fires = data["dca_fires"]
        wins = data["dca_wins"]

        parts = cell.split("_")
        bucket = parts[-1]
        lo, hi = int(bucket.split("-")[0]), int(bucket.split("-")[1])
        avg_entry = (lo + hi) / 2.0

        fire_rate = fires / n * 100 if n else 0
        win_rate = wins / fires * 100 if fires else 0
        ev_per_fire = data["pnl_sum"] / fires if fires else 0
        roi_delta = data["pnl_sum"] / (n * avg_entry * 10) * 100 if n * avg_entry else 0
        is_active = cell in active_cells

        writer.writerow([cell, trigger, combo, is_active, n, data["scalp_pre"],
                          fires, wins, data["dca_knife"], data["no_opp"],
                          "%.1f" % fire_rate, "%.1f" % win_rate,
                          "%.1f" % ev_per_fire, "%.2f" % roi_delta])

# Print summary
print("\n" + "=" * 70)
print("=== PER-CELL BEST DCA CONFIG (TIME-ORDERED) ===\n")
print("| Cell | Active? | Best config | N | Fires | Win% | ROI delta | Rec |")
print("|---|---|---|---|---|---|---|---|")

for cell in sorted(ALL_CELLS.keys()):
    best_roi = -999
    best_key = None
    best_data = None

    for (c, t, s), data in agg.items():
        if c != cell or data["total"] < 10:
            continue
        parts = cell.split("_")
        bucket = parts[-1]
        lo, hi = int(bucket.split("-")[0]), int(bucket.split("-")[1])
        avg_entry = (lo + hi) / 2.0
        roi = data["pnl_sum"] / (data["total"] * avg_entry * 10) * 100 if data["total"] else 0
        if roi > best_roi:
            best_roi = roi
            best_key = (t, s)
            best_data = data

    is_active = cell in active_cells
    if best_key and best_data and best_data["dca_fires"] > 0:
        fires = best_data["dca_fires"]
        wins = best_data["dca_wins"]
        wr = wins / fires * 100 if fires else 0
        rec = "ENABLE" if best_roi > 3 and best_data["total"] >= 20 else "TEST" if best_roi > 0 else "DISABLE"
        print("| %s | %s | -%dc/%s | %d | %d | %.0f%% | %+.1f%% | %s |" % (
            cell, "YES" if is_active else "no",
            best_key[0], best_key[1], best_data["total"], fires, wr, best_roi, rec))

print("\nOutput: %s" % output_file)
print("Methodology: %s" % os.path.join(OUTPUT_DIR, "methodology_v3.txt"))

# Write methodology
with open(os.path.join(OUTPUT_DIR, "methodology_v3.txt"), "w") as f:
    f.write("DCA Time-Ordered Analysis v3\n")
    f.write("============================\n\n")
    f.write("Input: %s (515M rows, gzipped)\n" % BBO_GZ)
    f.write("Date range: Mar 20 - Apr 17, 2026\n")
    f.write("Rows processed: %d\n" % rows_processed)
    f.write("Tickers processed: %d\n" % tickers_processed)
    f.write("Runtime: %.0f minutes\n" % (total_time / 60))
    f.write("Peak memory: %.0f MB\n" % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))
    f.write("\nCells tested: %d (active) + %d (disabled)\n" % (len(active_cells), len(DISABLED_EXITS)))
    f.write("Triggers: %s\n" % TRIGGERS)
    f.write("Combos: A (original exit), B (recalc avg+exit)\n")
    f.write("\nArchitecture: Inline state machine (no buffering)\n")
    f.write("  - Each (ticker, trigger, combo) has its own state: WAIT/FIRED/DONE\n")
    f.write("  - State transitions happen as BBO rows stream in\n")
    f.write("  - O(1) memory per ticker (no price history stored)\n")
    f.write("  - Stale tickers finalized after 5 min of inactivity\n")
    f.write("\nTime-ordering: ENFORCED\n")
    f.write("  1. Process BBO rows in chronological order per ticker\n")
    f.write("  2. WAIT state: if mid >= target_A → SCALP (done), if mid <= dca_price → FIRED\n")
    f.write("  3. FIRED state: if mid >= exit_target → DCA_WIN (done)\n")
    f.write("  4. End of ticker in FIRED state → DCA_KNIFE\n")
    f.write("  5. End of ticker in WAIT state → NO_OPPORTUNITY\n")
    f.write("  6. Entry price = first bid (maker fill)\n")
