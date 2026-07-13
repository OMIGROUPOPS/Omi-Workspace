# LIVE VALIDATION — rolling status

- cycle 110 @ **2026-07-13 03:55:47 PM ET** | build `87dddba1` | session boot 07-13 15:32 ET | log `live_v3_20260713.jsonl` | 1166 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 4 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:38:15 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 1958.3 |
| 15:43:02 | **taker_capped** | KXITFWMATCH-26JUL13OLIKAI-KAI | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 15:43:03 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 15:53:02 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_taker_capped.md**

## FILLS — 0 graded (session)
none yet this session

## RESTING BIDS — 12 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 8, 'NO_FLOW': 4} | repriceable now: true 8 / false 4 | **cumulative bid_grade lines: 9474 (repriceable true 1399 / false 8075)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13RODALK-R | 75 | 23m | 9/79-79/241 | 77-79 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→79 |
| ATPCHALLENGERMATCH-26JUL13SANLOP-L | 12 | 18m | 7/13-13/219 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ATPCHALLENGERMATCH-26JUL13SANLOP-S | 87 | 23m | 5/88-88/36 | 87-88 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→88 |
| ATPCHALLENGERMATCH-26JUL13SHIHAR-S | 37 | 23m | 16/41-43/972 | 41-43 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ATPCHALLENGERMATCH-26JUL13VUKBRO-V | 40 | 23m | 25/41-43/5079 | 41-41 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 23m | 1/59-59/16 | 57-59 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 23m | 2/51-51/44 | 50-51 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 23m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 23m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BLISAS-SAS | 55 | 23m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 23m | 1/90-90/8 | 89-90 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| WTAMATCH-26JUL13VALCOS-COS | 16 | 23m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 10 tracked game(s) ({'OPEN': 3, 'WAKING': 7}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13RODALK | ATP_CHALL | 0.333 | 2 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL13SANLOP | ATP_CHALL | 0.5 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL13SHIHAR | ATP_CHALL | 0.533 | 2 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL13VUKBRO | ATP_CHALL | 0.9 | — | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.067 | 2 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
