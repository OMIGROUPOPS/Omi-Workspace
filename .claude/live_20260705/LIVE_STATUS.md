# LIVE VALIDATION — rolling status

- cycle 6 @ **2026-07-10 12:55:35 AM ET** | build `deeb8e0` | session boot 07-10 00:49 ET | log `live_v3_20260710.jsonl` | 1264 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:49 | ITFWMATCH-26JUL10DYUSAG-SAG | ITF_W | ? | 78 | 76 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 00:51 | ITFWMATCH-26JUL10PLOERC-ERC | ITF_W | ? | 89 | 87 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 19 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 4, 'NO_FLOW': 15} | repriceable now: true 2 / false 17 | **cumulative bid_grade lines: 7452 (repriceable true 960 / false 6492)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK-NAK | 43 | 6m | 322/45-58/29093 | 55-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL10ADDCRA-ADD | 32 | 3m | 0 | 32-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10BAYERE-ERE | 90 | 3m | 0 | 90-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATDEL-CAT | 16 | 3m | 0 | 16-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATSNI-CAT | 14 | 5m | 2/16-16/29 | 14-16 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→16 |
| ITFMATCH-26JUL10DOUVIR-VIR | 5 | 6m | 0 | 5-9 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10JONBAR-BAR | 63 | 6m | 0 | 63-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VIVJAN-VIV | 72 | 3m | 0 | 72-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZGISHI-SHI | 60 | 0m | 0 | 60-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZGISHI-ZGI | 37 | 6m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-DEN | 78 | 6m | 0 | 78-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-GOL | 20 | 4m | 0 | 20-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KRUSMI-KRU | 81 | 3m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-TOM | 87 | 3m | 0 | 87-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PLOERC-PLO | 6 | 1m | 1/11-11/8 | 10-11 | 5 | **FLOW_ABOVE** | 8 | flow above but bound 8c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL10SHENON-NON | 26 | 6m | 0 | 28-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10STAPOZ-POZ | 7 | 5m | 1/32-32/10 | 31-45 | 25 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10SUPPOP-SUP | 54 | 3m | 0 | 54-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10VLAMIS-VLA | 18 | 3m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10PLOERC | 89 | 11 | **100** | 97 | +3 |

## FLOW-STATE — 18 tracked game(s) ({'WAKING': 15, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10CATSNI | ITF_M | 0.233 | 2 | **OPEN** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 1.133 | 3 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 1.1 | 1 | **OPEN** |
| ITFMATCH-26JUL09IMANAK | ITF_M | 70.367 | — | **WAKING** |
| ITFMATCH-26JUL10ADDCRA | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10BAYERE | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10CATDEL | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10DOUVIR | ITF_M | 0.133 | 4 | **WAKING** |
| ITFMATCH-26JUL10JONBAR | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10ZGISHI | ITF_M | 0.133 | 2 | **WAKING** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 0.167 | 2 | **WAKING** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL10NATTOM | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL10SHENON | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL10STAPOZ | ITF_W | 0.033 | 14 | **WAKING** |
| ITFWMATCH-26JUL10SUPPOP | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL10VLAMIS | ITF_W | 0.0 | 4 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
