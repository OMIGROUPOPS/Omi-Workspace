# LIVE VALIDATION — rolling status

- cycle 128 @ **2026-07-07 01:17:37 PM ET** | build `0584a83` | session boot 07-07 13:13 ET | log `live_v3_20260707.jsonl` | 2273 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 10 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 13:13 | ITFWMATCH-26JUL07MIKPAQ-PAQ | ITF_W | ? | 70 | 68 | +2 (adopted_est) | — | pre | pair | 96 | PENDING |
| 13:13 | ITFMATCH-26JUL07RICMAR-RIC | ITF_M | ? | 53 | 50 | +3 (adopted_est) | — | pre | pair | 98 | PENDING |
| 13:13 | ITFMATCH-26JUL07RICMAR-MAR | ITF_M | ? | 45 | 41 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
| 13:13 | ITFWMATCH-26JUL07EVAGOW-GOW | ITF_W | ? | 14 | 10 | +4 (adopted_est) | -8.5 | pre | single |  | EARNED |
| 13:13 | ITFWMATCH-26JUL07GIADIA-GIA | ITF_W | ? | 34 | 30 | +4 (adopted_est) | -60.0 | pre | single |  | EARNED |
| 13:13 | ITFWMATCH-26JUL07MAROLU-OLU | ITF_W | ? | 30 | 26 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 13:13 | ATPCHALLENGERMATCH-26JUL07CLAHER-C | ATP_CHALL | ? | 44 | 41 | +3 (adopted_est) | -18.5 | pre | single |  | EARNED |
| 13:14 | ITFWMATCH-26JUL07SCHZID-SCH | ITF_W | ? | 27 | 23 | +4 (fill_est) | — | pre | single |  | PENDING |
| 13:16 | ITFWMATCH-26JUL07MIKPAQ-MIK | ITF_W | ? | 26 | 22 | +4 (fill_est) | — | pre | pair | 96 | PENDING |
| 13:16 | ITFWMATCH-26JUL07MOROLM-OLM | ITF_W | ? | 54 | 52 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 13 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 10, 'NO_FLOW': 3} | repriceable now: true 1 / false 12 | **cumulative bid_grade lines: 4889 (repriceable true 421 / false 4468)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07HAMWAL-W | 86 | 4m | 27/95-97/4532 | 98-99 | 9 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07MOESAN-S | 26 | 4m | 55/35-49/2034 | 37-38 | 9 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07OSOSOT-S | 77 | 4m | 69/95-99/13236 | 99-99 | 18 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07PACMEL-M | 48 | 4m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07PACMEL-P | 51 | 4m | 0 | 51-52 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07SKAPET-P | 36 | 4m | 7/45-48/470 | 45-46 | 9 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL07AUGDJO-AUG | 36 | 4m | 136/38-43/75566 | 41-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| ITFMATCH-26JUL07LERBRO-BRO | 16 | 4m | 184/50-84/16763 | 83-84 | 34 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07ELJRAB-ELJ | 57 | 4m | 7/78-84/48 | 79-83 | 21 | **FLOW_ABOVE** | 78 |  |
| ITFWMATCH-26JUL07EVAGOW-GOW | 18 | 4m | 32/24-32/700 | 25-31 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07KAYDUN-KAY | 26 | 3m | 0 | 26-62 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07MELROD-MEL | 90 | 3m | 15/95-97/1006 | 94-95 | 5 | **FLOW_ABOVE** | 99 |  |
| WTACHALLENGERMATCH-26JUL07ZAALEP-L | 39 | 4m | 38/72-74/15150 | 72-73 | 33 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## PATTERNS (sub-B) — 4
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07RICMAR {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-07 01:17:37 PM ET"}
- deep_neg_fv: KXITFWMATCH-26JUL07EVAGOW-GOW {"entry_minus_fv_burst": -8.5, "emitted_et": "2026-07-07 01:17:37 PM ET"}
- deep_neg_fv: KXITFWMATCH-26JUL07GIADIA-GIA {"entry_minus_fv_burst": -60.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07CLAHER-CLA {"entry_minus_fv_burst": -18.5}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
