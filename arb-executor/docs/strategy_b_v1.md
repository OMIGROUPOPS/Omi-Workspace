# Strategy B v1 — Cross-Book FV Convergence Entry

## Overview

Strategy B is an independent entry strategy that fires when Kalshi
last-traded price is ≥8c below cross-book consensus fair value.
It coexists with Strategy A (cell-based scalping) and can fire on
the same side, same event, simultaneously.

Strategy B exits pregame at convergence. Strategy A exits during
live match at cell target. They are separate revenue streams with
separate positions, separate order management, and separate P&L
tracking.

---

## 1. Entry Trigger

Independent of cells. Runs every routing_tick cycle.

```
For each Kalshi event with consensus FV in edge_scores table:
    kalshi_lt = book.last_trade_price  (from websocket trade channel)
    consensus_fv = edge_scores.pinnacle_p1 or pinnacle_p2  (for this side)
    
    if kalshi_lt == 0:
        skip  # no real trades yet, AMM default, unreliable
    
    delta = consensus_fv - kalshi_lt  (positive = Kalshi is cheap)
    
    if delta >= 8:
        # Kalshi is 8c+ below what 30-46 books think is fair
        # Strategy B entry fires
        
        if spread <= 5:
            # Tight market: post maker at ask - 1c
            entry_price = book.best_ask - 1
        else:
            # Wider market: post maker at kalshi_lt + 1c
            entry_price = kalshi_lt + 1
        
        post_order(ticker, "buy", "yes", entry_price, STRATEGY_B_SIZE)
```

**Key difference from Strategy A**: No cell lookup. No cell gating.
Any Kalshi side with FV data and ≥8c gap is eligible. This captures
opportunities in disabled cells (45-54c coin-flip zone), above
leader_85-89 range, and in any price zone where Strategy A has no
cell config.

---

## 2. Entry Sizing

```
STRATEGY_B_SIZE = 10  # fixed, independent of Strategy A
MAX_CONCURRENT_B = 5  # max 5 Strategy B positions at any time

# If both strategies post on same side:
#   Strategy A: 10ct at cell entry
#   Strategy B: 10ct at FV-gap entry
#   Total exposure on this side: 20ct
#   Each managed independently
```

Capital limit: 5 × 10ct × ~50c avg entry = ~$25 max Strategy B
capital at any time. Well within the $500 portfolio hard limit.

---

## 3. Position Tracking

Strategy B positions MUST be distinguishable from Strategy A.

```python
@dataclass
class Position:
    # ... existing fields ...
    
    # NEW: strategy type flag
    position_type: str = "CELL"  # "CELL" (Strategy A) or "FV" (Strategy B)
    
    # Strategy B specific fields (None for CELL positions)
    consensus_fv: int = 0           # FV at fill time (cents)
    fv_delta_at_fill: int = 0       # consensus_fv - fill_price
    fv_exit_target: int = 0         # consensus_fv - 2c
```

**Separation rules:**
- Strategy B fill does NOT update Strategy A's `Position.entry_qty`
- Strategy B exit does NOT cancel Strategy A's exit sell
- Each strategy's orders have independent `order_id` tracking
- Reconcile identifies Strategy B positions by `position_type == "FV"`

---

## 4. Exit Logic (Strategy B Only)

Strategy B exits PREGAME. Does not hold through live match.

```
On Strategy B fill:
    fv_exit_target = consensus_fv - 2c
    
    # Post resting sell at FV target immediately
    post_order(ticker, "sell", "yes", fv_exit_target, fill_qty)
    
    # Monitor every tick:
    if book.last_trade_price >= consensus_fv - 2:
        # Convergence reached — taker sell at best bid
        cancel resting sell
        post_order(ticker, "sell", "yes", book.best_bid, fill_qty)
        log("strategy_b_convergence_exit")
    
    # Hard stop: match_start - 15 min
    if now > match_start_ts - 900:
        cancel resting sell
        post_order(ticker, "sell", "yes", book.best_bid, fill_qty)
        log("strategy_b_hard_stop")
```

**Strategy B NEVER holds to settlement.** If convergence doesn't
happen pregame, exit at market before match starts. Accept small
loss (typically 2-5c) rather than binary settlement risk.

---

## 5. Strategy A Behavior — Unchanged

Strategy A continues exactly as current V4:
- Posts maker buys at `int(mid)` when cell is active
- Cell lookup uses `last_trade_price` primary, mid fallback (Build 1)
- Exits at `fill_price + cell.exit_cents` during live match
- Rides through to settlement as managed tail risk
- DCA logic per cell config

No changes to Strategy A entry, exit, sizing, or cell assignment.

---

## 6. Combined Behavior on Same Side

Both strategies can post on the same Kalshi ticker simultaneously.

```
Example: Rublev at 24c on Kalshi, consensus FV = 36c

Strategy A: cell ATP_MAIN_underdog_20-24 is active
  → posts maker buy at 24c (int(mid))
  → exit target: 24 + 25 = 49c
  → holds through live match

Strategy B: delta = 36 - 24 = 12c ≥ 8c threshold
  → posts maker buy at 25c (ask - 1)
  → exit target: 36 - 2 = 34c
  → exits pregame when price converges to ~34c

Timeline:
  T+0h:   Both orders posted. Rublev at 24c.
  T+2h:   Both fill as ask crosses down. A at 24c, B at 25c.
  T+6h:   Price converges to 33c. Strategy B exits at 33c. +8c profit.
  T+12h:  Match starts. Strategy A holds.
  T+13h:  Rublev takes lead. Bid hits 49c. Strategy A exits. +25c profit.
  
  Combined: +33c per contract on a single event.
  Strategy A alone: +25c.
  Strategy B alone: +8c.
  Both: +33c (additive, no interaction).
```

Capital returns in waves:
- Strategy B capital returns pregame (~6h hold time)
- Strategy A capital returns during/after match (~12h hold time)
- Strategy B capital can be redeployed to new events before
  Strategy A's capital comes back

---

## 7. Cell Gap Capture

Strategy B explicitly fires where Strategy A cannot:

| Price Zone | Strategy A | Strategy B |
|-----------|-----------|-----------|
| 0-14c (deep underdog) | No cell config | Fires if FV gap ≥ 8c |
| 45-54c (coin-flip) | Disabled cells | Fires if FV gap ≥ 8c |
| 55-59c (disabled leader) | Disabled cells | Fires if FV gap ≥ 8c |
| 90-99c (heavy favorite) | No cell config | Fires if FV gap ≥ 8c |
| Any active cell | Posts at cell entry | ALSO fires if FV gap ≥ 8c |

This is the primary value-add: Strategy B has no blind spots
in the price range. Every Kalshi event with cross-book data is
eligible regardless of cell configuration.

---

## 8. Changes to tennis_odds.py

Current code measures edge against Kalshi BID. Must change to
measure against Kalshi LAST-TRADED.

```python
# CURRENT (line 299-300):
kalshi_home_bid = sides[home_code]["bid"]
kalshi_away_bid = sides[away_code]["bid"]

# CHANGE TO:
kalshi_home_lt = sides[home_code].get("last_trade_price", 0)
kalshi_away_lt = sides[away_code].get("last_trade_price", 0)

# Skip if no real trades (AMM default)
if kalshi_home_lt == 0 or kalshi_away_lt == 0:
    continue

# Edge computation (line 306-307):
# CURRENT:
edge_home = fair_home * 100 - kalshi_home_bid
# CHANGE TO:
edge_home = fair_home * 100 - kalshi_home_lt
```

Also: `get_kalshi_books()` must include `last_trade_price` in the
data it returns. Currently only captures `yes_bid_dollars`. Need
to also capture `last_price_dollars` from the Kalshi market API.

---

## 9. What Strategy B Does NOT Do

- Does NOT modify Strategy A cell logic
- Does NOT replace Strategy A
- Does NOT run on events with no cross-book consensus
  (UNKNOWN state = no Strategy B, Strategy A runs as normal)
- Does NOT hold through live match
- Does NOT use DCA
- Does NOT reference deploy_v4.json cell config
- Does NOT change exit targets on Strategy A positions
- Does NOT share Position objects with Strategy A

---

## 10. Rollout Plan

### Phase 1: Instrumentation (Build 1 companion)

Deploy `tennis_odds.py` change: measure edge against
`last_trade_price` instead of `bid`. Run 24-48h. Collect corrected
edge data across all Main tour events.

### Phase 2: Read-Only Signal (3-5 days)

`live_v3.py` reads `edge_scores` table every routing_tick.
For every event where `delta >= 8c`:
```
log("strategy_b_signal", {
    "event": et, "side": tk,
    "kalshi_lt": lt, "consensus_fv": fv,
    "delta": delta, "would_fire": True,
})
```
No actual orders. Validate: how many signals per day? What's the
pregame convergence rate? Does the signal persist long enough
to fill a maker order?

### Phase 3: Live — Main Tour Only (Madrid Apr 22+)

Enable Strategy B entries for KXATPMATCH and KXWTAMATCH only.
- Sizing: 5ct initially (half of target)
- Max concurrent: 3 positions
- Hard stop at match_start - 30min (extra conservative)
- Forward-test for 7 days

### Phase 4: Scale Up

If Phase 3 forward results confirm:
- Win rate ≥ 80% on convergence exits
- Avg profit ≥ +5c per fill
- Max drawdown on any single position ≤ 15c

Scale to 10ct. Increase max concurrent to 5. Tighten hard stop
to match_start - 15min.

### Phase 5: Challenger Extension

Requires alternative cross-book data source for Challengers:
- Betfair Exchange API (if non-US access available)
- Flashscore scraper (fragile but free)
- Pinnacle direct API (if accessible)

Only extend Strategy B to Challengers when we have reliable
consensus FV data covering ≥60% of Challenger events.

---

## Dependencies

- `tennis_odds.py` running as sidecar, refreshing every 15 min
- `tennis.db` edge_scores table with last-traded-based edge
- `book.last_trade_price` populated from WebSocket trade channel
- Position dataclass extended with `position_type`, `consensus_fv`,
  `fv_delta_at_fill`, `fv_exit_target`
- Separate exit monitoring loop for Strategy B convergence check
- `MAX_CONCURRENT_B` counter in LiveV3 class

## Capital Budget

```
Strategy A: existing V4 capital allocation (unlimited entries,
            ~$50-100 deployed at any time)
Strategy B: max 5 × 10ct × ~50c = ~$25 max deployed
Combined:   ~$75-125 peak deployment
Hard limit: $500 total portfolio value
```
