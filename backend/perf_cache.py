"""
Shared performance cache — populated by scheduler, read by server.py.

The scheduler calls refresh_performance_cache() every 5 minutes using a
dedicated Supabase connection, so the /api/internal/edge/performance
endpoint never needs to touch Supabase at request time.
"""
import os
import time
import logging

logger = logging.getLogger(__name__)

# Cache storage: keyed by params tuple string → {"data": dict, "ts": float}
_perf_cache: dict = {}


def get_cached_performance(key: str) -> dict | None:
    """Return cached performance data if it exists."""
    entry = _perf_cache.get(key)
    if entry is not None:
        return entry["data"]
    return None


def refresh_performance_cache():
    """Called by scheduler every 5 min. Fetches aggregated performance via RPC."""
    try:
        from supabase import create_client
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        if not url or not key:
            logger.error("[PerfCache] Missing Supabase credentials")
            return
        client = create_client(url, key)

        # Default view: last 30 days, no filters
        _fetch_and_store(client, "default", {"p_days": 30})

        # Clean data view: since 2026-02-10
        _fetch_and_store(client, "clean", {
            "p_days": 30,
            "p_since": "2026-02-10T00:00:00+00:00",
        })

        logger.info(f"[PerfCache] Refreshed {len(_perf_cache)} cache entries")
    except Exception as e:
        logger.error(f"[PerfCache] Refresh failed: {e}")


def _fetch_and_store(client, label: str, params: dict):
    """Call the RPC and store result."""
    try:
        result = client.rpc("get_performance_summary", params).execute()
        data = result.data
        if isinstance(data, list) and len(data) == 1:
            data = data[0]
        if isinstance(data, dict) and "get_performance_summary" in data:
            data = data["get_performance_summary"]
        if isinstance(data, dict) and "total_predictions" in data:
            data["days"] = params.get("p_days", 30)
            data["filters"] = {
                "sport": params.get("p_sport"),
                "market": params.get("p_market"),
                "confidence_tier": params.get("p_confidence_tier"),
                "signal": params.get("p_signal"),
                "since": params.get("p_since"),
            }
            cache_key = _make_key(
                params.get("p_sport"),
                params.get("p_days", 30),
                params.get("p_market"),
                params.get("p_confidence_tier"),
                params.get("p_signal"),
                params.get("p_since"),
            )
            _perf_cache[cache_key] = {"data": data, "ts": time.time()}
            logger.info(f"[PerfCache] {label}: {data['total_predictions']} predictions cached")
        else:
            logger.warning(f"[PerfCache] {label}: RPC returned unexpected shape")
    except Exception as e:
        logger.warning(f"[PerfCache] {label} fetch failed: {e}")


def _make_key(sport=None, days=30, market=None, confidence_tier=None, signal=None, since=None) -> str:
    return f"perf:{sport}:{days}:{market}:{confidence_tier}:{signal}:{since}"


def lookup(sport=None, days=30, market=None, confidence_tier=None, signal=None, since=None) -> dict | None:
    """Look up cached performance data by filter params."""
    key = _make_key(sport, days, market, confidence_tier, signal, since)
    return get_cached_performance(key)
