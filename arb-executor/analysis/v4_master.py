#!/usr/bin/env python3
"""V4 master decision table, remaining heatmaps, fill rate, tour stats, cut list."""
import csv, json, os, math
from pathlib import Path
from collections import defaultdict

FACTS_PATH = "/root/Omi-Workspace/arb-executor/analysis/match_facts.csv"
CONFIG_PATH = "/root/Omi-Workspace/arb-executor/config/deploy_v4.json"
DAYS = 28
CONTRACTS = 10
DCA_QTY = 5

config = json.load(open(CONFIG_PATH))

facts_by_cell = defaultdict(list)
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        cat = r["category"]
        side = r["side"]
        entry = float(r["entry_mid"])
        bucket = int(entry / 5) * 5
        cell = "%s_%s_%d-%d" % (cat, side, bucket, bucket + 4)
        facts_by_cell[cell].append({
            "max_bounce": float(r["max_bounce_from_entry"]),
            "max_dip": float(r["max_dip_from_entry"]),
            "result": r["match_result"],
            "entry_mid": entry,
        })

BUCKETS = list(range(5, 95, 5))
SIDES = ["underdog", "leader"]

def compute(cell_name):
    matches = facts_by_cell.get(cell_name, [])
    n = len(matches)
    cfg = config["active_cells"].get(cell_name)
    if not cfg or n == 0:
        return None
    ex = cfg["exit_cents"]
    dca = cfg.get("dca_trigger_cents", 0)
    avg_entry = sum(m["entry_mid"] for m in matches) / n
    hits = sum(1 for m in matches if m["max_bounce"] >= ex)
    hit_rate = hits / n
    total_pnl = 0
    for m in matches:
        if m["max_bounce"] >= ex:
            total_pnl += ex
        else:
            settle = 99.5 if m["result"] == "win" else 0.5
            total_pnl += (settle - m["entry_mid"])
    ev_cents = total_pnl / n
    ev_dollars = ev_cents * CONTRACTS / 100.0
    entry_cost = avg_entry * CONTRACTS / 100.0
    roi = 100 * ev_dollars / entry_cost if entry_cost > 0 else 0
    tpd = n / DAYS
    dpd = ev_dollars * tpd
    daily_capital = entry_cost * tpd
    daily_roi = 100 * dpd / daily_capital if daily_capital > 0 else 0
    return {
        "cell": cell_name,
        "cat": cell_name.rsplit("_", 2)[0],
        "side": "underdog" if "underdog" in cell_name else "leader",
        "bucket": cell_name.split("_")[-1],
        "exit": ex, "dca": dca, "n": n,
        "hit_rate": hit_rate, "ev_cents": ev_cents,
        "ev_dollars": ev_dollars, "roi": roi,
        "tpd": tpd, "dpd": dpd, "daily_roi": daily_roi,
        "avg_entry": avg_entry, "daily_capital": daily_capital,
    }

# ============================================================
# TASK 1: WTA heatmaps
# ============================================================
def ascii_heatmap(tour):
    print("\n" + "=" * 72)
    print("  %s HEATMAP" % tour)
    print("=" * 72)
    print("%-10s | %-30s | %-30s" % ("BUCKET", "UNDERDOG", "LEADER"))
    print("-" * 72)
    for b in BUCKETS:
        row = "%-10s |" % ("%d-%dc" % (b, b+4))
        for side in SIDES:
            cell = "%s_%s_%d-%d" % (tour, side, b, b+4)
            r = compute(cell)
            matches = facts_by_cell.get(cell, [])
            n = len(matches)
            if r:
                flag = "*" if n < 10 else ""
                txt = "+%d/-%d %d%% $%.2f N=%d%s" % (
                    r["exit"], r["dca"], 100*r["hit_rate"], r["dpd"], n, flag)
            elif cell in config.get("disabled_cells", []):
                txt = "DISABLED (N=%d)" % n
            elif n > 0:
                txt = "no cfg (N=%d)" % n
            else:
                txt = "-"
            row += " %-30s|" % txt
        print(row)

for tour in ["WTA_MAIN", "WTA_CHALL"]:
    ascii_heatmap(tour)

# ============================================================
# TASK 2: Master decision table
# ============================================================
print("\n" + "=" * 130)
print("MASTER DECISION TABLE — ALL 37 ACTIVE CELLS")
print("=" * 130)

rows = []
for cell_name in config["active_cells"]:
    r = compute(cell_name)
    if r:
        rows.append(r)

rows.sort(key=lambda x: -x["dpd"])

print("%-30s %4s %4s %4s %5s %6s %6s %6s %5s %6s %6s" % (
    "CELL", "EXIT", "DCA", "N", "HIT%", "EV_c", "EV_$", "ROI%", "TR/D", "$/DAY", "D_ROI"))
print("-" * 130)

totals = {"tpd": 0, "dpd": 0, "ev_w": 0, "n_w": 0, "cap": 0}
for r in rows:
    print("%-30s +%3d  -%2d %4d %4.0f%% %+5.1fc $%+5.3f %+5.1f%% %4.2f $%+5.2f %+4.1f%%" % (
        r["cell"][:30], r["exit"], r["dca"], r["n"],
        100*r["hit_rate"], r["ev_cents"], r["ev_dollars"],
        r["roi"], r["tpd"], r["dpd"], r["daily_roi"]))
    totals["tpd"] += r["tpd"]
    totals["dpd"] += r["dpd"]
    totals["ev_w"] += r["ev_cents"] * r["n"]
    totals["n_w"] += r["n"]
    totals["cap"] += r["daily_capital"]

avg_ev = totals["ev_w"] / totals["n_w"] if totals["n_w"] else 0
total_roi = 100 * totals["dpd"] / totals["cap"] if totals["cap"] else 0

print("-" * 130)
print("%-30s %4s %4s %4d %5s %+5.1fc %6s %6s %4.1f $%+5.2f %+4.1f%%" % (
    "AGGREGATE", "", "", totals["n_w"], "",
    avg_ev, "", "", totals["tpd"], totals["dpd"], total_roi))
print("\nTotal capital deployed/day: $%.2f" % totals["cap"])

# ============================================================
# TASK 3: Fill rate from yesterday
# ============================================================
print("\n" + "=" * 80)
print("TASK 3: FILL RATE CHECK")
print("=" * 80)

import time
from datetime import datetime
from zoneinfo import ZoneInfo
ET = ZoneInfo("America/New_York")

log_dir = Path(__file__).resolve().parent.parent / "logs"
entries = {}
for log in sorted(log_dir.glob("live_v3_*.jsonl")):
    with open(log) as f:
        for line in f:
            e = json.loads(line)
            ev = e["event"]
            tk = e.get("ticker", "")
            d = e.get("details", {})
            epoch = e.get("ts_epoch", 0)
            if ev == "order_placed" and d.get("action") == "buy":
                entries[tk] = {"post_time": epoch, "price": d.get("price", 0)}
            elif ev == "entry_filled" and tk in entries:
                entries[tk]["fill_time"] = epoch
            elif ev == "settled" and tk in entries:
                entries[tk]["settled"] = True

# Filter to schedule-gated entries only (post_time after 06:00 PM Apr 17)
gated_cutoff = datetime(2026, 4, 17, 18, 0, tzinfo=ET).timestamp()
gated = {tk: v for tk, v in entries.items() if v["post_time"] > gated_cutoff}

filled = sum(1 for v in gated.values() if "fill_time" in v)
fill_times = [(v["fill_time"] - v["post_time"]) / 60 for v in gated.values() if "fill_time" in v]

print("\nSchedule-gated entries: %d" % len(gated))
print("Filled: %d (%.0f%%)" % (filled, 100*filled/len(gated) if gated else 0))
if fill_times:
    fill_times.sort()
    n = len(fill_times)
    print("Time to fill: min=%.0fm median=%.0fm max=%.0fm mean=%.0fm" % (
        fill_times[0], fill_times[n//2], fill_times[-1], sum(fill_times)/n))
else:
    print("(No fill time data — fills detected by reconcile, not check_fills)")

# Check Kalshi positions as proxy for fills
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
ak = os.getenv("KALSHI_API_KEY")
pkk = serialization.load_pem_private_key(
    (Path(__file__).resolve().parent.parent / "kalshi.pem").read_bytes(), password=None, backend=default_backend())
BASE = "https://api.elections.kalshi.com"
def auth(method, path):
    ts = str(int(time.time() * 1000))
    msg = ("%s%s%s" % (ts, method, path)).encode("utf-8")
    sig = pkk.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                   salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": ak, "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode("utf-8"),
            "KALSHI-ACCESS-TIMESTAMP": ts}

import base64
pos = requests.get(BASE + "/trade-api/v2/portfolio/positions?count_filter=position&settlement_status=unsettled",
    headers=auth("GET", "/trade-api/v2/portfolio/positions"), timeout=15).json().get("market_positions", [])
pos_tickers = set(p.get("ticker","") for p in pos)
resting_buys = set()
orders = requests.get(BASE + "/trade-api/v2/portfolio/orders?status=resting&limit=500",
    headers=auth("GET", "/trade-api/v2/portfolio/orders"), timeout=15).json().get("orders", [])
for o in orders:
    if o.get("action") == "buy":
        resting_buys.add(o.get("ticker",""))

gated_filled_kalshi = sum(1 for tk in gated if tk in pos_tickers or entries[tk].get("settled"))
gated_resting = sum(1 for tk in gated if tk in resting_buys)
print("\nFrom Kalshi state:")
print("  Filled (have position or settled): %d" % gated_filled_kalshi)
print("  Still resting (unfilled): %d" % gated_resting)
print("  Fill rate: %.0f%%" % (100*gated_filled_kalshi/len(gated) if gated else 0))

# ============================================================
# TASK 4: Tour imbalance
# ============================================================
print("\n" + "=" * 80)
print("TASK 4: TOUR IMBALANCE")
print("=" * 80)

tour_stats = defaultdict(lambda: {"dpd": 0, "cells": 0, "n": 0})
for r in rows:
    t = tour_stats[r["cat"]]
    t["dpd"] += r["dpd"]
    t["cells"] += 1
    t["n"] += r["n"]

print("\n%-15s %6s %8s %6s %6s" % ("TOUR", "CELLS", "$/DAY", "AVG/C", "N"))
for tour in ["ATP_CHALL", "ATP_MAIN", "WTA_MAIN", "WTA_CHALL"]:
    t = tour_stats.get(tour, {"dpd": 0, "cells": 0, "n": 0})
    avg = t["dpd"] / t["cells"] if t["cells"] else 0
    print("%-15s %6d $%+6.2f $%+5.2f %6d" % (tour, t["cells"], t["dpd"], avg, t["n"]))

# ============================================================
# TASK 5: Cells to cut
# ============================================================
print("\n" + "=" * 80)
print("TASK 5: CELLS TO CUT FROM V4")
print("=" * 80)

cut_list = []
for r in rows:
    reasons = []
    if r["n"] < 10 and r["dpd"] < 0.30:
        reasons.append("N<%d + $/d<$0.30" % r["n"])
    if r["ev_cents"] < 0:
        reasons.append("negative EV (%.1fc)" % r["ev_cents"])
    if r["dca"] >= 25 and r["dpd"] < 0.50:
        reasons.append("DCA>=-25c + $/d<$0.50")
    if reasons:
        cut_list.append((r["cell"], r["dpd"], r["n"], r["dca"], ", ".join(reasons)))

print("\nCells flagged for removal: %d" % len(cut_list))
print("%-35s %6s %4s %4s %s" % ("CELL", "$/DAY", "N", "DCA", "REASON"))
for cell, dpd, n, dca, reason in cut_list:
    print("%-35s $%+5.2f %4d  -%2d  %s" % (cell, dpd, n, dca, reason))

# Generate clean config
v4_clean = {
    "sizing": config["sizing"],
    "dca_fill_floor_cents": config["dca_fill_floor_cents"],
    "active_cells": {},
    "disabled_cells": list(config.get("disabled_cells", [])),
}

cut_names = set(c[0] for c in cut_list)
for cell_name, cfg in config["active_cells"].items():
    if cell_name in cut_names:
        v4_clean["disabled_cells"].append(cell_name)
    else:
        v4_clean["active_cells"][cell_name] = cfg

v4_clean["disabled_cells"].sort()

clean_path = "/root/Omi-Workspace/arb-executor/config/deploy_v4_clean.json"
with open(clean_path, "w") as f:
    json.dump(v4_clean, f, indent=2)

# Summary of clean config
clean_rows = [r for r in rows if r["cell"] not in cut_names]
clean_dpd = sum(r["dpd"] for r in clean_rows)
clean_tpd = sum(r["tpd"] for r in clean_rows)

print("\n--- deploy_v4_clean.json ---")
print("Active cells: %d (removed %d)" % (len(v4_clean["active_cells"]), len(cut_names)))
print("Disabled cells: %d" % len(v4_clean["disabled_cells"]))
print("Projected $/day: $%.2f (was $%.2f, cut $%.2f)" % (
    clean_dpd, totals["dpd"], totals["dpd"] - clean_dpd))
print("Trades/day: %.1f" % clean_tpd)
print("Saved: %s" % clean_path)

print("\nDONE")
