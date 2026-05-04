#!/usr/bin/env python3
"""Per-fill outcome analysis. Read-only against live_v3_*.jsonl logs."""
import json, glob, os, csv, hashlib
from collections import defaultdict, Counter

LOGS = sorted(glob.glob("/root/Omi-Workspace/arb-executor/logs/live_v3_*.jsonl"))
EXIT_EVENTS = {"exit_filled", "paper_exit_fill", "scalp_filled"}
SETTLE_EVENTS = {"settled", "paper_settled"}

fills_out = []  # list of dicts for output

for log_path in LOGS:
    # Pass 1: collect all events grouped by ticker, sorted by ts_epoch
    by_ticker = defaultdict(list)
    with open(log_path) as f:
        for line in f:
            try:
                d = json.loads(line)
            except:
                continue
            ev = d.get("event", "")
            tk = d.get("ticker", "")
            ts = d.get("ts_epoch", 0)
            if not tk:
                continue
            if ev in {"entry_filled"} | EXIT_EVENTS | SETTLE_EVENTS:
                by_ticker[tk].append((ts, ev, d))

    # Sort each ticker's events by ts
    for tk in by_ticker:
        by_ticker[tk].sort()

    # Pass 2: walk entry_filled events and find terminal
    log_date = os.path.basename(log_path).replace("live_v3_", "").replace(".jsonl", "")
    for tk, events in by_ticker.items():
        for i, (ts, ev, d) in enumerate(events):
            if ev != "entry_filled":
                continue
            det = d.get("details", {}) or {}
            entry_price = det.get("fill_price", 0)
            qty = det.get("qty", 0)
            cell = det.get("cell", "")
            direction = det.get("direction", "")
            play_type = det.get("play_type", "")

            # Find first exit / settle event after this entry on same ticker
            terminal_event = "no_terminal_event"
            exit_price = None
            pnl_cents = None
            terminal_ts = None
            for ts2, ev2, d2 in events[i+1:]:
                if ev2 in EXIT_EVENTS:
                    terminal_event = "exit_filled"
                    det2 = d2.get("details", {}) or {}
                    if ev2 == "paper_exit_fill":
                        exit_price = det2.get("fill_price")
                        pnl_cents = det2.get("realized_pnl_cents")
                    else:
                        exit_price = det2.get("exit_price")
                        pnl_cents = det2.get("pnl_cents")
                    terminal_ts = ts2
                    break
                elif ev2 in SETTLE_EVENTS:
                    terminal_event = "settled"
                    det2 = d2.get("details", {}) or {}
                    exit_price = det2.get("settle_price")
                    pnl_cents = det2.get("pnl_cents")
                    terminal_ts = ts2
                    break

            # Compute pnl/ROI if we can
            if pnl_cents is None and exit_price is not None and entry_price:
                try:
                    pnl_cents = (int(exit_price) - int(entry_price)) * int(qty)
                except:
                    pnl_cents = None
            pnl_per_contract = None
            if pnl_cents is not None and qty:
                try:
                    pnl_per_contract = pnl_cents / qty
                except:
                    pnl_per_contract = None
            roi_pct = None
            if pnl_per_contract is not None and entry_price:
                try:
                    roi_pct = pnl_per_contract / float(entry_price) * 100.0
                except:
                    roi_pct = None

            fills_out.append({
                "ts": d.get("ts", ""),
                "ts_epoch": ts,
                "log_date": log_date,
                "ticker": tk,
                "cell": cell,
                "direction": direction,
                "play_type": play_type,
                "entry_price": entry_price,
                "qty": qty,
                "terminal_event": terminal_event,
                "terminal_ts_epoch": terminal_ts or "",
                "exit_price": exit_price if exit_price is not None else "",
                "pnl_cents_total": pnl_cents if pnl_cents is not None else "",
                "pnl_cents_per_contract": "%.2f" % pnl_per_contract if pnl_per_contract is not None else "",
                "roi_pct": "%.2f" % roi_pct if roi_pct is not None else "",
            })

# Write CSV
csv_path = "/tmp/fill_outcomes.csv"
fieldnames = ["ts", "ts_epoch", "log_date", "ticker", "cell", "direction", "play_type",
              "entry_price", "qty", "terminal_event", "terminal_ts_epoch",
              "exit_price", "pnl_cents_total", "pnl_cents_per_contract", "roi_pct"]
with open(csv_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for row in fills_out:
        w.writerow(row)

# sha256
h = hashlib.sha256()
with open(csv_path, "rb") as f:
    for chunk in iter(lambda: f.read(8192), b""):
        h.update(chunk)
sha = h.hexdigest()

# Per-scenario summary
print("Total entry_filled events analyzed: %d" % len(fills_out))
print("CSV written to: %s" % csv_path)
print("CSV sha256: %s" % sha)
print()

print("=== Per-scenario (play_type) summary ===")
by_scenario = defaultdict(list)
for r in fills_out:
    by_scenario[r["play_type"] or "(unknown)"].append(r)

for sc in sorted(by_scenario.keys()):
    rows = by_scenario[sc]
    n = len(rows)
    term_counts = Counter(r["terminal_event"] for r in rows)
    exit_filled_rows = [r for r in rows if r["terminal_event"] == "exit_filled"]
    settled_rows = [r for r in rows if r["terminal_event"] == "settled"]
    print()
    print("scenario: %s  N=%d" % (sc, n))
    print("  terminal: exit_filled=%d  settled=%d  no_terminal=%d" % (
        term_counts.get("exit_filled", 0),
        term_counts.get("settled", 0),
        term_counts.get("no_terminal_event", 0)))
    if exit_filled_rows:
        valid_pnl = [r for r in exit_filled_rows if r["pnl_cents_per_contract"] != ""]
        if valid_pnl:
            avg_entry = sum(int(r["entry_price"]) for r in valid_pnl) / len(valid_pnl)
            avg_exit = sum(int(r["exit_price"]) for r in valid_pnl if r["exit_price"] != "") / len(valid_pnl)
            avg_pnl_pc = sum(float(r["pnl_cents_per_contract"]) for r in valid_pnl) / len(valid_pnl)
            avg_roi = sum(float(r["roi_pct"]) for r in valid_pnl if r["roi_pct"] != "") / len(valid_pnl)
            print("  exit_filled subgroup (N=%d):" % len(valid_pnl))
            print("    avg entry: %.1fc  avg exit: %.1fc  avg pnl: %+.2fc/contract  avg ROI: %+.1f%%" % (
                avg_entry, avg_exit, avg_pnl_pc, avg_roi))
    if settled_rows:
        valid_pnl = [r for r in settled_rows if r["pnl_cents_per_contract"] != ""]
        if valid_pnl:
            avg_entry = sum(int(r["entry_price"]) for r in valid_pnl) / len(valid_pnl)
            avg_settle = sum(int(r["exit_price"]) for r in valid_pnl if r["exit_price"] != "") / len(valid_pnl)
            avg_pnl_pc = sum(float(r["pnl_cents_per_contract"]) for r in valid_pnl) / len(valid_pnl)
            avg_roi = sum(float(r["roi_pct"]) for r in valid_pnl if r["roi_pct"] != "") / len(valid_pnl)
            print("  settled subgroup (N=%d):" % len(valid_pnl))
            print("    avg entry: %.1fc  avg settle: %.1fc  avg pnl: %+.2fc/contract  avg ROI: %+.1f%%" % (
                avg_entry, avg_settle, avg_pnl_pc, avg_roi))

print()
print("=== Per-cell summary (N >= 5) ===")
by_cell = defaultdict(list)
for r in fills_out:
    by_cell[r["cell"] or "(unknown)"].append(r)

cells_sorted = sorted([(c, rs) for c, rs in by_cell.items() if len(rs) >= 5],
                      key=lambda x: -len(x[1]))
for cell, rows in cells_sorted:
    n = len(rows)
    term_counts = Counter(r["terminal_event"] for r in rows)
    exit_filled_rows = [r for r in rows if r["terminal_event"] == "exit_filled"]
    settled_rows = [r for r in rows if r["terminal_event"] == "settled"]
    print()
    print("cell: %-40s N=%d" % (cell, n))
    print("  terminal: exit_filled=%d  settled=%d  no_terminal=%d" % (
        term_counts.get("exit_filled", 0),
        term_counts.get("settled", 0),
        term_counts.get("no_terminal_event", 0)))
    if exit_filled_rows:
        valid_pnl = [r for r in exit_filled_rows if r["pnl_cents_per_contract"] != ""]
        if valid_pnl:
            avg_entry = sum(int(r["entry_price"]) for r in valid_pnl) / len(valid_pnl)
            valid_exit = [r for r in valid_pnl if r["exit_price"] != ""]
            if valid_exit:
                avg_exit = sum(int(r["exit_price"]) for r in valid_exit) / len(valid_exit)
                avg_pnl_pc = sum(float(r["pnl_cents_per_contract"]) for r in valid_pnl) / len(valid_pnl)
                avg_roi = sum(float(r["roi_pct"]) for r in valid_pnl if r["roi_pct"] != "") / len(valid_pnl)
                print("  exit_filled subgroup (N=%d):" % len(valid_pnl))
                print("    avg entry: %.1fc  avg exit: %.1fc  avg pnl: %+.2fc/contract  avg ROI: %+.1f%%" % (
                    avg_entry, avg_exit, avg_pnl_pc, avg_roi))
    if settled_rows:
        valid_pnl = [r for r in settled_rows if r["pnl_cents_per_contract"] != ""]
        if valid_pnl:
            avg_entry = sum(int(r["entry_price"]) for r in valid_pnl) / len(valid_pnl)
            valid_exit = [r for r in valid_pnl if r["exit_price"] != ""]
            if valid_exit:
                avg_settle = sum(int(r["exit_price"]) for r in valid_exit) / len(valid_exit)
                avg_pnl_pc = sum(float(r["pnl_cents_per_contract"]) for r in valid_pnl) / len(valid_pnl)
                avg_roi = sum(float(r["roi_pct"]) for r in valid_pnl if r["roi_pct"] != "") / len(valid_pnl)
                print("  settled subgroup (N=%d):" % len(valid_pnl))
                print("    avg entry: %.1fc  avg settle: %.1fc  avg pnl: %+.2fc/contract  avg ROI: %+.1f%%" % (
                    avg_entry, avg_settle, avg_pnl_pc, avg_roi))

print()
print("=== Tickers worth a closer look ===")
no_terminal = [r for r in fills_out if r["terminal_event"] == "no_terminal_event"]
if no_terminal:
    print("Fills with NO terminal event in same log file (%d total — phantom-active candidates):" % len(no_terminal))
    for r in no_terminal[:30]:
        print("  %s  %s  cell=%s  scenario=%s  entry=%sc  qty=%s" % (
            r["ts"], r["ticker"], r["cell"], r["play_type"], r["entry_price"], r["qty"]))
    if len(no_terminal) > 30:
        print("  ... and %d more" % (len(no_terminal) - 30))

print()
big_loss = sorted([r for r in fills_out if r["roi_pct"] != "" and float(r["roi_pct"]) < -50],
                  key=lambda x: float(x["roi_pct"]))
if big_loss:
    print("Worst ROI fills (ROI < -50%%, %d total):" % len(big_loss))
    for r in big_loss[:15]:
        print("  ROI=%+.1f%%  pnl=%sc  entry=%sc  exit/settle=%sc  cell=%s  scenario=%s  ticker=%s" % (
            float(r["roi_pct"]), r["pnl_cents_total"], r["entry_price"], r["exit_price"],
            r["cell"], r["play_type"], r["ticker"]))

print()
big_win = sorted([r for r in fills_out if r["roi_pct"] != "" and float(r["roi_pct"]) > 100],
                 key=lambda x: -float(x["roi_pct"]))
if big_win:
    print("Best ROI fills (ROI > 100%%, %d total):" % len(big_win))
    for r in big_win[:10]:
        print("  ROI=%+.1f%%  pnl=%sc  entry=%sc  exit/settle=%sc  cell=%s  scenario=%s  ticker=%s" % (
            float(r["roi_pct"]), r["pnl_cents_total"], r["entry_price"], r["exit_price"],
            r["cell"], r["play_type"], r["ticker"]))
