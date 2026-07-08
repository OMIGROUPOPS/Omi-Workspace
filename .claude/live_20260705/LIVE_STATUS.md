# LIVE VALIDATION — rolling status

- cycle 189 @ **2026-07-08 12:06:30 AM ET** | build `a974d81` | session boot 07-07 23:56 ET | log `live_v3_20260707.jsonl` | 16191 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 5 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:56 | ITFWMATCH-26JUL07LIURUO-RUO | ITF_W | ? | 23 | 19 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 23:56 | ITFMATCH-26JUL07DELKOY-DEL | ITF_M | ? | 87 | 91 | -4 (window_cell) | — | pre | single |  | MIXED |
| 23:57 | ITFMATCH-26JUL07YAMNAK-NAK | ITF_M | ? | 7 | 3 | +4 (fill_est) | — | pre | single |  | PENDING |
| 23:58 | ITFMATCH-26JUL07BORZEN-BOR | ITF_M | ? | 53 | 50 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 00:03 | ITFMATCH-26JUL08HARBEA-BEA | ITF_M | leader | 91 | 86 | +5 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 40 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 34} | repriceable now: true 1 / false 39 | **cumulative bid_grade lines: 5371 (repriceable true 513 / false 4858)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07ICHOCH-OCH | 28 | 10m | 260/39-59/13820 | 56-51 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL07OKIMAT-MAT | 44 | 10m | 72/60-65/4147 | 63-61 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08BALKAS-BAL | 77 | 6m | 0 | 77-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BALKAS-KAS | 17 | 6m | 0 | 17-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BERKUM-BER | 63 | 5m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BERKUM-KUM | 34 | 5m | 0 | 34-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BRAWYG-BRA | 85 | 6m | 0 | 85-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BRAWYG-WYG | 11 | 6m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08CARERE-CAR | 6 | 5m | 0 | 6-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08CARERE-ERE | 88 | 5m | 0 | 88-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08GHAGEN-GEN | 34 | 9m | 0 | 34-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08GHAGEN-GHA | 64 | 3m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08HARBEA-HAR | 6 | 3m | 0 | 8-11 | — | **NO_FLOW** | 6 |  |
| ITFMATCH-26JUL08KUNMEN-MEN | 64 | 9m | 0 | 64-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAZADD-ADD | 82 | 5m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAZADD-LAZ | 14 | 1m | 0 | 14-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PELDUH-PEL | 74 | 9m | 0 | 74-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SERROS-ROS | 51 | 6m | 0 | 51-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SERROS-SER | 43 | 6m | 0 | 43-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-SHI | 61 | 9m | 0 | 61-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-VUJ | 34 | 9m | 0 | 34-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STEGSC-GSC | 85 | 6m | 0 | 85-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STEGSC-STE | 14 | 6m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STERAD-RAD | 34 | 5m | 0 | 34-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STERAD-STE | 64 | 5m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07WEISUN-SUN | 18 | 10m | 233/25-46/16107 | 41-27 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08CIRBRE-BRE | 11 | 9m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HAYGIO-GIO | 31 | 9m | 1/34-34/8 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL08MANKAV-MAN | 94 | 9m | 0 | 94-98 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAPCAP-CAP | 51 | 5m | 0 | 51-54 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAPCAP-PAP | 46 | 5m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PRIVON-PRI | 37 | 5m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PRIVON-VON | 59 | 6m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ROSPAR-ROS | 47 | 9m | 0 | 47-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHOSUV-SHO | 52 | 10m | 1/74-74/26 | 71-74 | 22 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08TRICEN-CEN | 87 | 5m | 0 | 87-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TRICEN-TRI | 6 | 5m | 0 | 6-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TUPPAN-TUP | 83 | 10m | 1/97-97/15 | 97-98 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08VANWON-VAN | 44 | 9m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08VANWON-WON | 53 | 9m | 0 | 53-56 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07DELKOY | 87 | 1 | **88** | 97 | -9 |
| ITFMATCH-26JUL08HARBEA | 91 | 11 | **102** | 97 | +5 |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
