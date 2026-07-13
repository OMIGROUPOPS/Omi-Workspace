# LIVE VALIDATION — rolling status

- cycle 106 @ **2026-07-13 03:12:46 PM ET** | build `99c88d0c` | session boot 07-13 15:02 ET | log `live_v3_20260713.jsonl` | 1249 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:08:24 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 1928.4 |

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:03 | ATPCHALLENGERMATCH-26JUL13RODALK-A | ATP_CHALL | ? | 23 | 20 | +3 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 14 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 9, 'FLOW_ABOVE': 5} | repriceable now: true 2 / false 12 | **cumulative bid_grade lines: 9468 (repriceable true 1394 / false 8074)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13RODALK-R | 74 | 9m | 2/79-79/18 | 77-79 | 5 | **FLOW_ABOVE** | 74 | flow above but bound 74c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL13SANLOP-L | 11 | 10m | 0 | 11-13 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13SANLOP-S | 87 | 8m | 0 | 87-88 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13SHIHAR-S | 37 | 10m | 4/43-43/73 | 41-43 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13VUKBRO-V | 40 | 10m | 2/42-42/44 | 41-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 10m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13OLIKAI-KAI | 74 | 10m | 0 | 74-77 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13OLIKAI-OLI | 21 | 4m | 10/26-30/3110 | 21-28 | 5 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 10m | 1/51-51/189 | 50-51 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 10m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 10m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BLISAS-SAS | 55 | 10m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 10m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13VALCOS-COS | 16 | 10m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13RODALK | 23 | 79 | **102** | 97 | +5 |

## FLOW-STATE — 11 tracked game(s) ({'WAKING': 9, 'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13SANLOP | ATP_CHALL | 0.333 | 1 | **OPEN** |
| ITFWMATCH-26JUL13OLIKAI | ITF_W | 0.367 | 3 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL13RODALK | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13SHIHAR | ATP_CHALL | 0.267 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13VUKBRO | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.133 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
