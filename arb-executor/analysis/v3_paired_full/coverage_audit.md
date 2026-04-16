# Coverage Audit + Fill Rate Diagnostic + Taker Fallback Analysis

## Step 1 — Current Cell Grid

| Category | Side | Cell | Status | Exit | DCA | Offset |
|---|---|---|---|---|---|---|
| ATP_CHALL | leader | 55-59 | active | +21c | 11 | -1 |
| ATP_CHALL | leader | 60-64 | active | +30c | 15 | -1 |
| ATP_CHALL | leader | 65-69 | active | hold99 | 17 | -1 |
| ATP_CHALL | leader | 70-74 | active | hold99 | 11 | +1 |
| ATP_CHALL | leader | 75-79 | active | hold99 | 27 | +0 |
| ATP_CHALL | leader | 80-84 | active | hold99 | 14 | -1 |
| ATP_CHALL | underdog | 10-14 | active | +21c | 5 | -1 |
| ATP_CHALL | underdog | 15-19 | active | +18c | 8 | -1 |
| ATP_CHALL | underdog | 20-24 | active | +27c | 5 | -1 |
| ATP_CHALL | underdog | 25-29 | active | +15c | 16 | -1 |
| ATP_CHALL | underdog | 30-34 | DISABLED | +10c | 30 | +0 |
| ATP_CHALL | underdog | 35-39 | active | +11c | 2 | +0 |
| ATP_CHALL | underdog | 40-44 | active | hold99 | 1 | +2 |
| ATP_MAIN | leader | 55-59 | active | +10c | 1 | +1 |
| ATP_MAIN | leader | 60-64 | active | +23c | 10 | +0 |
| ATP_MAIN | leader | 65-69 | active | +4c | 12 | +2 |
| ATP_MAIN | leader | 70-74 | active | +19c | 14 | -1 |
| ATP_MAIN | leader | 75-79 | active | +12c | 35 | +1 |
| ATP_MAIN | underdog | 15-19 | DISABLED | +20c | 15 | +0 |
| ATP_MAIN | underdog | 20-24 | active | +31c | 12 | -1 |
| ATP_MAIN | underdog | 25-29 | active | +21c | 24 | +1 |
| ATP_MAIN | underdog | 30-34 | active | hold99 | 1 | -1 |
| ATP_MAIN | underdog | 35-39 | active | +24c | 1 | -1 |
| ATP_MAIN | underdog | 40-44 | DISABLED | +30c | 30 | +0 |
| WTA_CHALL | leader | 60-64 | active | +15c | 15 | -1 |
| WTA_CHALL | leader | 85-89 | active | hold99 | 25 | +1 |
| WTA_CHALL | underdog | 35-39 | active | hold99 | 15 | -1 |
| WTA_CHALL | underdog | 40-44 | active | hold99 | 1 | -1 |
| WTA_MAIN | leader | 55-59 | active | +7c | 34 | +0 |
| WTA_MAIN | leader | 60-64 | active | +31c | 15 | +0 |
| WTA_MAIN | leader | 65-69 | active | hold99 | 10 | -1 |
| WTA_MAIN | leader | 70-74 | active | hold99 | 27 | -1 |
| WTA_MAIN | leader | 75-79 | active | hold99 | 2 | +2 |
| WTA_MAIN | leader | 80-84 | active | hold99 | 35 | +0 |
| WTA_MAIN | leader | 85-89 | active | hold99 | 1 | -1 |
| WTA_MAIN | underdog | 15-19 | active | +20c | 5 | +0 |
| WTA_MAIN | underdog | 20-24 | active | hold99 | 14 | -1 |
| WTA_MAIN | underdog | 25-29 | active | +21c | 18 | -1 |
| WTA_MAIN | underdog | 30-34 | active | +34c | 17 | +0 |
| WTA_MAIN | underdog | 35-39 | active | +28c | 2 | +1 |
| WTA_MAIN | underdog | 40-44 | active | +33c | 5 | -1 |

## Step 2 — Coverage Audit

| Category | Both in cell | Leader only | Underdog only | Both out | Total |
|---|---|---|---|---|---|
| ATP_CHALL | 211 | 0 | 0 | 0 | 211 |
| ATP_MAIN | 95 | 0 | 0 | 0 | 95 |
| WTA_MAIN | 94 | 0 | 0 | 0 | 94 |
| WTA_CHALL | 5 | 0 | 0 | 0 | 5 |

### Missing UNDERDOG breakdown (events where leader was in cell)


### Missing LEADER breakdown (events where underdog was in cell)


## Step 3 — Fill Rate Diagnostic

Of events where both sides are in active cells:

| Category | Both filled | Leader only | Underdog only | Neither | Total |
|---|---|---|---|---|---|
| ATP_CHALL | 124 | 35 | 38 | 14 | 211 |
| ATP_MAIN | 53 | 15 | 22 | 5 | 95 |
| WTA_MAIN | 53 | 12 | 24 | 5 | 94 |
| WTA_CHALL | 3 | 0 | 1 | 1 | 5 |

### Per-cell fill failure rates (worst first)

| Cell | Fails | Successes | Fail% |
|---|---|---|---|
| ATP_CHALL_underdog_10-14 | 5 | 1 | 83% |
| WTA_MAIN_leader_70-74 | 9 | 6 | 60% |
| WTA_MAIN_leader_80-84 | 6 | 6 | 50% |
| ATP_MAIN_leader_70-74 | 7 | 8 | 47% |
| ATP_MAIN_leader_55-59 | 9 | 11 | 45% |
| WTA_MAIN_leader_60-64 | 7 | 9 | 44% |
| ATP_CHALL_underdog_15-19 | 17 | 25 | 40% |
| WTA_CHALL_leader_60-64 | 2 | 3 | 40% |
| ATP_CHALL_leader_70-74 | 14 | 27 | 34% |
| WTA_MAIN_leader_85-89 | 1 | 2 | 33% |
| ATP_MAIN_underdog_15-19 | 1 | 2 | 33% |
| WTA_MAIN_underdog_15-19 | 6 | 13 | 32% |
| ATP_CHALL_leader_65-69 | 12 | 27 | 31% |
| ATP_CHALL_leader_75-79 | 10 | 24 | 29% |
| ATP_MAIN_underdog_20-24 | 3 | 8 | 27% |
| ATP_CHALL_underdog_20-24 | 7 | 19 | 27% |
| WTA_MAIN_leader_75-79 | 2 | 6 | 25% |
| ATP_CHALL_leader_55-59 | 11 | 33 | 25% |
| ATP_MAIN_underdog_40-44 | 4 | 13 | 24% |
| ATP_CHALL_underdog_25-29 | 7 | 24 | 23% |
| ATP_MAIN_leader_65-69 | 5 | 18 | 22% |
| WTA_MAIN_underdog_25-29 | 3 | 11 | 21% |
| ATP_MAIN_underdog_25-29 | 3 | 11 | 21% |
| WTA_MAIN_underdog_30-34 | 4 | 16 | 20% |
| ATP_MAIN_leader_75-79 | 2 | 8 | 20% |
| WTA_CHALL_underdog_35-39 | 1 | 4 | 20% |
| ATP_MAIN_underdog_35-39 | 5 | 21 | 19% |
| ATP_MAIN_underdog_30-34 | 4 | 20 | 17% |
| ATP_CHALL_underdog_35-39 | 10 | 51 | 16% |
| ATP_MAIN_leader_60-64 | 4 | 23 | 15% |
| WTA_MAIN_leader_65-69 | 2 | 12 | 14% |
| WTA_MAIN_underdog_40-44 | 3 | 21 | 12% |
| ATP_CHALL_leader_60-64 | 4 | 31 | 11% |
| WTA_MAIN_underdog_35-39 | 1 | 10 | 9% |
| ATP_CHALL_underdog_30-34 | 3 | 30 | 9% |
| WTA_MAIN_leader_55-59 | 2 | 24 | 8% |
| ATP_CHALL_leader_80-84 | 1 | 17 | 6% |

## Step 4 — Recoverability Analysis

### a) Re-enabling disabled cells

Total events recoverable by re-enabling disabled cells: **0**

### b-e) Grid expansion estimates

| Option | Events gained (est) | Tradeoff |
|---|---|---|
| Add coinflip cells 45-54c | 0 | Near-random, ~0% edge |
| Widen underdog floor 10c→5c | 0 | Extreme longshots, high loss rate |
| Widen leader ceiling 89c→94c | 0 | Near-locks, tiny profit per trade |
| Taker fallback on maker-miss | 172 | Spread cost (~1-2c), see Step 5 |

## Step 5 — Taker Fallback Analysis

| Category | Variant | N_recovered | Avg_spread_cost | Avg_match_pnl(c) | Cumul_EV_gain(c) |
|---|---|---|---|---|---|
| ATP_CHALL | A_pure | 24 | 0.3c | -190.3c | -4568c |
| ATP_CHALL | B_pregame | 24 | 0.3c | -190.3c | -4568c |
| ATP_CHALL | C_cell_gated | 6 | 0.3c | -130.5c | -783c |
| ATP_MAIN | A_pure | 11 | 0.5c | -169.7c | -1867c |
| ATP_MAIN | B_pregame | 11 | 0.5c | -169.7c | -1867c |
| ATP_MAIN | C_cell_gated | 6 | 0.2c | -260.2c | -1561c |
| WTA_MAIN | A_pure | 10 | 0.7c | -45.6c | -456c |
| WTA_MAIN | B_pregame | 10 | 0.7c | -45.6c | -456c |
| WTA_MAIN | C_cell_gated | 3 | 0.0c | -110.0c | -330c |
| WTA_CHALL | A_pure | 2 | 0.5c | +388.0c | +776c |
| WTA_CHALL | B_pregame | 2 | 0.5c | +388.0c | +776c |
| WTA_CHALL | C_cell_gated | 1 | 0.0c | +283.0c | +283c |