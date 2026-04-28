#!/usr/bin/env python3
"""
Ultimate Per-Cell Economics — Every variable, per cell, harmonized.

Data sources:
  1. historical_events (1,357 events, Mar 20 - Apr 17) → TWP, settlement rates, drawdown
  2. DCA v3 results (per_cell_dca_summary.csv) → DCA economics
  3. Live bot logs (live_v3_*.jsonl, last 7 days) → live fills, outcomes, skips
  4. deploy_v4.json → current cell config
"""

import sqlite3, json, csv, os, glob, sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta

BASE_DIR = "/root/Omi-Workspace/arb-executor"
ET = timezone(timedelta(hours=-4))

# === LOAD CONFIG ===
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
    direction = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, direction, bs, bs + 4)


# =====================================================================
# TASK 1: Per-cell baseline economics from historical_events
# =====================================================================
print("=" * 80)
print("=== TASK 1: PER-CELL BASELINE ECONOMICS (SETTLEMENT-BASED) ===")
print("=" * 80)
print()
print("Source: historical_events table, Mar 20 - Apr 17, N=1357 events")
print("Each event has winner side + loser side = 2 entries per event")
print()

conn = sqlite3.connect(os.path.join(BASE_DIR, "tennis.db"))
cur = conn.cursor()

cur.execute("""SELECT event_ticker, category, winner, loser,
    first_price_winner, min_price_winner, max_price_winner,
    first_price_loser, min_price_loser, max_price_loser,
    total_trades, first_ts, last_ts
    FROM historical_events
    WHERE first_ts > '2026-03-20' AND first_ts < '2026-04-18'
    AND total_trades >= 10""")
events = cur.fetchall()

# Map category to tier
cat_to_tier = {
    "ATP_MAIN": "ATP_MAIN", "ATP_CHALL": "ATP_CHALL",
    "WTA_MAIN": "WTA_MAIN", "WTA_CHALL": "WTA_CHALL",
}

# Per-cell data collection
cell_data = defaultdict(lambda: {
    "entries": [],  # list of (entry_price, won, max_price, min_price, event_ticker, duration_h)
})

for ev in events:
    evt, cat = ev[0], ev[1]
    tier = cat_to_tier.get(cat)
    if tier is None:
        continue

    fp_w, min_w, max_w = ev[4], ev[5], ev[6]
    fp_l, min_l, max_l = ev[7], ev[8], ev[9]
    first_ts, last_ts = ev[11], ev[12]

    # Duration
    try:
        t1 = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
        t2 = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
        dur_h = (t2 - t1).total_seconds() / 3600
    except:
        dur_h = 0

    # Winner side entry
    if fp_w and fp_w > 0 and fp_w < 100:
        cell_w = classify_cell(tier, fp_w)
        if cell_w in ALL_CELLS:
            cell_data[cell_w]["entries"].append((fp_w, True, max_w, min_w, evt, dur_h))

    # Loser side entry
    if fp_l and fp_l > 0 and fp_l < 100:
        cell_l = classify_cell(tier, fp_l)
        if cell_l in ALL_CELLS:
            cell_data[cell_l]["entries"].append((fp_l, False, max_l, min_l, evt, dur_h))


# Print Task 1 results
print("| Cell | Status | Exit | N | Avg entry | TWP | Mispricing | Scalp WR | Best exit | ROI/fill | Avg dur(h) | $/fill |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")

task1 = {}
for cell in sorted(ALL_CELLS.keys()):
    entries = cell_data.get(cell, {}).get("entries", [])
    if not entries:
        continue
    n = len(entries)
    exit_c = ALL_CELLS[cell]
    is_active = cell in active_cells
    status = "ACTIVE" if is_active else "disabled"

    avg_entry = sum(e[0] for e in entries) / n
    wins = sum(1 for e in entries if e[1])
    twp = wins / n  # true win probability
    mispricing = twp * 100 - avg_entry  # in cents: TWP*100 - entry price

    # Scalp analysis: did max_price reach entry + exit_c?
    scalps = 0
    for ep, won, mx, mn, evt, dur in entries:
        target = min(99, ep + exit_c)
        if mx and mx >= target:
            scalps += 1
    scalp_wr = scalps / n * 100

    # ROI per fill: expected value of each entry
    # Win (settlement at 99): profit = 99 - entry
    # Loss (settlement at 1): loss = entry - 1
    # Scalp (exit at entry + exit_c): profit = exit_c
    # Order: scalp happens before settlement if possible
    # Approximate: scalp_wr% get exit_c, rest settle
    ev_per_fill = (scalp_wr / 100) * exit_c + (1 - scalp_wr / 100) * (twp * (99 - avg_entry) - (1 - twp) * (avg_entry - 1))
    roi_pct = ev_per_fill / avg_entry * 100
    dollar_per_fill = ev_per_fill * 10 / 100  # 10 contracts at 1c each

    avg_dur = sum(e[5] for e in entries) / n

    task1[cell] = {
        "n": n, "avg_entry": avg_entry, "twp": twp, "mispricing": mispricing,
        "scalp_wr": scalp_wr, "exit_c": exit_c, "ev_per_fill": ev_per_fill,
        "roi_pct": roi_pct, "dollar_per_fill": dollar_per_fill, "avg_dur": avg_dur,
        "is_active": is_active, "wins": wins,
    }

    flag = "" if n >= 30 else " *"
    print("| %s | %s | +%dc | %d%s | %.0fc | %.0f%% | %+.1fc | %.0f%% | +%dc | %+.1f%% | %.1fh | $%+.2f |" % (
        cell, status, exit_c, n, flag, avg_entry, twp * 100, mispricing,
        scalp_wr, exit_c, roi_pct, avg_dur, dollar_per_fill))

print()
print("* = N<30, low confidence")
print()

# =====================================================================
# TASK 2: Paired economics
# =====================================================================
print("=" * 80)
print("=== TASK 2: PAIRED ECONOMICS ===")
print("=" * 80)
print()

# For each event, we have two sides. If both sides' cells are active,
# the pair is deployed. Compute joint economics.
pair_data = defaultdict(lambda: {"matches": 0, "both_active": 0, "joint_pnl": []})

for ev in events:
    evt, cat = ev[0], ev[1]
    tier = cat_to_tier.get(cat)
    if tier is None:
        continue

    fp_w, min_w, max_w = ev[4], ev[5], ev[6]
    fp_l, min_l, max_l = ev[7], ev[8], ev[9]

    if not fp_w or not fp_l or fp_w <= 0 or fp_l <= 0:
        continue

    cell_w = classify_cell(tier, fp_w)
    cell_l = classify_cell(tier, fp_l)

    if cell_w not in ALL_CELLS or cell_l not in ALL_CELLS:
        continue

    exit_w = ALL_CELLS[cell_w]
    exit_l = ALL_CELLS[cell_l]

    # Winner side PnL
    target_w = min(99, fp_w + exit_w)
    if max_w and max_w >= target_w:
        pnl_w = exit_w * 10  # scalped
    else:
        pnl_w = (99 - fp_w) * 10  # settlement win

    # Loser side PnL
    target_l = min(99, fp_l + exit_l)
    if max_l and max_l >= target_l:
        pnl_l = exit_l * 10  # scalped before loss
    else:
        pnl_l = -(fp_l - 1) * 10  # settlement loss

    joint_pnl = pnl_w + pnl_l
    capital = (fp_w + fp_l) * 10  # total capital deployed

    both_active = cell_w in active_cells and cell_l in active_cells
    pair_key = tuple(sorted([cell_w, cell_l]))

    pair_data[pair_key]["matches"] += 1
    pair_data[pair_key]["both_active"] += (1 if both_active else 0)
    pair_data[pair_key]["joint_pnl"].append((joint_pnl, capital, pnl_w, pnl_l))

print("| Pair | N matches | Both active | Avg joint PnL | Joint ROI | Avg capital | W-side PnL | L-side PnL |")
print("|---|---|---|---|---|---|---|---|")

for pair in sorted(pair_data.keys()):
    d = pair_data[pair]
    n = d["matches"]
    if n < 5:
        continue
    both = d["both_active"]
    pnls = d["joint_pnl"]
    avg_jpnl = sum(p[0] for p in pnls) / n
    avg_cap = sum(p[1] for p in pnls) / n
    avg_w = sum(p[2] for p in pnls) / n
    avg_l = sum(p[3] for p in pnls) / n
    roi = avg_jpnl / avg_cap * 100 if avg_cap else 0

    print("| %s / %s | %d | %d | %+.0fc | %+.1f%% | %.0fc | %+.0fc | %+.0fc |" % (
        pair[0], pair[1], n, both, avg_jpnl, roi, avg_cap, avg_w, avg_l))


# =====================================================================
# TASK 3: Pre-event vs post-event timing
# =====================================================================
print()
print("=" * 80)
print("=== TASK 3: ENTRY TIMING RELATIVE TO MATCH START ===")
print("=" * 80)
print()
print("Note: historical_events has first_ts (first BBO activity) and last_ts.")
print("We don't have match commence_time for Mar-Apr BBO period.")
print("Using BBO activity duration as proxy for match lifecycle.")
print()

# Entries that last < 2h are likely premarket-only (no match played yet at settlement)
# Entries that last > 6h span premarket + full match
# We can infer: early entries (high first_price stability) vs mid-match entries

# For each cell: distribution of event duration
print("| Cell | N | Avg duration | <2h (premarket) | 2-6h | 6-12h | >12h | Median dur |")
print("|---|---|---|---|---|---|---|---|")

for cell in sorted(ALL_CELLS.keys()):
    entries = cell_data.get(cell, {}).get("entries", [])
    if len(entries) < 10:
        continue
    n = len(entries)
    durs = sorted([e[5] for e in entries])
    avg_dur = sum(durs) / n
    lt2 = sum(1 for d in durs if d < 2)
    t2_6 = sum(1 for d in durs if 2 <= d < 6)
    t6_12 = sum(1 for d in durs if 6 <= d < 12)
    gt12 = sum(1 for d in durs if d >= 12)
    med = durs[n // 2]
    print("| %s | %d | %.1fh | %d (%.0f%%) | %d (%.0f%%) | %d (%.0f%%) | %d (%.0f%%) | %.1fh |" % (
        cell, n, avg_dur,
        lt2, lt2/n*100, t2_6, t2_6/n*100, t6_12, t6_12/n*100, gt12, gt12/n*100, med))


# =====================================================================
# TASK 4: Per-cell harmonized scorecard
# =====================================================================
print()
print("=" * 80)
print("=== TASK 4: PER-CELL HARMONIZED SCORECARD ===")
print("=" * 80)
print()

# Load DCA results
dca_results = {}
dca_file = "/tmp/validation5/per_cell_dca_summary.csv"
if os.path.exists(dca_file):
    with open(dca_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            cell = row["cell"]
            trigger = int(row["trigger"])
            combo = row["combo"]
            roi_delta = float(row["cell_roi_delta_pct"])
            fires = int(row["dca_fires"])
            total = int(row["total"])
            key = (cell, combo)
            if key not in dca_results or roi_delta > dca_results[key]["roi"]:
                dca_results[key] = {"roi": roi_delta, "trigger": trigger, "fires": fires, "total": total}

print("| Cell | Status | N | Entry | TWP | Misprice | Scalp% | Exit | ROI | $/fill | DCA-A ROI | DCA-A trig | DCA-B ROI | DCA-B trig | Action |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")

for cell in sorted(ALL_CELLS.keys()):
    t1 = task1.get(cell)
    if not t1:
        continue
    n = t1["n"]
    exit_c = t1["exit_c"]

    # DCA results
    dca_a = dca_results.get((cell, "A"), {"roi": 0, "trigger": 0, "fires": 0})
    dca_b = dca_results.get((cell, "B"), {"roi": 0, "trigger": 0, "fires": 0})

    # Action recommendation
    if t1["is_active"]:
        if t1["roi_pct"] > 5 and n >= 30:
            action = "KEEP"
        elif t1["roi_pct"] > 0 and n >= 30:
            action = "KEEP"
        elif t1["roi_pct"] > 0:
            action = "KEEP*"  # low N
        elif t1["roi_pct"] > -5:
            action = "RETUNE"
        else:
            action = "DISABLE"
    else:
        if t1["roi_pct"] > 5 and n >= 30:
            action = "RE-ENABLE"
        elif t1["roi_pct"] > 0 and n >= 20:
            action = "RE-ENABLE"
        else:
            action = "STAY-OFF"

    flag = "*" if n < 30 else ""
    print("| %s | %s | %d%s | %.0f | %.0f%% | %+.1f | %.0f%% | +%d | %+.1f%% | $%+.2f | %+.1f%% | -%d | %+.1f%% | -%d | %s |" % (
        cell, "ON" if t1["is_active"] else "off", n, flag,
        t1["avg_entry"], t1["twp"]*100, t1["mispricing"],
        t1["scalp_wr"], exit_c,
        t1["roi_pct"], t1["dollar_per_fill"],
        dca_a["roi"], dca_a["trigger"],
        dca_b["roi"], dca_b["trigger"],
        action))


# =====================================================================
# TASK 5: Cross-tabulation by tier
# =====================================================================
print()
print("=" * 80)
print("=== TASK 5: CROSS-TABULATION BY TIER ===")
print("=" * 80)
print()

# Group by tier
tier_data = defaultdict(lambda: {"entries": [], "wins": 0, "scalps": 0})
for cell, d in cell_data.items():
    parts = cell.split("_")
    tier = parts[0] + "_" + parts[1]
    for ep, won, mx, mn, evt, dur in d["entries"]:
        exit_c = ALL_CELLS.get(cell, 0)
        target = min(99, ep + exit_c)
        scalped = mx and mx >= target
        tier_data[tier]["entries"].append((ep, won, scalped))
        if won: tier_data[tier]["wins"] += 1
        if scalped: tier_data[tier]["scalps"] += 1

print("| Tier | N | TWP | Scalp% | Avg entry |")
print("|---|---|---|---|---|")
for tier in sorted(tier_data.keys()):
    d = tier_data[tier]
    n = len(d["entries"])
    if n < 10: continue
    twp = d["wins"] / n * 100
    sr = d["scalps"] / n * 100
    ae = sum(e[0] for e in d["entries"]) / n
    print("| %s | %d | %.0f%% | %.0f%% | %.0fc |" % (tier, n, twp, sr, ae))


# =====================================================================
# TASKS 6-9: Live trading analysis (last 7 days)
# =====================================================================
print()
print("=" * 80)
print("=== TASKS 6-9: LIVE TRADING ANALYSIS (LAST 7 DAYS) ===")
print("=" * 80)
print()

# Parse all recent log files
log_files = sorted(glob.glob(os.path.join(BASE_DIR, "logs/live_v3_*.jsonl")))

live_fills = []  # entry_filled events
live_exits = []  # exit_filled / scalp_filled
live_settlements = []  # settled events
live_skips = defaultdict(int)  # reason -> count
live_cell_matches = []  # cell_match events
live_orders = []  # order_placed events
live_cancels = []  # order_cancelled events

for logf in log_files[-7:]:
    with open(logf) as f:
        for line in f:
            try:
                d = json.loads(line.strip())
            except:
                continue
            ev = d.get("event", "")
            det = d.get("details", {})

            if ev == "entry_filled":
                live_fills.append({
                    "ticker": d.get("ticker", ""),
                    "ts": d.get("ts", ""),
                    "fill_price": det.get("fill_price", 0),
                    "qty": det.get("qty", 0),
                    "cell": det.get("cell", ""),
                    "direction": det.get("direction", ""),
                    "play_type": det.get("play_type", ""),
                })
            elif ev == "exit_filled":
                live_exits.append({
                    "ticker": d.get("ticker", ""),
                    "ts": d.get("ts", ""),
                    "exit_price": det.get("exit_price", 0),
                    "entry_price": det.get("entry_price", 0),
                    "pnl_cents": det.get("pnl_cents", 0),
                    "pnl_dollars": det.get("pnl_dollars", 0),
                })
            elif ev == "scalp_filled":
                live_exits.append({
                    "ticker": d.get("ticker", ""),
                    "ts": d.get("ts", ""),
                    "exit_price": det.get("exit_price", 0),
                    "entry_price": det.get("entry_price", 0),
                    "pnl_cents": det.get("profit_cents", 0),
                    "pnl_dollars": det.get("profit_cents", 0) * 10 / 100 if det.get("profit_cents") else 0,
                    "scalp": True,
                })
            elif ev == "settled":
                live_settlements.append({
                    "ticker": d.get("ticker", ""),
                    "ts": d.get("ts", ""),
                    "result": det.get("settle", ""),
                    "settle_price": det.get("settle_price", 0),
                    "entry_price": det.get("entry_price", 0),
                    "pnl_cents": det.get("pnl_cents", 0),
                    "pnl_dollars": det.get("pnl_dollars", 0),
                })
            elif ev == "skipped":
                reason = det.get("reason", "unknown")
                live_skips[reason] += 1
            elif ev == "cell_match":
                live_cell_matches.append({
                    "ticker": d.get("ticker", ""),
                    "ts": d.get("ts", ""),
                    "cell": det.get("cell", ""),
                    "direction": det.get("direction", ""),
                    "scenario": det.get("scenario", ""),
                    "anchor_source": det.get("anchor_source", ""),
                    "anchor_value": det.get("anchor_value", 0),
                    "delta": det.get("delta", 0),
                })
            elif ev == "order_placed":
                live_orders.append({
                    "ticker": d.get("ticker", ""),
                    "ts": d.get("ts", ""),
                    "price": det.get("price", 0),
                    "count": det.get("count", 0),
                    "action": det.get("action", ""),
                    "response_status": det.get("response_status", ""),
                })

print("=== TASK 6: Live fills and outcomes ===")
print()
print("Fills: %d | Exits: %d | Settlements: %d" % (
    len(live_fills), len(live_exits), len(live_settlements)))
print()

# Per-cell live performance
live_cell_pnl = defaultdict(lambda: {"fills": 0, "scalps": 0, "settle_w": 0, "settle_l": 0, "pnl": 0, "capital": 0})

for f in live_fills:
    cell = f["cell"]
    if cell:
        live_cell_pnl[cell]["fills"] += 1
        live_cell_pnl[cell]["capital"] += f["fill_price"] * f["qty"]

# Match exits to fills by ticker
ticker_to_cell = {f["ticker"]: f["cell"] for f in live_fills if f["cell"]}

for e in live_exits:
    cell = ticker_to_cell.get(e["ticker"], "")
    if cell:
        live_cell_pnl[cell]["scalps"] += 1
        live_cell_pnl[cell]["pnl"] += e.get("pnl_cents", 0) * 10

for s in live_settlements:
    cell = ticker_to_cell.get(s["ticker"], "")
    if cell:
        if s["result"] == "WIN":
            live_cell_pnl[cell]["settle_w"] += 1
            live_cell_pnl[cell]["pnl"] += s.get("pnl_cents", 0) * 10
        else:
            live_cell_pnl[cell]["settle_l"] += 1
            live_cell_pnl[cell]["pnl"] += s.get("pnl_cents", 0) * 10

if live_cell_pnl:
    print("| Cell | Fills | Scalps | Settle W | Settle L | PnL(c) | Live ROI | Sweep ROI | Gap |")
    print("|---|---|---|---|---|---|---|---|---|")
    for cell in sorted(live_cell_pnl.keys()):
        d = live_cell_pnl[cell]
        if d["fills"] == 0: continue
        live_roi = d["pnl"] / d["capital"] * 100 if d["capital"] else 0
        sweep_roi = task1.get(cell, {}).get("roi_pct", 0)
        gap = live_roi - sweep_roi
        print("| %s | %d | %d | %d | %d | %+d | %+.1f%% | %+.1f%% | %+.1f%% |" % (
            cell, d["fills"], d["scalps"], d["settle_w"], d["settle_l"],
            d["pnl"], live_roi, sweep_roi, gap))


# === TASK 7: P&L attribution ===
print()
print("=== TASK 7: P&L ATTRIBUTION (last 7 days settled) ===")
print()

if live_settlements:
    print("| Ticker | Cell | Entry | Result | PnL($) |")
    print("|---|---|---|---|---|")
    total_pnl = 0
    for s in live_settlements:
        cell = ticker_to_cell.get(s["ticker"], "?")
        pnl_d = s.get("pnl_dollars", 0)
        total_pnl += pnl_d
        print("| %s | %s | %dc | %s | $%+.2f |" % (
            s["ticker"][-20:], cell, s["entry_price"], s["result"], pnl_d))
    print()
    print("Total settlement PnL: $%.2f" % total_pnl)
    if live_exits:
        scalp_pnl = sum(e.get("pnl_dollars", e.get("pnl_cents", 0) * 10 / 100) for e in live_exits)
        print("Total scalp PnL: $%.2f" % scalp_pnl)
        print("Combined: $%.2f" % (total_pnl + scalp_pnl))
else:
    print("No settlement data in logs.")

for e in live_exits:
    cell = ticker_to_cell.get(e["ticker"], "?")
    pnl_c = e.get("pnl_cents", 0)
    print("  SCALP: %s | cell=%s | entry=%d exit=%d pnl=%dc" % (
        e["ticker"][-25:], cell, e.get("entry_price", 0), e.get("exit_price", 0), pnl_c))


# === TASK 8: Skip rate analysis ===
print()
print("=== TASK 8: SKIP RATE ANALYSIS ===")
print()

print("Skip reasons (last 7 days):")
for reason, count in sorted(live_skips.items(), key=lambda x: -x[1])[:20]:
    print("  %-40s %d" % (reason, count))

print()
print("Cell matches that led to orders: %d" % len(live_cell_matches))
print("Orders placed: %d" % len(live_orders))
print("Fills achieved: %d" % len(live_fills))
if live_cell_matches:
    print("Match → fill rate: %.0f%%" % (len(live_fills) / len(live_cell_matches) * 100))

# Per-cell skip pattern
cell_match_counts = defaultdict(int)
cell_fill_counts = defaultdict(int)
for cm in live_cell_matches:
    cell_match_counts[cm["cell"]] += 1
for f in live_fills:
    cell_fill_counts[f["cell"]] += 1

if cell_match_counts:
    print()
    print("| Cell | Matches | Fills | Fill rate |")
    print("|---|---|---|---|")
    for cell in sorted(cell_match_counts.keys()):
        m = cell_match_counts[cell]
        f = cell_fill_counts.get(cell, 0)
        print("| %s | %d | %d | %.0f%% |" % (cell, m, f, f / m * 100 if m else 0))


# === TASK 9: Anchor health ===
print()
print("=== TASK 9: ANCHOR HEALTH PER ENTRY ===")
print()

if live_cell_matches:
    anchor_sources = defaultdict(int)
    for cm in live_cell_matches:
        anchor_sources[cm["anchor_source"]] += 1
    print("Anchor source distribution (cell matches):")
    for src, cnt in sorted(anchor_sources.items(), key=lambda x: -x[1]):
        print("  %-30s %d (%.0f%%)" % (src, cnt, cnt / len(live_cell_matches) * 100))


# =====================================================================
# TASK 10: True opportunity space
# =====================================================================
print()
print("=" * 80)
print("=== TASK 10: TRUE OPPORTUNITY SPACE ===")
print("=" * 80)
print()

# For every event in historical data, was there mispricing?
print("For each event, both sides create entries. The side with positive mispricing")
print("(TWP > entry price) represents a profitable opportunity.")
print()

opp_space = {"total_events": 0, "any_misprice": 0, "both_misprice": 0,
             "total_ev": 0, "cell_opps": defaultdict(int)}

for ev in events:
    evt, cat = ev[0], ev[1]
    tier = cat_to_tier.get(cat)
    if tier is None:
        continue

    fp_w, fp_l = ev[4], ev[7]
    if not fp_w or not fp_l: continue

    cell_w = classify_cell(tier, fp_w)
    cell_l = classify_cell(tier, fp_l)

    opp_space["total_events"] += 1

    # Winner side is always mispriced IF entry < TWP
    # But we can only check this in aggregate via task1
    t1_w = task1.get(cell_w)
    t1_l = task1.get(cell_l)

    mp_w = t1_w["mispricing"] if t1_w else 0
    mp_l = t1_l["mispricing"] if t1_l else 0

    if mp_w > 0 or mp_l > 0:
        opp_space["any_misprice"] += 1
    if mp_w > 0 and mp_l > 0:
        opp_space["both_misprice"] += 1

    if mp_w > 0:
        opp_space["cell_opps"][cell_w] += 1
    if mp_l > 0:
        opp_space["cell_opps"][cell_l] += 1

print("Total events: %d" % opp_space["total_events"])
print("Events with any mispriced side: %d (%.0f%%)" % (
    opp_space["any_misprice"], opp_space["any_misprice"] / opp_space["total_events"] * 100))
print("Events with both sides mispriced: %d (%.0f%%)" % (
    opp_space["both_misprice"], opp_space["both_misprice"] / opp_space["total_events"] * 100))
print()

print("| Cell | Opportunities | Avg mispricing | $/opportunity |")
print("|---|---|---|---|")
for cell in sorted(opp_space["cell_opps"].keys()):
    t1 = task1.get(cell)
    if not t1: continue
    opps = opp_space["cell_opps"][cell]
    print("| %s | %d | %+.1fc | $%+.2f |" % (
        cell, opps, t1["mispricing"], t1["dollar_per_fill"]))


# =====================================================================
# TASK 11: Recommendation per cell
# =====================================================================
print()
print("=" * 80)
print("=== TASK 11: PER-CELL RECOMMENDATIONS ===")
print("=" * 80)
print()

print("| Cell | Status | N | TWP | Misprice | Scalp% | ROI | Rec | Why |")
print("|---|---|---|---|---|---|---|---|---|")

for cell in sorted(ALL_CELLS.keys()):
    t1 = task1.get(cell)
    if not t1:
        print("| %s | %s | 0 | - | - | - | - | NO_DATA | no historical entries |" % (
            cell, "ON" if cell in active_cells else "off"))
        continue

    n = t1["n"]
    is_active = t1["is_active"]
    twp = t1["twp"] * 100
    mp = t1["mispricing"]
    sr = t1["scalp_wr"]
    roi = t1["roi_pct"]

    # Live data check
    live = live_cell_pnl.get(cell)

    if is_active:
        if roi > 5 and n >= 30 and mp > 0:
            rec = "KEEP"
            why = "positive ROI (%.0f%%), %.1fc mispricing" % (roi, mp)
        elif roi > 0 and n >= 20:
            rec = "KEEP"
            why = "marginally positive (%.0f%%), N=%d" % (roi, n)
        elif n < 15:
            rec = "INVESTIGATE"
            why = "N=%d too low for confidence" % n
        elif mp <= 0 and roi <= 0:
            rec = "DISABLE"
            why = "negative mispricing (%.1fc), negative ROI (%.0f%%)" % (mp, roi)
        elif roi <= -10:
            rec = "DISABLE"
            why = "deeply negative ROI (%.0f%%)" % roi
        elif sr < 30 and roi < 0:
            rec = "RETUNE"
            why = "low scalp rate (%.0f%%), ROI=%.0f%%" % (sr, roi)
        else:
            rec = "INVESTIGATE"
            why = "mixed signals: TWP=%.0f%%, mp=%.1f, roi=%.0f%%" % (twp, mp, roi)
    else:
        if mp > 3 and roi > 5 and n >= 30:
            rec = "RE-ENABLE"
            why = "+%.1fc mispricing, +%.0f%% ROI, N=%d" % (mp, roi, n)
        elif mp > 0 and roi > 0 and n >= 20:
            rec = "RE-ENABLE"
            why = "positive signals: mp=%.1f, ROI=%.0f%%" % (mp, roi)
        else:
            rec = "STAY-OFF"
            why = "mp=%.1fc, ROI=%.0f%%" % (mp, roi)

    flag = "*" if n < 30 else ""
    print("| %s | %s | %d%s | %.0f%% | %+.1f | %.0f%% | %+.0f%% | %s | %s |" % (
        cell, "ON" if is_active else "off", n, flag,
        twp, mp, sr, roi, rec, why))


# =====================================================================
# TASK 12: Strategy capability summary
# =====================================================================
print()
print("=" * 80)
print("=== TASK 12: STRATEGY CAPABILITY SUMMARY ===")
print("=" * 80)
print()

# Active cells with positive ROI
active_positive = [(c, d) for c, d in task1.items() if d["is_active"] and d["roi_pct"] > 0]
all_positive = [(c, d) for c, d in task1.items() if d["roi_pct"] > 0]

# Daily opportunity rate: total events / 28 days
total_entries = sum(d["n"] for d in task1.values())
days = 28  # Mar 20 to Apr 17
daily_entries = total_entries / days / 2  # divide by 2 for per-side

print("Dataset: %d events, %d days, %.1f matches/day" % (len(events), days, len(events) / days))
print()

# Portfolio-level economics
print("=== Active cells portfolio ===")
total_ev = 0
total_capital = 0
for cell, d in task1.items():
    if not d["is_active"]:
        continue
    daily_fires = d["n"] / days / 2  # per-side entries per day
    daily_dollar = daily_fires * d["dollar_per_fill"]
    daily_cap = daily_fires * d["avg_entry"] * 10 / 100
    total_ev += daily_dollar
    total_capital += daily_cap

print("Daily expected PnL (active cells): $%.2f" % total_ev)
print("Daily capital turnover: $%.2f" % total_capital)
print("Portfolio ROI/day: %.2f%%" % (total_ev / total_capital * 100 if total_capital else 0))
print()

# Variance estimate from cell-level outcomes
daily_pnls_by_cell = {}
for cell, d in task1.items():
    if not d["is_active"]:
        continue
    entries = cell_data.get(cell, {}).get("entries", [])
    exit_c = d["exit_c"]

    cell_pnls = []
    for ep, won, mx, mn, evt, dur in entries:
        target = min(99, ep + exit_c)
        if mx and mx >= target:
            pnl = exit_c * 10 / 100  # scalp profit in $
        elif won:
            pnl = (99 - ep) * 10 / 100  # settlement win
        else:
            pnl = -(ep - 1) * 10 / 100  # settlement loss
        cell_pnls.append(pnl)

    if cell_pnls:
        daily_pnls_by_cell[cell] = cell_pnls

# Simulate daily PnL distribution
import random
random.seed(42)
simulated_daily = []
for _ in range(10000):
    day_pnl = 0
    for cell, pnls in daily_pnls_by_cell.items():
        # Each cell fires ~N/28 times per day, sample that many
        fires_per_day = max(1, len(pnls) // (days * 2))
        for _ in range(fires_per_day):
            day_pnl += random.choice(pnls)
    simulated_daily.append(day_pnl)

simulated_daily.sort()
n_sim = len(simulated_daily)
avg_daily = sum(simulated_daily) / n_sim
std_daily = (sum((x - avg_daily) ** 2 for x in simulated_daily) / n_sim) ** 0.5
sharpe = avg_daily / std_daily if std_daily else 0

print("=== Monte Carlo daily PnL distribution (10K simulations) ===")
print("  Mean daily PnL:    $%.2f" % avg_daily)
print("  Std dev:           $%.2f" % std_daily)
print("  Sharpe (daily):    %.2f" % sharpe)
print("  p5 (worst day):    $%.2f" % simulated_daily[n_sim // 20])
print("  p25:               $%.2f" % simulated_daily[n_sim // 4])
print("  Median:            $%.2f" % simulated_daily[n_sim // 2])
print("  p75:               $%.2f" % simulated_daily[3 * n_sim // 4])
print("  p95 (best day):    $%.2f" % simulated_daily[19 * n_sim // 20])
print()

# All positive cells (including disabled)
print("=== If all positive-ROI cells enabled ===")
total_ev_all = 0
for cell, d in all_positive:
    daily_fires = d["n"] / days / 2
    daily_dollar = daily_fires * d["dollar_per_fill"]
    total_ev_all += daily_dollar

print("Daily expected PnL (all +ROI cells): $%.2f" % total_ev_all)
print("Positive ROI cells: %d active + %d disabled = %d total" % (
    len(active_positive), len(all_positive) - len(active_positive), len(all_positive)))
print()

# True edge calculation
print("=== Strategy's true edge ===")
misprice_cells = [(c, d) for c, d in task1.items() if d["mispricing"] > 0]
print("Cells with positive mispricing: %d / %d" % (len(misprice_cells), len(task1)))
if misprice_cells:
    avg_mp = sum(d["mispricing"] for _, d in misprice_cells) / len(misprice_cells)
    avg_freq = sum(d["n"] for _, d in misprice_cells) / len(misprice_cells) / days
    print("Average mispricing (positive cells): %.1fc" % avg_mp)
    print("Average daily frequency per positive cell: %.1f entries" % avg_freq)
    print("Edge = mispricing × frequency × scalp_rate × sizing")
    total_edge = sum(d["dollar_per_fill"] * d["n"] / days / 2 for _, d in misprice_cells)
    print("Total daily edge from positive-mispricing cells: $%.2f" % total_edge)

conn.close()
print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
