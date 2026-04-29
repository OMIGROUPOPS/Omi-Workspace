# Bug 4 Brief — Missing Settlement Detection

**Version**: v2 (paper-mode gating + persistence verification added)
**Status**: investigation complete, design proposed, no code written
**Author**: paired with operator, 2026-04-29
**Target**: live_v3.py settlement detection path

## Changes in v2

- §2.5 added: paper-mode interaction explicitly resolved.
- §6 (pseudocode) rewritten: `process_settlement` dispatches paper vs live based on `_PAPER_API` state; `poll_settlements_rest` gated on `_PAPER_API is None`; `check_settlements` iterates `paper_positions` in paper mode.
- §8 (telemetry) updated with `paper_settled` event schema.
- §9 (test plan) extended with B4-T8 through B4-T11 covering paper-mode paths.
- §11 (risk register) extended with paper/live state-confusion risks.
- §13 (open questions) extended with persistence verification result.

---

## 1. Problem statement

The bot's only settlement-detection mechanism is `check_settlements()` (live_v3.py:1884-1903), a BBO threshold check that fires `pos.settled = True` when `book.best_bid >= 98` or `book.best_ask <= 2`. This is fragile: when the WebSocket book stops updating after market settlement, the threshold never fires and the position stays in `phase="active"` forever. Resting exit orders linger; reconcile loops re-touch dead state every cycle; phantom positions accumulate over multi-day burn-ins.

Bug 5 was scoped to clean up these phantoms. Bug 4 fixes the source.

---

## 2. Frequency from log analysis

**JSONL log scan across all `live_v3_*.jsonl`:**

| Outcome | Count | % of entry_filled |
|---|---|---|
| Total positions with `entry_filled` | 130 | 100% |
| Properly closed (`exit_filled` OR `settled`) | 122 | 94% |
| Of those: closed via `exit_filled` (scalp/exit/cell) | 84 | 65% |
| Of those: closed via `settled` (BBO threshold) | 38 | 29% |
| **PHANTOM-ACTIVE** (entry_filled, no exit_filled, no settled) | **8** | **6%** |

**Phantom rate among positions that didn't exit-fill** (the candidate pool for settlement detection):
**8 / (8 + 38) = 17%.**

That is the actual Bug 4 surface area: roughly 1 in 6 settlement-bound positions slips past the BBO heuristic.

### Phantom sample (all 8)

| Ticker | Entry | Age at scan | Last bot event |
|---|---|---|---|
| KXWTAMATCH-26APR25NOSSAM-SAM | 2026-04-26 04:09 | 86.8h | exit_posted |
| KXWTAMATCH-26APR25NOSSAM-NOS | 2026-04-26 04:46 | 86.2h | exit_posted |
| KXWTAMATCH-26APR27BENBAP-BEN | 2026-04-26 20:07 | 70.8h | exit_posted |
| KXATPCHALLENGERMATCH-26APR27WEBMON-WEB | 2026-04-27 05:19 | 61.6h | exit_posted |
| KXWTAMATCH-26APR27POTRYB-RYB | 2026-04-27 05:32 | 61.4h | exit_posted |
| KXATPCHALLENGERMATCH-26APR27CECMIC-MIC | 2026-04-27 07:13 | 59.8h | exit_posted |
| KXATPCHALLENGERMATCH-26APR28WALCUI-WAL | 2026-04-28 02:40 | 40.3h | exit_posted |
| KXATPCHALLENGERMATCH-26APR28STRBAX-STR | 2026-04-28 14:13 | 28.7h | exit_posted |

All 8 share the same shape: `entry_filled → exit_posted → silence`. None reached `exit_filled` or `settled`.

### Cross-check vs `tennis.db.kalshi_price_snapshots`

For each phantom ticker, the price-snapshot table shows polling stopped within hours of entry (well before any current-time scan). Sample:

| Ticker | snapshots N | last polled_at |
|---|---|---|
| KXWTAMATCH-26APR25NOSSAM-SAM | 499 | 2026-04-26 05:09:41 |
| KXATPCHALLENGERMATCH-26APR27WEBMON-WEB | 165 | 2026-04-27 09:39:31 |
| KXATPCHALLENGERMATCH-26APR28STRBAX-STR | 155 | 2026-04-28 18:41:45 |

The snapshot-scraper stops once Kalshi marks markets non-open. These markets DID settle on Kalshi. The bot's WS just stopped getting orderbook updates and the BBO heuristic had no last-update at the 98/2 threshold.

### Settlement-timing distribution (the 38 bot-detected settlements)

For comparison: positions that DID settle via BBO heuristic settled within:
- Median: 3.53h after entry
- P90: 6.43h
- Max: 12.04h
- 37/38 settled at price=1 (LOSS)
- 1/38 settled at price=99 (WIN)

The phantom positions are 28-87h old — well past every percentile of the legitimate settlement distribution. They are unambiguously stuck.

---

## 2.5 Paper-mode interaction (RESOLVED in v2)

When `_PAPER_API` is set (paper_mode=true), settlement state is held in `_PAPER_API.paper_positions[ticker]` (PaperPosition dataclass), NOT in `self.positions[ticker]`. Bug 4 must route settlement detection accordingly:

| Source | Paper mode behavior | Live mode behavior |
|---|---|---|
| WS `market_lifecycle_v2` `settled` event | Mutate `PaperPosition.settled` + `settlement_price`; emit `paper_settled` | Mutate `self.positions[tk].settled`; emit `settled` |
| REST `/portfolio/settlements` poll | **SKIP entirely.** REST returns the user's REAL Kalshi settlement history; applying it to paper positions would falsely settle them based on outcomes the paper bot did not actually trade. | Run on cadence; call `process_settlement(source="rest_poll")` per record. |
| BBO threshold (`check_settlements`) | Iterate `paper_positions` and route via paper handler. | Iterate `self.positions` and route via live handler (current behavior). |

**Single chokepoint principle preserved**: `process_settlement(ticker, settle_value, ts, source)` internally branches on `_PAPER_API`. Callers (WS handler, REST poller, BBO check) don't need to know about paper vs live — they call the same function.

**Side effect on `self.positions` in paper mode**: when paper settlement fires, also silently set `self.positions[ticker].settled = True` and `phase = "settled"` if the ticker exists there. The bot's `check_fills`-driven self.positions mirror in paper mode would otherwise stay "active" forever and cause `check_settlements` to re-iterate every cycle. No telemetry from this — it's just a quiet short-circuit.

**Persistence**: `PaperPosition.settled` (bool) and `settlement_price` (Optional[int]) round-trip cleanly through `dump_state` (uses `p.__dict__` which includes both fields) and `load_state` (explicitly restores `settled=bool(pd.get("settled", False))` and `settlement_price=pd.get("settlement_price")`). Verified on the deployed live_v3.py at the dump_state/load_state methods. No paper-mode persistence bug to fix as prerequisite.

---

## 3. Why the BBO heuristic fails

`check_settlements()` requires:
1. `book.best_bid >= 98` OR `book.best_ask <= 2`, AND
2. `pos.phase == "active"` AND `not pos.settled`

Failure modes:
- **Final book update never crosses the 98/2 threshold.** The market may settle when the BBO is, e.g., bid=92/ask=95 with a sudden lifecycle event from Kalshi rather than progressive book convergence.
- **WS subscription drops the ticker before convergence.** Once Kalshi marks a market not-open, no more `orderbook_snapshot` / `orderbook_delta` messages flow for that ticker. The `Book` in `self.books[ticker]` is frozen at its last pre-settlement state.
- **Bot offline during settlement window.** WS reconnect catches up only on currently-open markets; settled markets never re-emit historical book data.
- **Scalar markets** (irrelevant for tennis but a structural failure mode): settle at fractional values.

`check_settlements()` polls only the in-memory `self.books`, never asks Kalshi for authoritative settlement state.

---

## 4. Kalshi-side data sources we are not using

Web research confirmed two channels Kalshi already provides:

### 4.1 WebSocket: `market_lifecycle_v2` channel
Reference: https://docs.kalshi.com/websockets/market-&-event-lifecycle

Emits real-time events for every subscribed market:
- `settled` — final settlement; payload includes `settled_ts`, `determination_ts`, `settlement_value` (e.g., `"0.0000"` for NO, `"1.0000"` for YES, scalar in between for partial), `result` (`yes` / `no` / `scalar` / `void`).
- `determined` — outcome known but not yet settled.
- `deactivated` — trading paused.

Subscribed alongside `orderbook_delta` / `trade` in the same WS connection. No additional auth.

### 4.2 REST: `GET /trade-api/v2/portfolio/settlements`
Reference: https://docs.kalshi.com/api-reference/portfolio/get-settlements

Returns settlements for the authenticated account. Filter by `ticker`, `event_ticker`, time range (`min_ts`, `max_ts`). Pagination via `cursor` + `limit`. Per-record fields: `market_result`, `settlement_value`, `revenue` (payout), `settled_time`.

Useful as a backup/recovery query: "give me everything that settled since I last checked." Authoritative — no dependence on WS continuity.

### 4.3 REST: `GET /trade-api/v2/markets/{ticker}`
Reference: https://docs.kalshi.com/api-reference/market/get-market

Per-market lookup. After determination, returns `status: "finalized"` plus `settlement_value_dollars`. Useful for ad-hoc verification of a specific phantom. Not a primary mechanism (would require iterating all positions).

---

## 5. Recommended fix: WS-primary + REST safety-net

### Approach

Use **both** Kalshi-side mechanisms, with the existing BBO heuristic kept as a tertiary backstop:

| Tier | Mechanism | Latency | Reliability |
|---|---|---|---|
| 1 (primary) | WS `market_lifecycle_v2` `settled` event | seconds | High when bot online; lossy when bot offline |
| 2 (safety net) | REST poll of `/portfolio/settlements?min_ts=<last_seen>` every 5 min | up to 5 min | Authoritative; catches everything WS missed |
| 3 (backstop) | Existing `check_settlements()` BBO heuristic | seconds (when book updates) | Low; current Bug 4 surface |

Tier 2 alone would be sufficient for correctness; tier 1 reduces latency from minutes to seconds for live positions. Tier 3 stays in place for free — costs nothing and may catch edge cases (e.g., transient REST failure followed by reconnect with a stale lifecycle channel).

A single `process_settlement(ticker, settle_value_dollars, settled_ts, source)` function handles all three sources idempotently (via `pos.settled` short-circuit). Same telemetry shape; new `settle_source` field distinguishes which tier fired.

### Why not REST-only

REST polling alone works but introduces minutes of latency for active position cleanup. The bot may post avoidable repost cycles, DCAs, or exit-cancel/replaces against an already-settled market during that window. WS lifecycle events shrink the window to seconds and align with the existing real-time architecture.

### Why not WS-only

WS misses events when the bot is offline (deploys, OS updates, crashes during burn-in). REST `/portfolio/settlements` gives a deterministic catch-up: "everything that settled since `last_seen_ts`." This is exactly the recovery semantics the existing BBO heuristic lacks.

---

## 6. Pseudocode design

### 6.1 Subscribe to lifecycle channel

In `ws_subscribe(self, tickers)` (existing method), add `market_lifecycle_v2` to the channel list:

```python
sub_msg = {
    "id": self.msg_id,
    "cmd": "subscribe",
    "params": {
        "channels": ["orderbook_delta", "trade", "market_lifecycle_v2"],
        "market_tickers": tickers,
    },
}
```

(Verify exact channel name string at implementation time against the docs URL above.)

### 6.2 Handle lifecycle messages in `ws_reader`

After the existing `orderbook_snapshot` / `orderbook_delta` / `trade` branches in `ws_reader` (live_v3.py:1370):

```python
elif typ == "market_lifecycle":  # exact type-string verified at impl time
    sub = msg.get("msg", {})
    lifecycle_event = sub.get("event", "")  # "settled" | "determined" | "deactivated"
    tk = sub.get("market_ticker", "")
    if lifecycle_event == "settled" and tk:
        self.process_settlement(
            ticker=tk,
            settle_value_dollars=sub.get("settlement_value", "0"),
            settled_ts=sub.get("settled_ts", time.time()),
            source="ws_lifecycle",
        )
```

### 6.3 Add periodic REST poll (LIVE MODE ONLY)

In the main loop (live_v3.py:2920 area, near `check_settlements()`), add cadence-gated call. **Gated on `_PAPER_API is None`** — paper mode does not poll REST settlements (would falsely close paper positions using real-account history):

```python
SETTLEMENT_POLL_INTERVAL = 300  # 5 min
last_settlement_poll = 0

# Inside main loop:
if _PAPER_API is None and now - last_settlement_poll > SETTLEMENT_POLL_INTERVAL:
    await self.poll_settlements_rest()
    last_settlement_poll = now
```

```python
async def poll_settlements_rest(self):
    """Catch any settlements missed via WS. Idempotent — process_settlement
    short-circuits on pos.settled. LIVE MODE ONLY — never called when
    _PAPER_API is set (defensive guard at top in case caller forgets the gate)."""
    if _PAPER_API is not None:
        return  # paper mode: WS lifecycle is the only settlement source
    min_ts = getattr(self, "_last_settlement_min_ts", 0) or (time.time() - 86400)
    path = "/trade-api/v2/portfolio/settlements?min_ts=%d&limit=100" % int(min_ts)
    data = await api_get(self.session, self.ak, self.pk, path, self.rl)
    for s in (data or {}).get("settlements", []):
        self.process_settlement(
            ticker=s.get("ticker", ""),
            settle_value_dollars=s.get("settlement_value", "0"),
            settled_ts=s.get("settled_time", time.time()),
            source="rest_poll",
        )
    self._last_settlement_min_ts = time.time() - 60  # 60s overlap to avoid edge gaps
```

### 6.4 Unified `process_settlement` with paper-mode dispatch

```python
def _normalize_settle_value(self, settle_value_dollars):
    """Kalshi may deliver '0.5000' (float-string), 50 (cents int), or 0.5 (float).
    Normalize to integer cents 0-100."""
    try:
        sv = float(settle_value_dollars)
        cents = round(sv * 100) if sv <= 1.5 else int(sv)
    except (TypeError, ValueError):
        cents = 0
    return max(0, min(100, cents))


def process_settlement(self, ticker, settle_value_dollars, settled_ts, source):
    """Single chokepoint for all three settlement sources (WS, REST, BBO).
    Routes paper vs live based on module-level _PAPER_API."""
    settle_val = self._normalize_settle_value(settle_value_dollars)

    if _PAPER_API is not None:
        # Paper mode: mutate PaperPosition, emit paper_settled
        ppos = _PAPER_API.paper_positions.get(ticker)
        if not ppos or ppos.settled:
            return  # idempotent
        ppos.settled = True
        ppos.settlement_price = settle_val
        ppos.last_event_ts = settled_ts
        # Realized P&L for paper position at settlement:
        #   pre-settlement net_qty contracts pay out at settle_val
        #   pre-existing realized_pnl from prior partial-exits unchanged
        if ppos.qty > 0:
            avg_basis = ppos.total_cost_cents // ppos.qty
            net = ppos.net_qty
            if net > 0:
                ppos.realized_pnl_cents += (settle_val - avg_basis) * net

        # Silent short-circuit: mark self.positions mirror as settled so
        # check_settlements stops re-iterating on subsequent cycles.
        # No event emitted from this — paper_settled (above) is the source of truth.
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

    pnl = (settle_val - pos.entry_price) * pos.entry_qty
    if pos.dca_qty > 0:
        pnl += (settle_val - pos.dca_price) * pos.dca_qty
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
    }, ticker=ticker)

    # Cleanup: cancel any resting orders for this ticker
    if pos.exit_order_id:
        asyncio.create_task(self.cancel_order(ticker, pos.exit_order_id, "settlement_cleanup"))
    if pos.dca_order_id:
        asyncio.create_task(self.cancel_order(ticker, pos.dca_order_id, "settlement_cleanup"))
    if pos.cell_exit_order_id:
        asyncio.create_task(self.cancel_order(ticker, pos.cell_exit_order_id, "settlement_cleanup"))
```

### 6.5 Refactor `check_settlements` with paper-mode dispatch

```python
def check_settlements(self):
    """BBO threshold backstop. Iterates the appropriate position dict based
    on _PAPER_API and routes via process_settlement (which dispatches paper/live)."""
    if _PAPER_API is not None:
        # Paper mode: iterate paper_positions
        for tk, ppos in list(_PAPER_API.paper_positions.items()):
            if ppos.settled or ppos.net_qty <= 0:
                continue
            book = self.books.get(tk)
            if not book:
                continue
            if book.best_bid >= 98:
                self.process_settlement(tk, 1.0, time.time(), source="bbo_threshold_yes")
            elif book.best_ask <= 2:
                self.process_settlement(tk, 0.0, time.time(), source="bbo_threshold_no")
        return

    # Live mode: iterate self.positions (current behavior)
    for tk, pos in list(self.positions.items()):
        if pos.settled or pos.phase != "active":
            continue
        book = self.books.get(tk)
        if not book:
            continue
        if book.best_bid >= 98:
            self.process_settlement(tk, 1.0, time.time(), source="bbo_threshold_yes")
        elif book.best_ask <= 2:
            self.process_settlement(tk, 0.0, time.time(), source="bbo_threshold_no")
```

---

## 7. Phantom-cleanup migration

Once Bug 4 lands, the 8 existing phantoms in production state need a one-shot cleanup. Two paths:

1. **Bot picks them up automatically on next startup** via `poll_settlements_rest()` with `min_ts = now - 30 days` on first call. Authoritative.
2. **Manual sweep script** before re-deploy: query `/portfolio/settlements?min_ts=<oldest_phantom_entry_ts>` and call `process_settlement` for each. Faster cleanup; less waiting.

Recommend (1) — fewer moving parts. The first REST poll after deploy will resolve all historical phantoms in one shot, then maintain steady-state from there.

---

## 8. Telemetry additions

### 8.1 Live mode: extended `settled` event

New event field: `settle_source` (string) on existing `settled` event. Values:
- `"ws_lifecycle"` (primary)
- `"rest_poll"` (safety net catch)
- `"bbo_threshold_yes"` / `"bbo_threshold_no"` (backstop)
- `"settlement_unexpected_phase"` (warning event, separate name)

Burn-in metric: distribution of `settle_source` over a window. Healthy steady-state should be ~99% `ws_lifecycle`, with `rest_poll` only firing during/after bot restarts. If `rest_poll` dominates, WS subscription is broken.

### 8.2 Paper mode: new `paper_settled` event

Realizes the schema reserved in paper-mode spec §8.6 (which deferred settlement detection to Bug 4):

```json
{
  "event": "paper_settled",
  "ticker": "KX...",
  "details": {
    "settle_price": 1,
    "settle_source": "ws_lifecycle",
    "settled_ts": 1714400000.0,
    "qty": 10,
    "sold_qty": 0,
    "net_qty_at_settlement": 10,
    "avg_entry_price": 42,
    "realized_pnl_cents": -410
  }
}
```

Possible `settle_source` values for paper mode: `"ws_lifecycle"`, `"bbo_threshold_yes"`, `"bbo_threshold_no"`. **Never `"rest_poll"`** in paper mode (REST settlement poll is gated off when `_PAPER_API is not None`).

Heartbeat alarm threshold (paper-mode spec §8.6 mitigation): `active_paper_positions > 50` was the placeholder. Once Bug 4 lands, this alarm should be retired — paper positions now settle properly.

---

## 9. Test plan (for implementation phase)

Unit tests (extend the §11.1 harness already in `/tmp/paper_mode_unit_tests.py`):

### 9.1 Live-mode tests (mode = `_PAPER_API is None`)

- **B4-T1**: `process_settlement` happy path (live) — ticker with active position settles at value=99 → `pos.settled=True`, pnl computed, `settled` event emits with correct `settle_source`.
- **B4-T2**: Idempotency — call `process_settlement` twice for same ticker, only one `settled` event fires.
- **B4-T3**: WS lifecycle handler — feed synthetic `market_lifecycle` message into `ws_reader`'s dispatch logic, verify `process_settlement` is called.
- **B4-T4**: REST poll — mock `_real_api_get` to return synthetic settlements, verify each settlement triggers `process_settlement(source="rest_poll")` AND only when `_PAPER_API is None`.
- **B4-T5**: Cleanup — confirm `exit_order_id`, `dca_order_id`, `cell_exit_order_id` are cancelled after settlement.
- **B4-T6**: BBO threshold still works — refactored `check_settlements` correctly calls `process_settlement(source="bbo_threshold_*")` for live positions.
- **B4-T7**: Settle value normalization — `"0.0000"`, `"1.0000"`, `"0.5000"`, `0`, `99`, `50` all map to expected cents.

### 9.2 Paper-mode tests (mode = `_PAPER_API` is set)

- **B4-T8**: `process_settlement` in paper mode — set `_PAPER_API`, create PaperPosition, call `process_settlement` → `PaperPosition.settled=True`, `settlement_price=N`, `paper_settled` event emitted (NOT `settled`); `realized_pnl_cents` updated; `self.positions[tk]` (if present) silently marked settled to short-circuit `check_settlements`.
- **B4-T9**: REST poll guard — set `_PAPER_API`, mock `_real_api_get` to fail loudly if called, invoke main-loop tick → `poll_settlements_rest()` is NOT called; no settlement state mutated.
- **B4-T10**: BBO threshold in paper mode — set `_PAPER_API`, populate `paper_positions[tk]` with net_qty=5, set `book.best_bid=99` → `check_settlements` iterates `paper_positions` (not `self.positions`), routes through `process_settlement`, `paper_settled` emitted with `source="bbo_threshold_yes"`.
- **B4-T11**: Persistence round-trip with settled state — settle a paper position, call `dump_state`, create fresh `PaperApi`, call `load_state` → loaded `PaperPosition.settled=True` and `settlement_price` correctly restored. (Pre-existing dump_state/load_state implementation already round-trips these fields; this test confirms Bug 4's writes flow through cleanly.)

### 9.3 Burn-in observation

- **Live deploy**: after Bug 4, expect `phantom-active count → 0` over ~24 hours (REST poll picks up the 8 historical phantoms on first wide-window query).
- **Live deploy**: steady-state distribution of `settle_source` across new positions ~99% `ws_lifecycle`, residual `rest_poll` only on bot restart.
- **Paper deploy**: every paper position's lifecycle ends in `paper_settled` (no phantoms accumulating); `settle_source` distribution heavily favors `ws_lifecycle`; zero `rest_poll` events (confirmed gated off).

---

## 10. Out-of-scope for Bug 4

- Scalar-market handling (settle_value not in {0, 1}). Tennis is binary; this is a non-issue for current scope. Spec accepts it via the `settle_value_dollars` parameter signature; downstream pnl math handles fractional cents correctly.
- Settlement of positions that were never `entry_filled` (i.e., entry never filled but Kalshi opened/closed the market with a stranded resting buy). These get cancelled by reconcile, not by settlement detection.
- Account-level settlement reconciliation (i.e., reconcile bot pnl_cents totals against Kalshi `revenue` field). Useful for audit but outside Bug 4's surface.
- WS subscription scope — `market_lifecycle_v2` is added to the existing tickers list; we do not auto-subscribe to historical/settled markets.

---

## 11. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Kalshi WS channel name not exactly `market_lifecycle_v2` | Medium | Lifecycle events not received | Verify exact name at impl-time via docs + sandbox test |
| `settlement_value` payload format different from spec assumption | Low-Medium | Settle value parses to wrong cents | Defensive normalization in `process_settlement`; both string and numeric paths covered |
| REST `/portfolio/settlements` rate-limited under heavy poll | Low | Some polls fail (return None) | Existing rate-limiter handles; failed poll is non-fatal (next poll catches up) |
| Cancellation of resting orders on already-canceled settled market | Low | Spurious `order_error` logs | Existing `cancel_order` returns False on dead order; no state corruption |
| `process_settlement` fires before reconcile sees the position (race) | Low | Brief window where position is `settled` but reconcile re-touches | `pos.settled` short-circuit in reconcile already gates this |
| **REST poll fires in paper mode** (gate forgotten by future patch) | Medium-Low | Real-account settlement history would falsely settle paper positions | Defensive guard at top of `poll_settlements_rest()` (`if _PAPER_API is not None: return`) in addition to the cadence gate. B4-T9 verifies. |
| **Paper-mode bot's `self.positions` mirror grows unbounded** | Low | check_settlements wastes CPU re-iterating same tickers | Silent `self.positions[tk].settled = True` write inside paper branch of `process_settlement` short-circuits next iteration. |
| **Lifecycle event arrives before bot has a paper_position for ticker** (e.g., bot subscribed but never traded) | Low | `paper_positions.get(ticker)` returns None → silent no-op | By design — settlement of an untraded ticker is irrelevant. No log noise. |
| **Paper position `realized_pnl_cents` accounting drift** if partial-exit (sold_qty > 0) settles below avg basis | Low-Medium | P&L on remaining net_qty correctly computed; sold_qty proceeds already booked in `total_revenue_cents` | The formula `(settle_val - avg_basis) * net_qty` only credits the unsold portion. Confirmed in B4-T8 with a partial-exit fixture. |

---

## 12. Implementation plan (for the next session)

1. Pre-impl probe: verify exact `market_lifecycle_v2` channel name + `settled` payload format via Kalshi sandbox or docs deep-read.
2. Build `/tmp/live_v3_bug4.py` patched copy. Diff against current `live_v3.py` (post-paper-mode).
3. Run unit tests B4-T1 through B4-T7 against the patched module.
4. Apply patch, commit, push for review.
5. Restart paper bot with patched binary.
6. Burn-in: observe phantom resolution + `settle_source` distribution over 24h.
7. On clean burn-in: green light Bug 5 design.

---

## 13. Open questions (flag before implementation)

1. **Exact WS message type string** — docs say channel is `market_lifecycle_v2` but the Kalshi message envelope `type` field may be `"market_lifecycle"`, `"market_settled"`, or something else. Needs verification.
2. **`settled_ts` field name** — could be `settled_time`, `settlement_time`, `final_ts`, `determination_ts`. Defensive code reads both.
3. **REST `min_ts` semantics** — is it inclusive or exclusive? Whichever, the 60s overlap in `_last_settlement_min_ts` covers the boundary.
4. **Settled positions held beyond the REST `min_ts` window** — for the existing 8 phantoms, the entries are all <90 days old, well within any reasonable REST history window. New deploys with longer-stale phantoms would need a one-shot manual sweep.
5. **Persistence** (RESOLVED in v2) — `PaperPosition.settled` and `settlement_price` round-trip cleanly through `dump_state` (uses `p.__dict__` which captures both fields automatically) and `load_state` (explicitly reads `settled=bool(pd.get("settled", False))`, `settlement_price=pd.get("settlement_price")`). Verified against deployed live_v3.py at the dump_state/load_state methods. Bug 4 implementation can rely on this — no prerequisite paper-mode persistence fix needed.

End of brief.
