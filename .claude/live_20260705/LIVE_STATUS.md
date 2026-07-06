# LIVE VALIDATION — rolling status

- cycle 77 @ **2026-07-05 11:54:00 PM ET** | build `6770a7c` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 933 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:51 | ITFWMATCH-26JUL06PASCOP-PAS | ITF_W | underdog | 12 | 8 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:51 | ITFWMATCH-26JUL06LUCGAD-GAD | ITF_W | underdog | 37 | 33 | +4 (place_cell) | — | pre | single |  | PENDING |
| 23:52 | ITFWMATCH-26JUL06PASCOP-COP | ITF_W | leader | 85 | 83 | +2 (place_cell) | — | pre | pair | 97 | PENDING |

## RESTING BIDS — 20 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 13, 'FLOW_ABOVE': 7} | repriceable now: true 5 / false 15 | **cumulative bid_grade lines: 846 (repriceable true 87 / false 759)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL06BEASCO-SCO | 27 | 1m | 0 | 27-52 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 14 | 1m | 0 | 15-19 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-GEN | 50 | 3m | 1/85-85/1 | 81-85 | 35 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALNGW-NGW | 37 | 1m | 0 | 38-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VULCOU-COU | 15 | 1m | 0 | 16-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VULCOU-VUL | 83 | 3m | 1/87-87/1 | 83-87 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→87 |
| ITFWMATCH-26JUL06BRESAF-BRE | 63 | 3m | 0 | 63-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 36 | 3m | 1/40-40/90 | 36-40 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |
| ITFWMATCH-26JUL06HOSFEH-FEH | 5 | 2m | 0 | 27-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUCGAD-LUC | 60 | 2m | 1/67-67/29 | 62-66 | 7 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06PASCOP-PAS | 9 | 1m | 14/13-14/110 | 10-13 | 4 | **FLOW_ABOVE** | 12 | REPRICEABLE→12 |
| ITFWMATCH-26JUL06SACLAZ-LAZ | 16 | 3m | 1/20-20/4 | 16-20 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFWMATCH-26JUL06SACLAZ-SAC | 77 | 3m | 0 | 77-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SIMCIR-CIR | 16 | 1m | 0 | 16-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SIMCIR-SIM | 83 | 3m | 0 | 83-87 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TODSAG-SAG | 30 | 1m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TODSAG-TOD | 65 | 1m | 1/69-69/0 | 65-69 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL06VAJRAM-RAM | 14 | 1m | 0 | 15-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VAJRAM-VAJ | 77 | 1m | 0 | 78-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ZRNLUE-ZRN | 6 | 1m | 0 | 6-80 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06LUCGAD | 37 | 66 | **103** | 97 | +6 |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
