# LIVE VALIDATION — rolling status

- cycle 4 @ **2026-07-08 02:55:03 PM ET** | build `45b44b1` | session boot 07-08 14:22 ET | log `live_v3_20260708.jsonl` | 12380 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 23 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:22 | ATPCHALLENGERMATCH-26JUL08GEAZIN-Z | ATP_CHALL | ? | 27 | 24 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:22 | WTACHALLENGERMATCH-26JUL07KOBMAN-K | WTA_CHALL | ? | 26 | 23 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:23 | ITFMATCH-26JUL08DELRAP-RAP | ITF_M | ? | 65 | 62 | +3 (fill_est) | — | pre | single |  | PENDING |
| 14:24 | ITFMATCH-26JUL08LEGROB-ROB | ITF_M | ? | 6 | 2 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
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
| 14:48 | ITFWMATCH-26JUL08WEBFAK-WEB | ITF_W | ? | 18 | 14 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:49 | ITFMATCH-26JUL08LEGROB-LEG | ITF_M | ? | 92 | 89 | +3 (adopted_est) | — | pre | pair | 98 | PENDING |
| 14:51 | ATPCHALLENGERMATCH-26JUL08MANBER-B | ATP_CHALL | ? | 26 | 26 | +0 (window_cell) | — | pre | single |  | EARNED |
| 14:52 | ITFWMATCH-26JUL08FEIBER-FEI | ITF_W | ? | 59 | 57 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 14:54 | WTACHALLENGERMATCH-26JUL07SHYKIN-K | WTA_CHALL | ? | 40 | 37 | +3 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 7 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 2, 'NO_FLOW': 5} | repriceable now: true 0 / false 7 | **cumulative bid_grade lines: 5681 (repriceable true 557 / false 5124)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08JOHMAL-J | 39 | 4m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BEKPAN-PAN | 72 | 18m | 0 | 78-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 18m | 0 | 44-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08JUHKLO-KLO | 37 | 19m | 1/50-50/0 | 37-40 | 13 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08NAKDEA-DEA | 21 | 33m | 403/37-80/25373 | 70-75 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08GARBOH-GAR | 15 | 1m | 0 | 15-17 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 19m | 0 | 63-66 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08JUHKLO | 60 | 40 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL08MANBER | 26 | 83 | **109** | 97 | +12 |
| ITFWMATCH-26JUL08PARSLA | 16 | 94 | **110** | 97 | +13 |
| ITFWMATCH-26JUL08MULKUR | 20 | 90 | **110** | 97 | +13 |

## FLOW-STATE — 27 tracked game(s) ({'WAKING': 13, 'OPEN': 14}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08MANBER | ATP_CHALL | 1.2 | 1 | **OPEN** |
| ITFMATCH-26JUL08BRAMAN | ITF_M | 0.467 | 2 | **OPEN** |
| ITFMATCH-26JUL08DRASLO | ITF_M | 5.667 | 1 | **OPEN** |
| ITFMATCH-26JUL08FALGUA | ITF_M | 6.433 | 1 | **OPEN** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.367 | 3 | **OPEN** |
| ITFMATCH-26JUL08KLAZHA | ITF_M | 1.6 | 3 | **OPEN** |
| ITFMATCH-26JUL08LEEKAD | ITF_M | 0.767 | 1 | **OPEN** |
| ITFMATCH-26JUL08POLROZ | ITF_M | 5.167 | 1 | **OPEN** |
| ITFMATCH-26JUL08POWYOU | ITF_M | 1.467 | 1 | **OPEN** |
| ITFMATCH-26JUL08VERHEN | ITF_M | 3.4 | 1 | **OPEN** |
| ITFWMATCH-26JUL08MULKUR | ITF_W | 6.767 | 3 | **OPEN** |
| ITFWMATCH-26JUL08PARSLA | ITF_W | 4.433 | 2 | **OPEN** |
| ITFWMATCH-26JUL08WEBFAK | ITF_W | 0.333 | 2 | **OPEN** |
| WTACHALLENGERMATCH-26JUL07SHYKIN | WTA_CHALL | 3.8 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08GEAZIN | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08JOHMAL | ATP_CHALL | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL08BEKPAN | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL08DELRAP | ITF_M | 8.667 | 5 | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL08LEGROB | ITF_M | 0.567 | 4 | **WAKING** |
| ITFMATCH-26JUL08NAKDEA | ITF_M | 12.867 | 5 | **WAKING** |
| ITFWMATCH-26JUL08BADMEL | ITF_W | 0.2 | 5 | **WAKING** |
| ITFWMATCH-26JUL08FEIBER | ITF_W | 0.133 | 2 | **WAKING** |
| ITFWMATCH-26JUL08GARBOH | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL08LEEMAL | ITF_W | 0.033 | 6 | **WAKING** |
| WTACHALLENGERMATCH-26JUL07KOBMAN | WTA_CHALL | 0.067 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.067 | 3 | **WAKING** |

## PATTERNS (sub-B) — 5
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL08GEAZIN-ZIN {"fill": 27, "age_min": 33, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 02:55:03 PM ET"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07KOBMAN-KOB {"fill": 26, "age_min": 33, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08DELRAP-RAP {"fill": 65, "age_min": 32, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 02:55:03 PM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL08KLAZHA {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL08LEGROB {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-08 02:55:03 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
