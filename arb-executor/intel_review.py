#!/usr/bin/env python3
"""intel_review.py — Historical post-hoc analysis of intelligence-driven decisions."""

import sys, os, json, glob, argparse
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict

ET = ZoneInfo("America/New_York")
LOG_DIR = Path(__file__).resolve().parent / "logs"


def parse_logs(hours=48):
    """Parse cell_match, scalp_filled, and settled events from recent logs."""
    now = datetime.now(ET)
    cutoff_epoch = (now - timedelta(hours=hours)).timestamp()

    log_files = sorted(glob.glob(str(LOG_DIR / "live_v3_*.jsonl")))
    if not log_files:
        print("No log files found in %s" % LOG_DIR)
        return [], [], []

    entries = []
    scalps = {}
    settlements = {}

    for lf in log_files[-3:]:
        try:
            with open(lf) as f:
                for line in f:
                    try:
                        d = json.loads(line.strip())
                    except Exception:
                        continue
                    ts_epoch = d.get("ts_epoch", 0)
                    if ts_epoch < cutoff_epoch:
                        continue
                    evt = d.get("event", "")
                    tk = d.get("ticker", "")
                    det = d.get("details", {})

                    if evt == "cell_match":
                        entries.append({
                            "ts": d.get("ts", ""),
                            "ts_epoch": ts_epoch,
                            "ticker": tk,
                            "event_ticker": det.get("event", ""),
                            "play_type": det.get("play_type", ""),
                            "entry_price": det.get("entry_price", 0),
                            "entry_size": det.get("entry_size", 0),
                            "fv_cents": det.get("fv_cents", 0),
                            "fv_source": det.get("fv_source", ""),
                            "anchor_source": det.get("anchor_source", ""),
                            "intel_score": det.get("intel_score"),
                            "intel_grade": det.get("intel_grade"),
                            "intel_window_sec": det.get("intel_window_sec"),
                            "intel_anchor": det.get("intel_anchor"),
                            "cell": det.get("cell", ""),
                            "exit_cents": det.get("exit_cents", 0),
                        })
                    elif evt == "scalp_filled":
                        scalps[tk] = {
                            "ts": d.get("ts", ""),
                            "entry_price": det.get("entry_price", 0),
                            "exit_price": det.get("exit_price", 0),
                            "profit_cents": det.get("profit_cents", 0),
                            "play_type": det.get("play_type", ""),
                        }
                    elif evt == "settled":
                        settlements[tk] = {
                            "ts": d.get("ts", ""),
                            "settle": det.get("settle", ""),
                            "pnl_cents": det.get("pnl_cents", 0),
                            "pnl_dollars": det.get("pnl_dollars", 0),
                            "entry_price": det.get("entry_price", 0),
                        }
        except Exception as e:
            print("Error reading %s: %s" % (lf, e))

    return entries, scalps, settlements


def classify_outcome(tk, scalps, settlements):
    """Determine outcome for a ticker."""
    if tk in scalps:
        return "scalp_filled", scalps[tk].get("profit_cents", 0)
    if tk in settlements:
        s = settlements[tk]
        label = s.get("settle", "")
        pnl = s.get("pnl_cents", 0)
        if label == "WIN":
            return "settlement_win", pnl
        else:
            return "settlement_loss", pnl
    return "open_or_unfilled", 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=int, default=48)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    entries, scalps, settlements = parse_logs(hours=args.hours)

    if not entries:
        print("No cell_match events found in last %dh" % args.hours)
        return

    now_str = datetime.now(ET).strftime("%Y-%m-%d %I:%M:%S %p ET")
    print("=" * 100)
    print("INTELLIGENCE REVIEW @ %s (last %dh)" % (now_str, args.hours))
    print("=" * 100)

    # Separate pre-intelligence entries (no intel_score) from intelligence-era
    intel_entries = [e for e in entries if e["intel_score"] is not None]
    legacy_entries = [e for e in entries if e["intel_score"] is None]

    if legacy_entries:
        print("\nPRE-INTELLIGENCE ENTRIES (no intel_score in logs): %d" % len(legacy_entries))
        legacy_scalps = 0
        legacy_wins = 0
        legacy_losses = 0
        legacy_open = 0
        legacy_pnl = 0
        for e in legacy_entries:
            outcome, pnl = classify_outcome(e["ticker"], scalps, settlements)
            if outcome == "scalp_filled":
                legacy_scalps += 1
            elif outcome == "settlement_win":
                legacy_wins += 1
            elif outcome == "settlement_loss":
                legacy_losses += 1
            else:
                legacy_open += 1
            legacy_pnl += pnl
        print("  Scalps: %d  Wins: %d  Losses: %d  Open: %d  PnL: %+dc" % (
            legacy_scalps, legacy_wins, legacy_losses, legacy_open, legacy_pnl))

    if not intel_entries:
        print("\nNo intelligence-era entries yet (intel_score field missing from all cell_match events)")
        print("Intelligence decisions will appear after first routing tick with the new code.")
        return

    # Per-tier analysis
    tiers = defaultdict(lambda: {
        "entries": [], "scalps": 0, "wins": 0, "losses": 0,
        "open": 0, "total_pnl": 0, "sizes": [],
    })

    for e in intel_entries:
        grade = e["intel_grade"] or "UNKNOWN"
        tier = tiers[grade]
        tier["entries"].append(e)
        tier["sizes"].append(e["entry_size"])

        outcome, pnl = classify_outcome(e["ticker"], scalps, settlements)
        if outcome == "scalp_filled":
            tier["scalps"] += 1
        elif outcome == "settlement_win":
            tier["wins"] += 1
        elif outcome == "settlement_loss":
            tier["losses"] += 1
        else:
            tier["open"] += 1
        tier["total_pnl"] += pnl

    print("\n%-8s %5s %6s %5s %5s %5s %8s %6s %6s" % (
        "TIER", "N", "SCALP%", "WINS", "LOSS", "OPEN", "PNL(c)", "AVG_SZ", "AVG_SC"))
    print("-" * 70)

    for grade in ["HIGH", "MEDIUM", "LOW", "SKIP", "UNKNOWN"]:
        t = tiers.get(grade)
        if not t or not t["entries"]:
            continue
        n = len(t["entries"])
        resolved = t["scalps"] + t["wins"] + t["losses"]
        scalp_rate = (t["scalps"] / resolved * 100) if resolved > 0 else 0
        avg_size = sum(t["sizes"]) / n if n > 0 else 0
        avg_score = sum(e["intel_score"] for e in t["entries"]) / n if n > 0 else 0
        print("%-8s %5d %5.1f%% %5d %5d %5d %+7dc %5.0fct %6.0f" % (
            grade, n, scalp_rate, t["wins"], t["losses"], t["open"],
            t["total_pnl"], avg_size, avg_score))

    print("-" * 70)
    total_n = len(intel_entries)
    total_pnl = sum(t["total_pnl"] for t in tiers.values())
    total_scalps = sum(t["scalps"] for t in tiers.values())
    total_resolved = sum(t["scalps"] + t["wins"] + t["losses"] for t in tiers.values())
    print("%-8s %5d %5.1f%% %43s %+7dc" % (
        "TOTAL", total_n,
        (total_scalps / total_resolved * 100) if total_resolved > 0 else 0,
        "", total_pnl))

    # Per-anchor analysis
    print("\nANCHOR BREAKDOWN:")
    anchors = defaultdict(lambda: {"n": 0, "pnl": 0, "scalps": 0, "resolved": 0})
    for e in intel_entries:
        anchor = e.get("intel_anchor") or e.get("anchor_source") or "unknown"
        outcome, pnl = classify_outcome(e["ticker"], scalps, settlements)
        anchors[anchor]["n"] += 1
        anchors[anchor]["pnl"] += pnl
        if outcome == "scalp_filled":
            anchors[anchor]["scalps"] += 1
        if outcome in ("scalp_filled", "settlement_win", "settlement_loss"):
            anchors[anchor]["resolved"] += 1

    for anchor, a in sorted(anchors.items()):
        sr = (a["scalps"] / a["resolved"] * 100) if a["resolved"] > 0 else 0
        print("  %-15s n=%d  scalp_rate=%.1f%%  pnl=%+dc" % (anchor, a["n"], sr, a["pnl"]))

    # Verbose per-entry detail
    if args.verbose:
        print("\nDETAILED ENTRIES:")
        print("%-40s %5s %-6s %-8s %5s %4s %-15s %8s" % (
            "TICKER", "SCORE", "GRADE", "ANCHOR", "ENTRY", "SIZE", "OUTCOME", "PNL"))
        print("-" * 100)
        for e in sorted(intel_entries, key=lambda x: x["ts_epoch"]):
            outcome, pnl = classify_outcome(e["ticker"], scalps, settlements)
            print("%-40s %5d %-6s %-8s %4dc %3dct %-15s %+7dc" % (
                e["ticker"][:40], e["intel_score"] or 0, e["intel_grade"] or "?",
                (e.get("intel_anchor") or "?")[:8],
                e["entry_price"], e["entry_size"],
                outcome, pnl))


if __name__ == "__main__":
    main()
