#!/usr/bin/env python3
"""
DCA Event-Aware Analysis — Single-pass BBO parse tracking reaction events.

Instead of uniform trigger grid, identifies natural price reaction events
(Set 1 loss = sustained 20c+ drop) and analyzes DCA at event-matched depths.

Architecture: Inline state machine per ticker. Each ticker tracks:
- Entry price, cell classification
- Running max mid, drawdown tracking
- "Reaction event" detection (sustained drop from running max)
- DCA simulation at event-matched depths per cell
- Timing data for event analysis
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

# Event-matched trigger depths by entry price range
TRIGGER_MAP = {
    (5, 15):   [3, 5, 7],
    (15, 30):  [5, 10, 15],
    (30, 50):  [10, 15, 20, 25],
    (50, 60):  [15, 20, 25, 30],
    (60, 70):  [20, 25, 30, 35],
    (70, 80):  [25, 30, 35, 40],
    (80, 90):  [25, 30, 35, 40],
}

def get_triggers_for_price(price):
    for (lo, hi), triggers in TRIGGER_MAP.items():
        if lo <= price < hi:
            return triggers
    return []

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

# === AGGREGATORS ===

# Task 1: Per-cell reaction depth distribution
# reaction_depths[cell] = list of (entry_mid, max_drawdown_from_entry, max_drawdown_from_running_max)
reaction_depths = defaultdict(list)

# Task 2: Recovery after reaction
# reaction_recovery[cell] = list of {entry, drop_to, recovered_to_entry, recovered_to_exit, final_price}
reaction_recovery = defaultdict(list)

# Task 3: DCA simulation at event-matched depths
WAIT, FIRED, DONE = 0, 1, 2
dca_agg = defaultdict(lambda: {
    "total": 0, "scalp_pre": 0, "dca_fires": 0, "dca_wins": 0,
    "dca_knife": 0, "no_opp": 0, "pnl_sum": 0,
})

# Task 5: DCA timing data
# dca_timing = list of {cell, trigger, combo, entry_ts, fire_ts, win_ts, hours_to_fire, hours_to_win}
dca_timing = []

# Task 7: True opportunity space
# opp_space[cell] = {total, drop_20pct, drop_20pct_recover, ...}
opp_space = defaultdict(lambda: {"total": 0, "drop_20pct": 0, "drop_20pct_recover": 0})


# === PER-TICKER STATE ===

def init_ticker(tk, bid, ask, ts_str):
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

    P = bid  # entry at bid (maker fill)
    triggers = get_triggers_for_price(mid)

    # DCA state machines
    sims = {}
    for trigger in triggers:
        dca_price = P - trigger
        if dca_price < 5:
            continue
        target_A = min(99, P + exit_c)
        new_avg = (10 * P + 5 * dca_price) / 15.0
        target_B = min(99, new_avg + exit_c)

        for combo_name, exit_target in [("A", target_A), ("B", target_B)]:
            sims[(trigger, combo_name)] = {
                "state": WAIT,
                "target_A": target_A,
                "dca_price": dca_price,
                "exit_target": exit_target,
                "outcome": None,
                "fire_ts": None,
                "win_ts": None,
            }

    return {
        "cell": cell, "P": P, "entry_mid": mid, "exit_c": exit_c,
        "n_rows": 1, "entry_ts": ts_str,
        "running_max": mid, "running_min": mid,
        "max_drawdown_from_entry": 0,
        "max_drawdown_from_peak": 0,
        "reaction_detected": False,
        "reaction_depth": 0,
        "reaction_min": mid,
        "post_reaction_max": 0,
        "last_mid": mid,
        "sims": sims,
    }


def process_row(state, bid, ask, ts_str):
    mid = (bid + ask) / 2.0
    state["n_rows"] += 1
    state["last_mid"] = mid

    # Track running max/min
    if mid > state["running_max"]:
        state["running_max"] = mid
    if mid < state["running_min"]:
        state["running_min"] = mid

    # Drawdown tracking
    dd_from_entry = state["entry_mid"] - mid
    dd_from_peak = state["running_max"] - mid

    if dd_from_entry > state["max_drawdown_from_entry"]:
        state["max_drawdown_from_entry"] = dd_from_entry
    if dd_from_peak > state["max_drawdown_from_peak"]:
        state["max_drawdown_from_peak"] = dd_from_peak

    # Reaction event detection: sustained 15c+ drop from entry
    # (We use 15c instead of 20c to capture borderline events too)
    if not state["reaction_detected"] and dd_from_entry >= 15:
        state["reaction_detected"] = True
        state["reaction_depth"] = dd_from_entry
        state["reaction_min"] = mid

    # Track post-reaction behavior
    if state["reaction_detected"]:
        if mid < state["reaction_min"]:
            state["reaction_min"] = mid
            state["reaction_depth"] = state["entry_mid"] - mid
        if mid > state["post_reaction_max"]:
            state["post_reaction_max"] = mid

    # DCA state machines
    for key, sim in state["sims"].items():
        if sim["state"] == DONE:
            continue
        if sim["state"] == WAIT:
            if mid >= sim["target_A"]:
                sim["state"] = DONE
                sim["outcome"] = "scalp_pre"
            elif mid <= sim["dca_price"]:
                sim["state"] = FIRED
                sim["fire_ts"] = ts_str
        elif sim["state"] == FIRED:
            if mid >= sim["exit_target"]:
                sim["state"] = DONE
                sim["outcome"] = "dca_win"
                sim["win_ts"] = ts_str


def finalize_ticker(state):
    cell = state["cell"]
    P = state["P"]
    entry_mid = state["entry_mid"]
    exit_c = state["exit_c"]
    n_rows = state["n_rows"]

    if n_rows < 10:
        return

    # Task 1: Record reaction depth
    reaction_depths[cell].append((
        entry_mid,
        state["max_drawdown_from_entry"],
        state["max_drawdown_from_peak"],
    ))

    # Task 2: Recovery data for reaction events
    if state["reaction_detected"]:
        reaction_min = state["reaction_min"]
        post_max = state["post_reaction_max"]
        recovered_to_entry = post_max >= entry_mid
        recovered_to_exit = post_max >= min(99, entry_mid + exit_c)
        reaction_recovery[cell].append({
            "entry": entry_mid,
            "reaction_min": reaction_min,
            "depth": state["reaction_depth"],
            "post_max": post_max,
            "recovered_to_entry": recovered_to_entry,
            "recovered_to_exit": recovered_to_exit,
            "final_mid": state["last_mid"],
        })

    # Task 7: Opportunity space (20% relative drop)
    drop_threshold = entry_mid * 0.20
    drop_abs = state["max_drawdown_from_entry"]
    opp_space[cell]["total"] += 1
    if drop_abs >= drop_threshold:
        opp_space[cell]["drop_20pct"] += 1
        # Did it recover after the drop?
        # We check post_reaction_max vs entry — but only if reaction was detected
        if state["reaction_detected"] and state["post_reaction_max"] >= entry_mid:
            opp_space[cell]["drop_20pct_recover"] += 1

    # Task 3: DCA results
    for (trigger, combo), sim in state["sims"].items():
        key = (cell, trigger, combo)
        dca_agg[key]["total"] += 1

        dca_price = sim["dca_price"]
        exit_target = sim["exit_target"]

        if sim["outcome"] == "scalp_pre":
            dca_agg[key]["scalp_pre"] += 1
        elif sim["state"] == FIRED and sim["outcome"] is None:
            dca_agg[key]["dca_knife"] += 1
            dca_agg[key]["dca_fires"] += 1
            pnl = -(10 * P + 5 * dca_price)
            dca_agg[key]["pnl_sum"] += pnl
        elif sim["outcome"] == "dca_win":
            dca_agg[key]["dca_wins"] += 1
            dca_agg[key]["dca_fires"] += 1
            pnl = 10 * (exit_target - P) + 5 * (exit_target - dca_price)
            dca_agg[key]["pnl_sum"] += pnl

            # Task 5: Timing for DCA wins
            if sim["fire_ts"] and sim["win_ts"]:
                fire_epoch = parse_ts_cached(sim["fire_ts"])
                win_epoch = parse_ts_cached(sim["win_ts"])
                entry_epoch = parse_ts_cached(state["entry_ts"])
                if fire_epoch > 0 and win_epoch > 0 and entry_epoch > 0:
                    dca_timing.append({
                        "cell": cell,
                        "trigger": trigger,
                        "combo": combo,
                        "hours_entry_to_fire": (fire_epoch - entry_epoch) / 3600,
                        "hours_fire_to_win": (win_epoch - fire_epoch) / 3600,
                        "hours_entry_to_win": (win_epoch - entry_epoch) / 3600,
                    })
        else:
            dca_agg[key]["no_opp"] += 1


# === MAIN STREAMING LOOP ===

print("[%s] Starting event-aware DCA analysis of %s" % (
    datetime.now(ET).strftime("%I:%M %p"), BBO_GZ), flush=True)

ticker_states = {}
ticker_last_seen = {}
tickers_processed = 0
rows_processed = 0
start_time = time.time()
last_report = time.time()

with gzip.open(BBO_GZ, "rt") as f:
    reader = csv.reader(f)
    header = next(reader)

    for row in reader:
        rows_processed += 1
        if rows_processed >= 5000000: break

        if rows_processed % 5000000 == 0:
            elapsed = time.time() - last_report
            mem_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
            active = len(ticker_states)
            rate = 5000000 / elapsed if elapsed > 0 else 0
            eta = (515000000 - rows_processed) / rate / 60 if rate > 0 else 0
            print("[%s] %dM rows, %d active, %d done, %.0f/s, ~%.0f min left, %.0f MB" % (
                datetime.now(ET).strftime("%I:%M %p"),
                rows_processed // 1000000, active, tickers_processed,
                rate, eta, mem_mb), flush=True)
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

        if tk not in ticker_states:
            state = init_ticker(tk, bid, ask, ts_str)
            if state is None:
                ticker_states[tk] = None
            else:
                ticker_states[tk] = state
                ticker_last_seen[tk] = ts_str
        elif ticker_states[tk] is not None:
            process_row(ticker_states[tk], bid, ask, ts_str)
            ticker_last_seen[tk] = ts_str

        # Stale sweep
        if rows_processed % 50000 == 0:
            cur_epoch = parse_ts_cached(ts_str)
            stale = [t for t, lts in ticker_last_seen.items()
                     if cur_epoch - parse_ts_cached(lts) > 300]
            for t in stale:
                if ticker_states.get(t) is not None:
                    finalize_ticker(ticker_states[t])
                del ticker_states[t]
                del ticker_last_seen[t]
                tickers_processed += 1

# Flush remaining
print("[%s] Flushing %d tickers..." % (
    datetime.now(ET).strftime("%I:%M %p"), len(ticker_states)), flush=True)
for tk, state in ticker_states.items():
    if state is not None:
        finalize_ticker(state)
    tickers_processed += 1

total_time = time.time() - start_time
print("[%s] Complete. %d rows, %d tickers, %.0f min." % (
    datetime.now(ET).strftime("%I:%M %p"), rows_processed, tickers_processed,
    total_time / 60), flush=True)

# =======================================================================
# OUTPUT
# =======================================================================

# === TASK 1: Per-cell reaction depth distribution ===
print("\n" + "=" * 70)
print("=== TASK 1: POST-SET-1 REACTION DEPTH BY ENTRY RANGE ===\n")

# Group leader cells by entry price range
ranges = [(50, 60), (60, 70), (70, 80), (80, 90)]
print("| Entry range | N entries | N with 15c+ drop | Mean drop | p25 | Median | p75 | Max |")
print("|---|---|---|---|---|---|---|---|")

for lo, hi in ranges:
    all_drops = []
    big_drops = []
    for cell, depths in reaction_depths.items():
        for entry, dd_entry, dd_peak in depths:
            if lo <= entry < hi:
                all_drops.append(dd_entry)
                if dd_entry >= 15:
                    big_drops.append(dd_entry)

    if not all_drops:
        print("| %d-%dc | 0 | - | - | - | - | - | - |" % (lo, hi))
        continue

    big_drops.sort()
    n_big = len(big_drops)
    if n_big >= 2:
        mean_d = sum(big_drops) / n_big
        p25 = big_drops[n_big // 4]
        med = big_drops[n_big // 2]
        p75 = big_drops[3 * n_big // 4]
        mx = max(big_drops)
        print("| %d-%dc | %d | %d (%.0f%%) | %.1fc | %.1fc | %.1fc | %.1fc | %.1fc |" % (
            lo, hi, len(all_drops), n_big, n_big / len(all_drops) * 100,
            mean_d, p25, med, p75, mx))
    else:
        print("| %d-%dc | %d | %d | insufficient | - | - | - | - |" % (
            lo, hi, len(all_drops), n_big))

# Also for underdogs
print("\n| Entry range (underdog) | N entries | N with 15c+ drop | Mean drop | p25 | Median | p75 |")
print("|---|---|---|---|---|---|---|")
for lo, hi in [(5, 15), (15, 30), (30, 50)]:
    all_drops = []
    big_drops = []
    for cell, depths in reaction_depths.items():
        for entry, dd_entry, dd_peak in depths:
            if lo <= entry < hi:
                all_drops.append(dd_entry)
                if dd_entry >= 10:
                    big_drops.append(dd_entry)
    if not all_drops: continue
    big_drops.sort()
    n_big = len(big_drops)
    if n_big >= 2:
        mean_d = sum(big_drops) / n_big
        p25 = big_drops[n_big // 4]
        med = big_drops[n_big // 2]
        p75 = big_drops[3 * n_big // 4]
        print("| %d-%dc | %d | %d (%.0f%%) | %.1fc | %.1fc | %.1fc | %.1fc |" % (
            lo, hi, len(all_drops), n_big, n_big / len(all_drops) * 100,
            mean_d, p25, med, p75))

# Detailed per-cell breakdown
print("\n=== TASK 1b: Per-cell reaction depth (15c+ drops only) ===\n")
print("| Cell | N total | N 15c+ drop | % | Mean drop | Median | p75 |")
print("|---|---|---|---|---|---|---|")
for cell in sorted(ALL_CELLS.keys()):
    depths = reaction_depths.get(cell, [])
    if not depths: continue
    n_total = len(depths)
    big = sorted([dd for _, dd, _ in depths if dd >= 15])
    n_big = len(big)
    if n_big >= 3:
        mean_d = sum(big) / n_big
        med = big[n_big // 2]
        p75 = big[3 * n_big // 4]
        print("| %s | %d | %d (%.0f%%) | %.0f%% | %.1fc | %.1fc | %.1fc |" % (
            cell, n_total, n_big, n_big / n_total * 100,
            n_big / n_total * 100, mean_d, med, p75))


# === TASK 2: Recovery from reactions ===
print("\n" + "=" * 70)
print("=== TASK 2: RECOVERY FROM SET-1 LOSS REACTIONS ===\n")
print("| Cell | N reactions | Recovered to entry | Recovered to exit | Continued losing | Avg depth |")
print("|---|---|---|---|---|---|")

for cell in sorted(ALL_CELLS.keys()):
    recs = reaction_recovery.get(cell, [])
    if len(recs) < 3: continue
    n = len(recs)
    rec_entry = sum(1 for r in recs if r["recovered_to_entry"])
    rec_exit = sum(1 for r in recs if r["recovered_to_exit"])
    continued = n - rec_entry
    avg_depth = sum(r["depth"] for r in recs) / n
    print("| %s | %d | %d (%.0f%%) | %d (%.0f%%) | %d (%.0f%%) | %.1fc |" % (
        cell, n, rec_entry, rec_entry / n * 100,
        rec_exit, rec_exit / n * 100,
        continued, continued / n * 100, avg_depth))


# === TASK 3: DCA at event-matched depths ===
print("\n" + "=" * 70)
print("=== TASK 3: DCA AT EVENT-MATCHED DEPTHS ===\n")

# Write CSV
with open(os.path.join(OUTPUT_DIR, "dca_event_matched.csv"), "w") as f:
    writer = csv.writer(f)
    writer.writerow(["cell", "trigger", "combo", "is_active", "total", "scalp_pre",
                      "dca_fires", "dca_wins", "dca_knife", "no_opp",
                      "fire_rate_pct", "win_rate_pct", "dca_ev_per_fire_c", "cell_roi_delta_pct"])

    for (cell, trigger, combo), data in sorted(dca_agg.items()):
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
print("| Cell | Trigger | Combo | N | Fires | Win% | EV/fire | ROI delta |")
print("|---|---|---|---|---|---|---|---|")
for (cell, trigger, combo), data in sorted(dca_agg.items()):
    n = data["total"]
    fires = data["dca_fires"]
    if fires < 3: continue
    wins = data["dca_wins"]
    parts = cell.split("_")
    bucket = parts[-1]
    lo, hi = int(bucket.split("-")[0]), int(bucket.split("-")[1])
    avg_entry = (lo + hi) / 2.0
    wr = wins / fires * 100
    ev = data["pnl_sum"] / fires
    roi = data["pnl_sum"] / (n * avg_entry * 10) * 100 if n * avg_entry else 0
    print("| %s | -%dc | %s | %d | %d | %.0f%% | %+.0fc | %+.1f%% |" % (
        cell, trigger, combo, n, fires, wr, ev, roi))


# === TASK 4: Best event-matched DCA per cell ===
print("\n" + "=" * 70)
print("=== TASK 4: CELLS WHERE EVENT-MATCHED DCA WORKS ===\n")
print("| Cell | Best trigger | Combo | N | Fire% | Win% | ROI delta | Rec |")
print("|---|---|---|---|---|---|---|---|")

for cell in sorted(ALL_CELLS.keys()):
    best_roi = -999
    best_key = None
    best_data = None

    for (c, t, s), data in dca_agg.items():
        if c != cell or data["total"] < 20 or data["dca_fires"] < 5:
            continue
        parts = cell.split("_")
        bucket = parts[-1]
        lo, hi = int(bucket.split("-")[0]), int(bucket.split("-")[1])
        avg_entry = (lo + hi) / 2.0
        roi = data["pnl_sum"] / (data["total"] * avg_entry * 10) * 100
        if roi > best_roi:
            best_roi = roi
            best_key = (t, s)
            best_data = data

    if best_key and best_data and best_roi > -50:
        fires = best_data["dca_fires"]
        fire_rate = fires / best_data["total"] * 100
        wins = best_data["dca_wins"]
        wr = wins / fires * 100 if fires else 0
        rec = "ENABLE" if best_roi > 3 and best_data["total"] >= 20 else "TEST" if best_roi > 0 else "DISABLE"
        is_active = cell in active_cells
        print("| %s | -%dc | %s | %d | %.0f%% | %.0f%% | %+.1f%% | %s |" % (
            cell, best_key[0], best_key[1], best_data["total"],
            fire_rate, wr, best_roi, rec))


# === TASK 5: Timing analysis ===
print("\n" + "=" * 70)
print("=== TASK 5: DCA TIMING (WINS ONLY) ===\n")

if dca_timing:
    # Group by entry price range
    leader_timing = [t for t in dca_timing if "leader" in t["cell"]]
    underdog_timing = [t for t in dca_timing if "underdog" in t["cell"]]

    for label, group in [("Leader cells", leader_timing), ("Underdog cells", underdog_timing)]:
        if not group:
            print("%s: no DCA wins with timing data\n" % label)
            continue
        h2f = sorted([t["hours_entry_to_fire"] for t in group])
        h2w = sorted([t["hours_fire_to_win"] for t in group])
        total_h = sorted([t["hours_entry_to_win"] for t in group])
        n = len(group)

        print("%s (N=%d DCA wins):" % (label, n))
        print("  Entry to DCA fire:  median=%.1fh, p25=%.1fh, p75=%.1fh" % (
            h2f[n // 2], h2f[n // 4], h2f[3 * n // 4]))
        print("  DCA fire to win:    median=%.1fh, p25=%.1fh, p75=%.1fh" % (
            h2w[n // 2], h2w[n // 4], h2w[3 * n // 4]))
        print("  Total entry to win: median=%.1fh, p25=%.1fh, p75=%.1fh" % (
            total_h[n // 2], total_h[n // 4], total_h[3 * n // 4]))

        # How many fires happen within pregame window (first 12h from entry)?
        pregame_fires = sum(1 for t in group if t["hours_entry_to_fire"] < 12)
        postgame_fires = n - pregame_fires
        print("  Fires within 12h of entry (pregame-possible): %d (%.0f%%)" % (
            pregame_fires, pregame_fires / n * 100))
        print("  Fires after 12h (likely in-match): %d (%.0f%%)" % (
            postgame_fires, postgame_fires / n * 100))

        # Within our buffer (entries are T-12h to T-15min, so DCA fires within first ~12h)
        # More precisely: entries happen up to 12h before match, buffer closes at T-15min
        # If DCA fires 1h after entry and entry was T-6h, DCA fires at T-5h = pregame
        # If DCA fires 8h after entry and entry was T-12h, DCA fires at T-4h = pregame
        # Key: DCA fires at T-Xh if fire happens (entry_lead - hours_to_fire) before match

        # Approximate: if hours_entry_to_fire < 0.25h (15 min), it's definitely pregame
        # If > 12h, it's definitely in-match or post-match
        fast_fires = sum(1 for t in group if t["hours_entry_to_fire"] < 0.25)
        slow_fires = sum(1 for t in group if t["hours_entry_to_fire"] >= 0.25 and t["hours_entry_to_fire"] < 6)
        match_fires = sum(1 for t in group if t["hours_entry_to_fire"] >= 6)
        print("  Fire < 15min after entry (noise, not Set 1): %d" % fast_fires)
        print("  Fire 15min-6h after entry (pregame movement): %d" % slow_fires)
        print("  Fire 6h+ after entry (likely match events): %d" % match_fires)
        print()
else:
    print("No DCA timing data collected.\n")


# === TASK 6: Match-state-aware DCA ===
print("=" * 70)
print("=== TASK 6: MATCH-STATE FEASIBILITY ===\n")

if dca_timing:
    # For DCA to work with Set 1 reactions:
    # - Entry typically happens T-12h to T-0 (match start)
    # - Set 1 loss typically happens ~30-60 min after match start
    # - Our entry buffer closes at T-15min
    # - DCA order would need to be placed before T-15min
    # - But the trigger (price drop) happens after match starts

    # So the question is: how many DCA fires happen SOON after entry vs LATE?
    all_fires_h = sorted([t["hours_entry_to_fire"] for t in dca_timing])
    n = len(all_fires_h)
    print("All DCA fires timing (entry to fire):")
    print("  N = %d" % n)
    if n > 0:
        print("  Min: %.2fh, Max: %.1fh" % (min(all_fires_h), max(all_fires_h)))
        print("  p10=%.2fh, p25=%.1fh, median=%.1fh, p75=%.1fh, p90=%.1fh" % (
            all_fires_h[n // 10], all_fires_h[n // 4], all_fires_h[n // 2],
            all_fires_h[3 * n // 4], all_fires_h[9 * n // 10]))

        # If we extended active window to T+1h (1h after match start):
        # Assume median entry is T-6h, then fires within 7h would be T+1h
        print("\n  Scenario: extend window to T+1h post-match-start")
        print("    Fires reachable (< 7h from entry): %d (%.0f%%)" % (
            sum(1 for h in all_fires_h if h < 7), sum(1 for h in all_fires_h if h < 7) / n * 100))
        print("    Fires reachable (< 12h from entry): %d (%.0f%%)" % (
            sum(1 for h in all_fires_h if h < 12), sum(1 for h in all_fires_h if h < 12) / n * 100))
else:
    print("No DCA timing data.\n")


# === TASK 7: True opportunity space ===
print("\n" + "=" * 70)
print("=== TASK 7: TRUE DCA OPPORTUNITY SPACE ===\n")
print("| Cell | N entries | P(20%+ drop) | P(recovery|drop) | EV scenario |")
print("|---|---|---|---|---|")

for cell in sorted(ALL_CELLS.keys()):
    o = opp_space.get(cell)
    if not o or o["total"] < 10: continue
    n = o["total"]
    d20 = o["drop_20pct"]
    rec = o["drop_20pct_recover"]
    p_drop = d20 / n * 100 if n else 0
    p_rec = rec / d20 * 100 if d20 else 0

    parts = cell.split("_")
    bucket = parts[-1]
    lo, hi = int(bucket.split("-")[0]), int(bucket.split("-")[1])
    avg_e = (lo + hi) / 2.0
    exit_c = ALL_CELLS[cell]

    # EV scenario: if we DCA on all 20%+ drops
    # Win: 10*(exit_c) + 5*(exit_c + avg_e*0.2)  [approximate]
    # Loss: 10*avg_e + 5*(avg_e*0.8)
    if d20 >= 3:
        win_pnl = 10 * exit_c + 5 * (exit_c + avg_e * 0.2)
        loss_pnl = 10 * avg_e + 5 * (avg_e * 0.8)
        ev = (p_rec / 100) * win_pnl - (1 - p_rec / 100) * loss_pnl
        ev_per_entry = ev * (p_drop / 100) / 100  # per-entry in dollars
        print("| %s | %d | %.0f%% (%d) | %.0f%% (%d/%d) | $%+.2f/entry |" % (
            cell, n, p_drop, d20, p_rec, rec, d20, ev_per_entry))
    else:
        print("| %s | %d | %.0f%% (%d) | - | insufficient |" % (
            cell, n, p_drop, d20))


# === Final summary ===
print("\n" + "=" * 70)
mem_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
print("Runtime: %.0f min | Peak memory: %.0f MB | Tickers: %d" % (
    total_time / 60, mem_mb, tickers_processed))
print("Output CSV: %s/dca_event_matched.csv" % OUTPUT_DIR)
