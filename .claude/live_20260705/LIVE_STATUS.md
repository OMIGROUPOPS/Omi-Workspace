# LIVE VALIDATION — rolling status

- cycle 47 @ **2026-07-09 11:25:43 PM ET** | build `4f405c4` | session boot 07-09 23:15 ET | log `live_v3_20260709.jsonl` | 966 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:24 | ITFWMATCH-26JUL10TUPMAK-MAK | ITF_W | ? | 47 | 50 | -3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 26 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 16, 'FLOW_ABOVE': 10} | repriceable now: true 9 / false 17 | **cumulative bid_grade lines: 7276 (repriceable true 917 / false 6359)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK-NAK | 43 | 2m | 2/48-48/24 | 46-48 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10CATDEL-CAT | 15 | 10m | 0 | 15-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATDEL-DEL | 80 | 10m | 0 | 80-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATSNI-CAT | 13 | 10m | 0 | 13-14 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10FABOBR-FAB | 15 | 10m | 0 | 15-19 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MILMIK-MIK | 11 | 10m | 1/13-13/3 | 11-13 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFMATCH-26JUL10MIRTAL-TAL | 59 | 10m | 1/63-63/1 | 59-63 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFMATCH-26JUL10PAPJER-JER | 44 | 10m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-GOL | 19 | 10m | 0 | 19-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DYUSAG-SAG | 78 | 10m | 0 | 80-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FRISOL-SOL | 37 | 10m | 0 | 37-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-NAT | 12 | 10m | 1/14-14/33 | 12-14 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→14 |
| ITFWMATCH-26JUL10NATTOM-TOM | 85 | 10m | 0 | 85-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAVKAR-KAR | 57 | 10m | 0 | 57-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAVKAR-PAV | 41 | 10m | 0 | 41-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAWHRU-PAW | 21 | 10m | 0 | 21-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PLOERC-ERC | 89 | 6m | 2/90-90/22 | 89-90 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| ITFWMATCH-26JUL10PLOERC-PLO | 10 | 10m | 1/11-11/42 | 10-11 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFWMATCH-26JUL10RYSALL-ALL | 23 | 10m | 0 | 23-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SHOKRO-KRO | 51 | 10m | 2/55-55/11 | 51-55 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFWMATCH-26JUL10SHOKRO-SHO | 44 | 10m | 1/48-48/10 | 44-48 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFWMATCH-26JUL10SUPPOP-POP | 45 | 10m | 0 | 45-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUPPOP-SUP | 54 | 10m | 0 | 54-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10TUPMAK-TUP | 50 | 1m | 0 | 52-53 | — | **NO_FLOW** | 50 |  |
| ITFWMATCH-26JUL10YODJAN-JAN | 65 | 10m | 3/67-67/10 | 65-67 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL10YODJAN-YOD | 34 | 10m | 5/35-35/18 | 34-35 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10TUPMAK | 47 | 53 | **100** | 97 | +3 |

## FLOW-STATE — 19 tracked game(s) ({'OPEN': 4, 'WAKING': 15}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK | ITF_M | 7.367 | 2 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 0.333 | 1 | **OPEN** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 0.567 | 1 | **OPEN** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 0.3 | 1 | **OPEN** |
| ITFMATCH-26JUL10CATDEL | ITF_M | 0.067 | 5 | **WAKING** |
| ITFMATCH-26JUL10CATSNI | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10MILMIK | ITF_M | 0.167 | 2 | **WAKING** |
| ITFMATCH-26JUL10MIRTAL | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10PAPJER | ITF_M | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL10FRISOL | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10NATTOM | ITF_W | 0.167 | 2 | **WAKING** |
| ITFWMATCH-26JUL10PAVKAR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 0.067 | 3 | **WAKING** |
| ITFWMATCH-26JUL10RYSALL | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 0.133 | 4 | **WAKING** |
| ITFWMATCH-26JUL10SUPPOP | ITF_W | 0.0 | 3 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
