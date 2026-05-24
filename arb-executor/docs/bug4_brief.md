# Bug 4 Brief — Missing Settlement Detection

**Version**: v4 (probe-corrected WS/REST schema + four design decisions resolved)
**Status**: design locked, ready for implementation, no code written
**Author**: paired with operator, 2026-04-29; v4 promotion 2026-05-24
**Target**: live_v3.py settlement detection path

## Changes in v4 (this revision)

Folds in `docs/bug4_probe.md` §4.1/§4.2/§7 (the probe verified Kalshi's WS and REST schemas against the docs and found the v3 pseudocode assumed payload fields that do not exist). Four open design decisions are resolved with operator-confirmed answers (§0).

- **§4 / §6.2 — WS settled payload is MINIMAL.** The `market_lifecycle_v2` `settled` event carries only `market_ticker`, `event_type`, `settled_ts` — **no settlement value, no `market_result`**. v3's pseudocode read `sub.get("settlement_value")` from the WS payload; that field does not exist. v4 replaces the inline handler with an async REST hop to `GET /markets/{ticker}` that fetches `settlement_value_dollars` once `status == "finalized"` (with a pre-finalized race fallback to the REST poll).
- **§6.2 — WS envelope strings corrected.** Envelope `type` is `"market_lifecycle_v2"` (with the `_v2` suffix), not `"market_lifecycle"`. The event discriminator is the nested `msg.event_type`, not `msg.event`.
- **§6.3 — REST settlements field names corrected.** Per-record settlement value is `value` (integer cents, **nullable**), not `settlement_value`. Outcome is `market_result` (enum `yes`/`no`/`scalar`/`void`). Timestamp is `settled_time`, an **RFC3339 string** (e.g. `"2024-01-15T12:00:00Z"`), not Unix epoch — must be parsed. v4 maps `market_result` → cents at the call site.
- **§6.4 — `_normalize_settle_value` removed (decision c).** Central format-inference (`round(sv*100) if sv<=1.5 else int(sv)`) was brittle. Each source now produces integer cents at its own call site, where the wire format is known. `process_settlement` takes `settle_val_cents` (already 0–100) and applies only a defensive clamp.
- **Void handling (decision b).** `void` settlements are **skipped from automatic processing**, logged, and flagged for manual reconciliation. v4 does NOT assume a 50¢ payout (a void typically refunds cost basis, not a 50¢ settlement — the accounting differs and is low-frequency, so it is handled by hand rather than guessed).
- Partial-exit P&L fix from v3 retained verbatim (double-entry assignment).

## Changes in v3

- §6.4 paper-mode branch: realized_pnl_cents formula rewritten as **assignment** (not increment) using full double-entry form: `realized_pnl_cents = total_revenue_cents - total_cost_cents + settle_val * net_qty`. The v2 formula (`+= (settle_val - avg_basis) * net_qty`) was wrong for the partial-exit case — it ignored the prior-partial-sell P&L because `realized_pnl_cents` is zero at settlement entry whenever `net_qty > 0` (existing `try_fill` only books realized P&L when `net_qty` hits zero). Worked example: buy 10@40 → sell 5@50 → settle 5@99. Expected total P&L = 50 + 295 = 345. v2 formula gave 295 (understated by 50); v3 formula gives 250 − 400 + 99×5 = 345. ✓
- §9.2 B4-T8: extended with partial-exit fixture covering the previously-broken case.
- §9.2 B4-T11: extended to explicitly verify `realized_pnl_cents` round-trips through dump/load (most-likely-to-drift field).
- §11 risk register: "partial-exit P&L accounting drift" entry rewritten — was a real bug in v2; now correctly handled in v3.

## Changes in v2

- §2.5 added: paper-mode interaction explicitly resolved.
- §6 (pseudocode) rewritten: `process_settlement` dispatches paper vs live based on `_PAPER_API` state; `poll_settlements_rest` gated on `_PAPER_API is None`; `check_settlements` iterates `paper_positions` in paper mode.
- §8 (telemetry) updated with `paper_settled` event schema.
- §9 (test plan) extended with B4-T8 through B4-T11 covering paper-mode paths.
- §11 (risk register) extended with paper/live state-confusion risks.
- §13 (open questions) extended with persistence verification result.

---

## 0. Design decisions (resolved for v4)

These four were open at v3. They are now locked; implementation does not re-litigate them.

| # | Decision | Resolution | Rationale |
|---|---|---|---|
| a | WS-hop vs caching `determination` events to source the settle value | **REST hop** to `/markets/{ticker}` on each WS `settled` | Simpler — no buffered determination-state to track/clean up. Overhead is ~100–200ms per settlement, firing <1×/min in steady state. The `determination`-cache optimization stays deferred (§13). |
| b | `void` market settlement semantics | **Skip from automatic processing; log; require manual reconciliation.** Do not assume 50¢ payout. | A void refunds cost basis, not a 50¢ settlement. Auto-applying 50¢ would mis-account. Voids are rare in tennis; manual handling is correct and cheap. |
| c | Settle-value normalization site | **Per-source at the call site.** Remove the central `_normalize_settle_value` inference. | Each source's wire format is known where it is read (REST = `market_result` enum / `value` cents; WS-hop = `settlement_value_dollars`; BBO = literal). Central inference across ambiguous formats is brittle. |
| d | Bug 4 prioritization (now vs defer to pre-redeploy) | **Proceed now.** | Locked execution-lock sequence puts Bug 4 first; it is the gate to a trustworthy paper-mode burn-in (paper-mode must be running by Sunday evening for live Monday 5am ET). |

---

## 1. Problem statement

The bot's only settlement-detection mechanism is `check_settlements()` (live_v3.py:1884), a BBO threshold check that fires `pos.settled = True` when `book.best_bid >= 98` or `book.best_ask <= 2`. This is fragile: when the WebSocket book stops updating after market settlement, the threshold never fires and the position stays in `phase="active"` forever. Resting exit orders linger; reconcile loops re-touch dead state every cycle; phantom positions accumulate over multi-day burn-ins.

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
| WS `market_lifecycle_v2` `settled` event | Run the async `/markets/{ticker}` hop (public data, paper-safe), then mutate `PaperPosition.settled` + `settlement_price`; emit `paper_settled` | Same hop, then mutate `self.positions[tk].settled`; emit `settled` |
| REST `/portfolio/settlements` poll | **SKIP entirely.** REST returns the user's REAL Kalshi settlement history; applying it to paper positions would falsely settle them based on outcomes the paper bot did not actually trade. | Run on cadence; call `process_settlement(source="rest_poll")` per record. |
| BBO threshold (`check_settlements`) | Iterate `paper_positions` and route via paper handler. | Iterate `self.positions` and route via live handler (current behavior). |

**Single chokepoint principle preserved**: `process_settlement(ticker, settle_val_cents, settled_ts, source)` internally branches on `_PAPER_API`. Callers (WS hop, REST poller, BBO check) don't need to know about paper vs live — they call the same function with already-normalized integer cents.

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

## 4. Kalshi-side data sources (schema verified by probe)

Web research + probe (`docs/bug4_probe.md`) confirmed the channels Kalshi provides and their exact payloads.

### 4.1 WebSocket: `market_lifecycle_v2` channel
Reference: https://docs.kalshi.com/websockets/market-&-event-lifecycle

Subscribed alongside `orderbook_delta` / `trade` in the same WS connection. No additional auth. Inbound envelope `type` is literally `"market_lifecycle_v2"`; the event discriminator is the nested `msg.event_type`.

Event types on this channel:
- `settled` — final settlement. **Payload is minimal:** `market_ticker`, `event_type`, `settled_ts` (Unix epoch seconds). It does **NOT** carry `market_result`, `settlement_value`, `value`, `revenue`, or any position/cost info. Verbatim docs example:
  ```json
  { "type": "market_lifecycle_v2", "sid": 13,
    "msg": { "market_ticker": "INXD-23SEP14-B4487", "event_type": "settled", "settled_ts": 1694808000 } }
  ```
- `determination` — outcome known but not yet settled; carries `market_result` (yes/no/scalar/void). Used only by the deferred caching optimization (§13).
- `deactivated` — trading paused.

Because the `settled` event lacks the payout, the WS path must do a follow-up REST hop to source the settlement value (§4.3, §6.2).

### 4.2 REST: `GET /trade-api/v2/portfolio/settlements`
Reference: https://docs.kalshi.com/api-reference/portfolio/get-settlements

Returns settlements for the authenticated account. Filter by `ticker`, `event_ticker`, time range (`min_ts` exclusive, `max_ts`). Pagination via `cursor` + `limit` (default 100, max 1000). Top-level array key is `"settlements"`. Per-record fields (verbatim from probe §2b):
- `ticker` (string)
- `event_ticker` (string)
- `market_result` (enum: `yes` / `no` / `scalar` / `void`)
- `value` (integer cents, **nullable**) — per-contract settlement payout
- `revenue` (integer cents) — total account payout
- `settled_time` (**RFC3339 string**, e.g. `"2024-01-15T12:00:00Z"` — NOT Unix epoch)
- `yes_count_fp`, `yes_total_cost_dollars`, `no_count_fp`, `no_total_cost_dollars`, `fee_cost`

Authoritative — no dependence on WS continuity. Used as the live-mode safety-net catch-up: "everything that settled since `last_seen_ts`."

### 4.3 REST: `GET /trade-api/v2/markets/{ticker}`
Reference: https://docs.kalshi.com/api-reference/market/get-market

Public market data — **NOT account-scoped**, so safe to call in paper mode (passes through `PaperApi.handle_get` → `_real_api_get` per paper-spec §5.1; does not leak real-account state into paper accounting). After determination, returns `status: "finalized"` plus `settlement_value_dollars` (and/or `settlement_value`). This is the value-fetch for the WS `settled` path: when a `settled` lifecycle event arrives (which lacks the value), hit this endpoint once to obtain it.

---

## 5. Recommended fix: WS-primary + REST safety-net

### Approach

Use **both** Kalshi-side mechanisms, with the existing BBO heuristic kept as a tertiary backstop:

| Tier | Mechanism | Latency | Reliability |
|---|---|---|---|
| 1 (primary) | WS `market_lifecycle_v2` `settled` event → `/markets/{ticker}` value hop | seconds | High when bot online; lossy when bot offline |
| 2 (safety net) | REST poll of `/portfolio/settlements?min_ts=<last_seen>` every 5 min (LIVE ONLY) | up to 5 min | Authoritative; catches everything WS missed |
| 3 (backstop) | Existing `check_settlements()` BBO heuristic | seconds (when book updates) | Low; current Bug 4 surface |

Tier 2 alone would be sufficient for correctness; tier 1 reduces latency from minutes to seconds for live positions. Tier 3 stays in place for free — costs nothing and may catch edge cases (e.g., transient REST failure followed by reconnect with a stale lifecycle channel).

A single `process_settlement(ticker, settle_val_cents, settled_ts, source)` function handles all three sources idempotently (via `pos.settled` short-circuit). Same telemetry shape; the `settle_source` field distinguishes which tier fired. Each source normalizes its own wire format to integer cents before calling (decision c).

### Why not REST-only

REST polling alone works but introduces minutes of latency for active position cleanup. The bot may post avoidable repost cycles, DCAs, or exit-cancel/replaces against an already-settled market during that window. WS lifecycle events shrink the window to seconds and align with the existing real-time architecture.

### Why not WS-only

WS misses events when the bot is offline (deploys, OS updates, crashes during burn-in). REST `/portfolio/settlements` gives a deterministic catch-up: "everything that settled since `last_seen_ts`." This is exactly the recovery semantics the existing BBO heuristic lacks. WS also requires the §4.3 value hop, which can transiently race ahead of finalization (handled by falling back to the REST poll).

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

### 6.2 Handle lifecycle messages in `ws_reader` (probe-corrected)

After the existing `orderbook_snapshot` / `orderbook_delta` / `trade` branches in `ws_reader` (live_v3.py:1370). The envelope `type` is `"market_lifecycle_v2"`; the event is `msg.event_type`; the settled payload has no value, so dispatch to an async hop:

```python
elif typ == "market_lifecycle_v2":
    sub = msg.get("msg", {})
    if sub.get("event_type") == "settled":
        tk = sub.get("market_ticker", "")
        settled_ts = sub.get("settled_ts", time.time())
        if tk:
            # Don't block the WS reader on a REST call — fire and forget.
            asyncio.create_task(self._handle_ws_settlement(tk, settled_ts))
    # determination / deactivated: ignored in v1 (see §13 deferred caching)


async def _handle_ws_settlement(self, ticker, settled_ts):
    """WS settled events carry no settlement value (§4.1). Fetch it from the
    public /markets/{ticker} endpoint (paper-safe — passes through to real
    Kalshi). Decoupled into its own coroutine so the WS reader loop is not
    blocked by the REST call."""
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
```

### 6.3 Add periodic REST poll (LIVE MODE ONLY, probe-corrected)

In the main loop (live_v3.py:2920 area, near `check_settlements()`), add a cadence-gated call. **Gated on `_PAPER_API is None`** — paper mode does not poll REST settlements (would falsely close paper positions using real-account history):

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
        except (TypeError, ValueError):
            settled_ts = time.time()
        self.process_settlement(
            ticker=s.get("ticker", ""),
            settle_val_cents=settle_val_cents,
            settled_ts=settled_ts,
            source="rest_poll",
        )
    self._last_settlement_min_ts = time.time() - 60  # 60s overlap to avoid edge gaps
```

(`datetime` is `from datetime import datetime` — verify the import exists at impl time.)

### 6.4 Unified `process_settlement` with paper-mode dispatch

`process_settlement` now receives **already-normalized integer cents** (decision c removed the central `_normalize_settle_value`). It applies only a defensive clamp.

```python
def process_settlement(self, ticker, settle_val_cents, settled_ts, source):
    """Single chokepoint for all three settlement sources (WS, REST, BBO).
    Routes paper vs live based on module-level _PAPER_API.
    settle_val_cents is integer cents 0-100, already normalized at the call site."""
    settle_val = max(0, min(100, int(settle_val_cents)))  # defensive clamp only

    if _PAPER_API is not None:
        # Paper mode: mutate PaperPosition, emit paper_settled
        ppos = _PAPER_API.paper_positions.get(ticker)
        if not ppos or ppos.settled:
            return  # idempotent
        ppos.settled = True
        ppos.settlement_price = settle_val
        ppos.last_event_ts = settled_ts

        # Realized P&L at settlement — full double-entry form.
        # ASSIGNMENT (not +=) because this is the closing P&L computation:
        #   total_revenue_cents already accounts for all prior partial sells
        #     (booked at fill time inside PaperFillSimulator.try_fill)
        #   settle_val * net_qty is the settlement payout on remaining unsold contracts
        #   total_cost_cents is everything paid in
        #
        # NOTE: existing try_fill only writes realized_pnl_cents when net_qty
        # hits zero. For partial-exit positions reaching settlement with
        # net_qty > 0 and sold_qty > 0, realized_pnl_cents is still zero at
        # this point — so we must derive the final P&L from the totals, not
        # increment.
        #
        # Worked example:
        #   Buy 10 @ 40c -> qty=10, total_cost_cents=400, sold_qty=0, total_revenue_cents=0
        #   Sell 5 @ 50c -> sold_qty=5, total_revenue_cents=250, net_qty=5 (so realized_pnl_cents stays 0)
        #   Settle @ 99c -> realized_pnl_cents = 250 - 400 + 99*5 = -150 + 495 = 345
        #     (matches expected: 50 P&L on the partial sell + 295 P&L on the settled portion)
        ppos.realized_pnl_cents = (
            ppos.total_revenue_cents
            - ppos.total_cost_cents
            + settle_val * ppos.net_qty
        )

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

The BBO backstop passes literal cents (yes=100, no=0) — already normalized.

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

Warning/diagnostic events (separate names):
- `"settlement_unexpected_phase"` — settle arrived while position not active/entry_pending.
- `"ws_settled_pre_finalized"` — WS settled fired but `/markets/{ticker}` not yet `finalized` (REST poll will catch).
- `"settlement_void_manual"` — a void was detected and skipped; needs manual reconciliation.
- `"ws_settle_value_unparseable"` / `"rest_settlement_unknown_result"` — defensive parse failures.

Burn-in metric: distribution of `settle_source` over a window. Healthy steady-state should be ~99% `ws_lifecycle`, with `rest_poll` only firing during/after bot restarts. If `rest_poll` dominates, WS subscription is broken. A nonzero `settlement_void_manual` stream is the manual-reconciliation queue.

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
- **B4-T3**: WS lifecycle handler — feed synthetic `market_lifecycle_v2` / `event_type="settled"` message into `ws_reader`'s dispatch logic; mock `/markets/{ticker}` to return `status="finalized"`, `settlement_value_dollars="1.0000"`; verify `_handle_ws_settlement` fires and `process_settlement(source="ws_lifecycle", settle_val_cents=100)` is called. Add a `status="active"` variant → verify `ws_settled_pre_finalized` logged and NO settlement. Add a `result="void"` variant → verify `settlement_void_manual` logged and NO settlement.
- **B4-T4**: REST poll — mock `api_get` to return synthetic settlements with `market_result` ∈ {yes, no, scalar, void} and RFC3339 `settled_time`; verify each non-void triggers `process_settlement(source="rest_poll")` with correct cents (yes→100, no→0, scalar→`value`), `settled_ts` parsed from RFC3339, void→`settlement_void_manual` (no settle), AND the whole poll runs only when `_PAPER_API is None`.
- **B4-T5**: Cleanup — confirm `exit_order_id`, `dca_order_id`, `cell_exit_order_id` are cancelled after settlement.
- **B4-T6**: BBO threshold still works — refactored `check_settlements` correctly calls `process_settlement(source="bbo_threshold_*", settle_val_cents ∈ {100,0})` for live positions.
- **B4-T7**: Per-source normalization (replaces v3's central `_normalize_settle_value` test). Three call-site converters map correctly to integer cents 0–100:
  - WS hop: `settlement_value_dollars` `"1.0000"`→100, `"0.0000"`→0, `"0.5000"`→50, unparseable→`ws_settle_value_unparseable` (no settle).
  - REST poll: `market_result` yes→100, no→0, scalar(`value`=37)→37, void→skip, unknown→skip.
  - BBO: literal 100 / 0 passed through.

### 9.2 Paper-mode tests (mode = `_PAPER_API` is set)

- **B4-T8**: `process_settlement` in paper mode (three fixtures, all must pass):
  - **B4-T8a** _no-exit happy path_: PaperPosition with qty=10, sold_qty=0, total_cost_cents=400, total_revenue_cents=0; settle at 99c. Expected: `settled=True`, `settlement_price=99`, `realized_pnl_cents = 0 - 400 + 99*10 = 590`. `paper_settled` emitted (NOT `settled`); `self.positions[tk]` (if present) silently marked settled to short-circuit `check_settlements`.
  - **B4-T8b** _partial-exit fixture_ (covers the v2-formula bug): qty=10, sold_qty=5, total_cost_cents=400, total_revenue_cents=250 (5 contracts sold at 50c earlier); settle at 99c. Expected: `realized_pnl_cents = 250 - 400 + 99*5 = 345`. **NOT 295.** This case would have been undercounted by the v2 formula.
  - **B4-T8c** _fully-exited-then-settles_: qty=10, sold_qty=10, total_cost_cents=400, total_revenue_cents=600 (full exit at 60c), `realized_pnl_cents=200` from try_fill. Settle event arrives anyway (rare — settled position should not normally re-settle, but the idempotency guard `if ppos.settled` already handles this; this fixture verifies that BEFORE the settled flag is set in some weird edge ordering, the formula still computes correctly: `realized_pnl_cents = 600 - 400 + settle_val*0 = 200`, identical to what try_fill already booked).
- **B4-T9**: REST poll guard — set `_PAPER_API`, mock `api_get` to fail loudly if called with a `/portfolio/settlements` path, invoke main-loop tick → `poll_settlements_rest()` is NOT called; no settlement state mutated. (Note: `/markets/{ticker}` hop IS still permitted in paper mode — it is public data — so the guard is specific to the settlements poll.)
- **B4-T10**: BBO threshold in paper mode — set `_PAPER_API`, populate `paper_positions[tk]` with net_qty=5, set `book.best_bid=99` → `check_settlements` iterates `paper_positions` (not `self.positions`), routes through `process_settlement`, `paper_settled` emitted with `source="bbo_threshold_yes"` and `settle_price=100`.
- **B4-T11**: Persistence round-trip with settled state — use the partial-exit fixture from B4-T8b (qty=10, sold_qty=5, total_cost=400, total_revenue=250, settle@99 → realized_pnl_cents=345). Settle the paper position, call `dump_state`, create fresh `PaperApi`, call `load_state`. Verify on the loaded `PaperPosition`:
  - `settled == True`
  - `settlement_price == 99`
  - **`realized_pnl_cents == 345` (the settlement-computed value, not 0 or any partial)**
  - `total_revenue_cents == 250`, `total_cost_cents == 400`, `qty == 10`, `sold_qty == 5` (all balance fields preserved so re-derivation would yield same answer)

  `realized_pnl_cents` is the field most likely to drift if the formula changes (it's a derived value, not a balance counter). This test pins it explicitly. Pre-existing dump_state uses `p.__dict__` (captures all fields including `realized_pnl_cents`); load_state reads `realized_pnl_cents=int(pd.get("realized_pnl_cents", 0))`. Round-trip is mechanical; B4-T11 verifies Bug 4's writes flow through cleanly with the v3 formula.

### 9.3 Burn-in observation

- **Live deploy**: after Bug 4, expect `phantom-active count → 0` over ~24 hours (REST poll picks up the 8 historical phantoms on first wide-window query).
- **Live deploy**: steady-state distribution of `settle_source` across new positions ~99% `ws_lifecycle`, residual `rest_poll` only on bot restart.
- **Paper deploy**: every paper position's lifecycle ends in `paper_settled` (no phantoms accumulating); `settle_source` distribution heavily favors `ws_lifecycle`; zero `rest_poll` events (confirmed gated off); any `settlement_void_manual` events surfaced for hand-reconciliation.

---

## 10. Out-of-scope for Bug 4

- **Void auto-processing** (decision b): voids are logged + skipped, reconciled manually. Automatic void accounting (cost-basis refund) is a separate follow-up.
- **`determination`-event caching** to avoid the `/markets/{ticker}` hop (decision a): deferred; v1 uses the REST hop.
- Scalar-market handling beyond the `value`-cents passthrough. Tennis is binary; the `scalar` branch exists for completeness.
- Settlement of positions that were never `entry_filled` (stranded resting buy). These get cancelled by reconcile, not by settlement detection.
- Account-level settlement reconciliation (reconcile bot pnl_cents totals against Kalshi `revenue` field). Useful for audit — and would have caught the original foundation corruption — but outside Bug 4's surface; queue as a follow-up.
- WS subscription scope — `market_lifecycle_v2` is added to the existing tickers list; we do not auto-subscribe to historical/settled markets.

---

## 11. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| WS settled event lacks settlement value | **Confirmed (probe §1c)** | v3 inline value-read was broken | v4 §6.2 async `/markets/{ticker}` hop sources the value; B4-T3 covers it |
| `/markets/{ticker}` not yet `finalized` when WS `settled` arrives (race) | Medium | WS path can't settle yet | `ws_settled_pre_finalized` log + return; REST poll (live) or BBO (paper) catches it within the cycle |
| `/markets/{ticker}` exact value field name (`settlement_value` vs `settlement_value_dollars`) | Low-Medium | Value parses to 0 | v4 reads `settlement_value_dollars` with `settlement_value` fallback; first live settlement confirms (T11b) |
| REST `settled_time` RFC3339 vs epoch confusion | **Confirmed (probe §2b)** | Wrong ts | v4 §6.3 parses RFC3339 → epoch with try/except fallback |
| REST per-record field is `value` not `settlement_value` | **Confirmed (probe §2b)** | Wrong cents | v4 maps `market_result` → cents; `scalar` uses `value` |
| `void` mis-accounted as 50¢ | Low (rare) | Wrong P&L | decision b: skip + log + manual reconcile; never auto-settle void |
| Kalshi WS channel name not exactly `market_lifecycle_v2` | **Resolved (probe §1a/1b)** | — | Confirmed verbatim |
| REST `/portfolio/settlements` rate-limited under heavy poll | Low | Some polls fail (return None) | Existing rate-limiter handles; failed poll is non-fatal (next poll catches up) |
| Cancellation of resting orders on already-canceled settled market | Low | Spurious `order_error` logs | Existing `cancel_order` returns False on dead order; no state corruption |
| `process_settlement` fires before reconcile sees the position (race) | Low | Brief window where position is `settled` but reconcile re-touches | `pos.settled` short-circuit in reconcile already gates this |
| **REST settlements poll fires in paper mode** (gate forgotten by future patch) | Medium-Low | Real-account settlement history would falsely settle paper positions | Defensive guard at top of `poll_settlements_rest()` in addition to the cadence gate. B4-T9 verifies. The `/markets/{ticker}` hop is exempt — public data, paper-safe. |
| **Paper-mode bot's `self.positions` mirror grows unbounded** | Low | check_settlements wastes CPU re-iterating same tickers | Silent `self.positions[tk].settled = True` write inside paper branch short-circuits next iteration |
| **Lifecycle event arrives before bot has a paper_position for ticker** | Low | `paper_positions.get(ticker)` returns None → silent no-op | By design — settlement of an untraded ticker is irrelevant. No log noise. |
| **Paper position `realized_pnl_cents` accounting drift** for partial-exit case | **Was a real bug in v2; fixed in v3.** | Understated realized P&L | v3 double-entry assignment `= total_revenue_cents - total_cost_cents + settle_val * net_qty`. B4-T8b covers; B4-T11 verifies round-trip. |
| **`realized_pnl_cents` formula regression** if a future patch reverts to incremental form | Low (B4-T8b + B4-T11 pin the values) | Per-position P&L drift | B4-T8b pins three numerical answers; B4-T11 pins value across persistence |

---

## 12. Implementation plan (for the next session)

1. ~~Pre-impl probe~~ — DONE (`docs/bug4_probe.md`); schemas folded into this v4.
2. Build `/tmp/live_v3_bug4.py` patched copy. Diff against current `live_v3.py` (post-paper-mode). Touch points: `ws_subscribe` (§6.1), `ws_reader` dispatch + new `_handle_ws_settlement` (§6.2), main loop + new `poll_settlements_rest` (§6.3), new `process_settlement` (§6.4), refactored `check_settlements` (§6.5). Confirm `from datetime import datetime` import present.
3. Run unit tests B4-T1 through B4-T11 against the patched module.
4. Apply patch, commit, push for review.
5. Restart paper bot with patched binary.
6. Burn-in: observe phantom resolution + `settle_source` distribution + any `settlement_void_manual` / `ws_settled_pre_finalized` events over 24h.
7. On clean burn-in: green light Bug 5 design.

---

## 13. Open questions (runtime-verification only; design is locked)

1. **`/markets/{ticker}` exact value field** — `settlement_value` vs `settlement_value_dollars`. v4 reads `_dollars` with a plain-`settlement_value` fallback. First live settlement (T11b) confirms.
2. **`determination` event field shape** — needed only for the deferred caching optimization (decision a, §10). Not on the v1 path.
3. **REST `min_ts` inclusive/exclusive** — confirmed exclusive (`> min_ts`, probe §2c); 60s overlap window covers the boundary.
4. **Settled positions older than the REST history window** — the 8 phantoms are <90 days old, well within range. Longer-stale phantoms on a future deploy would need a one-shot manual sweep.
5. **Persistence** (RESOLVED in v2) — `PaperPosition.settled` and `settlement_price` round-trip cleanly through `dump_state` / `load_state`. Verified against deployed live_v3.py. No prerequisite fix needed.
6. **Sandbox capture of a real settled event** (T11b) — deferred (probe §5): opening a second WS subscription on the same credentials could kick the running paper bot off. Compensating control: first post-deploy live settlement is ground truth; field divergence logs (non-fatal) rather than crashes.

End of brief.
