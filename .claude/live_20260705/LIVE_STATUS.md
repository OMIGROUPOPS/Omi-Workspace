# LIVE VALIDATION — rolling status

- cycle 50 @ **2026-07-11 01:27:42 AM ET** | build `f7b65be0` | session boot 07-11 00:38 ET | log `live_v3_20260711.jsonl` | 2846 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:00 | ITFWMATCH-26JUL11MAKSHO-SHO | ITF_W | ? | 50 | 48 | +2 (fill_est) | — | pre | single |  | PENDING |
| 01:01 | ITFMATCH-26JUL11LAGRIV-LAG | ITF_M | leader | 69 | 67 | +2 (place_cell) | — | pre | single |  | PENDING |
| 01:25 | ITFWMATCH-26JUL11ERCHRU-HRU | ITF_W | ? | 82 | 80 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 26 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 17, 'NO_FLOW': 8, 'FLOW_AT_LEVEL': 1} | repriceable now: true 15 / false 11 | **cumulative bid_grade lines: 7993 (repriceable true 1104 / false 6889)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL11TABJEB-TAB | 90 | 49m | 8/92-93/69 | 92-93 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFMATCH-26JUL11DOUROB-DOU | 88 | 47m | 3/91-91/2 | 88-91 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→91 |
| ITFMATCH-26JUL11DOUROB-ROB | 11 | 21m | 3/12-13/109 | 11-12 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→12 |
| ITFMATCH-26JUL11DURBAR-BAR | 39 | 36m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11LAGRIV-RIV | 28 | 26m | 1/33-33/2 | 30-33 | 5 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11SHIROB-ROB | 68 | 47m | 2/69-70/21 | 68-69 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFMATCH-26JUL11SHIROB-SHI | 31 | 45m | 1/32-32/0 | 31-33 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→32 |
| ITFMATCH-26JUL11SNIMAZ-MAZ | 23 | 27m | 0 | 23-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11TALPAP-TAL | 44 | 27m | 1/45-45/5 | 44-45 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL11TYAMON-MON | 67 | 49m | 12/79-83/100 | 78-79 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL11DENSTR-DEN | 51 | 27m | 0 | 51-53 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11DENSTR-STR | 49 | 45m | 1/50-50/1 | 49-50 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL11FONROJ-ROJ | 44 | 47m | 0 | 44-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11HOSCIR-CIR | 33 | 46m | 2/37-37/42 | 33-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 47m | 4/67-67/63 | 64-67 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KARSUP-KAR | 59 | 24m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11KARSUP-SUP | 40 | 33m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11KUBRYS-KUB | 66 | 46m | 3/67-67/36 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KUBRYS-RYS | 32 | 49m | 1/34-34/28 | 32-33 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL11PERWIE-PER | 81 | 48m | 1/82-82/0 | 81-82 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL11PERWIE-WIE | 18 | 47m | 3/19-20/101 | 18-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ITFWMATCH-26JUL11SHEYAM-SHE | 46 | 47m | 0 | 46-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11SHEYAM-YAM | 52 | 19m | 1/54-54/3 | 52-54 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 46m | 9/39-39/501 | 38-39 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFWMATCH-26JUL11STATOM-STA | 62 | 47m | 1/62-62/5 | 62-63 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11STATOM-TOM | 36 | 47m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL11LAGRIV | 69 | 33 | **102** | 97 | +5 |

## FLOW-STATE — 19 tracked game(s) ({'WAKING': 16, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL11DOUROB | ITF_M | 0.233 | 1 | **OPEN** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.333 | 1 | **OPEN** |
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 0.267 | 2 | **OPEN** |
| ATPMATCH-26JUL11TABJEB | ATP_MAIN | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL11DURBAR | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11LAGRIV | ITF_M | 0.167 | 1 | **WAKING** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL11SNIMAZ | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL11TALPAP | ITF_M | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11DENSTR | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11FONROJ | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.133 | 3 | **WAKING** |
| ITFWMATCH-26JUL11KARSUP | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 6.567 | — | **WAKING** |
| ITFWMATCH-26JUL11PERWIE | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SHEYAM | ITF_W | 0.167 | 2 | **WAKING** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL11STATOM | ITF_W | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
