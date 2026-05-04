# Paper Mode Design Spec

**Status**: Draft, awaiting approval
**Author**: paired with operator, 2026-04-29
**Target file**: live_v3.py (currently 2365 lines, post Bugs 1-3)
**Locked design choices**: as specified by operator (Option C, permissive fills, telemetry-first, config-flag gated, no mixed mode)

---

## 1. Goals & Non-Goals

### Goals
1. **Validation env for Bug 4 / Bug 5** — paper mode is the development surface for the next two bug fixes.
2. **Integration test for Bugs 1-5** — run all five fixes simultaneously without exposing real capital.
3. **Liquidity telemetry capture** — every paper position emits enough metadata to retrospectively assess fill realism after burn-in.

### Non-Goals
- Perfect fill simulation. Permissive fills are accepted; volume telemetry is the realism check.
- Mixed real+paper operation. `paper_mode=true` means ALL orders are paper.
- Runtime mode toggle. Read once at startup; no flip-mid-run.
- Backfilling existing real Kalshi positions into paper state (operator must close real positions before switching modes).

---

## 2. Architecture

### 2.1 Dispatch (Option C — module-level branch to bot-owned class)

The three module-level HTTP wrappers (`api_get`, `api_post`, `api_delete` at lines 157, 176, 196) are renamed to `_real_*` and replaced by thin dispatchers that consult a module global `_PAPER_API`:

```python
_PAPER_API = None  # set at bot init if config["paper_mode"]

async def _real_api_get(s, ak, pk, path, rl):
    # original aiohttp implementation, unchanged
    ...

async def api_get(s, ak, pk, path, rl):
    if _PAPER_API is not None:
        return await _PAPER_API.handle_get(s, ak, pk, path, rl)
    return await _real_api_get(s, ak, pk, path, rl)
```

Same shape for `api_post` and `api_delete`.

**Why this works**:
- All 16 `api_get` call sites and the single `api_post` (`place_order`) and `api_delete` (`cancel_order`) call sites continue to use the original function names — zero call-site churn.
- `_PAPER_API` is None when `paper_mode=false`, so real path is identical, no overhead beyond a None check.
- `PaperApi` can selectively pass through to `_real_*` for endpoints it does not need to mock (e.g., `/markets`).

### 2.2 Bot init

In `LivBot.__init__` (or whatever the class is called — verify), after config load:

```python
if self.config.get("paper_mode", False):
    import sys
    _module = sys.modules[__name__]
    _module._PAPER_API = PaperApi(bot=self)
    self._log("paper_mode_enabled", {
        "config_path": self.config_path,
        "PAPER_MODE_VERSION": "1.0",
    })
```

PaperApi holds `self.bot` for access to `bot.books`, `bot.positions` (read-only — paper does NOT write to bot.positions; that goes through normal check_fills flow), `bot.config`, `bot._log`, `bot.get_category`, etc.

### 2.3 No mixed mode invariant

If `paper_mode=true`:
- Every `/portfolio/*` GET returns synthetic data (paper state only).
- Every order POST creates a synthetic order (no Kalshi traffic).
- Every order DELETE cancels a synthetic order (no Kalshi traffic).
- Real Kalshi positions held at startup are INVISIBLE to the bot. **Operator must close all real positions before enabling paper_mode.** Spec recommends adding a startup safety check (probe `/portfolio/positions` via `_real_api_get` once at boot, fail loud if non-empty).

---

## 3. Class Structure

```python
class PaperApi:
    """Top-level paper-mode dispatcher. Owns paper order state, paper position
    state, fill simulator, volume tracker. Methods invoked by module-level
    api_get/post/delete dispatchers and by trade/book ingestion hooks."""

    bot: Any                              # ref to LivBot for books/config/logging
    paper_orders: Dict[str, PaperOrder]   # order_id -> order
    paper_positions: Dict[str, PaperPosition]  # ticker -> position aggregate
    volume_tracker: VolumeTracker
    fill_simulator: PaperFillSimulator
    next_seq: int = 0                     # for synthetic order_id generation
    last_heartbeat_ts: float = 0.0
    fills_last_hour: deque                # (ts, event_name) tuples for rolling count

    # Dispatch
    async def handle_get(self, s, ak, pk, path, rl) -> dict
    async def handle_post(self, s, ak, pk, path, payload, rl) -> dict
    async def handle_delete(self, s, ak, pk, path, rl) -> bool

    # Ingestion hooks (called from WS handlers)
    def on_book_update(self, ticker: str) -> None
    def on_trade(self, ticker: str, ts: float, price: int, qty: int, side: str) -> None

    # Periodic
    def maybe_heartbeat(self) -> None  # called from main loop; gates on 60s cadence

    # Helpers
    def _new_order_id(self, ticker: str, ts: float) -> str
    def _emit(self, event: str, details: dict, ticker: str = "") -> None
    def _compute_mark_to_market_cents(self) -> int

    # Persistence (Revision 7)
    def dump_state(self, path: str) -> None
        # Atomic write of paper_orders + paper_positions to JSON. Called from
        # maybe_heartbeat. VolumeTracker NOT persisted (rebuilds organically).
    def load_state(self, path: str, max_age_sec: float) -> bool
        # True if loaded; False if file missing, stale, version-mismatched, or
        # parse-failed. Emits paper_state_restored or paper_state_skipped.


@dataclass
class PaperOrder:
    order_id: str
    ticker: str
    action: str           # "buy" or "sell"
    side: str             # "yes" or "no" (Kalshi convention; bot uses "yes" predominantly)
    yes_price: int        # cents, 1-99
    count: int            # original count requested
    remaining_count: int  # unfilled
    filled_count: int = 0
    status: str = "resting"  # "resting", "executed", or "canceled"
    post_ts: float = 0.0
    last_event_ts: float = 0.0
    client_order_id: str = ""

    # Captured at post for telemetry
    book_depth_at_price_post: int = 0
    best_bid_at_post: int = 0
    best_ask_at_post: int = 0
    last_trade_price_at_post: int = 0
    last_trade_age_at_post: float = 0.0
    fv_anchor_at_post: Optional[float] = None
    spread_at_post: int = 0

    def to_kalshi_dict(self) -> dict:
        """Shape matching /portfolio/orders/{id} and /portfolio/orders responses.
        Field names verified in §10: bot's parser tries `yes_price_dollars`,
        `remaining_count_fp`, `fill_count_fp`, `average_fill_price_fp` first
        (preferred) and falls back to `yes_price`, `remaining_count`,
        `count_filled`. Internal PaperOrder storage stays integer cents (cleaner
        accounting); float-dollar conversion happens here at the boundary."""
        return {
            "order_id": self.order_id,
            "ticker": self.ticker,
            "action": self.action,
            "side": self.side,
            # Preferred fields (bot reads these first):
            "yes_price_dollars": self.yes_price / 100.0,
            "remaining_count_fp": float(self.remaining_count),
            "fill_count_fp": float(self.filled_count),
            "average_fill_price_fp": (self.yes_price / 100.0) if self.filled_count > 0 else 0.0,
            # Fallback fields (bot's secondary lookup):
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
    event_ticker: str
    qty: int = 0                    # cumulative buy fills
    sold_qty: int = 0               # cumulative sell fills
    total_cost_cents: int = 0       # sum(buy_price_i * qty_i)
    total_revenue_cents: int = 0    # sum(sell_price_i * qty_i)
    realized_pnl_cents: int = 0     # finalized when position fully closed or settled
    open_buy_orders: List[str] = field(default_factory=list)
    open_sell_orders: List[str] = field(default_factory=list)
    first_entry_ts: float = 0.0
    last_event_ts: float = 0.0
    settled: bool = False
    settlement_price: Optional[int] = None

    @property
    def net_qty(self) -> int:
        return self.qty - self.sold_qty

    @property
    def avg_price(self) -> int:
        """Volume-weighted entry price in cents. Used by handle_get for
        /portfolio/positions response."""
        if self.qty == 0:
            return 0
        return self.total_cost_cents // self.qty

    def to_kalshi_dict(self) -> dict:
        """Shape matching /portfolio/positions response. Field names verified in §10:
        bot reads `position_fp` (numeric qty) and `market_exposure_dollars` (in
        dollars; multiplied by 100 to get cents). avg_price is computed by the bot
        as int(market_exposure_dollars * 100 / position_fp). PaperApi mirrors that
        exact shape here; bot's existing parser (live_v3.py:1862-1877) consumes the
        result unchanged."""
        net = self.net_qty
        # market_exposure_dollars represents OPEN cost basis (qty * avg in dollars).
        # Bot uses this with position_fp to recover avg_price.
        exposure_dollars = (self.avg_price * net) / 100.0 if net > 0 else 0.0
        traded_dollars = (self.avg_price * self.qty) / 100.0  # fallback, cumulative
        return {
            "ticker": self.ticker,
            "event_ticker": self.event_ticker,
            "position_fp": float(net),
            "market_exposure_dollars": exposure_dollars,
            "total_traded_dollars": traded_dollars,
            "settlement_status": "settled" if self.settled else "unsettled",
        }


class PaperFillSimulator:
    api: PaperApi  # back-ref

    def evaluate_book_cross(self, ticker: str) -> None:
        """Called from on_book_update. Walk resting paper orders for ticker;
        fill any whose price is met by current BBO."""

    def evaluate_trade_print(self, ticker: str, ts: float, price: int) -> None:
        """Called from on_trade. Fill any resting paper order whose level was
        traded through."""

    def try_fill(self, order: PaperOrder, fill_price: int, fill_ts: float,
                  trigger: str) -> None:
        """Execute the fill: update order, update position, emit telemetry.
        trigger: 'book_cross' or 'trade_print'."""


class VolumeTracker:
    """Per-ticker rolling tracker of trade prints. Used to answer 'how much
    volume traded at-or-through price X since timestamp T' for telemetry."""

    trades: Dict[str, deque]  # ticker -> deque[(ts, price, qty)]
    retention_sec: float = 21600.0  # 6h; trades older than this evicted

    def record(self, ticker: str, ts: float, price: int, qty: int, taker_side: str) -> None
        # Caller passes raw Kalshi WS taker_side ("yes" | "no"). Normalized at
        # record-time to internal aggressor side ("buy" | "sell"):
        #   taker_side == "yes" -> stored side = "buy"   (taker lifted ask, paid up for yes)
        #   taker_side == "no"  -> stored side = "sell"  (taker bought no = effectively sold yes by hitting bid)
        # Stored tuple: (ts, price, qty, normalized_side).
    def volume_at_or_through(self, ticker: str, side: str,
                              target_price: int, since_ts: float) -> int
    def depth_for_side(self, ticker: str, side: str, price: int) -> int
        # Read from self.api.bot.books[ticker]. side='ask' returns asks at
        # price; side='bid' returns bids at price.
    def evict_old(self, ticker: str, now: float) -> None
```

---

## 4. VolumeTracker Internals

### Data structure

`trades[ticker]` is a `collections.deque` of `(ts, price, qty)`. Append-only at the head. Eviction from the tail when ts is older than `retention_sec`.

For `volume_at_or_through`, we scan the deque and sum qty matching the predicate. With 6h retention and typical Kalshi tennis trade rates (low single-digit per second per ticker), the deque stays under ~50k entries per ticker, so linear scan is fine. If profiling shows otherwise, switch to a sorted price-bucketed structure.

### Side semantics

A trade print's direction (aggressor side) determines whether it represents volume that would have crossed our resting order. A buy-aggressor print at price P (someone lifted an ask at P) is informative for evaluating sell-side fill probability; it tells us nothing about whether anyone would have hit our resting bid.

- **Paper buy resting at price P** (we are posting a bid at P):
  - **SELL-aggressor** prints at price <= P represent liquidity that would have hit our bid.
  - `volume_at_or_through(ticker, "buy", P, since_ts)` = `sum(qty for (ts, price, qty, side) in trades[ticker] if ts >= since_ts and price <= P and side == "sell")`
  - BUY-aggressor prints at price <= P do NOT count: they represent someone lifting an even lower ask, which tells us about ask-side activity but not about our bid being hit.

- **Paper sell resting at price P** (we are posting an ask at P):
  - **BUY-aggressor** prints at price >= P represent liquidity that would have lifted our ask.
  - `volume_at_or_through(ticker, "sell", P, since_ts)` = `sum(qty for (ts, price, qty, side) in trades[ticker] if ts >= since_ts and price >= P and side == "buy")`

### Side annotation requirement

`VolumeTracker.record()` accepts raw Kalshi WS `taker_side` ("yes" | "no") and normalizes to the internal AGGRESSOR side ("buy" | "sell") at record-time:

- `taker_side == "yes"` → stored side = `"buy"` (taker lifted an ask, paid up for yes — buy-aggressor)
- `taker_side == "no"` → stored side = `"sell"` (taker bought no, equivalent to selling yes by hitting the bid — sell-aggressor)

The §10 probe confirmed Kalshi's WS trade messages use the field name `taker_side` (not `yes_taker_side`) and that 100.00% of 2,752,237 historical trade prints across 1,626 tickers carry a valid `"yes"` or `"no"` value.

### Fallback when side is unavailable

**§10 probe result: 100.00% of 2,752,237 historical trade prints carry a valid `taker_side`. SIDED MODE is confirmed; the unsided fallback is defensive only and will not engage in v1.**

The fallback path is retained for resilience against future Kalshi WS schema changes. If `VolumeTracker.record()` receives `taker_side=""` (or any unrecognized value) for ≥5% of records observed during a startup sample window, it switches to unsided mode:

- `volume_at_or_through_unsided(ticker, "buy", P, since_ts)` = `sum(qty for ... if ts >= since_ts and price <= P)`
- `volume_at_or_through_unsided(ticker, "sell", P, since_ts)` = `sum(qty for ... if ts >= since_ts and price >= P)`

Unsided mode OVERCOUNTS (includes buy-aggressors at lower prices for buy-side; sell-aggressors at higher prices for sell-side). Telemetry events report `volume_at_or_through_unsided` instead of `volume_at_or_through` so post-hoc analysis can distinguish. A `paper_volume_unsided_warning` event fires once at startup if degraded mode is detected.

### depth_for_side

Reads instantaneous book depth from `self.api.bot.books[ticker]`:
- For a buy at P: depth_for_side returns `bot.books[ticker].asks.get(P, 0)` plus aggregated asks <= P (the volume immediately available to fill us).
- For a sell at P: returns `bot.books[ticker].bids.get(P, 0)` plus aggregated bids >= P.

Note: Book class fields (line 219) include `bids: Dict[int, int]` and `asks: Dict[int, int]` — int price -> int qty.

---

## 5. Endpoint Dispatch (PaperApi.handle_get / handle_post / handle_delete)

The bot's 16 `api_get` sites hit these patterns (lines from prior probe). PaperApi handles each pattern; everything else passes through to `_real_api_get`.

### 5.1 handle_get(path)

| Pattern | Sites | Behavior |
|---|---|---|
| `/trade-api/v2/portfolio/orders/{order_id}` | 1048, 1211, 1251, 1750 | Look up order_id in `paper_orders`. Return `{"order": order.to_kalshi_dict()}`. If order_id does not start with "PAPER-" or not found, return `{"order": None, "_error": "not_found"}`. |
| `/trade-api/v2/portfolio/orders?ticker=X&status=resting` | 1114, 1242, 1510, 1946, 1973, 2000 | Filter `paper_orders` by ticker AND status=="resting". Return `{"orders": [order.to_kalshi_dict() for ...]}`. |
| `/trade-api/v2/portfolio/orders?status=resting` | 1881 | All resting paper orders. Return `{"orders": [...]}`. |
| `/trade-api/v2/portfolio/positions?ticker=X&...` | 1516 | Filter `paper_positions` by ticker, net_qty > 0, not settled. Return `{"market_positions": [pos.to_kalshi_dict()]}`. |
| `/trade-api/v2/portfolio/positions?count_filter=position&settlement_status=unsettled` | 1864 (reconcile) | All open paper positions. Return `{"market_positions": [...]}`. |
| `/trade-api/v2/markets?...` | 791 | **Pass through** to `_real_api_get`. Public market discovery. |
| anything else | — | Pass through. |

Path parsing: simple `urllib.parse.urlsplit` + query parsing. Pattern matching by `startswith` for the `/orders/{id}` form vs `=` query for filtered list.

### 5.2 handle_post(path, payload)

Only one POST endpoint in the bot: `/trade-api/v2/portfolio/orders`.

```
1. Generate order_id = f"PAPER-{ticker}-{int(post_ts)}-{seq:06d}", increment seq
2. Capture telemetry from current bot.books[ticker]:
     - book_depth_at_price_post (asks at yes_price for buy; bids at yes_price for sell)
     - best_bid_at_post, best_ask_at_post
     - last_trade_price_at_post, last_trade_age_at_post
     - spread_at_post = best_ask - best_bid
     - fv_anchor_at_post: §10 confirmed there is no `bot.get_fv(ticker)`. The
       callable is `self.bot._get_side_fv(ticker, event_ticker)` at live_v3.py:987,
       which returns a dict (or None) with keys `fv_cents`, `num_books`, `age_sec`.
       Access pattern:
           event_ticker = self.bot.ticker_to_event.get(ticker, "")
           side_fv = self.bot._get_side_fv(ticker, event_ticker) if event_ticker else None
           fv_anchor_at_post = side_fv["fv_cents"] if side_fv and side_fv.get("fv_cents") is not None else None
3. Construct PaperOrder, store in self.paper_orders
4. Get-or-create PaperPosition for ticker, append order_id to open_buy_orders or open_sell_orders
5. Emit paper_order_posted telemetry event
6. Return Kalshi-shaped response: {"order": {"order_id": oid, "status": "resting", "ticker": ..., ...}}
```

The response shape must match what `place_order` parses at line 635: `resp.get("order", {}).get("order_id", "")`.

### 5.3 handle_delete(path)

Pattern: `/trade-api/v2/portfolio/orders/{order_id}`.

```
1. Extract order_id from path
2. If order_id not in paper_orders OR status != "resting": return False
3. order.status = "canceled"
4. Remove order_id from position.open_*_orders
5. Emit paper_order_cancelled
6. Return True
```

---

## 6. Trade & Book Ingestion Hooks

### 6.1 Trade hook (single-line modification near live_v3.py:575)

Current code at line 575 (from probe):
```python
book.last_trade_price = price
```

Modified to:
```python
book.last_trade_price = price
book.last_trade_ts = ts_now
if _PAPER_API is not None:
    _PAPER_API.on_trade(ticker, ts_now, price, qty_from_msg, side_from_msg)
```

(The `book.last_trade_ts` write is already present nearby per Book class fields — verify and skip if duplicate.)

`qty_from_msg` and `side_from_msg` come from the WS trade message. Need to confirm Kalshi WS trade message schema at the same site during implementation. If qty is not available, default to 1 and document as a known limitation in telemetry.

### 6.2 Book hook (exactly 2 sites — confirmed in §10 probe)

The book is mutated through exactly two methods on the bot class. Both have `self` and `ticker` in scope, so the hook is identical at both sites:

```python
        if _PAPER_API is not None:
            _PAPER_API.on_book_update(ticker)
```

**Site 1**: `apply_snapshot(self, ticker, msg)` — live_v3.py:698-714. Builds new Book, populates `bids` and `asks`, calls `recalc_bbo`, sets `book.updated`, assigns `self.books[ticker]`, calls `self._log_tick(ticker, book)`. **Hook insertion: line 714, after the `_log_tick` call.**

**Site 2**: `apply_delta(self, ticker, msg)` — live_v3.py:716-737. Mutates `book.bids` or `book.asks` (incremental), pops levels with qty ≤ 0, calls `recalc_bbo`, sets `book.updated`, calls `self._log_tick(ticker, book)`. **Hook insertion: line 737, after the `_log_tick` call.**

Hooking at these two sites covers all book-mutation paths. `recalc_bbo` itself is NOT hooked because it does not have `ticker` in scope; callers do.

---

## 7. Fill Simulation (Permissive Policy)

### Fill conditions

| Order | Trigger A: book cross | Trigger B: trade print |
|---|---|---|
| Resting buy at P | `book.best_ask <= P` | trade at price <= P |
| Resting sell at P | `book.best_bid >= P` | trade at price >= P |

### Fill price (permissive)

Always fill at `order.yes_price`. No slippage. No partial fills. Full quantity in one shot.

Rationale: under permissive policy, the bot's accounting is exact (no partial-fill code paths to test in paper mode), and realism is assessed via volume telemetry post-hoc.

### Directional bias of permissive fills

Permissive policy is NOT symmetric across buy and sell sides. It biases paper P&L systematically:

- **On BUYS** (paper bot is patient maker, posting a bid): permissive fill is **FAVORABLE** to paper bot. In real markets, if the book gaps through our level (best_ask drops to 30 when we are bid 42), we might not get filled at 42 — a faster taker could sweep the asks before we reprice. Paper assumes we always fill at 42, our posted level. **This OVERSTATES paper fill rate.**

- **On SELLS** (paper bot is patient maker, posting an ask): permissive fill is **UNFAVORABLE** to paper bot. In real markets, if the book gaps through our level (best_bid jumps to 80 when we are offered 60), we might receive 80 (price improvement). Paper fills at 60. **This UNDERSTATES paper P&L.**

Net effect on P&L is sport- and conditions-dependent. Buy-side overcounting and sell-side undercounting partially offset, but not symmetrically.

**USE PAPER P&L ONLY AS A DECISION-QUALITY SIGNAL FOR BUG FIX VALIDATION, NOT AS A REALISM ESTIMATE OF LIVE BOT PERFORMANCE.** Burn-in P&L compared to historical real P&L should be interpreted with this directional asymmetry in mind. Liquidity telemetry (`volume_at_or_through`, `depth_at_price`) is the realism check, not realized P&L.

### evaluate_book_cross(ticker)

Called from `on_book_update`. For each `order in self.paper_orders.values()` matching ticker AND status == "resting":
- buy + best_ask <= price -> `try_fill(order, order.yes_price, now, "book_cross")`
- sell + best_bid >= price -> same

### evaluate_trade_print(ticker, ts, price)

Called from `on_trade` after volume_tracker.record. For each resting order on ticker:
- buy + price <= order.yes_price -> fill
- sell + price >= order.yes_price -> fill

### try_fill(order, fill_price, fill_ts, trigger)

```
1. order.status = "executed"
   order.filled_count = order.count
   order.remaining_count = 0
   order.last_event_ts = fill_ts

   # Idempotency: status is set before any further work. Both evaluate_book_cross
   # and evaluate_trade_print check status == "resting" before calling try_fill,
   # so a re-entrant call from a chained book/trade hook arriving mid-fill sees
   # status="executed" and short-circuits. No duplicate fills possible.

2. pos = self.paper_positions[order.ticker]
   if order.action == "buy":
       pos.qty += order.count
       pos.total_cost_cents += order.count * fill_price
       pos.first_entry_ts = pos.first_entry_ts or fill_ts
       pos.open_buy_orders.remove(order.order_id)
   else:  # sell
       pos.sold_qty += order.count
       pos.total_revenue_cents += order.count * fill_price
       pos.open_sell_orders.remove(order.order_id)
       if pos.net_qty == 0:
           pos.realized_pnl_cents = pos.total_revenue_cents - pos.total_cost_cents

3. Compute telemetry:
       time_to_fill_sec = fill_ts - order.post_ts
       volume_at_or_through_lifetime = volume_tracker.volume_at_or_through(
           ticker, order.action, order.yes_price, order.post_ts)
       depth_at_fill = volume_tracker.depth_for_side(
           ticker, "ask" if order.action == "buy" else "bid", order.yes_price)
       book_now = bot.books[order.ticker]

4. Emit event:
       event = "paper_fill" if order.action == "buy" else "paper_exit_fill"
       _emit(event, {
           "order_id": order.order_id,
           "fill_price": fill_price,
           "qty": order.count,
           "time_to_fill_sec": time_to_fill_sec,
           "volume_at_or_through_lifetime": volume_at_or_through_lifetime,
           "depth_at_fill": depth_at_fill,
           "fill_trigger": trigger,
           "best_bid_at_fill": book_now.best_bid,
           "best_ask_at_fill": book_now.best_ask,
           "last_trade_price_at_fill": book_now.last_trade_price,
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

5. Note: paper_fill / paper_exit_fill events are PAPER-NATIVE telemetry. They do NOT
   replace the bot's existing entry_filled / exit_filled events. The bot's check_fills
   will independently observe the order status change via api_get and emit its own
   entry_filled / exit_filled events. Both event streams flow into the JSONL log.
   Operator analysis can join paper_fill <- order_id -> entry_filled.
```

---

## 8. Telemetry Event Schemas

### 8.1 paper_mode_enabled

Emitted once at startup.
```json
{
  "event": "paper_mode_enabled",
  "details": {"config_path": "...", "PAPER_MODE_VERSION": "1.0"}
}
```

### 8.2 paper_order_posted

Emitted on every successful handle_post.
```json
{
  "event": "paper_order_posted",
  "ticker": "KX...",
  "details": {
    "order_id": "PAPER-KX...-1714397462-000001",
    "client_order_id": "...",
    "action": "buy",
    "side": "yes",
    "yes_price": 42,
    "count": 10,
    "best_bid": 41,
    "best_ask": 43,
    "spread": 2,
    "depth_at_price": 25,
    "depth_opposite_side": 18,
    "last_trade_price": 42,
    "last_trade_age_sec": 12,
    "fv_anchor": 0.448,
    "fv_minus_price_cents": 2.8,
    "post_ts": 1714397462.5
  }
}
```

### 8.3 paper_fill

Buy fill. Schema in Section 7 step 4.

### 8.4 paper_exit_fill

Sell fill. Same schema as paper_fill, plus `realized_pnl_cents` populated when position fully closes.

### 8.5 paper_order_cancelled

```json
{
  "event": "paper_order_cancelled",
  "ticker": "...",
  "details": {
    "order_id": "PAPER-...",
    "post_ts": ...,
    "lifetime_sec": ...,
    "fills_during_lifetime": 0,
    "volume_at_or_through_lifetime": 12345,
    "best_bid_at_cancel": 40,
    "best_ask_at_cancel": 43
  }
}
```

### 8.6 paper_settlement

**Deferred to Bug 4 implementation.** Paper positions remain OPEN in memory until Bug 4's settlement scan lands. The schema below is reserved; **no `paper_settlement` events emit in v1.** Known v1 limitations:

- Paper positions accumulate across match boundaries even though real Kalshi markets have settled. `paper_pnl_mtm` uses live `best_bid` which goes to 0/100 for settled markets, so MTM behaves correctly numerically — but the position count grows unbounded over multi-day burn-in.
- Mitigation: heartbeat alarm if `active_paper_positions > 50` (suggests settlement detection is needed earlier than Bug 4 timeline).

Once Bug 4 lands, the schema below is emitted on settlement detection.

```json
{
  "event": "paper_settlement",
  "ticker": "...",
  "details": {
    "qty": 10,
    "avg_entry_price": 42,
    "exit_avg_price_or_settlement": 99,
    "settlement_price": 99,
    "realized_pnl_cents": 570,
    "lifetime_sec": 3600.0,
    "max_volume_at_or_through_during_lifetime": 5000,
    "open_orders_at_settlement": ["PAPER-..."]
  }
}
```

### 8.7 paper_heartbeat

Emitted >=60s apart.
```json
{
  "event": "paper_heartbeat",
  "details": {
    "active_paper_positions": 5,
    "active_paper_orders_resting": 3,
    "paper_pnl_mtm_cents": 1250,
    "paper_pnl_realized_cents": 8400,
    "fills_in_last_hour": 12,
    "telemetry_event_counts_last_hour": {
      "paper_order_posted": 18,
      "paper_fill": 12,
      "paper_exit_fill": 7,
      "paper_order_cancelled": 4,
      "paper_settlement": 2
    }
  }
}
```

### 8.8 paper_real_orders_blocked (safety log)

If startup safety check finds real positions on Kalshi while paper_mode=true, log this and (optionally) abort.
```json
{
  "event": "paper_real_orders_blocked",
  "details": {"real_positions_count": 3, "real_orders_count": 1, "action": "abort"}
}
```

### 8.9 paper_state_restored / paper_state_skipped (Revision 7)

Emitted at startup after persistence load attempt.

`paper_state_restored`:
```json
{
  "event": "paper_state_restored",
  "details": {
    "orders_loaded": 5,
    "positions_loaded": 12,
    "state_age_sec": 18432.5,
    "schema_version": "1.0"
  }
}
```

`paper_state_skipped`:
```json
{
  "event": "paper_state_skipped",
  "details": {
    "reason": "file_not_found"
    // other reasons: "file_stale", "version_mismatch", "parse_error"
  }
}
```

If `volume_at_or_through_unsided` mode was confirmed at §10 probe, emit once at startup:
```json
{
  "event": "paper_volume_unsided_warning",
  "details": {
    "reason": "ws_trade_messages_missing_side_field",
    "trade_messages_sampled": 100,
    "messages_with_side": 47
  }
}
```

---

## 9. Heartbeat Cadence

Hook into the main loop. The check_fills cadence (line 2282 `last_fill_check`) is a good model. After each check_fills call, also call:

```python
if _PAPER_API is not None:
    _PAPER_API.maybe_heartbeat()
```

`maybe_heartbeat` gates on `now - self.last_heartbeat_ts >= 60`.

`fills_in_last_hour`: rolling deque of (fill_ts, ...) tuples. Evict ts < now - 3600 on each emit.

`telemetry_event_counts_last_hour`: similarly bounded counter.

`paper_pnl_mtm_cents`:
```
sum over open positions:
    net_qty = pos.qty - pos.sold_qty
    if net_qty > 0:
        unrealized = net_qty * bot.books[pos.ticker].best_bid - (pos.total_cost_cents - sold_proportional_cost)
```
Simplified MTM: `value_if_sold_now = net_qty * best_bid; cost_basis_remaining = (total_cost_cents / qty) * net_qty; mtm = value_if_sold_now - cost_basis_remaining`.

---

## 10. Pre-Implementation Verification (must run before patch)

The spec assumes Kalshi response shapes match what bot's parsers expect. Implementation phase MUST verify by reading these parser sites:

| Site | Endpoint | Need to confirm |
|---|---|---|
| 1864 reconcile | `/portfolio/positions` | Field names: `ticker`, `event_ticker`, `position`, `average_price` (or `avg_price`?). Currently spec uses `average_price`. |
| 1881 reconcile | `/portfolio/orders?status=resting` | Field names: `order_id`, `ticker`, `action`, `yes_price`, `remaining_count` (or `count`?). |
| 1048 entry fill check | `/portfolio/orders/{id}` | Single-order shape. `status` values exact strings. |
| 1114 resting-by-ticker | `/portfolio/orders?ticker=X&status=resting` | List shape, same field names. |
| `place_order` resp parse (635) | POST `/portfolio/orders` resp | `resp["order"]["order_id"]`, `resp["order"]["status"]`. |
| **line 575 area** | **WS trade message** | **HARD PREREQ.** Confirm `side`/`taker_side`/`yes_taker_side` field name and reliability. Sample 100 trade messages; count those with side present. If <95%, fall back to unsided VolumeTracker per Revision 1 and emit `paper_volume_unsided_warning`. |
| **book mutation grep** | **`book.bids` / `book.asks` writes** | **HARD PREREQ.** Enumerate every line that writes to a Book instance's bids or asks dict. Each gets an `on_book_update(ticker)` hook in §6.2. List must be exhaustive — any missed site means stale fill simulation. Use `grep -nE 'book\.(bids\|asks)\[' live_v3.py` and read each result with surrounding context. |

For each, read ~20 lines around the parse site and document the actual key names used. Implementation will adjust `to_kalshi_dict` field names if needed.

Also verify (these are now HARD prereqs, no longer deferred):
- WS trade message qty field — does it carry per-print qty? If not, default to 1 and emit `paper_volume_qty_missing_warning` once.
- `bot.get_fv(ticker)` — does this method exist? If not, fv_anchor telemetry is `None`. (FV computation seems to be in lines 1300-1350 area per prior probe; verify whether there is a callable.)

---

## 11. Test Plan

### 11.1 Pre-deployment (synthetic, no bot execution)

Standalone Python test script (lives at `tests/test_paper_mode.py`, NOT in live_v3.py). Imports the relevant classes from live_v3 module, builds mock Bot with stub books, drives PaperApi end-to-end.

**T1 - sanity**: paper_mode=true; PaperApi instance created; api_get to `/markets` passes through (verify _real_api_get called); api_get to `/portfolio/positions` returns synthetic empty.

**T2 - order placement**: handle_post with valid payload; PaperOrder created; paper_order_posted emitted; response shape matches `{"order": {"order_id": ..., "status": "resting"}}`.

**T3 - book-cross fill**: place buy at 42c; mock book with best_ask=43; update book to best_ask=42; on_book_update triggers fill; paper_fill emitted; PaperPosition.qty=count, avg_price=42.

**T4 - trade-through fill**: place buy at 42; mock trade print at 41; on_trade triggers fill at 42 (permissive — fill at our price); volume_at_or_through telemetry includes the print.

**T5 - sell fill closes position**: place buy at 42, fill; place sell at 60, fill at trade-through 60; PaperPosition.realized_pnl_cents == count * 18; paper_exit_fill emitted with realized_pnl populated.

**T6 - cancel**: place buy; cancel via handle_delete; order.status == "canceled"; paper_order_cancelled emitted; subsequent on_book_update does NOT fill it.

**T7 - reconcile shape**: handle_get to `/portfolio/positions` after some fills; response parses with bot's actual pos_data extraction code (extracted into a callable for the test).

**T8 - VolumeTracker eviction**: record 100 trades with monotonic ts, advance now > retention_sec; evict_old leaves only recent; volume_at_or_through respects window.

**T9 - heartbeat cadence**: call maybe_heartbeat 100x in 30s; only one paper_heartbeat emitted. Wait 61s; second emission.

### 11.2 Bot-against-self (live tennis match, paper_mode=true)

After unit tests pass, run the actual bot in paper mode for 1-2 hours during live matches. Pass criteria:

- >=1 paper_order_posted
- >=1 paper_fill OR explicit reason logged for no fill (e.g., orders cancelled before book crossed)
- >=1 full lifecycle: paper_order_posted -> paper_fill -> paper_order_posted (sell) -> paper_exit_fill OR paper_settlement
- 0 real api_post or api_delete to Kalshi (instrument _real_api_post/_real_api_delete to log "real_api_call" if invoked while paper_mode=true; expect 0 such logs)
- Heartbeats firing every ~60s
- No unhandled exceptions in PaperApi
- Bot's existing reconcile (line 1864) returns synthetic positions and does not crash
- Bug 3 guard (`reconcile_price_mismatch`) does NOT fire (paper state should track perfectly under permissive fills)

---

## 12. Burn-In Observation Plan (3-7 days)

### 12.1 Health metrics (pass)
- Heartbeat continuity: <=2% gaps >120s
- No bot crashes
- No real_api_call events
- check_fills cadence stays normal (no degradation from PaperApi overhead)

### 12.2 Realism check (compare to historical real-bot data)
- Distribution of `time_to_fill_sec` for paper_fill — compare median, p90 to historical entry_filled latency from real logs (the 130 historical events).
- Distribution of `volume_at_or_through_lifetime` — sanity check: if telemetry says 500 contracts traded through our level during lifetime, but bot's typical fill is 10 contracts, fill realism is plausible. If telemetry says 0 volume crossed but paper says we filled, something is wrong with VolumeTracker or fill simulator.
- Cancellation rates: paper_order_cancelled count vs paper_fill count — should be in similar ballpark to historical entry_cancelled/entry_filled ratio (254:130 ~= 2:1 historically).

### 12.3 P&L sanity
- Paper realized P&L distribution shape vs historical real bot. Per-position median, p10, p90 cents/contract.
- Paper MTM does not diverge unboundedly from realized — large MTM-realized gap suggests stuck positions (book never crossed sell level, never settled in paper view).

### 12.4 Bug 4 / Bug 5 development gates
- Bugs 4-5 development happens INSIDE paper mode. Each bug gets its own scenario:
  - Bug 4 manual trigger via crafted state -> expected paper events fire -> fix lands in live_v3.py
  - Bug 5 same workflow.
- After both fixes land, full integration burn-in for 3-7 days before live deploy.

### 12.5 Stop conditions (abort burn-in if observed)
- Any uncaught exception in PaperApi
- Heartbeat ceases >5min
- paper_real_orders_blocked event fires (real Kalshi positions appeared somehow)
- Real api_post or api_delete called while _PAPER_API is set
- Paper bot accumulates >100 paper positions in a few hours (suggests fills are not propagating, runaway buy loop)

---

## 13. Out-of-Scope (explicitly deferred)

- Partial fills under stress (full-fill assumption acceptable for permissive policy)
- Latency simulation (zero-latency assumption)
- Fee modeling (paper P&L is gross; fees can be applied post-hoc from telemetry)
- Order-book queue position simulation
- Adverse-selection adjustment (telemetry captures volume_at_or_through, post-hoc analysis can apply realistic fill probability)
- **Persistence** (v1 INCLUDES, scope-limited):
  - **Path**: `/root/Omi-Workspace/arb-executor/paper_state.json` (NOT `/tmp/` — `/tmp` is cleared on reboot, defeating the resilience purpose).
  - **Atomic write**: write to `paper_state.json.tmp` then `os.rename` to `paper_state.json` to prevent corruption on crash mid-write.
  - **Cadence**: dump on every heartbeat (60s) from `maybe_heartbeat`.
  - **Contents**: `paper_orders` + `paper_positions` only. `next_seq` and schema version included.
  - **Stale threshold**: configurable via `paper_state_max_age_sec` in `config.json`, default `86400` (24h). Allows tuning during development without code change.
  - **Startup behavior**: if `paper_mode=true` and `paper_state.json` exists with mtime within `paper_state_max_age_sec`, call `load_state(path, max_age_sec)`. On success, emit `paper_state_restored` with counts. On miss/stale/version-mismatch/parse-error, emit `paper_state_skipped` with reason and start fresh.
  - **VolumeTracker is NOT persisted.** Cold-start after restart loses up to 6h of rolling trade history; rebuilds organically from incoming WS prints. The first ~5min of post-restart fills will report low `volume_at_or_through`; flag this in burn-in analysis.
  - **Schema versioning**: dump includes `"PAPER_STATE_VERSION": "1.0"`. Mismatch on load -> `paper_state_skipped` with reason `"version_mismatch"`, start fresh. Allows future schema evolution without breaking burn-in.

---

## 14. Implementation Plan (after spec approval)

1. Probe pre-implementation verification items in Section 10 (all read-only, ~10 minutes).
2. Build `/tmp/live_v3_paper.py` from current `live_v3.py` plus:
   - VolumeTracker, PaperOrder, PaperPosition, PaperFillSimulator, PaperApi class definitions (added near the top, after Position class)
   - Renamed `_real_api_get/post/delete` and new `api_get/post/delete` dispatchers
   - Paper hooks at the trade/book ingestion sites
   - `_PAPER_API` module global and bot init wiring
   - Heartbeat call in the main loop
3. Diff /tmp/live_v3_paper.py against live_v3.py, show full diff to operator.
4. On approval: backup live_v3.py.bak.paper-pre, copy patched file, verify markers/syntax/sha.
5. Run Section 11.1 unit tests against the patched module.
6. On unit-test pass: run Section 11.2 bot-against-self for 1-2 hours.
7. On bot-against-self pass: green light Bug 4 / Bug 5 development inside paper mode.

---

## 15. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| WS trade message lacks qty/side fields | Medium | Volume telemetry less precise | Document defaults; flag in burn-in |
| Real Kalshi positions exist at paper-mode startup | Medium | Real positions go unmanaged | Section 2.3 startup safety check; fail loud |
| `pos_data` parsing key names do not match spec | Medium | Reconcile crash on first iteration | Section 10 pre-implementation probe |
| Permissive fills hide real liquidity issues | Low (by design) | Paper looks better than real | Volume telemetry is the realism check |
| `_PAPER_API` global pollution between tests | Low | Test cross-contamination | Tests must `_PAPER_API = None` in teardown |
| Memory growth of VolumeTracker | Low | OOM after long burn-in | 6h retention; profile during burn-in |
| Heartbeat coupled to check_fills cadence | Low | If check_fills hangs, no heartbeat | Acceptable for v1; flag if observed |
| WS trade messages missing side field (Revision 1) | Medium-Low | Volume telemetry overcounts | §10 probe; degrade to `volume_at_or_through_unsided` and emit `paper_volume_unsided_warning` |
| Persistence file corruption mid-write (Revision 7) | Low | Paper state lost on next restart | Atomic write (tmpfile + rename); `paper_state_skipped` with `"parse_error"` on load failure |

---

## 16. Approval Checklist

Operator confirms before Section 14 step 2 begins:

- [ ] Class structure (Section 3) matches mental model
- [ ] Endpoint dispatch table (Section 5) covers all 16 api_get sites
- [ ] Telemetry schema (Section 8) sufficient for burn-in analysis
- [ ] Test plan (Section 11) hits required scenarios
- [ ] Pre-implementation probes (Section 10) acceptable to run first
- [ ] Risk register (Section 15) — no missing risks

End of spec.
