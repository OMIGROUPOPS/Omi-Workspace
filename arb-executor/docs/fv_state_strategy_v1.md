# FV State Strategy v1 — Spec

## Data Flow

```
Entry fill detected (check_fills or reconcile)
  │
  ├─ Record on Position:
  │   kalshi_fill_price        = fill price (cents)
  │   kalshi_last_traded       = book.last_trade_price at fill time
  │   consensus_fv             = lookup_edge(event_ticker) from tennis.db
  │                              (None if no Odds API coverage)
  │   fv_delta                 = kalshi_fill_price - consensus_fv
  │   fv_state                 = classify(fv_delta)
  │
  └─ State classification:
      fv_delta <= -8c  →  DISCOUNT   (filled below consensus)
      -5c < fv_delta < +5c  →  FAIR  (consensus-aligned)
      fv_delta >= +8c  →  PREMIUM    (filled above consensus)
      consensus_fv is None  →  UNKNOWN (no cross-book data)
```

## State Exit Logic

### DISCOUNT state (filled 8c+ below consensus FV)

Edge: near-deterministic convergence toward consensus during pregame.

```
Primary exit: CONVERGENCE SCALP
  Monitor kalshi_last_traded every tick
  When |kalshi_last_traded - consensus_fv| <= 3c:
    Post taker sell at current bid
    Log: "convergence_exit", profit = bid - fill_price
  
  Timeout: if convergence not reached by match_start - 30min:
    Fall through to secondary exit

Secondary exit: CELL EXIT TARGET (normal V4 behavior)
  Keep resting sell at cell exit target
  If bid reaches exit target during live match → fill
  This is bonus profit on top of convergence edge

Settlement: acceptable for DISCOUNT
  If match resolves before either exit fires,
  accept settlement outcome (risk managed by discount entry)
```

### FAIR state (within 5c of consensus)

Standard V4 cell scalp. No modification to existing behavior.

```
Exit: cell exit target (resting sell posted at fill + exit_cents)
  If bid reaches target → scalp success
  If match settles → tail outcome (managed risk)
```

### PREMIUM state (filled 8c+ above consensus FV)

Risk state. We overpaid relative to what informed books think is fair.

```
Primary exit: EARLY SCRATCH
  Monitor kalshi_last_traded every 5 min
  If kalshi_last_traded moves further from consensus by 3c+ 
    within 30 min of fill:
    Post taker sell at current bid
    Accept small loss to avoid larger settlement loss
    Log: "premium_scratch", loss = bid - fill_price

Secondary exit: CONVERGENCE BACK
  If kalshi_last_traded moves TOWARD consensus:
    Hold to normal cell exit target
    The premium may have been noise, not signal

Hard stop: DO NOT hold PREMIUM positions to settlement
  At match_start - 15min, if position still open:
    Post taker sell at current bid regardless
    Log: "premium_hard_stop"
```

### UNKNOWN state (no cross-book data)

Fallback to existing V4 behavior. No consensus gating.

```
Exit: cell exit target (standard)
Settlement: accepted as normal tail risk
```

## Sizing Rules

### DISCOUNT state — double sizing
```
On DISCOUNT classification:
  Post follow-up maker buy at kalshi_last_traded - 2c
  Qty: entry_size (10ct)
  Total exposure: 20ct on this ticker
  
  Guard: max 2 DISCOUNT doublings concurrently
  (prevents capital concentration in single convergence play)
```

### PREMIUM state — no DCA
```
On PREMIUM classification:
  Cancel any pending DCA order on this ticker
  Do NOT post DCA even if cell says DCA-A
  Reason: adding to a position we're already overpaying for
```

### FAIR / UNKNOWN — standard sizing
No change to existing V4 behavior.

## Capital Exposure Limits

```
Max concurrent DISCOUNT doublings:     2 events (40ct total)
Max single-position PREMIUM exposure:  10ct (no DCA)
Max total UNKNOWN exposure:            existing V4 limits apply
Total portfolio hard limit:            $500 deployed
```

## Fallback Behavior

When tennis_odds.py sidecar is down or Odds API returns no data:
- All positions classified as UNKNOWN
- Existing V4 behavior applies unchanged
- No sizing modifications, no early scratches
- Strategy degrades gracefully to pure cell scalping

## Dependencies

- `tennis_odds.py` running as sidecar, writing to `tennis.db`
- `lookup_edge(event_ticker)` function in tennis_v5.py (already exists)
- Position dataclass extended with: `fv_state`, `consensus_fv`, `fv_delta`
- Separate exit monitoring loop for DISCOUNT convergence and PREMIUM scratch
