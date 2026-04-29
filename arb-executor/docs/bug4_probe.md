# Bug 4 Pre-Implementation Probe Report

**Status**: docs verified, sandbox test deferred (with rationale)
**Date**: 2026-04-29
**Brief reference**: docs/bug4_brief.md @ commit `47bfce0` (v3)

---

## Summary

| Open question (brief §13) | Status | Adjustment to brief required? |
|---|---|---|
| 1a. WS subscribe channel name | ✓ confirmed `market_lifecycle_v2` | No |
| 1b. WS message envelope `type` | ✓ confirmed `market_lifecycle_v2` | Minor — exact string locked in |
| 1c. Settled-event payload field names | ⚠ **WS settled event payload is MINIMAL** — does NOT carry `market_result` or settlement value | **Yes — see §4** |
| 1c. settled_ts field name + format | ✓ confirmed `settled_ts`, Unix epoch seconds (integer) | No |
| 2a. REST top-level response key | ✓ confirmed `"settlements"` | No |
| 2b. REST per-record field names | ✓ confirmed; brief's `"settlement_value"` should be `"value"` (cents int, nullable) or computed from `revenue` | **Yes — see §4** |
| 2c. REST `min_ts` semantics | ✓ confirmed exclusive (`> min_ts`) | Minor — overlap window already in design |
| 2d. REST pagination | ✓ `cursor` field, default limit 100, max 1000 | No |
| 3. Sandbox capture of real settled event | **Deferred** — see §5 | N/A (deferred) |

---

## 1. WebSocket `market_lifecycle_v2` — verified verbatim

### 1a. Subscribe message channel string

Literally `"market_lifecycle_v2"` in `params.channels`.

Source: https://docs.kalshi.com/websockets/market-&-event-lifecycle

Implementation in `ws_subscribe`:
```python
"channels": ["orderbook_delta", "trade", "market_lifecycle_v2"]
```

### 1b. Inbound message envelope `type`

`type` field on the inbound envelope is literally `"market_lifecycle_v2"`. Verbatim from Kalshi docs:

```json
{
  "type": "market_lifecycle_v2",
  "sid": 13,
  "msg": { ... }
}
```

The bot's existing dispatch pattern `typ = msg.get("type", "")` and `if typ == "market_lifecycle_v2":` is correct. **NOT** `"market_lifecycle"` or `"market_settled"` — those don't appear.

The `event_type` value (e.g., `"settled"`, `"determination"`, `"deactivated"`) is NESTED inside `msg.event_type`, not the envelope's `type`.

### 1c. Settled event payload — CRITICAL GAP

Verbatim example from Kalshi docs:

```json
{
  "type": "market_lifecycle_v2",
  "sid": 13,
  "msg": {
    "market_ticker": "INXD-23SEP14-B4487",
    "event_type": "settled",
    "settled_ts": 1694808000
  }
}
```

**That's the entire payload.** The settled event carries:
- `market_ticker` (string)
- `event_type` (string, literal `"settled"`)
- `settled_ts` (integer, Unix epoch seconds)

It does NOT carry:
- `market_result` (would tell us yes/no/void)
- `settlement_value` / `value` / any payout cents
- `revenue`
- Any cost-basis or position info

This is the single most important deviation from what the brief assumed. The brief's pseudocode passes `settle_value_dollars` from the WS payload directly into `process_settlement` — that path is broken. **See §4 for the design adjustment.**

### 1d. Companion events on the same channel

Kalshi's `market_lifecycle_v2` channel publishes additional `event_type` values:

- `"determination"` — fires when the outcome becomes known. Per the prior research agent's notes, this carries `market_result` (yes/no/scalar/void) but precise field shape was not captured verbatim. Likely fires before `"settled"` for the same market.
- `"deactivated"` — trading paused.

The `determination` event **may** be the right place to capture `market_result`, paired with `settled_ts` from the later `settled` event. Buffering complexity; see §4.

---

## 2. REST `/trade-api/v2/portfolio/settlements` — verified verbatim

### 2a. Top-level response key

`"settlements"` (array). Pagination via top-level `"cursor"` (string).

### 2b. Per-record field names + types

Verbatim from docs:

```json
{
  "settlements": [
    {
      "ticker": "...",
      "event_ticker": "...",
      "market_result": "yes",
      "yes_count_fp": "10.00",
      "yes_total_cost_dollars": "5.60",
      "no_count_fp": "0.00",
      "no_total_cost_dollars": "0.00",
      "revenue": 1000,
      "settled_time": "2024-01-15T12:00:00Z",
      "fee_cost": "0.34",
      "value": 100
    }
  ],
  "cursor": "next_page_cursor"
}
```

**Per-record fields**:
- `ticker` (string) — market symbol
- `event_ticker` (string)
- `market_result` (string enum: `"yes"`, `"no"`, `"scalar"`, `"void"`)
- `yes_count_fp` (string, FixedPointCount) — YES contracts held by account
- `yes_total_cost_dollars` (string, FixedPointDollars) — YES cost basis
- `no_count_fp`, `no_total_cost_dollars` — NO side analogs
- `revenue` (integer, cents) — total account payout
- `settled_time` (string, **RFC3339**, NOT Unix epoch) — e.g., `"2024-01-15T12:00:00Z"`
- `fee_cost` (string, FixedPointDollars)
- `value` (integer, cents, **nullable**) — per-contract settlement payout

**Brief adjustment**: the brief's pseudocode reads `s.get("settlement_value", "0")` — wrong field name. Correct field is `"value"` (integer cents) for per-contract payout, or compute settle_val from `market_result` (`"yes"` → 100, `"no"` → 0, `"void"` → 50, `"scalar"` → from `value`).

**Format mismatch**: WS `settled_ts` is Unix epoch seconds; REST `settled_time` is RFC3339 string. The unified `process_settlement(..., settled_ts=...)` parameter takes a numeric ts. Caller from REST must parse:
```python
import datetime
settled_ts = datetime.datetime.fromisoformat(s["settled_time"].replace("Z", "+00:00")).timestamp()
```

### 2c. `min_ts` semantics

> "Filter items **after** this Unix timestamp"

Exclusive (`> min_ts`). The brief's 60s overlap window (`_last_settlement_min_ts = time.time() - 60`) covers the boundary safely.

### 2d. Pagination

- `cursor` field name: literally `"cursor"`
- Default `limit`: 100
- Max `limit`: 1000

For the bug-4 catch-up poll, default 100 is sufficient (settlements per 5-min window are well under that for tennis-only).

### 2e. `min_ts` parameter format

Unix epoch seconds (integer). Bot already passes `int(min_ts)`. No change.

---

## 3. Companion REST endpoint: `GET /trade-api/v2/markets/{ticker}`

Public market data — NOT account-scoped, so safe to call in paper mode (does not leak real-account state into paper accounting).

After determination, returns:
- `status: "finalized"`
- `settlement_value` and/or `settlement_value_dollars`
- (other market fields)

**Use case**: when WS `settled` event arrives, hit this endpoint to get the settlement value (since the WS settled event doesn't carry it). One REST call per settlement event.

URL: https://docs.kalshi.com/api-reference/market/get-market

---

## 4. Brief design adjustments (for v4)

### 4.1 WS handler must do an extra hop to get the settle_value

The brief's §6.2 currently reads:
```python
elif typ == "market_lifecycle":  # exact type-string verified at impl time
    sub = msg.get("msg", {})
    lifecycle_event = sub.get("event", "")
    tk = sub.get("market_ticker", "")
    if lifecycle_event == "settled" and tk:
        self.process_settlement(
            ticker=tk,
            settle_value_dollars=sub.get("settlement_value", "0"),  # <-- field doesn't exist
            settled_ts=sub.get("settled_ts", time.time()),
            source="ws_lifecycle",
        )
```

Three fixes:
1. Envelope `type` is `"market_lifecycle_v2"` (with the `_v2` suffix), not `"market_lifecycle"`.
2. Inner field is `event_type`, not `event`.
3. The settled event has no settlement value — must fetch it.

Recommended v4 shape:

```python
elif typ == "market_lifecycle_v2":
    sub = msg.get("msg", {})
    if sub.get("event_type") == "settled":
        tk = sub.get("market_ticker", "")
        settled_ts = sub.get("settled_ts", time.time())
        if tk:
            asyncio.create_task(
                self._handle_ws_settlement(tk, settled_ts)
            )

async def _handle_ws_settlement(self, ticker, settled_ts):
    """Fetch settlement value via /markets/{ticker} and dispatch to
    process_settlement. Decoupled into its own coroutine so the WS reader
    loop is not blocked by the REST call."""
    path = "/trade-api/v2/markets/%s" % ticker
    data = await api_get(self.session, self.ak, self.pk, path, self.rl)
    market = (data or {}).get("market", data) or {}
    if market.get("status") != "finalized":
        # Determination not yet complete (rare race); retry later via REST poll
        self._log("ws_settled_pre_finalized", {"market_status": market.get("status")}, ticker=ticker)
        return
    settle_value_dollars = market.get("settlement_value_dollars",
                                       market.get("settlement_value", "0"))
    self.process_settlement(ticker, settle_value_dollars, settled_ts, source="ws_lifecycle")
```

Note: `api_get` dispatches via the paper-mode wrapper. For a `/markets/{ticker}` path, PaperApi.handle_get falls through to `_real_api_get` (per spec §5.1) — which is what we want, since this is public market data, not account state. Verified: paper-mode code path correctly passes through to real Kalshi.

### 4.2 REST poll record field names

Brief's §6.3 reads `s.get("settlement_value", "0")` and `s.get("settled_time", time.time())` — the second is correct (`settled_time`) but format is RFC3339, not numeric. The first should be derived from `market_result`:

```python
async def poll_settlements_rest(self):
    if _PAPER_API is not None:
        return
    min_ts = getattr(self, "_last_settlement_min_ts", 0) or (time.time() - 86400)
    path = "/trade-api/v2/portfolio/settlements?min_ts=%d&limit=100" % int(min_ts)
    data = await api_get(self.session, self.ak, self.pk, path, self.rl)
    for s in (data or {}).get("settlements", []):
        # market_result -> settle value mapping
        result = s.get("market_result", "")
        if result == "yes":
            settle_val_dollars = 1.0
        elif result == "no":
            settle_val_dollars = 0.0
        elif result == "scalar":
            settle_val_dollars = (s.get("value", 0) or 0) / 100.0
        elif result == "void":
            settle_val_dollars = 0.5
        else:
            self._log("rest_settlement_unknown_result", {"result": result, "ticker": s.get("ticker")})
            continue
        # RFC3339 -> epoch
        settled_time_str = s.get("settled_time", "")
        try:
            settled_ts = datetime.fromisoformat(settled_time_str.replace("Z", "+00:00")).timestamp()
        except Exception:
            settled_ts = time.time()
        self.process_settlement(
            ticker=s.get("ticker", ""),
            settle_value_dollars=settle_val_dollars,
            settled_ts=settled_ts,
            source="rest_poll",
        )
    self._last_settlement_min_ts = time.time() - 60
```

### 4.3 Optional v2 enhancement: cache `determination` events to avoid REST hop

Subscribing to `market_lifecycle_v2` already gets us `determination` events (which carry `market_result`). We could cache them in a `self._pending_determinations: Dict[ticker, market_result]` and consume on `settled`:

```python
elif sub.get("event_type") == "determination":
    self._pending_determinations[sub["market_ticker"]] = sub.get("market_result")
elif sub.get("event_type") == "settled":
    tk = sub["market_ticker"]
    result = self._pending_determinations.pop(tk, None)
    if result in ("yes", "no", "void", "scalar"):
        # use cached result, no REST call needed
        ...
    else:
        # fallback: REST hop to /markets/{ticker}
        ...
```

**Defer to a later iteration.** Adds state tracking + cleanup complexity. v1 with REST hop is simpler and the latency is acceptable (one GET per settlement = ~100-200ms overhead, fires <1x/min steady-state).

---

## 5. Sandbox test deferred — rationale

Step 3 of the probe asked for a live sandbox capture of one real settlement message. Skipped:

**Risk profile**:
- Capturing a `market_lifecycle_v2` event requires opening a Kalshi WS subscription with the bot's credentials.
- The paper bot is currently running in tmux session `paper` with an active WS subscription using the same credentials.
- Kalshi WS may or may not allow concurrent sessions per credentials; behavior is undocumented. Worst case: parallel subscriber kicks the bot off, ending the §11.2 burn-in.
- The bot's existing WS does NOT subscribe to `market_lifecycle_v2` (only `orderbook_delta` + `trade`), so observing the running bot doesn't help.

**No money at risk** (WS subscribe is read-only), but **operational risk** to the in-flight burn-in is non-zero.

**Compensating controls**:
- Kalshi docs provide a verbatim example of the `settled` event payload (see §1c above) — high confidence the field shape is correct.
- The implementation can be defensive: try multiple field names with fallback (`event_type` first, fall back to `event`; `settled_ts` first, fall back to `settled_time`).
- First post-deploy live position settlement will provide ground truth verification within 1-12 hours of bot restart.
- If field names diverge from docs, the bot logs an unrecognized envelope and continues — no crash, no money loss.

**Recommendation**: proceed to implementation with docs-only verification. First settlement event captured after Bug 4 deploys will validate live; if fields differ, patch is a single Edit and ship a v2.

---

## 6. Pre-implementation checklist (locked)

Before writing code:
- [x] Channel name `"market_lifecycle_v2"` confirmed
- [x] Envelope `type` = `"market_lifecycle_v2"` confirmed
- [x] Settled event field names: `market_ticker`, `event_type`, `settled_ts` (NOT `settlement_time`, NOT `settled_time` for the WS path)
- [x] WS settled event lacks settlement_value → needs REST hop to `/markets/{ticker}`
- [x] REST settlements top-level key `"settlements"` confirmed
- [x] REST settlements per-record: `ticker`, `market_result`, `value`, `settled_time` (RFC3339), `revenue`
- [x] REST `min_ts` exclusive — 60s overlap window in brief safely covers
- [x] Public `/markets/{ticker}` is paper-mode safe (passes through `_real_api_get`)

Open for verification at runtime (first deployed settlement):
- Determination event `event_type` exact string (likely `"determination"`)
- Determination event payload field names (for the optional v2 enhancement)
- `/markets/{ticker}` exact field name: `settlement_value` vs `settlement_value_dollars`

---

## 7. Next step

Update `docs/bug4_brief.md` to v4 incorporating §4.1 and §4.2 adjustments. Then build `/tmp/live_v3_bug4.py`.
