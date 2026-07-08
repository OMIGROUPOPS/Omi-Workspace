# LIVE VALIDATION — rolling status

- cycle 7 @ **2026-07-08 03:26:14 PM ET** | build `a2763fd` | session boot 07-08 15:20 ET | log `live_v3_20260708.jsonl` | 2100 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 4 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:20 | ITFWMATCH-26JUL08GARBOH-GAR | ITF_W | ? | 6 | 2 | +4 (window_cell) | — | pre | single |  | MIXED |
| 15:22 | ITFWMATCH-26JUL08LAUTOR-LAU | ITF_W | ? | 6 | 2 | +4 (fill_est) | -0.5 | pre | single |  | MIXED |
| 15:22 | ATPCHALLENGERMATCH-26JUL06HOLSCH-S | ATP_CHALL | ? | 50 | 47 | +3 (fill_est) | -0.5 | pre | single |  | MIXED |
| 15:24 | ITFWMATCH-26JUL08PERCCU-PER | ITF_W | ? | 19 | 15 | +4 (fill_est) | -18.0 | 0.8 | single |  | EARNED |

## RESTING BIDS — 12 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 8, 'NO_FLOW': 4} | repriceable now: true 0 / false 12 | **cumulative bid_grade lines: 5698 (repriceable true 557 / false 5141)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 59 | 1m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL08FEALAJ-L | 39 | 1m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL08MANBER-M | 71 | 5m | 22/96-99/14566 | 98-99 | 25 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08BRAMAN-MAN | 57 | 5m | 1/67-67/30 | 63-65 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08LEGROB-ROB | 5 | 5m | 0 | 6-9 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08POLROZ-ROZ | 49 | 5m | 2/80-85/1006 | 79-80 | 31 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08BADMEL-MEL | 8 | 5m | 0 | 8-12 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08FEIBER-FEI | 58 | 5m | 6/84-88/314 | 88-89 | 26 | **FLOW_ABOVE** | 82 | flow above but bound 82c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08MCNGAI-MCN | 36 | 5m | 13/47-50/376 | 49-48 | 11 | **FLOW_ABOVE** | 48 |  |
| ITFWMATCH-26JUL08MILMIS-MIL | 6 | 5m | 2/16-21/75 | 16-20 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08REARAB-REA | 57 | 5m | 18/73-84/716 | 84-83 | 16 | **FLOW_ABOVE** | 82 |  |
| WTACHALLENGERMATCH-26JUL06LEANGO-L | 32 | 5m | 15/40-54/2272 | 53-52 | 8 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08GARBOH | 6 | 97 | **103** | 97 | +6 |

## FLOW-STATE — 15 tracked game(s) ({'WAKING': 10, 'OPEN': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08MANBER | ATP_CHALL | 1.567 | 1 | **OPEN** |
| ITFMATCH-26JUL08POLROZ | ITF_M | 0.767 | 1 | **OPEN** |
| ITFWMATCH-26JUL08FEIBER | ITF_W | 0.7 | 1 | **OPEN** |
| ITFWMATCH-26JUL08GARBOH | ITF_W | 0.567 | 1 | **OPEN** |
| ITFWMATCH-26JUL08LAUTOR | ITF_W | 9.367 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL06HOLSCH | ATP_CHALL | 8.0 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL08BRAMAN | ITF_M | 0.133 | 2 | **WAKING** |
| ITFMATCH-26JUL08LEGROB | ITF_M | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL08BADMEL | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL08MCNGAI | ITF_W | 1.233 | — | **WAKING** |
| ITFWMATCH-26JUL08MILMIS | ITF_W | 0.8 | 4 | **WAKING** |
| ITFWMATCH-26JUL08PERCCU | ITF_W | 14.067 | — | **WAKING** |
| ITFWMATCH-26JUL08REARAB | ITF_W | 1.667 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL06LEANGO | WTA_CHALL | 0.833 | — | **WAKING** |

## PATTERNS (sub-B) — 1
- deep_neg_fv: KXITFWMATCH-26JUL08PERCCU-PER {"entry_minus_fv_burst": -18.0, "emitted_et": "2026-07-08 03:26:14 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
