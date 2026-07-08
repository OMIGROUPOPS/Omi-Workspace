# LIVE VALIDATION — rolling status

- cycle 2 @ **2026-07-08 02:34:22 PM ET** | build `7564173` | session boot 07-08 14:22 ET | log `live_v3_20260708.jsonl` | 5156 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 15 graded (session)
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
| 14:29 | ITFMATCH-26JUL08KLAZHA-ZHA | ITF_M | ? | 9 | 5 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:32 | ITFMATCH-26JUL08POWYOU-YOU | ITF_M | ? | 60 | 57 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:32 | ITFWMATCH-26JUL08BADMEL-MEL | ITF_W | ? | 9 | 5 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:33 | ITFWMATCH-26JUL08MULKUR-MUL | ITF_W | ? | 20 | 25 | -5 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 3 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 2, 'FLOW_ABOVE': 1} | repriceable now: true 0 / false 3 | **cumulative bid_grade lines: 5674 (repriceable true 557 / false 5117)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL08DRASLO-SLO | 6 | 12m | 0 | 7-16 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08NAKDEA-DEA | 21 | 12m | 156/50-64/11328 | 54-55 | 29 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08GARBOH-GAR | 13 | 2m | 0 | 13-20 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08MULKUR | 20 | 82 | **102** | 97 | +5 |
| ITFWMATCH-26JUL08PARSLA | 16 | 89 | **105** | 97 | +8 |

## FLOW-STATE — 18 tracked game(s) ({'OPEN': 9, 'QUIET': 1, 'WAKING': 8}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08GEAZIN | ATP_CHALL | 2.533 | 1 | **OPEN** |
| ITFMATCH-26JUL08BRAMAN | ITF_M | 0.333 | 2 | **OPEN** |
| ITFMATCH-26JUL08DELRAP | ITF_M | 2.433 | 1 | **OPEN** |
| ITFMATCH-26JUL08FALGUA | ITF_M | 6.433 | 1 | **OPEN** |
| ITFMATCH-26JUL08NAKDEA | ITF_M | 9.067 | 1 | **OPEN** |
| ITFMATCH-26JUL08POLROZ | ITF_M | 2.433 | 2 | **OPEN** |
| ITFMATCH-26JUL08VERHEN | ITF_M | 1.267 | 1 | **OPEN** |
| ITFWMATCH-26JUL08MULKUR | ITF_W | 5.6 | 1 | **OPEN** |
| ITFWMATCH-26JUL08PARSLA | ITF_W | 4.133 | 1 | **OPEN** |
| ITFMATCH-26JUL08DRASLO | ITF_M | 0.0 | 9 | **QUIET** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.033 | 16 | **WAKING** |
| ITFMATCH-26JUL08KLAZHA | ITF_M | 1.267 | 5 | **WAKING** |
| ITFMATCH-26JUL08LEEKAD | ITF_M | 0.167 | 2 | **WAKING** |
| ITFMATCH-26JUL08LEGROB | ITF_M | 0.733 | 10 | **WAKING** |
| ITFMATCH-26JUL08POWYOU | ITF_M | 0.1 | 4 | **WAKING** |
| ITFWMATCH-26JUL08BADMEL | ITF_W | 0.2 | 5 | **WAKING** |
| ITFWMATCH-26JUL08GARBOH | ITF_W | 0.067 | 7 | **WAKING** |
| WTACHALLENGERMATCH-26JUL07KOBMAN | WTA_CHALL | 0.2 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
