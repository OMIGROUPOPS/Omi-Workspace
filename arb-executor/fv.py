#!/usr/bin/env python3
"""
fv.py — Single authoritative fair value lookup for any tennis event.

Tiered hierarchy:
  Tier 1: Pinnacle (sharpest book, Main tour)
  Tier 2: Aggregate (mean of all non-Pinnacle books, 3+ required)
  Tier 3: BetExplorer (Challenger scraper)
  Tier 5: Paired-sum (100 - other side's Kalshi price, last resort)

Usage:
  from fv import get_consensus_fv
  result = get_consensus_fv("KXATPMATCH-26APR20GEAGAU", "p1")
  # Returns: {"fv_cents": 44.8, "source": "pinnacle", "tier": 1,
  #           "confidence": 0.95, "age_sec": 120, "num_books": 1, ...}
"""

import sqlite3, time, os, base64, requests
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
DB_PATH = str(Path(__file__).resolve().parent / "tennis.db")

FRESHNESS_LIMIT_SEC = {
    1: 1800,   # Pinnacle: 30 min
    2: 1800,   # Aggregate: 30 min
    3: 3600,   # BetExplorer: 1 hour (scraped, updates less often)
    5: 300,    # Paired-sum: 5 min (Kalshi price moves fast)
}

CONFIDENCE = {
    1: 0.95,   # Pinnacle
    2: 0.80,   # Aggregate
    3: 0.50,   # BetExplorer (single source, volatile — see Challenger risk)
    5: 0.30,   # Paired-sum
}

MIN_AGGREGATE_BOOKS = 3


def get_consensus_fv(event_ticker, side, conn=None):
    """Return authoritative FV for one side of an event.

    Args:
        event_ticker: Kalshi event ticker (e.g. "KXATPMATCH-26APR20GEAGAU")
        side: "p1" or "p2"
        conn: optional sqlite3 connection (caller manages lifecycle)

    Returns dict with keys:
        fv_cents, source, tier, confidence, age_sec, fetched_at, num_books
        or None if no FV available.
    """
    close_conn = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        close_conn = True

    try:
        cur = conn.cursor()
        now = datetime.now(ET)
        stale_best = None

        # Tier 1+2: Pinnacle with aggregate cross-check
        pinnacle_fv = None
        pinnacle_age = None
        pinnacle_polled = None

        cur.execute("""
            SELECT book_p1_fv_cents, book_p2_fv_cents, polled_at
            FROM book_prices
            WHERE event_ticker = ? AND book_key = 'pinnacle'
            ORDER BY polled_at DESC LIMIT 1
        """, (event_ticker,))
        row = cur.fetchone()
        if row:
            p1_fv, p2_fv, polled = row
            age = _age_sec(polled, now)
            if age is not None and age < FRESHNESS_LIMIT_SEC[1]:
                pinnacle_fv = p1_fv if side == "p1" else p2_fv
                pinnacle_age = int(age)
                pinnacle_polled = polled
            elif age is not None:
                stale_best = {"source": "pinnacle", "tier": 1, "age_sec": int(age)}

        # Collect aggregate from other books
        cur.execute("""
            SELECT bp.book_key, bp.book_p1_fv_cents, bp.book_p2_fv_cents, bp.polled_at
            FROM book_prices bp
            INNER JOIN (
                SELECT event_ticker, book_key, MAX(polled_at) as mp
                FROM book_prices
                WHERE event_ticker = ? AND book_key NOT IN ('pinnacle', 'betexplorer')
                GROUP BY event_ticker, book_key
            ) latest ON bp.event_ticker = latest.event_ticker
                    AND bp.book_key = latest.book_key
                    AND bp.polled_at = latest.mp
            WHERE bp.event_ticker = ?
        """, (event_ticker, event_ticker))
        agg_rows = cur.fetchall()
        fresh_fvs = []
        for book_key, p1_fv, p2_fv, polled in agg_rows:
            age = _age_sec(polled, now)
            if age is not None and age < FRESHNESS_LIMIT_SEC[2]:
                fv = p1_fv if side == "p1" else p2_fv
                if fv and fv > 0:
                    fresh_fvs.append(fv)

        # Blend: if Pinnacle fresh AND aggregate available, cross-check
        if pinnacle_fv and pinnacle_fv > 0:
            if len(fresh_fvs) >= MIN_AGGREGATE_BOOKS:
                agg_median = sorted(fresh_fvs)[len(fresh_fvs) // 2]
                divergence_pct = abs(pinnacle_fv - agg_median) / pinnacle_fv * 100 if pinnacle_fv > 0 else 0
                if divergence_pct > 10:
                    # Pinnacle is outlier — use median of all books (including Pinnacle)
                    all_fvs = fresh_fvs + [pinnacle_fv]
                    blended = sorted(all_fvs)[len(all_fvs) // 2]
                    return {
                        "fv_cents": round(blended, 1),
                        "source": "blended_median",
                        "tier": 1,
                        "confidence": CONFIDENCE[1] * 0.9,
                        "age_sec": pinnacle_age,
                        "fetched_at": pinnacle_polled,
                        "num_books": len(all_fvs),
                        "reason": "ok",
                    }
            # Pinnacle consistent with market or no aggregate — use Pinnacle
            return {
                "fv_cents": round(pinnacle_fv, 1),
                "source": "pinnacle",
                "tier": 1,
                "confidence": CONFIDENCE[1],
                "age_sec": pinnacle_age,
                "fetched_at": pinnacle_polled,
                "num_books": 1 + len(fresh_fvs),
                "reason": "ok",
            }

        # No Pinnacle — use aggregate if available
        if len(fresh_fvs) >= MIN_AGGREGATE_BOOKS:
            mean_fv = sum(fresh_fvs) / len(fresh_fvs)
            return {
                "fv_cents": round(mean_fv, 1),
                "source": "aggregate",
                "tier": 2,
                "confidence": CONFIDENCE[2],
                "age_sec": 0,
                "fetched_at": datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S"),
                "num_books": len(fresh_fvs),
                "reason": "ok",
            }

        # Tier 3: BetExplorer (Challenger coverage)
        cur.execute("""
            SELECT book_p1_fv_cents, book_p2_fv_cents, polled_at
            FROM book_prices
            WHERE event_ticker = ? AND book_key = 'betexplorer'
            ORDER BY polled_at DESC LIMIT 1
        """, (event_ticker,))
        row = cur.fetchone()
        if row:
            p1_fv, p2_fv, polled = row
            age = _age_sec(polled, now)
            if age is not None and age < FRESHNESS_LIMIT_SEC[3]:
                fv = p1_fv if side == "p1" else p2_fv
                if fv and fv > 0:
                    return {
                        "fv_cents": round(fv, 1),
                        "source": "betexplorer",
                        "tier": 3,
                        "confidence": CONFIDENCE[3],
                        "age_sec": int(age),
                        "fetched_at": polled,
                        "num_books": 1,
                        "reason": "ok",
                    }
            elif age is not None and stale_best is None:
                stale_best = {"source": "betexplorer", "tier": 3, "age_sec": int(age)}

        if stale_best:
            return {"fv_cents": None, "reason": "stale", **stale_best}

        return {"fv_cents": None, "reason": "no_data", "source": None, "age_sec": None}

    finally:
        if close_conn:
            conn.close()


def _age_sec(polled_at_str, now):
    """Parse polled_at string and return age in seconds."""
    try:
        polled_dt = datetime.strptime(polled_at_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ET)
        return (now - polled_dt).total_seconds()
    except Exception:
        return None


FV_STABILITY_WINDOW_SEC = 1800  # 30 min
FV_STABILITY_MAX_RANGE_C = 4.0
FV_STABILITY_MAX_RANGE_PCT = 10.0


def check_fv_stability(event_ticker, side, conn=None):
    """Check if FV has been stable over the last 30 minutes.

    Returns dict: {"stable": bool, "range_c": float, "range_pct": float,
                   "fv_now": float, "fv_oldest": float, "samples": int}
    """
    close_conn = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        close_conn = True

    try:
        cur = conn.cursor()
        now = datetime.now(ET)
        cutoff = (now - __import__("datetime").timedelta(seconds=FV_STABILITY_WINDOW_SEC)).strftime("%Y-%m-%d %H:%M:%S")
        fv_col = "book_p1_fv_cents" if side == "p1" else "book_p2_fv_cents"

        cur.execute("""
            SELECT %s, polled_at FROM book_prices
            WHERE event_ticker = ? AND book_key IN ('pinnacle', 'betexplorer')
            AND polled_at > ? AND %s > 0
            ORDER BY polled_at DESC
        """ % (fv_col, fv_col), (event_ticker, cutoff))
        rows = cur.fetchall()

        if len(rows) < 2:
            return {"stable": True, "range_c": 0, "range_pct": 0,
                    "fv_now": rows[0][0] if rows else 0, "fv_oldest": rows[0][0] if rows else 0,
                    "samples": len(rows)}

        fvs = [r[0] for r in rows]
        fv_now = fvs[0]
        fv_oldest = fvs[-1]
        fv_min = min(fvs)
        fv_max = max(fvs)
        range_c = fv_max - fv_min
        mean_fv = sum(fvs) / len(fvs)
        range_pct = (range_c / mean_fv * 100) if mean_fv > 0 else 0

        stable = range_c <= FV_STABILITY_MAX_RANGE_C and range_pct <= FV_STABILITY_MAX_RANGE_PCT

        return {"stable": stable, "range_c": round(range_c, 1), "range_pct": round(range_pct, 1),
                "fv_now": round(fv_now, 1), "fv_oldest": round(fv_oldest, 1),
                "samples": len(fvs)}
    except Exception:
        return {"stable": True, "range_c": 0, "range_pct": 0, "fv_now": 0, "fv_oldest": 0, "samples": 0}
    finally:
        if close_conn:
            conn.close()


def self_test():
    """Run self-test showing FV for all events in book_prices."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT event_ticker FROM book_prices ORDER BY event_ticker")
    tickers = [r[0] for r in cur.fetchall()]
    print("fv.py self-test — %d events in book_prices" % len(tickers))
    print()
    print("%-52s %-4s %6s  %-14s  T  Conf  Age   Books" % ("event_ticker", "side", "FV", "source"))
    print("-" * 110)

    for et in tickers:
        for side in ("p1", "p2"):
            result = get_consensus_fv(et, side, conn=conn)
            if result:
                print("%-52s %-4s %5.1fc  %-14s  %d  %.2f  %4ds  %d" % (
                    et[:52], side, result["fv_cents"], result["source"],
                    result["tier"], result["confidence"],
                    result["age_sec"], result["num_books"]))
            else:
                print("%-52s %-4s   —     no FV available" % (et[:52], side))
    conn.close()


if __name__ == "__main__":
    self_test()
