#!/usr/bin/env python3
"""
live_v4.py - Path B v4 bid-laying executor (forked from live_v3.py).

Strategy: docs/bid_laying_policy_v1.md Sections 2-7 + Section 12 (v4 net-PnL
offsets). For each atlas-qualifying paired leg, post a maker bid at
T-(placement_minute) per the leg's anchor regime; marketable-taker if the
target bid is already at/through the ask, else resting maker; T-20m taker
fallback (= atlas baseline). Exit per the adaptive exit band table: "exit at
+X" with >=250ct depth, or "hold to settlement" (no exit posted; Bug 4 closes).

Entry table : docs/policy/per_regime_offsets_v2.csv
Exit table  : data/durable/spike_volatility_map/{category}_adaptive_exit_bands.parquet
Config      : config/deploy_v5.json (live_v3.py keeps deploy_v4.json -- rollback)

Bug 4 settlement detection (WS market_lifecycle_v2 + REST safety-net + BBO
backstop + idempotent process_settlement chokepoint) is inherited VERBATIM from
live_v3.py @366d8aa -- DO NOT modify those paths.
"""

import asyncio
import aiohttp
import base64
import json
import os
import sys
import time
import traceback
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Set, List, Optional
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from fv import get_consensus_fv, check_fv_stability

try:
    from intelligence import recommended_window_seconds, kalshi_price_anchor
    INTELLIGENCE_AVAILABLE = True
except ImportError:
    INTELLIGENCE_AVAILABLE = False

def _parse_ticker_date(event_ticker: str):
    """Parse YYMMMDD from ticker like KXATPMATCH-26APR21GEAGAU -> datetime(2026,4,21,11,0 UTC)."""
    import re as _re
    m = _re.search(r'-(\d{2})([A-Z]{3})(\d{2})', event_ticker)
    if not m:
        return None
    yy, mmm, dd = m.groups()
    _month_map = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
                  "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
    if mmm not in _month_map:
        return None
    try:
        return datetime(2000 + int(yy), _month_map[mmm], int(dd), 11, 0, tzinfo=timezone.utc)
    except ValueError:
        return None

# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------
BASE_URL = "https://api.elections.kalshi.com"
WS_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"
WS_PATH = "/trade-api/ws/v2"
MAX_RPS = 8
MIN_VOLUME = 0
MAX_HOURS_TO_EXPIRY = 36
WS_PING_INTERVAL = 30
WS_SUBSCRIBE_BATCH = 50
DISCOVERY_INTERVAL = 300
# ENTRY_CANCEL_TIMEOUT removed in V4.2 -- replaced by match-start-aware expiry
FILL_CHECK_INTERVAL = 5      # poll fills every 5s
EXIT_PRICE_CAP = 98           # never post exit above 98c
ENTRY_BUFFER_SEC = 900        # stop entering 15 min before scheduled start
ENTRY_MAX_LEAD_SEC_BY_SERIES = {
    "KXATPMATCH": 43200,         # ATP Main Draw: 12h (books stable at T-12h, 1c spread)
    "KXWTAMATCH": 43200,         # WTA Main Draw: 12h (books stable at T-12h, 1c spread)
    "KXATPCHALLENGERMATCH": 14400,  # ATP Challenger: 4h (books not formed until T-4h)
    "KXWTACHALLENGERMATCH": 14400,  # WTA Challenger: 4h (books not formed until T-4h)
}
DEFAULT_ENTRY_MAX_LEAD_SEC = 14400

def _entry_lead_cap(event_ticker):
    series = event_ticker.split("-")[0] if event_ticker else ""
    return ENTRY_MAX_LEAD_SEC_BY_SERIES.get(series, DEFAULT_ENTRY_MAX_LEAD_SEC)
UNMATCHED_SKIP_CYCLES = 3     # skip unmatched events after this many discovery cycles
UNMATCHED_SKIP_AGE = 3600     # ...only if open_time is > 1h old
BOOK_STALENESS_SEC = 900      # 15 min — quiet pregame books may not update for 5-15 min
DEAD_SPREAD_THRESHOLD = 20    # don't post if spread > 20c
STALE_BUY_DELTA = 5           # cancel resting buy if our price > mid + 5c
PENDING_TIMEOUT_SEC = 7200    # cancel pending entry after 2h with no tight spread
STALE_CHECK_INTERVAL = 120    # validate resting buys every 2 min
SETTLEMENT_POLL_INTERVAL = 300  # Bug 4 §6.3: REST settlements safety-net poll every 5 min (LIVE only)
SETTLEMENT_RETRY_COOLDOWN = 60  # min seconds between WS-lifecycle settlement hops per ticker (kills pre-finalized re-emit storm)
ROUTING_SWEEP_INTERVAL = 60     # backstop full-universe routing sweep cadence (placement is event-driven via on_bbo_update)

# v4 bid-laying timing (all ET-relative to scheduled match start)
V4_MAX_PLACEMENT_SEC = 240 * 60   # earliest placement in per_regime_offsets_v2 (T-4h)
V4_T20M_SEC = 20 * 60             # T-20m taker fallback = atlas baseline entry
V4_REPRICE_MOVE_CENTS = 5         # resting bid re-post threshold (1 cell width); STEP 5 heuristic
# [C-JOIN-TRIAL] pre-registered degraded-deploy abort bars -- LOCKED before the trial runs
# (mirror C-ABORT-SEAL falsifiable-magnitude discipline). The bid_low<=L validation is a
# price-touch UPPER BOUND; real Kalshi is price-time priority and the walk resets queue
# position ~5x more than static, so live queue-conditional fill is unmeasured. The trial
# measures it; the abort kills it if queue starvation is confirmed:
#   ABORT iff, over the first JOIN_TRIAL_MIN_RESOLVED resolved attempts, BOTH bars trip:
#     mean(re-posts/leg) > JOIN_TRIAL_ABORT_REPOSTS  AND  fill_rate < JOIN_TRIAL_ABORT_FILLRATE
JOIN_TRIAL_MIN_RESOLVED   = 10      # evaluate only after >=10 attempts reached fill-or-cancel
JOIN_TRIAL_ABORT_REPOSTS  = 20.0    # mean re-posts/leg ABOVE this ...
JOIN_TRIAL_ABORT_FILLRATE = 0.60    # ... AND fill_rate BELOW this -> abort the join trial
# [C-STAIRCASE SHIP-2 abort-spec] Plex-ratified BAR gates for the ATP_MAIN staircase walk. Source:
# docs/policy/range_final_ATP_MAIN_abort_fills.csv (source_sha 4e4c1553, mean(offset)=1.9388, n=3595).
# ABORT iff, over the first STAIRCASE_MIN_RESOLVED resolved staircase legs, BOTH bars trip:
#   mean(realized depth) < STAIRCASE_ABORT_DEPTH  AND  fill_rate < STAIRCASE_ABORT_FILLRATE.
# DEPTH = mean(offset) - 0.5c margin = 1.9388 - 0.5 = 1.44 (ratified). Halts NEW staircase entries;
# resting legs continue (placement-side skip only). Mirrors the join_trial_aborted flag pattern.
STAIRCASE_MIN_RESOLVED   = 10
# [C-STAIRCASE 4CAT] per-cat abort bars (abort_validation harness 2026-06-19; ATP_MAIN reproduced EXACTLY).
# The other 3 cats fill DEEPER (mean offset 2.2-2.4c vs 1.94) so each needs its OWN DEPTH bar.
STAIRCASE_ABORT_FILLRATE = {"ATP_MAIN": 0.623, "WTA_MAIN": 0.602, "ATP_CHALL": 0.621, "WTA_CHALL": 0.685}
STAIRCASE_ABORT_DEPTH    = {"ATP_MAIN": 1.44,  "WTA_MAIN": 1.89,  "ATP_CHALL": 1.88,  "WTA_CHALL": 1.71}
V4_PAIRED_BASIS_CAP = 99          # T50: refuse entering BOTH sides of an event when (this side + sibling) basis > this cap. yes+no > ~100 is a guaranteed loss (KESMAR 37+75=112). Ported from arb_executor_ws.py intra-k combined=ask_a+ask_b math (negative space). Cap 99 leaves ~1c for the taker fee.

# T51 match-live detection (VOLUME ACCELERATION, not price-move — a tight even
# match stays price-flat so price-move is blind, proven on TIAARN's 50-51c book).
LIVE_DETECT_WINDOW_SEC = 60       # rolling window for the trade-burst signal
LIVE_TRADE_BURST = 10             # >= this many trade prints in the window across both legs => match is live (tunable; pre-match tennis books trade far below this)
LIVE_TRADE_RETENTION_SEC = 600    # prune per-ticker trade-time deques older than this
# [C-FEEDER FIX-1] time-to-start floor + two-stage latch + counter-evidence
# unlatch. Envelope from the C-DETECTOR-EVAL teardown (deployed K=10/T=60):
# genuine starts latch within ~60s of onset (p50=9s p90=61s); false fires
# cluster >=30min before the feed start (68.5% of events). A burst seen with
# more than the floor still on the clock is noise by construction (the
# 2026-06-12 5AM block: ZHAMAN/MPEBUB/BLAJOR scratched at T-3.5h..4h).
LIVE_DETECT_TTS_FLOOR_SEC = 1800       # volume burst can NEVER latch when feed tts > 30min
LIVE_DETECT_CONFIRM_MIN_GAP_SEC = 60   # stage-2 confirm needs a burst >= one full window after stage-1
LIVE_DETECT_CONFIRM_TTL_SEC = 300      # stage-1 evidence expires; a real live match re-arms instantly
LIVE_DETECT_UNLATCH_QUIET_SEC = 300    # latched + tts>floor + tape quiet this long => false latch, clear
FV_BURST_RETENTION_SEC = 6 * 3600      # [C-FV-BURST] age-prune the observe-only fv-burst snapshot dict
MAX_TAKER_SPREAD = 5              # T52: never TAKER-cross when (ask-bid) > this. The KESMAR fat-spread cross paid a wide ask; a wide spread means the taker floor isn't cleanly achievable -> stay flat rather than overpay. Tunable; resting-maker entries are unaffected.

# T58 premarket maker entry — live running-mid anchor (Stage-2-validated
# close-proxy: trailing-30-min mean of LAST-TRADED price, pure live microstructure,
# NOT eventual close). When trade history is too sparse, fall back to the BBO mid.
V4_RUNNING_MID_WINDOW_SEC = 30 * 60   # trailing window for the running-mid (RUNNING_MID_K=30 in the surface build)
V4_RUNNING_MID_MIN_TRADES = 1         # >= this many traded prints in-window to use running-mid; else BBO-mid fallback
V4_LAST_TRADE_MAX_AGE_SEC = 1800      # #1 ref-price: max age (s) of the last-traded print to use as the entry reference; staler/absent -> skip (no BBO-mid fallback)
V4_SHUTDOWN_TIMEOUT_SEC = 10          # #0-infra: graceful-shutdown budget; if cancel/drain exceeds this, hard-exit rather than wedge in a zombie state

# PART-2 completion_reprice (Plex-gated, default OFF). Mechanism: when leg-1 of a pair
# fills and the pair is NOT over the T50 cap, reprice the sibling's resting entry bid to
# s1 = min(s0 + X_cell, sibling_ask - 1, 99 - leg1_basis) sized to leg-1's FILLED qty.
# Frame: WINDOW-OPEN (the leg's first last-trade reference at-or-after T-240) -- the cell
# keying the eligibility table is NEVER computed from current_price (frame-mismatch leak).
# Eligibility: docs/policy/completion_cells_v1.csv (SHIP_FIRST, 1944b250 tape replay).
V4_COMPLETION_FRESHNESS_SEC = 600     # item 4: completion bid resting 10 min unfilled -> re-evaluate. Ships at 10; evidence logged (completion_freshness) for post-hoc tuning, not tuned now.
V4_WINDOW_OPEN_MAX_AGE_SEC = 172800   # prune window-open frames older than 48h on state save (events long past)

STATE_DIR = Path(__file__).resolve().parent / "state"
PROCESSED_FILE = STATE_DIR / "live_v3_processed.json"
V4_RESTING_FILE = STATE_DIR / "live_v4_resting.json"  # v4 resting-bid recovery (STEP 5)
COMPLETION_INCIDENT_FILE = STATE_DIR / "completion_incident.json"  # [C-TRIPWIRE] survives restart; remove BY HAND to re-arm
ENGAGEMENT_INCIDENT_FILE = STATE_DIR / "engagement_incident.json"  # [C-JOINBID AMEND] same discipline, engagement mechanism
SCHEDULE_FILE = STATE_DIR / "schedule.json"
TICK_DIR = Path(__file__).resolve().parent / "analysis" / "premarket_ticks"
TRADE_DIR = Path(__file__).resolve().parent / "analysis" / "trades"

SERIES_MAP = {
    'ATP_MAIN': ['KXATPMATCH'],
    'WTA_MAIN': ['KXWTAMATCH'],
    'ATP_CHALL': ['KXATPCHALLENGERMATCH'],
    'WTA_CHALL': ['KXWTACHALLENGERMATCH'],
    'ATP_SLAM': ['KXATPGRANDSLAM'],
    'WTA_SLAM': ['KXWTAGRANDSLAM'],
    # [C-COPILOT ITF] SEE-NOT-TRADE: discovery/mapping VISIBILITY ONLY -- the
    # bot NEVER places ITF entries (categories_enabled untouched; placement,
    # engagement, offset table, FIX-6 all sit behind that gate). Manual fills
    # adopt with attribution ITF_M/ITF_W; exits borrow the Challenger EXIT
    # surface at the fill cent (ITF_EXIT_BORROW) without polluting native
    # CHALL cells (ledger keys on the position's own category).
    'ITF_M': ['KXITFMATCH'],
    'ITF_W': ['KXITFWMATCH'],
}
ITF_VISIBILITY_CATS = ('ITF_M', 'ITF_W')
ITF_EXIT_BORROW = {'ITF_M': 'ATP_CHALL', 'ITF_W': 'WTA_CHALL'}
# [C-SCHEDULE-TRUST-FIX] schedule-source trust ranking. The dedicated feeds
# (tennisexplorer, espn -- the corroborated match schedules) outrank the
# odds-API commence proxy, which outranks a bare code/fuzzy match. A stored
# start is only corrected by a source whose rank is >= the source that set it.
SCHED_SOURCE_RANK = {'tennisexplorer': 3, 'espn': 3, 'odds_api': 2,
                     'direct_6char': 1, 'fuzzy_name': 1, 'schedule': 1}
ALL_SERIES = []
for prefixes in SERIES_MAP.values():
    ALL_SERIES.extend(prefixes)

# v4: own config file. Default is the FINALIZED live config (deploy_v5_live.json)
# so a restart WITHOUT the LIVE_V4_CONFIG env var deploys the safe foundation, not
# the stale pre-finalization deploy_v5.json (size 10 / old exit surface -- the RUN 0
# footgun, 2026-06-02). deploy_v4.json stays as live_v3.py's rollback config -- zero
# coupling. Env override var renamed so the two executors cannot share one config.
CONFIG_PATH = Path(__file__).resolve().parent / "config" / "deploy_v5_live.json"
_cfg_override = os.environ.get("LIVE_V4_CONFIG")
if _cfg_override:
    CONFIG_PATH = Path(__file__).resolve().parent / _cfg_override
LOG_DIR = Path(__file__).resolve().parent / "logs"

# -------------------------------------------------------------------------
# Credentials
# -------------------------------------------------------------------------
def load_credentials():
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent / ".env")
    except ImportError:
        pass
    api_key = os.getenv("KALSHI_API_KEY")
    pem_path = Path(__file__).resolve().parent / "kalshi.pem"
    if not pem_path.exists():
        sys.exit("[FATAL] kalshi.pem not found")
    pk = serialization.load_pem_private_key(pem_path.read_bytes(), password=None, backend=default_backend())
    return api_key, pk

def sign_request(pk, ts, method, path):
    msg = ("%s%s%s" % (ts, method, path)).encode("utf-8")
    sig = pk.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return base64.b64encode(sig).decode("utf-8")

def auth_headers(ak, pk, method, path):
    ts = str(int(time.time() * 1000))
    return {"KALSHI-ACCESS-KEY": ak,
            "KALSHI-ACCESS-SIGNATURE": sign_request(pk, ts, method, path.split("?")[0]),
            "KALSHI-ACCESS-TIMESTAMP": ts, "Content-Type": "application/json"}

# [C-ORDER-V2] Kalshi deprecated POST /trade-api/v2/portfolio/orders (410 deprecated_v1_order_endpoint)
# -> create-order-v2 at /portfolio/events/orders. side bid/ask (YES book only), price str-dollars, count
# str, time_in_force + self_trade_prevention_type required; flat response (no "order" wrapper / no _fp /
# no status). Cancel (DELETE /portfolio/orders/{id}), GET, and signing are UNCHANGED. Pure/testable.
ORDER_CREATE_V2_PATH = "/trade-api/v2/portfolio/events/orders"

def build_order_payload_v2(ticker, action, price, count, post_only, client_order_id):
    """CreateOrderV2Request body. The bot trades the YES book ONLY -> action buy=bid, sell=ask.
    price is int CENTS -> dollars string ("%.2f"); count int -> string. post_only resting -> GTC,
    crossing -> IOC (dead under maker_only_entry). self_trade_prevention_type taker_at_cross keeps
    resting makers."""
    return {
        "ticker": ticker,
        "side": "bid" if action == "buy" else "ask",
        "count": str(int(count)),
        "price": "%.2f" % (float(price) / 100.0),
        "time_in_force": "good_till_canceled" if post_only else "immediate_or_cancel",
        "self_trade_prevention_type": "taker_at_cross",
        "post_only": bool(post_only),
        "client_order_id": client_order_id,
    }

def parse_order_response_v2(resp):
    """Flat create-order-v2 response (HTTP 201; NO 'order' wrapper / NO 'status' / NO _fp suffix).
    Returns (order_id, status, fill_count, avg_fill_price_cents|None). status derived from
    remaining_count (0 -> filled, else/absent -> resting). average_fill_price dollars -> cents."""
    if not isinstance(resp, dict):
        return "", "?", 0, None
    oid = resp.get("order_id", "") or ""
    fill_count = int(float(resp.get("fill_count", 0) or 0))
    rem = resp.get("remaining_count", None)
    status = "filled" if (rem is not None and int(float(rem)) == 0) else "resting"
    afp = resp.get("average_fill_price", None)
    avg_cents = round(float(afp) * 100) if afp not in (None, "") else None
    return oid, status, fill_count, avg_cents

# -------------------------------------------------------------------------
# Rate limiter
# -------------------------------------------------------------------------
class RateLimiter:
    def __init__(self):
        self.ts = deque()
    async def acquire(self):
        now = time.monotonic()
        while self.ts and now - self.ts[0] >= 1.0:
            self.ts.popleft()
        if len(self.ts) >= MAX_RPS:
            await asyncio.sleep(1.0 - (now - self.ts[0]))
        self.ts.append(time.monotonic())

# -------------------------------------------------------------------------
# Async HTTP helpers
# -------------------------------------------------------------------------
async def _real_api_get(s, ak, pk, path, rl):
    for bo in [1, 2, 4, None]:
        await rl.acquire()
        try:
            async with s.get("%s%s" % (BASE_URL, path), headers=auth_headers(ak, pk, "GET", path),
                             timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status == 200:
                    return await r.json()
                if r.status == 429 and bo:
                    await asyncio.sleep(bo)
                    continue
                return None
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if bo:
                await asyncio.sleep(bo)
                continue
            return None
    return None

async def _real_api_post(s, ak, pk, path, payload, rl):
    for bo in [2, None]:
        await rl.acquire()
        try:
            async with s.post("%s%s" % (BASE_URL, path), headers=auth_headers(ak, pk, "POST", path),
                              json=payload, timeout=aiohttp.ClientTimeout(total=15)) as r:
                body = await r.text()
                if r.status in (200, 201):
                    return json.loads(body)
                if r.status == 429 and bo:
                    await asyncio.sleep(bo)
                    continue
                return {"_error": True, "_status": r.status, "_body": body[:500]}
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if bo:
                await asyncio.sleep(bo)
                continue
            return {"_error": True, "_status": 0, "_body": str(e)}
    return {"_error": True, "_status": 0, "_body": "exhausted retries"}

async def _real_api_delete(s, ak, pk, path, rl):
    for bo in [2, None]:
        await rl.acquire()
        try:
            async with s.delete("%s%s" % (BASE_URL, path), headers=auth_headers(ak, pk, "DELETE", path),
                                timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status in (200, 204):
                    return True
                if r.status == 429 and bo:
                    await asyncio.sleep(bo)
                    continue
                return False
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if bo:
                await asyncio.sleep(bo)
                continue
            return False
    return False

# -------------------------------------------------------------------------
# Book
# -------------------------------------------------------------------------
@dataclass
class Book:
    bids: Dict[int, int] = field(default_factory=dict)
    asks: Dict[int, int] = field(default_factory=dict)
    best_bid: int = 0
    best_ask: int = 100
    updated: float = 0.0
    last_trade_price: int = 0
    last_trade_ts: float = 0.0
    last_trade_side: str = ""

def recalc_bbo(b):
    b.best_bid = max(b.bids.keys()) if b.bids else 0
    b.best_ask = min(b.asks.keys()) if b.asks else 100

# -------------------------------------------------------------------------
# Position state per ticker
# -------------------------------------------------------------------------
@dataclass
class Position:
    ticker: str
    event_ticker: str
    category: str
    direction: str
    cell_name: str
    cell_cfg: dict

    # Entry
    entry_price: int = 0
    entry_qty: int = 0
    entry_order_id: str = ""
    entry_posted_ts: float = 0.0
    match_start_ts: float = 0.0
    entry_filled_ts: float = 0.0

    # Exit
    exit_price: int = 0
    exit_order_id: str = ""
    exit_filled: bool = False
    # [C-PARTIAL-BOOKING P0v2] partial-fill primitives (NAETAN-TAN 2026-06-12,
    # the first partial under this stack: increments 1/1/2/1 across the phase
    # flip went unbooked -> 4 shares naked).
    # exit_filled_qty: the exit-side COUNT; exit_filled (bool) means COMPLETE
    # only. entry_order_done: the entry order has reached a terminal exchange
    # status with every fill booked -> stop polling it.
    exit_filled_qty: int = 0
    entry_order_done: bool = False

    # DCA
    dca_price: int = 0
    dca_order_id: str = ""
    dca_qty: int = 0
    dca_filled: bool = False

    # Play type
    play_type: str = "A_tight"
    layered_exit_price: int = 0
    cell_exit_order_id: str = ""
    cell_exit_price: int = 0
    legacy: bool = False
    anchor_source: str = "fv_consensus"
    routed_cell: str = ""
    last_cancel_repost_ts: float = 0.0

    # State
    phase: str = "entry_pending"
    settled: bool = False
    pnl_cents: float = 0.0

    # ---- v4 bid-laying fields ----
    is_v4: bool = False
    regime_at_posting: str = ""        # e.g. "r85_94" at the minute the bid was placed
    target_price: int = 0             # the regime-offset target bid (resting maker)
    placement_minute: int = 0         # minutes-before-start this leg's bid was scheduled
    entry_mode: str = ""              # marketable_taker | resting_maker | miss_fallback
    paid_taker_fee: bool = False      # 1c/ct fee applies to marketable + fallback entries
    # P0 #5 decision (operator, 2026-05-25): fee is NOT modeled in computed
    # pnl_cents -- this flag only records the mode. The Bug-4 / paper try_fill
    # PnL math is left untouched (highest-risk surface; no edits near the
    # idempotent chokepoint before the live window). Computed PnL is ~1c/ct
    # optimistic on taker entries in BOTH paper and live; the Kalshi account
    # reconciliation reflects true fees. Paper findings report raw + fee-haircut
    # PnL; live cash is fee-accurate via exchange-side deduction.
    # [C-BID-SURVIVAL DIFF-2] set at PLACEMENT iff the resting-maker bid was
    # placed AT the join level (target == best_bid at placement). Exempts the
    # bid from bid_marketable_stale (joining the bid is the desired state, not
    # staleness). Drift bids (flag unset) keep the full stale rule. Persisted
    # sparsely in live_v4_resting.json (key present only when True).
    intended_join: bool = False
    # [C-FEEDER FIX-3] Option (a): set at PLACEMENT iff the resting-maker bid
    # was DELIBERATELY posted at ask-1 given the decision-time book (locked /
    # 1c books put the table target exactly there -- the AUGMAJ 206-cycle and
    # KRERUS 61-cycle churn storms). Exempts the bid from bid_marketable_stale
    # exactly like intended_join (placement-time key, never the current book).
    # cancel_marketable_buffer stays 1: a DRIFT bid (flag unset) that the book
    # moves onto still cancels. Persisted sparsely (key present only when True).
    intended_clamp: bool = False
    # [C-FEEDER FIX-6] A5 runway ledger: status of the validated
    # (offset, placement_minute) runway at (re)placement, and the reference
    # actually used. runway_status in {full, late_window, late_remap, sub_60};
    # reference_source == "join_late_runway" when the deep offset was
    # invalidated and the bid joined the anchor level instead. Persisted
    # sparsely (keys present only when non-default).
    runway_status: str = "full"
    reference_source: str = ""
    walk_ref: int = 0            # [C-JOIN-WALK] decision-time join target last (re-)posted -- the
                                 # re-post key (NOT shared target_price, which other paths mutate)
    join_reposts: int = 0        # [C-JOIN-TRIAL] re-post count this leg (queue-priority resets)
    join_depth_post: int = 0     # [C-JOIN-TRIAL] queue-depth-ahead at the last (re-)post
    join_post_ts: float = 0.0    # [C-JOIN-TRIAL] ts of the last (re-)post (for fill latency)
    join_is_trial: bool = False  # leg placed under the join trial (counts toward the abort bars)
    staircase_anchor: int = 0    # [C-STAIRCASE SHIP-2] FIXED deep-cast anchor, set once at placement (Risk 2)
    staircase_cell: int = 0      # [C-STAIRCASE SHIP-2] FIXED cell for final_target lookup (Risk 3)
    staircase_ref: int = 0       # [C-STAIRCASE SHIP-2] last posted staircase target (knot-crossing key, Risk 1)
    strategy: str = ""                # "exit" | "hold" (set at fill from exit table)
    exit_band_x: Optional[int] = None  # +X cents for exit cells; None for hold cells
    exit_cell_id: int = 0             # 1c cell used for the exit-table lookup (entry-priced)

    # ---- PART-2 completion_reprice fields (dormant unless completion_reprice=true).
    # Set on the SIBLING position when its bid is completion-repriced after leg-1 fills.
    completion_s0: int = 0              # sibling window-open price at attempt (replay s0)
    completion_x: int = 0               # X from completion_cells_v1 (leg-1 window-open cell)
    completion_leg1_basis: int = 0      # leg-1 fill basis at attempt (cap arithmetic frozen)
    completion_qty: int = 0             # leg-1 FILLED qty at attempt (completion size)
    completion_reprice_ts: float = 0.0  # last completion (re)price time (freshness clock)
    completion_prev_price: int = 0      # pre-completion resting bid (revert target)
    completion_prev_mode: str = ""      # pre-completion entry_mode (revert)
    completion_prev_target: int = 0     # pre-completion target_price (revert)
    completion_lookup_cell: int = 0     # leg-1 window-open cell used for the table lookup

# -------------------------------------------------------------------------
# Paper Mode (spec sha 32f29fda)
# -------------------------------------------------------------------------

_PAPER_API = None  # module-level; set at LiveV3 init when paper_mode=true


@dataclass
class PaperOrder:
    order_id: str
    ticker: str
    action: str
    side: str
    yes_price: int          # cents (internal storage)
    count: int
    remaining_count: int
    filled_count: int = 0
    status: str = "resting"
    post_ts: float = 0.0
    last_event_ts: float = 0.0
    client_order_id: str = ""
    book_depth_at_price_post: int = 0
    best_bid_at_post: int = 0
    best_ask_at_post: int = 100
    last_trade_price_at_post: int = 0
    last_trade_age_at_post: float = 0.0
    fv_anchor_at_post: Optional[float] = None
    spread_at_post: int = 0
    # [C-FV-BURST] observe-only instrumentation: FV (book mid) at the real-start
    # latch and the entry's distance from it (fill_price - fv_at_burst; positive =
    # entered ABOVE FV). Read by NOTHING in any order/cancel/repost/exit/timing
    # path; written only by _fv_burst_snapshot's consumer and _book_v4_entry_fill.
    fv_at_burst: Optional[float] = None
    entry_minus_fv_burst: Optional[float] = None

    def to_kalshi_dict(self):
        return {
            "order_id": self.order_id,
            "ticker": self.ticker,
            "action": self.action,
            "side": self.side,
            "yes_price_dollars": self.yes_price / 100.0,
            "remaining_count_fp": float(self.remaining_count),
            "fill_count_fp": float(self.filled_count),
            "average_fill_price_fp": (self.yes_price / 100.0) if self.filled_count > 0 else 0.0,
            "yes_price": self.yes_price,
            "remaining_count": self.remaining_count,
            "count_filled": self.filled_count,
            "count": self.count,
            "status": self.status,
            "client_order_id": self.client_order_id,
        }


@dataclass
class PaperPosition:
    ticker: str
    event_ticker: str = ""
    qty: int = 0
    sold_qty: int = 0
    total_cost_cents: int = 0
    total_revenue_cents: int = 0
    realized_pnl_cents: int = 0
    open_buy_orders: List[str] = field(default_factory=list)
    open_sell_orders: List[str] = field(default_factory=list)
    first_entry_ts: float = 0.0
    last_event_ts: float = 0.0
    settled: bool = False
    settlement_price: Optional[int] = None

    @property
    def net_qty(self):
        return self.qty - self.sold_qty

    @property
    def avg_price(self):
        if self.qty == 0:
            return 0
        return self.total_cost_cents // self.qty

    def to_kalshi_dict(self):
        net = self.net_qty
        exposure_dollars = (self.avg_price * net) / 100.0 if net > 0 else 0.0
        traded_dollars = (self.avg_price * self.qty) / 100.0
        return {
            "ticker": self.ticker,
            "event_ticker": self.event_ticker,
            "position_fp": float(net),
            "market_exposure_dollars": exposure_dollars,
            "total_traded_dollars": traded_dollars,
            "settlement_status": "settled" if self.settled else "unsettled",
        }


class VolumeTracker:
    """Per-ticker rolling tracker of trade prints. Normalizes Kalshi WS
    taker_side ("yes"/"no") to internal aggressor side ("buy"/"sell") at
    record-time per spec §4."""

    def __init__(self, api=None, retention_sec=21600.0):
        self.api = api
        self.trades = {}  # ticker -> deque[(ts, price, qty, side)]
        self.retention_sec = retention_sec
        self.unsided_count = 0
        self.sample_count = 0

    def record(self, ticker, ts, price, qty, taker_side):
        if taker_side == "yes":
            side = "buy"
        elif taker_side == "no":
            side = "sell"
        else:
            side = ""
            self.unsided_count += 1
        self.sample_count += 1
        if ticker not in self.trades:
            self.trades[ticker] = deque()
        dq = self.trades[ticker]
        dq.append((ts, int(price), int(qty), side))
        cutoff = ts - self.retention_sec
        while dq and dq[0][0] < cutoff:
            dq.popleft()

    def volume_at_or_through(self, ticker, side, target_price, since_ts):
        """side here is internal ("buy" or "sell")."""
        dq = self.trades.get(ticker)
        if not dq:
            return 0
        total = 0
        if side == "buy":
            for ts, price, qty, s in dq:
                if ts >= since_ts and price <= target_price and s == "sell":
                    total += qty
        else:
            for ts, price, qty, s in dq:
                if ts >= since_ts and price >= target_price and s == "buy":
                    total += qty
        return total

    def depth_for_side(self, ticker, side, price):
        if not self.api or not self.api.bot:
            return 0
        book = self.api.bot.books.get(ticker)
        if not book:
            return 0
        if side == "ask":
            return book.asks.get(price, 0)
        return book.bids.get(price, 0)


class PaperFillSimulator:
    def __init__(self, api):
        self.api = api

    def evaluate_book_cross(self, ticker):
        bot = self.api.bot
        book = bot.books.get(ticker)
        if not book:
            return
        for order in list(self.api.paper_orders.values()):
            if order.ticker != ticker or order.status != "resting":
                continue
            if order.action == "buy" and book.best_ask <= order.yes_price and book.best_ask > 0:
                self.try_fill(order, order.yes_price, time.time(), "book_cross")
            elif order.action == "sell" and book.best_bid >= order.yes_price and book.best_bid < 100:
                self.try_fill(order, order.yes_price, time.time(), "book_cross")

    def evaluate_trade_print(self, ticker, ts, price):
        for order in list(self.api.paper_orders.values()):
            if order.ticker != ticker or order.status != "resting":
                continue
            if order.action == "buy" and price <= order.yes_price:
                self.try_fill(order, order.yes_price, ts, "trade_print")
            elif order.action == "sell" and price >= order.yes_price:
                self.try_fill(order, order.yes_price, ts, "trade_print")

    def try_fill(self, order, fill_price, fill_ts, trigger):
        if order.status != "resting":
            return  # Idempotency — see spec §7
        order.status = "executed"
        order.filled_count = order.count
        order.remaining_count = 0
        order.last_event_ts = fill_ts

        bot = self.api.bot
        pos = self.api.paper_positions.get(order.ticker)
        if pos is None:
            event_ticker = bot.ticker_to_event.get(order.ticker, "")
            pos = PaperPosition(ticker=order.ticker, event_ticker=event_ticker)
            self.api.paper_positions[order.ticker] = pos

        if order.action == "buy":
            pos.qty += order.count
            pos.total_cost_cents += order.count * fill_price
            if not pos.first_entry_ts:
                pos.first_entry_ts = fill_ts
            if order.order_id in pos.open_buy_orders:
                pos.open_buy_orders.remove(order.order_id)
        else:
            pos.sold_qty += order.count
            pos.total_revenue_cents += order.count * fill_price
            if order.order_id in pos.open_sell_orders:
                pos.open_sell_orders.remove(order.order_id)
            if pos.net_qty == 0:
                pos.realized_pnl_cents = pos.total_revenue_cents - pos.total_cost_cents
        pos.last_event_ts = fill_ts

        time_to_fill_sec = fill_ts - order.post_ts
        internal_side = order.action
        vol_lifetime = self.api.volume_tracker.volume_at_or_through(
            order.ticker, internal_side, order.yes_price, order.post_ts)
        depth_side = "ask" if order.action == "buy" else "bid"
        depth_at_fill = self.api.volume_tracker.depth_for_side(
            order.ticker, depth_side, order.yes_price)
        book_now = bot.books.get(order.ticker)
        best_bid = book_now.best_bid if book_now else 0
        best_ask = book_now.best_ask if book_now else 100
        last_trade_price = book_now.last_trade_price if book_now else 0

        event = "paper_fill" if order.action == "buy" else "paper_exit_fill"
        self.api._emit(event, {
            "order_id": order.order_id,
            "fill_price": fill_price,
            "qty": order.count,
            "time_to_fill_sec": round(time_to_fill_sec, 2),
            "volume_at_or_through_lifetime": vol_lifetime,
            "depth_at_fill": depth_at_fill,
            "fill_trigger": trigger,
            "best_bid_at_fill": best_bid,
            "best_ask_at_fill": best_ask,
            "last_trade_price_at_fill": last_trade_price,
            "post_telemetry": {
                "best_bid": order.best_bid_at_post,
                "best_ask": order.best_ask_at_post,
                "depth_at_price": order.book_depth_at_price_post,
                "fv_anchor": order.fv_anchor_at_post,
                "last_trade_price": order.last_trade_price_at_post,
            },
            "entry_avg_price_after_fill": pos.avg_price,
            "net_qty_after_fill": pos.net_qty,
            "realized_pnl_cents": pos.realized_pnl_cents if order.action == "sell" else None,
        }, ticker=order.ticker)


class PaperApi:
    PAPER_STATE_VERSION = "1.0"

    def __init__(self, bot):
        self.bot = bot
        self.paper_orders = {}
        self.paper_positions = {}
        self.volume_tracker = VolumeTracker(api=self)
        self.fill_simulator = PaperFillSimulator(self)
        self.next_seq = 0
        self.last_heartbeat_ts = 0.0
        self.fills_last_hour = deque()
        self.event_counts_last_hour = deque()

    def _new_order_id(self, ticker, ts):
        self.next_seq += 1
        return "PAPER-%s-%d-%06d" % (ticker, int(ts), self.next_seq)

    def _emit(self, event, details=None, ticker=""):
        self.bot._log(event, details or {}, ticker=ticker)
        now = time.time()
        self.event_counts_last_hour.append((now, event))
        if event in ("paper_fill", "paper_exit_fill"):
            self.fills_last_hour.append(now)
        cutoff = now - 3600
        while self.event_counts_last_hour and self.event_counts_last_hour[0][0] < cutoff:
            self.event_counts_last_hour.popleft()
        while self.fills_last_hour and self.fills_last_hour[0] < cutoff:
            self.fills_last_hour.popleft()

    async def handle_get(self, s, ak, pk, path, rl):
        if not path.startswith("/trade-api/v2/portfolio/"):
            return await _real_api_get(s, ak, pk, path, rl)
        from urllib.parse import urlsplit, parse_qs
        parts = urlsplit(path)
        path_only = parts.path
        query = parse_qs(parts.query)

        # Single order: /trade-api/v2/portfolio/orders/<id>
        if path_only.startswith("/trade-api/v2/portfolio/orders/"):
            oid = path_only.split("/")[-1]
            order = self.paper_orders.get(oid)
            if not order:
                return {"order": None, "_error": "not_found"}
            return {"order": order.to_kalshi_dict()}

        # List orders
        if path_only == "/trade-api/v2/portfolio/orders":
            ticker_filter = query.get("ticker", [None])[0]
            status_filter = query.get("status", [None])[0]
            orders = []
            for o in self.paper_orders.values():
                if ticker_filter and o.ticker != ticker_filter:
                    continue
                if status_filter and o.status != status_filter:
                    continue
                orders.append(o.to_kalshi_dict())
            return {"orders": orders}

        # Positions
        if path_only == "/trade-api/v2/portfolio/positions":
            ticker_filter = query.get("ticker", [None])[0]
            settlement_filter = query.get("settlement_status", [None])[0]
            positions = []
            for p in self.paper_positions.values():
                if p.net_qty == 0:
                    continue
                if ticker_filter and p.ticker != ticker_filter:
                    continue
                if settlement_filter == "unsettled" and p.settled:
                    continue
                if settlement_filter == "settled" and not p.settled:
                    continue
                positions.append(p.to_kalshi_dict())
            return {"market_positions": positions}

        return await _real_api_get(s, ak, pk, path, rl)

    async def handle_post(self, s, ak, pk, path, payload, rl):
        if path != "/trade-api/v2/portfolio/orders":
            return await _real_api_post(s, ak, pk, path, payload, rl)
        ticker = payload.get("ticker", "")
        action = payload.get("action", "")
        side = payload.get("side", "yes")
        count = int(payload.get("count", 0))
        yes_price = int(payload.get("yes_price", 0))
        client_order_id = payload.get("client_order_id", "")
        post_ts = time.time()
        order_id = self._new_order_id(ticker, post_ts)

        book = self.bot.books.get(ticker)
        best_bid = book.best_bid if book else 0
        best_ask = book.best_ask if book else 100
        spread = (best_ask - best_bid) if (best_ask < 100 and best_bid > 0) else 0
        last_trade_price = book.last_trade_price if book else 0
        last_trade_ts = book.last_trade_ts if book else 0.0
        last_trade_age = (post_ts - last_trade_ts) if last_trade_ts else 0.0
        if action == "buy":
            depth_at_price = book.bids.get(yes_price, 0) if book else 0
            depth_opposite = book.asks.get(yes_price, 0) if book else 0
        else:
            depth_at_price = book.asks.get(yes_price, 0) if book else 0
            depth_opposite = book.bids.get(yes_price, 0) if book else 0

        fv_anchor = None
        try:
            event_ticker = self.bot.ticker_to_event.get(ticker, "")
            if event_ticker and hasattr(self.bot, "_get_side_fv"):
                side_fv = self.bot._get_side_fv(ticker, event_ticker)
                if side_fv and side_fv.get("fv_cents") is not None:
                    fv_anchor = float(side_fv["fv_cents"])
        except Exception:
            fv_anchor = None
        fv_minus_price = (fv_anchor - yes_price) if fv_anchor is not None else None

        order = PaperOrder(
            order_id=order_id, ticker=ticker, action=action, side=side,
            yes_price=yes_price, count=count, remaining_count=count,
            post_ts=post_ts, last_event_ts=post_ts, client_order_id=client_order_id,
            book_depth_at_price_post=depth_at_price,
            best_bid_at_post=best_bid, best_ask_at_post=best_ask,
            last_trade_price_at_post=last_trade_price,
            last_trade_age_at_post=last_trade_age,
            fv_anchor_at_post=fv_anchor, spread_at_post=spread,
        )
        self.paper_orders[order_id] = order

        pos = self.paper_positions.get(ticker)
        if pos is None:
            event_ticker = self.bot.ticker_to_event.get(ticker, "")
            pos = PaperPosition(ticker=ticker, event_ticker=event_ticker)
            self.paper_positions[ticker] = pos
        if action == "buy":
            pos.open_buy_orders.append(order_id)
        else:
            pos.open_sell_orders.append(order_id)

        self._emit("paper_order_posted", {
            "order_id": order_id,
            "client_order_id": client_order_id,
            "action": action, "side": side,
            "yes_price": yes_price, "count": count,
            "best_bid": best_bid, "best_ask": best_ask,
            "spread": spread,
            "depth_at_price": depth_at_price,
            "depth_opposite_side": depth_opposite,
            "last_trade_price": last_trade_price,
            "last_trade_age_sec": round(last_trade_age, 1),
            "fv_anchor": fv_anchor,
            "fv_minus_price_cents": fv_minus_price,
            "post_ts": post_ts,
        }, ticker=ticker)

        return {"order": {"order_id": order_id, "ticker": ticker, "status": "resting",
                          "yes_price": yes_price, "count": count}}

    async def handle_delete(self, s, ak, pk, path, rl):
        if not path.startswith("/trade-api/v2/portfolio/orders/"):
            return await _real_api_delete(s, ak, pk, path, rl)
        oid = path.split("/")[-1]
        order = self.paper_orders.get(oid)
        if not order or order.status != "resting":
            return False
        order.status = "canceled"
        cancel_ts = time.time()
        order.last_event_ts = cancel_ts
        pos = self.paper_positions.get(order.ticker)
        if pos:
            if oid in pos.open_buy_orders:
                pos.open_buy_orders.remove(oid)
            if oid in pos.open_sell_orders:
                pos.open_sell_orders.remove(oid)
        lifetime = cancel_ts - order.post_ts
        internal_side = order.action
        vol = self.volume_tracker.volume_at_or_through(
            order.ticker, internal_side, order.yes_price, order.post_ts)
        book = self.bot.books.get(order.ticker)
        best_bid = book.best_bid if book else 0
        best_ask = book.best_ask if book else 100
        self._emit("paper_order_cancelled", {
            "order_id": oid,
            "post_ts": order.post_ts,
            "lifetime_sec": round(lifetime, 2),
            "fills_during_lifetime": 0,
            "volume_at_or_through_lifetime": vol,
            "best_bid_at_cancel": best_bid,
            "best_ask_at_cancel": best_ask,
        }, ticker=order.ticker)
        return True

    def on_book_update(self, ticker):
        try:
            self.fill_simulator.evaluate_book_cross(ticker)
        except Exception as e:
            self.bot._log("paper_error", {"where": "on_book_update",
                                          "error": str(e)}, ticker=ticker)

    def on_trade(self, ticker, ts, price, qty, taker_side):
        try:
            self.volume_tracker.record(ticker, ts, price, qty, taker_side)
            self.fill_simulator.evaluate_trade_print(ticker, ts, price)
        except Exception as e:
            self.bot._log("paper_error", {"where": "on_trade",
                                          "error": str(e)}, ticker=ticker)

    def maybe_heartbeat(self):
        now = time.time()
        if now - self.last_heartbeat_ts < 60:
            return
        self.last_heartbeat_ts = now
        try:
            active_pos = sum(1 for p in self.paper_positions.values()
                             if p.net_qty > 0 and not p.settled)
            active_orders = sum(1 for o in self.paper_orders.values()
                                if o.status == "resting")
            mtm = self._compute_mark_to_market_cents()
            realized = sum(p.realized_pnl_cents for p in self.paper_positions.values())
            counts = {}
            cutoff = now - 3600
            for ts, event in self.event_counts_last_hour:
                if ts >= cutoff:
                    counts[event] = counts.get(event, 0) + 1
            fills_last_hour = sum(1 for ts in self.fills_last_hour if ts >= cutoff)
            self._emit("paper_heartbeat", {
                "active_paper_positions": active_pos,
                "active_paper_orders_resting": active_orders,
                "paper_pnl_mtm_cents": mtm,
                "paper_pnl_realized_cents": realized,
                "fills_in_last_hour": fills_last_hour,
                "telemetry_event_counts_last_hour": counts,
            })
            try:
                self.dump_state("/root/Omi-Workspace/arb-executor/paper_state.json")
            except Exception as e:
                self.bot._log("paper_error", {"where": "dump_state", "error": str(e)})
        except Exception as e:
            self.bot._log("paper_error", {"where": "maybe_heartbeat", "error": str(e)})

    def _compute_mark_to_market_cents(self):
        total = 0
        for pos in self.paper_positions.values():
            if pos.settled or pos.net_qty <= 0:
                continue
            book = self.bot.books.get(pos.ticker)
            best_bid = book.best_bid if book else 0
            net = pos.net_qty
            value_now = net * best_bid
            cost_basis_remaining = (pos.total_cost_cents // pos.qty) * net if pos.qty > 0 else 0
            total += value_now - cost_basis_remaining
        return total

    def dump_state(self, path):
        data = {
            "PAPER_STATE_VERSION": self.PAPER_STATE_VERSION,
            "next_seq": self.next_seq,
            "ts": time.time(),
            "orders": [o.__dict__ for o in self.paper_orders.values()],
            "positions": [p.__dict__ for p in self.paper_positions.values()],
        }
        tmp_path = path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(data, f, default=str)
        os.replace(tmp_path, path)

    def load_state(self, path, max_age_sec):
        if not os.path.exists(path):
            self._emit("paper_state_skipped", {"reason": "file_not_found"})
            return False
        mtime = os.path.getmtime(path)
        age = time.time() - mtime
        if age > max_age_sec:
            self._emit("paper_state_skipped", {"reason": "file_stale",
                                               "age_sec": round(age, 1)})
            return False
        try:
            with open(path) as f:
                data = json.load(f)
        except Exception as e:
            self._emit("paper_state_skipped", {"reason": "parse_error",
                                               "error": str(e)})
            return False
        if data.get("PAPER_STATE_VERSION") != self.PAPER_STATE_VERSION:
            self._emit("paper_state_skipped", {"reason": "version_mismatch"})
            return False
        try:
            self.next_seq = int(data.get("next_seq", 0))
            for od in data.get("orders", []):
                o = PaperOrder(
                    order_id=od["order_id"], ticker=od["ticker"],
                    action=od["action"], side=od["side"],
                    yes_price=int(od["yes_price"]), count=int(od["count"]),
                    remaining_count=int(od["remaining_count"]),
                    filled_count=int(od.get("filled_count", 0)),
                    status=od.get("status", "resting"),
                    post_ts=float(od.get("post_ts", 0.0)),
                    last_event_ts=float(od.get("last_event_ts", 0.0)),
                    client_order_id=od.get("client_order_id", ""),
                    book_depth_at_price_post=int(od.get("book_depth_at_price_post", 0)),
                    best_bid_at_post=int(od.get("best_bid_at_post", 0)),
                    best_ask_at_post=int(od.get("best_ask_at_post", 100)),
                    last_trade_price_at_post=int(od.get("last_trade_price_at_post", 0)),
                    last_trade_age_at_post=float(od.get("last_trade_age_at_post", 0.0)),
                    fv_anchor_at_post=od.get("fv_anchor_at_post"),
                    spread_at_post=int(od.get("spread_at_post", 0)),
                )
                self.paper_orders[o.order_id] = o
            for pd in data.get("positions", []):
                p = PaperPosition(
                    ticker=pd["ticker"],
                    event_ticker=pd.get("event_ticker", ""),
                    qty=int(pd.get("qty", 0)),
                    sold_qty=int(pd.get("sold_qty", 0)),
                    total_cost_cents=int(pd.get("total_cost_cents", 0)),
                    total_revenue_cents=int(pd.get("total_revenue_cents", 0)),
                    realized_pnl_cents=int(pd.get("realized_pnl_cents", 0)),
                    open_buy_orders=list(pd.get("open_buy_orders", [])),
                    open_sell_orders=list(pd.get("open_sell_orders", [])),
                    first_entry_ts=float(pd.get("first_entry_ts", 0.0)),
                    last_event_ts=float(pd.get("last_event_ts", 0.0)),
                    settled=bool(pd.get("settled", False)),
                    settlement_price=pd.get("settlement_price"),
                )
                self.paper_positions[p.ticker] = p
            self._emit("paper_state_restored", {
                "orders_loaded": len(self.paper_orders),
                "positions_loaded": len(self.paper_positions),
                "state_age_sec": round(age, 1),
                "schema_version": self.PAPER_STATE_VERSION,
            })
            return True
        except Exception as e:
            self._emit("paper_state_skipped", {"reason": "parse_error",
                                               "error": str(e)})
            return False


# -------------------------------------------------------------------------
# Module-level dispatchers (replace the original api_get/post/delete)
# -------------------------------------------------------------------------

async def api_get(s, ak, pk, path, rl):
    if _PAPER_API is not None:
        return await _PAPER_API.handle_get(s, ak, pk, path, rl)
    return await _real_api_get(s, ak, pk, path, rl)


async def api_post(s, ak, pk, path, payload, rl):
    if _PAPER_API is not None:
        return await _PAPER_API.handle_post(s, ak, pk, path, payload, rl)
    return await _real_api_post(s, ak, pk, path, payload, rl)


async def api_delete(s, ak, pk, path, rl):
    if _PAPER_API is not None:
        return await _PAPER_API.handle_delete(s, ak, pk, path, rl)
    return await _real_api_delete(s, ak, pk, path, rl)


# -------------------------------------------------------------------------
# Live V3 Bot
# -------------------------------------------------------------------------
class LiveV3:
    def __init__(self):
        self.ak, self.pk = load_credentials()
        self.rl = RateLimiter()
        self.session = None
        self.ws = None
        self.ws_connected = False

        with open(CONFIG_PATH) as f:
            self.config = json.load(f)
        self.entry_size = self.config["sizing"]["entry_contracts"]
        # v4 has no DCA. deploy_v5.json omits these keys; default safely so the
        # FV/legacy DCA paths (gated off) don't KeyError at init.
        self.dca_size = self.config["sizing"].get("dca_contracts", 0)
        self.dca_fill_floor = self.config.get("dca_fill_floor_cents", 10)
        self.exit_size = self.config["sizing"].get("exit_contracts", self.entry_size)
        # v4 toggles
        self.fv_scenarios_enabled = self.config.get("fv_anchor_scenarios_enabled", False)
        self.round5_enabled = self.config.get("round5_detector_enabled", False)
        self.exit_depth_floor = self.config.get("min_depth_for_exit_realization", 250)
        self.categories_enabled = set(self.config.get("categories_enabled",
            ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"]))
        # Open the log file BEFORE anything that calls _log() (the table
        # loaders below log their results). _log needs self.log_file.
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now(ET).strftime("%Y%m%d")
        self.log_path = LOG_DIR / ("live_v3_%s.jsonl" % date_str)
        self.log_file = open(self.log_path, "a")

        # v4 deployable tables (loaded once into plain dicts; no hot-path I/O)
        self.entry_table = {}   # (category, regime) -> (placement_min, offset_cents, fill_rate, net_roi_pct)
        self.entry_table_cell = {}  # T58: (category, cell c) -> (placement_min, offset_cents, fill_rate, net_roi_pct)
        self.exit_table = {}    # category -> {cell_id(int) -> (band_x|None, "exit"|"hold")}
        # T58: anchor entry on the live running-mid close-proxy (else BBO mid).
        # #1 ref-price: when this flag is OFF (default), the entry reference is the LAST-TRADED
        # price (A37 honest reference / B17 mid-is-a-lie); ON restores the legacy 30-min-mean +
        # BBO-mid path as a one-line rollback. See _v4_entry_anchor.
        self.running_mid_anchor = self.config.get("premarket_running_mid_anchor", False)
        # #1 ref-price soft-alert: rolling anchor_src over the last 100 placements; warn once when
        # tight_mid (fresh print outside a tight book) exceeds 5%. Telemetry only, no gate.
        self._anchor_src_hist = deque(maxlen=100)
        self._anchor_alert_armed = True
        # T58 entry-fix levers (config-gated; defaults reproduce pre-fix behavior for clean rollback).
        # Lever 2: pull the taker fallback from T-20 to T-1 so the maker rests through the
        # convergence window (catches the period-2 dips). Lever 3 (A): cancel a resting bid only
        # on a degenerate book OR when it goes marketable/stale (target_bid >= best_ask - buffer),
        # NOT on wide-spread-alone — a bid resting safely below a wide book is the intended dip-catcher.
        self.v4_fallback_sec = int(self.config.get("fallback_min_before_start", 20)) * 60
        self.cancel_on_marketable = self.config.get("cancel_on_marketable", False)
        self.cancel_marketable_buffer = int(self.config.get("cancel_marketable_buffer", 1))
        # RUN-7: replace the T-20m taker cross with an ask-1 MAKER clamp (no premium/fee, forfeits
        # the certainty floor). Fires at fallback_min_before_start (set 20 for the T-20->T-15 window).
        # Default False = byte-identical pre-RUN-7 (taker cross).
        self.fallback_maker_clamp = self.config.get("fallback_maker_clamp", False)
        # 3rd cross site: when the INITIAL placement target is already marketable (target_bid >= ask),
        # clamp to ask-1 MAKER and rest (same mechanism as _reprice_target / _fallback_order) instead
        # of crossing taker. Live forensics: 5/6 taker crosses went through here with fillable sell-flow
        # within 0-4c (premature, not firming). round5 force_cross is preserved (still crosses).
        # Default False = byte-identical (taker cross at the ask).
        self.marketable_clamp_placement = self.config.get("marketable_clamp_placement", False)
        # STAGE 1 (maker-only entry): one reversible switch making all three taker-entry sites
        # maker-only. miss_fallback (:3096) -> CANCEL/place-nothing (pure rest-or-no-fill);
        # marketable_taker (:3110) and t20m_fallback (_fallback_order) -> already gated by
        # round5_detector=off and fallback_maker_clamp, belt-coupled to this flag (:3098, :2126)
        # so the gating holds even if those are walked back. Default False = exact pre-flag state.
        self.maker_only_entry = self.config.get("maker_only_entry", False)
        # #0-infra: clean SIGTERM/SIGINT shutdown (gated; default OFF = legacy immediate-terminate on
        # SIGTERM, swallowed SIGINT). ON installs asyncio signal handlers that stop the loop, cancel
        # resting entry bids via the API, and exit within V4_SHUTDOWN_TIMEOUT_SEC. See run() / _shutdown_drain.
        self.graceful_shutdown = self.config.get("graceful_shutdown", False)
        self._shutdown_requested = False
        # PART-2 completion_reprice (Plex-gated; default OFF = byte-identical pre-Part-2).
        # OFF: no window-open tracking, no table load, no new log events, legacy state-file
        # shape -- the completion arm of the sibling handler is unreachable.
        self.completion_reprice = self.config.get("completion_reprice", False)
        self.completion_cells = {}   # (category, leg1 window-open cell) -> X; absent = never attempt
        self._window_open = {}       # ticker -> {price, cell, ts, ttm_min}; tick-loop set at/after T-240
        _r5 = "off" if not self.round5_enabled else "ON(!)"
        _fmc = "on" if self.fallback_maker_clamp else "OFF(!)"
        if self.maker_only_entry:
            print("[BOOT] MAKER_ONLY_ENTRY=true -> miss_fallback CANCEL-no-replace | "
                  "marketable_taker GATED (also round5_detector=%s) | "
                  "t20m_fallback GATED (also fallback_maker_clamp=%s)" % (_r5, _fmc), flush=True)
        else:
            print("[BOOT] MAKER_ONLY_ENTRY=false (taker entry sites live)", flush=True)
        # SAFETY: the BBO-threshold settlement backstop (check_settlements) treats a price touching
        # best_bid>=98 / best_ask<=2 as settlement and cancels the resting exit (settlement_cleanup).
        # But prices round-trip to extremes mid-match -- that is NOT settlement. This falsely pulls
        # live resting exits early (cohort: 4/4 fired 7m-1h52m before real settlement, 1 wrong-dir:
        # MARPAL-PAL exit cancelled, market then settled the OTHER way). Real settlement = exchange
        # truth only (ws_lifecycle / rest_poll). True = disable the BBO heuristic as a settlement
        # source (it never closes a position / cancels an exit). Default False = byte-identical.
        self.disable_bbo_threshold_settlement = self.config.get("disable_bbo_threshold_settlement", False)
        self._load_entry_table()
        self._load_exit_table()
        self._load_staircase()
        # [C-CAP-REMOVAL] operator-ruled 2026-06-12: the T50 paired-basis cap
        # (99) forbade the strategy's structural cost by construction -- the
        # foundation's own economics (combined T-20 taker ~101.9 with positive
        # per-cell expectancy) sit ABOVE it, which is why zero maker pairs ever
        # completed. paired_cap_enforced=False (deploy config) disarms the
        # three pair-arithmetic guards: (1) the entry-placement gate, (2) the
        # T-20 paired_basis_no_fallback cancel, (3) the T50
        # cancel-sibling-on-fill -- and re-keys E1/V3 + the completion bound
        # to the per-leg sanity check (<=99). Per-leg sanity, exit cap, T-15
        # buffer, freshness and degenerate-book guards are UNTOUCHED. Code
        # default True = legacy behavior byte-identical; rollback is one
        # config flip. NAMED RESIDUAL (operator-accepted): both legs filling
        # rich (KESMAR shape) now rides the per-cell exits instead of being
        # cancelled -- bounded ~$0.60/pair worst case at 5-lot.
        self.paired_cap_enforced = bool(self.config.get("paired_cap_enforced", True))
        # [C-CAP-DIFF] reach-repost cap (dormant; default False = byte-identical).
        # When enforced, a resting entry bid is never reposted ABOVE its conception
        # cell (the drift-supported ceiling); holds/down-moves are untouched. Reads
        # the existing set-once _window_open[tk]["cell"] as the conception cell.
        # NOTE coupling: _window_open is populated only when completion_reprice=True;
        # if that is ever off, this cap no-ops (conservative). Activation = config flip.
        self.reach_repost_cap_enforced = bool(self.config.get("reach_repost_cap_enforced", False))
        # [C-RIDE-LIVE override #6, operator-directed 2026-06-12] resting maker
        # ENTRY bids persist into play: the T-15 buffer cancel and the
        # match-live resting sweep EXEMPT them, and a rode-in bid HOLDS in-play
        # (no T-20 fallback re-post, no move-repost -- those are placement
        # decisions, and in-play conception stays forbidden; placement-time
        # gates untouched). Economic cancels (bid_marketable_stale on drift
        # bids, degenerate book, T52) still govern; exits already ride,
        # unchanged. Bounded 5-lot; audit read queued (outcome distribution of
        # premarket bids filling within the first N minutes of play; the
        # bounce surface grades the policy). Code default False = legacy.
        self.premarket_bids_ride_live = bool(self.config.get("premarket_bids_ride_live", False))
        # [C-COPILOT, operator-directed 2026-06-12] the operator trades
        # manually alongside the bot (incl. ITF). Unrecognized resting buys on
        # mapped tickers are HIS: never cancelled, observed and adopted.
        self.operator_manual_mode = bool(self.config.get("operator_manual_mode", False))
        # [C-FV-OBSERVE] same computation as analysis/fv_quote.py riding the
        # v4_place log. Default OFF pending Plex's split countersign -- one
        # codepath, two consumers. Reference only: never a gate.
        self.fv_observe = bool(self.config.get("fv_observe", False))
        # [C-COPILOT] the bot's own order-id registry: every id this process
        # places or restores. An unknown resting order is MANUAL by definition
        # (Plex test 2's attribution source). manual_bids tracks observed
        # foreign resting buys per ticker until fill (adoption) or withdrawal.
        self._bot_order_ids: Set[str] = set()
        self._bot_order_tickers: Set[str] = set()
        self.manual_bids: Dict[str, dict] = {}
        # [C-TRIPWIRE] runtime guard state: first V1-V4 violation self-disables the
        # completion mechanism in-process AND across restarts (incident file). The
        # bot itself keeps trading; only the completion mechanism dies.
        self.completion_disabled = False
        if self.completion_reprice:
            self._load_completion_cells()
            self._completion_arm_check()
        # [C-JOINBID WAVE-1] engagement join-bid for the no-print hole. Default
        # OFF (key absent from deploy_v5_live.json). ON: at a leg's evaluation,
        # when the live rule yields skip_no_trade AND (category, time bucket,
        # best_bid band) is in the 30-cell wave-1 table (C1_join_strict
        # BEATS_SKIP_0p5x rows of engagement_replay_v1, sha b601b5e8...), place
        # a JOIN bid at best_bid through the NORMAL placement machinery
        # end-to-end (paired cap, T52, race-resolve, intended_join, buffer all
        # inherited). Printed legs and ineligible cells are untouched.
        self.engagement_joinbid = bool(self.config.get("engagement_joinbid", False))
        # [C-FEEDER FIX-4] band-gating OFF engagement entry per LESSONS B22
        # (cells are anchored at FILL, not predicted in advance -- gating the
        # placement on the band at evaluation predicts the cell prospectively,
        # which B22 names as the wrong altitude; the 2026-06-12 card: 8
        # one-sided-by-construction pairs incl. PLIVEK). Default False =
        # engagement fires on ANY no-print leg inside the bucket window; only
        # the named economic gates remain (paired cap, T52, T-15 buffer,
        # book-shape). The wave-1 table stays LOADED (ledger attribution +
        # dormant rollback) and the flag restores the gate one-line.
        self.engagement_band_gating = bool(self.config.get("engagement_band_gating", False))
        self.engagement_cells = set()   # (category, bucket, band); attribution always; GATE only when engagement_band_gating
        # [C-JOINBID AMEND] engagement tripwire state (E1-E3; shared fire-once
        # primitive with completion's; incident file blocks re-arm across restarts)
        self.engagement_disabled = False
        if self.engagement_joinbid:
            self._load_engagement_cells()
            self._engagement_arm_check()

        self.books: Dict[str, Book] = {}
        self.subscribed: Set[str] = set()
        self.msg_id = 0
        self.ticker_to_event: Dict[str, str] = {}
        self.event_tickers: Dict[str, Set[str]] = defaultdict(set)
        self.ticker_category: Dict[str, str] = {}
        self.event_open_time: Dict[str, float] = {}   # Kalshi open_time (for unmatched-skip logic)
        self.event_start_time: Dict[str, float] = {}   # scheduled start from TE/ESPN
        # [C-SCHEDULE-TRUST-FIX] provenance of the stored start (source-priority corrections)
        self.event_start_source: Dict[str, str] = {}
        self.event_player_names: Dict[str, List[str]] = {}  # player names per event
        self.event_unmatched_cycles: Dict[str, int] = {}  # discovery cycles without schedule match

        self.positions: Dict[str, Position] = {}
        self.pending_entries: Dict[str, dict] = {}  # ticker -> {event, direction, cat, cell_name, cell_cfg, discovered_ts}
        self.inflight_orders: Set[str] = set()  # tickers with orders being placed (race guard)
        self._event_routing: Set[str] = set()   # events currently being routed (on_bbo_update vs backstop sweep)
        self._mgmt_inflight: Set[str] = set()    # tickers whose v4 resting bid is being managed (serialize callers)
        # [C-P0-RACE] per-order booking guard: serializes the AWAITED tail of
        # _book_v4_entry_fill (exit application / sibling handler) against a
        # concurrent booking attempt for the same order. The check->write segment
        # itself is await-free (see _book_v4_entry_fill); this guard covers the tail.
        self._booking_inflight: Set[str] = set()
        self._bbo_dirty: Set[str] = set()        # tickers with unprocessed BBO change (coalesced; last-value-wins)
        self._bbo_event = None                   # asyncio.Event: recv producer -> worker; created in run()
        self._loop_lag_samples = 0               # loop-lag monitor sample counter
        self._inflight_settlements: Set[str] = set()   # tickers with an in-flight settlement hop (dedup task spawn)
        self._settlement_attempt_ts: Dict[str, float] = {}  # last WS-lifecycle settlement-hop attempt per ticker
        # T51 match-live detection (volume-acceleration): per-ticker rolling
        # trade timestamps + latched live-event set.
        self._trade_times: Dict[str, deque] = defaultdict(deque)
        self._events_live: Set[str] = set()
        # [C-FV-BURST] ticker -> {mid,bid,ask,last,ts} snapshot taken at the real-
        # start latch (observe-only; consumed by _book_v4_entry_fill to tag post-
        # burst fills). Self-pruned by age inside _fv_burst_snapshot.
        self._fv_burst: Dict[str, dict] = {}
        # [C-FV-BURST RE-GATE] events whose observe-only FV snapshot has fired (fire-once)
        self._fv_burst_done: Set[str] = set()
        # [C-FEEDER FIX-1] two-stage latch state + once-per-latch skip logging
        self._live_stage1: Dict[str, float] = {}   # event -> first-burst ts
        self._live_skip_logged: Set[str] = set()   # events whose skip_live_match was logged this latch
        # T58 running-mid anchor: per-ticker rolling (ts, last-traded price) over
        # a 30-min window. Separate from _trade_times (which retains only 600s).
        self._trade_prices: Dict[str, deque] = defaultdict(deque)

        # Persistent processed-tickers set (survives restarts)
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.processed_events: Set[str] = self._load_processed()

        # Schedule loaded after log_file init (below)
        self.schedule: dict = {}

        # Tick logging
        TICK_DIR.mkdir(parents=True, exist_ok=True)
        TRADE_DIR.mkdir(parents=True, exist_ok=True)
        self._tick_files: Dict[str, object] = {}
        self._tick_writers: Dict[str, object] = {}
        self._tick_last_bbo: Dict[str, tuple] = {}  # dedup unchanged ticks
        self._trade_files: Dict[str, object] = {}
        self._trade_writers: Dict[str, object] = {}

        self.n_matches_seen = 0
        self.n_entries = 0
        # [C-JOIN-TRIAL] degraded-deploy abort state (dormant unless join_trial_mode)
        self.join_trial_mode = bool(self.config.get("join_trial_mode", False))
        self.join_trial_aborted = False
        # [C-STAIRCASE SHIP-2 abort-spec] staircase abort state (mirrors join_trial_aborted)
        # [C-STAIRCASE 4CAT] per-cat tally (was scalars): a failing cat can't be masked by a healthy
        # one, and an abort halts ONLY the failing cat. In-memory, resets on restart (unchanged).
        self.staircase_aborted = {}        # cat -> bool
        self.staircase_resolved = {}       # cat -> int
        self.staircase_fills = {}          # cat -> int
        self.staircase_depth_sum = {}      # cat -> float
        self.trial_attempts = 0
        self.trial_resolved = 0
        self.trial_fills = 0
        self.trial_reposts = 0
        self.n_skips = 0
        self.n_exits = 0
        self.n_dcas = 0
        self.n_settlements = 0
        self.start_ts = time.time()

        # log_file already opened above (before the table loaders).
        self._log("system_start", {"mode": "LIVE", "config_path": str(CONFIG_PATH),
                                    "executor": "v4_bid_laying",
                                    "fv_scenarios_enabled": self.fv_scenarios_enabled,
                                    "active_cells": len(self.config.get("active_cells", {})),
                                    "disabled_cells": len(self.config.get("disabled_cells", [])),
                                    "entry_table_rows": len(self.entry_table),
                                    "exit_table_categories": list(self.exit_table.keys()),
                                    "entry_size": self.entry_size,
                                    "exit_size": self.exit_size,
                                    "exit_cap": EXIT_PRICE_CAP})
        self._load_schedule()

        # Paper mode init (spec §2.2)
        if self.config.get("paper_mode", False):
            global _PAPER_API
            _PAPER_API = PaperApi(bot=self)
            self._log("paper_mode_enabled", {
                "config_path": str(CONFIG_PATH),
                "PAPER_MODE_VERSION": "1.0",
                "paper_state_max_age_sec": self.config.get("paper_state_max_age_sec", 86400),
            })

    def _log(self, event, details=None, ticker=""):
        entry = {
            "ts": datetime.now(ET).strftime("%Y-%m-%d %I:%M:%S %p ET"),
            "ts_epoch": time.time(),
            "event": event,
            "ticker": ticker,
            "details": details or {},
        }
        self.log_file.write(json.dumps(entry) + "\n")
        self.log_file.flush()
        print("[%s] %s %s %s" % (
            datetime.now(ET).strftime("%I:%M:%S %p"),
            event.upper().ljust(20),
            ticker[:40] if ticker else "",
            json.dumps(details)[:120] if details else ""
        ), flush=True)

    def _load_processed(self):
        try:
            with open(PROCESSED_FILE) as f:
                return set(json.load(f))
        except (FileNotFoundError, ValueError):
            return set()

    def _save_processed(self):
        with open(PROCESSED_FILE, "w") as f:
            json.dump(sorted(self.processed_events), f)

    @staticmethod
    def _read_schedule_file():
        """Pure-CPU file read + JSON parse (the 2126-event schedule). Touches no
        shared state, so it is safe to run in an executor. Returns (data, err)."""
        try:
            with open(SCHEDULE_FILE) as f:
                return json.load(f), None
        except FileNotFoundError:
            return None, "__missing__"
        except Exception as e:
            return None, str(e)

    def _apply_schedule_data(self, data, err):
        """Apply a parsed schedule onto self (main-thread only)."""
        if err == "__missing__":
            self._log("schedule_missing", {"path": str(SCHEDULE_FILE)})
            self.schedule = {}
            return
        if err is not None:
            self._log("schedule_error", {"error": err})
            self.schedule = {}
            return
        self.schedule = data.get("schedule", {})
        age = time.time() - data.get("fetched_epoch", time.time())
        self._log("schedule_loaded", {
            "count": len(self.schedule),
            "fetched": data.get("fetched_et", "?"),
            "age_min": round(age / 60),
        })

    def _load_schedule(self):
        """Synchronous load -- startup only, before the event loop is running."""
        data, err = self._read_schedule_file()
        self._apply_schedule_data(data, err)

    async def _load_schedule_async(self):
        """FIX 2: offload the schedule file parse to a thread so the json.load
        (2126 events) doesn't block the event loop on the 5-min refresh path.
        The parse touches no shared state; the apply runs back on the loop."""
        loop = asyncio.get_running_loop()
        data, err = await loop.run_in_executor(None, self._read_schedule_file)
        self._apply_schedule_data(data, err)

    @staticmethod
    def _match_event_pure(event_ticker, schedule, player_names):
        """Pure-CPU schedule match (no I/O, no logging, no shared-state mutation)
        -> safe to run in an executor. match_kalshi_event's fuzzy path scans all
        ~2198 schedule entries; a single call can take seconds, so this is the
        block to offload. Returns (result|None, method|None, logs) where logs is
        a list of (event, details) for the caller to emit ON the loop. Logic is
        byte-identical to the prior inline _match_event_to_schedule."""
        from tennis_schedule import match_kalshi_event
        import re as _re
        logs = []
        _dm = _re.search(r"-(\d{2})([A-Z]{3})(\d{2})", event_ticker)
        _month_map = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
                      "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}

        def _date_ok(sched_result):
            """Reject match if start_time date differs from ticker date by >12h."""
            if not _dm:
                return True
            try:
                tk_date = datetime(2000+int(_dm.group(1)), _month_map[_dm.group(2)],
                                   int(_dm.group(3)), 16, 0, tzinfo=timezone.utc)
                sched_dt = datetime.fromisoformat(sched_result.get("start_time","").replace("Z","+00:00"))
                if abs((sched_dt - tk_date).total_seconds()) > 43200:
                    logs.append(("schedule_date_mismatch", {
                        "event": event_ticker,
                        "ticker_date": tk_date.strftime("%Y-%m-%d"),
                        "schedule_date": sched_dt.strftime("%Y-%m-%dT%H:%M"),
                    }))
                    return False
            except Exception:
                pass
            return True

        # Try direct match first
        result = match_kalshi_event(event_ticker, schedule)
        if result and _date_ok(result):
            logs.append(("schedule_match", {
                "event": event_ticker, "method": "direct_6char",
                "start_time": result.get("start_time", "?"),
                "p1": result.get("p1", "?"), "p2": result.get("p2", "?"),
                "category": result.get("category", "?"),
                "kalshi_players": player_names,
            }))
            return result, "direct_6char", logs

        # Try fuzzy with player names
        if player_names:
            result = match_kalshi_event(event_ticker, schedule, kalshi_player_names=player_names)
            if result and _date_ok(result):
                logs.append(("schedule_match", {
                    "event": event_ticker, "method": "fuzzy_name",
                    "start_time": result.get("start_time", "?"),
                    "p1": result.get("p1", "?"), "p2": result.get("p2", "?"),
                    "category": result.get("category", "?"),
                    "kalshi_players": player_names,
                }))
                return result, "fuzzy_name", logs

        # No match — record closest candidate for debugging
        parts = event_ticker.split("-")
        raw = parts[-1] if len(parts) >= 2 else ""
        m = _re.match(r"\d{2}[A-Z]{3}\d{2}(.+)", raw)
        pair_code = m.group(1) if m else raw
        closest = ""
        if pair_code and schedule:
            candidates = sorted(schedule.keys())
            matches = [k for k in candidates if k[:3] == pair_code[:3] or k[3:] == pair_code[3:]]
            closest = ", ".join(matches[:3]) if matches else "(none with shared prefix)"
        logs.append(("schedule_unmatched", {
            "event": event_ticker, "pair_code": pair_code,
            "kalshi_players": player_names,
            "closest_schedule_keys": closest,
            "schedule_size": len(schedule),
        }))
        return None, None, logs

    def _match_event_to_schedule(self, event_ticker):
        """Sync match (startup / non-async callers): pure match + emit logs."""
        player_names = self.event_player_names.get(event_ticker, [])
        result, method, logs = self._match_event_pure(event_ticker, self.schedule, player_names)
        for ev, det in logs:
            self._log(ev, det)
        return result, method

    async def _match_event_to_schedule_async(self, event_ticker):
        """Offload the pure-CPU schedule match (the ~2198-entry fuzzy scan, the
        residual ~10-16s post-reload stall) to a thread so a single multi-second
        match can't block the loop. The GIL releases on the ~5ms switch interval
        during the match, keeping the loop / keepalive serviced. Logging and
        state stay on the loop."""
        player_names = self.event_player_names.get(event_ticker, [])
        loop = asyncio.get_running_loop()
        result, method, logs = await loop.run_in_executor(
            None, self._match_event_pure, event_ticker, self.schedule, player_names)
        for ev, det in logs:
            self._log(ev, det)
        return result, method

    # ------------------------------------------------------------------
    # v4 deployable table loaders (STEP 3) -- run once at init
    # ------------------------------------------------------------------
    def _load_entry_table(self):
        """Load per_regime_offsets_v2.csv into self.entry_table keyed
        (category, anchor_regime) -> (placement_minute, bid_offset_cents,
        expected_fill_rate, expected_net_roi_pct). 36 rows = 4 cat x 9 regime."""
        import csv as _csv
        rel = self.config.get("entry_table_path", "docs/policy/per_regime_offsets_v2.csv")
        path = Path(__file__).resolve().parent / rel
        n = 0
        with open(path, newline="") as f:
            for row in _csv.DictReader(f):
                key = (row["category"].strip(), row["anchor_regime"].strip())
                self.entry_table[key] = (
                    int(float(row["placement_minute"])),
                    int(float(row["bid_offset_cents"])),
                    float(row["expected_fill_rate"]),
                    float(row["expected_net_roi_pct"]),
                )
                n += 1
        self._log("entry_table_loaded", {"rows": n, "path": str(rel)})
        # T58: optional per-cell table (entry_table_percell.csv, 360 rows =
        # 4 cat x 90 cells). Preferred at decision time; regime table is the
        # fallback. Offsets are the cell's regime net-optimal SHALLOW value
        # (T47, NOT a per-cell f x D argmax); per-cell fill-reach attached.
        cell_rel = self.config.get("entry_table_cell_path")
        if cell_rel:
            cpath = Path(__file__).resolve().parent / cell_rel
            m = 0
            with open(cpath, newline="") as f:
                for row in _csv.DictReader(f):
                    key = (row["category"].strip(), int(float(row["c"])))
                    self.entry_table_cell[key] = (
                        int(float(row["placement_minute"])),
                        int(float(row["bid_offset_cents"])),
                        float(row["expected_fill_rate"]),
                        float(row["expected_net_roi_pct"]),
                    )
                    m += 1
            self._log("entry_table_cell_loaded", {"rows": m, "path": str(cell_rel)})

    def _running_mid(self, ticker):
        """T58: trailing-30-min mean of last-traded price for this leg (the
        Stage-2-validated live close-proxy — pure traded microstructure, NOT the
        eventual close). Returns a float in cents, or None when fewer than
        V4_RUNNING_MID_MIN_TRADES prints sit in the window (caller falls back to
        the BBO mid)."""
        pdq = self._trade_prices.get(ticker)
        if not pdq:
            return None
        now = time.time()
        cut = now - V4_RUNNING_MID_WINDOW_SEC
        prices = [p for (ts, p) in pdq if ts >= cut and p > 0]
        if len(prices) < V4_RUNNING_MID_MIN_TRADES:
            return None
        return sum(prices) / float(len(prices))

    def _v4_entry_anchor(self, tk, cat, book, time_to_start):
        """#1 ref-price: resolve the entry REFERENCE price + offset-table row for one leg.
        The reference is the LAST-TRADED price (A37: the real trade is the honest reference;
        B17: on a wide/one-sided book the BBO mid is a phantom midpoint, not a price). Returns
        (ref_price, anchor_src, cell, regime, placement_min, offset, exp_fill, exp_roi,
        target_bid, table_src), or None to skip.

        anchor_src in {last_traded, tight_mid, late_miss}:
          - last_traded : fresh print used directly -- wide book (ask-bid>2) unconditionally;
                          tight book (ask-bid<=2) only when the print sits inside [bid, ask].
                          T50/T52 gate any downstream cross/paired exposure.
          - tight_mid   : tight book with a fresh print OUTSIDE the book -> fall back to the BBO mid.
          - late_miss   : no fresh print, inside T-20m, taker enabled -> return current_ask so the
                          downstream miss_fallback crosses at the ask. INERT under Stage 1
                          (the maker_only_entry guard keeps this branch off, so the enum never
                          fires today) -- a no-op until taker is restored.
        No fresh print (age > V4_LAST_TRADE_MAX_AGE_SEC or absent) and not the late_miss case
        -> None: caller logs skip_no_trade; the event stays unprocessed and retries next tick.
        There is NO general BBO-mid fallback on a stale book by design.

        ROLLBACK: running_mid_anchor=True restores the legacy 30-min-mean + BBO-mid path
        (anchor_src running_mid / bbo_mid_fallback). Default OFF; one-line config rollback."""
        bbo_mid = (book.best_bid + book.best_ask) / 2.0
        if self.running_mid_anchor:
            # --- ROLLBACK: legacy running-mid (trailing 30-min trade mean) + BBO-mid fallback ---
            rmid = self._running_mid(tk)
            if rmid is not None and rmid > 0:
                anchor_price, anchor_src = int(round(rmid)), "running_mid"
            else:
                anchor_price, anchor_src = int(round(bbo_mid)), "bbo_mid_fallback"
        else:
            # --- DEFAULT: last-traded reference ---
            lt = book.last_trade_price
            lt_age = (time.time() - book.last_trade_ts) if book.last_trade_ts else float("inf")
            if lt > 0 and lt_age <= V4_LAST_TRADE_MAX_AGE_SEC:
                if (book.best_ask - book.best_bid) <= 2:
                    # tight book: trust the print only if it sits inside the book; else the mid
                    if book.best_bid <= lt <= book.best_ask:
                        anchor_price, anchor_src = int(round(lt)), "last_traded"
                    else:
                        anchor_price, anchor_src = int(round(bbo_mid)), "tight_mid"
                else:
                    # wide book (B17): the mid is a phantom midpoint -> use the print unconditionally
                    anchor_price, anchor_src = int(round(lt)), "last_traded"
            elif not self.maker_only_entry and time_to_start <= V4_T20M_SEC:
                # late_miss carve-out (Plex-gated): no fresh print inside T-20m with taker enabled ->
                # return the ask so the existing miss_fallback path crosses. INERT under Stage 1 --
                # the maker_only_entry guard above keeps this off, so the enum never fires today.
                anchor_price, anchor_src = book.best_ask, "late_miss"
            else:
                # no fresh print -> skip (no BBO-mid fallback by design). Caller logs skip_no_trade.
                return None
        cell = self.cell_lookup(cat, anchor_price)
        regime = self.regime_lookup(cat, anchor_price)
        row, table_src = None, None
        if self.entry_table_cell:
            row = self.entry_table_cell.get((cat, cell))
            if row is not None:
                table_src = "per_cell"
        if row is None:
            row = self.entry_table.get((cat, regime))
            if row is not None:
                table_src = "regime"
        if row is None:
            return None
        placement_min, offset, exp_fill, exp_roi = row
        target_bid = max(1, anchor_price - offset)
        return (anchor_price, anchor_src, cell, regime, placement_min, offset,
                exp_fill, exp_roi, target_bid, table_src)

    def _load_exit_table(self):
        """Load the 4 {category}_adaptive_exit_bands.parquet into
        self.exit_table[category] = {cell_id -> (band_x|None, "exit"|"hold")}.
        Each band's [price_low, price_high] is expanded to its constituent 1c
        cell_ids; band_exit_X == "HOLD" -> ("hold", band_x=None), else
        ("exit", band_x=int). pyarrow read happens here only; the hot path
        reads the cached dict."""
        import pyarrow.parquet as _pq
        rel_dir = self.config.get("exit_table_dir", "data/durable/spike_volatility_map/")
        base = Path(__file__).resolve().parent / rel_dir
        loaded = {}
        for cat in ("ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"):
            fp = base / ("%s_adaptive_exit_bands.parquet" % cat.lower())
            tbl = _pq.read_table(fp).to_pandas()
            cell_map = {}
            n_hold = 0
            for _, r in tbl.iterrows():
                lo, hi = int(r["price_low"]), int(r["price_high"])
                raw = str(r["band_exit_X"]).strip()
                if raw.upper() == "HOLD":
                    rule, band_x = "hold", None
                    n_hold += (hi - lo + 1)
                else:
                    rule, band_x = "exit", int(round(float(raw)))
                for cid in range(lo, hi + 1):
                    cell_map[cid] = (band_x, rule)
            loaded[cat] = cell_map
            self._log("exit_table_loaded", {
                "category": cat, "bands": len(tbl),
                "cells_mapped": len(cell_map), "hold_cells": n_hold,
            })
        self.exit_table = loaded

    def _load_completion_cells(self):
        """PART-2: load docs/policy/completion_cells_v1.csv into
        self.completion_cells[(category, cell)] = X. SHIP_FIRST eligibility from the
        1944b250 tape replay (parquet sha 7883f5c8...); one X per cell (per-cell argmax
        blended_lift_pp_0p5x, tie -> smallest X). Absent cell = never attempt. Called
        only when completion_reprice=true; a missing file fails the boot loudly (no
        silent flag-on-without-table)."""
        import csv as _csv
        rel = self.config.get("completion_cells_path", "docs/policy/completion_cells_v1.csv")
        path = Path(__file__).resolve().parent / rel
        n = 0
        sha = ""
        with open(path, newline="") as f:
            for row in _csv.DictReader(f):
                key = (row["category"].strip(), int(float(row["cell"])))
                self.completion_cells[key] = int(float(row["X"]))
                sha = row.get("provenance_sha", "")
                n += 1
        self._log("completion_cells_loaded", {"rows": n, "path": str(rel),
                                              "provenance_sha": sha[:16]})

    def _load_engagement_cells(self):
        """[C-JOINBID WAVE-1] load docs/policy/engagement_cells_v1.csv into
        self.engagement_cells = {(category, bucket, band)}. The 30 strict-cleared
        rows (C1_join_strict x BEATS_SKIP_0p5x) of engagement_replay_v1.parquet
        (sha b601b5e8...). Absent row = skip stands. Called only when
        engagement_joinbid=true; a missing file fails the boot loudly."""
        import csv as _csv
        rel = self.config.get("engagement_cells_path", "docs/policy/engagement_cells_v1.csv")
        path = Path(__file__).resolve().parent / rel
        n = 0
        sha = ""
        with open(path, newline="") as f:
            for row in _csv.DictReader(f):
                self.engagement_cells.add((row["category"].strip(),
                                           row["bucket"].strip(), row["band"].strip()))
                sha = row.get("provenance_sha", "")
                n += 1
        self._log("engagement_cells_loaded", {"rows": n, "path": str(rel),
                                              "provenance_sha": sha[:16]})

    def _engagement_bucket(self, tts_sec):
        """[C-JOINBID] replay time-bucket of an evaluation moment. (240,60] min ->
        T240_T60; (60,15] -> T60_T15; outside -> None (no engagement)."""
        if 3600.0 < tts_sec <= 14400.0: return "T240_T60"
        if 900.0 < tts_sec <= 3600.0: return "T60_T15"
        return None

    def _engagement_join_eligible(self, cat, book, time_to_start):
        """[C-JOINBID WAVE-1] pure eligibility: returns the join level (best_bid,
        int cents) or None. None when: flag off; no/locked/degenerate book (a
        join NEEDS a strict bid<ask level to rest at -- locked books place via
        the normal anchor path only); outside the replay buckets.

        [C-FEEDER FIX-4] the wave-1 band check is now GATED behind
        engagement_band_gating (default OFF, per LESSONS B22: cells are
        anchored at fill, not predicted in advance -- the band at evaluation
        is not the band at fill, and gating on it built the
        one-sided-by-construction class). The bucket window stays: it is the
        structural premarket envelope ((15,240] min), not a band prediction.
        The economic gates (paired cap, T52, T-15 buffer) live downstream in
        the normal machinery, unchanged."""
        if not self.engagement_joinbid or self.engagement_disabled:
            return None
        b, a = book.best_bid, book.best_ask
        if not (1 <= b < a <= 99):
            return None
        bucket = self._engagement_bucket(time_to_start)
        if bucket is None:
            return None
        lvl = int(round(b))
        if (self.engagement_band_gating
                and (cat, bucket, self.regime_lookup(cat, lvl)) not in self.engagement_cells):
            return None
        return lvl

    def _completion_arm_check(self):
        """[C-TRIPWIRE] boot arm/block. An incident file from a prior tripwire fire
        keeps the completion mechanism DISABLED across restarts until the operator
        removes the file by hand. Indeterminate state (unreadable fs) fails CLOSED."""
        try:
            if COMPLETION_INCIDENT_FILE.exists():
                self.completion_disabled = True
                try:
                    with open(COMPLETION_INCIDENT_FILE) as f:
                        payload = json.load(f)
                except Exception:
                    payload = {"unreadable": True}
                self._log("completion_incident_block", {
                    "file": str(COMPLETION_INCIDENT_FILE), "incident": payload})
                print("[BOOT] completion_reprice=ON but INCIDENT FILE present -> "
                      "mechanism DISABLED (remove %s by hand to re-arm)"
                      % COMPLETION_INCIDENT_FILE, flush=True)
            else:
                self._log("completion_tripwire_armed", {
                    "violations": "V1 post_only breach, V2 is_taker completion fill, "
                                  "V3 cap breach, V4 cell not in table"})
                print("[BOOT] completion_reprice=ON -> tripwire ARMED (V1-V4), "
                      "no incident file", flush=True)
        except Exception as e:
            self.completion_disabled = True
            self._log("completion_incident_check_error", {"error": str(e)})

    async def _mechanism_tripwire(self, kind, violation, context, tk=""):
        """[C-JOINBID AMEND] THE fire-once tripwire primitive, shared by the
        completion and engagement mechanisms (Plex amendment: one primitive, no
        parallel implementations): (a) self-disable in-process, (b) cancel-only
        sweep of the MECHANISM'S resting bids (race-resolved, never deleted
        unbooked -- [C-P0-RACE site 5]), (c) atomic incident-file persistence
        (blocks re-arm across restarts; arm checks fail CLOSED), (d) log with
        full context, (e) the BOT keeps trading normally."""
        if kind == "completion":
            if self.completion_disabled:
                return
            self.completion_disabled = True
            inc_file = COMPLETION_INCIDENT_FILE
            def is_mine(p): return p.entry_mode == "completion_reprice"
        else:
            if self.engagement_disabled:
                return
            self.engagement_disabled = True
            inc_file = ENGAGEMENT_INCIDENT_FILE
            def is_mine(p): return p.play_type == "v4_engagement_join"
        payload = {"violation": violation, "context": context, "ticker": tk,
                   "ts_epoch": time.time(),
                   "ts_et": datetime.now(ET).strftime("%Y-%m-%d %I:%M:%S %p ET")}
        try:
            tmp = str(inc_file) + ".tmp"
            with open(tmp, "w") as f:
                json.dump(payload, f, indent=1)
            os.replace(tmp, str(inc_file))
        except Exception as e:
            self._log("%s_incident_write_error" % kind, {"error": str(e)})
        self._log("%s_tripwire_fired" % kind, payload, ticker=tk)
        for tk2, pos in list(self.positions.items()):
            if (pos.is_v4 and pos.phase == "entry_resting"
                    and pos.entry_order_id and is_mine(pos)):
                res = await self._cancel_entry_and_resolve(
                    tk2, pos, "%s_tripwire" % kind, "tripwire_cancel_race")
                if res == "cancelled":
                    if kind == "completion":
                        self._log("completion_reverted", {"event": pos.event_ticker,
                            "reason": "tripwire", "s1": pos.entry_price,
                            "s0": pos.completion_s0}, ticker=tk2)
                    else:
                        self._log("engagement_reverted", {"event": pos.event_ticker,
                            "reason": "tripwire", "bid": pos.entry_price}, ticker=tk2)
                    pos.entry_order_id = ""
                    self._untombstone_entry(tk2, pos)
        self._save_v4_resting()

    async def _completion_tripwire(self, violation, context, tk=""):
        """[C-TRIPWIRE] delegates to the shared fire-once primitive (event names,
        payload shape, incident path, sweep semantics unchanged)."""
        await self._mechanism_tripwire("completion", violation, context, tk=tk)

    async def _engagement_tripwire(self, violation, context, tk=""):
        """[C-JOINBID AMEND] engagement arm of the shared primitive."""
        await self._mechanism_tripwire("engagement", violation, context, tk=tk)

    def _engagement_place_guards(self, tk, et, cat, pos, time_to_start):
        """[C-JOINBID AMEND] the three Plex tripwire conditions, checked at the
        engagement placement (same time_to_start value the eligibility check
        used -- no boundary drift). Returns (violation, context) or None:
          E1 paired-cap bypass: the placed bid fails _paired_basis_ok NOW;
          E2 off-table: (category, bucket, band) not in the 30-row table;
          E3 missing intended_join on an engagement placement."""
        # [C-CAP-REMOVAL] E1 re-keys with the gate it guards: cap enforced ->
        # pair arithmetic (unchanged); cap dormant -> the per-leg sanity bound
        # (1..99) is the live placement constraint, so THAT is what a bypass
        # means (tripwire follows the gate, the FIX-4/E2 principle).
        if getattr(self, "paired_cap_enforced", True):
            if not self._paired_basis_ok(tk, et, pos.entry_price):
                return ("E1_paired_cap_bypass",
                        {"event": et, "entry_price": pos.entry_price})
        elif not (1 <= pos.entry_price <= 99):
            return ("E1_per_leg_sanity_breach",
                    {"event": et, "entry_price": pos.entry_price})
        # [C-FEEDER FIX-4] E2 is the BAND-GATE's tripwire; with band gating off
        # (B22: cells anchor at fill) off-table placements are by-design, so E2
        # is checked only when the gate is live. The bucket-window condition
        # stays armed either way (a placement outside (15,240] is a machinery
        # regression, not a band call).
        bucket = self._engagement_bucket(time_to_start)
        if bucket is None:
            return ("E2_cell_off_table",
                    {"event": et, "cat": cat, "bucket": None,
                     "band": self.regime_lookup(cat, pos.entry_price)})
        if (self.engagement_band_gating and (cat, bucket,
                self.regime_lookup(cat, pos.entry_price)) not in self.engagement_cells):
            return ("E2_cell_off_table",
                    {"event": et, "cat": cat, "bucket": bucket,
                     "band": self.regime_lookup(cat, pos.entry_price)})
        if pos.intended_join is not True:
            return ("E3_missing_intended_join", {"event": et})
        return None

    def _engagement_arm_check(self):
        """[C-JOINBID AMEND] boot arm/block, completion discipline verbatim: an
        incident file keeps the engagement mechanism DISABLED across restarts
        until removed by hand; indeterminate state fails CLOSED."""
        try:
            if ENGAGEMENT_INCIDENT_FILE.exists():
                self.engagement_disabled = True
                try:
                    with open(ENGAGEMENT_INCIDENT_FILE) as f:
                        payload = json.load(f)
                except Exception:
                    payload = {"unreadable": True}
                self._log("engagement_incident_block", {
                    "file": str(ENGAGEMENT_INCIDENT_FILE), "incident": payload})
                print("[BOOT] engagement_joinbid=ON but INCIDENT FILE present -> "
                      "mechanism DISABLED (remove %s by hand to re-arm)"
                      % ENGAGEMENT_INCIDENT_FILE, flush=True)
            else:
                gating = bool(getattr(self, "engagement_band_gating", False))
                self._log("engagement_tripwire_armed", {
                    "conditions": "E1 paired-cap bypass, E2 cell off-table%s, "
                                  "E3 missing intended_join"
                                  % ("" if gating else " (bucket-window only; band gating OFF)"),
                    "band_gating": gating})
                print("[BOOT] engagement_joinbid=ON -> tripwire ARMED (E1-E3), "
                      "no incident file; band gating %s"
                      % ("ON" if gating else "OFF (B22: cells anchor at fill)"), flush=True)
        except Exception as e:
            self.engagement_disabled = True
            self._log("engagement_incident_check_error", {"error": str(e)})

    def _completion_fill_guards(self, pos, fill_price, is_taker):
        """[C-TRIPWIRE] V2/V3/V4 checks at the completion-fill booking site. Returns
        (violation, context) or None. V2 fires only on affirmative is_taker=True
        (a failed /fills lookup returns None and does NOT fire -- transient API
        errors must not kill the mechanism). Pure/testable."""
        if is_taker is True:
            return ("V2_is_taker_completion_fill",
                    {"fill_price": fill_price, "is_taker": True,
                     "s1_posted": pos.entry_price})
        # [C-CAP-REMOVAL] V3 re-keys with the gate it guards (E1 discipline):
        # cap enforced -> pair arithmetic (unchanged); cap dormant ->
        # over-cap completion fills are BY DESIGN, so V3 guards the per-leg
        # sanity bound instead.
        if getattr(self, "paired_cap_enforced", True):
            if pos.completion_leg1_basis + fill_price > V4_PAIRED_BASIS_CAP:
                return ("V3_cap_breach",
                        {"leg1_basis": pos.completion_leg1_basis, "fill_price": fill_price,
                         "combined": pos.completion_leg1_basis + fill_price,
                         "cap": V4_PAIRED_BASIS_CAP})
        elif not (1 <= fill_price <= 99):
            return ("V3_per_leg_sanity_breach",
                    {"leg1_basis": pos.completion_leg1_basis,
                     "fill_price": fill_price})
        if (pos.category, pos.completion_lookup_cell) not in self.completion_cells:
            return ("V4_cell_not_in_table",
                    {"category": pos.category, "cell": pos.completion_lookup_cell,
                     "table_cells": len(self.completion_cells)})
        return None

    def _maybe_set_window_open(self, tk, now):
        """PART-2 item 2: latch the leg's WINDOW-OPEN reference -- the first
        time-t-available last-trade reference computed at-or-after T-240 (last-trade
        discipline; NEVER the BBO mid; NEVER at placement time). Set-once per leg by the
        tick loop (apply_trade on each print + the 60s routing sweep for the T-240
        boundary crossing with an already-fresh print). A leg whose first fresh print
        only exists pre-T-240 stays unset -> leg-1 fills there make NO completion
        attempt (designed conservative edge). Flag-gated: completion_reprice=false is a
        single boolean check (byte-identical behavior)."""
        if not self.completion_reprice or self.completion_disabled:
            return
        if tk in self._window_open:
            return
        et = self.ticker_to_event.get(tk)
        if not et:
            return
        st = self.event_start_time.get(et)
        if not st:
            return
        tts = st - now
        if tts <= 0 or tts > V4_MAX_PLACEMENT_SEC:
            return
        book = self.books.get(tk)
        if not book:
            return
        lt = book.last_trade_price
        lt_age = (now - book.last_trade_ts) if book.last_trade_ts else float("inf")
        if lt <= 0 or lt_age > V4_LAST_TRADE_MAX_AGE_SEC:
            return
        price = int(round(lt))
        cell = min(94, max(5, price))
        self._window_open[tk] = {"price": price, "cell": cell, "ts": now,
                                 "ttm_min": round(tts / 60.0, 1)}
        self._log("window_open_set", {"event": et, "price": price, "cell": cell,
            "last_trade_age_sec": round(lt_age, 1),
            "ttm_min": round(tts / 60.0, 1)}, ticker=tk)
        # lifecycle (c): persist immediately -- a crash between here and the next
        # resting-bid save must not lose the frame (leak-proofing).
        self._save_v4_resting()

    def exit_rule_for(self, category, price_cents):
        """v4 exit lookup: returns (band_x|None, rule) for the 1c cell of
        price_cents. rule in {"exit","hold"}. Falls back to ("exit", default)
        if the category/cell is somehow absent (never expected for the 4
        enabled categories).

        [C-COPILOT ITF] ITF_M/ITF_W BORROW the Challenger exit surface at the
        fill cent (lookup-only translation; the position keeps its ITF
        category, so ledger/cell attribution never pollutes native CHALL)."""
        category = ITF_EXIT_BORROW.get(category, category)
        cid = self.cell_lookup(category, price_cents)
        cmap = self.exit_table.get(category)
        if cmap and cid in cmap:
            return cmap[cid]
        return (15, "exit")  # defensive default; logged by caller if hit

    def get_category(self, ticker):
        for cat_name, prefixes in SERIES_MAP.items():
            for prefix in prefixes:
                if ticker.startswith(prefix):
                    return cat_name
        return None

    def cell_lookup(self, category, current_kalshi_price_cents):
        """v4 direction-free 1c cell classification from the current Kalshi
        yes-price. Returns an int cell_id in [5, 94] (the exit-band table's
        domain). No direction, no 5c bucket -- the exit band table is keyed on
        the 1c cell of the *current* price (entry-priced cell at exit lookup)."""
        cell_id = int(round(current_kalshi_price_cents))
        if cell_id < 5:
            cell_id = 5
        if cell_id > 94:
            cell_id = 94
        return cell_id

    def regime_lookup(self, category, current_kalshi_price_cents):
        """Map the current Kalshi yes-price to its 10c regime band for the v4
        entry-offset table (per_regime_offsets_v2.csv). Band low boundaries:
        5,15,25,...,85 -> r05_14 ... r85_94."""
        p = current_kalshi_price_cents
        if p < 15: return "r05_14"
        if p < 25: return "r15_24"
        if p < 35: return "r25_34"
        if p < 45: return "r35_44"
        if p < 55: return "r45_54"
        if p < 65: return "r55_64"
        if p < 75: return "r65_74"
        if p < 85: return "r75_84"
        return "r85_94"

    def _legacy_cell_lookup(self, category, direction, entry_mid):
        """LEGACY FV-anchor cell lookup (5c bucket + direction). Used only by the
        FV-scenario routing path, which v4 gates off by default
        (config fv_anchor_scenarios_enabled). Retained for emergency rollback."""
        bucket = int(entry_mid / 5) * 5
        cell_name = "%s_%s_%d-%d" % (category, direction, bucket, bucket + 4)
        active = self.config.get("active_cells", {})
        if cell_name in self.config.get("disabled_cells", []):
            return cell_name, None
        if cell_name in active:
            return cell_name, active[cell_name]
        return cell_name, None

    def _extract_depth(self, book, side="bid", levels=5):
        """Extract top N price levels with sizes. Returns list of (price, size) tuples."""
        if side == "bid":
            items = sorted(book.bids.items(), reverse=True)[:levels]
        else:
            items = sorted(book.asks.items())[:levels]
        result = list(items)
        while len(result) < levels:
            result.append(("", ""))
        return result

    def _depth_signature(self, book):
        """Hashable snapshot of top-5 depth on both sides for dedup."""
        bids = tuple(sorted(book.bids.items(), reverse=True)[:5])
        asks = tuple(sorted(book.asks.items())[:5])
        return (bids, asks)

    def _log_tick(self, ticker, book):
        """Write depth tick to per-ticker CSV. Dedup on top-5 depth change."""
        bid, ask = book.best_bid, book.best_ask
        if bid <= 0 or ask >= 100:
            return
        sig = self._depth_signature(book)
        last = self._tick_last_bbo.get(ticker)
        if last and last == sig:
            return
        self._tick_last_bbo[ticker] = sig
        mid = (bid + ask) / 2.0

        bid_levels = self._extract_depth(book, "bid")
        ask_levels = self._extract_depth(book, "ask")

        if ticker not in self._tick_writers:
            import csv as _csv
            path = TICK_DIR / ("%s.csv" % ticker)
            is_new = not path.exists() or path.stat().st_size == 0
            fh = open(path, "a", newline="")
            w = _csv.writer(fh)
            if is_new:
                header = ["ts_et", "ticker"]
                for i in range(1, 6):
                    header += ["bid_%d" % i, "bid_%d_sz" % i]
                for i in range(1, 6):
                    header += ["ask_%d" % i, "ask_%d_sz" % i]
                header += ["mid", "bid_depth_5", "ask_depth_5", "depth_ratio", "last_trade"]
                w.writerow(header)
                fh.flush()
            self._tick_files[ticker] = fh
            self._tick_writers[ticker] = w

        ts_str = datetime.now(ET).strftime("%Y-%m-%d %I:%M:%S %p")
        row = [ts_str, ticker]
        total_bid_sz = 0
        total_ask_sz = 0
        for price, size in bid_levels:
            row += [price, size]
            if isinstance(size, (int, float)) and size > 0:
                total_bid_sz += size
        for price, size in ask_levels:
            row += [price, size]
            if isinstance(size, (int, float)) and size > 0:
                total_ask_sz += size
        total = total_bid_sz + total_ask_sz
        depth_ratio = total_bid_sz / total if total > 0 else 0.5
        row += ["%.1f" % mid, total_bid_sz, total_ask_sz, "%.3f" % depth_ratio, book.last_trade_price]
        self._tick_writers[ticker].writerow(row)
        self._tick_files[ticker].flush()

    def apply_trade(self, ticker, msg):
        """Process a trade event from WebSocket."""
        if ticker not in self.books:
            self.books[ticker] = Book()
        book = self.books[ticker]
        price_raw = msg.get("yes_price", msg.get("yes_price_dollars", 0))
        if isinstance(price_raw, str):
            price_raw = float(price_raw)
        price = round(price_raw * 100) if price_raw < 2 else int(price_raw)
        count = msg.get("count", msg.get("count_fp", 0))
        if isinstance(count, str):
            count = int(float(count))
        side = msg.get("taker_side", "?")
        book.last_trade_price = price
        book.last_trade_ts = time.time()
        book.last_trade_side = side
        # T51: feed the volume-acceleration live detector (per-ticker trade times).
        dq = self._trade_times[ticker]
        dq.append(book.last_trade_ts)
        cutoff = book.last_trade_ts - LIVE_TRADE_RETENTION_SEC
        while dq and dq[0] < cutoff:
            dq.popleft()
        # T58: feed the running-mid buffer (ts, price) over the 30-min window.
        pdq = self._trade_prices[ticker]
        pdq.append((book.last_trade_ts, price))
        pcut = book.last_trade_ts - V4_RUNNING_MID_WINDOW_SEC
        while pdq and pdq[0][0] < pcut:
            pdq.popleft()
        # PART-2: a fresh print inside the T-240 window may be the leg's first
        # time-t-available window-open reference (flag-gated no-op when off).
        self._maybe_set_window_open(ticker, book.last_trade_ts)
        if _PAPER_API is not None:
            _PAPER_API.on_trade(ticker, book.last_trade_ts, price, count, side)
        self._log_trade(ticker, price, count, side)

    def _log_trade(self, ticker, price, count, taker_side):
        """Write trade to per-ticker CSV."""
        if ticker not in self._trade_writers:
            import csv as _csv
            path = TRADE_DIR / ("%s.csv" % ticker)
            is_new = not path.exists() or path.stat().st_size == 0
            fh = open(path, "a", newline="")
            w = _csv.writer(fh)
            if is_new:
                w.writerow(["ts_et", "ticker", "price", "count", "taker_side"])
                fh.flush()
            self._trade_files[ticker] = fh
            self._trade_writers[ticker] = w
        ts_str = datetime.now(ET).strftime("%Y-%m-%d %I:%M:%S %p")
        self._trade_writers[ticker].writerow([ts_str, ticker, price, count, taker_side])
        self._trade_files[ticker].flush()

    # ------------------------------------------------------------------
    # Order placement — REAL Kalshi API calls
    # ------------------------------------------------------------------
    async def place_order(self, ticker, action, side, price, count, post_only=True):
        """Place a real order on Kalshi. Returns (order_id, response_dict) or ("", error_dict)."""
        # Position accumulation guard: cap total buy exposure per ticker
        if action == "buy":
            target_max = self.config["sizing"]["entry_contracts"]
            existing_pos = self.positions.get(ticker)
            current_qty = existing_pos.entry_qty if existing_pos and existing_pos.phase == "active" else 0
            if current_qty >= target_max:
                self._log("buy_blocked_position_full", {
                    "current_qty": current_qty, "target_max": target_max,
                    "attempted_count": count, "price": price,
                }, ticker=ticker)
                return "", {"_error": "position_full"}
            if current_qty + count > target_max:
                count = target_max - current_qty
                self._log("buy_qty_reduced", {
                    "current_qty": current_qty, "reduced_to": count,
                    "target_max": target_max, "price": price,
                }, ticker=ticker)

        coid = str(uuid.uuid4())
        path = ORDER_CREATE_V2_PATH                      # [C-ORDER-V2] /portfolio/events/orders
        payload = build_order_payload_v2(ticker, action, price, count, post_only, coid)
        resp = await api_post(self.session, self.ak, self.pk, path, payload, self.rl)
        if resp and not resp.get("_error"):
            oid, _v2_status, _v2_fill, _v2_avg = parse_order_response_v2(resp)   # [C-ORDER-V2] flat
            # [C-COPILOT] register: this id/ticker is the BOT's
            if oid:
                getattr(self, "_bot_order_ids", set()).add(oid)
                getattr(self, "_bot_order_tickers", set()).add(ticker)
            self._log("order_placed", {
                "action": action, "side": side, "price": price, "count": count,
                "order_id": oid, "client_order_id": coid,
                "response_status": _v2_status,
            }, ticker=ticker)
            return oid, resp
        else:
            self._log("order_error", {
                "action": action, "side": side, "price": price, "count": count,
                "error_status": resp.get("_status") if resp else "null",
                "error_body": resp.get("_body", "")[:300] if resp else "null response",
            }, ticker=ticker)
            return "", resp

    async def cancel_order(self, ticker, order_id, label=""):
        """Cancel a resting order. Returns True on success."""
        if not order_id:
            return False
        path = "/trade-api/v2/portfolio/orders/%s" % order_id
        ok = await api_delete(self.session, self.ak, self.pk, path, self.rl)
        self._log("order_cancelled", {
            "order_id": order_id, "label": label, "success": ok,
        }, ticker=ticker)
        return ok

    # ------------------------------------------------------------------
    # WebSocket (identical to paper_v3)
    # ------------------------------------------------------------------
    async def ws_connect(self):
        ts = str(int(time.time() * 1000))
        headers = {"KALSHI-ACCESS-KEY": self.ak,
                    "KALSHI-ACCESS-SIGNATURE": sign_request(self.pk, ts, "GET", WS_PATH),
                    "KALSHI-ACCESS-TIMESTAMP": ts}
        try:
            import websockets
            self.ws = await websockets.connect(WS_URL, additional_headers=headers,
                ping_interval=WS_PING_INTERVAL, ping_timeout=10, max_size=10_000_000)
            self.ws_connected = True
            self._log("ws_connected")
            return True
        except Exception as e:
            self._log("ws_connect_failed", {"error": str(e)})
            self.ws_connected = False
            return False

    async def ws_subscribe(self, tickers):
        if not self.ws_connected or not self.ws:
            return
        new = [t for t in tickers if t not in self.subscribed]
        if not new:
            return
        for i in range(0, len(new), WS_SUBSCRIBE_BATCH):
            batch = new[i:i + WS_SUBSCRIBE_BATCH]
            self.msg_id += 1
            try:
                await self.ws.send(json.dumps({"id": self.msg_id, "cmd": "subscribe",
                    "params": {"channels": ["orderbook_delta", "trade", "market_lifecycle_v2"], "market_tickers": batch}}))
                self.subscribed.update(batch)
                await asyncio.sleep(0.05)
            except Exception as e:
                self._log("ws_subscribe_error", {"error": str(e)})
        self._log("ws_subscribed", {"new": len(new), "total": len(self.subscribed)})

    def apply_snapshot(self, ticker, msg):
        book = Book()
        for level in msg.get("yes_dollars_fp", msg.get("yes", [])):
            if isinstance(level, list) and len(level) >= 2:
                price, size = round(float(level[0]) * 100), int(float(level[1]))
                if size > 0:
                    book.bids[price] = size
        for level in msg.get("no_dollars_fp", msg.get("no", [])):
            if isinstance(level, list) and len(level) >= 2:
                no_price, size = round(float(level[0]) * 100), int(float(level[1]))
                if size > 0:
                    book.asks[100 - no_price] = size
        recalc_bbo(book)
        book.updated = time.time()
        self.books[ticker] = book
        self._log_tick(ticker, book)
        if _PAPER_API is not None:
            _PAPER_API.on_book_update(ticker)

    def apply_delta(self, ticker, msg):
        if ticker not in self.books:
            self.books[ticker] = Book()
        book = self.books[ticker]
        price_raw = msg.get("price_dollars", msg.get("price"))
        delta = msg.get("delta_fp", msg.get("delta", 0))
        side = msg.get("side", "yes").lower()
        if price_raw is None:
            return
        price = round(float(price_raw) * 100)
        if side == "yes":
            book.bids[price] = book.bids.get(price, 0) + int(float(delta))
            if book.bids[price] <= 0:
                book.bids.pop(price, None)
        else:
            ap = 100 - price
            book.asks[ap] = book.asks.get(ap, 0) + int(float(delta))
            if book.asks[ap] <= 0:
                book.asks.pop(ap, None)
        recalc_bbo(book)
        book.updated = time.time()
        self._log_tick(ticker, book)
        if _PAPER_API is not None:
            _PAPER_API.on_book_update(ticker)

    async def _ws_reconnect(self):
        """Reconnect WebSocket with exponential backoff. Never gives up."""
        delays = [5, 10, 30, 60]
        attempt = 0
        while True:
            delay = delays[min(attempt, len(delays) - 1)]
            self._log("ws_reconnecting", {"attempt": attempt + 1, "delay_sec": delay})
            await asyncio.sleep(delay)
            if await self.ws_connect():
                if self.subscribed:
                    old = list(self.subscribed)
                    self.subscribed.clear()
                    await self.ws_subscribe(old)
                self._log("ws_reconnected", {"attempt": attempt + 1})
                return
            attempt += 1

    async def ws_reader(self):
        """PRODUCER: read frames and ingest them with O(1) NON-BLOCKING work
        only (no bounded queue, no blocking put). The recv await yields to the
        loop -- and thus the websockets keepalive -- on every frame.

        The 0a2f4eb regression: a bounded Queue(maxsize=5000) with blocking
        put() saturated at qdepth=4999 during a resubscribe snapshot flood, so
        ws_reader's await put() blocked, recv stopped, the library couldn't
        process pong/control frames, the keepalive timed out (1011), reconnect,
        flood again. All loop spikes occurred exactly at qdepth=4999.

        Fix: BBO state is last-value-wins, not a stream of independent events.
        _ingest_ws_frame applies book/trade state synchronously in-order (fast;
        deltas are increments that CANNOT be coalesced) and flags BBO-changed
        tickers into a per-ticker dirty set. The expensive part -- on_bbo_update
        routing (paper api calls that don't yield) -- is deferred to _ws_worker,
        coalesced to AT MOST one route per ticker per drain."""
        while True:
            try:
                if not self.ws_connected or not self.ws:
                    await self._ws_reconnect()
                    continue
                raw = await asyncio.wait_for(self.ws.recv(), timeout=30)
                self._ingest_ws_frame(raw)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self._log("ws_error", {"error": str(e)})
                self.ws_connected = False
                await self._ws_reconnect()

    def _ingest_ws_frame(self, raw):
        """Synchronous, non-blocking frame ingest (runs in the recv coroutine).
        Applies book/trade/lifecycle state in-order and flags BBO-changed
        tickers dirty for the worker. No awaits -> work is bounded to one frame
        between recv yields, so a flood can never starve the keepalive."""
        msg = json.loads(raw)
        typ = msg.get("type", "")
        if typ == "orderbook_snapshot":
            tk = msg.get("msg", {}).get("market_ticker", "")
            if tk:
                self.apply_snapshot(tk, msg.get("msg", {}))
                self._mark_bbo_dirty(tk)
        elif typ == "orderbook_delta":
            tk = msg.get("msg", {}).get("market_ticker", "")
            if tk:
                bk_before = self.books.get(tk)
                old_bbo = (bk_before.best_bid, bk_before.best_ask) if bk_before else None
                self.apply_delta(tk, msg.get("msg", {}))
                bk_after = self.books.get(tk)
                new_bbo = (bk_after.best_bid, bk_after.best_ask) if bk_after else None
                # Only flag dirty on an actual BBO change (matches tennis_stb):
                # a delta that doesn't move best_bid/best_ask can't change any
                # placement decision.
                if new_bbo != old_bbo:
                    self._mark_bbo_dirty(tk)
        elif typ == "trade":
            # Trades are NOT coalesceable -- every print matters for the tape and
            # VolumeTracker. Applied synchronously in-order; fast, low volume.
            self.apply_trade(msg.get("msg", {}).get("market_ticker", msg.get("msg", {}).get("ticker", "")),
                            msg.get("msg", {}))
        elif typ == "market_lifecycle_v2":
            # Bug 4 §6.2: rare and must NEVER be dropped. Dispatch directly (the
            # settled payload is minimal; the REST value-hop is its own
            # fire-and-forget task, so this does not block recv).
            sub = msg.get("msg", {})
            if sub.get("event_type") == "settled":
                tk = sub.get("market_ticker", "")
                settled_ts = sub.get("settled_ts", time.time())
                if tk:
                    self._maybe_spawn_settlement(tk, settled_ts)
            # determination / deactivated: ignored in v1 (§13 deferred caching)

    def _mark_bbo_dirty(self, ticker):
        """Flag a ticker as needing on_bbo_update routing. O(1), never blocks.
        Last-value-wins: repeated flags before the worker drains collapse to a
        single route on the latest book state."""
        self._bbo_dirty.add(ticker)
        if self._bbo_event is not None:
            self._bbo_event.set()

    async def _ws_worker(self):
        """CONSUMER: run on_bbo_update routing (the expensive, paper-non-yielding
        part) for dirty tickers, COALESCED -- at most one route per ticker per
        drain regardless of how many BBO frames arrived for it. Yields after
        every ticker so a flood can never monopolize the loop. on_bbo_update is
        already self-guarding; the extra try/except is belt-and-suspenders so a
        routing error never kills the worker."""
        while True:
            await self._bbo_event.wait()
            # Clear the event BEFORE snapshotting the set: any ticker flagged
            # after this point re-sets the event and is caught next iteration
            # (no lost updates). There is no await between clear() and the
            # set swap, so the recv coroutine cannot interleave in that window.
            self._bbo_event.clear()
            pending = list(self._bbo_dirty)
            self._bbo_dirty.clear()
            for ticker in pending:
                try:
                    await self.on_bbo_update(ticker)
                except Exception as e:
                    self._log("ws_worker_error",
                              {"error": str(e), "traceback": traceback.format_exc()},
                              ticker=ticker)
                await asyncio.sleep(0)  # yield -- one ticker's routing between yields

    async def _loop_lag_monitor(self):
        """Instrument event-loop scheduling lag (verification for the keepalive
        starvation fix). Sleeps 1.0s and measures the actual elapsed time; a
        delta >1.5s means the loop was starved by synchronous work. Emits a
        loop_lag event on any starvation spike and a periodic loop_lag_sample
        baseline every 30s. App greps loop_lag* to confirm starvation is gone
        before the cutover gate (healthy steady-state ~1.000s, zero spikes)."""
        while True:
            t0 = time.monotonic()
            await asyncio.sleep(1.0)
            delta = time.monotonic() - t0
            self._loop_lag_samples += 1
            dd = len(self._bbo_dirty)
            if delta > 1.5:
                self._log("loop_lag", {"expected_sec": 1.0, "actual_sec": round(delta, 3),
                                       "lag_sec": round(delta - 1.0, 3), "bbo_dirty_depth": dd})
            elif self._loop_lag_samples % 30 == 0:
                self._log("loop_lag_sample", {"actual_sec": round(delta, 3),
                                              "bbo_dirty_depth": dd})

    def _is_settled(self, ticker):
        """True if this ticker's position is already settled (paper or live)."""
        if _PAPER_API is not None:
            ppos = _PAPER_API.paper_positions.get(ticker)
            return bool(ppos and ppos.settled)
        pos = self.positions.get(ticker)
        return bool(pos and pos.settled)

    def _maybe_spawn_settlement(self, ticker, settled_ts):
        """FIX 1: dedup the settled-lifecycle handler spawn. A pre-finalized
        market re-emits `settled` repeatedly; spawning the /markets hop on every
        emit was a CPU/REST storm (1,175 ws_settled_pre_finalized hits, all on
        the event loop). Spawn only if no handler is in-flight for this ticker,
        it isn't already settled, and we haven't attempted within
        SETTLEMENT_RETRY_COOLDOWN. The BBO backstop (and, live, the 5-min REST
        poll) still guarantee settlement, so cooling down repeat hops cannot
        lose one. process_settlement remains idempotent regardless."""
        if ticker in self._inflight_settlements:
            return
        if self._is_settled(ticker):
            return
        now_ts = time.time()
        if now_ts - self._settlement_attempt_ts.get(ticker, 0.0) < SETTLEMENT_RETRY_COOLDOWN:
            return
        self._inflight_settlements.add(ticker)
        self._settlement_attempt_ts[ticker] = now_ts
        asyncio.create_task(self._handle_ws_settlement_dedup(ticker, settled_ts))

    async def _handle_ws_settlement_dedup(self, ticker, settled_ts):
        """Wrap the settlement hop so the in-flight guard is always released,
        even on error (the guard is what suppresses the re-emit storm)."""
        try:
            await self._handle_ws_settlement(ticker, settled_ts)
        finally:
            self._inflight_settlements.discard(ticker)

    async def _handle_ws_settlement(self, ticker, settled_ts):
        """Bug 4 §6.2: WS settled events carry no settlement value (§4.1). Fetch
        it from the public /markets/{ticker} endpoint (paper-safe -- passes
        through to real Kalshi via PaperApi.handle_get). Decoupled into its own
        coroutine so the WS reader loop is not blocked by the REST call."""
        path = "/trade-api/v2/markets/%s" % ticker
        data = await api_get(self.session, self.ak, self.pk, path, self.rl)
        market = (data or {}).get("market", data) or {}

        if market.get("status") != "finalized":
            # Pre-finalized race: determination not yet complete. Do NOT settle.
            # The 5-min REST poll (live) or a later BBO cross will catch it.
            self._log("ws_settled_pre_finalized",
                      {"market_status": market.get("status")}, ticker=ticker)
            return

        # Void guard (decision b): never auto-settle a voided market.
        result = market.get("result") or market.get("market_result")
        if result == "void":
            self._log("settlement_void_manual",
                      {"source": "ws_lifecycle"}, ticker=ticker)
            return

        # Normalize dollars -> integer cents at the call site (decision c).
        sv_dollars = market.get("settlement_value_dollars",
                                market.get("settlement_value", "0"))
        try:
            settle_val_cents = max(0, min(100, round(float(sv_dollars) * 100)))
        except (TypeError, ValueError):
            self._log("ws_settle_value_unparseable", {"raw": sv_dollars}, ticker=ticker)
            return

        self.process_settlement(ticker, settle_val_cents, settled_ts, source="ws_lifecycle")

    # ------------------------------------------------------------------
    # Market discovery
    # ------------------------------------------------------------------
    async def discover_markets(self):
        all_tickers = []
        now = time.time()
        counts = defaultdict(int)
        last_yield = time.monotonic()  # FIX 3: time-based chunk-yield cursor
        _reconciled_starts = set()  # [C-SCHEDULE-TRUST-FIX] reconcile once per event per cycle
        for series in ALL_SERIES:
            cursor = ""
            for _ in range(10):
                path = "/trade-api/v2/markets?limit=100&status=open&series_ticker=%s" % series
                if cursor:
                    path += "&cursor=%s" % cursor
                data = await api_get(self.session, self.ak, self.pk, path, self.rl)
                if not data:
                    break
                for m in data.get("markets", []):
                    # FIX 3: yield whenever ~2ms of synchronous work has
                    # accumulated (schedule fuzzy-match + per-event sqlite
                    # commence lookups). Bounding work-between-yields (not market
                    # count) keeps the loop / keepalive serviced even when many
                    # events hit the heavy match path. ~2ms chunks -> sub-30ms
                    # loop lag (verified).
                    if time.monotonic() - last_yield > 0.002:
                        await asyncio.sleep(0)
                        last_yield = time.monotonic()
                    ticker = m["ticker"]
                    vol = int(float(m.get("volume_fp", "0") or "0"))
                    if vol < MIN_VOLUME:
                        continue
                    expiry_str = m.get("expected_expiration_time", "")
                    if expiry_str and not expiry_str.startswith("0001"):
                        try:
                            exp = datetime.fromisoformat(expiry_str.replace("Z", "+00:00")).timestamp()
                            if (exp - now) / 3600 > MAX_HOURS_TO_EXPIRY:
                                continue
                        except:
                            pass
                    et = m["event_ticker"]
                    self.ticker_to_event[ticker] = et
                    self.event_tickers[et].add(ticker)
                    # Capture open_time (for unmatched-skip age check)
                    if et not in self.event_open_time:
                        ot_str = m.get("open_time", "")
                        if ot_str:
                            try:
                                self.event_open_time[et] = datetime.fromisoformat(
                                    ot_str.replace("Z", "+00:00")).timestamp()
                            except Exception:
                                pass
                    # Capture player names for schedule matching
                    if et not in self.event_player_names:
                        names = []
                        yes_name = m.get("yes_sub_title", "")
                        no_name = m.get("no_sub_title", "")
                        if yes_name:
                            names.append(yes_name)
                        if no_name and no_name != yes_name:
                            names.append(no_name)
                        if names:
                            self.event_player_names[et] = names
                    # Schedule match (if not already matched and not processed)
                    if et not in self.event_start_time and et not in self.processed_events:
                        sched_entry, method = await self._match_event_to_schedule_async(et)
                        if sched_entry:
                            st_str = sched_entry.get("start_time", "")
                            if st_str:
                                try:
                                    self.event_start_time[et] = datetime.fromisoformat(
                                        st_str.replace("Z", "+00:00")).timestamp()
                                    self.event_start_source[et] = sched_entry.get("source", method or "schedule")
                                except Exception:
                                    pass
                        else:
                            # Fallback 1: Odds API commence_time from book_prices
                            ct = self._commence_time_from_book_prices(et)
                            if ct is not None:
                                self.event_start_time[et] = ct.timestamp()
                                self.event_start_source[et] = "odds_api"
                                self._log("schedule_match", {
                                    "event": et, "method": "odds_api_commence_time",
                                    "start_time": ct.isoformat(),
                                })
                            else:
                                # No reliable commence source — skip rather than use Kalshi expiration
                                self.event_unmatched_cycles[et] = self.event_unmatched_cycles.get(et, 0) + 1
                                self._log("no_reliable_commence_source", {"event": et})
                    # [C-SCHEDULE-TRUST-FIX] pre-start correction of a set-once /
                    # _date_ok-rejected start (JOVANI root). Runs even for matched
                    # / processed events; once per event per cycle.
                    if et not in _reconciled_starts:
                        _reconciled_starts.add(et)
                        await self._reconcile_event_start(et, now)
                    cat = self.get_category(ticker)
                    if cat:
                        self.ticker_category[ticker] = cat
                        counts[cat] += 1
                        all_tickers.append(ticker)
                cursor = data.get("cursor", "")
                if not cursor:
                    break
        self._log("discovery", {"total_tickers": len(all_tickers), "by_category": dict(counts)})
        return all_tickers

    # ------------------------------------------------------------------
    # Side identification
    # ------------------------------------------------------------------
    def _sibling_ticker(self, tk, et):
        """The other side of a two-outcome event (None if not exactly one sibling)."""
        sibs = [t for t in self.event_tickers.get(et, ()) if t != tk]
        return sibs[0] if len(sibs) == 1 else None

    def _sibling_engageable(self, sib):
        """[C-BID-SURVIVAL DIFF-1 / PRE-GATE B] Engageable := we hold or rest the
        sibling (real cost exists), OR its book has a print within
        V4_LAST_TRADE_MAX_AGE_SEC (1800s) -- the EXACT constant placement uses,
        so engageable <=> the routing could legally bid that leg right now.
        Non-thrash: computed once per guard evaluation from a single snapshot;
        dead->engageable flips only on a NEW print (evidence-monotone),
        engageable->dead only by clock advance."""
        sp = self.positions.get(sib)
        if (sp is not None and not sp.settled
                and (sp.entry_qty > 0
                     or (sp.phase == "entry_resting" and sp.entry_order_id))):
            return True
        sb = self.books.get(sib)
        if sb is None or sb.last_trade_price <= 0:
            return False
        lt_age = (time.time() - sb.last_trade_ts) if sb.last_trade_ts else float("inf")
        return lt_age <= V4_LAST_TRADE_MAX_AGE_SEC

    def _paired_basis_ok(self, tk, et, this_price):
        """T50 paired-basis guard. Returns False if entering `tk` at this_price
        would push the event's COMBINED basis (this side + the sibling's
        committed cost) over V4_PAIRED_BASIS_CAP — i.e. a yes+no > ~100
        guaranteed loss (KESMAR 37+75=112). Sibling committed cost = its
        Position.entry_price if we hold/rest a side (fill price if filled, bid
        price if resting), else the sibling's current ask (the level we'd pay).
        No sibling signal -> allow (cancel-on-fill is the backstop). Ports the
        arb_executor_ws.py intra-k combined=ask_a+ask_b math (negative space).

        [C-BID-SURVIVAL DIFF-1] phantom-sibling scoping: the current-ask
        substitution applies ONLY when the sibling is ENGAGEABLE (we could
        actually buy it -- _sibling_engageable). A dead sibling (no position,
        no print within 1800s) cannot complete the pair, so the leg is
        single-sided: the per-leg sanity governs and the decision is NAMED
        (single_sided_hold). Revival: the next evaluation sees the fresh print
        and runs the guard on REAL prices; over-cap then DECLINES placement
        (paired_basis_skip, named) -- never retroactive-cancels a held leg.
        The Collarini kill (2026-06-11 12:41:19, own 69 + phantom ask 33 = 102
        with ZERO sibling exposure and the sibling anchor-dead) is this exact
        branch."""
        sib = self._sibling_ticker(tk, et)
        if not sib:
            return True
        sp = self.positions.get(sib)
        if sp is not None and not sp.settled and sp.entry_price > 0:
            sib_cost = sp.entry_price
        else:
            if not self._sibling_engageable(sib):
                sb = self.books.get(sib)
                lt_age = ((time.time() - sb.last_trade_ts)
                          if sb is not None and sb.last_trade_ts else None)
                self._log("single_sided_hold", {
                    "event": et, "this_price": this_price, "sibling": sib[-12:],
                    "reason": "sibling_dead_no_position_no_fresh_print",
                    "sibling_ask": sb.best_ask if sb else None,
                    "sibling_last_trade_age_sec": round(lt_age, 1) if lt_age is not None else None,
                    "cap": V4_PAIRED_BASIS_CAP}, ticker=tk)
                return True
            sb = self.books.get(sib)
            sib_cost = sb.best_ask if sb else None
        if not sib_cost or sib_cost <= 0:
            return True
        combined = this_price + sib_cost
        if combined > V4_PAIRED_BASIS_CAP:
            self._log("paired_basis_skip", {
                "event": et, "this_price": this_price, "sibling": sib[-12:],
                "sibling_cost": sib_cost, "combined": combined,
                "cap": V4_PAIRED_BASIS_CAP}, ticker=tk)
            return False
        return True

    async def _cancel_sibling_if_paired_over_cap(self, tk, et, this_basis):
        """T50 backstop + PART-2 completion hook -- the ONE sibling handler invoked at
        all three entry-fill booking sites (check_fills entry poll, placement
        instant-fill, T-20m instant-fill). Mutually exclusive by cap arithmetic:

          this_basis + sibling_bid > cap -> T50 cancel (UNCHANGED, byte-identical);
          else, completion_reprice=true AND (category, leg-1 window-open cell) in
          completion_cells AND the sibling still entry_resting -> reprice the sibling's
          bid to s1 = min(s0 + X, sibling_ask - 1, 99 - this_basis), sized to leg-1's
          FILLED qty (s0 = SIBLING window-open price; replay frame, 1944b250).

        T50 part: cancels the sibling's still-RESTING entry bid when the pair would be
        a yes+no > ~100 guaranteed loss. Closes the both-bids-resting race the placement
        guard can't prevent. No-op if the sibling already filled (pair locked) or isn't
        a resting entry. Default completion_reprice OFF -> the completion arm is
        unreachable and this method IS the pre-Part-2 T50 backstop exactly."""
        sib = self._sibling_ticker(tk, et)
        if not sib:
            return
        sp = self.positions.get(sib)
        if sp is None or sp.settled or sp.phase != "entry_resting" or not sp.entry_order_id:
            return
        if sp.entry_qty > 0:
            return  # sibling already filled -> nothing to cancel
        sib_bid = sp.entry_price
        # [C-CAP-REMOVAL site 3] flag-gated dormant: with the cap off, a leg-1
        # fill never cancels the resting sibling on pair arithmetic -- the
        # over-cap pair falls through to the completion arm (cell-valid
        # reprice, per-leg-bounded). NAMED RESIDUAL (operator-accepted): both
        # legs filling rich (KESMAR shape) rides the per-cell exits, bounded
        # ~$0.60/pair worst case at 5-lot.
        if (sib_bid > 0 and (this_basis + sib_bid) > V4_PAIRED_BASIS_CAP
                and getattr(self, "paired_cap_enforced", True)):
            # [C-P0-RACE site 4] resolve against exchange truth: if the sibling's
            # bid filled in the race window (both legs filling near-simultaneously),
            # its fill is BOOKED -- the pair is locked, reality, manage the exits --
            # instead of the old delete-unbooked path. Clean cancel is byte-identical
            # to the pre-fix T50 arm.
            res = await self._cancel_entry_and_resolve(
                sib, sp, "paired_basis_cancel", "t50_cancel_race")
            if res == "cancelled":
                self._log("paired_basis_cancel", {
                    "event": et, "filled_side": tk[-12:], "filled_basis": this_basis,
                    "cancelled_sibling": sib[-12:], "sibling_bid": sib_bid,
                    "combined": this_basis + sib_bid, "cap": V4_PAIRED_BASIS_CAP},
                    ticker=sib)
                sp.entry_order_id = ""
                self._untombstone_entry(sib, sp)
                self._save_v4_resting()
            elif res == "booked":
                self._log("paired_basis_filled_race", {
                    "event": et, "filled_side": tk[-12:], "filled_basis": this_basis,
                    "sibling": sib[-12:], "sibling_fill": sp.entry_price,
                    "combined": this_basis + sp.entry_price,
                    "cap": V4_PAIRED_BASIS_CAP}, ticker=sib)
            else:
                self._log("paired_basis_cancel_unresolved", {
                    "event": et, "sibling": sib[-12:], "sibling_bid": sib_bid,
                    "combined": this_basis + sib_bid}, ticker=sib)
            return
        if not self.completion_reprice or self.completion_disabled:
            return
        await self._attempt_completion_reprice(tk, et, this_basis, sib, sp)

    def _completion_target(self, s0, x_cell, sib_ask, leg1_basis):
        """PART-2: s1 = min(s0 + X, sib_ask - 1, 99 - leg1_basis). sib_ask=None (no
        real ask on the book) drops the ask term -- replay parity (the 1944b250
        completion branch adds the ask candidate only when an ask exists). The cap term
        guarantees leg1_basis + s1 <= V4_PAIRED_BASIS_CAP. Pure/testable.

        [C-CAP-REMOVAL] with the cap dormant the pair-arithmetic term is
        replaced by the PER-LEG sanity bound (99): the completion reprices to
        the sibling's own cell-valid level (s0 + X, ask-clamped), no longer
        squeezed by leg-1's basis. The manage-side freshness re-evaluation and
        its cap_headroom_gone revert flow through THIS function, so both
        attempt and manage sites follow the flag automatically."""
        if getattr(self, "paired_cap_enforced", True):
            cands = [s0 + x_cell, V4_PAIRED_BASIS_CAP - leg1_basis]
        else:
            cands = [s0 + x_cell, 99]
        if sib_ask is not None:
            cands.append(sib_ask - 1)
        return min(cands)

    def _completion_buffer_exempt(self, pos):
        """PART-2 item 5: completion bids are exempt from the T-15 match_start_buffer
        cancel and ride to T-0 under freshness re-evaluation (_v4_manage_completion).
        Scoped to entry_mode == "completion_reprice" ONLY -- fresh entry bids keep the
        buffer unchanged. Void/halt on a never-filled completion bid is exchange-
        counterparty risk: a voided market simply cancels the resting order exchange-
        side; NO assumption about void settlement price is made anywhere in this code.
        Pure/testable."""
        return pos.entry_mode == "completion_reprice"

    async def _fill_is_taker(self, tk, order_id):
        """PART-2 item 7: exchange fill truth (operator feedback: maker/taker comes
        from /portfolio/fills is_taker, NEVER from placement intent). Returns True if
        any fill on this order was taker, False if all maker, None on lookup failure.
        Called only on completion-path events (flag-gated call sites) -- zero extra API
        load when completion_reprice is off."""
        try:
            data = await api_get(self.session, self.ak, self.pk,
                "/trade-api/v2/portfolio/fills?ticker=%s&limit=50" % tk, self.rl)
            takers = [bool(f.get("is_taker")) for f in (data or {}).get("fills", [])
                      if f.get("order_id") == order_id]
            if not takers:
                return None
            return any(takers)
        except Exception:
            return None

    async def _attempt_completion_reprice(self, tk, et, this_basis, sib, sp):
        """PART-2 item 3: one completion attempt for a freshly-filled leg-1 (`tk` at
        this_basis) against its sibling's resting bid. Caller has already verified:
        flag on, sibling entry_resting + unfilled + has order, and -- when the paired
        cap is ENFORCED -- pair not over the T50 cap ([C-CAP-REMOVAL]: with the cap
        dormant, over-cap pairs reach here by design and s1 is per-leg-bounded via
        _completion_target). The eligibility cell comes from LEG-1's window-open frame and s0 from the
        SIBLING's window-open price -- NEVER from current_price (frame-mismatch leak;
        the only book-time inputs are the ask clamp and the cap term)."""
        if self.completion_disabled:
            return  # [C-TRIPWIRE] belt: mechanism dead -> no attempts
        if sp.entry_mode == "completion_reprice":
            return  # already completion-repriced (idempotent across partial leg-1 fills)
        pos = self.positions.get(tk)
        if pos is None or pos.entry_qty <= 0:
            return
        wo1 = self._window_open.get(tk)
        if wo1 is None:
            # designed conservative edge: leg-1 filled with no window-open frame
            # (pre-T-240 fill / no fresh print ever inside the window) -> NO attempt.
            self._log("completion_no_attempt", {"event": et,
                "reason": "leg1_window_open_unset", "leg1_basis": this_basis}, ticker=tk)
            return
        x_cell = self.completion_cells.get((pos.category, wo1["cell"]))
        if x_cell is None:
            # absent cell = never attempt (the no-attempt arm of the wave-gate pairing)
            self._log("completion_no_attempt", {"event": et,
                "reason": "cell_not_eligible", "category": pos.category,
                "cell_at_completion_lookup": wo1["cell"],
                "leg1_basis": this_basis}, ticker=tk)
            return
        wo2 = self._window_open.get(sib)
        if wo2 is None:
            self._log("completion_no_attempt", {"event": et,
                "reason": "sibling_window_open_unset",
                "cell_at_completion_lookup": wo1["cell"],
                "leg1_basis": this_basis}, ticker=tk)
            return
        s0 = wo2["price"]
        sib_book = self.books.get(sib)
        sib_ask = sib_book.best_ask if (sib_book and 0 < sib_book.best_ask < 100) else None
        s1 = self._completion_target(s0, x_cell, sib_ask, this_basis)
        cap_headroom = V4_PAIRED_BASIS_CAP - this_basis
        if s1 <= s0 or s1 < 1:
            self._log("completion_no_attempt", {"event": et, "reason": "no_headroom",
                "s0": s0, "s1": s1, "x": x_cell, "cap_headroom": cap_headroom,
                "sib_ask": sib_ask, "cell_at_completion_lookup": wo1["cell"],
                "leg1_basis": this_basis}, ticker=tk)
            return
        if s1 == sp.entry_price:
            # already resting exactly at s1 -- a cancel/re-place would only forfeit
            # queue priority (inert skip, disclosed).
            self._log("completion_no_attempt", {"event": et, "reason": "already_at_s1",
                "s0": s0, "s1": s1, "x": x_cell,
                "cell_at_completion_lookup": wo1["cell"]}, ticker=tk)
            return
        # fill-race discipline (mirrors the move-repost path): the sibling's original
        # bid may have just filled -- never cancel-and-replace a filled order's booking.
        old = await api_get(self.session, self.ak, self.pk,
            "/trade-api/v2/portfolio/orders/%s" % sp.entry_order_id, self.rl)
        if old:
            old_filled = int(float((old.get("order", old).get("fill_count_fp", 0)) or 0))
            if old_filled > 0:
                return  # filled at its own price -- check_fills books it; pair completed naturally
        qty = pos.entry_qty  # completion qty = leg-1 FILLED qty
        prev_price, prev_mode, prev_target = sp.entry_price, sp.entry_mode, sp.target_price
        price, po = self._reprice_target(s1, sib_book.best_ask if sib_book else 100)
        if not po:
            # [C-TRIPWIRE] V1: a completion order about to go out non-post-only IS the
            # violation -- fire BEFORE touching the sibling's resting bid.
            await self._completion_tripwire("V1_post_only_breach",
                {"site": "attempt", "s1": s1, "price": price, "event": et}, tk=sib)
            return
        # [C-P0-RACE site 5b] pre-place resolve: never stack a completion bid on top
        # of an unconfirmed cancel. A raced sibling fill books normally (the pair is
        # complete -- no completion needed); an unresolved cancel aborts the attempt.
        res = await self._cancel_entry_and_resolve(
            sib, sp, "completion_reprice", "completion_attempt_race")
        if res != "cancelled":
            self._log("completion_no_attempt", {
                "event": et,
                "reason": ("sibling_filled_in_race" if res == "booked"
                           else "cancel_unresolved")}, ticker=sib)
            return
        self.inflight_orders.add(sib)
        try:
            oid, _resp = await self.place_order(sib, "buy", "yes", price, qty,
                                                post_only=po)
        finally:
            self.inflight_orders.discard(sib)
        if not oid:
            # place failed after the old bid was cancelled -> free the leg cleanly
            # (leg-1 rides as a normal v4 position; orphan snapshot for the wave-gate).
            self._log("completion_reverted", {"event": et, "reason": "place_failed",
                "s0": s0, "s1": price, "x": x_cell, "time_since_reprice": 0.0}, ticker=sib)
            sp.entry_order_id = ""
            self._untombstone_entry(sib, sp)
            self._save_v4_resting()
            return
        sp.entry_price = price
        sp.entry_order_id = oid
        sp.entry_mode = "completion_reprice"
        sp.play_type = "v4_completion_reprice"
        sp.target_price = price
        sp.completion_s0 = s0
        sp.completion_x = x_cell
        sp.completion_leg1_basis = this_basis
        sp.completion_qty = qty
        sp.completion_reprice_ts = time.time()
        sp.completion_prev_price = prev_price
        sp.completion_prev_mode = prev_mode
        sp.completion_prev_target = prev_target
        sp.completion_lookup_cell = wo1["cell"]
        self._log("completion_attempt", {
            "event": et, "s0": s0, "s1": price, "x": x_cell,
            "cap_headroom": cap_headroom, "trigger_fill_id": pos.entry_order_id,
            "cell_at_completion_lookup": wo1["cell"], "leg1_basis": this_basis,
            "qty": qty, "sib_ask": sib_ask, "prev_bid": prev_price,
            "order_id": oid}, ticker=sib)
        self._save_v4_resting()

    async def _reconcile_event_start(self, et, now):
        """[C-SCHEDULE-TRUST-FIX] Pre-start correction of a set-once / _date_ok-
        rejected start. The initial match (:2503) is set-once, and _date_ok
        rejects a legitimately-postponed next-day start vs the Kalshi ticker
        date (the JOVANI/Berlin frame: direct_6char locked 06-13, real 06-14,
        ~24h early). Re-read the schedule by the event's EXACT 6-char code (no
        fuzzy match, so _date_ok's wrong-event guard is moot) and adopt a
        corroborated correction PRE-START only. Updating event_start_time
        re-derives the entry window on the next routing pass (a later start
        defers the T-240m window). Guard rails:
          (1) never rewrite a genuinely live match (tape latch via
              _is_match_live) -- protects ride-live / in-play logic;
          (2) source priority -- a stronger/equal feed may correct, a weaker
              one may not (SCHED_SOURCE_RANK);
          (3) a correction pushing the start beyond T-240m cancels resting
              entry bids that are now early (filled positions + exits untouched);
          (4) a schedule_corrected event logs every firing.
        """
        seg = et.rsplit("-", 1)[-1]
        code = seg[7:] if len(seg) > 7 else seg  # strip DDMmmYY (7-char) date prefix -> 6-char code
        if not code:
            return
        sched = self.schedule.get(code)
        if not sched:
            return
        st_str = sched.get("start_time", "")
        if not st_str:
            return
        try:
            new_start = datetime.fromisoformat(st_str.replace("Z", "+00:00")).timestamp()
        except Exception:
            return
        # Only correct to a FUTURE start. An already-started or stale schedule
        # row (wrong-code collision -- e.g. a 5-day-old entry, or a date a feed
        # placed before the ticker date) is handled by the live-tape latch and
        # match_already_started; bypassing _date_ok must NOT resurrect a
        # wrong-day past row as a "start".
        if new_start <= now:
            return
        new_src = sched.get("source", "?")
        new_rank = SCHED_SOURCE_RANK.get(new_src, 0)
        if new_rank < 1:
            return  # untrusted / unknown source never drives a correction
        if self._is_match_live(et):
            return  # tape says live -> never rewrite the start (ride-live / in-play)
        stored = self.event_start_time.get(et)
        stored_rank = SCHED_SOURCE_RANK.get(self.event_start_source.get(et, "?"), 0)
        if stored is not None:
            if abs(new_start - stored) <= 900:
                return  # no material change (<15min)
            if new_rank < stored_rank:
                return  # a weaker source may not override a stronger-sourced start
        old, old_src = stored, self.event_start_source.get(et)
        self.event_start_time[et] = new_start
        self.event_start_source[et] = new_src
        # Re-derive the window: a start now beyond T-240m means any resting entry
        # bid for this event is early -> cancel it (exchange-truth resolved; a
        # raced fill books, _untombstone_entry frees an unfilled leg for re-entry
        # at the real window). Filled positions and their exits are untouched.
        cancelled = []
        new_tts = new_start - now
        if new_tts > V4_MAX_PLACEMENT_SEC:
            for tk, pos in list(self.positions.items()):
                if (pos.event_ticker == et and pos.phase == "entry_resting"
                        and pos.entry_order_id):
                    res = await self._cancel_entry_and_resolve(
                        tk, pos, "schedule_corrected_window_deferred",
                        "schedule_corrected_race")
                    if res == "cancelled":
                        self._untombstone_entry(tk, pos)
                        cancelled.append(tk)
            if cancelled:
                self._save_v4_resting()
        action = ("early_bids_cancelled" if cancelled
                  else "window_deferred" if new_tts > V4_MAX_PLACEMENT_SEC
                  else "start_set" if old is None else "start_updated")
        self._log("schedule_corrected", {
            "event": et,
            "old_start": (datetime.fromtimestamp(old, tz=timezone.utc).isoformat()
                          if old else None),
            "old_source": old_src,
            "new_start": datetime.fromtimestamp(new_start, tz=timezone.utc).isoformat(),
            "new_source": new_src,
            "new_tts_min": round(new_tts / 60.0, 1),
            "cancelled_bids": cancelled,
            "action": action,
        })

    def _is_match_live(self, et):
        """T51 match-live detection via VOLUME ACCELERATION. Live = >=
        LIVE_TRADE_BURST trade prints across the event's legs within the last
        LIVE_DETECT_WINDOW_SEC. Price-move is deliberately NOT the signal — a
        tight even match stays price-flat (TIAARN sat at 50-51c through its
        window), so the old >=10c proxy was blind; trade flow is the reliable
        tell. (A reliable in-play status feed would strengthen this; none is
        currently available — see T51.)

        [C-FEEDER FIX-1] three amendments (the 2026-06-12 5AM block: premarket
        volume bursts at T-3.5h..4h latched ZHAMAN/MPEBUB/BLAJOR live and
        permanently scratched them):
          1. TTS FLOOR: a burst can never latch while the feed time-to-start is
             above LIVE_DETECT_TTS_FLOOR_SEC (teardown envelope: real starts
             latch within ~60s of onset; >=30min-early fires are 68.5% noise).
             Unknown start time -> floor cannot apply (those events are already
             blocked from placement by no_reliable_commence_source).
          2. TWO-STAGE LATCH: the first qualifying burst only arms stage-1; the
             latch requires a second qualifying burst at least
             LIVE_DETECT_CONFIRM_MIN_GAP_SEC later (sustained flow across two
             non-overlapping windows), within LIVE_DETECT_CONFIRM_TTL_SEC.
          3. COUNTER-EVIDENCE UNLATCH: a latch claiming "live" while the feed
             still says tts > floor AND the tape has been quiet for
             LIVE_DETECT_UNLATCH_QUIET_SEC is a false latch (a real live match
             prints continuously) -> cleared, named. Time-based clears were
             rejected (Plex); this is evidence-based only."""
        now = time.time()
        st = getattr(self, "event_start_time", {}).get(et)
        tts = (st - now) if st else None
        if et in self._events_live:
            if tts is not None and tts > LIVE_DETECT_TTS_FLOOR_SEC:
                qcut = now - LIVE_DETECT_UNLATCH_QUIET_SEC
                quiet = not any(t >= qcut
                                for tk in self.event_tickers.get(et, ())
                                for t in (self._trade_times.get(tk) or ()))
                if quiet:
                    self._events_live.discard(et)
                    getattr(self, "_live_stage1", {}).pop(et, None)
                    getattr(self, "_live_skip_logged", set()).discard(et)
                    self._log("match_live_unlatched", {
                        "event": et, "reason": "counter_evidence_quiet",
                        "tts_min": round(tts / 60.0, 1),
                        "quiet_sec": LIVE_DETECT_UNLATCH_QUIET_SEC})
                    return False
            return True
        cutoff = now - LIVE_DETECT_WINDOW_SEC
        recent = 0
        for tk in self.event_tickers.get(et, ()):
            dq = self._trade_times.get(tk)
            if dq:
                recent += sum(1 for t in dq if t >= cutoff)
        if recent < LIVE_TRADE_BURST:
            return False
        if tts is not None and tts > LIVE_DETECT_TTS_FLOOR_SEC:
            return False  # FIX-1 floor: premarket burst, not a start
        stage1 = getattr(self, "_live_stage1", None)
        if stage1 is None:
            stage1 = self._live_stage1 = {}
        t0 = stage1.get(et)
        if t0 is None or (now - t0) > LIVE_DETECT_CONFIRM_TTL_SEC:
            stage1[et] = now
            return False  # stage-1 armed; confirm on a later window
        if (now - t0) < LIVE_DETECT_CONFIRM_MIN_GAP_SEC:
            return False  # same window; not yet independent confirmation
        stage1.pop(et, None)
        self._events_live.add(et)
        # [C-FV-BURST] observe-only snapshot of FV at the real-start latch. Wrapped
        # so it can NEVER raise into the latch path; runs AFTER the latch and does
        # not touch _events_live / orders / the return value. (try scope = this
        # call only; Exception, not bare, so KeyboardInterrupt/SystemExit propagate.)
        try:
            self._fv_burst_snapshot(et, now)
        except Exception:
            pass
        self._log("match_live_detected", {
            "event": et, "trades_in_window": recent,
            "window_sec": LIVE_DETECT_WINDOW_SEC, "signal": "volume_burst",
            "stage1_age_sec": round(now - t0, 1),
            "tts_min": (round(tts / 60.0, 1) if tts is not None else None)})
        return True

    def _fv_burst_ready(self, et, now):
        """[C-FV-BURST RE-GATE] OBSERVE-ONLY real-start trigger for the FV snapshot,
        decoupled from _is_match_live's latch (which fires only via the resting-bid
        path in _v4_manage_resting -> misses both-filled events, ~67% of the slate).
        True once the event's tape shows a burst (>= LIVE_TRADE_BURST prints /
        LIVE_DETECT_WINDOW_SEC across legs) and we are not premarket (tts <= floor).

        PURE READ -- reads event_start_time / _trade_times / event_tickers only;
        writes nothing; no _events_live, no _live_stage1, no two-stage, no log, no
        await, no side effect. Mirrors only the recent-count + TTS-floor INPUTS of
        _is_match_live and shares NONE of its state -> cannot alter any trading
        decision or the real _is_match_live latch."""
        st = getattr(self, "event_start_time", {}).get(et)
        tts = (st - now) if st else None
        if tts is not None and tts > LIVE_DETECT_TTS_FLOOR_SEC:
            return False
        cutoff = now - LIVE_DETECT_WINDOW_SEC
        recent = 0
        for tk in self.event_tickers.get(et, ()):
            dq = self._trade_times.get(tk)
            if dq:
                recent += sum(1 for t in dq if t >= cutoff)
        return recent >= LIVE_TRADE_BURST

    def _fv_burst_snapshot(self, et, now):
        """[C-FV-BURST instrumentation -- OBSERVE-ONLY] At the real-start latch,
        snapshot per-leg FV (book mid/bid/ask/last) into self._fv_burst and emit a
        fv_burst_anchor log line tagging each leg's entry distance from FV
        (entry_minus_fv_burst = entry_price - fv_mid; positive = entered ABOVE FV;
        entry_price = fill price if already filled, else the resting target).

        ZERO behavior change: the body mutates ONLY self._fv_burst (the new
        instrumentation dict). It does NOT write Position objects, self.books,
        self._events_live, the rate limiter, or any order queue; it contains no
        await and makes no order/cancel/price/timing decision. Reads are the books,
        positions and event-ticker map. Called once per event (the latch branch
        runs only on the latching pass; a re-latch after counter-evidence unlatch
        keeps the FIRST anchor via the `tk in self._fv_burst` guard). Pre-burst
        fills are tagged here in the log line; post-burst fills are tagged in
        _book_v4_entry_fill from the stored snapshot. Self-prunes by age (memory
        hygiene -- touches only this dict)."""
        if self._fv_burst:
            cut = now - FV_BURST_RETENTION_SEC
            for stale in [k for k, v in self._fv_burst.items()
                          if v.get("ts", 0) < cut]:
                self._fv_burst.pop(stale, None)
        legs = self.event_tickers.get(et, ())
        n_filled = sum(1 for t in legs
                       if self.positions.get(t) and self.positions[t].entry_filled_ts)
        for tk in legs:
            if tk in self._fv_burst:
                continue
            bk = self.books.get(tk)
            if bk is None:
                continue
            mid = ((bk.best_bid + bk.best_ask) / 2.0
                   if bk.best_bid > 0 and bk.best_ask < 100 else None)
            self._fv_burst[tk] = {"mid": mid, "bid": bk.best_bid, "ask": bk.best_ask,
                                  "last": bk.last_trade_price, "ts": now}
            pos = self.positions.get(tk)
            if pos is None:
                continue
            filled = bool(pos.entry_filled_ts)
            entry_px = pos.entry_price if filled else pos.target_price
            emfv = (entry_px - mid) if (mid is not None and entry_px) else None
            self._log("fv_burst_anchor", {
                "event": et, "cat": pos.category, "cell": pos.cell_name,
                "regime": pos.regime_at_posting,
                "reference_source": pos.reference_source,
                "legs_filled": n_filled,
                "solo_or_pair": ("pair" if n_filled >= 2 else "solo"),
                "filled_pre_burst": filled,
                "entry_price": entry_px,
                "fill_price": (pos.entry_price if filled else None),
                "fv_mid": mid, "fv_bid": bk.best_bid, "fv_ask": bk.best_ask,
                "fv_last": bk.last_trade_price,
                "entry_minus_fv_burst": emfv}, ticker=tk)

    def _fv_observe_fields(self, et, tk, full_name, price, match_live):
        """[C-FV-OBSERVE-SHIP, Plex-countersigned] the sharp-book blend riding
        placement/observation/adoption logs -- the SAME sharp_fv codepath as
        analysis/fv_quote.py (one backend, two consumers; tennis_odds'
        calc_no_vig is the single no-vig implementation, the math OMI Edge
        consumes). Emits fv, fv_gap (price - fv) and the SOURCE LIST
        [[book_key, age_sec, status]] so calibration recovers the blend's
        anatomy per row. ZERO behavioral effect: logging only, no gate, no
        veto; any failure degrades to an empty dict."""
        try:
            mod = getattr(self, "_fv_quote_mod", None)
            if mod is None:
                import importlib.util
                _p = Path(__file__).resolve().parent / "analysis" / "fv_quote.py"
                spec = importlib.util.spec_from_file_location("fv_quote_mod", _p)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                self._fv_quote_mod = mod
            fv, sources, reason = mod.sharp_fv(et, full_name or "",
                                               bool(match_live), ticker=tk)
            return {
                "fv": fv,
                "fv_gap": (round(price - fv, 2)
                           if fv is not None and price is not None else None),
                "fv_sources": sources,
                **({"fv_reason": reason} if reason else {}),
            }
        except Exception:
            return {}

    def _manual_owns_leg(self, tk):
        """[C-MANUAL-FIRST, OP-3 ruling] first trade on a leg owns it; the bot
        yields to operator presence. True when the leg carries a resting
        manual bid (manual_bids registry) OR an open manual-attributed
        position. Scope is PER-LEG -- the sibling stays bot-eligible
        (bilateral coverage stands). The operator withdrawing his bid
        untracks it in reconcile, re-opening the leg next pass. Entry-side
        only: exits are untouched (mixed-share legs size to total open per
        the P0v2 machinery). Pure/testable."""
        if not getattr(self, "operator_manual_mode", False):
            return False
        if tk in getattr(self, "manual_bids", {}):
            return True
        pos = self.positions.get(tk)
        return bool(pos is not None and not pos.settled
                    and pos.play_type == "v4_manual")

    def _intended_join_at_placement(self, entry_mode, target_bid, placement_bid,
                                    table_src):
        """[C-FEEDER FIX-2] the intended_join key, derived from the placement
        DECISION. Pure/testable. Two sources of truth, no live-book re-read:
          - engagement placements (table_src == engagement_wave1) are joins BY
            CONSTRUCTION (the eligibility check returned best_bid as the
            level); True regardless of which execution branch the moving book
            pushed them down (resting_maker OR marketable_clamp). The old
            post-await `target_bid == book.best_bid` re-read keyed a
            by-construction join False whenever the book ticked during the
            pre-post-guard/place_order awaits -- the QUESAM E3 fire,
            2026-06-12 10:32:21 ET.
          - normal resting-maker placements: target sat AT the decision-time
            best bid (the captured snapshot, same values the v4_place log
            carries)."""
        if table_src == "engagement_wave1":
            return True
        return entry_mode == "resting_maker" and target_bid == placement_bid

    def _runway_status(self, placement_min, time_to_start, late_tag="late_window"):
        """[C-FEEDER FIX-6] (offset, placement_minute) is INDIVISIBLE -- the
        table validated the pair as a unit: a deep offset earns its fill rate
        by resting the row's full runway. A1 boundary, whichever fires first:
          sub_60     : the placement sits inside T-60 (RADRAK frame, T-56 open)
          late_*     : available runway (tts minus the T-15 buffer) is under
                       HALF the validated runway (placement_minute - 15)
          full       : the validated envelope holds
        late_tag distinguishes A2 granularity: late_window for placement-path
        (the leg's window opened late -> every affected band of the match gets
        the tag as its legs evaluate), late_remap for the manage-side repost
        (that bid only). Pure/testable."""
        if time_to_start <= 3600.0:
            return "sub_60"
        validated = max(placement_min - 15, 1) * 60.0
        available = time_to_start - 900.0
        if available < 0.5 * validated:
            return late_tag
        return "full"

    def _fix6_reference(self, runway_status, offset, table_src, current_price,
                        target_bid):
        """[C-FEEDER FIX-6] A3/A4: on a late runway, a deep table offset is
        INVALID (its validated runway is gone) -> switch the reference to a
        JOIN at the anchor level (offset 0), flagged
        reference_source=join_late_runway. Scope: deep-offset table placements
        and reposts ONLY -- engagement joins (table_src engagement_wave1,
        offset 0 by construction) are untouched. The flag route is the A4
        answer: routing through the engagement code path proper is NOT
        feasible (it is keyed on the ABSENCE of a fresh print and carries
        wave-1 ledger attribution); cap/T52/T-15-buffer equivalence is
        inherited through the normal machinery exactly the way engagement
        joins inherit it, and the FIX-2/3 placement-time keys grant the
        stale-exemption precisely when the join level IS the bid / ask-1.
        Returns (target_bid, reference_source). Pure/testable."""
        if (runway_status != "full" and offset >= 1
                and table_src in ("per_cell", "regime")):
            return current_price, "join_late_runway"
        return target_bid, ""

    def _intended_clamp_at_placement(self, entry_mode, target_bid, placement_ask):
        """[C-FEEDER FIX-3] the intended_clamp key, derived from the placement
        DECISION. Pure/testable. True iff a resting-maker bid was knowingly
        posted at ask-1 given the decision-time book (a locked or 1c-spread
        book puts the table target exactly there). The fallback_maker /
        marketable_clamp modes are NOT keyed here -- their entry_mode already
        carries the RUN-7 exemption."""
        return (entry_mode == "resting_maker"
                and target_bid == max(1, placement_ask - 1))

    def _resting_cancel_reason(self, target_bid, best_bid, best_ask):
        """Lever 3: should a resting v4 entry bid be cancelled? Returns (cancel, reason). Pure/testable.
        cancel_on_marketable (A): degenerate book OR the bid gone marketable/stale (target within
        cancel_marketable_buffer of the ask -> about to fill against a moved book = the real pick-off
        risk). A bid resting safely below a wide market is NOT cancelled (kills the churn). Legacy
        path: degenerate OR wide spread (>2c) — the MAIN-calibrated proxy that over-cancels thin books."""
        degenerate = best_bid <= 0 or best_ask >= 100
        if self.cancel_on_marketable:
            if degenerate:
                return True, "degenerate"
            if target_bid > 0 and target_bid >= (best_ask - self.cancel_marketable_buffer):
                return True, "bid_marketable_stale"
            return False, None
        if degenerate or (best_ask - best_bid) > 2:
            return True, "degenerate_or_wide_spread"
        return False, None

    def _reprice_target(self, new_target, current_ask):
        """Fix-3 (reprice-maker-only): a significant-move reprice NEVER crosses. If the
        re-evaluated target is marketable (>= ask), clamp to a resting bid one below the ask.
        Returns (price, post_only) -- post_only is ALWAYS True; the T-20m fallback is the only
        sanctioned taker entry. (Also removes a D18-class hole: a post_only=False cross here
        could instant-fill while phase stays "entry_resting" -> the match_start_buffer cleanup
        would strand it naked, since its exit-repost guard requires phase=="active".) Pure/testable."""
        if new_target >= current_ask:
            new_target = max(1, current_ask - 1)
        return new_target, True

    def _fallback_order(self, best_bid, best_ask):
        """RUN-7 + [C-JOIN-THE-BID]: the T-20m fallback now JOINS the standing bid
        (max(1, min(best_bid, best_ask-1))) rather than resting at ask-1 -- ask-1 posts ABOVE
        standing demand and gets run over (backtest: +2.6..+3.9c/attempt worse, 16,806 legs).
        fallback_maker_clamp=False keeps the atlas-baseline taker (byte-identical). Engagement is
        routed best_bid:=best_ask by the caller -> ask-1 preserved. Pure/testable."""
        if self.fallback_maker_clamp or self.maker_only_entry:
            return max(1, min(int(best_bid), int(best_ask) - 1)), True
        return best_ask, False

    def _join_target(self, best_bid, best_ask):
        """[C-JOIN-THE-BID] rest AT the standing best bid, never above it, never cross.
        max(1, min(best_bid, best_ask-1)): wide book -> best_bid; 1c book -> ask-1 (== best_bid);
        locked/crossed -> ask-1. Replaces the anchor-offset target and the ask-1 PLACEMENT clamps
        (NOT _reprice_target, the shared never-cross safety for the completion paths). Returns
        (price, post_only=True). Pure/testable. Backtest (16,806 legs, 4 cats): join beats ask-1 by
        +2.6..+3.9c/attempt; bilateral doubles EV & cuts variance; deeper/FV-conditioned casts dead."""
        return max(1, min(int(best_bid), int(best_ask) - 1)), True

    def _staircase_target(self, anchor, offset, best_ask):
        """[C-STAIRCASE SHIP-1] anchor-relative offset>=1 floor for the staircase deep-cast path.
        Reproduces abort_validation.py:58 (D = max(1, ...)): the posted bid is anchor - D with
        D >= 1, so bid <= anchor - 1 -- never shallower than 1c below anchor, even when
        ask-1 > anchor-1. never-cross (<= ask-1) and absolute floor (>= 1) preserved;
        post_only ALWAYS True.

        offset MUST be a PRE-ROUNDED integer per-knot depth. Under Path A (Ship 2) the ATP_MAIN
        caller computes it live: max(1,int(round(1+(final_target-1)*frac2(t)))) (== abort_validation.py:58,
        the SOLE rounding site). This clamp performs NO rounding/truncation. A float is REJECTED, not
        silently truncated (the 753a9d9c off-by-one: int(3.5)->3 truncates vs sim int(round(3.5))->4
        banker's-rounds; half-integers at dt=2/dt=6,frac=0.5 would post 1c shallow vs validated).

        DORMANT in 59565d5: invoked by NOTHING -- the staircase placement path that calls this is
        Ship 2. Does NOT touch _join_target (live join_trial @4553), _fallback_order, or
        _reprice_target (shared completion safety): all byte-identical. Pure/testable."""
        assert isinstance(offset, int), "_staircase_target requires pre-rounded integer offset (sim parity, abort_validation.py:58)"
        D = max(1, offset)                     # offset>=1 floor; NO live rounding (pre-rounded in CSV)
        bid = int(anchor) - D                   # anchor - offset deep cast  ->  bid <= anchor-1
        bid = min(bid, int(best_ask) - 1)       # never-cross (existing clamp style)
        return max(1, bid), True                # absolute floor + post_only

    def _frac2(self, t):
        # [C-STAIRCASE SHIP-2] held-step knot lookup COPIED BYTE-FOR-BYTE from abort_validation.py:20-22
        # (the min(c, key=lambda x: x[0]) held-step semantics are the only float-precision surface;
        # do NOT rewrite). KN/FR are the sealed walk_schedule arrays loaded at boot.
        KN, FR = self._walk_knots, self._walk_fracs
        c=[(k,f) for k,f in zip(KN,FR) if k>=t]; return min(c,key=lambda x:x[0])[1] if c else 0.0

    def _staircase_bid(self, cat, cell, anchor, time_to_start, best_bid, best_ask):
        """[C-STAIRCASE SHIP-2] ATP_MAIN staircase caller (Path A). Computes depth D LIVE from the
        SEALED inputs (range_final_ATP_MAIN.csv final_target + walk_schedule frac2 + formula) and
        posts via _staircase_target. NEVER reads CSV D@T cols (seal addendum). int(round(...)) is the
        ONE rounding site (== abort_validation.py:58). [C-STAIRCASE 4CAT] ALL 4 cats; a cat with no
        range_final surface or an absent cell -> _join_target fallback."""
        _rf = self._range_final.get(cat)
        ft = _rf.get(int(cell)) if _rf else None
        if ft is None:
            return self._join_target(best_bid, best_ask)
        D = max(1, int(round(1 + (ft - 1) * self._frac2(time_to_start / 60.0))))
        return self._staircase_target(int(anchor), int(D), int(best_ask))

    def _load_staircase(self):
        """[C-STAIRCASE SHIP-2] load SEALED Path-A inputs once at boot. D@T cols deliberately NOT read."""
        import csv as _csv, json as _json
        base = Path(__file__).resolve().parent
        sch = _json.load(open(base / "docs/policy/range_final_walk_schedule.json"))
        self._walk_knots = sch["knots_min_before_start"]; self._walk_fracs = sch["depth_fraction_at_knot"]
        # [C-STAIRCASE 4CAT] per-cat final_target dicts (was ATP_MAIN-only). Walk schedule SHARED.
        self._range_final = {}             # cat -> {cell: final_target}
        for _cat in ("ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"):
            _d = {}
            with open(base / ("docs/policy/range_final_%s.csv" % _cat), newline="") as f:
                for r in _csv.DictReader(f):
                    _d[int(r["c"])] = int(r["final_target"])
            self._range_final[_cat] = _d
        self._log("staircase_loaded", {"cats": {c: len(v) for c, v in self._range_final.items()},
                  "knots": self._walk_knots, "note": "Path A 4-cat: final_target+frac2 live; D@T cols NOT read"})

    def _queue_depth_ahead(self, book, price):
        """[C-JOIN-TRIAL] contracts resting AT our price level = the FIFO queue ahead of a join
        that lands there (price-time priority). 0 if the level is empty or the book is missing."""
        if book is None or price <= 0:
            return 0
        return int(book.bids.get(int(round(price)), 0) or 0)

    def _join_trial_resolve(self, pos, outcome, book, price, tk):
        """[C-JOIN-TRIAL] record one resolved join attempt (outcome in {fill,cancel}) with the
        queue telemetry the bid_low<=L validation could not measure, then evaluate the
        pre-registered abort bars. join_queue logging is unconditional for join legs; the abort
        gate fires ONLY under join_trial_mode (degraded first-slate trial)."""
        if pos.reference_source != "join_bid":
            return
        depth_now = self._queue_depth_ahead(book, price)
        latency = (time.time() - pos.join_post_ts) if pos.join_post_ts > 0 else -1.0
        self._log("join_queue", {
            "outcome": outcome, "depth_at_post": pos.join_depth_post, "depth_now": depth_now,
            "fill_latency_sec": round(latency, 1), "reposts": pos.join_reposts,
            "play_type": pos.play_type, "trial": pos.join_is_trial}, ticker=tk)
        if not (self.join_trial_mode and pos.join_is_trial):
            return
        self.trial_resolved += 1
        self.trial_reposts += pos.join_reposts
        if outcome == "fill":
            self.trial_fills += 1
        if self.join_trial_aborted or self.trial_resolved < JOIN_TRIAL_MIN_RESOLVED:
            return
        mean_reposts = self.trial_reposts / self.trial_resolved
        fill_rate = self.trial_fills / self.trial_resolved
        if mean_reposts > JOIN_TRIAL_ABORT_REPOSTS and fill_rate < JOIN_TRIAL_ABORT_FILLRATE:
            self.join_trial_aborted = True
            self._log("join_trial_abort", {
                "resolved": self.trial_resolved, "mean_reposts": round(mean_reposts, 2),
                "fill_rate": round(fill_rate, 3), "bar_reposts": JOIN_TRIAL_ABORT_REPOSTS,
                "bar_fillrate": JOIN_TRIAL_ABORT_FILLRATE,
                "action": "ABORT -- queue starvation confirmed; halting new join entries"})

    def _staircase_resolve(self, pos, outcome, fill_price):
        """[C-STAIRCASE SHIP-2 abort-spec] record one resolved staircase leg (fill|cancel) and trip the
        AND-gated abort: over the first STAIRCASE_MIN_RESOLVED resolved legs, halt NEW staircase entries
        iff mean(realized depth) < STAIRCASE_ABORT_DEPTH AND fill_rate < STAIRCASE_ABORT_FILLRATE. Resting
        legs continue (placement-side skip only). Mirrors join_trial_aborted. Staircase-only by reference_source."""
        if pos.reference_source != "staircase":
            return
        _cat = pos.category                                  # [C-STAIRCASE 4CAT] per-cat tally
        self.staircase_resolved[_cat] = self.staircase_resolved.get(_cat, 0) + 1
        depth = 0
        if outcome == "fill":
            self.staircase_fills[_cat] = self.staircase_fills.get(_cat, 0) + 1
            depth = max(0, int(pos.staircase_anchor) - int(fill_price))   # realized offset (anchor - fill)
            self.staircase_depth_sum[_cat] = self.staircase_depth_sum.get(_cat, 0.0) + depth
        _res = self.staircase_resolved[_cat]; _fil = self.staircase_fills.get(_cat, 0)
        self._log("staircase_walk", {
            "cat": _cat, "outcome": outcome, "resolved": _res, "fills": _fil,
            "anchor": pos.staircase_anchor, "fill_price": fill_price, "depth": depth,
            "staircase_ref": pos.staircase_ref, "cell": pos.staircase_cell})
        if self.staircase_aborted.get(_cat, False) or _res < STAIRCASE_MIN_RESOLVED:
            return
        fill_rate = _fil / _res
        mean_depth = (self.staircase_depth_sum.get(_cat, 0.0) / _fil) if _fil else 0.0
        _dbar = STAIRCASE_ABORT_DEPTH.get(_cat, STAIRCASE_ABORT_DEPTH["ATP_MAIN"])
        _frbar = STAIRCASE_ABORT_FILLRATE.get(_cat, STAIRCASE_ABORT_FILLRATE["ATP_MAIN"])
        if mean_depth < _dbar and fill_rate < _frbar:
            self.staircase_aborted[_cat] = True
            self._log("staircase_trial_abort", {
                "cat": _cat, "resolved": _res, "fill_rate": round(fill_rate, 3),
                "mean_depth": round(mean_depth, 3), "bar_fillrate": _frbar, "bar_depth": _dbar,
                "action": "ABORT -- staircase depth+fill below bars; halting new entries (THIS cat only)"})

    def _taker_spread_ok(self, bid, ask):
        """T52: True if (ask-bid) is tight enough to TAKER-cross. A fat spread
        means crossing overpays (the KESMAR fat-spread mechanism) -> block the
        cross and stay flat rather than lift a wide ask."""
        return (ask - bid) <= MAX_TAKER_SPREAD

    def identify_sides(self, event_ticker):
        tickers = list(self.event_tickers.get(event_ticker, set()))
        if len(tickers) < 2:
            return []
        sides = []
        for tk in tickers:
            book = self.books.get(tk)
            if not book or book.updated < time.time() - BOOK_STALENESS_SEC:
                continue
            sides.append((tk, book.best_bid, book.best_ask))
        if len(sides) < 2:
            return []
        sides.sort(key=lambda x: -x[1])
        leader_tk, leader_bid, _ = sides[0]
        underdog_tk, underdog_bid, _ = sides[1]
        cat = self.get_category(leader_tk)
        if not cat:
            return []
        results = []
        if leader_bid > 50:
            results.append((leader_tk, "leader", cat))
        if underdog_bid < 50 and underdog_bid > 0:
            results.append((underdog_tk, "underdog", cat))
        return results

    # ------------------------------------------------------------------
    # Check fills via REST API
    # ------------------------------------------------------------------
    def _untombstone_entry(self, tk, pos):
        """Handle entry cancellation. If unfilled, remove from processed_events
        to allow re-entry. If partially filled, keep position managed."""
        if pos.entry_qty > 0:
            # Partially filled — position is real, keep it managed
            pos.entry_order_id = ""
            pos.phase = "active"
            self._log("entry_cancel_partial", {
                "filled_qty": pos.entry_qty, "kept_position": True,
            }, ticker=tk)
            return
        # Unfilled — remove tombstone, allow re-entry
        et = pos.event_ticker
        if et and et in self.processed_events:
            self.processed_events.discard(et)
            self._save_processed()
        if tk in self.positions:
            del self.positions[tk]

    SIDECAR_INTERVALS = {
        "tennis_odds": 600,
        "betexplorer": 700,
        "fv_monitor": 400,
        "kalshi_price": 400,
    }

    def _check_sidecar_heartbeats(self):
        now = int(time.time())
        for name, expected in self.SIDECAR_INTERVALS.items():
            path = "/tmp/heartbeat_%s.json" % name
            try:
                with open(path) as f:
                    hb = json.load(f)
                age = now - hb.get("ts", 0)
                if age > expected * 2:
                    self._log("sidecar_stale", {
                        "name": name, "age_sec": age,
                        "expected_max_age": expected * 2,
                        "last_extra": {k: v for k, v in hb.items() if k not in ("ts", "name", "status")},
                    })
            except FileNotFoundError:
                self._log("sidecar_missing", {"name": name, "path": path})
            except Exception as e:
                self._log("sidecar_heartbeat_error", {"name": name, "error": str(e)})

    def _commence_time_from_book_prices(self, event_ticker):
        """Query book_prices for most recent commence_time for this event."""
        import sqlite3 as _sql
        try:
            conn = _sql.connect(str(Path(__file__).resolve().parent / "tennis.db"), timeout=5)
            cur = conn.cursor()
            cur.execute(
                "SELECT commence_time FROM book_prices WHERE event_ticker=? "
                "AND commence_time IS NOT NULL AND commence_time != '' "
                "ORDER BY polled_at DESC LIMIT 1",
                (event_ticker,))
            row = cur.fetchone()
            conn.close()
            if not row or not row[0]:
                return None
            ct = datetime.fromisoformat(row[0].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            if timedelta(hours=-6) < (ct - now) < timedelta(hours=120):
                return ct
            return None
        except Exception:
            return None

    def _kalshi_commence_time(self, event_ticker):
        """Query kalshi_price_snapshots for commence_time."""
        import sqlite3 as _sql
        try:
            conn = _sql.connect(str(Path(__file__).resolve().parent / "tennis.db"), timeout=5)
            cur = conn.cursor()
            cur.execute(
                "SELECT commence_time FROM kalshi_price_snapshots WHERE event_ticker=? "
                "AND commence_time IS NOT NULL AND commence_time != '' "
                "ORDER BY polled_at DESC LIMIT 1",
                (event_ticker,))
            row = cur.fetchone()
            conn.close()
            if not row or not row[0]:
                return None
            ct = datetime.fromisoformat(row[0].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            if timedelta(hours=-2) < (ct - now) < timedelta(hours=120):
                return ct
            return None
        except Exception:
            return None

    def _get_side_fv(self, ticker, event_ticker):
        """Return get_consensus_fv result for the side corresponding to this Kalshi ticker."""
        import sqlite3
        conn = sqlite3.connect(str(Path(__file__).resolve().parent / "tennis.db"), timeout=5)
        cur = conn.cursor()
        cur.execute(
            "SELECT player1_name, player2_name FROM book_prices WHERE event_ticker = ? ORDER BY polled_at DESC LIMIT 1",
            (event_ticker,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        p1_name, p2_name = row
        ticker_side = ticker.split("-")[-1].upper()
        p1_last3 = p1_name.split()[-1].upper()[:3]
        p2_last3 = p2_name.split()[-1].upper()[:3]
        resolved_side = None
        if ticker_side[:3] == p1_last3:
            resolved_side = "p1"
        elif ticker_side[:3] == p2_last3:
            resolved_side = "p2"
        else:
            p1_full = p1_name.split()[-1].upper()
            p2_full = p2_name.split()[-1].upper()
            if ticker_side in p1_full or p1_full.startswith(ticker_side):
                resolved_side = "p1"
            elif ticker_side in p2_full or p2_full.startswith(ticker_side):
                resolved_side = "p2"
        if resolved_side is None:
            return None
        result = get_consensus_fv(event_ticker, resolved_side)
        if result:
            result["_side"] = resolved_side
        return result

    async def _book_placement_cross_fill(self, tk, pos, resp, anchor_price):
        """D18 (TRASQU NO_EXIT, placement-side). Book a post_only=False placement cross
        (miss_fallback / marketable_taker) that filled ON PLACEMENT, and post its exit at
        source. Returns True iff a fill was booked.

        Why this is needed: the placement path stores the Position as phase="entry_resting"
        and has no instant-fill poll. A post_only=False cross can fill immediately; that fill
        never transits check_fills' entry_resting poll -- the match_start_buffer branch
        cancels the (already-filled) order and its phase=="active" guard then skips the exit,
        leaving a NAKED-held position with uncapped downside (SHEBRA-SHE, 2026-06-01).

        Mirrors the T-20m fallback path's instant-fill handler (the same TRASQU fix that path
        already has). anchor_price is the cross/limit price; a taker buy fills at <= its limit,
        so anchoring the exit on it is conservative (A53). _v4_apply_exit is HOLD-safe and
        clears stray sells before posting, so it is safe to call here."""
        _bid, _v2_status, filled, _v2_avg = parse_order_response_v2(resp)   # [C-ORDER-V2] flat create resp
        if filled <= 0 or pos.exit_order_id:
            return False
        if pos.entry_qty == 0:
            self.n_entries += 1
        pos.entry_qty = filled
        pos.entry_filled_ts = time.time()
        pos.phase = "active"
        self._log("entry_filled", {
            "fill_price": anchor_price, "posted_price": anchor_price,
            "qty": filled, "new_fills": filled, "cell": pos.cell_name,
            "direction": pos.direction, "play_type": pos.play_type,
            "kalshi_status": _v2_status, "source": "placement_instant_fill",
        }, ticker=tk)
        if pos.is_v4:
            await self._v4_apply_exit(tk, pos, anchor_price, filled)
            await self._cancel_sibling_if_paired_over_cap(tk, pos.event_ticker, anchor_price)
        self._save_v4_resting()
        return True

    async def _v4_apply_exit(self, tk, pos, fill_price, filled):
        """STEP 7. Apply the atlas exit rule for a freshly-filled v4 position
        from its entry-priced 1c cell. Two outcomes:

          rule == "hold"  -> post NO exit. Set strategy="hold"; the position is
            left net-open so Bug 4's settlement chokepoint (WS lifecycle / REST
            safety-net / BBO backstop -> process_settlement) closes it at
            settlement. (P0 #1, #4.)
          rule == "exit"  -> post a resting sell at min(fill+band_x, cap),
            sized to the filled qty, after clearing any stray sells. (P0 #4.)

        Highest-risk surface (inventory #8c, checklist P0). Bug 4 paths are NOT
        touched here -- a hold position simply never gets an exit order, and
        arrives at the same chokepoint it would have via an exit-fill."""
        pos.phase = "active"
        cell_id = self.cell_lookup(pos.category, fill_price)
        band_x, rule = self.exit_rule_for(pos.category, fill_price)
        pos.exit_cell_id = cell_id

        # Clear any stray resting sells (idempotent; fresh fill normally has none)
        if pos.exit_order_id:
            await self.cancel_order(tk, pos.exit_order_id, "v4_exit_reset")
            pos.exit_order_id = ""
        existing = await api_get(self.session, self.ak, self.pk,
            "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
        for o in (existing or {}).get("orders", []):
            if o.get("action") == "sell":
                await self.cancel_order(tk, o.get("order_id", ""), "v4_exit_reset_stray")

        if rule == "hold":
            pos.strategy = "hold"
            pos.exit_band_x = None
            self._log("hold_to_settle", {
                "cell_id": cell_id, "entry_price": fill_price,
                "regime": pos.regime_at_posting, "category": pos.category,
                "entry_mode": pos.entry_mode, "qty": filled,
                "expected_settle_note": "Bug4 chokepoint closes at settlement",
            }, ticker=tk)
            return

        # exit at +X
        pos.strategy = "exit"
        pos.exit_band_x = band_x
        exit_target = min(fill_price + band_x, EXIT_PRICE_CAP)
        pos.exit_price = exit_target
        # [C-PARTIAL-BOOKING P0v2] the exit sizes to OPEN shares, never total
        # bought: booked entry fills minus the exit-side count, CLAMPED to the
        # exchange position (never oversell -- the operator-manual-order frame
        # 2026-06-12: a total-bought-sized repost over a partially-exited
        # position would have sold 5 against 4 open).
        open_qty = filled - pos.exit_filled_qty
        try:
            pdata = await api_get(self.session, self.ak, self.pk,
                "/trade-api/v2/portfolio/positions?ticker=%s&count_filter=position"
                "&settlement_status=unsettled" % tk, self.rl)
            if pdata:
                ex_open = sum(int(float(p.get("position_fp", 0)))
                              for p in pdata.get("market_positions", []))
                if ex_open >= 0:
                    open_qty = min(open_qty, ex_open)
        except Exception:
            pass  # ledger-derived open_qty stands on a failed lookup
        if open_qty <= 0:
            self._log("exit_skip_no_open_shares", {
                "filled": filled, "exit_filled_qty": pos.exit_filled_qty,
            }, ticker=tk)
            return
        filled = open_qty
        book = self.books.get(tk)
        depth_at_target = book.asks.get(exit_target, 0) if book else 0
        # [C-FEEDER RIDE-ALONG] depth_ok semantics fixed. The old key compared
        # the single-level ask size AT our exit price -- a level we are usually
        # FIRST to quote, so it read 0/1 and "depth_ok": false on every healthy
        # exit (all 5 of last night's). The floor
        # (min_depth_for_exit_realization, gated-optima surface) is a
        # REALIZATION-LIQUIDITY proxy: ask-side size resting in the band the
        # spike must trade through, (entry, exit_target], captured before our
        # own order posts. Observational only -- never a gate.
        depth_within_band = (sum(sz for p, sz in book.asks.items()
                                 if fill_price < p <= exit_target)
                             if book else 0)

        oid, resp = await self.place_order(tk, "sell", "yes", exit_target, filled)
        if not oid:
            await asyncio.sleep(1)
            oid, resp = await self.place_order(tk, "sell", "yes", exit_target, filled)
        if not oid:
            self._log("v4_exit_fatal", {
                "exit_price": exit_target, "qty": filled,
            }, ticker=tk)
        pos.exit_order_id = oid
        self._log("v4_exit_posted", {
            "exit_price": exit_target, "band_x": band_x, "cell_id": cell_id,
            "entry_price": fill_price, "qty": filled,
            "depth_at_exit": depth_at_target,
            "depth_within_band": depth_within_band,
            "depth_floor": self.exit_depth_floor,
            "depth_ok": depth_within_band >= self.exit_depth_floor,
            "order_id": oid,
        }, ticker=tk)

    def _parse_entry_fill(self, order, pos):
        """[C-P0-RACE] Shared fill parse for an exchange order object (get-order
        poll shape). Byte-equivalent to the former inline check_fills derivation:
        average_fill_price_fp (dollars) -> x100; yes_price (cents) -> as-is;
        non-positive -> posted-price fallback. Returns (filled_qty, fill_price)."""
        filled = int(float(order.get("fill_count_fp", order.get("count_filled", 0)) or 0))
        fpr = order.get("average_fill_price_fp", order.get("yes_price", pos.entry_price / 100.0))
        if isinstance(fpr, str):
            fpr = float(fpr)
        fill_price = round(fpr * 100) if fpr < 1.5 else int(fpr)
        if fill_price <= 0:
            fill_price = pos.entry_price
        return filled, fill_price

    async def _book_v4_entry_fill(self, tk, pos, filled, fill_price, status, source=None):
        """[C-P0-RACE STEP 2] THE v4 entry-fill booking handler, extracted from the
        check_fills inline block (Gate-1 contract -- every mutation/side-effect of
        the inline version, in order):

          1. idempotency gate: books only NEW fills (filled > pos.entry_qty);
             qty-monotonic and order-scoped (each call's `filled` is that order's
             exchange fill count) -- a repeat call for the same order+count no-ops.
          2. state: entry_qty=filled, entry_filled_ts=now, phase="active";
             n_entries += 1 on first fill only.
          3. log entry_filled (same fields as the former inline emission;
             `source` key added ONLY when a non-poll site books -- the check_fills
             no-race path emits byte-identical events).
          4. _v4_apply_exit (hold-aware exit application, stray-sell clearing).
          5. _cancel_sibling_if_paired_over_cap (T50 + PART-2 completion arm).
          6. completion-bid fills: completion_fill paired event with exchange
             is_taker truth + V2/V3/V4 tripwire guards.
          7. _save_v4_resting.

        ATOMICITY (Plex Gate 3): the segment from the idempotency check through the
        state writes in step 2 contains NO await -- under asyncio's single-threaded
        cooperative scheduling no other coroutine can interleave between check and
        write. The AWAITED tail (steps 4-6) is additionally serialized per order_id
        by self._booking_inflight: exactly one concurrent caller books; others
        observe the booked state (or the inflight guard) and no-op.

        Returns True iff new fills were booked."""
        key = pos.entry_order_id or ("adopt:" + tk)
        if key in self._booking_inflight:
            return False  # a concurrent booking for this order is in its awaited tail
        # ---- await-free check->write segment (do not add awaits here) ----
        if filled <= 0 or filled <= pos.entry_qty:
            return False
        self._booking_inflight.add(key)
        try:
            new_fills = filled - pos.entry_qty
            first_fill = pos.entry_qty == 0
            pos.entry_qty = filled
            pos.entry_filled_ts = time.time()
            pos.phase = "active"
            if first_fill:
                self.n_entries += 1
            ev = {
                "fill_price": fill_price,
                "posted_price": pos.entry_price,
                "qty": filled,
                "new_fills": new_fills,
                "cell": pos.cell_name,
                "direction": pos.direction,
                "play_type": pos.play_type,
                "kalshi_status": status,
            }
            if source is not None:
                ev["source"] = source
            # [C-FV-BURST] observe-only: tag fills landing AFTER the burst latch
            # (ride-live / completion / adoption) from the stored snapshot. Sets
            # two never-read Position fields + two log keys; no control-flow,
            # filled, fill_price, idempotency, exit or sibling-cancel effect. (Pre-
            # burst fills are tagged by _fv_burst_snapshot's fv_burst_anchor line.)
            _fvb = self._fv_burst.get(tk)
            if _fvb is not None and _fvb.get("mid") is not None:
                pos.fv_at_burst = _fvb["mid"]
                pos.entry_minus_fv_burst = fill_price - _fvb["mid"]
                ev["fv_at_burst"] = _fvb["mid"]
                ev["entry_minus_fv_burst"] = pos.entry_minus_fv_burst
            # [C-FEEDER FIX-4] B22 ledger attribution at the anchor that
            # matters -- the FILL: cell/band where the market actually filled
            # us, plus wave-1 table membership of that band (the would-have-
            # been gate), for the band retrospective. Exit attribution rides
            # the normal v4_exit_posted/exit_filled events.
            if pos.play_type == "v4_engagement_join":
                tts_f = (pos.match_start_ts - time.time()) if pos.match_start_ts > 0 else -1.0
                bucket_f = self._engagement_bucket(tts_f) if tts_f > 0 else None
                band_f = self.regime_lookup(pos.category, fill_price)
                ev.update({
                    "cell_at_fill": self.cell_lookup(pos.category, fill_price),
                    "band_at_fill": band_f,
                    "bucket_at_fill": bucket_f,
                    "band_on_table": (bucket_f is not None and
                                      (pos.category, bucket_f, band_f) in self.engagement_cells),
                    "posted_level": pos.target_price,
                })
            self._log("entry_filled", ev, ticker=tk)
            self._join_trial_resolve(pos, "fill", self.books.get(tk), fill_price, tk)
            self._staircase_resolve(pos, "fill", fill_price)
            # ---- awaited tail (serialized per order_id by _booking_inflight) ----
            if pos.is_v4:
                await self._v4_apply_exit(tk, pos, fill_price, filled)
                # T50 backstop: this side just filled -> cancel the sibling's
                # resting bid if the pair would exceed cap.
                # (PART-2: same handler also runs the completion arm.)
                await self._cancel_sibling_if_paired_over_cap(tk, pos.event_ticker, fill_price)
                # PART-2 item 7: a COMPLETION bid filling is logged as its own
                # paired event (separate from the leg fill), with exchange
                # is_taker truth (never placement intent).
                if pos.entry_mode == "completion_reprice":
                    is_taker = await self._fill_is_taker(tk, pos.entry_order_id)
                    self._log("completion_fill", {
                        "event": pos.event_ticker, "fill_price": fill_price,
                        "qty": filled, "new_fills": new_fills,
                        "s0": pos.completion_s0, "x": pos.completion_x,
                        "s1_posted": pos.entry_price,
                        "leg1_basis": pos.completion_leg1_basis,
                        "time_since_reprice": round(
                            time.time() - pos.completion_reprice_ts, 1),
                        "is_taker": is_taker}, ticker=tk)
                    # [C-TRIPWIRE] V2/V3/V4 at the booking site: the filled
                    # position keeps its normal exit; the MECHANISM dies.
                    viol = self._completion_fill_guards(pos, fill_price, is_taker)
                    if viol is not None:
                        await self._completion_tripwire(viol[0], viol[1], tk=tk)
            self._save_v4_resting()
            return True
        finally:
            self._booking_inflight.discard(key)

    async def _cancel_entry_and_resolve(self, tk, pos, label, source):
        """[C-P0-RACE STEP 3] Cancel a resting v4 entry bid and resolve the outcome
        against EXCHANGE truth before any state is dropped. STEP-0 finding: our
        DELETE plumbing (live _real_api_delete AND paper handle_delete) returns only
        an HTTP-status boolean -- the response body (which on a 200 carries the
        canceled order object incl. fill counts) is discarded, and the
        already-filled failure case carries no fill info at all. So ALL three
        branches resolve from one get-order poll after the cancel attempt:

          filled > booked (regardless of cancel ok) -> book via _book_v4_entry_fill
            (full OR partial fill; partial+cancelled-remainder books the filled qty
            and the exit is sized to it)                       -> "booked"
          no new fill + cancel confirmed (ok or status canceled) -> caller deletes
            per its existing discipline                         -> "cancelled"
          poll unavailable (transient API failure)              -> "unresolved":
            caller keeps the position tracked and retries next cycle -- NEVER
            delete on ambiguity (deleting an unconfirmed order is the exact bug
            this exists to fix).
        """
        oid = pos.entry_order_id
        if not oid:
            return "cancelled"  # nothing resting exchange-side; caller's discipline applies
        ok = await self.cancel_order(tk, oid, label)
        order = None
        for attempt in (0, 1):
            data = await api_get(self.session, self.ak, self.pk,
                "/trade-api/v2/portfolio/orders/%s" % oid, self.rl)
            if data:
                order = data.get("order", data)
                break
            if attempt == 0:
                await asyncio.sleep(0.5)
        if order is None:
            self._log("cancel_resolve_unresolved", {
                "label": label, "order_id": oid, "cancel_ok": ok}, ticker=tk)
            return "unresolved"
        filled, fill_price = self._parse_entry_fill(order, pos)
        if filled > pos.entry_qty:
            self._log("cancel_fill_race", {
                "label": label, "order_id": oid, "cancel_ok": ok,
                "filled": filled, "fill_price": fill_price,
                "status": order.get("status", "")}, ticker=tk)
            await self._book_v4_entry_fill(tk, pos, filled, fill_price,
                                           order.get("status", ""), source=source)
            return "booked"
        self._join_trial_resolve(pos, "cancel", self.books.get(tk),
                                 pos.walk_ref or pos.target_price, tk)
        self._staircase_resolve(pos, "cancel", pos.staircase_ref or pos.target_price)
        return "cancelled"

    async def check_fills(self):
        """Poll Kalshi for fill status on all active orders."""
        for tk, pos in list(self.positions.items()):
            if pos.settled:
                continue

            # V4.2 migration: backfill match_start_ts from schedule
            if pos.match_start_ts == 0 and pos.event_ticker:
                st = self.event_start_time.get(pos.event_ticker, 0)
                if st > 0:
                    pos.match_start_ts = st

            # Check entry order fill
            if pos.phase == "entry_resting" and pos.entry_order_id:
                now = time.time()
                # PART-2 item 5: completion bids are buffer-exempt (ride to T-0 under
                # _v4_manage_completion); fresh entry bids keep the T-15 cancel.
                if (pos.match_start_ts > 0 and now > pos.match_start_ts - ENTRY_BUFFER_SEC
                        and not self._completion_buffer_exempt(pos)
                        # [C-RIDE-LIVE override #6] flag on -> the T-15 buffer
                        # exempts resting maker entries; the poll below keeps
                        # booking fills (incl. partials) into play
                        and not getattr(self, "premarket_bids_ride_live", False)):
                    # [C-P0-RACE site 3] resolve the cancel against exchange truth:
                    # a fill since the last poll books instead of being deleted.
                    res = await self._cancel_entry_and_resolve(
                        tk, pos, "match_start_buffer", "buffer_cancel_race")
                    if res == "cancelled":
                        self._log("entry_cancelled", {
                            "reason": "match_start_buffer",
                            "match_start": pos.match_start_ts,
                            "waited_min": round((now - pos.entry_posted_ts) / 60),
                        }, ticker=tk)
                        self._untombstone_entry(tk, pos)
                    # "booked": filled in the race window -- booked with its exit
                    # posted; nothing to delete. "unresolved": keep the leg tracked;
                    # this branch re-fires on the next poll pass.
                    # DEFENSE-IN-DEPTH (TRASQU NO_EXIT fix): if cleanup kept a
                    # filled position, ensure an exit exists. _v4_apply_exit is a
                    # no-op for HOLD cells and clears stray sells before posting,
                    # so this is safe to call whenever no exit order is recorded.
                    kept = self.positions.get(tk)
                    if (kept is not None and kept.is_v4 and kept.phase == "active"
                            and kept.entry_qty > 0 and not kept.exit_order_id):
                        self._log("exit_repost_on_cleanup", {
                            "filled_qty": kept.entry_qty,
                            "entry_price": kept.entry_price,
                        }, ticker=tk)
                        await self._v4_apply_exit(tk, kept, kept.entry_price, kept.entry_qty)
                        self._save_v4_resting()
                    continue

                path = "/trade-api/v2/portfolio/orders/%s" % pos.entry_order_id
                data = await api_get(self.session, self.ak, self.pk, path, self.rl)
                if not data:
                    continue
                order = data.get("order", data)
                status = order.get("status", "")
                filled = int(float(order.get("fill_count_fp", order.get("count_filled", 0)) or 0))

                if filled > 0 and filled > pos.entry_qty:
                    fill_price_raw = order.get("average_fill_price_fp",
                                               order.get("yes_price", pos.entry_price / 100.0))
                    if isinstance(fill_price_raw, str):
                        fill_price_raw = float(fill_price_raw)
                    fill_price = round(fill_price_raw * 100) if fill_price_raw < 1.5 else int(fill_price_raw)
                    if fill_price <= 0:
                        fill_price = pos.entry_price

                    # [C-P0-RACE STEP 2] v4 booking extracted to _book_v4_entry_fill
                    # (Gate-1 contract: state writes, entry_filled emission, exit
                    # application, T50/completion arm, completion_fill + tripwire
                    # guards, state save -- all byte-equivalent for this no-race
                    # path; no `source` key is added here).
                    if pos.is_v4:
                        await self._book_v4_entry_fill(tk, pos, filled, fill_price, status)
                        continue

                    new_fills = filled - pos.entry_qty
                    first_fill = pos.entry_qty == 0
                    pos.entry_qty = filled
                    pos.entry_filled_ts = time.time()
                    pos.phase = "active"
                    if first_fill:
                        self.n_entries += 1

                    self._log("entry_filled", {
                        "fill_price": fill_price,
                        "posted_price": pos.entry_price,
                        "qty": filled,
                        "new_fills": new_fills,
                        "cell": pos.cell_name,
                        "direction": pos.direction,
                        "play_type": pos.play_type,
                        "kalshi_status": status,
                    }, ticker=tk)

                    # Re-classify cell based on fill_price (may differ from anchor)
                    old_cell = pos.cell_name
                    old_exit_cents = pos.cell_cfg.get("exit_cents", 0) if pos.cell_cfg else 0
                    fill_cell, fill_cell_cfg = self._legacy_cell_lookup(pos.category, pos.direction, fill_price)
                    if fill_cell != old_cell:
                        if fill_cell_cfg is None:
                            fill_cell_cfg = {"exit_cents": 15, "strategy": pos.cell_cfg.get("strategy", "noDCA")}
                            self._log("cell_drift_to_inactive", {
                                "old_cell": old_cell, "new_cell": fill_cell,
                                "anchor_price": pos.entry_price, "fill_price": fill_price,
                                "drift_cents": pos.entry_price - fill_price,
                                "old_exit_cents": old_exit_cents, "new_exit_cents": 15,
                                "direction": pos.direction,
                            }, ticker=tk)
                        else:
                            self._log("cell_reclassified", {
                                "old_cell": old_cell, "new_cell": fill_cell,
                                "anchor_price": pos.entry_price, "fill_price": fill_price,
                                "drift_cents": pos.entry_price - fill_price,
                                "old_exit_cents": old_exit_cents,
                                "new_exit_cents": fill_cell_cfg["exit_cents"],
                                "direction": pos.direction,
                            }, ticker=tk)
                        pos.cell_name = fill_cell
                        pos.cell_cfg = fill_cell_cfg

                    # Cancel ALL existing exit sells before posting new ones
                    if pos.exit_order_id:
                        await self.cancel_order(tk, pos.exit_order_id, "exit_consolidate")
                    if pos.cell_exit_order_id:
                        await self.cancel_order(tk, pos.cell_exit_order_id, "exit_consolidate_cell")
                    existing_orders = await api_get(self.session, self.ak, self.pk,
                        "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
                    if existing_orders:
                        for old_sell in existing_orders.get("orders", []):
                            if old_sell.get("action") == "sell":
                                old_oid = old_sell.get("order_id", "")
                                if old_oid and old_oid not in (pos.exit_order_id, pos.cell_exit_order_id):
                                    await self.cancel_order(tk, old_oid, "exit_consolidate_extra")

                    if pos.play_type == "B_convergence" and pos.layered_exit_price > 0:
                        # Play 4: layered exits — 9ct at convergence, rest at cell scalp
                        conv_exit_price = pos.layered_exit_price
                        cell_exit_price = min(fill_price + pos.cell_cfg["exit_cents"], EXIT_PRICE_CAP)

                        conv_qty = min(9, filled)
                        cell_qty = filled - conv_qty

                        if conv_qty > 0:
                            oid_conv, _ = await self.place_order(tk, "sell", "yes", conv_exit_price, conv_qty)
                            pos.exit_order_id = oid_conv
                            pos.exit_price = conv_exit_price
                            self._log("exit_posted_convergence", {
                                "exit_price": conv_exit_price, "qty": conv_qty,
                                "order_id": oid_conv,
                            }, ticker=tk)

                        if cell_qty > 0:
                            oid_cell, _ = await self.place_order(tk, "sell", "yes", cell_exit_price, cell_qty)
                            pos.cell_exit_order_id = oid_cell
                            pos.cell_exit_price = cell_exit_price
                            self._log("exit_posted_cell_scalp", {
                                "exit_price": cell_exit_price, "qty": cell_qty,
                                "order_id": oid_cell,
                            }, ticker=tk)

                    else:
                        # Play 3 / Play 1: standard single exit
                        exit_price = min(fill_price + pos.cell_cfg["exit_cents"], EXIT_PRICE_CAP)
                        pos.exit_price = exit_price

                        sell_qty = filled
                        oid, resp = await self.place_order(tk, "sell", "yes", exit_price, sell_qty)
                        if not oid:
                            self._log("exit_retry", {"reason": "first attempt failed"}, ticker=tk)
                            await asyncio.sleep(1)
                            oid, resp = await self.place_order(tk, "sell", "yes", exit_price, sell_qty)
                        if not oid:
                            self._log("exit_fatal", {
                                "error": "exit sell failed after retry",
                                "exit_price": exit_price, "qty": sell_qty,
                            }, ticker=tk)
                        pos.exit_order_id = oid
                        self._log("exit_posted", {
                            "exit_price": exit_price,
                            "qty": sell_qty, "total_position": filled,
                            "based_on_fill": fill_price,
                            "play_type": pos.play_type,
                            "order_id": oid,
                            "consolidated": True,
                        }, ticker=tk)

                    # Place DCA if applicable (only on first fill, guard against double-post)
                    if first_fill and not pos.dca_order_id and pos.cell_cfg.get("strategy") == "DCA-A":
                        dca_trigger = pos.cell_cfg.get("dca_trigger_cents", 0)
                        dca_price = fill_price - dca_trigger
                        if dca_price >= self.dca_fill_floor:
                            pos.dca_price = dca_price
                            # FIX 2: DCA qty = min(5, filled_qty)
                            dca_qty = min(self.dca_size, filled)
                            dca_oid, dresp = await self.place_order(tk, "buy", "yes", dca_price, dca_qty)
                            if not dca_oid:
                                self._log("dca_retry", {"reason": "first attempt failed"}, ticker=tk)
                                await asyncio.sleep(1)
                                dca_oid, dresp = await self.place_order(tk, "buy", "yes", dca_price, dca_qty)
                            if not dca_oid:
                                self._log("dca_fatal", {
                                    "error": "DCA buy failed after retry",
                                    "dca_price": dca_price, "qty": dca_qty,
                                }, ticker=tk)
                            pos.dca_order_id = dca_oid
                            self._log("dca_posted", {
                                "dca_price": dca_price,
                                "qty": dca_qty, "position_qty": filled,
                                "trigger_cents": dca_trigger,
                                "based_on_fill": fill_price,
                                "order_id": dca_oid,
                            }, ticker=tk)
                        else:
                            self._log("dca_skipped", {
                                "reason": "below_floor",
                                "would_be": dca_price,
                                "floor": self.dca_fill_floor,
                            }, ticker=tk)

            # [C-PARTIAL-BOOKING P0v2] entry order with unfilled quantity is
            # polled while NON-TERMINAL regardless of phase. The old scope
            # (phase == "entry_resting" only) is THE defect: the first partial
            # flipped phase to "active" and increments 2..N were never polled
            # (NAETAN-TAN: booked 1, exchange filled 5, 4 shares naked).
            # Booking flows through the idempotent _book_v4_entry_fill (books
            # the delta); _v4_apply_exit re-sizes the exit to OPEN shares.
            if (pos.is_v4 and pos.phase == "active" and pos.entry_order_id
                    and not pos.entry_order_done):
                path = "/trade-api/v2/portfolio/orders/%s" % pos.entry_order_id
                data = await api_get(self.session, self.ak, self.pk, path, self.rl)
                if data:
                    order = data.get("order", data)
                    status = order.get("status", "")
                    filled, fill_price = self._parse_entry_fill(order, pos)
                    if filled > pos.entry_qty:
                        await self._book_v4_entry_fill(
                            tk, pos, filled, fill_price, status,
                            source="active_partial_poll")
                    if status in ("executed", "canceled") and filled <= pos.entry_qty:
                        pos.entry_order_done = True

            # Check exit order fill
            # [C-PARTIAL-BOOKING P0v2] exit_filled is now a COUNT
            # (exit_filled_qty); the bool means COMPLETE only. A partial exit
            # books its increment; the remainder order stays managed and is
            # never cancelled while backed by open shares (the only path that
            # replaces it -- _v4_apply_exit on a new entry increment -- is an
            # atomic cancel-and-repost sized to open, never both resting).
            if pos.phase == "active" and pos.exit_order_id and not pos.exit_filled:
                path = "/trade-api/v2/portfolio/orders/%s" % pos.exit_order_id
                data = await api_get(self.session, self.ak, self.pk, path, self.rl)
                if data:
                    order = data.get("order", data)
                    status = order.get("status", "")
                    filled = int(float(order.get("fill_count_fp", order.get("count_filled", 0)) or 0))
                    if filled > pos.exit_filled_qty:
                        new_exit_fills = filled - pos.exit_filled_qty
                        pos.exit_filled_qty = filled
                        complete = (status == "executed"
                                    or pos.exit_filled_qty >= pos.entry_qty)
                        inc_pnl = (pos.exit_price - pos.entry_price) * new_exit_fills
                        pos.pnl_cents += inc_pnl
                        if pos.dca_qty > 0 and complete:
                            pos.pnl_cents += (pos.exit_price - pos.dca_price) * pos.dca_qty
                        pnl = pos.pnl_cents
                        self._log("exit_filled", {
                            "exit_price": pos.exit_price,
                            "entry_price": pos.entry_price,
                            "qty": pos.exit_filled_qty,
                            "new_fills": new_exit_fills,
                            "complete": complete,
                            "pnl_cents": pnl,
                            "pnl_dollars": pnl / 100.0,
                            "had_dca": pos.dca_qty > 0,
                        }, ticker=tk)
                        if not complete:
                            continue  # remainder stays managed; nothing closes
                        if (pos.exit_filled_qty < pos.entry_qty
                                and pos.is_v4):
                            # exit order terminal but open shares remain
                            # (TAN-shape history): re-cover the remainder via
                            # the open-shares-sized exit path.
                            self._log("exit_partial_remainder", {
                                "exit_filled_qty": pos.exit_filled_qty,
                                "entry_qty": pos.entry_qty,
                                "open_shares": pos.entry_qty - pos.exit_filled_qty,
                            }, ticker=tk)
                            pos.exit_order_id = ""
                            await self._v4_apply_exit(tk, pos, pos.entry_price,
                                                      pos.entry_qty)
                            continue
                        pos.exit_filled = True
                        pos.settled = True
                        pos.phase = "settled"
                        self.n_exits += 1
                        # Classify: scalp (pregame exit) vs settlement-adjacent
                        if pos.match_start_ts > 0 and time.time() < pos.match_start_ts:
                            hrs_before = (pos.match_start_ts - time.time()) / 3600
                            self._log("scalp_filled", {
                                "entry_price": pos.entry_price,
                                "exit_price": pos.exit_price,
                                "profit_cents": pos.exit_price - pos.entry_price,
                                "hours_before_commence": round(hrs_before, 2),
                                "play_type": pos.play_type,
                            }, ticker=tk)
                        # FIX 3: Cancel ALL resting buys on this ticker (DCA + any extras)
                        cleanup = await api_get(self.session, self.ak, self.pk,
                            "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
                        for co in (cleanup or {}).get("orders", []):
                            if co.get("action") == "buy":
                                await self.cancel_order(tk, co.get("order_id", ""), "exit_cleanup_dca")

            # Check DCA order fill
            if pos.phase == "active" and pos.dca_order_id and not pos.dca_filled and not pos.exit_filled:
                path = "/trade-api/v2/portfolio/orders/%s" % pos.dca_order_id
                data = await api_get(self.session, self.ak, self.pk, path, self.rl)
                if data:
                    order = data.get("order", data)
                    filled = int(float(order.get("fill_count_fp", order.get("count_filled", 0)) or 0))
                    if filled > 0 and not pos.dca_filled:
                        pos.dca_filled = True
                        pos.dca_qty = filled
                        self.n_dcas += 1
                        self._log("dca_filled", {
                            "dca_price": pos.dca_price,
                            "qty": filled,
                            "entry_price": pos.entry_price,
                            "exit_stays_at": pos.exit_price,
                        }, ticker=tk)

    # ------------------------------------------------------------------
    # Detect settlement via BBO
    # ------------------------------------------------------------------
    async def poll_settlements_rest(self):
        """Bug 4 §6.3: catch any settlements missed via WS. Idempotent --
        process_settlement short-circuits on pos.settled. LIVE MODE ONLY --
        never called when _PAPER_API is set (defensive guard at top in case a
        caller forgets the cadence gate; the real-account settlement history
        would otherwise falsely settle paper positions)."""
        if _PAPER_API is not None:
            return  # paper mode: WS lifecycle is the only settlement source
        min_ts = getattr(self, "_last_settlement_min_ts", 0) or (time.time() - 86400)
        path = "/trade-api/v2/portfolio/settlements?min_ts=%d&limit=100" % int(min_ts)
        data = await api_get(self.session, self.ak, self.pk, path, self.rl)
        for s in (data or {}).get("settlements", []):
            # market_result -> integer cents, normalized at the call site (decision c).
            result = s.get("market_result", "")
            if result == "yes":
                settle_val_cents = 100
            elif result == "no":
                settle_val_cents = 0
            elif result == "scalar":
                settle_val_cents = max(0, min(100, int(s.get("value") or 0)))
            elif result == "void":
                # decision b: skip + log, manual reconciliation. No auto-settle.
                self._log("settlement_void_manual",
                          {"source": "rest_poll"}, ticker=s.get("ticker"))
                continue
            else:
                self._log("rest_settlement_unknown_result",
                          {"result": result, "ticker": s.get("ticker")})
                continue
            # settled_time is RFC3339, not epoch -> parse.
            settled_time_str = s.get("settled_time", "")
            try:
                settled_ts = datetime.fromisoformat(
                    settled_time_str.replace("Z", "+00:00")).timestamp()
            except (TypeError, ValueError, AttributeError):
                settled_ts = time.time()
            self.process_settlement(
                ticker=s.get("ticker", ""),
                settle_val_cents=settle_val_cents,
                settled_ts=settled_ts,
                source="rest_poll",
            )
        self._last_settlement_min_ts = time.time() - 60  # 60s overlap to avoid edge gaps

    def process_settlement(self, ticker, settle_val_cents, settled_ts, source):
        """Bug 4 §6.4: single chokepoint for all three settlement sources
        (WS, REST, BBO). Routes paper vs live based on module-level _PAPER_API.
        settle_val_cents is integer cents 0-100, already normalized at the call
        site (decision c removed the central _normalize_settle_value)."""
        settle_val = max(0, min(100, int(settle_val_cents)))  # defensive clamp only

        if _PAPER_API is not None:
            # Paper mode: mutate PaperPosition, emit paper_settled
            ppos = _PAPER_API.paper_positions.get(ticker)
            if not ppos or ppos.settled:
                return  # idempotent
            ppos.settled = True
            ppos.settlement_price = settle_val
            ppos.last_event_ts = settled_ts

            # Realized P&L at settlement -- full double-entry form (v3 fix).
            # ASSIGNMENT (not +=) because try_fill only books realized_pnl_cents
            # when net_qty hits zero; a partial-exit position reaching settlement
            # with net_qty > 0 still has realized_pnl_cents == 0 here, so the
            # final P&L must be derived from the totals:
            #   total_revenue_cents already accounts for all prior partial sells
            #   settle_val * net_qty is the payout on remaining unsold contracts
            #   total_cost_cents is everything paid in
            ppos.realized_pnl_cents = (
                ppos.total_revenue_cents
                - ppos.total_cost_cents
                + settle_val * ppos.net_qty
            )

            # Silent short-circuit: mark self.positions mirror as settled so
            # check_settlements stops re-iterating on subsequent cycles.
            # No event emitted -- paper_settled (below) is the source of truth.
            if ticker in self.positions:
                self.positions[ticker].settled = True
                self.positions[ticker].phase = "settled"

            _PAPER_API._emit("paper_settled", {
                "settle_price": settle_val,
                "settle_source": source,
                "settled_ts": settled_ts,
                "qty": ppos.qty,
                "sold_qty": ppos.sold_qty,
                "net_qty_at_settlement": ppos.net_qty,
                "avg_entry_price": ppos.avg_price,
                "realized_pnl_cents": ppos.realized_pnl_cents,
            }, ticker=ticker)

            # Cleanup: cancel resting paper orders via dispatch (handle_delete -> paper)
            for oid in list(ppos.open_buy_orders) + list(ppos.open_sell_orders):
                asyncio.create_task(self.cancel_order(ticker, oid, "settlement_cleanup"))
            return

        # ---- Live mode ----
        pos = self.positions.get(ticker)
        if not pos or pos.settled:
            return  # idempotent
        if pos.phase not in ("active", "entry_pending"):
            self._log("settlement_unexpected_phase", {
                "phase": pos.phase, "source": source,
            }, ticker=ticker)

        # [C-PARTIAL-BOOKING P0v2] settle only the shares still OPEN: a partial
        # exit already realized (exit - entry) on exit_filled_qty shares; those
        # must not be re-priced at settlement (double-count). pnl accumulates
        # on top of any partial-exit pnl already booked into pos.pnl_cents.
        settled_qty = max(pos.entry_qty - pos.exit_filled_qty, 0)
        pnl = (settle_val - pos.entry_price) * settled_qty
        if pos.dca_qty > 0:
            pnl += (settle_val - pos.dca_price) * pos.dca_qty
        pnl += pos.pnl_cents  # partial-exit increments already realized
        pos.pnl_cents = pnl
        pos.settled = True
        pos.phase = "settled"
        self.n_settlements += 1

        self._log("settled", {
            "settle": "WIN" if settle_val >= 50 else "LOSS",
            "settle_price": settle_val,
            "settle_source": source,             # ws_lifecycle | rest_poll | bbo_threshold_*
            "settled_ts": settled_ts,
            "pnl_cents": pnl,
            "pnl_dollars": pnl / 100.0,
            "entry_price": pos.entry_price,
            "had_dca": pos.dca_qty > 0,
            # [C-PARTIAL-BOOKING P0v2] partial-exit history visibility
            "settled_qty": settled_qty,
            "exit_filled_qty": pos.exit_filled_qty,
        }, ticker=ticker)

        # Cleanup: cancel any resting orders for this ticker
        if pos.exit_order_id:
            asyncio.create_task(self.cancel_order(ticker, pos.exit_order_id, "settlement_cleanup"))
        if pos.dca_order_id:
            asyncio.create_task(self.cancel_order(ticker, pos.dca_order_id, "settlement_cleanup"))
        if pos.cell_exit_order_id:
            asyncio.create_task(self.cancel_order(ticker, pos.cell_exit_order_id, "settlement_cleanup"))

    def check_settlements(self):
        """Bug 4 §6.5: BBO threshold backstop. Iterates the appropriate position
        dict based on _PAPER_API and routes via process_settlement (which
        dispatches paper/live). Passes literal cents (yes=100, no=0).

        SAFETY GATE: disable_bbo_threshold_settlement makes this a no-op so the BBO
        price heuristic is NEVER a settlement source -- a price touching 98/2 mid-match
        round-trips and is NOT settlement; settling on it cancels the resting exit early
        (settlement_cleanup at process_settlement). Real settlement still flows from
        ws_lifecycle / rest_poll (exchange truth, unchanged). Default False = byte-identical."""
        if self.disable_bbo_threshold_settlement:
            return
        if _PAPER_API is not None:
            # Paper mode: iterate paper_positions
            for tk, ppos in list(_PAPER_API.paper_positions.items()):
                if ppos.settled or ppos.net_qty <= 0:
                    continue
                book = self.books.get(tk)
                if not book:
                    continue
                if book.best_bid >= 98:
                    self.process_settlement(tk, 100, time.time(), source="bbo_threshold_yes")
                elif book.best_ask <= 2:
                    self.process_settlement(tk, 0, time.time(), source="bbo_threshold_no")
            return

        # Live mode: iterate self.positions (current behavior)
        for tk, pos in list(self.positions.items()):
            if pos.settled or pos.phase != "active":
                continue
            book = self.books.get(tk)
            if not book:
                continue
            if book.best_bid >= 98:
                self.process_settlement(tk, 100, time.time(), source="bbo_threshold_yes")
            elif book.best_ask <= 2:
                self.process_settlement(tk, 0, time.time(), source="bbo_threshold_no")

    # ------------------------------------------------------------------
    # Routing: SCHEDULE-BASED entry trigger + cell assignment at post time
    # ------------------------------------------------------------------
    def get_market_price(self, ticker, max_last_trade_age_sec=1800):
        book = self.books.get(ticker)
        if not book:
            return None, 'none'
        now = time.time()
        mid = (book.best_bid + book.best_ask) / 2.0 if book.best_bid > 0 and book.best_ask < 100 else 0
        if book.last_trade_price > 0 and book.last_trade_ts > 0:
            age = now - book.last_trade_ts
            if age < max_last_trade_age_sec:
                if mid > 0 and abs(book.last_trade_price - mid) > 2:
                    self._log('price_signal', {
                        'source': 'last_traded', 'price': book.last_trade_price,
                        'mid': round(mid, 1), 'last_traded_age_sec': round(age),
                        'divergence_cents': round(abs(book.last_trade_price - mid), 1),
                    }, ticker=ticker)
                return book.last_trade_price, 'last_traded'
            else:
                if mid > 0:
                    self._log('price_signal', {
                        'source': 'mid_fallback', 'reason': 'last_traded_stale',
                        'stale_price': book.last_trade_price,
                        'stale_age_sec': round(age), 'mid': round(mid, 1),
                    }, ticker=ticker)
        if mid > 0:
            return mid, 'mid'
        return None, 'none'

    def _resolve_anchor(self, tk, et):
        """Resolve anchor price via priority chain: FV aggregate > Kalshi mid > Kalshi last-traded."""
        book = self.books.get(tk)

        # Priority A: FV aggregate (>=2 sources, age < 600s)
        side_fv = self._get_side_fv(tk, et)
        if side_fv and side_fv.get("fv_cents") and side_fv.get("num_books", 0) >= 2:
            age = side_fv.get("age_sec", 9999)
            if age < 600:
                return side_fv["fv_cents"], "fv_aggregate", side_fv

        # Priority B: Kalshi mid (spread <= 1c, valid bids)
        if book and book.best_bid > 0 and book.best_ask < 100:
            spread = book.best_ask - book.best_bid
            if spread <= 1:
                mid = (book.best_bid + book.best_ask) / 2.0
                return mid, "kalshi_mid", None

        # Priority C: Kalshi last-traded (age < 900s, spread <= 2c)
        if book and book.last_trade_price > 0 and book.last_trade_ts > 0:
            trade_age = time.time() - book.last_trade_ts
            if trade_age < 900 and book.best_bid > 0 and book.best_ask < 100:
                spread = book.best_ask - book.best_bid
                if spread <= 2:
                    return book.last_trade_price, "kalshi_last_traded", None

        # Priority D: FV with single source (spread <= 2c gate)
        if side_fv and side_fv.get("fv_cents") and side_fv.get("age_sec", 9999) < 1800:
            if book and book.best_bid > 0 and book.best_ask < 100:
                spread_d = book.best_ask - book.best_bid
                if spread_d <= 2:
                    return side_fv["fv_cents"], "fv_single", side_fv
                else:
                    self._log("fv_single_spread_gate", {"spread": spread_d, "fv_cents": side_fv["fv_cents"]}, ticker=tk)
            # No book or degenerate → skip fv_single

        return None, "no_anchor", None

    def round5_detector_fire(self, ticker, current_ask, target_bid):
        # TODO: Implement the 2-of-4 composite per bid_laying_policy_v1.md Section 5
        # (volume burst + bilateral taker flow + BBO velocity + distortion spike).
        # When it fires AND current_ask <= target_bid + 5c, cross immediately
        # (Round-6 Stage-3 velocity override); when it fires AND ask > target+5c,
        # the spread is pathological -> hold (do NOT cross).
        # Currently stubbed False -- the static placement is never overridden.
        # Reusable components for the real build (per live_v3_v4_inventory #6b):
        #   volume-burst    -> VolumeTracker rolling counts
        #   bilateral taker -> taker_side mix (book.last_trade_side)
        #   BBO velocity    -> tennis_stb.py capture_depth_snapshot deltas
        #   distortion      -> arb_executor_ws.py ~628 combined yes+no > $1
        # Follow-up patch (production week 1).
        return False

    async def routing_tick(self):
        """Periodic backstop sweep over all events. Placement is now primarily
        event-driven (on_bbo_update, one event per BBO message); this slow sweep
        runs on a 60s main-loop cadence -- OFF the 1s hot path -- only to catch
        legs whose placement_minute opens while their book is quiet (no BBO
        update to trigger on_bbo_update). Per-event reentrancy is guarded inside
        _route_event so the sweep and on_bbo_update never double-place."""
        now = time.time()
        for et, tickers in list(self.event_tickers.items()):
            # Yield after every event so a long sweep never blocks the loop /
            # WS keepalive. No delay -- sleep(0) yields control only.
            await asyncio.sleep(0)
            # PART-2: T-240 boundary crossing with an already-fresh print -- the
            # window-open reference becomes available by TIME passing, not only by a
            # new print arriving (apply_trade covers that). Flag-gated no-op when off.
            if self.completion_reprice:
                for tk in tickers:
                    self._maybe_set_window_open(tk, now)
            # [C-FV-BURST RE-GATE] observe-only FV snapshot at the real-start burst,
            # decoupled from the _is_match_live latch (which fires only via the
            # resting-bid path -> misses both-filled events). Runs in the routing
            # SWEEP (iterates ALL events in event_tickers) BEFORE _route_event's
            # processed_events skip, so processed / both-filled events snapshot too.
            # Fire-once per event; only for events we hold a leg in. Reads tape/books;
            # writes ONLY self._fv_burst(_done) + the fv_burst_anchor log. Touches NO
            # _events_live / _is_match_live / _route_event / orders / cancels / timing.
            if et not in self._fv_burst_done and any(t in self.positions for t in tickers):
                try:
                    if self._fv_burst_ready(et, now):
                        self._fv_burst_snapshot(et, now)
                        self._fv_burst_done.add(et)
                except Exception:
                    pass
            await self._route_event(et, tickers, now)

    async def _route_event(self, et, tickers, now):
        """Route ONE event (both legs) to v4 bid-laying placement. Invoked from
        on_bbo_update (per-ticker hot path) and routing_tick (periodic backstop).
        Bounded to a single event so the loop is never blocked across the full
        ticker universe. Logic is byte-identical to the pre-restructure per-event
        body -- only the invocation pattern changed. The reentrancy guard
        serializes the two callers so they cannot double-place the same event."""
        if et in self._event_routing:
            return
        self._event_routing.add(et)
        try:
            if et in self.processed_events:
                return

            start_ts = self.event_start_time.get(et)

            # No schedule match yet
            if start_ts is None:
                cycles = self.event_unmatched_cycles.get(et, 0)
                open_ts = self.event_open_time.get(et, now)
                open_age = now - open_ts
                if cycles >= UNMATCHED_SKIP_CYCLES and open_age > UNMATCHED_SKIP_AGE:
                    self._log("skipped", {"reason": "schedule_gap", "event": et,
                        "unmatched_cycles": cycles, "open_age_sec": round(open_age)})
                return

            time_to_start = start_ts - now

            if time_to_start > 86400:
                return

            if time_to_start <= 0:
                self.processed_events.add(et)
                self._save_processed()
                self._log("skipped", {"reason": "match_already_started", "event": et,
                    "time_to_start_sec": round(time_to_start),
                    "start_time": datetime.fromtimestamp(start_ts, tz=ET).strftime("%b %d %I:%M %p ET")})
                return

            if time_to_start <= ENTRY_BUFFER_SEC:
                self.processed_events.add(et)
                self._save_processed()
                self._log("skipped", {"reason": "inside_buffer", "event": et,
                    "time_to_start_sec": round(time_to_start),
                    "start_time": datetime.fromtimestamp(start_ts, tz=ET).strftime("%b %d %I:%M %p ET")})
                return

            # v4: coarse event-level gate only. The fine-grained per-leg
            # placement timing (post at T-placement_minute for that leg's
            # regime) lives in the side loop below. Earliest placement in the
            # v2 table is T-240m, so don't even evaluate sides before T-4h.
            # (Legacy FV path keeps its intel-window gate when enabled.)
            if self.fv_scenarios_enabled:
                intel_window = _entry_lead_cap(et)
                if INTELLIGENCE_AVAILABLE:
                    try:
                        tk0 = list(tickers)[0] if tickers else ""
                        if tk0:
                            intel_rec = recommended_window_seconds(et, tk0)
                            intel_window = intel_rec["window_seconds"]
                            if intel_window == 0:
                                return
                    except Exception:
                        pass
                if time_to_start > intel_window:
                    return
            else:
                if time_to_start > V4_MAX_PLACEMENT_SEC:
                    return

            tk_list = list(tickers)
            if len(tk_list) < 2:
                return
            all_have_bbo = all(tk in self.books and self.books[tk].updated > now - BOOK_STALENESS_SEC for tk in tk_list)
            if not all_have_bbo:
                self._log("event_skip_stale_book", {
                    "event": et,
                    "book_ages_sec": [int(now - self.books[tk].updated) for tk in tk_list if tk in self.books],
                    "missing_books": [tk[-20:] for tk in tk_list if tk not in self.books],
                })
                return

            self.n_matches_seen += 1

            # T51: never ENTER a live match (existing positions are managed
            # separately by check_fills / _v4_manage_resting). Volume-accel
            # detector, latched per event.
            # [C-FEEDER FIX-1] RE-EVALUABLE scratch: the event is NOT marked
            # processed (the old permanent scratch is what turned the 5AM-block
            # false positives into zero-placement nights). While latched, the
            # leg skips; an unlatch (counter-evidence) restores normal
            # evaluation on the next tick. skip_live_match logs once per latch.
            if self._is_match_live(et):
                skip_logged = getattr(self, "_live_skip_logged", None)
                if skip_logged is None:
                    skip_logged = self._live_skip_logged = set()
                if et not in skip_logged:
                    skip_logged.add(et)
                    self._log("skip_live_match", {"event": et})
                return

            sides = self.identify_sides(et)
            if not sides:
                self.n_skips += 1
                self._log("skipped", {"reason": "no_valid_sides", "event": et})
                return

            for (tk, direction, cat) in sides:
                # [C-MANUAL-FIRST OP-3] operator presence on THIS leg -> named
                # skip; every bot entry path (offset table, engagement, and the
                # manage-side fallback/repost via their own gate) yields. The
                # sibling leg is evaluated independently right after.
                if self._manual_owns_leg(tk):
                    self.n_skips += 1
                    self._log("skipped", {"reason": "manual_first",
                        "event": et}, ticker=tk)
                    continue
                if tk in self.positions:
                    continue
                if tk in self.inflight_orders:
                    continue

                book = self.books.get(tk)
                if not book or book.updated < now - BOOK_STALENESS_SEC:
                    self._log("side_skip_stale_book", {
                        "book_age_sec": int(now - book.updated) if book else "missing",
                    }, ticker=tk)
                    continue

                # Universal anti-degenerate guard. Skip only genuinely CROSSED books (bid > ask, a
                # real book artifact) and true degenerates (no bid, or ask pinned at 100). A LOCKED
                # book (bid == ask) is a tight, fully-priced two-sided market -- investable, not
                # degenerate -- so it is allowed through (recovers ~22 entries/day incl. Slam main-
                # draw). The artifact fence stays side_skip_stale_book (BOOK_STALENESS_SEC); not this.
                if book.best_bid <= 0 or book.best_ask >= 100 or book.best_bid > book.best_ask:
                    self._log("skipped", {"reason": "degenerate_book_skip", "event": et,
                        "bid": book.best_bid, "ask": book.best_ask}, ticker=tk)
                    continue

                # ---- Dispatch: legacy FV A/B/C scenarios (gated) vs v4 ----
                if self.fv_scenarios_enabled:
                    await self._legacy_route_side(tk, et, direction, cat,
                                                  book, time_to_start, start_ts, now)
                    continue

                # ===== v4 bid-laying placement (STEP 4) =====
                if cat not in self.categories_enabled:
                    continue

                # #1 ref-price: resolve the entry REFERENCE (last-traded; rollback running-mid)
                # and the per-cell offset row (regime fallback). v4 cell = the ref price's 1c cell.
                lt_age_sec = (time.time() - book.last_trade_ts) if book.last_trade_ts else -1.0
                ent = self._v4_entry_anchor(tk, cat, book, time_to_start)
                if ent is None:
                    # Distinguish a no-fresh-trade skip (last-traded path) from a missing table row,
                    # so the no-trade thread is visible and the late_miss enum stays clean.
                    fresh = book.last_trade_price > 0 and 0 <= lt_age_sec <= V4_LAST_TRADE_MAX_AGE_SEC
                    no_trade = (not self.running_mid_anchor) and not fresh
                    # [C-JOINBID WAVE-1] the no-print hole: instead of skipping an
                    # eligible quiet leg, JOIN the bid at best_bid and fall through
                    # to the NORMAL placement machinery below (paired cap, T52,
                    # pre-post guards, race-resolve, intended_join -- by
                    # construction target_bid == best_bid -- and the T-15 buffer
                    # all inherited unchanged). Ineligible / no-bid / locked /
                    # flag-off -> the skip stands, named exactly as before.
                    if no_trade:
                        _ej = self._engagement_join_eligible(cat, book, time_to_start)
                        if _ej is not None:
                            ent = (_ej, "engagement_join", _ej,
                                   self.regime_lookup(cat, _ej), 240, 0,
                                   0.0, 0.0, _ej, "engagement_wave1")
                    if ent is None:
                        self.n_skips += 1
                        self._log("skipped", {
                            "reason": "skip_no_trade" if no_trade else "no_entry_table_row",
                            "anchor_src": "skip_no_trade" if no_trade else None,
                            "last_trade_age_sec": round(lt_age_sec, 1), "cat": cat,
                            "price": int(round((book.best_bid + book.best_ask) / 2.0))}, ticker=tk)
                        continue
                (current_price, anchor_src, cell, regime, placement_min, offset,
                 exp_fill, exp_roi, target_bid, table_src) = ent

                # Per-leg placement timing: wait until this leg's window opens
                # (post at T-placement_minute). Event is NOT marked processed, so
                # the next tick re-evaluates this leg.
                if time_to_start > placement_min * 60:
                    continue

                # [C-FEEDER FIX-2] decision-time book capture. Every downstream
                # branch, guard, log field and placement-time key derives from
                # THIS synchronous snapshot -- never a re-read of the live book
                # after an await. The QUESAM E3 fire (2026-06-12 10:32:21 ET)
                # was exactly that race: the book moved during the pre-post
                # guard/place_order awaits, the old keying re-read
                # book.best_bid, and a by-construction join keyed
                # intended_join=False. (Also kills the PLIVEK-class log
                # incoherence: current_ask 78 vs book_ask 46 in one event.)
                placement_bid, placement_ask = book.best_bid, book.best_ask
                current_ask = placement_ask
                # [C-FEEDER FIX-6] late-runway boundary + reference switch
                # (RADRAK frame 2026-06-12: window opened T-56, the 180-min
                # offset row posted anchor-1 = 78 and the 79 dip traded through
                # it unfilled; on a late runway the deep offset is invalid ->
                # join the anchor level instead).
                runway_status = self._runway_status(placement_min, time_to_start)
                target_bid, reference_source = self._fix6_reference(
                    runway_status, offset, table_src, current_price, target_bid)
                # [C-JOIN-THE-BID] non-engagement entries rest AT the standing bid (join),
                # capped <= ask-1, replacing the anchor-offset target. Engagement (wave1)
                # keeps its by-construction level under ALL book regimes (incl. locked, where
                # ask-1 < best_bid) -- gated out here. _reprice_target untouched (shared w/
                # completion). Backtest: join beats ask-1 by +2.6..+3.9c/attempt, 16,806 legs.
                if table_src != "engagement_wave1":
                    if cat in self._range_final:   # [C-STAIRCASE 4CAT] all 4 cats staircase (was ATP_MAIN-only)
                        target_bid, _ = self._staircase_bid(cat, cell, current_price, time_to_start, placement_bid, placement_ask)
                        reference_source = "staircase"
                    else:
                        target_bid, _ = self._join_target(placement_bid, placement_ask)
                        reference_source = "join_bid"   # [C-JOIN-THE-BID WALK] fresh join walks from placement
                # [C-JOIN-TRIAL] pre-registered abort halts NEW join entries once tripped.
                if self.join_trial_aborted and reference_source == "join_bid":
                    self.n_skips += 1
                    self._log("skipped", {"reason": "join_trial_aborted", "cat": cat}, ticker=tk)
                    continue
                # [C-STAIRCASE SHIP-2 abort-spec] halt NEW staircase entries once aborted; resting legs continue.
                if reference_source == "staircase" and self.staircase_aborted.get(cat, False):
                    self.n_skips += 1
                    self._log("skipped", {"reason": "staircase_aborted", "cat": cat}, ticker=tk)
                    continue
                force_cross = self.round5_enabled and self.round5_detector_fire(
                    tk, current_ask, target_bid)

                # Execution branch (Section 4) with late-discovery / T-20m
                # fallback folded in.
                # Placement-side fallback DELIBERATELY stays at V4_T20M_SEC (not
                # self.v4_fallback_sec like the manage-side). The T-15m match_start_buffer
                # (ENTRY_BUFFER_SEC) cancels any unfilled entry_resting bid, so resting a
                # FRESH sub-20m placement to T-1 is futile -- it would be cancelled at T-15m,
                # adding only place-then-cancel churn. A fresh late placement takes the atlas
                # baseline taker. (Lever-2's T-1 governs the MANAGE side -- bids placed >20m
                # out that rest down; note both fallback-crosses are themselves bounded by
                # the T-15m buffer -> see SESSION_HANDOFF "lever-2 fill-window" note.)
                if time_to_start <= V4_T20M_SEC:
                    if self.maker_only_entry:
                        # STAGE 1: maker-only -- do NOT taker-cross, and do NOT stab an ask-1 maker
                        # into the T-20m->start window (won't fill / adverse-selection / muddies the
                        # Stage-1 cohort). Place nothing; any earlier unfilled resting bid self-cleans
                        # via match_start_buffer (T-15m) -> _untombstone_entry (del). Rest-or-no-fill.
                        self.n_skips += 1
                        self._log("skipped", {"reason": "maker_only_no_late_entry",
                            "min_before_start": round(time_to_start / 60), "cat": cat}, ticker=tk)
                        continue
                    entry_price, post_only, entry_mode = current_ask, False, "miss_fallback"
                elif target_bid >= current_ask or force_cross:
                    if (self.marketable_clamp_placement or self.maker_only_entry) and not force_cross:
                        # 3rd cross site clamp: the placement target is marketable (>= ask), but the
                        # fillable sell-flow is typically 0-4c away (live forensics 5/6) -- rest an
                        # ask-1 MAKER instead of lifting, the same clamp _reprice_target/_fallback_order
                        # already apply on the other two cross sites. force_cross (round5) is exempt
                        # (still crosses, below). target_bid tracks the clamp so target_price and the
                        # cancel-on-marketable logic stay consistent (manage-side exemption mirrors
                        # fallback_maker). post_only=True cannot cross -> no taker fill, no fee.
                        # [C-JOIN-THE-BID] site-4 clamp (Plex amend #1): join (non-engagement)
                        # instead of ask-1; engagement keeps ask-1 (preserved, amend #4).
                        if table_src != "engagement_wave1":
                            target_bid = max(1, min(placement_bid, current_ask - 1))
                        else:
                            target_bid = max(1, current_ask - 1)
                        entry_price, post_only, entry_mode = target_bid, True, "marketable_clamp"
                    else:
                        # MARKETABLE TAKER: lift the ask, pay the 1c taker fee.
                        entry_price, post_only, entry_mode = current_ask, False, "marketable_taker"
                else:
                    # RESTING MAKER limit buy at target_bid; manage to T-20m.
                    entry_price, post_only, entry_mode = target_bid, True, "resting_maker"

                if entry_price <= 0 or entry_price >= 100:
                    continue

                # [C-FEEDER RIDE-ALONG] depth-ahead read fixed: contracts
                # resting at OUR final target level, captured in the same
                # synchronous decision slice (the old read took the level at
                # the post-await best_bid -- wrong level on any tick, and the
                # exact-500 cluster turned out to be real MM quote sizes (G2
                # median 499), not a code sentinel -- the read itself was the
                # defect).
                placement_depth_ahead = int(book.bids.get(int(round(target_bid)), 0) or 0)

                # T50 paired-basis guard: refuse this leg if (this side +
                # sibling committed cost) > cap (yes+no > ~100 guaranteed loss).
                # [C-CAP-REMOVAL site 1] flag-gated dormant: with the cap off,
                # the per-leg sanity bound above (entry_price < 100) governs.
                if (getattr(self, "paired_cap_enforced", True)
                        and not self._paired_basis_ok(tk, et, entry_price)):
                    continue

                # T52: never TAKER-cross a fat spread (the KESMAR fat-spread
                # mechanism). Resting-maker entries (post_only) are unaffected.
                if post_only is False and not self._taker_spread_ok(placement_bid, current_ask):
                    self.n_skips += 1
                    self._log("skip_fat_spread_taker", {"event": et, "mode": entry_mode,
                        "spread": current_ask - placement_bid, "bid": placement_bid,
                        "ask": current_ask, "cap": MAX_TAKER_SPREAD}, ticker=tk)
                    continue

                # Pre-post guards: existing resting order / open position.
                existing = await api_get(self.session, self.ak, self.pk,
                    "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
                if existing and existing.get("orders"):
                    self._log("skipped", {"reason": "resting_order_exists",
                        "ticker": tk, "existing_count": len(existing["orders"])}, ticker=tk)
                    continue
                existing_pos = await api_get(self.session, self.ak, self.pk,
                    "/trade-api/v2/portfolio/positions?ticker=%s&count_filter=position&settlement_status=unsettled" % tk, self.rl)
                if existing_pos:
                    if any(int(float(p.get("position_fp", 0))) > 0
                           for p in existing_pos.get("market_positions", [])):
                        self._log("skipped", {"reason": "position_exists", "ticker": tk}, ticker=tk)
                        continue

                self._log("v4_place", {
                    "event": et, "direction": direction, "cat": cat,
                    "regime": regime, "cell": cell, "current_price": current_price,
                    "anchor_src": anchor_src, "table_src": table_src,
                    "last_trade_age_sec": round(lt_age_sec, 1),
                    "offset": offset, "target_bid": target_bid,
                    "current_ask": current_ask, "entry_price": entry_price,
                    "entry_mode": entry_mode, "post_only": post_only,
                    "placement_minute": placement_min,
                    "min_before_start": round(time_to_start / 60),
                    # [C-FEEDER FIX-6] A5: runway tag on EVERY placement;
                    # cell-performance analysis filters runway_status == full
                    "runway_status": runway_status,
                    **({"reference_source": reference_source,
                        "offset_table": offset} if reference_source else {}),
                    # [C-FV-OBSERVE-SHIP] Plex-countersigned; logging only
                    **(self._fv_observe_fields(
                        et, tk, (self.event_player_names.get(et) or [""])[0],
                        entry_price,
                        time_to_start <= 0 or self._is_match_live(et))
                       if getattr(self, "fv_observe", False) else {}),
                    "exp_fill_rate": round(exp_fill, 3), "exp_net_roi_pct": round(exp_roi, 2),
                    # Locked-book verification hook (Plex): record the placement-time book so the
                    # next is_taker-truth pass can confirm locked-book (bid==ask) placements fill
                    # like normal tight markets, not a hidden adverse cohort. Telemetry only, not a gate.
                    # [C-FEEDER FIX-2] decision-time snapshot, not a post-await re-read.
                    "book_bid": placement_bid, "book_ask": placement_ask,
                    "book_spread": placement_ask - placement_bid,
                    "locked_book": placement_bid == placement_ask,
                    # [C-JOINBID] ratified depth logging (observational): contracts
                    # resting at the join level at placement, for the wave-gate
                    # ledger (G2 quartiles 84/499/1381 are the interpretation grid).
                    # [C-FEEDER FIX-4] ledger attribution: the would-have-been
                    # band + table membership ride every engagement placement so
                    # the band retrospective is computable with gating OFF.
                    **({"engagement": True,
                        "depth_ahead": placement_depth_ahead,
                        "band": regime,
                        "bucket": self._engagement_bucket(time_to_start),
                        "band_on_table": (cat, self._engagement_bucket(time_to_start),
                                          regime) in self.engagement_cells,
                        "band_gating": bool(getattr(self, "engagement_band_gating", False))}
                       if table_src == "engagement_wave1" else {}),
                }, ticker=tk)

                # #1 ref-price soft-alert: rolling tight_mid rate over the last 100 placements.
                self._anchor_src_hist.append(anchor_src)
                if len(self._anchor_src_hist) == self._anchor_src_hist.maxlen:
                    tm_rate = sum(1 for a in self._anchor_src_hist if a == "tight_mid") / float(
                        self._anchor_src_hist.maxlen)
                    if tm_rate > 0.05 and self._anchor_alert_armed:
                        self._anchor_alert_armed = False
                        self._log("anchor_src_alert", {"tight_mid_rate": round(tm_rate, 3),
                            "window": self._anchor_src_hist.maxlen,
                            "note": "tight_mid (fresh print outside a tight book) > 5%"}, ticker=tk)
                    elif tm_rate <= 0.05:
                        self._anchor_alert_armed = True

                self.inflight_orders.add(tk)
                try:
                    oid, resp = await self.place_order(tk, "buy", "yes", entry_price,
                                                       self.entry_size, post_only=post_only)
                finally:
                    self.inflight_orders.discard(tk)

                pos = Position(
                    ticker=tk, event_ticker=et, category=cat,
                    direction=direction, cell_name="", cell_cfg={},
                    entry_price=entry_price, entry_order_id=oid,
                    entry_posted_ts=now, phase="entry_resting",
                    match_start_ts=start_ts,
                    play_type="v4_" + entry_mode,
                    is_v4=True, regime_at_posting=regime, target_price=target_bid,
                    placement_minute=placement_min, entry_mode=entry_mode,
                    paid_taker_fee=(post_only is False),
                    # [C-BID-SURVIVAL DIFF-2] precise key, set at placement only.
                    # [C-FEEDER FIX-2] keyed on the DECISION (captured snapshot +
                    # construction), never a post-await book re-read.
                    intended_join=self._intended_join_at_placement(
                        entry_mode, target_bid, placement_bid, table_src),
                    # [C-FEEDER FIX-3] deliberate ask-1 rest (locked/1c book),
                    # keyed on the same decision snapshot
                    intended_clamp=self._intended_clamp_at_placement(
                        entry_mode, target_bid, placement_ask),
                    # [C-FEEDER FIX-6] A5 ledger tags ride the Position
                    runway_status=runway_status,
                    reference_source=reference_source,
                )
                self.positions[tk] = pos
                # [C-STAIRCASE SHIP-2] Risk 7: set the FIXED staircase state once at placement.
                if reference_source == "staircase":
                    pos.staircase_anchor = int(current_price); pos.staircase_cell = int(cell); pos.staircase_ref = int(target_bid)
                # [C-JOIN-TRIAL] join leg: stamp the queue-telemetry baseline + trial enrolment.
                if reference_source == "join_bid":
                    pos.walk_ref = target_bid
                    pos.join_depth_post = placement_depth_ahead
                    pos.join_post_ts = now
                    pos.join_is_trial = self.join_trial_mode
                    if self.join_trial_mode:
                        self.trial_attempts += 1
                # [C-JOINBID] ledger separability: engagement fills must be
                # distinguishable from offset-table placements (play_type drives
                # cohort labeling only; ALL manage/exit semantics key on
                # entry_mode, which stays the normal resting_maker).
                if table_src == "engagement_wave1":
                    pos.play_type = "v4_engagement_join"
                    # [C-JOINBID AMEND] E1-E3 at the placement; first violation
                    # fires the shared tripwire (self-disable + cancel-only sweep
                    # incl. THIS bid + incident file); the bot keeps trading.
                    _viol = self._engagement_place_guards(tk, et, cat, pos, time_to_start)
                    if _viol is not None:
                        await self._engagement_tripwire(_viol[0], _viol[1], tk=tk)
                if entry_mode == "resting_maker":
                    self._save_v4_resting()
                elif post_only is False:
                    # D18 fix: a placement-side cross can fill ON PLACEMENT; book it at
                    # source (the placement path has no entry_resting poll for it).
                    await self._book_placement_cross_fill(tk, pos, resp, entry_price)
        finally:
            self._event_routing.discard(et)

    async def on_bbo_update(self, ticker):
        """Event-driven hot path (tennis_stb pattern): a single ticker's BBO
        changed. Route its event for placement and manage its own resting bid --
        both bounded to one ticker/event so the WS reader (which awaits this
        inline) never blocks long enough to starve the keepalive ping. Wrapped
        so any routing error is logged, never bubbling into ws_reader's
        reconnect path (a routing bug must NOT trigger a WS reconnect)."""
        et = self.ticker_to_event.get(ticker)
        if not et:
            return
        tickers = self.event_tickers.get(et)
        if not tickers:
            return
        try:
            now = time.time()
            # Placement for this ticker's event (bounded to one event; the
            # reentrancy guard makes this safe against the periodic sweep).
            await self._route_event(et, tickers, now)
            # Manage this ticker's own resting bid (move-repost, T-20m fallback)
            # on its own BBO update. validate_resting_buys remains the backstop
            # for quiet books; the per-ticker mgmt guard serializes the two.
            pos = self.positions.get(ticker)
            if (pos and pos.is_v4 and pos.phase == "entry_resting"
                    and pos.entry_order_id):
                book = self.books.get(ticker)
                if book and book.updated >= now - BOOK_STALENESS_SEC:
                    await self._v4_manage_resting(ticker, pos, book, now)
        except Exception as e:
            self._log("on_bbo_update_error",
                      {"error": str(e), "traceback": traceback.format_exc()},
                      ticker=ticker)

    async def _legacy_route_side(self, tk, et, direction, cat, book, time_to_start, start_ts, now):
        """LEGACY FV-anchor A/B/C scenario routing for one side. Fires only when
        config fv_anchor_scenarios_enabled is true (default false). Preserved
        verbatim for emergency rollback. `continue` semantics become `return`."""
        # Resolve anchor
        anchor_value, anchor_source, side_fv = self._resolve_anchor(tk, et)
        if anchor_value is None:
            self.n_skips += 1
            self._log("skipped", {"reason": "no_anchor_available", "event": et}, ticker=tk)
            return

        # Cell assignment from anchor
        anchor_cell, anchor_cell_cfg = self._legacy_cell_lookup(cat, direction, anchor_value)
        if anchor_cell_cfg is None or anchor_cell in self.config.get("disabled_cells", []):
            self.n_skips += 1
            self._log("skipped", {"reason": "fv_cell_not_active",
                "fv_cell": anchor_cell, "fv_cents": round(anchor_value, 1),
                "event": et, "anchor_source": anchor_source}, ticker=tk)
            return

        # Scenario classification
        kalshi_mid = (book.best_bid + book.best_ask) / 2.0
        delta = kalshi_mid - anchor_value
        spread = book.best_ask - book.best_bid
        entry_size = self.config["sizing"]["entry_contracts"]

        if not self.config.get("b_convergence_enabled", True) and delta <= -8:
            delta = 0  # B disabled -> force Scenario C path

        if delta <= -8:
            scenario = "B_take"
            if spread <= 2 and book.best_bid > 0 and book.best_ask < 100 and anchor_source.startswith("fv"):
                entry_price = book.best_ask
                post_only = False
            else:
                scenario = "C_discount"
                entry_price = book.best_bid
                post_only = True
        elif delta > 0:
            scenario = "A_premium"
            if time_to_start > 3600:
                return  # too early for premium entries
            entry_price = book.best_bid
            post_only = True
        else:
            scenario = "C_discount"
            entry_price = book.best_bid
            post_only = True

        if entry_price <= 0 or entry_price >= 100:
            return

        existing = await api_get(self.session, self.ak, self.pk,
            "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
        if existing and existing.get("orders"):
            self._log("skipped", {"reason": "resting_order_exists",
                "ticker": tk, "existing_count": len(existing["orders"])}, ticker=tk)
            return
        existing_pos = await api_get(self.session, self.ak, self.pk,
            "/trade-api/v2/portfolio/positions?ticker=%s&count_filter=position&settlement_status=unsettled" % tk, self.rl)
        if existing_pos:
            pos_list = existing_pos.get("market_positions", [])
            if any(int(float(p.get("position_fp", 0))) > 0 for p in pos_list):
                self._log("skipped", {"reason": "position_exists", "ticker": tk}, ticker=tk)
                return

        self._log("cell_match", {
            "event": et, "direction": direction, "cell": anchor_cell,
            "scenario": scenario, "anchor_value": round(anchor_value, 1),
            "anchor_source": anchor_source, "kalshi_mid": round(kalshi_mid, 1),
            "delta": round(delta, 1), "spread": spread,
            "entry_price": entry_price, "entry_size": entry_size,
            "post_only": post_only,
            "strategy": anchor_cell_cfg["strategy"],
            "exit_cents": anchor_cell_cfg["exit_cents"],
            "min_before_start": round(time_to_start / 60),
        }, ticker=tk)

        self.inflight_orders.add(tk)
        try:
            oid, resp = await self.place_order(tk, "buy", "yes", entry_price, entry_size, post_only=post_only)
        finally:
            self.inflight_orders.discard(tk)

        pos = Position(
            ticker=tk, event_ticker=et,
            category=self.ticker_category.get(tk, "?"),
            direction=direction, cell_name=anchor_cell, cell_cfg=anchor_cell_cfg,
            entry_price=entry_price, entry_order_id=oid,
            entry_posted_ts=now, phase="entry_resting",
            match_start_ts=start_ts,
            play_type=scenario,
            anchor_source=anchor_source,
            routed_cell=anchor_cell,
        )
        self.positions[tk] = pos

    # ------------------------------------------------------------------
    # Check pending entries: post when spread tightens
    # ------------------------------------------------------------------
    async def check_pending_entries(self):
        now = time.time()
        for tk in list(self.pending_entries.keys()):
            # Race guard: skip if routing_tick already handling or position exists
            if tk in self.positions or tk in self.inflight_orders:
                del self.pending_entries[tk]
                continue

            pe = self.pending_entries[tk]

            # Timeout: 2h with no tight spread → skip permanently
            if now - pe["discovered_ts"] > PENDING_TIMEOUT_SEC:
                del self.pending_entries[tk]
                self._log("pending_timeout", {"ticker": tk, "cell": pe["cell_name"]}, ticker=tk)
                continue

            book = self.books.get(tk)
            if not book or book.updated < now - 120:
                continue

            spread = book.best_ask - book.best_bid
            if spread > DEAD_SPREAD_THRESHOLD:
                continue  # still dead, wait

            current_price, price_source = self.get_market_price(tk)
            if current_price is None:
                continue

            # Re-evaluate play with current FV
            et = pe["event"]
            side_fv = self._get_side_fv(tk, et)
            if side_fv is None or side_fv.get("fv_cents") is None:
                del self.pending_entries[tk]
                self._log("pending_no_fv", {"ticker": tk}, ticker=tk)
                continue

            fv_cents = side_fv["fv_cents"]
            direction = "leader" if current_price > 50 else "underdog"
            kalshi_cell, _ = self._legacy_cell_lookup(pe["cat"], direction, current_price)
            fv_cell, fv_cell_cfg = self._legacy_cell_lookup(pe["cat"], direction, fv_cents)
            gap = current_price - fv_cents
            cell_low = int(fv_cents / 5) * 5
            cell_high = cell_low + 4

            if fv_cell_cfg is None or fv_cell in self.config.get("disabled_cells", []):
                del self.pending_entries[tk]
                continue

            # Intelligence re-query at resolve time — gate only, no size override
            if INTELLIGENCE_AVAILABLE:
                try:
                    p_rec = recommended_window_seconds(et, tk)
                    if p_rec["window_seconds"] == 0:
                        del self.pending_entries[tk]
                        self._log("pending_intel_skip", {
                            "ticker": tk, "rationale": p_rec.get("rationale", ""),
                            "confidence_score": p_rec.get("confidence_score"),
                        }, ticker=tk)
                        continue
                except Exception:
                    pass

            # Determine play — exhaustive, no fall-through
            play_type = None
            entry_price = None
            entry_size = None
            layered_exit_price = 0

            if kalshi_cell == fv_cell:
                play_type = "A_tight"
                entry_price = max(cell_low, int(current_price) - 1)
                entry_size = self.config["sizing"]["entry_contracts"]
            elif current_price < fv_cents:
                play_type = "B_convergence"
                entry_price = int(current_price) + 1
                entry_size = 19
                layered_exit_price = int(fv_cents) - 2
            else:
                play_type = "A_patient"
                entry_price = cell_high
                entry_size = self.config["sizing"]["entry_contracts"]

            del self.pending_entries[tk]

            self._log("pending_resolved", {
                "spread": spread, "entry_price": entry_price, "cell": fv_cell,
                "play_type": play_type,
                "fv_cents": round(fv_cents, 1), "gap": round(gap, 1),
                "waited_sec": round(now - pe["discovered_ts"]),
            }, ticker=tk)

            self.inflight_orders.add(tk)
            try:
                oid, resp = await self.place_order(tk, "buy", "yes", entry_price, entry_size)
            finally:
                self.inflight_orders.discard(tk)
            pos = Position(
                ticker=tk, event_ticker=et,
                category=self.ticker_category.get(tk, "?"),
                direction=direction, cell_name=fv_cell, cell_cfg=fv_cell_cfg,
                entry_price=entry_price, entry_order_id=oid,
                entry_posted_ts=now, phase="entry_resting",
                match_start_ts=self.event_start_time.get(et, 0),
                play_type=play_type,
                layered_exit_price=layered_exit_price,
            )
            self.positions[tk] = pos

    # ------------------------------------------------------------------
    # Validate resting buys: cancel stale orders
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # v4 resting-bid management + state persistence (STEP 5)
    # ------------------------------------------------------------------
    def _save_v4_resting(self):
        """Persist live v4 resting bids for restart recovery (STEP 5). Holds
        order_id, posted_at, posted_price, target_price, regime_at_posting and
        the fields needed to rebuild the Position. Live mode only; paper mode
        recovers via PaperApi.load_state.

        PART-2 (flag-gated): completion-repriced bids carry their completion fields,
        and the file gains a v2 shape {"_shape":"v2","legs":{...},"window_open":{...}}
        carrying the window-open frames (lifecycle (c)). completion_reprice=false
        writes the legacy bare-legs shape byte-identically."""
        if _PAPER_API is not None:
            return
        out = {}
        for tk, pos in self.positions.items():
            if pos.is_v4 and pos.phase == "entry_resting" and pos.entry_order_id:
                out[tk] = {
                    "order_id": pos.entry_order_id,
                    "event_ticker": pos.event_ticker,
                    "category": pos.category,
                    "direction": pos.direction,
                    "posted_at": pos.entry_posted_ts,
                    "posted_price": pos.entry_price,
                    "target_price": pos.target_price,
                    "regime_at_posting": pos.regime_at_posting,
                    "placement_minute": pos.placement_minute,
                    "entry_mode": pos.entry_mode,
                    "match_start_ts": pos.match_start_ts,
                }
                # [C-BID-SURVIVAL DIFF-2] sparse key: present ONLY when True, so
                # non-join legs keep the exact legacy key set (shape regression
                # in test_completion_reprice stays byte-identical).
                if pos.intended_join:
                    out[tk]["intended_join"] = True
                # [C-FEEDER FIX-3] sparse, same discipline as intended_join
                if pos.intended_clamp:
                    out[tk]["intended_clamp"] = True
                # [C-FEEDER FIX-6] sparse A5 ledger tags survive restart
                if pos.runway_status != "full":
                    out[tk]["runway_status"] = pos.runway_status
                if pos.reference_source:
                    out[tk]["reference_source"] = pos.reference_source
                # [C-JOIN-TRIAL] sparse: join-walk queue telemetry survives restart so a
                # respawn does NOT reset the re-post count / abort ledger mid-trial.
                if pos.reference_source == "join_bid":
                    out[tk]["walk_ref"] = pos.walk_ref
                    out[tk]["join_reposts"] = pos.join_reposts
                    out[tk]["join_depth_post"] = pos.join_depth_post
                    out[tk]["join_post_ts"] = pos.join_post_ts
                    out[tk]["join_is_trial"] = pos.join_is_trial
                # [C-STAIRCASE SHIP-2] Risk 6: staircase state survives restart (anchor=0->1c bid,
                # cell=0->KeyError; must persist). Sparse-when-set, da9f6ac C-JOIN-TRIAL pattern.
                if pos.reference_source == "staircase":
                    out[tk]["staircase_anchor"] = pos.staircase_anchor
                    out[tk]["staircase_cell"] = pos.staircase_cell
                    out[tk]["staircase_ref"] = pos.staircase_ref
                # [C-JOINBID] sparse: engagement cohort label survives restart
                if pos.play_type == "v4_engagement_join":
                    out[tk]["play_type"] = "v4_engagement_join"
                if pos.entry_mode == "completion_reprice":
                    out[tk].update({
                        "completion_s0": pos.completion_s0,
                        "completion_x": pos.completion_x,
                        "completion_leg1_basis": pos.completion_leg1_basis,
                        "completion_qty": pos.completion_qty,
                        "completion_reprice_ts": pos.completion_reprice_ts,
                        "completion_prev_price": pos.completion_prev_price,
                        "completion_prev_mode": pos.completion_prev_mode,
                        "completion_prev_target": pos.completion_prev_target,
                        "completion_lookup_cell": pos.completion_lookup_cell,
                    })
        if self.completion_reprice:
            cutoff = time.time() - V4_WINDOW_OPEN_MAX_AGE_SEC
            payload = {"_shape": "v2", "legs": out,
                       "window_open": {tk: wo for tk, wo in self._window_open.items()
                                       if wo.get("ts", 0) >= cutoff}}
        else:
            payload = out
        tmp = str(V4_RESTING_FILE) + ".tmp"
        with open(tmp, "w") as f:
            json.dump(payload, f)
        os.replace(tmp, str(V4_RESTING_FILE))

    def _load_v4_resting(self):
        """Rebuild v4 resting-bid Positions from the state file on startup.
        Skips tickers already present (reconcile may have linked them)."""
        if _PAPER_API is not None:
            return
        try:
            with open(V4_RESTING_FILE) as f:
                data = json.load(f)
        except (FileNotFoundError, ValueError):
            return
        # T54: a malformed/empty state file (e.g. a bare list) must not crash
        # startup. Coerce anything that isn't a dict to a no-op restore.
        if not isinstance(data, dict):
            self._log("v4_resting_bad_shape", {"type": type(data).__name__})
            return
        # PART-2 v2 shape (lifecycle (d)): restore window-open frames, then fall
        # through to the legs dict. Legacy bare-legs files load unchanged.
        if data.get("_shape") == "v2":
            wo = data.get("window_open", {})
            if isinstance(wo, dict):
                n_wo = 0
                for wtk, wd in wo.items():
                    if isinstance(wd, dict) and "price" in wd and "cell" in wd:
                        self._window_open.setdefault(wtk, wd)
                        n_wo += 1
                if n_wo:
                    self._log("window_open_restored", {"count": n_wo})
            data = data.get("legs", {})
            if not isinstance(data, dict):
                self._log("v4_resting_bad_shape", {"type": type(data).__name__})
                return
        restored = 0
        for tk, d in data.items():
            if tk in self.positions:
                continue
            self.positions[tk] = Position(
                ticker=tk, event_ticker=d.get("event_ticker", ""),
                category=d.get("category", "?"), direction=d.get("direction", ""),
                cell_name="", cell_cfg={},
                entry_price=int(d.get("posted_price", 0)),
                entry_order_id=d.get("order_id", ""),
                entry_posted_ts=float(d.get("posted_at", 0.0)),
                phase="entry_resting", match_start_ts=float(d.get("match_start_ts", 0.0)),
                play_type=d.get("play_type", "v4_" + d.get("entry_mode", "resting_maker")),
                is_v4=True, regime_at_posting=d.get("regime_at_posting", ""),
                target_price=int(d.get("target_price", 0)),
                placement_minute=int(d.get("placement_minute", 0)),
                entry_mode=d.get("entry_mode", "resting_maker"),
                intended_join=bool(d.get("intended_join", False)),
                intended_clamp=bool(d.get("intended_clamp", False)),
                runway_status=d.get("runway_status", "full"),
                reference_source=d.get("reference_source", ""),
                walk_ref=int(d.get("walk_ref", 0)),
                join_reposts=int(d.get("join_reposts", 0)),
                join_depth_post=int(d.get("join_depth_post", 0)),
                join_post_ts=float(d.get("join_post_ts", 0.0)),
                join_is_trial=bool(d.get("join_is_trial", False)),
                staircase_anchor=int(d.get("staircase_anchor", 0)),
                staircase_cell=int(d.get("staircase_cell", 0)),
                staircase_ref=int(d.get("staircase_ref", 0)),
                completion_s0=int(d.get("completion_s0", 0)),
                completion_x=int(d.get("completion_x", 0)),
                completion_leg1_basis=int(d.get("completion_leg1_basis", 0)),
                completion_qty=int(d.get("completion_qty", 0)),
                completion_reprice_ts=float(d.get("completion_reprice_ts", 0.0)),
                completion_prev_price=int(d.get("completion_prev_price", 0)),
                completion_prev_mode=d.get("completion_prev_mode", ""),
                completion_prev_target=int(d.get("completion_prev_target", 0)),
                completion_lookup_cell=int(d.get("completion_lookup_cell", 0)),
            )
            restored += 1
            # [C-COPILOT] restored legs are BOT orders -- seed the registry
            if d.get("order_id"):
                getattr(self, "_bot_order_ids", set()).add(d["order_id"])
                getattr(self, "_bot_order_tickers", set()).add(tk)
        if restored:
            self._log("v4_resting_restored", {"count": restored})

    async def _v4_manage_resting(self, tk, pos, book, now):
        """Serialized entry point for v4 resting-bid management. Both
        on_bbo_update (per BBO tick) and validate_resting_buys (120s backstop)
        can call this; the per-ticker guard ensures only one manager runs at a
        time so they cannot race a double cancel/repost or double T-20m take."""
        if tk in self._mgmt_inflight:
            return
        self._mgmt_inflight.add(tk)
        try:
            await self._v4_manage_resting_inner(tk, pos, book, now)
        finally:
            self._mgmt_inflight.discard(tk)

    async def _v4_manage_resting_inner(self, tk, pos, book, now):
        """Manage one v4 resting bid from placement -> T-20m. Maintains
        target_bid (re-classifies regime and re-posts when the current Kalshi
        price moves > 1 cell width from the last placement basis), cancels on a
        degenerate/wide-spread book, and crosses as taker if a re-evaluated
        target becomes marketable. T-20m fallback is handled below (STEP 6)."""
        # PART-2: completion bids have their own lifecycle (freshness re-eval, buffer-
        # exempt ride to T-0). They must NEVER enter the regular move-repost / T-20
        # fallback / wide-spread machinery, which would reprice them back to the entry
        # frame (the frame-mismatch leak).
        if pos.entry_mode == "completion_reprice":
            await self._v4_manage_completion(tk, pos, book, now)
            return
        spread = book.best_ask - book.best_bid
        # Degenerate / wide-spread book: cancel and free the leg for re-entry.
        # T51/T52: cancel a resting entry bid the moment the match goes live --
        # do not let a pre-match bid fill into live play. Filled positions are
        # managed separately and unaffected.
        # [C-RIDE-LIVE-OFF 2026-06-15] Fires on _is_match_live ALONE (the volume-
        # burst latch = tape-detected real start, delay-proof), REGARDLESS of
        # premarket_bids_ride_live. ride_live no longer exempts the bid from this
        # sweep -- it now SOLELY gates the T-15 wall-clock buffer exemption
        # (check_fills, ENTRY_BUFFER_SEC). [C-P0-RACE site 2] a raced fill that
        # filled pre-live is booked by _cancel_entry_and_resolve, not deleted.
        if self._is_match_live(pos.event_ticker):
            res = await self._cancel_entry_and_resolve(
                tk, pos, "match_live_cancel", "match_live_cancel_race")
            if res == "cancelled":
                self._log("match_live_resting_cancel", {"event": pos.event_ticker}, ticker=tk)
                self._untombstone_entry(tk, pos)
                self._save_v4_resting()
            return
        should_cancel, creason = self._resting_cancel_reason(pos.target_price, book.best_bid, book.best_ask)
        # RUN-7: the ask-1 fallback bid is INTENTIONALLY marketable-adjacent (placed just below the
        # ask to catch final-window flow) -- exempt ONLY that bid from the marketable-cancel so
        # cancel-on-marketable doesn't pick it off. Scoped to the two intentional ask-1 maker rests
        # (fallback_maker = T-20m clamp; marketable_clamp = 3rd-cross-site placement clamp): a normal
        # resting bid that drifts marketable is NOT exempt (still cancelled). Degenerate still cancels.
        if should_cancel and creason == "bid_marketable_stale" and pos.entry_mode in ("fallback_maker", "marketable_clamp"):
            should_cancel, creason = False, None
        # [C-BID-SURVIVAL DIFF-2] join-bid exemption (same shape as the RUN-7
        # exemption above, keyed on the PLACEMENT-time intended_join flag --
        # never on the current book): a bid deliberately placed AT the join
        # level is in its desired state; cancelling it is the E3..E5 churn
        # engine (8%->97% stale-kill share, C-ERA-LINK) and -- via anchor
        # aging past 1800s -- the leg-death spiral (Coria, 29 cycles,
        # 2026-06-11). The bid rests; no re-anchor, so the freshness clock
        # stops applying to it. Drift bids (flag unset) keep the full rule;
        # degenerate cancel, T51 match-live, T52, and the T-15 buffer all
        # still govern this bid.
        if should_cancel and creason == "bid_marketable_stale" and pos.intended_join:
            should_cancel, creason = False, None
        # [C-FEEDER FIX-3] Option (a): intended-clamp exemption, same shape and
        # same placement-time-key discipline. A resting-maker bid DELIBERATELY
        # posted at ask-1 (locked/1c book -- the AUGMAJ 206-cycle, KRERUS
        # 61-cycle churn engines) is in its desired state; buffer stays 1, so a
        # genuine DRIFT bid (flag unset) the book moves onto still cancels.
        # Degenerate, T51 match-live, T52 and the T-15 buffer all still govern.
        if should_cancel and creason == "bid_marketable_stale" and pos.intended_clamp:
            should_cancel, creason = False, None
        # [C-STAIRCASE WALK-FINAL] 4th exemption (same shape as fallback_maker/intended_join/
        # intended_clamp): the walk's final-window post (anchor-1, == ask-1 in a 1-wide book) is the
        # validated aggressive-maker END STATE, not a drift bid. intended_clamp is keyed at PLACEMENT
        # (deep cast -> False) and never re-derived on walk repost, so for staircase this is the SOLE
        # marketable-stale guard (Plex cond-3). Without it clause #1 buys nothing -- the anchor-1 bid
        # self-cancels next pass. Degenerate, tape-cancel (5326), T51/T52, T-15 buffer all still govern.
        if should_cancel and creason == "bid_marketable_stale" and pos.reference_source == "staircase":
            should_cancel, creason = False, None
        if should_cancel:
            # [C-P0-RACE site 1 -- THE observed bug, AUGFUC-AUG 2026-06-11 05:42:10 ET]
            # the marketable-stale cancel raced a fill; the old path ignored the
            # cancel failure and deleted the filled position. Now: resolve against
            # exchange truth -- a raced fill books through the normal entry path.
            res = await self._cancel_entry_and_resolve(
                tk, pos, "v4_cancel_" + creason, "manage_cancel_race")
            if res == "cancelled":
                self._log("v4_resting_cancel", {"reason": creason, "spread": spread,
                    "bid": book.best_bid, "ask": book.best_ask, "target_bid": pos.target_price}, ticker=tk)
                self._untombstone_entry(tk, pos)
                self._save_v4_resting()
            return

        time_to_start = pos.match_start_ts - now if pos.match_start_ts > 0 else 99999

        # [C-MANUAL-FIRST OP-3] operator presence on this leg -> the bot's own
        # resting bid (if any) HOLDS as-is: no T-20 fallback re-post, no
        # move-repost onto his level. Economic cancels above already ran.
        # (mode-flag short-circuit first: pure-stub harnesses without the
        # registry never reach the predicate)
        if (getattr(self, "operator_manual_mode", False)
                and self._manual_owns_leg(tk)):
            return

        # [C-RIDE-LIVE override #6] a rode-in bid HOLDS in-play: no T-20
        # fallback re-post, no move-repost (both are placement decisions --
        # in-play conception is forbidden; without this hold, negative tts
        # satisfies the fallback window and the first manage pass in play
        # would cancel/re-price the bid, defeating the ride -- the Naef
        # 13:40:00 re-post-into-play shape). The economic cancels above
        # (stale on drift bids, degenerate) already ran this pass.
        if (getattr(self, "premarket_bids_ride_live", False)
                and (time_to_start <= 0 or self._is_match_live(pos.event_ticker))):
            return

        # T-20m taker fallback (STEP 6): if the bid is still unfilled at T-20m,
        # cross as a taker at the current ask. This IS the atlas baseline entry
        # -- the +8.70% floor -- so the strategy can never underperform it. Pay
        # the 1c taker fee (by design). Fires once; after crossing, entry_mode is
        # miss_fallback and we just wait for the taker fill.
        # [C-STAIRCASE WALK-FINAL] staircase legs OWN their final window via the walk (knots 30/10
        # -> anchor-1); STEP-6 must NOT cancel+convert them to a join at T-20 (the sim-parity gap
        # Plex ratified: the walk was validated to T-10). Keyed on reference_source ONLY -- join_bid
        # legs (which share entry_mode="resting_maker") still take STEP-6 unchanged. ride-live (5395),
        # tape-cancel (5326), manual (5384), degenerate/marketable cancels all already ran above.
        if time_to_start <= self.v4_fallback_sec and pos.reference_source != "staircase" and pos.entry_mode not in ("miss_fallback", "fallback_maker", "marketable_clamp"):
            old = await api_get(self.session, self.ak, self.pk,
                "/trade-api/v2/portfolio/orders/%s" % pos.entry_order_id, self.rl)
            if old:
                old_filled = int(float((old.get("order", old).get("fill_count_fp", 0)) or 0))
                if old_filled > 0:
                    return  # filled as maker before the deadline -- let check_fills book it
            # T52: do not fallback-cross into a LIVE match (T51) or across a FAT
            # SPREAD (the KESMAR fat-spread taker mechanism). Cancel + stay flat
            # rather than fire the atlas-baseline taker into bad execution.
            t52_live = self._is_match_live(pos.event_ticker)
            t52_spread = book.best_ask - book.best_bid
            if t52_live or not self._taker_spread_ok(book.best_bid, book.best_ask):
                reason = "match_live" if t52_live else "fat_spread"
                # [C-P0-RACE site 6a] residual window after the pre-poll above.
                res = await self._cancel_entry_and_resolve(
                    tk, pos, "no_fallback_" + reason, "fallback_blocked_race")
                if res == "cancelled":
                    self._log("v4_fallback_blocked", {"event": pos.event_ticker,
                        "reason": reason, "spread": t52_spread, "bid": book.best_bid,
                        "ask": book.best_ask, "cap": MAX_TAKER_SPREAD}, ticker=tk)
                    self._untombstone_entry(tk, pos)
                    self._save_v4_resting()
                return
            # T50: do not fallback-cross into a guaranteed-loss pair. If the
            # sibling is already committed and best_ask would push combined
            # basis over cap, cancel the unfilled bid and stay flat on this leg.
            # [C-CAP-REMOVAL site 2] flag-gated dormant: the Kawa-Salkova
            # 2026-06-12 frame (SAL killed paired_basis_no_fallback at
            # 48+52=100 vs cap 99) now rests through the T-20 evaluation.
            if (getattr(self, "paired_cap_enforced", True)
                    and not self._paired_basis_ok(tk, pos.event_ticker, book.best_ask)):
                # [C-P0-RACE site 6b] residual window after the pre-poll above.
                res = await self._cancel_entry_and_resolve(
                    tk, pos, "paired_basis_no_fallback", "fallback_paired_race")
                if res == "cancelled":
                    self._untombstone_entry(tk, pos)
                    self._save_v4_resting()
                return
            # [C-P0-RACE site 6c] pre-cross resolve: NEVER fire the taker cross on
            # an unconfirmed cancel -- a raced maker fill + the cross = double
            # position. Raced fill books and the fallback is moot; unresolved
            # retries next pass (the T-20m window condition stays true).
            res = await self._cancel_entry_and_resolve(
                tk, pos, "v4_t20m_fallback", "fallback_cross_race")
            if res != "cancelled":
                return
            # [C-JOIN-THE-BID] fallback joins the standing bid (non-engagement); engagement
            # keeps ask-1 (best_bid:=best_ask -> min(ask,ask-1)=ask-1, byte-identical).
            if pos.play_type != "v4_engagement_join":
                fb_price, fb_post_only = self._fallback_order(book.best_bid, book.best_ask)
            else:
                fb_price, fb_post_only = self._fallback_order(book.best_ask, book.best_ask)
            self.inflight_orders.add(tk)
            try:
                oid, resp = await self.place_order(tk, "buy", "yes", fb_price,
                                                self.entry_size, post_only=fb_post_only)
            finally:
                self.inflight_orders.discard(tk)
            pos.entry_price = fb_price
            pos.entry_order_id = oid
            if fb_post_only:
                # RUN-7 ask-1 MAKER clamp: re-posted just below the ask; RESTS (no taker fill, no
                # instant-fill handler -- post_only cannot cross). entry_mode=fallback_maker fires the
                # fallback once AND scopes the cancel-on-marketable exemption to this bid only (it is
                # intentionally marketable-adjacent; a normal drifted bid is NOT exempt). target_price
                # tracks the clamp. Cancelled only by match_start_buffer (T-15m), degenerate, or fill.
                pos.entry_mode = "fallback_maker"
                pos.play_type = "v4_fallback_maker"
                pos.paid_taker_fee = False
                pos.target_price = fb_price
                self._log("v4_fallback_maker_clamp", {
                    "ask1_price": fb_price, "best_ask": book.best_ask,
                    "regime": pos.regime_at_posting,
                    "time_to_start_min": round(time_to_start / 60, 1),
                }, ticker=tk)
                self._save_v4_resting()
                return
            pos.entry_mode = "miss_fallback"
            pos.play_type = "v4_miss_fallback"
            pos.paid_taker_fee = True
            self._log("v4_t20m_fallback", {
                "take_price": book.best_ask, "target_was": pos.target_price,
                "regime": pos.regime_at_posting,
                "time_to_start_min": round(time_to_start / 60, 1),
            }, ticker=tk)
            # INSTANT TAKER FILL (TRASQU NO_EXIT fix): a post_only=False cross can
            # fill ON PLACEMENT. That fill never transits the entry_resting poll
            # (it can be shadowed by the match_start_buffer branch), so book it
            # here and post the exit via the SAME path ENTRY_FILLED uses.
            # Reuses _v4_apply_exit (HOLD-safe, sizes to filled qty).
            _oid2, _v2_status2, filled, _avg2 = parse_order_response_v2(resp)   # [C-ORDER-V2] flat create resp
            if filled > 0 and not pos.exit_order_id:
                fill_price = _avg2 if (_avg2 and _avg2 > 0) else book.best_ask
                if pos.entry_qty == 0:
                    self.n_entries += 1
                pos.entry_qty = filled
                pos.entry_filled_ts = time.time()
                pos.phase = "active"
                self._log("entry_filled", {
                    "fill_price": fill_price, "posted_price": pos.entry_price,
                    "qty": filled, "new_fills": filled, "cell": pos.cell_name,
                    "direction": pos.direction, "play_type": pos.play_type,
                    "kalshi_status": _v2_status2,
                    "source": "t20m_instant_fill",
                }, ticker=tk)
                if pos.is_v4:
                    await self._v4_apply_exit(tk, pos, fill_price, filled)
                    await self._cancel_sibling_if_paired_over_cap(tk, pos.event_ticker, fill_price)
            self._save_v4_resting()
            return

        # Significant-move re-post (cadence-gated 60s). "Significant" = the
        # current Kalshi price has moved > V4_REPRICE_MOVE_CENTS (5c = 1 cell
        # width) from the price basis at the last placement. Heuristic --
        # surfaced for operator review.
        if now - pos.last_cancel_repost_ts < 60:
            return
        offset_at_post = self.entry_table.get((pos.category, pos.regime_at_posting), (0, 0, 0, 0))[1]
        price_basis = pos.target_price + offset_at_post  # current price when last placed
        # [C-FEEDER FIX-6] a join_late_runway bid sat AT the reference -- no
        # offset to add back when reconstructing the placement basis
        if pos.reference_source in ("join_late_runway", "join_bid"):
            price_basis = pos.target_price
        current_price = int(round((book.best_bid + book.best_ask) / 2.0))
        # [C-JOIN-THE-BID WALK] join-bid entries re-join best_bid every cycle (60s floor kept,
        # >5c threshold dropped): re-post iff the live join target has moved off the resting bid.
        # The walk is half the validated edge -- the 16,806-leg backtest re-joins best_bid each
        # minute; the static >5c gate left the bid 1-4c above a drifted best_bid. No move -> hold
        # the rest (preserves queue priority -- only re-queues when the level actually changes).
        # Non-join paths (completion/engagement/offset) keep the >5c mid-move gate exactly. The
        # never-cross safety (_reprice_target) still applies on the re-post below.
        # [C-STAIRCASE SHIP-2 WALK] Risk 1/2/3: re-quote against the FIXED anchor & cell as D walks
        # the knot schedule (t->0). Gate on staircase_ref change (a knot crossing), NOT the 5c mid-move
        # gate and NOT current_price. target = staircase_anchor - D(t); final_target keyed on
        # staircase_cell. ~8 reposts/leg max by construction.
        if pos.reference_source == "staircase":
            _rf = self._range_final.get(pos.category); _ft = _rf.get(pos.staircase_cell) if _rf else None   # [C-STAIRCASE 4CAT] per-cat
            if _ft is None:
                return
            _sc_D = max(1, int(round(1 + (_ft - 1) * self._frac2(time_to_start / 60.0))))   # == abort_validation.py:58
            _sc_target, _ = self._staircase_target(pos.staircase_anchor, _sc_D, book.best_ask)
            if _sc_target == pos.staircase_ref:
                return
        elif pos.reference_source == "join_bid" and pos.play_type != "v4_engagement_join":
            # [C-JOIN-WALK FIX] key the re-post on walk_ref (the decision-time join we last
            # posted), NOT pos.target_price (mutated by completion/sibling paths): a book that
            # ticks away-and-back to the same level no longer double-reposts. FIX-2/3 discipline.
            if max(1, min(book.best_bid, book.best_ask - 1)) == pos.walk_ref:
                return
        elif abs(current_price - price_basis) <= V4_REPRICE_MOVE_CENTS:
            return

        # Re-classify regime and recompute the target at the new price.
        if pos.reference_source == "staircase":
            new_target = _sc_target; repost_ref = "staircase"   # [C-STAIRCASE SHIP-2] fixed-anchor target; skip regime/join recompute
        else:
            new_regime = self.regime_lookup(pos.category, current_price)
            row = self.entry_table.get((pos.category, new_regime))
            if row is None:
                return
            row_pm, new_offset, _, _ = row
            new_target = max(1, current_price - new_offset)
            # [C-FEEDER FIX-6] A2 late_remap: THIS bid only. The repost row's
            # validated runway is re-checked against the remaining clock; a late
            # remap invalidates the deep offset -> join the reference level.
            # A3: engagement joins untouched (their repost path keeps its shape).
            repost_runway = self._runway_status(row_pm, time_to_start,
                                                late_tag="late_remap")
            repost_ref = ""
            if pos.play_type != "v4_engagement_join":
                # [C-JOIN-THE-BID] reprice joins the standing bid (replaces the FIX-6 offset
                # reference). repost_ref=join_bid -> price_basis uses target_price (no offset
                # add-back). Engagement reposts keep the offset path above (FIX-6 A3).
                new_target, _ = self._join_target(book.best_bid, book.best_ask)
                repost_ref = "join_bid"
        # [C-FEEDER FIX-2/3] decision-time capture for the repost keys (the
        # cancel/place awaits below are a book-tick window, same race class as
        # the QUESAM placement-side fire)
        current_ask = book.best_ask
        repost_bid = book.best_bid

        # Cancel the old bid, but first check it didn't just fill.
        old = await api_get(self.session, self.ak, self.pk,
            "/trade-api/v2/portfolio/orders/%s" % pos.entry_order_id, self.rl)
        if old:
            old_filled = int(float((old.get("order", old).get("fill_count_fp", 0)) or 0))
            if old_filled > 0:
                # Fill happened -- let check_fills book it on its next pass.
                return
        # [C-P0-RACE site 7] residual window after the pre-poll: a raced fill books
        # and the repost is aborted; unresolved aborts too (cadence ts not bumped,
        # so the next pass retries).
        res = await self._cancel_entry_and_resolve(
            tk, pos, "v4_move_repost", "move_repost_race")
        if res != "cancelled":
            return

        # [C-CAP-DIFF] reach-repost cap (dormant; default OFF). new_target here is
        # ALREADY either the offset-computed target (current_price - new_offset) or the
        # join_late_runway override (current_price) -- both repost flavors converge here,
        # so ONE clamp gates both: never repost ABOVE the conception cell (the drift-
        # supported ceiling). Holds/down-moves never trip it (new_target <= ceiling).
        # Phantom-low conception (cell 4-6) -> ceiling sits AT the phantom cell, blocking
        # ALL upward correction (desired; no sanity floor -- subtractive, conservative).
        # Subtractive only; the entry_table offset (the bidding source) is untouched.
        if getattr(self, "reach_repost_cap_enforced", False):
            _wo = self._window_open.get(tk)
            if _wo is not None and _wo.get("cell") is not None and new_target > _wo["cell"]:
                self._log("reach_repost_capped", {
                    "proposed_target": new_target, "conception_ceiling": int(_wo["cell"]),
                    "current_price": current_price,
                    "reference_source": repost_ref or "regime_offset"}, ticker=tk)
                new_target = int(_wo["cell"])

        # Fix-3 (reprice-maker-only): NEVER cross on a reprice. A marketable re-evaluated
        # target is clamped to a resting bid one below the ask and re-rested as a maker.
        new_target, po = self._reprice_target(new_target, current_ask)
        self.inflight_orders.add(tk)
        try:
            oid, _ = await self.place_order(tk, "buy", "yes", new_target,
                                            self.entry_size, post_only=po)
        finally:
            self.inflight_orders.discard(tk)
        pos.entry_price = new_target
        pos.entry_order_id = oid
        pos.entry_mode = "resting_maker"
        # [C-FEEDER RIDE-ALONG] move_repost PRESERVES the engagement cohort
        # label (manage/exit semantics key on entry_mode, never play_type).
        # The old unconditional relabel is why 2 of last night's 3
        # engagement-origin fills (PLIVEK-VEK, MEDCIL-CIL) booked as
        # v4_resting_maker and undercounted the scorecard 3x.
        if pos.play_type != "v4_engagement_join":
            pos.play_type = "v4_resting_maker"
        mode = "repost_resting"
        pos.target_price = new_target
        # [C-STAIRCASE SHIP-2] re-stamp the knot-crossing key after a staircase repost.
        if repost_ref == "staircase":
            pos.staircase_ref = new_target
        # [C-JOIN-TRIAL] walk re-post: bump the re-post ledger + re-stamp the queue baseline.
        if repost_ref == "join_bid":
            pos.walk_ref = new_target
            pos.join_reposts += 1
            pos.join_depth_post = self._queue_depth_ahead(book, new_target)
            pos.join_post_ts = now
        # [C-BID-SURVIVAL DIFF-2] re-key the join flag at every re-placement
        # ([C-FEEDER FIX-2/3] from the decision-time snapshot, not a post-await
        # re-read; clamp re-keyed the same way -- _reprice_target lands the
        # marketable case exactly at ask-1)
        pos.intended_join = (new_target == repost_bid)
        pos.intended_clamp = (new_target == max(1, current_ask - 1))
        pos.regime_at_posting = new_regime
        pos.last_cancel_repost_ts = now
        # [C-FEEDER FIX-6] A5: re-key the runway ledger at every re-placement
        pos.runway_status = repost_runway
        pos.reference_source = repost_ref
        self._log("v4_move_repost", {
            "mode": mode, "old_basis": price_basis, "current_price": current_price,
            "new_regime": new_regime, "new_offset": new_offset,
            "new_target": new_target, "current_ask": current_ask,
            "move_cents": current_price - price_basis,
            "runway_status": repost_runway,
            **({"reference_source": repost_ref} if repost_ref else {}),
        }, ticker=tk)
        self._save_v4_resting()

    async def _v4_manage_completion(self, tk, pos, book, now):
        """PART-2 item 4: freshness re-evaluation + protective cancels for a resting
        completion bid. Serialized by the caller's _mgmt_inflight guard (on_bbo_update
        + the 120s validate_resting_buys backstop). The bid is T-15-buffer-exempt
        (item 5) and rides to T-0; at T-0 -- or the moment T51 flags the match live --
        it is cancelled (never let a pre-match bid fill into live play). A flag walked
        back off reverts the bid to normal entry handling on the next pass."""
        if not self.completion_reprice or self.completion_disabled:
            await self._completion_revert(tk, pos, book, now,
                "flag_off" if not self.completion_reprice else "completion_disabled")
            return
        # [C-TRIPWIRE] V4: a resting completion order whose lookup cell is not in the
        # table (state corruption / table swap) -- fire; the tripwire cancels it.
        if (pos.category, pos.completion_lookup_cell) not in self.completion_cells:
            await self._completion_tripwire("V4_cell_not_in_table",
                {"site": "manage", "category": pos.category,
                 "cell": pos.completion_lookup_cell, "event": pos.event_ticker}, tk=tk)
            return
        if self._is_match_live(pos.event_ticker):
            await self._completion_revert(tk, pos, book, now, "match_live")
            return
        if pos.match_start_ts > 0 and now >= pos.match_start_ts:
            await self._completion_revert(tk, pos, book, now, "t0_reached")
            return
        if now - pos.completion_reprice_ts < V4_COMPLETION_FRESHNESS_SEC:
            return
        # re-evaluate s1 against the current book (s0 / X / leg-1 basis are frozen at
        # attempt time; only the ask clamp moves) and refresh qty to leg-1's CURRENT
        # filled qty (later partial leg-1 fills).
        sib_ask = book.best_ask if 0 < book.best_ask < 100 else None
        s1 = self._completion_target(pos.completion_s0, pos.completion_x, sib_ask,
                                     pos.completion_leg1_basis)
        if s1 <= pos.completion_s0 or s1 < 1:
            await self._completion_revert(tk, pos, book, now, "cap_headroom_gone")
            return
        leg1_tk = self._sibling_ticker(tk, pos.event_ticker)
        leg1 = self.positions.get(leg1_tk) if leg1_tk else None
        qty = leg1.entry_qty if (leg1 and leg1.entry_qty > 0) else pos.completion_qty
        if s1 == pos.entry_price and qty == pos.completion_qty:
            pos.completion_reprice_ts = now
            self._log("completion_freshness", {"event": pos.event_ticker, "s1": s1,
                "qty": qty, "sib_ask": sib_ask, "unchanged": True}, ticker=tk)
            return
        # fill-race discipline before the cancel/re-place
        old = await api_get(self.session, self.ak, self.pk,
            "/trade-api/v2/portfolio/orders/%s" % pos.entry_order_id, self.rl)
        if old:
            old_filled = int(float((old.get("order", old).get("fill_count_fp", 0)) or 0))
            if old_filled > 0:
                return  # filled -- check_fills books it (completion_fill path)
        price, po = self._reprice_target(s1, book.best_ask)
        if not po:
            # [C-TRIPWIRE] V1 at the freshness re-place site
            await self._completion_tripwire("V1_post_only_breach",
                {"site": "freshness", "s1": s1, "price": price,
                 "event": pos.event_ticker}, tk=tk)
            return
        # [C-P0-RACE site 8] residual window after the pre-poll: a raced completion
        # fill books (completion_fill + guards); the re-place is aborted.
        res = await self._cancel_entry_and_resolve(
            tk, pos, "completion_freshness_reprice", "completion_freshness_race")
        if res != "cancelled":
            return
        self.inflight_orders.add(tk)
        try:
            oid, _ = await self.place_order(tk, "buy", "yes", price, qty, post_only=po)
        finally:
            self.inflight_orders.discard(tk)
        if not oid:
            self._log("completion_reverted", {"event": pos.event_ticker,
                "reason": "place_failed",
                "time_since_reprice": round(now - pos.completion_reprice_ts, 1)}, ticker=tk)
            self._log_orphan_outcome(tk, pos, "place_failed", now)
            pos.entry_order_id = ""
            self._untombstone_entry(tk, pos)
            self._save_v4_resting()
            return
        old_s1 = pos.entry_price
        pos.entry_price = price
        pos.entry_order_id = oid
        pos.target_price = price
        pos.completion_qty = qty
        pos.completion_reprice_ts = now
        self._log("completion_freshness", {"event": pos.event_ticker, "old_s1": old_s1,
            "new_s1": price, "qty": qty, "sib_ask": sib_ask,
            "unchanged": False}, ticker=tk)
        self._save_v4_resting()

    async def _completion_revert(self, tk, pos, book, now, reason):
        """PART-2: cancel a resting completion bid and hand the leg back to normal
        rules, emitting the orphan_outcome snapshot (the no-completion arm of the
        wave-gate pairing). match_live / t0_reached -> cancel only (never re-place into
        live play; T51 semantics). Inside the T-15 buffer -> cancel only (a re-placed
        normal bid would be instantly buffer-cancelled -- pure churn). Otherwise
        re-place the pre-completion bid (maker-clamped) and restore the prior
        entry_mode so the standard machinery (incl. the T-15 buffer) resumes."""
        old = await api_get(self.session, self.ak, self.pk,
            "/trade-api/v2/portfolio/orders/%s" % pos.entry_order_id, self.rl)
        if old:
            old_filled = int(float((old.get("order", old).get("fill_count_fp", 0)) or 0))
            if old_filled > 0:
                return  # filled -- check_fills books it (completion_fill path)
        # [C-P0-RACE site 9] residual window after the pre-poll: a raced completion
        # fill books; the revert is moot. Unresolved retries next manage pass.
        res = await self._cancel_entry_and_resolve(
            tk, pos, "completion_revert_" + reason, "completion_revert_race")
        if res != "cancelled":
            return
        self._log("completion_reverted", {"event": pos.event_ticker, "reason": reason,
            "s0": pos.completion_s0, "s1": pos.entry_price, "x": pos.completion_x,
            "time_since_reprice": round(now - pos.completion_reprice_ts, 1)}, ticker=tk)
        self._log_orphan_outcome(tk, pos, reason, now)
        inside_buffer = (pos.match_start_ts > 0
                         and now > pos.match_start_ts - ENTRY_BUFFER_SEC)
        if reason in ("match_live", "t0_reached") or inside_buffer:
            pos.entry_order_id = ""
            self._untombstone_entry(tk, pos)
            self._save_v4_resting()
            return
        price, po = self._reprice_target(pos.completion_prev_price or 1, book.best_ask)
        self.inflight_orders.add(tk)
        try:
            oid, _ = await self.place_order(tk, "buy", "yes", price, self.entry_size,
                                            post_only=po)
        finally:
            self.inflight_orders.discard(tk)
        if not oid:
            pos.entry_order_id = ""
            self._untombstone_entry(tk, pos)
            self._save_v4_resting()
            return
        pos.entry_price = price
        pos.entry_order_id = oid
        # [C-BID-SURVIVAL DIFF-2] revert re-places at the PRE-completion price in
        # a possibly-moved book -- not a placement-time join; clear conservatively
        # so the full stale rule governs the reverted bid.
        pos.intended_join = False
        pos.entry_mode = pos.completion_prev_mode or "resting_maker"
        pos.play_type = "v4_" + pos.entry_mode
        pos.target_price = pos.completion_prev_target or price
        pos.completion_s0 = 0
        pos.completion_x = 0
        pos.completion_leg1_basis = 0
        pos.completion_qty = 0
        pos.completion_reprice_ts = 0.0
        pos.completion_prev_price = 0
        pos.completion_prev_mode = ""
        pos.completion_prev_target = 0
        pos.completion_lookup_cell = 0
        self._save_v4_resting()

    def _log_orphan_outcome(self, tk, pos, reason, now):
        """PART-2 item 7: terminal no-completion outcome snapshot. Captures BOTH legs'
        book + last-trade state at completion-bid termination so the T-20-frame orphan
        valuation is computable offline from day one (join vs completion_attempt and
        the existing settlement events; exit surface untouched). `tk`/`pos` are the
        SIBLING (completion) leg; leg-1 is the filled trigger leg."""
        et = pos.event_ticker
        leg1_tk = self._sibling_ticker(tk, et)
        leg1 = self.positions.get(leg1_tk) if leg1_tk else None

        def _snap(t):
            b = self.books.get(t) if t else None
            if not b:
                return None
            return {"bid": b.best_bid, "ask": b.best_ask,
                    "last_trade": b.last_trade_price,
                    "last_trade_age_sec": round(now - b.last_trade_ts, 1)
                                          if b.last_trade_ts else None}
        st = self.event_start_time.get(et, pos.match_start_ts or 0)
        self._log("orphan_outcome", {
            "event": et, "reason": reason,
            "leg1_ticker": (leg1_tk or "")[-20:],
            "leg1_basis": pos.completion_leg1_basis,
            "leg1_qty": leg1.entry_qty if leg1 else None,
            "s0": pos.completion_s0, "s1": pos.entry_price, "x": pos.completion_x,
            "time_to_start_min": round((st - now) / 60.0, 1) if st else None,
            "sibling_book": _snap(tk), "leg1_book": _snap(leg1_tk),
        }, ticker=tk)

    async def validate_resting_buys(self):
        """Cadence-gated cancel/repost for resting entry orders + deadline force-take."""
        now = time.time()
        for tk, pos in list(self.positions.items()):
            if pos.phase != "entry_resting" or not pos.entry_order_id:
                continue

            book = self.books.get(tk)
            if not book or book.updated < now - BOOK_STALENESS_SEC:
                self._log("validate_skip_stale_book", {
                    "book_age_sec": int(now - book.updated) if book else "missing",
                }, ticker=tk)
                continue

            # v4 resting bids are managed by the v4 manager (target-bid based,
            # not best-bid reprice / FV-anchor freshness).
            if pos.is_v4:
                await self._v4_manage_resting(tk, pos, book, now)
                continue

            # Legacy positions skip validation
            if pos.legacy:
                continue

            time_to_start = pos.match_start_ts - now if pos.match_start_ts > 0 else 99999
            spread = book.best_ask - book.best_bid

            # Immediate cancel conditions (no cadence gate)
            if spread > 2 or book.best_bid <= 0 or book.best_ask >= 100:
                await self.cancel_order(tk, pos.entry_order_id, "degenerate_cancel")
                self._log("stale_buy_cancel", {"reason": "degenerate_or_wide_spread",
                    "spread": spread, "bid": book.best_bid, "ask": book.best_ask}, ticker=tk)
                self._untombstone_entry(tk, pos)
                continue

            # Cancel if our price is far above current mid (falling knife protection)
            mid = (book.best_bid + book.best_ask) / 2.0
            if pos.entry_price > mid + STALE_BUY_DELTA:
                await self.cancel_order(tk, pos.entry_order_id, 'stale_buy_price_too_high')
                self._log('stale_buy_cancel', {
                    'reason': 'price_above_mid',
                    'our_price': pos.entry_price,
                    'current_mid': round(mid, 1),
                    'delta': round(pos.entry_price - mid, 1),
                }, ticker=tk)
                self._untombstone_entry(tk, pos)
                continue

            # Check anchor freshness — cancel if expired
            anchor_value, anchor_source, _ = self._resolve_anchor(tk, pos.event_ticker)
            if anchor_value is None:
                await self.cancel_order(tk, pos.entry_order_id, "anchor_expired")
                self._log("stale_buy_cancel", {"reason": "anchor_expired"}, ticker=tk)
                self._untombstone_entry(tk, pos)
                continue

            # Deadline force-take at T-16 min
            if 955 <= time_to_start <= 965:
                kalshi_mid = (book.best_bid + book.best_ask) / 2.0
                if kalshi_mid < anchor_value and spread <= 2 and book.best_bid > 0 and book.best_ask < 100:
                    await self.cancel_order(tk, pos.entry_order_id, "deadline_force_take")
                    self.inflight_orders.add(tk)
                    try:
                        oid, _ = await self.place_order(tk, "buy", "yes", book.best_ask,
                            self.config["sizing"]["entry_contracts"], post_only=False)
                    finally:
                        self.inflight_orders.discard(tk)
                    pos.entry_price = book.best_ask
                    pos.entry_order_id = oid
                    pos.play_type = "deadline_force_take"
                    self._log("deadline_force_take", {
                        "old_price": pos.entry_price, "take_price": book.best_ask,
                        "anchor": round(anchor_value, 1), "kalshi_mid": round(kalshi_mid, 1),
                        "time_to_start": round(time_to_start),
                    }, ticker=tk)
                    continue

            # Cadence-gated cancel/repost
            cadence = 60
            if now - pos.last_cancel_repost_ts < cadence:
                continue

            # Reprice to current best_bid if different
            target = book.best_bid
            if target != pos.entry_price and target > 0 and target < 100:
                await self.cancel_order(tk, pos.entry_order_id, "cadence_repost")
                # Check if old order filled before placing replacement
                old_order = await api_get(self.session, self.ak, self.pk,
                    "/trade-api/v2/portfolio/orders/%s" % pos.entry_order_id, self.rl)
                if old_order:
                    old_filled = int(float((old_order.get("order", old_order).get("fill_count_fp", 0)) or 0))
                    if old_filled > 0:
                        pos.entry_qty = old_filled
                        pos.phase = "active"
                        pos.entry_filled_ts = time.time()
                        # Re-classify cell based on fill price
                        old_cell = pos.cell_name
                        old_exit_cents = pos.cell_cfg.get("exit_cents", 0) if pos.cell_cfg else 0
                        fill_cell, fill_cell_cfg = self._legacy_cell_lookup(pos.category, pos.direction, pos.entry_price)
                        if fill_cell != old_cell:
                            if fill_cell_cfg is None:
                                fill_cell_cfg = {"exit_cents": 15, "strategy": pos.cell_cfg.get("strategy", "noDCA")}
                                self._log("cell_drift_to_inactive", {
                                    "old_cell": old_cell, "new_cell": fill_cell,
                                    "anchor_price": pos.entry_price, "fill_price": pos.entry_price,
                                    "drift_cents": 0,
                                    "old_exit_cents": old_exit_cents, "new_exit_cents": 15,
                                    "direction": pos.direction,
                                }, ticker=tk)
                            else:
                                self._log("cell_reclassified", {
                                    "old_cell": old_cell, "new_cell": fill_cell,
                                    "anchor_price": pos.entry_price, "fill_price": pos.entry_price,
                                    "drift_cents": 0,
                                    "old_exit_cents": old_exit_cents,
                                    "new_exit_cents": fill_cell_cfg["exit_cents"],
                                    "direction": pos.direction,
                                }, ticker=tk)
                            pos.cell_name = fill_cell
                            pos.cell_cfg = fill_cell_cfg
                        self._log("cadence_repost_fill_detected", {
                            "filled_qty": old_filled, "price": pos.entry_price,
                        }, ticker=tk)
                        continue
                self.inflight_orders.add(tk)
                try:
                    oid, _ = await self.place_order(tk, "buy", "yes", target,
                        self.config["sizing"]["entry_contracts"])
                finally:
                    self.inflight_orders.discard(tk)
                old = pos.entry_price
                pos.entry_price = target
                pos.entry_order_id = oid
                pos.last_cancel_repost_ts = now
                self._log("cadence_repost", {
                    "old_price": old, "new_price": target,
                    "anchor": round(anchor_value, 1), "cadence_sec": cadence,
                    "time_to_start_min": round(time_to_start / 60),
                }, ticker=tk)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    def print_summary(self):
        elapsed_hr = (time.time() - self.start_ts) / 3600
        settled = [p for p in self.positions.values() if p.settled]
        total_pnl = sum(p.pnl_cents for p in settled)
        active = [p for p in self.positions.values() if not p.settled]

        print("\n" + "=" * 70, flush=True)
        print("LIVE V3 SUMMARY  (%.1f hours)" % elapsed_hr, flush=True)
        print("=" * 70, flush=True)
        print("  Matches seen:     %d" % self.n_matches_seen, flush=True)
        print("  Entries posted:   %d" % len(self.positions), flush=True)
        print("  Entries filled:   %d" % self.n_entries, flush=True)
        print("  Exits filled:     %d" % self.n_exits, flush=True)
        print("  DCAs filled:      %d" % self.n_dcas, flush=True)
        print("  Settlements:      %d" % self.n_settlements, flush=True)
        print("  Active positions: %d" % len(active), flush=True)
        print("  Total P&L:        %.1fc = $%.2f" % (total_pnl, total_pnl / 100.0), flush=True)
        print("  Skipped:          %d" % self.n_skips, flush=True)

        cell_pnl = defaultdict(lambda: {"n": 0, "pnl": 0})
        for p in settled:
            c = cell_pnl[p.cell_name]
            c["n"] += 1
            c["pnl"] += p.pnl_cents
        if cell_pnl:
            print("\n  Per-cell:", flush=True)
            for cell in sorted(cell_pnl.keys()):
                c = cell_pnl[cell]
                print("    %-35s N=%d  P&L=%.1fc" % (cell, c["n"], c["pnl"]), flush=True)

        if active:
            print("\n  Active:", flush=True)
            for p in active:
                book = self.books.get(p.ticker)
                cur_mid = (book.best_bid + book.best_ask) / 2.0 if book else 0
                print("    %-40s entry=%dc exit=%dc mid=%.0fc %s" % (
                    p.ticker[:40], p.entry_price, p.exit_price, cur_mid, p.phase), flush=True)
        print("=" * 70, flush=True)
        self._log("summary", {
            "elapsed_hr": round(elapsed_hr, 1),
            "matches_seen": self.n_matches_seen, "entries": self.n_entries,
            "exits": self.n_exits, "dcas": self.n_dcas,
            "settlements": self.n_settlements, "active": len(active),
            "total_pnl_cents": total_pnl, "skips": self.n_skips,
        })

    # ------------------------------------------------------------------
    # Startup reconciliation: sync in-memory state with Kalshi account
    # ------------------------------------------------------------------
    async def _v4_reconcile_naked(self, tk, et, cat, avg, pinfo,
                                  context="steady_state_reconcile"):
        """v4 restart recovery for a naked open position (no resting sell).

        [C-P0-RACE STEP 5] Adoption routes through _book_v4_entry_fill so an
        adopted entry fill gets the SAME booking as a polled fill: entry_filled
        emission, hold-aware exit application (replaces the old inline
        reconcile_v4_hold / reconcile_v4_exit_posted paths), and -- closing the
        live 96-minute cap hole -- the sibling/T50 cap check (adopted leg @69c +
        sibling resting @31c = 100 > 99 cancels the sibling; same action as live
        T50). STEP 6 (V5): while the completion flag is ON, every adopted entry
        fill logs completion_booking_adoption -- a fill reached us through
        reconcile means the booking sites were bypassed upstream (visibility,
        not a kill; steady_state_reconcile is the alert case).
        An existing resting sell still LINKS as before (already-booked restart
        path -- no booking, no exit cancel/repost churn)."""
        qty = pinfo["qty"]
        # [C-COPILOT] attribution via the bot's own order-id/ticker registry:
        # a naked position on a ticker the bot never ordered (or whose resting
        # bid we observed as foreign) is the OPERATOR'S -- unknown = manual by
        # definition. Booked at the FILL cell through the same proven path.
        manual = bool(getattr(self, "operator_manual_mode", False)
                      and (tk in getattr(self, "manual_bids", {})
                           or tk not in getattr(self, "_bot_order_tickers", set())))
        if manual:
            getattr(self, "manual_bids", {}).pop(tk, None)
        play = "v4_manual" if manual else "v4_reconciled"
        cell_id = self.cell_lookup(ITF_EXIT_BORROW.get(cat, cat), avg)
        band_x, rule = self.exit_rule_for(cat, avg)
        if rule != "hold":
            fresh = await api_get(self.session, self.ak, self.pk,
                "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
            fresh_sells = [o for o in (fresh or {}).get("orders", []) if o.get("action") == "sell"]
            if fresh_sells:
                sp = round(float(fresh_sells[0].get("yes_price_dollars", "0")) * 100)
                self.positions[tk] = Position(
                    ticker=tk, event_ticker=et, category=cat, direction="",
                    cell_name="", cell_cfg={}, entry_price=avg, entry_qty=qty,
                    phase="active", entry_filled_ts=time.time(),
                    is_v4=True, exit_cell_id=cell_id, play_type=play,
                    strategy="exit", exit_band_x=band_x,
                    exit_price=sp, exit_order_id=fresh_sells[0].get("order_id", ""))
                self._log("reconcile_v4_exit_found", {
                    "exit_price": sp, "cell_id": cell_id}, ticker=tk)
                return
        pos = Position(
            ticker=tk, event_ticker=et, category=cat, direction="",
            cell_name="", cell_cfg={}, entry_price=avg, entry_qty=0,
            phase="entry_resting", is_v4=True, exit_cell_id=cell_id,
            play_type=play)
        self.positions[tk] = pos
        _mst = self.event_start_time.get(et, 0)
        self._log("reconcile_v4_adopted", {
            "cell_id": cell_id, "avg": avg, "qty": qty, "rule": rule,
            "context": context,
            # [C-COPILOT] ledger attribution (Plex test 2)
            "attribution": "manual" if manual else "reconciled",
            "category": cat,
            # [C-FV-OBSERVE-SHIP] calibration anatomy per adoption row
            **(self._fv_observe_fields(et, tk, "", avg,
                                       bool(_mst and time.time() > _mst))
               if getattr(self, "fv_observe", False) else {}),
            }, ticker=tk)
        if self.completion_reprice:
            self._log("completion_booking_adoption", {
                "event": et, "avg": avg, "qty": qty, "context": context}, ticker=tk)
        await self._book_v4_entry_fill(tk, pos, qty, avg, "adopted",
                                       source="reconcile_adoption")

    async def reconcile(self, quiet=False):
        """Load existing positions and resting orders from Kalshi.
        Populate in-memory state so the bot doesn't re-enter or orphan orders.
        quiet=True suppresses the full report (for periodic 60s runs)."""
        if not quiet:
            print("\n[RECONCILE] Loading account state from Kalshi...", flush=True)

        # 1. Fetch positions
        pos_path = "/trade-api/v2/portfolio/positions?count_filter=position&settlement_status=unsettled"
        pos_data = await api_get(self.session, self.ak, self.pk, pos_path, self.rl)
        positions = (pos_data or {}).get("market_positions", [])

        pos_map = {}  # ticker -> {qty, avg_price, event_ticker}
        for p in positions:
            tk = p.get("ticker", "")
            qty = int(float(p.get("position_fp", 0)))
            total = float(p.get("market_exposure_dollars", p.get("total_traded_dollars", 0))) * 100  # cents
            avg_price = int(total / qty) if qty > 0 else 0
            et = self.ticker_to_event.get(tk, "")
            if not et:
                parts = tk.rsplit("-", 1)
                et = parts[0] if len(parts) == 2 else ""
            pos_map[tk] = {"qty": qty, "avg_price": avg_price, "event_ticker": et}

        # 2. Fetch resting orders
        ord_path = "/trade-api/v2/portfolio/orders?status=resting"
        ord_data = await api_get(self.session, self.ak, self.pk, ord_path, self.rl)
        resting = (ord_data or {}).get("orders", [])

        ord_map = {}  # ticker -> list of orders
        for o in resting:
            tk = o.get("ticker", "")
            price_raw = o.get("yes_price_dollars", o.get("yes_price", "0"))
            price_cents = round(float(price_raw) * 100) if float(price_raw) < 2 else int(price_raw)
            qty_raw = o.get("remaining_count_fp", o.get("remaining_count", o.get("initial_count_fp", 0)))
            entry = {
                "order_id": o.get("order_id", ""),
                "action": o.get("action", ""),
                "side": o.get("side", ""),
                "price": price_cents,
                "qty": int(float(qty_raw or 0)),
            }
            ord_map.setdefault(tk, []).append(entry)

        # 3. Link positions to exits and populate bot state
        linked = []
        unmanaged = []
        reconcile_exits = []
        orphan_orders = []

        for tk, pinfo in pos_map.items():
            await asyncio.sleep(0)  # FIX 3: yield per position so reconcile can't block the loop
            et = pinfo["event_ticker"]
            sells = [o for o in ord_map.get(tk, []) if o["action"] == "sell"]

            existing = self.positions.get(tk)
            if existing and existing.entry_price > 0:
                # [C-RIDE-LIVE-RACE-FIX] An exchange position on a leg the bot
                # still tracks as a RESTING entry bid (phase entry_resting, the
                # fill not yet booked) is a clamp/maker bid that filled while
                # this reconcile -- not check_fills -- reached it first. The old
                # path bumped entry_qty 0->N and `continue`d WITHOUT booking or
                # posting the exit, which permanently blocked check_fills
                # (filled N > entry_qty N == False) and skipped the naked
                # adoption below the continue (the live MARITO/SINYUA/BERJAN/
                # OKOGRE naked legs, 2026-06-13; premarket_bids_ride_live kept
                # the clamp resting long enough for the 60s reconcile to win the
                # race). Route the fill through the proven naked-recovery path:
                # it BOOKS via _book_v4_entry_fill (idempotent) and posts the
                # cell exit at filled size, or ADOPTS an existing resting sell
                # (the operator's manual exit, copilot mode) instead of double-
                # posting. Order-independent: check_fills-first leaves
                # phase=active, so this guard is skipped and the link path below
                # runs instead; reconcile-first books here. Either poller that
                # reaches the fill first now books it.
                if (existing.phase == "entry_resting"
                        and pinfo["qty"] > existing.entry_qty
                        and not existing.exit_order_id):
                    _cat = self.get_category(tk) or existing.category or "?"
                    if not self.fv_scenarios_enabled and (
                            _cat in self.categories_enabled
                            or _cat in ITF_VISIBILITY_CATS):
                        await self._v4_reconcile_naked(
                            tk, et, _cat, pinfo["avg_price"], pinfo,
                            context=("steady_state_reconcile" if quiet
                                     else "boot_reconcile"))
                        continue
                kalshi_avg = pinfo["avg_price"]
                if abs(kalshi_avg - existing.entry_price) > 1:
                    self._log("reconcile_price_mismatch", {
                        "bot_entry_price": existing.entry_price,
                        "kalshi_avg_price": kalshi_avg,
                        "delta": kalshi_avg - existing.entry_price,
                        "entry_qty": existing.entry_qty,
                        "kalshi_qty": pinfo["qty"],
                    }, ticker=tk)
                if pinfo["qty"] > existing.entry_qty:
                    existing.entry_qty = pinfo["qty"]
                if sells and not existing.exit_order_id:
                    existing.exit_order_id = sells[0]["order_id"]
                    existing.exit_price = sells[0]["price"]
                continue

            if sells:
                sell = sells[0]
                total_sell_qty = sum(s["qty"] for s in sells)
                cat = self.get_category(tk) or "?"
                pos = Position(
                    ticker=tk, event_ticker=et, category=cat,
                    direction="reconciled", cell_name="reconciled",
                    cell_cfg={}, entry_price=pinfo["avg_price"],
                    entry_qty=pinfo["qty"], phase="active",
                    exit_price=sell["price"], exit_order_id=sell["order_id"],
                    entry_filled_ts=time.time(),
                    legacy=True, play_type="A_legacy",
                )
                self.positions[tk] = pos
                linked.append((tk, pinfo, sell))
                # Check qty gap — position may have more contracts than sell covers
                naked_qty = pinfo["qty"] - total_sell_qty
                if naked_qty > 0:
                    exit_price = sell["price"]  # same price as existing sell
                    fresh = await api_get(self.session, self.ak, self.pk,
                        "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
                    fresh_sell_qty = sum(int(float(o.get("remaining_count_fp", 0) or 0))
                        for o in (fresh or {}).get("orders", []) if o.get("action") == "sell")
                    actual_naked = pinfo["qty"] - fresh_sell_qty
                    if actual_naked > 0:
                        # Cancel existing sells and repost consolidated
                        for old_sell in (fresh or {}).get("orders", []):
                            if old_sell.get("action") == "sell":
                                await self.cancel_order(tk, old_sell.get("order_id", ""), "reconcile_consolidate")
                        oid, resp = await self.place_order(tk, "sell", "yes", exit_price, pinfo["qty"])
                        reconcile_exits.append((tk, pinfo, exit_price, "qty_gap_consolidated", oid))
                        self._log("reconcile_exit_posted", {
                            "reason": "qty_gap_consolidated", "exit_price": exit_price,
                            "position_qty": pinfo["qty"],
                            "order_id": oid,
                        }, ticker=tk)
                # Check DCA coverage for DCA-A cells
                avg = pinfo["avg_price"]
                direction = "leader" if avg > 50 else "underdog"
                if cat and cat != "?":
                    dca_cell_name, dca_cell_cfg = self._legacy_cell_lookup(cat, direction, avg)
                    if dca_cell_cfg and dca_cell_cfg.get("strategy") == "DCA-A":
                        dca_trigger = dca_cell_cfg.get("dca_trigger_cents", 0)
                        dca_price = avg - dca_trigger
                        if dca_price >= self.dca_fill_floor:
                            # FIX 1: strict any-resting-buy guard (no price proximity check)
                            fresh_buys = await api_get(self.session, self.ak, self.pk,
                                "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
                            any_resting_buy = any(o.get("action") == "buy"
                                for o in (fresh_buys or {}).get("orders", []))
                            if not any_resting_buy:
                                # FIX 2: DCA qty = min(5, position_qty)
                                dca_qty = min(self.dca_size, pinfo["qty"])
                                dca_oid, _ = await self.place_order(tk, "buy", "yes", dca_price, dca_qty)
                                reconcile_exits.append((tk, pinfo, dca_price, "dca_missing", dca_oid))
                                self._log("reconcile_dca_posted", {
                                    "dca_price": dca_price, "qty": dca_qty,
                                    "position_qty": pinfo["qty"],
                                    "cell": dca_cell_name, "order_id": dca_oid,
                                }, ticker=tk)
            else:
                # No exit sell — try to auto-post one
                cat = self.get_category(tk)
                avg = pinfo["avg_price"]
                # v4: use the adaptive exit band table (hold-skip aware). Avoids
                # posting an unwanted exit on a hold-cell position after restart.
                # [C-COPILOT ITF] visibility categories adopt manual fills too
                # (borrowed Challenger exit surface); placement stays excluded.
                if not self.fv_scenarios_enabled and (
                        cat in self.categories_enabled or cat in ITF_VISIBILITY_CATS):
                    await self._v4_reconcile_naked(tk, et, cat, avg, pinfo,
                        context=("steady_state_reconcile" if quiet else "boot_reconcile"))
                    continue
                direction = "leader" if avg > 50 else "underdog"
                if cat:
                    cell_name, cell_cfg = self._legacy_cell_lookup(cat, direction, avg)
                else:
                    cell_name, cell_cfg = None, None

                if cell_cfg:
                    exit_price = min(avg + cell_cfg["exit_cents"], EXIT_PRICE_CAP)
                    # Fresh Kalshi check: verify no resting sell already exists
                    fresh = await api_get(self.session, self.ak, self.pk,
                        "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
                    fresh_sells = [o for o in (fresh or {}).get("orders", []) if o.get("action") == "sell"]
                    if fresh_sells:
                        sell = {"order_id": fresh_sells[0].get("order_id", ""),
                                "price": round(float(fresh_sells[0].get("yes_price_dollars", "0")) * 100)}
                        pos = Position(
                            ticker=tk, event_ticker=et, category=cat or "?",
                            direction=direction, cell_name=cell_name, cell_cfg=cell_cfg,
                            entry_price=avg, entry_qty=pinfo["qty"], phase="active",
                            exit_price=sell["price"], exit_order_id=sell["order_id"],
                            entry_filled_ts=time.time(),
                            legacy=True, play_type="A_legacy",
                        )
                        self.positions[tk] = pos
                        linked.append((tk, pinfo, sell))
                        self._log("reconcile_exit_found_fresh", {
                            "ticker": tk, "exit_price": sell["price"],
                        }, ticker=tk)
                    else:
                        oid, resp = await self.place_order(tk, "sell", "yes", exit_price, pinfo["qty"])
                        pos = Position(
                            ticker=tk, event_ticker=et, category=cat or "?",
                            direction=direction, cell_name=cell_name, cell_cfg=cell_cfg,
                            entry_price=avg, entry_qty=pinfo["qty"], phase="active",
                            exit_price=exit_price, exit_order_id=oid,
                            entry_filled_ts=time.time(),
                            legacy=True, play_type="A_legacy",
                        )
                        self.positions[tk] = pos
                        reconcile_exits.append((tk, pinfo, exit_price, cell_name, oid))
                        self._log("reconcile_exit_posted", {
                            "exit_price": exit_price, "qty": pinfo["qty"],
                            "avg_price": avg, "cell": cell_name,
                            "exit_cents": cell_cfg["exit_cents"],
                            "order_id": oid,
                        }, ticker=tk)
                else:
                    unmanaged.append((tk, pinfo))
                    reason = "cell disabled" if cell_name and cell_name in self.config.get("disabled_cells", []) else "no cell config"
                    self._log("reconcile_orphan_no_cell", {
                        "ticker": tk, "avg_price": avg, "cell": cell_name or "?",
                        "reason": reason,
                    }, ticker=tk)

        # Check for orphan resting orders (not matched to any position)
        for tk, orders in ord_map.items():
            if tk not in pos_map:
                # Skip tickers the bot is actively managing in entry_resting phase
                in_memory_pos = self.positions.get(tk)
                if in_memory_pos and in_memory_pos.phase == "entry_resting":
                    continue
                for o in orders:
                    orphan_orders.append((tk, o))

        # Cancel orphan resting buys so bot can re-discover cleanly.
        # [C-COPILOT HOTFIX, operator-directed 2026-06-12] operator_manual_mode
        # (deploy true): an unrecognized resting BUY on a mapped ticker is the
        # OPERATOR'S (the sweep killed his RADRAK-RAK re-posts on every
        # reconcile pass today, 14:59:34 + 15:01:35 ET) -> LEAVE RESTING, log
        # manual_bid_observed once per order id. Full copilot adoption follows.
        for tk, o in orphan_orders:
            if o["action"] == "buy":
                oid = o.get("order_id", "")
                # [C-COPILOT] adopted-as-foreign: an unrecognized resting buy
                # (id not in the bot's own registry) is the OPERATOR'S --
                # tracked, left resting, observed once. A bot-registry id in
                # the orphan list is a bot bug and keeps the legacy cancel.
                if (getattr(self, "operator_manual_mode", False)
                        and oid not in getattr(self, "_bot_order_ids", set())):
                    mb = getattr(self, "manual_bids", None)
                    if mb is None:
                        mb = self.manual_bids = {}
                    if mb.get(tk, {}).get("order_id") != oid:
                        mb[tk] = {"order_id": oid, "price": o["price"],
                                  "qty": o["qty"], "first_seen": time.time()}
                        _met = tk.rsplit("-", 1)[0]
                        _mst = self.event_start_time.get(_met, 0)
                        self._log("manual_bid_observed", {
                            "price": o["price"], "qty": o["qty"],
                            "order_id": oid,
                            # [C-FV-OBSERVE-SHIP] calibration anatomy per row
                            **(self._fv_observe_fields(
                                _met, tk, "", o["price"],
                                bool(_mst and time.time() > _mst))
                               if getattr(self, "fv_observe", False) else {}),
                            }, ticker=tk)
                    continue
                await self.cancel_order(tk, o["order_id"], "orphan_buy_reconcile_cleanup")
                self._log("orphan_buy_cancelled", {
                    "price": o["price"], "qty": o["qty"],
                }, ticker=tk)

        # [C-COPILOT] operator-cancel reconciliation (Plex test 3): a tracked
        # manual bid that is no longer resting and produced NO position means
        # the operator pulled his own order -> untrack cleanly, never attempt
        # an orphan exit. A fill instead surfaces as a position and the
        # adoption path books it (manual_bids popped there).
        if getattr(self, "operator_manual_mode", False):
            mb = getattr(self, "manual_bids", None) or {}
            for mtk in list(mb):
                info = mb[mtk]
                still = any(x.get("order_id") == info["order_id"]
                            for x in ord_map.get(mtk, []))
                if still or mtk in pos_map:
                    continue
                mb.pop(mtk, None)
                self._log("manual_bid_withdrawn", {
                    "order_id": info["order_id"], "price": info["price"],
                    "qty": info["qty"]}, ticker=mtk)

        self._save_processed()

        # 4. Print reconciliation report
        if not quiet:
            print("\n" + "=" * 70, flush=True)
            print("RECONCILIATION REPORT", flush=True)
            print("=" * 70, flush=True)

            print("\nPositions found: %d" % len(pos_map), flush=True)
            for tk, p in sorted(pos_map.items()):
                print("  %-45s qty=%d  avg=%dc" % (tk[:45], p["qty"], p["avg_price"]), flush=True)

            print("\nResting orders found: %d" % len(resting), flush=True)
            for o in resting:
                pr = o.get("yes_price_dollars", o.get("yes_price", "0"))
                pc = round(float(pr) * 100) if float(pr) < 2 else int(pr)
                qr = o.get("remaining_count_fp", o.get("remaining_count", o.get("initial_count_fp", 0)))
                print("  %-45s %s %s price=%dc qty=%d oid=%s" % (
                    o.get("ticker","")[:45], o.get("action",""), o.get("side",""),
                    pc, int(float(qr or 0)),
                    o.get("order_id","")[:12]), flush=True)

            print("\nLinked (position + exit): %d" % len(linked), flush=True)
            for tk, p, s in linked:
                print("  %-45s qty=%d entry=%dc exit=%dc oid=%s" % (
                    tk[:45], p["qty"], p["avg_price"], s["price"], s["order_id"][:12]), flush=True)

        # Always print reconcile exits (even in quiet mode — these are actions)
        if reconcile_exits:
            print("\n[RECONCILE] Exits auto-posted: %d" % len(reconcile_exits), flush=True)
            for tk, p, ep, cell, oid in reconcile_exits:
                print("  [EXIT_POSTED] %-35s avg=%dc exit=%dc cell=%s oid=%s" % (
                    tk[:35], p["avg_price"], ep, cell, oid[:12]), flush=True)

        if not quiet:
            print("\nUnmanaged (position, NO exit, no cell): %d" % len(unmanaged), flush=True)
            for tk, p in unmanaged:
                print("  [ORPHAN_NO_CELL] %-35s qty=%d avg=%dc" % (tk[:35], p["qty"], p["avg_price"]), flush=True)

            print("\nOrphan orders (no position): %d" % len(orphan_orders), flush=True)
            for tk, o in orphan_orders:
                print("  [ORPHAN] %-39s %s price=%s oid=%s" % (
                    tk[:39], o["action"], o["price"], o["order_id"][:12]), flush=True)

            print("\nProcessed events: %d" % len(self.processed_events), flush=True)
            print("=" * 70, flush=True)

        self._log("reconcile", {
            "positions": len(pos_map),
            "resting_orders": len(resting),
            "linked": len(linked),
            "reconcile_exits_posted": len(reconcile_exits),
            "unmanaged": len(unmanaged),
            "orphans": len(orphan_orders),
            "processed_events": len(self.processed_events),
        })

        return len(pos_map), len(linked), len(unmanaged), len(orphan_orders)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def _install_signal_handlers(self):
        """#0-infra: install asyncio SIGTERM/SIGINT handlers for clean shutdown (gated by
        graceful_shutdown). add_signal_handler is the asyncio-safe path -- the bare
        `except KeyboardInterrupt` is unreliable under asyncio 3.12 (SIGINT was swallowed).
        Defensive: NEVER crashes startup -- a failure (non-Unix / no running loop) logs a warning
        and the process runs on the legacy terminate path. signal is imported lazily (Unix-only;
        keeps the module importable on Windows for the test suite)."""
        import signal as _signal
        try:
            loop = asyncio.get_running_loop()
            for _sig in (_signal.SIGTERM, _signal.SIGINT):
                loop.add_signal_handler(_sig, self._request_shutdown, _sig.name)
            print("[BOOT] graceful_shutdown=on -> SIGTERM/SIGINT handlers installed "
                  "(cancel resting entry bids, %ds budget)" % V4_SHUTDOWN_TIMEOUT_SEC, flush=True)
        except Exception as e:
            print("[BOOT] WARN: signal handlers not installed (%r) -- legacy shutdown path" % (e,), flush=True)

    def _request_shutdown(self, signame):
        """#0-infra: signal-handler callback (runs on the loop thread; no I/O here). Idempotent:
        the FIRST signal requests a graceful drain and arms the force-exit watchdog; a SECOND
        signal escalates to immediate hard exit (do not wait for a wedged drain). os._exit skips
        atexit/buffers -- safe here because the drain writes no in-place state (cancel-only)."""
        if self._shutdown_requested:
            print("[STOP] second %s -> hard exit" % signame, flush=True)
            os._exit(1)
        self._shutdown_requested = True
        print("[STOP] %s received -> graceful shutdown (%ds budget)" % (signame, V4_SHUTDOWN_TIMEOUT_SEC), flush=True)
        try:
            asyncio.get_running_loop().call_later(V4_SHUTDOWN_TIMEOUT_SEC, self._force_exit)
        except Exception:
            os._exit(1)

    def _force_exit(self):
        """#0-infra: hard-deadline backstop. If the graceful drain wedges (API hang / deadlock),
        exit rather than sit in a zombie 'shutting down' state. persist-or-die, not persist-forever."""
        print("[STOP] shutdown budget (%ds) exceeded -> hard exit" % V4_SHUTDOWN_TIMEOUT_SEC, flush=True)
        os._exit(1)

    async def _shutdown_drain(self):
        """#0-infra: clean cancel-and-exit. Cancel all resting v4 ENTRY bids via the API, then let
        run() close the session and return. Resting EXIT orders on open positions are LEFT (they
        protect the position). Orphan-cancel is already benign (0 naked exposure) -- this just makes
        the next boot's reconcile a no-op. Never raises; bounded by the _force_exit watchdog. Writes
        no in-place state (cancel-only), so a mid-drain hard exit cannot corrupt state."""
        try:
            resting = [(tk, pos.entry_order_id) for tk, pos in list(self.positions.items())
                       if getattr(pos, "is_v4", False) and pos.phase == "entry_resting" and pos.entry_order_id]
        except Exception as e:
            self._log("shutdown_drain_fatal", {"error": str(e)})
            return
        self._log("shutdown_drain_begin", {"resting_entry_bids": len(resting)})
        _t0 = time.time()
        n_ok = 0
        for tk, oid in resting:
            try:
                if await self.cancel_order(tk, oid, "shutdown_cancel"):
                    n_ok += 1
            except Exception as e:
                self._log("shutdown_cancel_error", {"ticker": tk, "error": str(e)})
        # #0-infra observability (#2-#5 rollout): pre-count + cancel-count + drain duration.
        # exit code + post-boot reconcile-orphans are captured by the restart wrapper / next boot.
        self._log("shutdown_drain_done", {"attempted": len(resting), "cancelled": n_ok,
                                          "duration_sec": round(time.time() - _t0, 3)})

    async def run(self, reconcile_only=False):
        mode = "PAPER" if _PAPER_API is not None else "LIVE - REAL ORDERS"
        print("=" * 70, flush=True)
        print("LIVE V4 - BID-LAYING EXECUTOR - %s" % mode, flush=True)
        print("=" * 70, flush=True)
        print("Config: %s" % CONFIG_PATH, flush=True)
        if self.fv_scenarios_enabled:
            print("Mode: LEGACY FV-anchor scenarios (active=%d disabled=%d)" % (
                len(self.config.get("active_cells", {})),
                len(self.config.get("disabled_cells", []))), flush=True)
        else:
            print("Mode: v4 bid-laying  |  entry rows: %d  |  categories: %s" % (
                len(self.entry_table), ",".join(sorted(self.categories_enabled))), flush=True)
            print("Exit bands/cat: %s" % {c: len(self.exit_table.get(c, {}))
                for c in sorted(self.categories_enabled)}, flush=True)
        print("Entry: %d contracts  Exit: %d contracts" % (self.entry_size, self.exit_size), flush=True)
        print("Exit cap: %dc" % EXIT_PRICE_CAP, flush=True)
        print("Log: %s" % self.log_path, flush=True)
        print("=" * 70, flush=True)

        self.session = aiohttp.ClientSession()

        # #0-infra: install clean-shutdown signal handlers (gated; default off = legacy terminate).
        if self.graceful_shutdown:
            self._install_signal_handlers()

        if not await self.ws_connect():
            print("[FATAL] Cannot connect WebSocket", flush=True)
            return

        tickers = await self.discover_markets()
        if tickers:
            await self.ws_subscribe(tickers)

        # Reconcile: load existing positions and resting orders
        await self.reconcile()

        # v4: rebuild any persisted resting bids reconcile didn't link (STEP 5)
        self._load_v4_resting()

        # Startup skip: events inside the 15-min buffer or past start
        now = time.time()
        startup_skipped = 0
        for evt, start_ts in self.event_start_time.items():
            if evt not in self.processed_events and (start_ts - now) <= ENTRY_BUFFER_SEC:
                self.processed_events.add(evt)
                startup_skipped += 1

        # Expire old tombstones: remove events with dates >24h in the past
        import re as _tomb_re
        _month_map = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
                      "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
        expired = set()
        for evt in list(self.processed_events):
            m = _tomb_re.search(r"-(\d{2})([A-Z]{3})(\d{2})", evt)
            if not m:
                continue
            try:
                evt_date = datetime(2000 + int(m.group(1)), _month_map[m.group(2)], int(m.group(3)),
                                    tzinfo=timezone.utc)
                if (datetime.now(timezone.utc) - evt_date).total_seconds() > 86400:
                    expired.add(evt)
            except Exception:
                pass
        if expired:
            self.processed_events -= expired
            startup_skipped -= len(expired)  # net out

        if startup_skipped > 0:
            self._save_processed()

        # Startup validation
        now_et = datetime.fromtimestamp(now, tz=ET)
        print("\n[TIME] %s" % now_et.strftime("%Y-%m-%d %I:%M:%S %p ET"), flush=True)

        total_events = len(self.event_tickers)
        matched = len(self.event_start_time)
        unmatched = sum(1 for et in self.event_tickers if et not in self.event_start_time and et not in self.processed_events)
        print("[SCHED] Kalshi events: %d  Schedule-matched: %d  Unmatched: %d  Already-processed: %d" % (
            total_events, matched, unmatched, len(self.processed_events)), flush=True)
        print("[INIT] Skipped %d stale events at startup" % startup_skipped, flush=True)

        # Next 5 matches bot is waiting on
        # Event status report
        all_events_status = []
        for evt in sorted(self.event_tickers.keys()):
            players = ", ".join(self.event_player_names.get(evt, ["?"]))
            if evt in self.processed_events:
                all_events_status.append((evt, "PROCESSED", 0, "", players))
                continue
            start_ts = self.event_start_time.get(evt)
            if start_ts is None:
                all_events_status.append((evt, "UNMATCHED", 0, "", players))
                continue
            time_to_start = start_ts - now
            start_str = datetime.fromtimestamp(start_ts, tz=ET).strftime("%I:%M %p ET")
            cutoff = datetime.fromtimestamp(start_ts - ENTRY_BUFFER_SEC, tz=ET).strftime("%I:%M %p ET")
            if time_to_start > _entry_lead_cap(evt):
                all_events_status.append((evt, "WAIT (>24h)", time_to_start, start_str, players))
            elif time_to_start > ENTRY_BUFFER_SEC:
                all_events_status.append((evt, "ENTER", time_to_start, "eligible until %s, start=%s" % (cutoff, start_str), players))
            else:
                all_events_status.append((evt, "SKIP (buffer)", time_to_start, start_str, players))

        print("\n[EVENTS] All discovered events:", flush=True)
        for evt, status, secs, detail, players in all_events_status:
            if status == "PROCESSED":
                print("  %-40s  PROCESSED  [%s]" % (evt[:40], players[:30]), flush=True)
            elif status == "ENTER":
                print("  %-40s  ENTER  %s  [%s]" % (evt[:40], detail, players[:30]), flush=True)
            elif status == "WAIT (>24h)":
                print("  %-40s  WAIT  >24h to start=%s  [%s]" % (evt[:40], detail, players[:30]), flush=True)
            elif status == "UNMATCHED":
                print("  %-40s  UNMATCHED  no schedule  [%s]" % (evt[:40], players[:30]), flush=True)
            else:
                print("  %-40s  SKIP  %.0f min to start=%s  [%s]" % (evt[:40], secs/60, detail, players[:30]), flush=True)

        eligible = [e for e, st, s, d, p in all_events_status if st == "ENTER"]
        waiting = [(e, s, d) for e, st, s, d, p in all_events_status if st == "WAIT (>24h)"]
        if eligible:
            print("\n[ALERT] %d events ELIGIBLE for immediate entry!" % len(eligible), flush=True)
        if not eligible and not waiting:
            print("\n[NEXT] No upcoming entries — all events processed or unmatched", flush=True)

        # Log FOMSUN schedule match verification (if present)
        for evt in self.event_tickers:
            if "FOMSUN" in evt:
                st = self.event_start_time.get(evt)
                is_processed = evt in self.processed_events
                if st:
                    print("\n[VERIFY] %s schedule matched: start=%s, processed=%s" % (
                        evt, datetime.fromtimestamp(st, tz=ET).strftime("%I:%M %p ET"), is_processed), flush=True)
                else:
                    print("\n[VERIFY] %s schedule: NO MATCH, processed=%s" % (evt, is_processed), flush=True)

        # Unmatched events with recent open_time (coverage gaps)
        recent_unmatched = []
        for evt in self.event_tickers:
            if evt in self.processed_events or evt in self.event_start_time:
                continue
            open_ts = self.event_open_time.get(evt, 0)
            if now - open_ts < 86400:
                recent_unmatched.append((evt, now - open_ts))
        if recent_unmatched:
            print("\n[WARN] Unmatched events with open_time < 24h:", flush=True)
            for evt, age in recent_unmatched:
                players = self.event_player_names.get(evt, ["?"])
                print("  %-40s  open_age=%.0fh  players=%s" % (evt[:40], age/3600, ", ".join(players)), flush=True)

        self._log("startup_validation", {
            "time_et": now_et.strftime("%Y-%m-%d %I:%M:%S %p ET"),
            "total_events": total_events,
            "schedule_matched": matched,
            "unmatched": unmatched,
            "processed": len(self.processed_events),
            "startup_skipped": startup_skipped,
            "waiting": len(waiting),
            "eligible": len(eligible),
        })

        if reconcile_only:
            print("\n[RECONCILE-ONLY] Exiting after validation.", flush=True)
            await self.session.close()
            self.log_file.close()
            return

        # WS producer/consumer split with per-ticker BBO coalescing: ws_reader
        # ingests frames synchronously (book/trade/lifecycle in-order, O(1),
        # never blocks) and flags BBO-changed tickers dirty; _ws_worker runs the
        # expensive on_bbo_update routing coalesced (>=1 route per ticker per
        # drain) so a snapshot flood can't starve the keepalive ping.
        # _loop_lag_monitor instruments scheduling lag for the cutover gate.
        self._bbo_event = asyncio.Event()
        asyncio.create_task(self.ws_reader())
        asyncio.create_task(self._ws_worker())
        asyncio.create_task(self._loop_lag_monitor())

        print("\n[INIT] Waiting 10s for BBO snapshots...", flush=True)
        await asyncio.sleep(10)

        # Paper mode startup: safety check + restore prior state (spec §2.3, §13)
        if _PAPER_API is not None:
            real_pos = await _real_api_get(self.session, self.ak, self.pk,
                "/trade-api/v2/portfolio/positions?count_filter=position&settlement_status=unsettled",
                self.rl)
            real_positions_count = len((real_pos or {}).get("market_positions", []))
            if real_positions_count > 0:
                self._log("paper_real_orders_blocked", {
                    "real_positions_count": real_positions_count,
                    "action": "abort",
                })
                raise RuntimeError(
                    "paper_mode=true but %d real Kalshi positions exist; close them first"
                    % real_positions_count)
            paper_state_path = "/root/Omi-Workspace/arb-executor/paper_state.json"
            paper_state_max_age = self.config.get("paper_state_max_age_sec", 86400)
            _PAPER_API.load_state(paper_state_path, paper_state_max_age)

        last_discovery = time.time()
        last_fill_check = 0  # force immediate first check_fills
        last_reconcile = time.time()
        last_stale_check = time.time()
        last_summary = time.time()
        last_settlement_poll = 0  # Bug 4 §6.3: force first REST settlements poll early (live only)
        last_routing_sweep = 0    # force first backstop routing sweep immediately at startup
        discovery_pending = False # FIX 3 stagger: discover one loop turn after the schedule reload

        print("[RUNNING] Main loop started.", flush=True)

        while True:
            try:
                # #0-infra: graceful shutdown -- a signal handler set the flag; break out and drain.
                if self._shutdown_requested:
                    break
                now = time.time()

                # Check settlements via BBO (tier-3 backstop)
                self.check_settlements()

                # Bug 4 §6.3: REST settlements safety-net poll (LIVE ONLY; 5-min cadence).
                # Gated on _PAPER_API is None -- paper mode must NOT poll real-account
                # settlement history (would falsely close paper positions).
                if _PAPER_API is None and now - last_settlement_poll > SETTLEMENT_POLL_INTERVAL:
                    await self.poll_settlements_rest()
                    last_settlement_poll = now

                # Backstop routing sweep (placement is primarily event-driven
                # via on_bbo_update per BBO message). Runs on a slow cadence,
                # OFF the 1s hot path, only to catch legs whose placement window
                # opens while their book is quiet (no BBO update to trigger
                # on_bbo_update). This is what keeps the full-universe iteration
                # from starving the WS keepalive.
                if now - last_routing_sweep > ROUTING_SWEEP_INTERVAL:
                    await self.routing_tick()
                    last_routing_sweep = now

                # Poll fills every 30s
                if now - last_fill_check > FILL_CHECK_INTERVAL:
                    await self.check_fills()
                    if _PAPER_API is not None:
                        _PAPER_API.maybe_heartbeat()
                    last_fill_check = now

                # Check sidecar heartbeats every 5 min
                if now - last_discovery > DISCOVERY_INTERVAL:
                    self._check_sidecar_heartbeats()

                # Refresh schedule + re-discover every 5 min. FIX 3 (stagger):
                # the schedule reload and the discovery re-match/subscribe run in
                # SEPARATE loop turns (~1s apart) so their work can't converge in
                # one turn. Both heavy parts are now offloaded (parse via FIX 2's
                # executor; per-event match via _match_event_to_schedule_async),
                # so neither blocks the loop even on the reload boundary.
                if now - last_discovery > DISCOVERY_INTERVAL:
                    await self._load_schedule_async()  # FIX 2: parse off the loop
                    last_discovery = now
                    discovery_pending = True
                elif discovery_pending:
                    discovery_pending = False
                    new_tickers = await self.discover_markets()
                    if new_tickers:
                        await self.ws_subscribe(new_tickers)

                # check_pending_entries disabled — new routing_tick re-evaluates every tick
                # await self.check_pending_entries()

                # Validate resting buys every 2 min
                if now - last_stale_check > STALE_CHECK_INTERVAL:
                    await self.validate_resting_buys()
                    last_stale_check = now

                # Reconcile every 60s — auto-post exits for naked positions
                if now - last_reconcile > 60:
                    await self.reconcile(quiet=True)
                    last_reconcile = now

                # Write own heartbeat
                try:
                    ws_age = int(now - max((b.updated for b in self.books.values()), default=0)) if self.books else 999
                    with open("/tmp/heartbeat_live_v3.json", "w") as _hf:
                        json.dump({"ts": int(now), "name": "live_v3", "status": "ok",
                                       "positions": len(self.positions), "resting_orders": len(self.pending_entries),
                                       "ws_connected": self.ws_connected, "bbo_age_sec": ws_age}, _hf)
                except Exception:
                    pass

                # Summary every 30 min
                if now - last_summary > 1800:
                    self.print_summary()
                    last_summary = now

                await asyncio.sleep(1)

            except KeyboardInterrupt:
                print("\n[STOP] Shutting down...", flush=True)
                self.print_summary()
                break
            except Exception as e:
                self._log("error", {"error": str(e), "traceback": traceback.format_exc()})
                await asyncio.sleep(5)

        # #0-infra: on a graceful shutdown request, cancel resting entry bids before exit (bounded
        # by the _force_exit watchdog). Legacy KeyboardInterrupt break leaves this False -> no drain.
        if self._shutdown_requested:
            await self._shutdown_drain()

        if self.session:
            await self.session.close()
        self.log_file.close()


def _raise_fd_limit(target=262144):
    """Raise the RLIMIT_NOFILE soft limit to `target` (capped at the hard limit) at startup --
    replaces the manual per-restart `ulimit -n` step (skipped on every restart this session, so
    the process ran on the 1024 default). Raising soft up to hard needs no privileges (hard is
    ~1,048,576). Defensive: NEVER crashes startup -- a setrlimit failure logs a warning and the
    process continues on the inherited limit. `resource` is lazy-imported (Unix-only; keeps this
    module importable on Windows for the test suite). Returns (soft, hard) on success, else None."""
    try:
        import resource
        old_soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        new_soft = min(target, hard)
        resource.setrlimit(resource.RLIMIT_NOFILE, (new_soft, hard))
        cur_soft, cur_hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        print("[BOOT] RLIMIT_NOFILE soft %d -> %d (hard %d)" % (old_soft, cur_soft, cur_hard), flush=True)
        return (cur_soft, cur_hard)
    except Exception as e:
        print("[BOOT] WARN: RLIMIT_NOFILE not raised (%r) -- continuing on inherited limit" % (e,), flush=True)
        return None


async def main():
    _raise_fd_limit()
    reconcile_only = "--reconcile-only" in sys.argv
    bot = LiveV3()
    await bot.run(reconcile_only=reconcile_only)

if __name__ == "__main__":
    asyncio.run(main())
