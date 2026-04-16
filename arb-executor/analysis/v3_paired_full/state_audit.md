# State Audit

## Verification 1 — Per-Ticker State Variables in tennis_v5.py

### Complete MatchState fields (lines 550-650):

**Bid-side tracking:**
- `gate_bid` (line 560): leader bid at gate open time
- `first_bid` (line 592): first observed bid on leader side
- `first_bid_ts` (line 593): timestamp of first_bid
- `last_bid` (line 565): last seen bid (for change detection)
- `pick_bid` (line 571): bid at PICK_SIDE time
- `entry_price` (line 578): actual fill price

**Ask-side tracking: NONE.**
No `first_ask`, `gate_ask`, `opening_mid`, `opening_spread` anywhere in the codebase. Confirmed by empty grep:
`grep -n 'first_ask\|gate_ask\|opening_ask\|opening_mid\|opening_spread' tennis_v5.py` → zero results.

The bot tracks ONLY bid-side price data. Ask is read transiently for maker placement (`ask - 1` for leaders) but never stored as state.

**Match timing:**
- `earliest_entry_ts` (line 582): gate open time (scheduled_start - 3600s)
- `scheduled_start_ts` (line 583): from ESPN/TE schedule
- `latest_entry_ts` (line 584): gate close (scheduled_start + 3600s)
- `match_started` (line 561): bool, set when bid_change_count >= 8/min
- `match_start_ts` (line 562): timestamp of match start detection

**Match detection:**
- `tick_count_window` (line 563): ticks in current window
- `bid_change_count` (line 566): bid changes in current minute
- MATCH_START_TPM = 8 (line 311): threshold for match start logging

**Entry timing:**
- `ENTRY_BEFORE_START = 3600` (line 318): gate opens **60 min before** scheduled start
- `ENTRY_AFTER_START = 3600` (line 319): gate closes 60 min after scheduled start

### What would need to be added for drift-aware entry:
Already has: `gate_bid` (price at gate open) and `current bid` at each tick.
Delta = `current_bid - gate_bid` gives drift direction. No code changes needed for drift computation — just needs a conditional on the taker path.

Would benefit from: `gate_ask` and `gate_spread` to quantify liquidity at gate vs at entry decision.

## Verification 2 — Tick Regime Change Detection

### Findings:

| Match | Cat | Market_open(h) | Pregame_tpm | Live_tpm | Settle_delta(min) |
|---|---|---|---|---|---|
| DARLAN | ATP_MAIN | 18.3h | 8.1 | 886.5 | 361 |
| NOSCIR | WTA_MAIN | 10.7h | 8.5 | 808.3 | 5 |
| MORTRO | ATP_CHALL | 10.0h | 105.9 | 1900.4 | 4 |
| CREAGA | ATP_CHALL | 4.3h | 621.5 | 1854.1 | 5 |
| RINKHA | ATP_MAIN | 34.8h | 3.0 | 253.4 | 1 |

**Clear regime change exists**: pregame tpm is 3-100, live tpm is 250-1900. A 3-5x jump is consistent and detectable.

**But settle_delta varies wildly**: 0-958 minutes. This means my backward-scan method (finding last low-tick window) doesn't reliably hit match start — it sometimes picks a pregame quiet period.

**Key observation**: markets open **10-36 hours** before match start. The bot's current entry gate (`ENTRY_BEFORE_START = 3600` = 60 min) means it only acts in the final hour. By then, pregame drift has already played out.

### Can tick behavior identify pregame→live without external game state?

**Partially.** The tpm jump from ~10 to ~500+ is unmistakable. But:
1. Some ATP_CHALL matches have high pregame tpm (100+), making the boundary fuzzy
2. The transition isn't instant — there's often a 5-15 min ramp
3. Settle_delta (time from inferred start to settlement) is unreliable because matches have variable length

**Recommendation:** Use tick regime change as a SUPPLEMENT to ESPN/TE schedule, not a replacement. The bot already uses bid_change_count >= 8/min for MATCH_START detection (line 1231) — this is the right approach. External schedule gives the gate timing; tick behavior confirms it.

### ENTRY_BEFORE_START = 3600 (60 minutes)

This means:
- Markets open 10-36h before match
- Bot ignores the first 9-35h of market activity
- Entry gate opens T-60min, closes T+60min
- All pregame drift happens BEFORE the bot's entry window
- The bot enters in a relatively stable pregame period (last hour before start)
