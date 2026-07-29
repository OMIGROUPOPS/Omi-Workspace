#!/usr/bin/env python3
"""Deterministic Window-1 replay shell for the unchanged live_v4 OS.

The shell replaces only the external clock, WebSocket input, REST input, and
order API.  All discovery, routing, dossier, recognition, authority, aiming,
posting, fill booking, re-aiming, parking, and headroom decisions execute from
arb-executor/live_v4.py itself.

Fill model (RESTING_TOUCH_FILL_V1): a resting order fills in full when a later
true print or opposite BBO touches or passes its limit; no depth, capacity, or
five-contract proof gate is applied.
"""

from __future__ import annotations

import argparse
import asyncio
import bisect
import copy
import csv
import difflib
import gzip
import hashlib
import importlib.util
import json
import re
import shutil
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime as _RealDateTime
from datetime import timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo


REPO = Path(__file__).resolve().parents[2]
EXECUTOR = REPO / "arb-executor"
LIVE_V4 = EXECUTOR / "live_v4.py"
PRIVATE_ROOT = Path(r"C:\Users\omigr\OMI-Window1-private")
VPS_INPUT_ROOT = (
    REPO / ".claude" / "window1_live_v4_replay" / "vps_inputs_20260729"
)
EVENT_LEDGER = PRIVATE_ROOT / "joined" / "events.jsonl"
PRINTS = PRIVATE_ROOT / "fit-local" / "prints.jsonl"
MILESTONES = (
    PRIVATE_ROOT
    / "start-recovery-v2"
    / "PUBLIC_MILESTONES.normalized.jsonl"
)
OBSERVED_STARTS = VPS_INPUT_ROOT / "db" / "observed_starts.db"
TENNIS_DB = VPS_INPUT_ROOT / "db" / "tennis.snapshot.db"
TICKS = PRIVATE_ROOT / "fit-local" / "ticks"
GRID = REPO / ".claude" / "window1_t2_iteration_history" / "WINDOW1_T2_GAME_GRID.json"
DEFAULT_OUT = REPO / ".claude" / "window1_live_v4_replay"
ET = ZoneInfo("America/New_York")

FILL_MODEL = (
    "RESTING_TOUCH_FILL_V1: a resting order fills in full when a later true "
    "print or opposite BBO touches or passes its limit; no depth, capacity, "
    "or five-contract proof gate."
)
_REAL_SQLITE_CONNECT = sqlite3.connect


def _iso_ts(value: str) -> float:
    return _RealDateTime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    return str(value)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


@dataclass
class ReplayClock:
    now: float

    def set(self, ts: float) -> None:
        if ts < self.now:
            raise ValueError(f"replay clock moved backward: {ts} < {self.now}")
        self.now = float(ts)

    def time(self) -> float:
        return self.now

    def monotonic(self) -> float:
        return self.now


class TimeProxy:
    def __init__(self, clock: ReplayClock, real_time: Any):
        self._clock = clock
        self._real = real_time

    def time(self) -> float:
        return self._clock.time()

    def monotonic(self) -> float:
        return self._clock.monotonic()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._real, name)


def replay_datetime_class(clock: ReplayClock) -> type[_RealDateTime]:
    class ReplayDateTime(_RealDateTime):
        @classmethod
        def now(cls, tz=None):
            base = _RealDateTime.fromtimestamp(clock.time(), tz=timezone.utc)
            if tz is not None:
                base = base.astimezone(tz)
            else:
                base = base.replace(tzinfo=None)
            return cls(
                base.year,
                base.month,
                base.day,
                base.hour,
                base.minute,
                base.second,
                base.microsecond,
                tzinfo=base.tzinfo,
                fold=base.fold,
            )

        @classmethod
        def utcnow(cls):
            base = _RealDateTime.fromtimestamp(clock.time(), tz=timezone.utc)
            return cls(
                base.year,
                base.month,
                base.day,
                base.hour,
                base.minute,
                base.second,
                base.microsecond,
            )

    return ReplayDateTime


def install_vps_database_replay(clock: ReplayClock):
    """Expose preserved VPS databases read-only under the replay clock.

    live_v4's reader remains unchanged.  Its read-only SQLite connection is
    redirected to the byte-preserved VPS copy, and a connection-local TEMP
    view hides rows until their original ``inserted_at`` timestamp arrives on
    the replay clock.  Every direct ``tennis.db`` read is redirected to the
    real VPS database copy in read-only mode.  Neither source is ever written.
    """
    if not OBSERVED_STARTS.exists():
        raise FileNotFoundError(
            f"historical observed-start feed is absent: {OBSERVED_STARTS}"
        )
    if not TENNIS_DB.exists() or TENNIS_DB.stat().st_size == 0:
        raise FileNotFoundError(
            f"real VPS tennis database is absent: {TENNIS_DB}"
        )

    observed_uri = "file:" + OBSERVED_STARTS.as_posix() + "?mode=ro"
    tennis_uri = "file:" + TENNIS_DB.as_posix() + "?mode=ro"

    def replay_connect(database, *args, **kwargs):
        raw = str(database)
        lowered = raw.replace("\\", "/").lower()
        if lowered.endswith("/observed_starts.db") or (
            "observed_starts.db?" in lowered
        ):
            observed_kwargs = dict(kwargs)
            observed_kwargs["uri"] = True
            conn = _REAL_SQLITE_CONNECT(
                observed_uri, *args, **observed_kwargs
            )
            conn.create_function(
                "replay_visible_at",
                0,
                lambda: _RealDateTime.fromtimestamp(
                    clock.time(), tz=ET
                ).strftime("%Y-%m-%d %H:%M:%S"),
            )
            conn.execute(
                "CREATE TEMP VIEW observed_starts AS "
                "SELECT * FROM main.observed_starts "
                "WHERE inserted_at <= replay_visible_at()"
            )
            return conn
        if lowered.endswith("/tennis.db") or "tennis.db?" in lowered:
            tennis_kwargs = dict(kwargs)
            tennis_kwargs["uri"] = True
            return _REAL_SQLITE_CONNECT(
                tennis_uri, *args, **tennis_kwargs
            )
        return _REAL_SQLITE_CONNECT(database, *args, **kwargs)

    sqlite3.connect = replay_connect

    def restore() -> None:
        sqlite3.connect = _REAL_SQLITE_CONNECT

    return restore


def build_print_index(path: Path, index_path: Path) -> dict[str, list[int]]:
    """Index the ticker-contiguous normalized public-print ledger by byte range."""
    source = {"bytes": path.stat().st_size, "mtime_ns": path.stat().st_mtime_ns}
    if index_path.exists():
        existing = json.loads(index_path.read_text(encoding="utf-8"))
        if existing.get("source") == source:
            return existing["ticker_ranges"]

    marker = b'"ticker":"'
    ranges: dict[str, list[int]] = {}
    current: str | None = None
    start = 0
    with path.open("rb") as fh:
        while True:
            pos = fh.tell()
            line = fh.readline()
            if not line:
                end = fh.tell()
                break
            i = line.find(marker)
            if i < 0:
                raise ValueError(f"ticker missing at byte {pos}")
            j = line.find(b'"', i + len(marker))
            ticker = line[i + len(marker) : j].decode("ascii")
            if ticker != current:
                if current is not None:
                    ranges[current] = [start, pos]
                current, start = ticker, pos
        if current is not None:
            ranges[current] = [start, end]

    payload = {"source": source, "ticker_ranges": ranges}
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        json.dumps(payload, separators=(",", ":"), sort_keys=True),
        encoding="utf-8",
    )
    return ranges


def load_print_block(
    ticker: str,
    ranges: dict[str, list[int]],
    left_ts: float,
    right_ts: float,
) -> tuple[list[dict], dict | None]:
    span = ranges.get(ticker)
    if not span:
        return [], None
    rows: list[dict] = []
    prior: dict | None = None
    with PRINTS.open("rb") as fh:
        fh.seek(span[0])
        while fh.tell() < span[1]:
            line = fh.readline()
            if not line:
                break
            raw = json.loads(line)
            ts = _iso_ts(raw["exchange_ts"])
            row = {
                "ts": ts,
                "ticker": ticker,
                "price": int(raw["price_cents"]),
                "size": float(raw.get("size") or 0),
                "taker_side": raw.get("taker_side") or "?",
                "trade_id": raw.get("trade_id"),
            }
            if ts <= left_ts and (prior is None or ts > prior["ts"]):
                prior = row
            if left_ts <= ts <= right_ts:
                rows.append(row)
    rows.sort(key=lambda x: (x["ts"], x.get("trade_id") or ""))
    return rows, prior


def _parse_tick_ts(value: str) -> float:
    local = _RealDateTime.strptime(value, "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET)
    return local.timestamp()


def _levels(row: dict[str, str], side: str) -> list[list[float]]:
    out = []
    for i in range(1, 6):
        p = row.get(f"{side}_{i}", "")
        q = row.get(f"{side}_{i}_sz", "")
        if p in ("", None) or q in ("", None):
            continue
        try:
            price, size = int(float(p)), float(q)
        except ValueError:
            continue
        if 0 < price < 100 and size > 0:
            out.append([price, size])
    return out


def load_tick_block(
    ticker: str, left_ts: float, right_ts: float
) -> tuple[list[dict], dict | None]:
    path = TICKS / f"{ticker}.csv.gz"
    if not path.exists():
        return [], None
    rows: list[dict] = []
    prior: dict | None = None
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        for raw in csv.DictReader(fh):
            ts = _parse_tick_ts(raw["ts_et"])
            item = {
                "ts": ts,
                "ticker": ticker,
                "bids": _levels(raw, "bid"),
                "asks": _levels(raw, "ask"),
                "last_trade": int(float(raw.get("last_trade") or 0)),
            }
            if ts <= left_ts:
                prior = item
            if left_ts <= ts <= right_ts:
                rows.append(item)
            if ts > right_ts:
                break
    return rows, prior


def load_scope(event_filter: str | None) -> list[dict]:
    ledger = {}
    with EVENT_LEDGER.open(encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            ledger[row["event_id"]] = row

    grid = json.loads(GRID.read_text(encoding="utf-8"))
    out = []
    for game in grid["games"]:
        event = game["event_id"]
        if event_filter and event != event_filter:
            continue
        base = ledger[event]
        windows = [leg["price_path"]["window"] for leg in game["legs"].values()]
        if any(
            not bool(window.get("evaluator_boundary_resolved"))
            for window in windows
        ):
            raise SystemExit(
                f"{event}: guarded actual-start cutoff is unresolved; "
                "replay refused rather than substituting the scheduled "
                "policy horizon"
            )
        left = max(float(w["left_ts"]) for w in windows)
        right = min(float(w["evaluator_right_ts"]) for w in windows)
        policy_right = min(float(w["policy_right_ts"]) for w in windows)
        out.append(
            {
                "event": event,
                "category": game["category"],
                "slice": game["slice"],
                "event_date": game["event_date"],
                "left_ts": left,
                "right_ts": right,
                "policy_right_ts": policy_right,
                "evaluator_right_ts": right,
                "scheduled_start_ts": _iso_ts(base["scheduled_start_exchange_ts"]),
                "schedule_observed_ts": _iso_ts(base["schedule_observed_exchange_ts"]),
                "legs": base["legs"],
                "tape_truth": {
                    leg_id: {
                        "low": leg["price_path"]["tape_low"],
                        "close": leg["price_path"]["close"],
                        "shape": leg["price_path"]["shape"],
                    }
                    for leg_id, leg in game["legs"].items()
                },
            }
        )
    out.sort(key=lambda x: (x["left_ts"], x["event"]))
    if event_filter and not out:
        raise SystemExit(f"event not in 804-game scope: {event_filter}")
    return out


class ReplayRest:
    def __init__(
        self,
        game: dict,
        clock: ReplayClock,
        prints_by_ticker: dict[str, list[dict]],
        milestone: dict | None,
    ):
        self.game = game
        self.clock = clock
        self.prints = prints_by_ticker
        self.milestone = milestone
        self.bot = None
        self.print_times = {
            tk: [row["ts"] for row in rows] for tk, rows in prints_by_ticker.items()
        }
        self.unknown: list[dict] = []

    def _market_rows(self, series: str) -> list[dict]:
        event = self.game["event"]
        if not event.startswith(series):
            return []
        expiry = _RealDateTime.fromtimestamp(
            self.game["scheduled_start_ts"] + 6 * 3600, tz=timezone.utc
        ).isoformat().replace("+00:00", "Z")
        occurrence = _RealDateTime.fromtimestamp(
            self.game["scheduled_start_ts"], tz=timezone.utc
        ).isoformat().replace("+00:00", "Z")
        opened = _RealDateTime.fromtimestamp(
            self.game["schedule_observed_ts"], tz=timezone.utc
        ).isoformat().replace("+00:00", "Z")
        out = []
        leg_names = [x["leg"] for x in self.game["legs"]]
        for leg in self.game["legs"]:
            tk = leg["ticker"]
            rows = self.prints.get(tk, [])
            cut = bisect.bisect_right(self.print_times.get(tk, []), self.clock.time())
            volume = sum(float(x["size"]) for x in rows[:cut])
            out.append(
                {
                    "ticker": tk,
                    "event_ticker": event,
                    "volume_fp": str(volume),
                    "open_time": opened,
                    "occurrence_datetime": occurrence,
                    "expected_expiration_time": expiry,
                    "yes_sub_title": leg["leg"],
                    "no_sub_title": next(x for x in leg_names if x != leg["leg"]),
                }
            )
        return out

    async def get(self, _s, _ak, _pk, path: str, _rl):
        parts = urlsplit(path)
        query = parse_qs(parts.query)
        if parts.path == "/trade-api/v2/markets":
            series = query.get("series_ticker", [""])[0]
            return {"markets": self._market_rows(series), "cursor": ""}
        if parts.path == "/trade-api/v2/markets/trades":
            ticker = query.get("ticker", [""])[0]
            rows = self.prints.get(ticker, [])
            cut = bisect.bisect_right(self.print_times.get(ticker, []), self.clock.time())
            if cut <= 0:
                return {"trades": []}
            limit = max(1, int(query.get("limit", ["100"])[0]))
            selected = list(reversed(rows[max(0, cut - limit) : cut]))
            return {
                "trades": [
                    {
                        "created_time": _RealDateTime.fromtimestamp(
                            row["ts"], tz=timezone.utc
                        ).isoformat().replace("+00:00", "Z"),
                        "yes_price": row["price"],
                        "count": row["size"],
                        "taker_side": row["taker_side"],
                        "trade_id": row.get("trade_id"),
                    }
                    for row in selected
                ]
            }
        if parts.path == "/trade-api/v2/milestones":
            if not self.milestone:
                return {"milestones": []}
            start = self.milestone.get("start_utc")
            start_ts = _iso_ts(start) if start else None
            final_status = self.milestone.get("status")
            # The frozen export is a terminal observation, not a time series.
            # Never leak a terminal live status backward into the replay.
            status = (
                "not_started"
                if start_ts is not None and self.clock.time() < start_ts
                else final_status
            )
            return {
                "milestones": [
                    {
                        "start_date": start,
                        "details": {"status": status},
                        "source_id": self.milestone.get("source_identity_sha256"),
                    }
                ]
            }
        market_match = re.fullmatch(r"/trade-api/v2/markets/([^/]+)", parts.path)
        if market_match:
            ticker = market_match.group(1)
            book = self.bot.books.get(ticker) if self.bot is not None else None
            return {
                "market": {
                    "ticker": ticker,
                    "status": "open",
                    "yes_bid_dollars": (
                        book.best_bid / 100.0
                        if book is not None and book.best_bid > 0
                        else None
                    ),
                    "yes_ask_dollars": (
                        book.best_ask / 100.0
                        if book is not None and book.best_ask < 100
                        else None
                    ),
                }
            }
        if parts.path.endswith("/settlements"):
            return {"settlements": []}
        self.unknown.append({"ts": self.clock.time(), "method": "GET", "path": path})
        return {}


class TraceCollector:
    def __init__(self, clock: ReplayClock, game: dict):
        self.clock = clock
        self.game = game
        self.rows: list[dict] = []

    def record(self, event: str, details: Any, ticker: str) -> None:
        et = ticker.rsplit("-", 1)[0] if ticker else ""
        detail_event = details.get("event") if isinstance(details, dict) else None
        if et and et != self.game["event"]:
            return
        if detail_event and detail_event != self.game["event"]:
            return
        self.rows.append(
            {
                "ts": self.clock.time(),
                "event": event,
                "ticker": ticker or None,
                "leg": ticker.rsplit("-", 1)[-1] if ticker else None,
                "details": _jsonable(details or {}),
            }
        )


def import_live_v4(clock: ReplayClock, run_dir: Path):
    if str(EXECUTOR) not in sys.path:
        sys.path.insert(0, str(EXECUTOR))
    spec = importlib.util.spec_from_file_location("window1_live_v4_replay_target", LIVE_V4)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {LIVE_V4}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    state = run_dir / "_state"
    logs = run_dir / "_engine_logs"
    ticks = run_dir / "_suppressed_tick_logs"
    trades = run_dir / "_suppressed_trade_logs"
    for path in (state, logs, ticks, trades):
        path.mkdir(parents=True, exist_ok=True)
    module.STATE_DIR = state
    module.PROCESSED_FILE = state / "live_v3_processed.json"
    module.V4_RESTING_FILE = state / "live_v4_resting.json"
    module.COMPLETION_INCIDENT_FILE = state / "completion_incident.json"
    module.ENGAGEMENT_INCIDENT_FILE = state / "engagement_incident.json"
    module.SCHEDULE_FILE = state / "schedule.json"
    module.LOG_DIR = logs
    module.TICK_DIR = ticks
    module.TRADE_DIR = trades
    module.load_credentials = lambda: ("REPLAY", None)
    module.time = TimeProxy(clock, module.time)
    module.datetime = replay_datetime_class(clock)
    return module


def snapshot_frame(item: dict) -> str:
    return json.dumps(
        {
            "type": "orderbook_snapshot",
            "msg": {
                "market_ticker": item["ticker"],
                "yes_dollars_fp": [[p / 100.0, q] for p, q in item["bids"]],
                "no_dollars_fp": [[(100 - p) / 100.0, q] for p, q in item["asks"]],
            },
        },
        separators=(",", ":"),
    )


def trade_frame(item: dict) -> str:
    return json.dumps(
        {
            "type": "trade",
            "msg": {
                "market_ticker": item["ticker"],
                "yes_price": item["price"],
                "count": item["size"],
                "taker_side": item["taker_side"],
                "trade_id": item.get("trade_id"),
            },
        },
        separators=(",", ":"),
    )


def install_path_aim_counterfactual(bot, dial: dict | None) -> dict | None:
    """Change one fitted path-depth dial while leaving live_v4 downstream intact."""
    if not dial:
        return None
    if dial.get("kind") != "path_aim_shift":
        raise ValueError(f"unsupported counterfactual dial: {dial}")

    page = str(dial["page"])
    shift = int(dial["shift_cents"])
    original_atlas = bot._trendpath_atlas
    original_pages = original_atlas()
    original_page = original_pages.get(page)
    if not original_page:
        raise ValueError(f"counterfactual atlas page is absent: {page}")
    original_depth = (original_page.get("bottom") or {}).get("depth_p50")
    if original_depth is None:
        raise ValueError(f"counterfactual page has no depth_p50: {page}")
    changed_depth = max(0, float(original_depth) - shift)

    def counterfactual_atlas():
        pages = copy.deepcopy(original_atlas())
        row = pages.get(page)
        if row is None:
            raise ValueError(f"counterfactual atlas page disappeared: {page}")
        row.setdefault("bottom", {})["depth_p50"] = changed_depth
        return pages

    bot._trendpath_atlas = counterfactual_atlas
    return {
        "kind": "path_aim_shift",
        "leg": dial["leg"],
        "page": page,
        "requested_aim_shift_cents": shift,
        "depth_p50_before": original_depth,
        "depth_p50_after": changed_depth,
        "law": (
            "one fitted path-depth dial changed; every clamp, authority, order, "
            "fill, headroom, sibling, exit, hold, walk, and park method remains live_v4"
        ),
    }


async def replay_one(
    game: dict,
    print_ranges: dict[str, list[int]],
    out_dir: Path,
    counterfactual: dict | None = None,
) -> dict:
    event = game["event"]
    run_dir = out_dir / "runs" / event
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    all_prints: dict[str, list[dict]] = {}
    window_prints: dict[str, list[dict]] = {}
    tick_rows: dict[str, list[dict]] = {}
    prior_ticks: dict[str, dict | None] = {}
    for leg in game["legs"]:
        tk = leg["ticker"]
        # Read the whole ticker block for honest REST lifetime volume and latest
        # pre-window seed; execution is still clipped at the frozen horizon.
        rows, _ = load_print_block(tk, print_ranges, float("-inf"), float("inf"))
        all_prints[tk] = rows
        window_prints[tk] = [
            x for x in rows if game["left_ts"] <= x["ts"] <= game["right_ts"]
        ]
        ticks, prior = load_tick_block(tk, game["left_ts"], game["right_ts"])
        tick_rows[tk] = ticks
        prior_ticks[tk] = prior

    clock = ReplayClock(game["left_ts"])
    module = import_live_v4(clock, run_dir)
    restore_sqlite = install_vps_database_replay(clock)
    source_hash_before = _sha256(LIVE_V4)
    bot = module.LiveV3()
    applied_counterfactual = install_path_aim_counterfactual(bot, counterfactual)
    source_hash_after_init = _sha256(LIVE_V4)
    if source_hash_before != source_hash_after_init:
        raise RuntimeError("live_v4.py changed during import/initialization")

    collector = TraceCollector(clock, game)
    original_log = bot._log

    def observed_log(name, details=None, ticker=""):
        collector.record(name, details or {}, ticker)
        return original_log(name, details, ticker=ticker)

    bot._log = observed_log
    # These are output sinks only.  Suppressing their duplicate CSV writes does
    # not alter books, tape memory, decisions, orders, or fills.
    bot._log_tick = lambda *_args, **_kwargs: None
    bot._log_trade = lambda *_args, **_kwargs: None
    bot.session = SimpleNamespace()
    paper = module.PaperApi(bot=bot)
    module._PAPER_API = paper
    milestone = None
    if MILESTONES.exists():
        with MILESTONES.open(encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                if row.get("event_id") == event:
                    milestone = row
                    break
    rest = ReplayRest(game, clock, all_prints, milestone)
    rest.bot = bot

    async def api_get(s, ak, pk, path, rl):
        if path.startswith("/trade-api/v2/portfolio/"):
            return await paper.handle_get(s, ak, pk, path, rl)
        return await rest.get(s, ak, pk, path, rl)

    async def api_post(s, ak, pk, path, payload, rl):
        if path.startswith("/trade-api/v2/portfolio/"):
            return await paper.handle_post(s, ak, pk, path, payload, rl)
        rest.unknown.append(
            {"ts": clock.time(), "method": "POST", "path": path, "payload": payload}
        )
        return {}

    async def api_delete(s, ak, pk, path, rl):
        if path.startswith("/trade-api/v2/portfolio/"):
            return await paper.handle_delete(s, ak, pk, path, rl)
        rest.unknown.append({"ts": clock.time(), "method": "DELETE", "path": path})
        return {}

    module.api_get = api_get
    module.api_post = api_post
    module.api_delete = api_delete

    # Discovery is the real live_v4 method.  The replay REST catalog supplies
    # only the frozen event, with its actual occurrence clock and tape volume.
    discovered = await bot.discover_markets()

    # Seed both books with the last recorded top-five state at/before the
    # frozen left edge, then route on the real event-driven entry point.
    for leg in game["legs"]:
        tk = leg["ticker"]
        prior = prior_ticks.get(tk)
        if prior:
            bot._ingest_ws_frame(snapshot_frame(prior))
            await bot.on_bbo_update(tk)

    stream = []
    seq = 0
    for rows, kind in (
        ((x for v in tick_rows.values() for x in v), "snapshot"),
        ((x for v in window_prints.values() for x in v), "trade"),
    ):
        for item in rows:
            seq += 1
            # snapshots precede prints on exact timestamp ties
            priority = 0 if kind == "snapshot" else 1
            stream.append((item["ts"], priority, seq, kind, item))
    stream.sort(key=lambda x: (x[0], x[1], x[2]))

    due = {
        "gun": game["left_ts"],
        "fill": game["left_ts"],
        "route": game["left_ts"],
        "reconcile": game["left_ts"] + 61,
        "stale": game["left_ts"] + 121,
        "discovery": game["left_ts"] + 302,
    }

    async def run_due(until: float) -> None:
        while True:
            name, ts = min(due.items(), key=lambda kv: kv[1])
            if ts > until or ts > game["right_ts"]:
                return
            clock.set(ts)
            if name == "gun":
                try:
                    await bot._gun_poll()
                except Exception as exc:
                    bot._log("replay_timer_error", {"timer": name, "error": str(exc)})
                due[name] += max(1, int(bot.gun_poll_sec)) + 1
            elif name == "fill":
                await bot.check_fills()
                due[name] += int(module.FILL_CHECK_INTERVAL) + 1
            elif name == "route":
                await bot.routing_tick()
                due[name] += int(module.ROUTING_SWEEP_INTERVAL) + 1
            elif name == "reconcile":
                await bot.reconcile(quiet=True)
                bot._band_cascade_pass(clock.time())
                due[name] += 61
            elif name == "stale":
                await bot.validate_resting_buys()
                due[name] += int(module.STALE_CHECK_INTERVAL) + 1
            elif name == "discovery":
                await bot.discover_markets()
                due[name] += int(module.DISCOVERY_INTERVAL) + 1

    for ts, _priority, _seq, kind, item in stream:
        await run_due(ts)
        clock.set(ts)
        if kind == "snapshot":
            bot._ingest_ws_frame(snapshot_frame(item))
            await bot.on_bbo_update(item["ticker"])
        else:
            bot._ingest_ws_frame(trade_frame(item))
    await run_due(game["right_ts"])
    clock.set(game["right_ts"])
    await bot.check_fills()
    bot._band_cascade_pass(clock.time())

    traces_by_leg = defaultdict(list)
    for row in collector.rows:
        traces_by_leg[row.get("leg")].append(row)

    positions = {}
    completions = 0
    for leg in game["legs"]:
        tk = leg["ticker"]
        ppos = paper.paper_positions.get(tk)
        lpos = bot.positions.get(tk)
        filled = bool(ppos and ppos.qty > 0)
        completions += int(filled)
        positions[leg["leg"]] = {
            "ticker": tk,
            "filled": filled,
            "paper_position": _jsonable(ppos.to_kalshi_dict()) if ppos else None,
            "live_position": _jsonable(vars(lpos)) if lpos else None,
            "orders": [
                _jsonable(order.to_kalshi_dict())
                for order in paper.paper_orders.values()
                if order.ticker == tk
            ],
            "trace": traces_by_leg.get(leg["leg"], []),
            "tape_truth": game["tape_truth"].get(leg["leg"]),
        }

    source_hash_after = _sha256(LIVE_V4)
    if source_hash_before != source_hash_after:
        raise RuntimeError("live_v4.py changed during replay")

    input_breaks = []
    seen_breaks = set()
    for row in collector.rows:
        if row["event"] != "gun_feed_error":
            continue
        key = (row["details"].get("src"), row["details"].get("err"))
        if key in seen_breaks:
            continue
        seen_breaks.add(key)
        input_breaks.append(
            {
                "ts": row["ts"],
                "source": row["details"].get("src"),
                "error": row["details"].get("err"),
            }
        )
    for call in rest.unknown:
        key = (call["method"], call["path"])
        if key in seen_breaks:
            continue
        seen_breaks.add(key)
        input_breaks.append(
            {
                "ts": call["ts"],
                "source": "REST",
                "error": (
                    f"unavailable replay response: "
                    f"{call['method']} {call['path']}"
                ),
            }
        )
    input_breaks.sort(key=lambda x: x["ts"])

    result = {
        "schema_version": "window1-live-v4-replay-event-v1",
        "event": event,
        "category": game["category"],
        "slice": game["slice"],
        "frozen_window": {"left_ts": game["left_ts"], "right_ts": game["right_ts"]},
        "fill_model": FILL_MODEL,
        "counterfactual": applied_counterfactual,
        "live_v4": {
            "path": str(LIVE_V4),
            "sha256_before": source_hash_before,
            "sha256_after": source_hash_after,
            "class": f"{module.LiveV3.__module__}.{module.LiveV3.__name__}",
            "config_path": str(module.CONFIG_PATH),
            "config_sha256": _sha256(module.CONFIG_PATH),
        },
        "policy": {"combined_goal": int(bot.combined_goal)},
        "discovered_tickers": sorted(discovered),
        "positions": positions,
        "pair_completed": completions == 2,
        "trace": collector.rows,
        "first_input_break": input_breaks[0] if input_breaks else None,
        "input_breaks": input_breaks,
        "unavailable_rest_calls": rest.unknown,
        "input_counts": {
            "bbo_ticks": sum(len(x) for x in tick_rows.values()),
            "true_prints": sum(len(x) for x in window_prints.values()),
            "observed_starts_source": str(OBSERVED_STARTS),
            "observed_starts_sha256": _sha256(OBSERVED_STARTS),
            "observed_starts_visibility": "inserted_at <= replay clock",
            "tennis_db_source": str(TENNIS_DB),
            "tennis_db_sha256": _sha256(TENNIS_DB),
            "tennis_db_access": "read_only",
        },
    }
    (run_dir / "trace.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    try:
        bot.log_file.close()
    except Exception:
        pass
    restore_sqlite()
    return result


_VOLATILE_TRACE_KEYS = {"client_order_id"}


def _normalize_trace_value(value):
    if isinstance(value, dict):
        return {
            key: _normalize_trace_value(item)
            for key, item in value.items()
            if key not in _VOLATILE_TRACE_KEYS
        }
    if isinstance(value, list):
        return [_normalize_trace_value(item) for item in value]
    return value


def _keyed_trace(rows: list[dict]) -> list[dict]:
    counts = defaultdict(int)
    out = []
    for row in rows:
        base = (round(float(row["ts"]), 6), row["event"], row.get("leg"))
        counts[base] += 1
        out.append(
            {
                "key": (*base, counts[base]),
                "row": _normalize_trace_value(row),
            }
        )
    return out


def _trace_layer(event: str) -> str:
    if event in {
        "schedule_match",
        "kalshi_occ_delta",
        "window_open_set",
        "discovery",
        "entry_dossier",
        "band_call",
        "band_recall",
        "pair_class_read",
        "orientation_prior",
        "conviction_shadow",
    }:
        return "recognition_and_dossier"
    if "aim" in event or event in {
        "trendpath_shadow",
        "price_authority",
        "authority_foreign_order_flag",
        "sizing_shadow",
    }:
        return "authority_and_aim"
    if event in {
        "v4_place",
        "order_placed",
        "paper_order_posted",
        "staircase_hold_place",
        "os_shadow",
        "skipped",
    } or any(word in event for word in ("walk", "park", "hold", "repost")):
        return "post_hold_walk_park"
    if "fill" in event or event in {
        "completion_booking_adoption",
        "reconcile_v4_adopted",
        "naked_leg_defect",
    }:
        return "fills_and_booking"
    if "completion" in event or "sibling" in event or "headroom" in event:
        return "headroom_and_sibling"
    if "exit" in event or "settle" in event:
        return "exit_and_settlement"
    return "engine_and_tape"


def build_trace_diff(baseline: dict, counterfactual: dict, dial: dict) -> dict:
    left = _keyed_trace(baseline["trace"])
    right = _keyed_trace(counterfactual["trace"])
    matcher = difflib.SequenceMatcher(
        a=[item["key"] for item in left],
        b=[item["key"] for item in right],
        autojunk=False,
    )
    differences = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for li, rj in zip(range(i1, i2), range(j1, j2)):
                if left[li]["row"] == right[rj]["row"]:
                    continue
                event = left[li]["row"]["event"]
                differences.append(
                    {
                        "kind": "details_changed",
                        "layer": _trace_layer(event),
                        "key": left[li]["key"],
                        "baseline": left[li]["row"],
                        "counterfactual": right[rj]["row"],
                    }
                )
            continue
        left_rows = [item["row"] for item in left[i1:i2]]
        right_rows = [item["row"] for item in right[j1:j2]]
        events = {
            row["event"]
            for row in left_rows + right_rows
        }
        layers = sorted({_trace_layer(event) for event in events})
        differences.append(
            {
                "kind": tag,
                "layers": layers,
                "baseline": left_rows,
                "counterfactual": right_rows,
            }
        )

    layer_summary = defaultdict(lambda: {"differences": 0, "events": set()})
    for difference in differences:
        layers = difference.get("layers") or [difference["layer"]]
        rows = difference.get("baseline", [])
        if isinstance(rows, dict):
            rows = [rows]
        rows += (
            difference.get("counterfactual", [])
            if isinstance(difference.get("counterfactual"), list)
            else [difference.get("counterfactual")]
        )
        events = {row["event"] for row in rows if row}
        for layer in layers:
            layer_summary[layer]["differences"] += 1
            layer_summary[layer]["events"].update(events)

    return {
        "schema_version": "window1-live-v4-counterfactual-diff-v1",
        "event": baseline["event"],
        "same_tape": {
            "frozen_window": baseline["frozen_window"],
            "baseline_counts": baseline["input_counts"],
            "counterfactual_counts": counterfactual["input_counts"],
        },
        "dial": dial,
        "first_divergence": differences[0] if differences else None,
        "layers": {
            layer: {
                "differences": row["differences"],
                "events": sorted(row["events"]),
            }
            for layer, row in sorted(layer_summary.items())
        },
        "downstream_differences": differences,
        "outcomes": {
            "baseline": _counterfactual_outcome(baseline),
            "counterfactual": _counterfactual_outcome(counterfactual),
        },
    }


def _first_trace(result: dict, event: str, leg: str | None = None) -> dict | None:
    return next(
        (
            row
            for row in result["trace"]
            if row["event"] == event and (leg is None or row.get("leg") == leg)
        ),
        None,
    )


def _counterfactual_outcome(result: dict) -> dict:
    legs = {}
    filled_prices = []
    resting_prices = []
    for leg, row in result["positions"].items():
        buy_orders = [order for order in row["orders"] if order["action"] == "buy"]
        resting = next(
            (order for order in buy_orders if order["status"] == "resting"),
            None,
        )
        fill = _first_trace(result, "paper_fill", leg)
        fill_price = (fill or {}).get("details", {}).get("fill_price")
        if fill_price is not None:
            filled_prices.append(int(fill_price))
        if resting is not None:
            resting_prices.append(int(resting["yes_price"]))
        legs[leg] = {
            "filled": bool(row["filled"]),
            "fill_price": fill_price,
            "fill_ts": (fill or {}).get("ts"),
            "final_resting_buy": (
                int(resting["yes_price"]) if resting is not None else None
            ),
            "final_buy_statuses": [
                {"price": int(order["yes_price"]), "status": order["status"]}
                for order in buy_orders
            ],
        }
    goal = int(result["policy"]["combined_goal"])
    exposed_pair_cost = sum(filled_prices) + sum(resting_prices)
    return {
        "pair_completed": bool(result["pair_completed"]),
        "legs": legs,
        "combined_goal": goal,
        "filled_plus_resting_pair_cost": exposed_pair_cost,
        "remaining_headroom": goal - exposed_pair_cost,
    }


def _counterfactual_markdown(diff: dict, baseline: dict, variant: dict) -> str:
    dial = diff["dial"]
    leg = dial["leg"]
    base_aim = _first_trace(baseline, "trendpath_live_aim", leg)
    variant_aim = _first_trace(variant, "trendpath_live_aim", leg)
    first = diff["first_divergence"]
    first_row = (
        first.get("baseline")
        if first and isinstance(first.get("baseline"), dict)
        else None
    )
    first_event = (first_row or {}).get("event") or (first or {}).get("kind")
    first_ts = (first_row or {}).get("ts")
    bo = diff["outcomes"]["baseline"]
    co = diff["outcomes"]["counterfactual"]
    lines = [
        f"# Counterfactual replay — {diff['event']}",
        "",
        "Same frozen tape, same clock, same live_v4 source, one changed dial.",
        "",
        "## Dial",
        "",
        f"- Leg: `{leg}`",
        f"- Atlas page: `{dial['page']}`",
        (
            f"- Path depth p50: {dial['depth_p50_before']}¢ → "
            f"{dial['depth_p50_after']}¢"
        ),
        f"- Requested aim movement: +{dial['requested_aim_shift_cents']}¢",
        (
            f"- Executed path aim: "
            f"{(base_aim or {}).get('details', {}).get('path_aim')}¢ → "
            f"{(variant_aim or {}).get('details', {}).get('path_aim')}¢"
        ),
        "",
        "## First separation",
        "",
        f"- Event: `{first_event}`",
        f"- Replay timestamp: `{first_ts}`",
        (
            "- The requested aim was passed through every unchanged live_v4 "
            "clamp and authority before the order was posted."
        ),
        "",
        "## Outcome",
        "",
        "| Run | Pair complete | Filled + resting pair cost | Headroom |",
        "|---|---:|---:|---:|",
        (
            f"| Baseline | {bo['pair_completed']} | "
            f"{bo['filled_plus_resting_pair_cost']}¢ | "
            f"{bo['remaining_headroom']}¢ |"
        ),
        (
            f"| Counterfactual | {co['pair_completed']} | "
            f"{co['filled_plus_resting_pair_cost']}¢ | "
            f"{co['remaining_headroom']}¢ |"
        ),
        "",
        "### Leg outcomes",
        "",
        "| Leg | Baseline | Counterfactual |",
        "|---|---|---|",
    ]
    for name in sorted(bo["legs"]):
        b = bo["legs"][name]
        c = co["legs"][name]
        lines.append(
            f"| {name} | filled={b['filled']}, fill={b['fill_price']}, "
            f"resting={b['final_resting_buy']} | "
            f"filled={c['filled']}, fill={c['fill_price']}, "
            f"resting={c['final_resting_buy']} |"
        )
    lines += [
        "",
        "## Downstream layer diff",
        "",
        "| Layer | Changed trace blocks | Events affected |",
        "|---|---:|---|",
    ]
    for layer, row in diff["layers"].items():
        lines.append(
            f"| {layer} | {row['differences']} | {', '.join(row['events'])} |"
        )
    lines += [
        "",
        "The complete aligned downstream diff is in `COUNTERFACTUAL_DIFF.json`; "
        "the baseline and counterfactual trace files remain separate and complete.",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--event", help="Replay one event from the frozen 804-game scope")
    p.add_argument("--all", action="store_true", help="Replay all 804 games")
    p.add_argument(
        "--counterfactual-aim-shift",
        metavar="LEG=DELTA",
        help=(
            "Run baseline plus one path-aim counterfactual for a single event; "
            "example: ALV=+2"
        ),
    )
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return p.parse_args()


def _parse_aim_shift(raw: str) -> tuple[str, int]:
    match = re.fullmatch(r"([A-Z0-9]+)=([+-]?\d+)", raw.strip().upper())
    if not match:
        raise SystemExit(
            "--counterfactual-aim-shift must be LEG=DELTA, for example ALV=+2"
        )
    leg, shift = match.group(1), int(match.group(2))
    if shift == 0:
        raise SystemExit("counterfactual aim shift must be non-zero")
    return leg, shift


async def async_main() -> int:
    args = parse_args()
    if not args.event and not args.all:
        raise SystemExit("choose --event EVENT_ID or --all")
    if args.counterfactual_aim_shift and (not args.event or args.all):
        raise SystemExit("counterfactual replay requires exactly one --event")
    args.out.mkdir(parents=True, exist_ok=True)
    games = load_scope(args.event)
    ranges = build_print_index(PRINTS, args.out / "_input_index" / "prints_by_ticker.json")

    if args.counterfactual_aim_shift:
        leg, shift = _parse_aim_shift(args.counterfactual_aim_shift)
        game = games[0]
        if leg not in {row["leg"] for row in game["legs"]}:
            raise SystemExit(f"leg {leg} is not in {game['event']}")
        root = args.out / "counterfactual" / game["event"]
        print(f"[baseline] replay {game['event']}", flush=True)
        baseline = await replay_one(game, ranges, root / "baseline")
        baseline_aim = _first_trace(baseline, "trendpath_live_aim", leg)
        if baseline_aim is None:
            raise SystemExit(f"baseline produced no trendpath aim for leg {leg}")
        dial = {
            "kind": "path_aim_shift",
            "leg": leg,
            "page": baseline_aim["details"]["page"],
            "shift_cents": shift,
        }
        print(
            f"[counterfactual] replay {game['event']} {leg} aim {shift:+d}c",
            flush=True,
        )
        variant = await replay_one(
            game,
            ranges,
            root / "variant",
            counterfactual=dial,
        )
        applied = variant["counterfactual"]
        diff = build_trace_diff(baseline, variant, applied)
        root.mkdir(parents=True, exist_ok=True)
        diff_path = root / "COUNTERFACTUAL_DIFF.json"
        report_path = root / "COUNTERFACTUAL_DIFF.md"
        diff_path.write_text(
            json.dumps(diff, indent=2, sort_keys=True), encoding="utf-8"
        )
        report_path.write_text(
            _counterfactual_markdown(diff, baseline, variant), encoding="utf-8"
        )
        summary = {
            "event": game["event"],
            "dial": applied,
            "first_divergence": diff["first_divergence"],
            "outcomes": diff["outcomes"],
            "baseline_trace": str(
                root / "baseline" / "runs" / game["event"] / "trace.json"
            ),
            "counterfactual_trace": str(
                root / "variant" / "runs" / game["event"] / "trace.json"
            ),
            "diff": str(diff_path),
            "report": str(report_path),
        }
        (root / "COUNTERFACTUAL_SUMMARY.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
        )
        print(json.dumps(summary, indent=2), flush=True)
        return 0

    results = []
    for i, game in enumerate(games, 1):
        print(f"[{i}/{len(games)}] replay {game['event']}", flush=True)
        results.append(await replay_one(game, ranges, args.out))
    first_break = next(
        (x["first_input_break"] for x in results if x["first_input_break"]),
        None,
    )
    valid_for_scoring = first_break is None
    summary = {
        "schema_version": "window1-live-v4-replay-summary-v1",
        "fill_model": FILL_MODEL,
        "games": len(results),
        "valid_for_scoring": valid_for_scoring,
        "first_input_break": first_break,
        "completions_out_of_804": (
            sum(bool(x["pair_completed"]) for x in results)
            if valid_for_scoring
            else None
        ),
        "results": [
            {
                "event": x["event"],
                "pair_completed": x["pair_completed"],
                "trace_path": f"runs/{x['event']}/trace.json",
            }
            for x in results
        ],
    }
    (args.out / "REPLAY_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2), flush=True)
    return 0


def main() -> int:
    return asyncio.run(async_main())


if __name__ == "__main__":
    raise SystemExit(main())
