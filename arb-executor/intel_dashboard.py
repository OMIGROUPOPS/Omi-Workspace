#!/usr/bin/env python3
"""intel_dashboard.py — Live snapshot of intelligence decisions for all discoverable events."""

import sys, os, json, time, sqlite3, argparse
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from intelligence import (
    confidence_score, recommended_window_seconds, fv_stability,
    kalshi_price_anchor, _conn, CONFIG_PATH,
)

ET = ZoneInfo("America/New_York")
DB_PATH = str(Path(__file__).resolve().parent / "tennis.db")
STATE_DIR = Path(__file__).resolve().parent / "state"
PROCESSED_FILE = STATE_DIR / "live_v3_processed.json"


def load_processed():
    try:
        with open(PROCESSED_FILE) as f:
            return set(json.load(f))
    except Exception:
        return set()


def get_resting_orders():
    """Read resting orders from Kalshi API via health_check's auth."""
    try:
        from health_check import check_positions
        return {}
    except Exception:
        return {}


def get_active_positions():
    """Read positions from live_v3 heartbeat."""
    try:
        with open("/tmp/heartbeat_live_v3.json") as f:
            hb = json.load(f)
        return hb
    except Exception:
        return {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", help="Filter by tier (HIGH/MEDIUM/LOW/SKIP)")
    parser.add_argument("--series", help="Filter by series (ATP_MAIN/WTA_MAIN/ATP_CHALL/WTA_CHALL)")
    args = parser.parse_args()

    now = datetime.now(ET)
    now_ts = time.time()
    now_str = now.strftime("%Y-%m-%d %I:%M:%S %p ET")

    conn = sqlite3.connect(DB_PATH, timeout=10)
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT kps.event_ticker, kps.ticker, kps.series_ticker,
               kps.bid_cents, kps.ask_cents, kps.last_cents
        FROM kalshi_price_snapshots kps
        INNER JOIN (
            SELECT ticker, MAX(polled_at) as mp
            FROM kalshi_price_snapshots
            GROUP BY ticker
        ) latest ON kps.ticker = latest.ticker AND kps.polled_at = latest.mp
        ORDER BY kps.event_ticker, kps.ticker
    """)
    ticker_rows = cur.fetchall()

    cur.execute("""
        SELECT event_ticker, commence_time
        FROM kalshi_price_snapshots
        WHERE commence_time IS NOT NULL AND commence_time != ''
        GROUP BY event_ticker
    """)
    commence_map = {}
    for et, ct in cur.fetchall():
        try:
            dt = datetime.fromisoformat(ct.replace("Z", "+00:00"))
            commence_map[et] = dt.timestamp()
        except Exception:
            pass

    cur.execute("""
        SELECT DISTINCT event_ticker, book_key,
               MAX(polled_at) as last_poll
        FROM book_prices
        GROUP BY event_ticker, book_key
        HAVING last_poll > ?
    """, ((now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),))
    fv_coverage = {}
    for et, bk, lp in cur.fetchall():
        fv_coverage.setdefault(et, []).append(bk)

    conn.close()

    processed = load_processed()

    events = {}
    for et, tk, series, bid, ask, last in ticker_rows:
        if et not in events:
            events[et] = {"tickers": [], "series": series or ""}
        mid = (bid + ask) / 2 if bid and ask and bid > 0 and ask > 0 else (last or 0)
        events[et]["tickers"].append({"ticker": tk, "mid": mid, "bid": bid, "ask": ask})

    rows = []
    tier_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "SKIP": 0}

    for et, info in sorted(events.items()):
        series = info["series"]
        if "KXATPCHALLENGER" in et:
            cat = "ATP_CHALL"
        elif "KXWTACHALLENGER" in et:
            cat = "WTA_CHALL"
        elif "KXATPMATCH" in et:
            cat = "ATP_MAIN"
        elif "KXWTAMATCH" in et:
            cat = "WTA_MAIN"
        else:
            cat = "OTHER"

        if args.series and cat != args.series:
            continue

        commence_ts = commence_map.get(et)
        if commence_ts:
            hours_to_start = (commence_ts - now_ts) / 3600
        else:
            hours_to_start = None

        is_processed = et in processed
        fv_books = len(fv_coverage.get(et, []))

        for tk_info in info["tickers"]:
            tk = tk_info["ticker"]
            mid = tk_info["mid"]

            try:
                cs = confidence_score(et, tk)
            except Exception as e:
                cs = {"score": 0, "grade": "ERROR", "anchor_mode": "?", "components": {}, "flags": [str(e)[:50]]}

            try:
                rec = recommended_window_seconds(et, tk)
            except Exception:
                rec = {"window_seconds": 0, "anchor_source": "error", "recommended_size": 0}

            grade = cs.get("grade", "?")
            if args.tier and grade != args.tier:
                continue

            tier_counts[grade] = tier_counts.get(grade, 0) + 1

            in_window = False
            if hours_to_start is not None and rec["window_seconds"] > 0:
                window_hours = rec["window_seconds"] / 3600
                in_window = 0.25 < hours_to_start <= window_hours

            rows.append({
                "et": et,
                "tk": tk,
                "cat": cat,
                "mid": mid,
                "hours": hours_to_start,
                "score": cs.get("score", 0),
                "grade": grade,
                "anchor": cs.get("anchor_mode", "?"),
                "window_h": rec["window_seconds"] / 3600 if rec["window_seconds"] > 0 else 0,
                "size": rec.get("recommended_size", 0),
                "anchor_src": rec.get("anchor_source", "?"),
                "fv_books": fv_books,
                "in_window": in_window,
                "processed": is_processed,
                "flags": cs.get("flags", []),
            })

    print("=" * 120)
    print("INTELLIGENCE DASHBOARD @ %s" % now_str)
    if args.tier:
        print("Filter: tier=%s" % args.tier)
    if args.series:
        print("Filter: series=%s" % args.series)
    print("=" * 120)

    print("\n%-48s %-10s %5s %5s %-6s %-8s %5s %4s %3s %-6s %s" % (
        "TICKER", "CATEGORY", "MID", "SCORE", "GRADE", "ANCHOR", "WIN_H", "SIZE",
        "FV#", "STATUS", "FLAGS"))
    print("-" * 120)

    in_window_count = 0
    for r in sorted(rows, key=lambda x: (-x["score"], x["et"])):
        status = ""
        if r["processed"]:
            status = "DONE"
        elif r["in_window"]:
            status = "LIVE"
            in_window_count += 1
        elif r["hours"] is not None and r["hours"] <= 0:
            status = "PAST"
        elif r["hours"] is not None:
            status = "WAIT"
        else:
            status = "NOSCHED"

        hours_str = "%.1fh" % r["hours"] if r["hours"] is not None else "?"
        flags_str = ",".join(r["flags"][:2]) if r["flags"] else ""

        print("%-48s %-10s %4.0fc %5d %-6s %-8s %5s %3dct %3d %-6s %s" % (
            r["tk"][:48], r["cat"], r["mid"], r["score"], r["grade"],
            r["anchor"][:8], hours_str, r["size"], r["fv_books"],
            status, flags_str[:30]))

    print("-" * 120)
    print("\nSUMMARY:")
    print("  Events: %d tickers across %d events" % (len(rows), len(events)))
    print("  Tier distribution: HIGH=%d  MEDIUM=%d  LOW=%d  SKIP=%d" % (
        tier_counts.get("HIGH", 0), tier_counts.get("MEDIUM", 0),
        tier_counts.get("LOW", 0), tier_counts.get("SKIP", 0)))
    print("  In-window (LIVE): %d" % in_window_count)
    print("  Already processed: %d" % sum(1 for r in rows if r["processed"]))


if __name__ == "__main__":
    main()
