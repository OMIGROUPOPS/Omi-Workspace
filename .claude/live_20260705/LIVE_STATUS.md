# LIVE VALIDATION — rolling status

- cycle 1 @ **2026-07-10 01:14:41 PM ET** | build `0ee7467a` | session boot 07-10 13:13 ET | log `live_v3_20260710.jsonl` | 413 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 13:13 | ITFMATCH-26JUL10FORSVA-FOR | ITF_M | ? | 33 | 29 | +4 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 30 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 24} | repriceable now: true 0 / false 30 | **cumulative bid_grade lines: 7894 (repriceable true 1065 / false 6829)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL10BERBON-B | 45 | 1m | 0 | 45-46 | — | **NO_FLOW** | 43 |  |
| ATPCHALLENGERMATCH-26JUL10BERBON-B | 54 | 1m | 0 | 54-55 | — | **NO_FLOW** | 52 |  |
| ATPCHALLENGERMATCH-26JUL10BROMIC-B | 13 | 1m | 1/16-16/113 | 15-16 | 3 | **FLOW_ABOVE** | 13 | flow above but bound 13c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL10GALMIL-M | 35 | 1m | 0 | 38-39 | — | **NO_FLOW** | 36 |  |
| ATPCHALLENGERMATCH-26JUL10MEJCAS-M | 58 | 1m | 2/63-63/26 | 62-63 | 5 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL10SAIDEL-D | 70 | 1m | 3/82-85/903 | 82-82 | 12 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL10VARPDA-P | 60 | 1m | 2/67-67/11 | 66-67 | 7 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL10ANGBER-BER | 5 | 1m | 0 | 5-88 | — | **NO_FLOW** | 88 |  |
| ITFMATCH-26JUL10ANTKLA-KLA | 38 | 1m | 1/51-51/7 | 49-51 | 13 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10BAXJAD-BAX | 79 | 1m | 0 | 80-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10DRARIC-DRA | 74 | 1m | 0 | 75-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10DRARIC-RIC | 19 | 1m | 0 | 19-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10FORWES-FOR | 54 | 1m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10FORWES-WES | 41 | 1m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10GHASPI-GHA | 73 | 1m | 0 | 98-99 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10JOHHOH-HOH | 16 | 1m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10JOHHOH-JOH | 82 | 1m | 0 | 82-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10JOHZAM-JOH | 38 | 1m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10KRUYOU-KRU | 49 | 1m | 0 | 52-54 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ROLWEI-WEI | 33 | 1m | 1/80-80/3 | 76-80 | 47 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10CHAFAK-CHA | 41 | 1m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10CHAFAK-FAK | 56 | 1m | 0 | 56-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NAHMAL-MAL | 35 | 1m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NGUMIR-MIR | 57 | 1m | 0 | 57-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NGUMIR-NGU | 41 | 1m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10MINBRE-B | 25 | 1m | 0 | 25-27 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10MINBRE-M | 73 | 1m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10STEMAR-M | 73 | 1m | 0 | 76-77 | — | **NO_FLOW** | 74 |  |
| WTACHALLENGERMATCH-26JUL10VOLMAN-M | 21 | 1m | 0 | 21-23 | — | **NO_FLOW** | 20 |  |
| WTACHALLENGERMATCH-26JUL10VOLMAN-V | 77 | 1m | 0 | 77-78 | — | **NO_FLOW** | 75 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 23 tracked game(s) ({'WAKING': 17, 'OPEN': 5, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL10BROMIC | ATP_CHALL | 0.367 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL10VARPDA | ATP_CHALL | 0.3 | 1 | **OPEN** |
| ITFMATCH-26JUL10FORSVA | ITF_M | 1.4 | 1 | **OPEN** |
| ITFMATCH-26JUL10GHASPI | ITF_M | 0.733 | 1 | **OPEN** |
| ITFMATCH-26JUL10KRUYOU | ITF_M | 0.4 | 2 | **OPEN** |
| ITFMATCH-26JUL10ANGBER | ITF_M | 0.0 | 83 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL10BERBON | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL10GALMIL | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL10MEJCAS | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL10SAIDEL | ATP_CHALL | 4.2 | — | **WAKING** |
| ITFMATCH-26JUL10ANTKLA | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL10BAXJAD | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10DRARIC | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10FORWES | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10JOHHOH | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10JOHZAM | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10ROLWEI | ITF_M | 2.6 | 4 | **WAKING** |
| ITFWMATCH-26JUL10CHAFAK | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL10NAHMAL | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL10NGUMIR | ITF_W | 0.033 | 3 | **WAKING** |
| WTACHALLENGERMATCH-26JUL10MINBRE | WTA_CHALL | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL10STEMAR | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL10VOLMAN | WTA_CHALL | 0.133 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
