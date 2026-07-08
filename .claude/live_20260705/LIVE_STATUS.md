# LIVE VALIDATION — rolling status

- cycle 3 @ **2026-07-08 02:44:40 PM ET** | build `dac842c` | session boot 07-08 14:22 ET | log `live_v3_20260708.jsonl` | 8979 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 18 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:22 | ATPCHALLENGERMATCH-26JUL08GEAZIN-Z | ATP_CHALL | ? | 27 | 24 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:22 | WTACHALLENGERMATCH-26JUL07KOBMAN-K | WTA_CHALL | ? | 26 | 23 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:23 | ITFMATCH-26JUL08DELRAP-RAP | ITF_M | ? | 65 | 62 | +3 (fill_est) | — | pre | single |  | PENDING |
| 14:24 | ITFMATCH-26JUL08LEGROB-ROB | ITF_M | ? | 6 | 2 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:25 | ITFMATCH-26JUL08VERHEN-HEN | ITF_M | ? | 18 | 14 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:26 | ITFWMATCH-26JUL08PARSLA-SLA | ITF_W | ? | 16 | 13 | +3 (window_cell) | — | pre | single |  | MIXED |
| 14:26 | ITFMATCH-26JUL08POLROZ-POL | ITF_M | ? | 48 | 44 | +4 (fill_est) | — | pre | single |  | PENDING |
| 14:27 | ITFMATCH-26JUL08BRAMAN-MAN | ITF_M | ? | 65 | 62 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:27 | ITFMATCH-26JUL08FALGUA-GUA | ITF_M | ? | 16 | 12 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:27 | ITFMATCH-26JUL08LEEKAD-KAD | ITF_M | ? | 59 | 56 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:27 | ITFMATCH-26JUL08JUHKLO-JUH | ITF_M | ? | 60 | 57 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:29 | ITFMATCH-26JUL08KLAZHA-ZHA | ITF_M | ? | 9 | 5 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
| 14:32 | ITFMATCH-26JUL08POWYOU-YOU | ITF_M | ? | 60 | 57 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:32 | ITFWMATCH-26JUL08BADMEL-MEL | ITF_W | ? | 9 | 5 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:33 | ITFWMATCH-26JUL08MULKUR-MUL | ITF_W | ? | 20 | 25 | -5 (window_cell) | — | pre | single |  | EARNED |
| 14:39 | ITFMATCH-26JUL08DRASLO-SLO | ITF_M | ? | 6 | 2 | +4 (fill_est) | — | pre | single |  | PENDING |
| 14:39 | ITFMATCH-26JUL08KLAZHA-KLA | ITF_M | ? | 89 | 86 | +3 (adopted_est) | — | pre | pair | 98 | PENDING |
| 14:43 | ITFWMATCH-26JUL08LEEMAL-LEE | ITF_W | ? | 32 | 28 | +4 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 6 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 2, 'NO_FLOW': 4} | repriceable now: true 0 / false 6 | **cumulative bid_grade lines: 5679 (repriceable true 557 / false 5122)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL08BEKPAN-PAN | 72 | 8m | 0 | 77-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 8m | 0 | 44-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08JUHKLO-KLO | 37 | 9m | 1/50-50/0 | 37-40 | 13 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08NAKDEA-DEA | 21 | 22m | 240/46-64/15970 | 46-47 | 25 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08GARBOH-GAR | 14 | 2m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 9m | 0 | 63-66 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08PARSLA | 16 | 84 | **100** | 97 | +3 |
| ITFMATCH-26JUL08JUHKLO | 60 | 40 | **100** | 97 | +3 |
| ITFWMATCH-26JUL08MULKUR | 20 | 84 | **104** | 97 | +7 |

## FLOW-STATE — 22 tracked game(s) ({'WAKING': 12, 'QUIET': 2, 'OPEN': 8}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DRASLO | ITF_M | 1.867 | 1 | **OPEN** |
| ITFMATCH-26JUL08FALGUA | ITF_M | 7.6 | 1 | **OPEN** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.367 | 3 | **OPEN** |
| ITFMATCH-26JUL08NAKDEA | ITF_M | 8.933 | 1 | **OPEN** |
| ITFMATCH-26JUL08POLROZ | ITF_M | 4.433 | 2 | **OPEN** |
| ITFMATCH-26JUL08POWYOU | ITF_M | 0.433 | 1 | **OPEN** |
| ITFWMATCH-26JUL08MULKUR | ITF_W | 6.9 | 1 | **OPEN** |
| ITFWMATCH-26JUL08PARSLA | ITF_W | 5.9 | 2 | **OPEN** |
| ITFMATCH-26JUL08BEKPAN | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.0 | 19 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL08GEAZIN | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ITFMATCH-26JUL08BRAMAN | ITF_M | 0.533 | — | **WAKING** |
| ITFMATCH-26JUL08DELRAP | ITF_M | 4.8 | — | **WAKING** |
| ITFMATCH-26JUL08KLAZHA | ITF_M | 1.4 | 5 | **WAKING** |
| ITFMATCH-26JUL08LEEKAD | ITF_M | 0.367 | 5 | **WAKING** |
| ITFMATCH-26JUL08LEGROB | ITF_M | 0.733 | 11 | **WAKING** |
| ITFMATCH-26JUL08VERHEN | ITF_M | 2.033 | — | **WAKING** |
| ITFWMATCH-26JUL08BADMEL | ITF_W | 0.167 | 5 | **WAKING** |
| ITFWMATCH-26JUL08GARBOH | ITF_W | 0.067 | 4 | **WAKING** |
| ITFWMATCH-26JUL08LEEMAL | ITF_W | 0.033 | 6 | **WAKING** |
| WTACHALLENGERMATCH-26JUL07KOBMAN | WTA_CHALL | 0.1 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.067 | 3 | **WAKING** |

## PATTERNS (sub-B) — 1
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL08KLAZHA {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-08 02:44:40 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
