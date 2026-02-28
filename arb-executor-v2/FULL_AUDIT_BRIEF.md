# FULL SYSTEM AUDIT BRIEF — Feb 22, 2026
## For CC: Complete reaudit of all code paths, past issues, and fixes

---

## CRITICAL: This must be institutional-grade. Zero tolerance for errors.

---

## 1. ISSUES DISCOVERED & FIXED (Feb 20-21)

### 1a. BUY_SHORT Price Frame Bug [FIXED in 4890078]
- **Root cause:** PM API `price.value` is ALWAYS YES-frame. BUY_SHORT code sent underdog cost directly instead of converting to YES-frame (`100 - underdog_cost`).
- **Impact:** ~87% PM no-fill rate on BUY_SHORT trades. Only filled by accident when underdog cost was low.
- **Fix:** `pm_price = (100 - max_underdog_cost) / 100.0`
- **AUDIT NEEDED:** Verify this fix against PM US API docs. Test with edge cases (underdog cost near 0, near 99, exactly 50).

### 1b. Unwind Path SELL_SHORT Buffer Direction [FIXED in 4890078]
- **Root cause:** SELL_SHORT (intent=4) grouped with SELL_LONG in "subtract buffer" branch. SELL_SHORT = buy YES to close → needs +buffer.
- **Fix:** Intent 2 gets -buffer, intent 4 gets +buffer.
- **AUDIT NEEDED:** Trace ALL unwind/recovery code paths. Verify every `place_order` call uses correct YES-frame price.

### 1c. Unwind Call Sites Frame Mismatch [FIXED in 4890078]
- **Root cause:** Unwind used `pm_price_cents` (underdog-frame for BUY_SHORT) instead of `pm_fill_price * 100` (YES-frame).
- **Fix:** Lines 1251, 1305, 2033 now use `pm_fill_price * 100`.
- **AUDIT NEEDED:** Verify every unwind/tier2/tier3 call passes YES-frame prices.

### 1d. PM Orderbook Crossed Book Detection [FIXED in bc396d1]
- **Root cause:** PM WS stale data caused bid >= ask (impossible). System traded on phantom spreads (952 SLU-VCU trades).
- **Fix:** Skip if `best_bid >= best_ask`.
- **AUDIT NEEDED:** Verify this check fires correctly. Check if Kalshi side needs same check.

### 1e. Kalshi Orderbook Staleness [FIXED in be2a491]
- **Root cause:** No staleness check on Kalshi data when PM WS triggered spread detection. PM had 2s max age, Kalshi had none.
- **Fix:** Added `k_age_ms > PM_PRICE_MAX_AGE_MS` check.
- **AUDIT NEEDED:** Is 2s the right threshold? Should it be tighter (1s)?

### 1f. Pre-execution Freshness & Drift Check [FIXED in be2a491]
- **Root cause:** 100-500ms between spread detection and order execution. Prices could move.
- **Fix:** Re-reads both price caches before execution, aborts if stale (>2s) or drifted (>2c).
- **AUDIT NEEDED:** Is 2c drift threshold optimal? Should it be spread-proportional?

### 1g. No-fill Cooldown with Exponential Backoff [FIXED in bc396d1]
- **Root cause:** Infinite retry loops on illiquid games (3731 attempts on 2 games).
- **Fix:** 30s base cooldown, max 300s, blacklist after 10 consecutive. Exponential backoff.
- **AUDIT NEEDED:** Verify cooldown resets correctly on success. Check if blacklisted games get un-blacklisted when they should.

### 1h. Config Changes [Manual]
- `spread_min_cents`: 4 → 6 (CLI `--spread-min 6` required, argparse default still 4)
- `expected_slippage_cents`: 0 → 2
- `max_contracts`: CLI default 20, running with `--contracts 5`
- **AUDIT NEEDED:** Fix argparse defaults to match config.py. Evaluate if 6c is optimal or should be higher.

---

## 2. REMAINING KNOWN ISSUES (NOT YET FIXED)

### 2a. Unhedged Position Management
- 6 UNHEDGED positions from Feb 20-21 (ATL, STNH, SFPA, SHSU, LONG, PV).
- Tier 3 fallback failed on several. PV has NO SIGNAL — should not have been held.
- **AUDIT:** Why did tier 3 fail? Is the fallback actually executing? Are directional signals being checked before holding unhedged positions?

### 2b. SUCCESS Trades Losing Money
- WASH: 20 contracts, 5.3c spread, -$0.87 net
- JMU: 20 contracts, 4.1c spread, -$0.99 net
- UNF: 5 contracts, 4.8c spread, -$0.08 net
- **Root cause:** Execution slippage + fees exceed thin spreads. The fee model uses static `kalshi_fee_cents=2` instead of dynamic `_kalshi_fee_cents()` function in profit estimation (line 834).
- **AUDIT:** Replace static fee with dynamic `_kalshi_fee_cents(price)` in profit estimation. Verify actual fees match estimates. The depth walker (line 834) and quick spread check (line 911) both use static fees.

### 2c. PM US API Price Semantics — Full Verification Needed
- PM US docs: https://docs.polymarket.us/api-reference/orders/overview
- `price.value` ALWAYS represents long side's price regardless of intent
- For BUY_SHORT: `price.value = min YES sell price`, NO cost = `1.00 - price.value`
- **AUDIT:** Fetch PM US API docs fresh. Verify our understanding is correct. Test with a $0.01 paper trade if possible.

### 2d. Outcome Index Override Logic
- Line 1134: `actual_pm_outcome_idx = pm_outcome_idx if is_long_team else (1 - pm_outcome_idx)`
- Logged trades show `pm_outcome_index` vs `pm_outcome_index_used` sometimes differ.
- **AUDIT:** Verify this logic for all 4 cases. Wrong outcome index = betting on wrong team = catastrophic.

### 2e. Cache Inversion Consistency
- Long team: cache stores raw YES-frame bid/ask
- Non-long team: cache stores inverted (bid=100-ask, ask=100-bid)
- `pm_invert_price` in TRADE_PARAMS re-inverts for non-long teams
- **AUDIT:** Trace the full price path from WS → cache → spread detection → execution for ALL 4 cases. Document expected values at each step.

### 2f. P&L Calculation Accuracy
- Dashboard P&L shows +$6.31 but account balance dropped ~$10
- Settlement script reads trades.json which was reset
- **AUDIT:** Verify P&L calculations match actual balance changes. Account for settlements, fees, and unsettled positions.

---

## 3. PERFORMANCE REQUIREMENTS

### Speed
- Target: sub-100ms from spread detection to order placement
- Current: WS processing 172 msgs/sec (improved from 88)
- Pre-game mapping eliminates runtime overhead
- **AUDIT:** Measure actual end-to-end latency. Where are the bottlenecks? Can we shave more time?

### Risk
- Max 5 contracts per trade ($5 max risk per position at 100c)
- 6c minimum spread (covers ~4c fees + 2c slippage)
- Freshness checks (2s max staleness, 2c max drift)
- No-fill cooldown prevents spam
- **AUDIT:** Is the risk model adequate? What's the worst-case scenario if Kalshi doesn't fill? What's our max drawdown tolerance?

### Reliability
- Crossed book detection
- Staleness checks on both platforms
- Tier 1/2/3 recovery for failed hedges
- **AUDIT:** Stress test the recovery paths. What happens if PM goes down mid-trade? What if Kalshi WS disconnects? What if both disconnect?

---

## 4. CODE PATHS TO AUDIT (Priority Order)

1. **executor_core.py: execute_arb()** — The main execution path. Every line matters.
2. **executor_core.py: TRADE_PARAMS** — All 4 cases. Verify price fields, intents, inversion flags.
3. **executor_core.py: _unwind_pm_position()** — Recovery path. Price frame correctness.
4. **executor_core.py: depth walk & profit estimation** — Fee calculation accuracy.
5. **arb_executor_ws.py: update_pm_price()** — Cache inversion for long vs non-long teams.
6. **arb_executor_ws.py: check_spread_for_ticker()** — Spread calculation correctness.
7. **arb_executor_ws.py: has_quick_spread()** — Fast path spread check.
8. **arb_executor_v7.py: place_order()** — SDK call, price formatting, response parsing.
9. **arb_executor_v7.py: _parse_pm_response()** — Fill detection, order state handling.
10. **settle_positions.py** — Settlement correctness, P&L accuracy.

---

## 5. REFERENCE: PM US API INTENTS

| Intent | Name | Meaning | price.value represents |
|--------|------|---------|----------------------|
| 1 | BUY_LONG | Buy YES shares | Max YES price willing to pay |
| 2 | SELL_LONG | Sell YES shares | Min YES price willing to accept |
| 3 | BUY_SHORT | Buy NO shares | Min YES price willing to sell at (NO cost = 1 - price) |
| 4 | SELL_SHORT | Sell NO shares | Max YES price willing to buy at (NO proceeds = 1 - price) |

---

## 6. REFERENCE: Current Account State

- PM: $162.84 | Kalshi: $167.41 | Total: $330.25
- Starting (Feb 15): $317.77 | Overall P&L: +$12.48
- Open positions: 1 (LONG, unsettled)
- Running: LIVE, 5 contracts, 6c min spread

---

**Bottom line: The BUY_SHORT price bug was the #1 issue causing most no-fills. It's fixed. But there are at least 5 other issues that need verification. Every code path that touches PM prices needs to be traced end-to-end against the PM US API docs. No assumptions — verify everything.**
