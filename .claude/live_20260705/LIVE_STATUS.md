# LIVE VALIDATION — rolling status

- cycle 107 @ **2026-07-13 03:23:46 PM ET** | build `16369e5a` | session boot 07-13 15:02 ET | log `live_v3_20260713.jsonl` | 1813 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:08:24 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 1928.4 |
| 15:13:16 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:03 | ATPCHALLENGERMATCH-26JUL13RODALK-A | ATP_CHALL | ? | 23 | 20 | +3 (fill_est) | — | pre | single |  | PENDING |
| 15:18 | ITFWMATCH-26JUL13OLIKAI-KAI | ITF_W | leader | 74 | 72 | +2 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 12 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 6, 'FLOW_ABOVE': 6} | repriceable now: true 4 / false 8 | **cumulative bid_grade lines: 9469 (repriceable true 1395 / false 8074)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13RODALK-R | 74 | 20m | 3/79-79/30 | 77-79 | 5 | **FLOW_ABOVE** | 74 | flow above but bound 74c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL13SANLOP-L | 11 | 21m | 1/13-13/7 | 11-13 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ATPCHALLENGERMATCH-26JUL13SANLOP-S | 87 | 19m | 0 | 87-88 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13SHIHAR-S | 37 | 21m | 5/43-43/95 | 41-43 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13VUKBRO-V | 40 | 21m | 4/42-42/87 | 41-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 21m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 21m | 8/51-51/934 | 50-51 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 21m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 21m | 1/41-41/121 | 40-41 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| WTAMATCH-26JUL13BLISAS-SAS | 55 | 21m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 21m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13VALCOS-COS | 16 | 21m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13RODALK | 23 | 79 | **102** | 97 | +5 |

## FLOW-STATE — 11 tracked game(s) ({'WAKING': 10, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL13OLIKAI | ITF_W | 1.533 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL13RODALK | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13SANLOP | ATP_CHALL | 0.267 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13SHIHAR | ATP_CHALL | 0.167 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13VUKBRO | ATP_CHALL | 0.133 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.267 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
