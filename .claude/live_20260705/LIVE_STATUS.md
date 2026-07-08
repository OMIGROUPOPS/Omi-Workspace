# LIVE VALIDATION — rolling status

- cycle 8 @ **2026-07-08 03:36:32 PM ET** | build `341ee35` | session boot 07-08 15:20 ET | log `live_v3_20260708.jsonl` | 5490 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 8 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:20 | ITFWMATCH-26JUL08GARBOH-GAR | ITF_W | ? | 6 | 2 | +4 (window_cell) | — | pre | single |  | MIXED |
| 15:22 | ITFWMATCH-26JUL08LAUTOR-LAU | ITF_W | ? | 6 | 2 | +4 (fill_est) | -0.5 | pre | single |  | MIXED |
| 15:22 | ATPCHALLENGERMATCH-26JUL06HOLSCH-S | ATP_CHALL | ? | 50 | 47 | +3 (fill_est) | -0.5 | pre | single |  | MIXED |
| 15:24 | ITFWMATCH-26JUL08PERCCU-PER | ITF_W | ? | 19 | 15 | +4 (fill_est) | -18.0 | 0.8 | single |  | EARNED |
| 15:26 | WTACHALLENGERMATCH-26JUL08YAMROG-Y | WTA_CHALL | ? | 57 | 54 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 15:29 | ITFWMATCH-26JUL08MCNGAI-MCN | ITF_W | ? | 35 | 48 | -13 (window_cell) | — | pre | single |  | EARNED |
| 15:34 | ITFWMATCH-26JUL08LEEMAL-MAL | ITF_W | ? | 63 | 61 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 15:34 | ITFMATCH-26JUL08OCOZAM-ZAM | ITF_M | ? | 76 | 73 | +3 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 9 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 8, 'NO_FLOW': 1} | repriceable now: true 3 / false 6 | **cumulative bid_grade lines: 5701 (repriceable true 560 / false 5141)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 59 | 11m | 2/60-60/77 | 59-60 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ATPCHALLENGERMATCH-26JUL08FEALAJ-L | 39 | 11m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BRAMAN-MAN | 57 | 15m | 49/65-79/1534 | 76-77 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08LEGROB-ROB | 5 | 16m | 10/9-10/246 | 6-9 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFMATCH-26JUL08POLROZ-ROZ | 49 | 16m | 112/67-85/6187 | 75-76 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08BADMEL-MEL | 8 | 16m | 4/11-13/47 | 8-12 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFWMATCH-26JUL08FEIBER-FEI | 58 | 16m | 24/84-89/728 | 86-89 | 26 | **FLOW_ABOVE** | 82 | flow above but bound 82c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08MILMIS-MIL | 6 | 15m | 7/15-21/246 | 15-19 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08REARAB-REA | 57 | 15m | 83/73-93/4196 | 89-90 | 16 | **FLOW_ABOVE** | 82 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08MCNGAI | 35 | 58 | **93** | 97 | -4 |
| WTACHALLENGERMATCH-26JUL08YAMROG | 57 | 43 | **100** | 97 | +3 |
| ITFWMATCH-26JUL08GARBOH | 6 | 97 | **103** | 97 | +6 |

## FLOW-STATE — 16 tracked game(s) ({'OPEN': 11, 'WAKING': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06HOLSCH | ATP_CHALL | 20.5 | 1 | **OPEN** |
| ITFMATCH-26JUL08BRAMAN | ITF_M | 1.667 | 1 | **OPEN** |
| ITFMATCH-26JUL08LEGROB | ITF_M | 0.333 | 3 | **OPEN** |
| ITFMATCH-26JUL08OCOZAM | ITF_M | 0.233 | 1 | **OPEN** |
| ITFMATCH-26JUL08POLROZ | ITF_M | 4.133 | 1 | **OPEN** |
| ITFWMATCH-26JUL08FEIBER | ITF_W | 1.0 | 3 | **OPEN** |
| ITFWMATCH-26JUL08GARBOH | ITF_W | 2.033 | 1 | **OPEN** |
| ITFWMATCH-26JUL08LAUTOR | ITF_W | 9.733 | 1 | **OPEN** |
| ITFWMATCH-26JUL08LEEMAL | ITF_W | 0.633 | 1 | **OPEN** |
| ITFWMATCH-26JUL08PERCCU | ITF_W | 29.533 | 3 | **OPEN** |
| ITFWMATCH-26JUL08REARAB | ITF_W | 3.067 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL08BADMEL | ITF_W | 0.133 | 4 | **WAKING** |
| ITFWMATCH-26JUL08MCNGAI | ITF_W | 4.167 | 10 | **WAKING** |
| ITFWMATCH-26JUL08MILMIS | ITF_W | 0.367 | 4 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08YAMROG | WTA_CHALL | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- deep_neg_fv: KXITFWMATCH-26JUL08PERCCU-PER {"entry_minus_fv_burst": -18.0}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
