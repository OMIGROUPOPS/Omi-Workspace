"""
SQLite orderbook snapshot storage for liquidity/volume research.

Stores sampled snapshots (10s throttle per game+platform) with top-5 levels.
Data is retained for 7 days, cleaned up on startup and every 24h.

Query examples (via SSH):
    sqlite3 orderbook_data.db "SELECT * FROM orderbook_snapshots WHERE game_id LIKE '%ATL%' ORDER BY timestamp DESC LIMIT 20"
    sqlite3 orderbook_data.db "SELECT game_id, platform, AVG(bid_depth), AVG(ask_depth) FROM orderbook_snapshots GROUP BY game_id, platform"
"""

import sqlite3
import json
import time
import os
import threading
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__) or ".", "orderbook_data.db")

_conn: sqlite3.Connection | None = None
_lock = threading.Lock()

# Throttle: (game_id, platform) -> last snapshot timestamp
_last_snapshot: dict = {}
SNAPSHOT_INTERVAL = 10  # seconds

# Cleanup tracking
_last_cleanup: float = 0
CLEANUP_INTERVAL = 86400  # 24 hours
RETENTION_DAYS = 7


def init_db():
    """Initialize SQLite database with WAL mode and create table."""
    global _conn, _last_cleanup

    _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    _conn.execute("PRAGMA journal_mode=WAL")
    _conn.execute("""
        CREATE TABLE IF NOT EXISTS orderbook_snapshots (
            timestamp TEXT NOT NULL,
            game_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            best_bid INTEGER,
            best_ask INTEGER,
            bid_depth INTEGER,
            ask_depth INTEGER,
            bid_levels TEXT,
            ask_levels TEXT,
            spread INTEGER
        )
    """)
    _conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_snapshots_game_time
        ON orderbook_snapshots(game_id, platform, timestamp)
    """)
    _conn.commit()

    # Run initial cleanup
    cleanup_old_rows()
    _last_cleanup = time.time()
    print(f"[ORDERBOOK_DB] Initialized at {DB_PATH}", flush=True)


def record_snapshot(
    game_id: str,
    platform: str,
    best_bid: int,
    best_ask: int,
    bid_depth: int,
    ask_depth: int,
    bid_levels_json: str,
    ask_levels_json: str,
    spread: int,
):
    """Record an orderbook snapshot if 10s+ since last for this game+platform."""
    global _last_cleanup

    if _conn is None:
        return

    # Throttle check
    key = (game_id, platform)
    now = time.time()
    if key in _last_snapshot and now - _last_snapshot[key] < SNAPSHOT_INTERVAL:
        return
    _last_snapshot[key] = now

    ts = datetime.now(timezone.utc).isoformat()

    try:
        with _lock:
            _conn.execute(
                "INSERT INTO orderbook_snapshots VALUES (?,?,?,?,?,?,?,?,?,?)",
                (ts, game_id, platform, best_bid, best_ask,
                 bid_depth, ask_depth, bid_levels_json, ask_levels_json, spread),
            )
            _conn.commit()
    except Exception as e:
        # Don't crash the executor over DB writes
        pass

    # Periodic cleanup check
    if now - _last_cleanup > CLEANUP_INTERVAL:
        _last_cleanup = now
        try:
            cleanup_old_rows()
        except Exception:
            pass


def cleanup_old_rows(days: int = RETENTION_DAYS):
    """Delete rows older than `days` days."""
    if _conn is None:
        return

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    try:
        with _lock:
            cursor = _conn.execute(
                "DELETE FROM orderbook_snapshots WHERE timestamp < ?", (cutoff,)
            )
            _conn.commit()
            deleted = cursor.rowcount
            if deleted > 0:
                print(f"[ORDERBOOK_DB] Cleaned up {deleted} rows older than {days} days", flush=True)
    except Exception as e:
        print(f"[ORDERBOOK_DB] Cleanup error: {e}", flush=True)
