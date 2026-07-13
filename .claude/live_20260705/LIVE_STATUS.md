# LIVE VALIDATION — rolling status

- cycle 111 @ **2026-07-13 04:06:17 PM ET** | build `a1315822` | session boot 07-13 15:32 ET | log `live_v3_20260713.jsonl` | 2321 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 5 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:38:15 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 1958.3 |
| 15:43:02 | **taker_capped** | KXITFWMATCH-26JUL13OLIKAI-KAI | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 15:43:03 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 15:53:02 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:03:03 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_taker_capped.md**

## FILLS — 0 graded (session)
none yet this session

## RESTING BIDS — 17 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 5, 'NO_FLOW': 12} | repriceable now: true 5 / false 12 | **cumulative bid_grade lines: 9482 (repriceable true 1399 / false 8083)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13SHIHAR-S | 37 | 33m | 23/41-43/1140 | 41-43 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ATPCHALLENGERMATCH-26JUL13VUKBRO-V | 40 | 33m | 29/41-43/5552 | 41-41 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ATPCHALLENGERMATCH-26JUL13WOLFEN-F | 21 | 5m | 0 | 22-23 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 33m | 1/59-59/16 | 57-59 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFMATCH-26JUL13IBRCAM-IBR | 39 | 3m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SCH | 18 | 5m | 0 | 18-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13STEKOT-KOT | 19 | 0m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13STEKOT-STE | 79 | 1m | 0 | 79-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GILNAY-GIL | 60 | 5m | 0 | 60-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GILNAY-NAY | 29 | 1m | 0 | 31-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SATSCH-SCH | 8 | 3m | 0 | 8-50 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 33m | 3/51-51/57 | 50-51 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 33m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 33m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BLISAS-SAS | 55 | 33m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 33m | 2/90-90/13 | 89-90 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| WTAMATCH-26JUL13VALCOS-COS | 16 | 33m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 14 tracked game(s) ({'OPEN': 1, 'WAKING': 9, 'QUIET': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13SHIHAR | ATP_CHALL | 0.6 | 2 | **OPEN** |
| ITFMATCH-26JUL13IBRCAM | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 0.0 | 32 | **QUIET** |
| ITFWMATCH-26JUL13GILNAY | ITF_W | 0.0 | 9 | **QUIET** |
| ITFWMATCH-26JUL13SATSCH | ITF_W | 0.0 | 42 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL13VUKBRO | ATP_CHALL | 0.633 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13WOLFEN | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL13STEKOT | ITF_M | 0.067 | 2 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.1 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
