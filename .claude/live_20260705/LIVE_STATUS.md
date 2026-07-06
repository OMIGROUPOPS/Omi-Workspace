# LIVE VALIDATION — rolling status

- cycle 78 @ **2026-07-06 12:04:07 AM ET** | build `5ad8905` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 2165 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 5 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:51 | ITFWMATCH-26JUL06PASCOP-PAS | ITF_W | underdog | 12 | 8 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:51 | ITFWMATCH-26JUL06LUCGAD-GAD | ITF_W | underdog | 37 | 33 | +4 (place_cell) | — | pre | single |  | PENDING |
| 23:52 | ITFWMATCH-26JUL06PASCOP-COP | ITF_W | leader | 85 | 83 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:59 | ITFWMATCH-26JUL06BRESAF-BRE | ITF_W | leader | 63 | 61 | +2 (place_cell) | — | pre | single |  | PENDING |
| 00:04 | ITFWMATCH-26JUL06SIMCIR-CIR | ITF_W | underdog | 16 | 12 | +4 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 23 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 10, 'FLOW_AT_LEVEL': 1, 'NO_FLOW': 12} | repriceable now: true 7 / false 16 | **cumulative bid_grade lines: 866 (repriceable true 92 / false 774)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 6 | 4m | 1/9-9/5 | 6-9 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 24 | 4m | 0 | 24-26 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BEASCO-SCO | 28 | 10m | 0 | 28-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 9m | 1/20-20/4 | 16-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL06GENAZO-GEN | 81 | 8m | 0 | 81-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALNGW-NGW | 39 | 7m | 0 | 39-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALNGW-SAL | 52 | 8m | 1/60-60/12 | 52-60 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06VULCOU-COU | 16 | 9m | 2/20-20/22 | 16-20 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL06VULCOU-VUL | 83 | 13m | 1/87-87/1 | 83-87 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→87 |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 5m | 4/41-42/70 | 42-44 | 7 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06HOSFEH-FEH | 5 | 12m | 0 | 27-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUCGAD-LUC | 60 | 12m | 18/60-69/175 | 61-66 | 0 | **FLOW_AT_LEVEL** | 60 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 7 | 1m | 6/12-13/75 | 10-12 | 5 | **FLOW_ABOVE** | 12 |  |
| ITFWMATCH-26JUL06SACLAZ-LAZ | 19 | 1m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SACLAZ-SAC | 78 | 3m | 3/82-82/32 | 78-82 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL06SIMCIR-SIM | 81 | 0m | 0 | 83-87 | — | **NO_FLOW** | 81 |  |
| ITFWMATCH-26JUL06SIMCIR-SIM | 81 | 0m | 0 | 83-87 | — | **NO_FLOW** | 81 |  |
| ITFWMATCH-26JUL06TODSAG-SAG | 31 | 9m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TODSAG-TOD | 65 | 12m | 3/69-70/34 | 65-69 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL06VAJRAM-RAM | 17 | 5m | 3/18-22/17 | 17-22 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→18 |
| ITFWMATCH-26JUL06VAJRAM-VAJ | 82 | 3m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ZRNLUE-LUE | 60 | 2m | 0 | 60-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ZRNLUE-ZRN | 12 | 1m | 0 | 12-38 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06LUCGAD | 37 | 66 | **103** | 97 | +6 |
| ITFWMATCH-26JUL06SIMCIR | 16 | 87 | **103** | 97 | +6 |
| ITFWMATCH-26JUL06BRESAF | 63 | 44 | **107** | 97 | +10 |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
