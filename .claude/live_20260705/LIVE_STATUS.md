# LIVE VALIDATION — rolling status

- cycle 109 @ **2026-07-13 03:45:18 PM ET** | build `669e7afc` | session boot 07-13 15:32 ET | log `live_v3_20260713.jsonl` | 922 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 3 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:38:15 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 1958.3 |
| 15:43:02 | **taker_capped** | KXITFWMATCH-26JUL13OLIKAI-KAI | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 15:43:03 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_taker_capped.md**

## FILLS — 0 graded (session)
none yet this session

## RESTING BIDS — 12 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 6} | repriceable now: true 6 / false 6 | **cumulative bid_grade lines: 9473 (repriceable true 1398 / false 8075)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13RODALK-R | 75 | 12m | 6/79-79/177 | 77-79 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→79 |
| ATPCHALLENGERMATCH-26JUL13SANLOP-L | 12 | 8m | 6/13-13/211 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ATPCHALLENGERMATCH-26JUL13SANLOP-S | 87 | 12m | 4/88-88/8 | 87-88 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→88 |
| ATPCHALLENGERMATCH-26JUL13SHIHAR-S | 37 | 12m | 14/41-43/923 | 41-43 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ATPCHALLENGERMATCH-26JUL13VUKBRO-V | 40 | 12m | 13/41-43/1967 | 40-41 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 12m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 12m | 1/51-51/43 | 50-51 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 12m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 12m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BLISAS-SAS | 55 | 12m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 12m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13VALCOS-COS | 16 | 12m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 10 tracked game(s) ({'WAKING': 7, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13SANLOP | ATP_CHALL | 0.533 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL13SHIHAR | ATP_CHALL | 0.567 | 2 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL13VUKBRO | ATP_CHALL | 0.5 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL13RODALK | ATP_CHALL | 0.267 | 2 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.033 | 2 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.2 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
