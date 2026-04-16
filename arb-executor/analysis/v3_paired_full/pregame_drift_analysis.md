# Pregame Drift Analysis

## Step 1 — Market Open Timing

Market open lead time (hours before estimated match start):
- Median: 10.2h
- P25: 7.1h
- P75: 17.0h
- N: 1481

| Category | Median(h) | P25(h) | P75(h) | N |
|---|---|---|---|---|
| ATP_CHALL | 8.5 | 4.7 | 10.7 | 790 |
| ATP_MAIN | 14.4 | 11.0 | 27.8 | 320 |
| WTA_MAIN | 13.4 | 9.7 | 21.2 | 325 |
| WTA_CHALL | 9.4 | 3.9 | 10.8 | 46 |

## Step 2 — Pregame Price Drift

| Category | Side | N | Open_mid | T-60min | T-10min | Start_mid | Avg_drift |
|---|---|---|---|---|---|---|---|
| ATP_CHALL | leader | 377 | 69.1 | 66.3 | 66.3 | 65.8 | -3.3c |
| ATP_CHALL | underdog | 427 | 32.1 | 36.0 | 36.4 | 36.3 | +4.2c |
| ATP_MAIN | leader | 157 | 65.6 | 65.3 | 64.6 | 65.0 | -0.7c |
| ATP_MAIN | underdog | 152 | 33.7 | 34.5 | 34.4 | 34.8 | +1.2c |
| WTA_MAIN | leader | 134 | 70.1 | 68.7 | 67.9 | 66.6 | -3.6c |
| WTA_MAIN | underdog | 141 | 32.0 | 33.3 | 34.6 | 36.0 | +4.0c |
| WTA_CHALL | leader | 11 | 72.1 | 73.4 | 70.0 | 69.8 | -2.3c |
| WTA_CHALL | underdog | 30 | 41.9 | 39.2 | 43.2 | 46.5 | +4.5c |

## Step 3 — Drift Direction vs Fill Success

| Outcome | N | Leader drift (avg) | Underdog drift (avg) |
|---|---|---|---|
| both_filled | 233 | -3.9c | +3.8c |
| leader_only | 62 | -4.8c | +4.6c |
| underdog_only | 85 | -0.7c | +1.4c |
| neither | 25 | +0.2c | +0.1c |

## Step 4 — Drift-Aware Taker Policy

Rules:
- Leader miss + UP drift (firming fav): TAKER
- Leader miss + DOWN drift (softening): SKIP
- Underdog miss + DOWN drift (dying dog): SKIP
- Underdog miss + UP drift (firming dog): TAKER

| Category | Taken | Avg_pnl(c) | Win% | Skipped | Skip_reasons |
|---|---|---|---|---|---|
| ATP_CHALL | 10 | -129.3c | 50% | 91 | no_taker_fill=47, down_drift=44 |
| ATP_MAIN | 8 | +15.0c | 75% | 39 | no_taker_fill=21, down_drift=18 |
| WTA_MAIN | 6 | +42.0c | 83% | 40 | no_taker_fill=21, down_drift=19 |
| WTA_CHALL | 1 | +283.0c | 100% | 2 | down_drift=2 |

### Drift-aware taker by side

| Category | Side | N_taken | Avg_pnl | Win% |
|---|---|---|---|---|
| ATP_CHALL | leader | 4 | -117.2c | 75% |
| ATP_CHALL | underdog | 6 | -137.3c | 33% |
| ATP_MAIN | leader | 6 | +59.0c | 83% |
| ATP_MAIN | underdog | 2 | -117.0c | 50% |
| WTA_MAIN | leader | 4 | +103.2c | 100% |
| WTA_MAIN | underdog | 2 | -80.5c | 50% |
| WTA_CHALL | underdog | 1 | +283.0c | 100% |

## Bot Code Audit — What tennis_v5.py Currently Tracks

1. **Market open timestamp**: YES — `first_bid_ts` (line 593) records when first bid observed
2. **Pregame price drift**: PARTIAL — `first_bid` vs current bid logged in `[EARLY_START]` events, but not systematic
3. **Time-to-match-start**: YES — `scheduled_start_ts` (line 583) from ESPN/TE schedule, used for gate timing

To implement drift-aware taker: need `gate_bid` (already tracked) compared to `current_bid` at taker decision point.
Delta = `current_bid - gate_bid`. If delta > 0 for leaders (firming), allow taker. Already has all needed state.