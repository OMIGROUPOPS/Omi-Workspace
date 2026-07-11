# LIVE VALIDATION — rolling status

- cycle 49 @ **2026-07-11 01:17:37 AM ET** | build `3062d639` | session boot 07-11 00:38 ET | log `live_v3_20260711.jsonl` | 2641 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:00 | ITFWMATCH-26JUL11MAKSHO-SHO | ITF_W | ? | 50 | 48 | +2 (fill_est) | — | pre | single |  | PENDING |
| 01:01 | ITFMATCH-26JUL11LAGRIV-LAG | ITF_M | leader | 69 | 67 | +2 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 27 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 16, 'NO_FLOW': 10, 'FLOW_AT_LEVEL': 1} | repriceable now: true 14 / false 13 | **cumulative bid_grade lines: 7991 (repriceable true 1102 / false 6889)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL11TABJEB-TAB | 90 | 39m | 7/93-93/54 | 92-93 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→93 |
| ITFMATCH-26JUL11DOUROB-DOU | 88 | 37m | 2/91-91/1 | 88-91 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→91 |
| ITFMATCH-26JUL11DOUROB-ROB | 11 | 11m | 3/12-13/109 | 11-12 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→12 |
| ITFMATCH-26JUL11DURBAR-BAR | 39 | 26m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11LAGRIV-RIV | 28 | 16m | 1/33-33/2 | 30-33 | 5 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11SHIROB-ROB | 68 | 36m | 1/70-70/13 | 68-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| ITFMATCH-26JUL11SHIROB-SHI | 31 | 34m | 1/32-32/0 | 31-33 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→32 |
| ITFMATCH-26JUL11SNIMAZ-MAZ | 23 | 17m | 0 | 23-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11TALPAP-TAL | 44 | 17m | 1/45-45/5 | 44-45 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL11TYAMON-MON | 67 | 39m | 8/83-83/58 | 81-83 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL11DENSTR-DEN | 51 | 17m | 0 | 51-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11DENSTR-STR | 49 | 34m | 1/50-50/1 | 49-50 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL11ERCHRU-HRU | 82 | 39m | 9/85-85/112 | 83-85 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFWMATCH-26JUL11FONROJ-ROJ | 44 | 36m | 0 | 44-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11HOSCIR-CIR | 33 | 36m | 1/37-37/1 | 33-37 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 36m | 4/67-67/63 | 64-67 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KARSUP-KAR | 59 | 14m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11KARSUP-SUP | 40 | 23m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11KUBRYS-KUB | 66 | 36m | 3/67-67/36 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KUBRYS-RYS | 32 | 39m | 1/34-34/28 | 32-33 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL11PERWIE-PER | 81 | 37m | 0 | 81-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11PERWIE-WIE | 18 | 37m | 0 | 18-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11SHEYAM-SHE | 46 | 36m | 0 | 46-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11SHEYAM-YAM | 52 | 9m | 1/54-54/3 | 52-54 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 36m | 8/39-39/499 | 38-39 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFWMATCH-26JUL11STATOM-STA | 62 | 36m | 1/62-62/5 | 62-63 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11STATOM-TOM | 36 | 36m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL11LAGRIV | 69 | 33 | **102** | 97 | +5 |

## FLOW-STATE — 19 tracked game(s) ({'WAKING': 15, 'OPEN': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL11DOUROB | ITF_M | 0.233 | 1 | **OPEN** |
| ITFMATCH-26JUL11LAGRIV | ITF_M | 0.3 | 1 | **OPEN** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.233 | 2 | **OPEN** |
| ITFWMATCH-26JUL11SHEYAM | ITF_W | 0.2 | 2 | **OPEN** |
| ATPMATCH-26JUL11TABJEB | ATP_MAIN | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL11DURBAR | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL11SNIMAZ | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL11TALPAP | ITF_M | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11DENSTR | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 0.133 | 2 | **WAKING** |
| ITFWMATCH-26JUL11FONROJ | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.167 | 3 | **WAKING** |
| ITFWMATCH-26JUL11KARSUP | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 3.733 | — | **WAKING** |
| ITFWMATCH-26JUL11PERWIE | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11STATOM | ITF_W | 0.033 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
