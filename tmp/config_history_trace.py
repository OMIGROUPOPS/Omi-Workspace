#!/usr/bin/env python3
"""
Trace full config change history and correlate with live performance.
"""
import json, csv, os, glob, subprocess
from collections import defaultdict
from datetime import datetime, timezone, timedelta

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/per_cell_verification"
ET = timezone(timedelta(hours=-4))

# 1. Get all config-touching commits in last 14 days
print("=== 1. CONFIG CHANGE COMMITS ===\n")

result = subprocess.check_output(
    ["git", "log", "--format=%H %ai %s", "--since=2026-04-14",
     "--", "arb-executor/config/deploy_v4.json"],
    cwd="/root/Omi-Workspace").decode().strip()

commits = []
for line in result.split("\n"):
    if not line.strip(): continue
    parts = line.split(" ", 3)
    commits.append({"hash": parts[0], "date": parts[1] + " " + parts[2], "msg": parts[3] if len(parts) > 3 else ""})

for c in commits:
    print("  %s %s %s" % (c["hash"][:8], c["date"][:16], c["msg"][:70]))

# 2. For each commit, extract active_cells and their exit_cents
print("\n=== 2. PER-COMMIT CONFIG STATE ===\n")

config_versions = []  # list of {hash, date, epoch, cells: {cell: exit_cents}}

for c in reversed(commits):  # oldest first
    try:
        raw = subprocess.check_output(
            ["git", "show", "%s:arb-executor/config/deploy_v4.json" % c["hash"]],
            cwd="/root/Omi-Workspace", stderr=subprocess.DEVNULL).decode()
        cfg = json.loads(raw)
        ac = cfg.get("active_cells", {})
        cells = {}
        for cell, params in ac.items():
            cells[cell] = params.get("exit_cents", 0)

        # Parse date
        dt = datetime.fromisoformat(c["date"])
        epoch = dt.timestamp()

        config_versions.append({
            "hash": c["hash"][:8], "date": c["date"][:16],
            "epoch": epoch, "cells": cells, "msg": c["msg"][:60]
        })
    except Exception as e:
        print("  skip %s: %s" % (c["hash"][:8], e))

# Find changes between consecutive versions
print("Changes per commit:")
all_changes = []  # list of {hash, date, cell, old_exit, new_exit, change_type}

for i in range(1, len(config_versions)):
    prev = config_versions[i-1]["cells"]
    curr = config_versions[i]["cells"]
    h = config_versions[i]["hash"]
    d = config_versions[i]["date"]
    msg = config_versions[i]["msg"]

    changes = []
    # Added cells
    for cell in curr:
        if cell not in prev:
            changes.append({"cell": cell, "old": "OFF", "new": curr[cell], "type": "ADDED"})
    # Removed cells
    for cell in prev:
        if cell not in curr:
            changes.append({"cell": cell, "old": prev[cell], "new": "OFF", "type": "REMOVED"})
    # Changed exit_cents
    for cell in curr:
        if cell in prev and curr[cell] != prev[cell]:
            changes.append({"cell": cell, "old": prev[cell], "new": curr[cell], "type": "RETUNED"})

    if changes:
        print("\n  %s %s: %s" % (h, d, msg))
        for ch in changes:
            print("    %s: %s -> %s (%s)" % (ch["cell"], ch["old"], ch["new"], ch["type"]))
            all_changes.append({**ch, "hash": h, "date": d, "msg": msg})

# 3. Load live fills and tag with config version
print("\n\n=== 3. FILLS TAGGED WITH CONFIG VERSION ===\n")

fills = []
exits_map = {}
settle_map = {}

for lf in sorted(glob.glob(os.path.join(BASE_DIR, "logs/live_v3_*.jsonl"))):
    with open(lf) as f:
        for line in f:
            try:
                d = json.loads(line.strip())
            except: continue
            ev = d.get("event", "")
            det = d.get("details", {})
            tk = d.get("ticker", "")
            ts = d.get("ts", "")
            ts_epoch = d.get("ts_epoch", 0)

            if ev == "entry_filled":
                fills.append({
                    "ticker": tk, "ts": ts, "ts_epoch": ts_epoch,
                    "fill_price": det.get("fill_price", 0),
                    "cell": det.get("cell", ""),
                })
            elif ev in ("exit_filled", "scalp_filled") and tk not in exits_map:
                exits_map[tk] = {"pnl_cents": det.get("pnl_cents", det.get("profit_cents", 0)),
                                  "exit_price": det.get("exit_price", 0)}
            elif ev == "settled" and tk not in settle_map:
                settle_map[tk] = {"result": det.get("settle", ""),
                                   "pnl_cents": det.get("pnl_cents", 0)}

# For each fill, find which config version was active
def find_config_version(fill_epoch):
    """Return the config version active at this epoch."""
    active = config_versions[0]  # default to oldest
    for cv in config_versions:
        if cv["epoch"] <= fill_epoch:
            active = cv
        else:
            break
    return active

# Parse fill timestamps
for f in fills:
    if f["ts_epoch"] == 0:
        try:
            ts = f["ts"].replace(" ET", "").strip()
            dt = datetime.strptime(ts, "%Y-%m-%d %I:%M:%S %p")
            dt = dt.replace(tzinfo=ET)
            f["ts_epoch"] = dt.timestamp()
        except:
            f["ts_epoch"] = 0

# Apr 26 retune epoch
apr26_retune_epoch = datetime(2026, 4, 26, 13, 31, tzinfo=ET).timestamp()

tagged_fills = []
for f in fills:
    cv = find_config_version(f["ts_epoch"])
    exit_cents = cv["cells"].get(f["cell"], "?")
    days_since = (f["ts_epoch"] - cv["epoch"]) / 86400 if f["ts_epoch"] and cv["epoch"] else 0

    # Outcome
    tk = f["ticker"]
    pnl = 0
    outcome = "unknown"
    if tk in exits_map:
        pnl = exits_map[tk]["pnl_cents"]
        outcome = "scalp"
    elif tk in settle_map:
        pnl = settle_map[tk]["pnl_cents"]
        outcome = "settle_" + settle_map[tk]["result"].lower()

    pnl_dollars = pnl * 10 / 100
    cost = f["fill_price"] * 10 / 100
    pnl_pct = pnl_dollars / cost * 100 if cost else 0

    before_retune = f["ts_epoch"] < apr26_retune_epoch

    tagged_fills.append({
        "ticker": tk, "ts": f["ts"], "cell": f["cell"],
        "fill_price": f["fill_price"],
        "exit_cents": exit_cents, "config_hash": cv["hash"],
        "config_date": cv["date"], "days_since_change": days_since,
        "outcome": outcome, "pnl_cents": pnl, "pnl_dollars": pnl_dollars,
        "pnl_pct": pnl_pct, "before_apr26_retune": before_retune,
    })

# Write tagged fills CSV
with open(os.path.join(OUT_DIR, "fills_by_config_version.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ticker","fill_ts","cell","fill_price","exit_cents_at_fill",
                "config_hash","config_date","days_since_config_change",
                "outcome","pnl_cents","pnl_dollars","pnl_pct","before_apr26_retune"])
    for tf in tagged_fills:
        w.writerow([tf["ticker"], tf["ts"], tf["cell"], tf["fill_price"],
                     tf["exit_cents"], tf["config_hash"], tf["config_date"],
                     "%.1f" % tf["days_since_change"],
                     tf["outcome"], tf["pnl_cents"], "%.2f" % tf["pnl_dollars"],
                     "%.1f" % tf["pnl_pct"], tf["before_apr26_retune"]])

# 4. Aggregate by cell × config version
print("=== 4. PER-CELL BY CONFIG VERSION ===\n")

cell_config_agg = defaultdict(lambda: {"fills": 0, "pnl_total": 0, "pnl_list": []})
for tf in tagged_fills:
    key = (tf["cell"], tf["config_hash"], tf["exit_cents"])
    cell_config_agg[key]["fills"] += 1
    cell_config_agg[key]["pnl_total"] += tf["pnl_dollars"]
    cell_config_agg[key]["pnl_list"].append(tf["pnl_pct"])

with open(os.path.join(OUT_DIR, "pnl_by_cell_config.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","config_hash","exit_cents","N_fills","avg_pnl_pct","total_pnl_dollars"])
    print("| Cell | Config | Exit | N | Avg PnL% | Total$ |")
    print("|---|---|---|---|---|---|")
    for (cell, ch, ec), d in sorted(cell_config_agg.items()):
        n = d["fills"]
        avg_pct = sum(d["pnl_list"]) / n if n else 0
        print("| %s | %s | +%s | %d | %+.0f%% | $%+.2f |" % (
            cell, ch, ec, n, avg_pct, d["pnl_total"]))
        w.writerow([cell, ch, ec, n, "%.1f" % avg_pct, "%.2f" % d["pnl_total"]])

# 5. Before vs after Apr 26 retune
print("\n=== 5. BEFORE vs AFTER APR 26 RETUNE ===\n")

before = [tf for tf in tagged_fills if tf["before_apr26_retune"]]
after = [tf for tf in tagged_fills if not tf["before_apr26_retune"]]

print("Before retune (fills before Apr 26 13:31 ET):")
print("  N fills: %d" % len(before))
if before:
    total_b = sum(tf["pnl_dollars"] for tf in before)
    days_b = (apr26_retune_epoch - min(tf["ts_epoch"] for tf in before if tf["ts_epoch"])) / 86400
    print("  Total PnL: $%.2f" % total_b)
    print("  Days: %.1f" % days_b)
    print("  Daily PnL: $%.2f" % (total_b / days_b if days_b else 0))

print("\nAfter retune (fills from Apr 26 13:31 ET onward):")
print("  N fills: %d" % len(after))
if after:
    total_a = sum(tf["pnl_dollars"] for tf in after)
    days_a = (max(tf["ts_epoch"] for tf in after if tf["ts_epoch"]) - apr26_retune_epoch) / 86400
    print("  Total PnL: $%.2f" % total_a)
    print("  Days: %.1f" % days_a)
    print("  Daily PnL: $%.2f" % (total_a / days_a if days_a else 0))

# Per-cell before/after
print("\nPer-cell before vs after:")
print("| Cell | Before N | Before $/day | After N | After $/day | Delta |")
print("|---|---|---|---|---|---|")

cell_before = defaultdict(lambda: {"n": 0, "pnl": 0})
cell_after = defaultdict(lambda: {"n": 0, "pnl": 0})
for tf in before:
    cell_before[tf["cell"]]["n"] += 1
    cell_before[tf["cell"]]["pnl"] += tf["pnl_dollars"]
for tf in after:
    cell_after[tf["cell"]]["n"] += 1
    cell_after[tf["cell"]]["pnl"] += tf["pnl_dollars"]

all_cells = sorted(set(list(cell_before.keys()) + list(cell_after.keys())))
days_b_val = days_b if before else 1
days_a_val = days_a if after and days_a > 0 else 1

with open(os.path.join(OUT_DIR, "before_vs_after_retune.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","before_N","before_total_pnl","before_daily_pnl",
                "after_N","after_total_pnl","after_daily_pnl","delta_daily"])
    for cell in all_cells:
        b = cell_before[cell]
        a = cell_after[cell]
        bd = b["pnl"] / days_b_val if b["n"] else 0
        ad = a["pnl"] / days_a_val if a["n"] else 0
        delta = ad - bd
        if b["n"] or a["n"]:
            print("| %s | %d | $%+.2f/d | %d | $%+.2f/d | $%+.2f |" % (
                cell, b["n"], bd, a["n"], ad, delta))
            w.writerow([cell, b["n"], "%.2f" % b["pnl"], "%.2f" % bd,
                         a["n"], "%.2f" % a["pnl"], "%.2f" % ad, "%.2f" % delta])

# Write config change history CSV
with open(os.path.join(OUT_DIR, "config_change_history.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["commit_hash","commit_date","cell","old_exit_cents","new_exit_cents","change_type","commit_msg"])
    for ch in all_changes:
        w.writerow([ch["hash"], ch["date"], ch["cell"], ch["old"], ch["new"], ch["type"], ch["msg"]])

print("\nWritten: fills_by_config_version.csv, pnl_by_cell_config.csv, before_vs_after_retune.csv, config_change_history.csv")
