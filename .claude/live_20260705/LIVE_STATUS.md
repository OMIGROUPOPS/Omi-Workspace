# LIVE VALIDATION — rolling status

- cycle 46 @ **2026-07-13 04:35:25 AM ET** | build `f4c37b8b` | session boot 07-13 03:44 ET | log `live_v3_20260713.jsonl` | 26920 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 24 item(s)
- **half_arm_aging**: KXATPCHALLENGERMATCH-26JUL13BINFUE-FUE {"fill": 62, "age_min": 50, "mode": "STARVATION(no prints since post)"}
- **half_arm_aging**: KXATPMATCH-26JUL13PASKRU-PAS {"fill": 64, "age_min": 50, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- **reality_divergence**: KXITFMATCH-26JUL13BARURA-URA {"kind": "resting_bid", "ref": 14.0, "market_mid": 44.0, "divergence": -30.0}
- **reality_divergence**: KXITFMATCH-26JUL13BATSYC-BAT {"kind": "resting_bid", "ref": 49.0, "market_mid": 75.5, "divergence": -26.5}
- **reality_divergence**: KXITFMATCH-26JUL13HOSSIN-HOS {"kind": "resting_bid", "ref": 51.0, "market_mid": 90.0, "divergence": -39.0}
- **reality_divergence**: KXITFMATCH-26JUL13LEAMEN-MEN {"kind": "resting_bid", "ref": 12.0, "market_mid": 44.5, "divergence": -32.5}
- **reality_divergence**: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 11.0, "market_mid": 48.0, "divergence": -37.0}
- **reality_divergence**: KXITFWMATCH-26JUL13CEUKRE-CEU {"kind": "resting_bid", "ref": 20.0, "market_mid": 53.5, "divergence": -33.5}
- **reality_divergence**: KXITFWMATCH-26JUL13CEUKRE-KRE {"kind": "resting_bid", "ref": 16.0, "market_mid": 46.0, "divergence": -30.0}
- **reality_divergence**: KXITFWMATCH-26JUL13ZHACOR-ZHA {"kind": "resting_bid", "ref": 15.0, "market_mid": 49.0, "divergence": -34.0}
- **reality_divergence**: KXITFMATCH-26JUL13MARVAL-VAL {"kind": "resting_bid", "ref": 35.0, "market_mid": 67.5, "divergence": -32.5}
- **reality_divergence**: KXITFMATCH-26JUL13SEGKAS-KAS {"kind": "resting_bid", "ref": 16.0, "market_mid": 49.5, "divergence": -33.5}
- **reality_divergence**: KXITFMATCH-26JUL13TAZHAR-TAZ {"kind": "resting_bid", "ref": 48.0, "market_mid": 76.5, "divergence": -28.5}
- **reality_divergence**: KXITFMATCH-26JUL13VRTKLA-KLA {"kind": "resting_bid", "ref": 19.0, "market_mid": 47.5, "divergence": -28.5}
- **reality_divergence**: KXITFWMATCH-26JUL13SIMMAR-SIM {"kind": "resting_bid", "ref": 14.0, "market_mid": 48.0, "divergence": -34.0}
- **combined_over_goal_UNVERIFIED_BASIS**: KXITFWMATCH-26JUL13SVIART {"combined": 101, "detail": "pair combined 101c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- **reality_divergence**: KXITFMATCH-26JUL13BARURA-URA {"kind": "resting_bid", "ref": 14.0, "market_mid": 73.0, "divergence": -59.0}
- **reality_divergence**: KXITFMATCH-26JUL13HOSSIN-HOS {"kind": "resting_bid", "ref": 59.0, "market_mid": 90.0, "divergence": -31.0}
- **reality_divergence**: KXITFMATCH-26JUL13LEAMEN-MEN {"kind": "resting_bid", "ref": 13.0, "market_mid": 41.0, "divergence": -28.0}
- **reality_divergence**: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 11.0, "market_mid": 48.0, "divergence": -37.0}
- **reality_divergence**: KXITFWMATCH-26JUL13CEUKRE-KRE {"kind": "resting_bid", "ref": 16.0, "market_mid": 47.5, "divergence": -31.5}
- **reality_divergence**: KXITFWMATCH-26JUL13ZHACOR-ZHA {"kind": "resting_bid", "ref": 15.0, "market_mid": 49.0, "divergence": -34.0}
- **reality_divergence**: KXITFMATCH-26JUL13SEGKAS-KAS {"kind": "resting_bid", "ref": 29.0, "market_mid": 66.0, "divergence": -37.0, "emitted_et": "2026-07-13 04:35:25 AM ET"}
- **reality_divergence**: KXITFWMATCH-26JUL13SIMMAR-SIM {"kind": "resting_bid", "ref": 14.0, "market_mid": 44.0, "divergence": -30.0, "emitted_et": "2026-07-13 04:35:25 AM ET"}
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 8 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 03:45:53 | **self_fill_bell** | KXITFWMATCH-26JUL13IVAKOP-IVA | own buys rose 40c (51->91) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:48:31 | **self_fill_bell** | KXITFMATCH-26JUL13BATSYC-BAT | own buys rose 15c (49->64) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:51:44 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 1251.7 |
| 03:53:36 | **self_fill_bell** | KXITFMATCH-26JUL13URRDRA-URR | own buys rose 19c (49->68) in 1800s -> match-live presumption, entry buys FROZEN |
| 04:21:46 | **self_fill_bell** | KXITFMATCH-26JUL13HOSSIN-HOS | own buys rose 19c (52->71) in 1800s -> match-live presumption, entry buys FROZEN |
| 04:26:50 | **taker_capped** | KXATPMATCH-26JUL13PASKRU-PAS | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 04:31:14 | **self_fill_bell** | KXITFMATCH-26JUL13BRIDUB-DUB | own buys rose 17c (11->28) in 1800s -> match-live presumption, entry buys FROZEN |
| 04:34:15 | **self_fill_bell** | KXITFMATCH-26JUL13ASUKLU-KLU | own buys rose 14c (20->34) in 1800s -> match-live presumption, entry buys FROZEN |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_self_fill_bell.md**

## FILLS — 6 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 03:45 | ATPCHALLENGERMATCH-26JUL13BINFUE-F | ATP_CHALL | ? | 62 | 58 | +4 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 03:45 | ATPMATCH-26JUL13PASKRU-PAS | ATP_MAIN | ? | 64 | 63 | +1 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 04:07 | ITFWMATCH-26JUL13SVIART-SVI | ITF_W | ? | 22 | 18 | +4 (fill_est) | — | pre | pair | 101 | PENDING |
| 04:07 | ITFWMATCH-26JUL13SVIART-ART | ITF_W | ? | 79 | 77 | +2 (adopted_est) | — | pre | pair | 101 | PENDING |
| 04:09 | ITFWMATCH-26JUL13VELKOR-KOR | ITF_W | ? | 65 | 63 | +2 (fill_est) | — | pre | single |  | PENDING |
| 04:10 | ATPCHALLENGERMATCH-26JUL13PRICRI-P | ATP_CHALL | leader | 89 | 86 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 175 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 143, 'FLOW_ABOVE': 29, 'FLOW_AT_LEVEL': 3} | repriceable now: true 15 / false 160 | **cumulative bid_grade lines: 9189 (repriceable true 1331 / false 7858)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL12DEGEE-DE | 41 | 5m | 0 | 41-42 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13BINFUE-B | 34 | 16m | 0 | 36-38 | — | **NO_FLOW** | 35 |  |
| ATPCHALLENGERMATCH-26JUL13DONWES-D | 27 | 4m | 0 | 27-28 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13DONWES-W | 72 | 4m | 0 | 72-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13KRASAL-S | 12 | 50m | 0 | 17-18 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13KUZNIJ-K | 65 | 50m | 0 | 65-68 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13KUZNIJ-N | 32 | 50m | 0 | 32-34 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13YEVCAM-C | 56 | 50m | 3/58-58/417 | 57-58 | 2 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL13YEVCAM-Y | 42 | 46m | 0 | 43-45 | — | **NO_FLOW** | 42 |  |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 50m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12SONSCH-SON | 65 | 50m | 94/69-71/16230 | 68-69 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ATPMATCH-26JUL13COLSKA-SKA | 16 | 34m | 2/17-17/21 | 16-17 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→17 |
| ATPMATCH-26JUL13FAUDAM-FAU | 55 | 37m | 3/56-56/34 | 55-56 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ATPMATCH-26JUL13MARMID-MAR | 37 | 50m | 3/38-38/281 | 37-38 | 1 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ATPMATCH-26JUL13MARMID-MID | 62 | 50m | 4/63-63/60 | 62-63 | 1 | **FLOW_ABOVE** | 63 | REPRICEABLE→63 |
| ATPMATCH-26JUL13PASKRU-KRU | 33 | 49m | 5/36-37/806 | 36-37 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| ATPMATCH-26JUL13SANDAN-DAN | 77 | 50m | 3/78-78/12 | 77-78 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ATPMATCH-26JUL13SANDAN-SAN | 22 | 50m | 0 | 22-23 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL13TABROD-ROD | 40 | 5m | 2/41-41/17 | 40-41 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ATPMATCH-26JUL13TABROD-TAB | 59 | 50m | 42/59-60/8577 | 59-60 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL13ASUKLU-ASU | 49 | 1m | 1/49-49/26 | 49-51 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL13ASUKLU-KLU | 34 | 1m | 2/55-55/27 | 49-55 | 21 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13BARURA-URA | 14 | 50m | 408/52-89/23363 | 85-61 | 38 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13BATSYC-BAT | 64 | 47m | 0 | 64-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BATSYC-SYC | 12 | 50m | 0 | 12-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BENWRI-BEN | 38 | 50m | 0 | 38-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BENWRI-WRI | 55 | 47m | 0 | 55-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERPIA-BER | 83 | 47m | 0 | 83-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERPIA-PIA | 9 | 50m | 0 | 9-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERWAL-BER | 69 | 47m | 0 | 69-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERWAL-WAL | 24 | 47m | 0 | 24-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13CASMOL-CAS | 81 | 45m | 0 | 81-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13CASMOL-MOL | 12 | 49m | 0 | 12-19 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DUTHAI-DUT | 54 | 45m | 0 | 54-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DUTHAI-HAI | 8 | 44m | 0 | 8-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GARCIO-CIO | 21 | 47m | 0 | 21-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GARCIO-GAR | 74 | 23m | 0 | 74-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GUNKUZ-GUN | 35 | 32m | 0 | 35-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GUNKUZ-KUZ | 59 | 44m | 0 | 59-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HASZAG-HAS | 86 | 47m | 0 | 86-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HASZAG-ZAG | 12 | 49m | 0 | 12-13 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HOSSIN-HOS | 71 | 14m | 0 | 88-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HOSSIN-SIN | 7 | 50m | 0 | 7-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13KOZHUS-HUS | 21 | 35m | 0 | 21-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13KOZHUS-KOZ | 69 | 35m | 0 | 69-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13LEAMEN-MEN | 13 | 45m | 0 | 13-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MARVAL-VAL | 49 | 0m | 0 | 52-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MAYAER-AER | 40 | 50m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MAYAER-MAY | 55 | 47m | 0 | 55-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MCHAND-AND | 11 | 50m | 0 | 11-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MEHJEF-JEF | 82 | 9m | 0 | 82-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MEHJEF-MEH | 15 | 50m | 0 | 15-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MOHKEZ-MOH | 90 | 0m | 0 | 91-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13PICLEM-PIC | 64 | 7m | 0 | 64-70 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13PIELUE-LUE | 64 | 47m | 0 | 64-70 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13PIELUE-PIE | 30 | 50m | 0 | 30-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SARANG-SAR | 26 | 49m | 0 | 26-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SEGKAS-KAS | 29 | 0m | 0 | 49-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SEGKAS-SEG | 17 | 21m | 0 | 17-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13TAZHAR-HAR | 12 | 19m | 0 | 12-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13TAZHAR-TAZ | 62 | 1m | 0 | 69-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13TIMCAR-CAR | 9 | 50m | 0 | 9-13 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13TIMCAR-TIM | 87 | 49m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13TROYUN-TRO | 6 | 0m | 0 | 8-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13TROYUN-YUN | 85 | 0m | 0 | 85-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13URRDRA-DRA | 12 | 43m | 0 | 16-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13URRDRA-URR | 68 | 42m | 0 | 79-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13VRTKLA-KLA | 26 | 1m | 0 | 27-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13VULPAO-PAO | 16 | 49m | 0 | 16-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13VULPAO-VUL | 51 | 49m | 0 | 51-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13WITHUE-WIT | 87 | 49m | 0 | 87-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BALHEJ-BAL | 70 | 34m | 0 | 70-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BALHEJ-HEJ | 24 | 34m | 0 | 24-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BOEPOH-BOE | 16 | 47m | 0 | 16-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BOEPOH-POH | 76 | 49m | 0 | 76-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BULEVT-BUL | 75 | 49m | 0 | 75-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BULEVT-EVT | 16 | 50m | 0 | 16-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13CAKVOZ-CAK | 71 | 16m | 0 | 71-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13CAKVOZ-VOZ | 24 | 48m | 0 | 24-28 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13CEUKRE-KRE | 16 | 49m | 0 | 16-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13DELBRO-BRO | 61 | 50m | 1/64-64/9 | 61-64 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ITFWMATCH-26JUL13DELBRO-DEL | 36 | 48m | 0 | 36-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13FEHKRO-FEH | 10 | 50m | 0 | 10-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13FEHKRO-KRO | 87 | 47m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GADSVA-GAD | 25 | 34m | 0 | 25-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GADSVA-SVA | 65 | 34m | 0 | 65-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GIZVLA-GIZ | 14 | 50m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GIZVLA-VLA | 82 | 49m | 0 | 82-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GRORAS-GRO | 42 | 49m | 0 | 42-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GRORAS-RAS | 52 | 49m | 3/58-58/15 | 52-58 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13IBRVER-IBR | 23 | 47m | 0 | 23-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IBRVER-VER | 65 | 7m | 0 | 65-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IVAKOP-IVA | 91 | 50m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KARFER-FER | 24 | 50m | 0 | 24-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KARFER-KAR | 57 | 47m | 0 | 57-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KMISUC-KMI | 22 | 35m | 0 | 22-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUHSEK-KUH | 76 | 21m | 0 | 76-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUHSEK-SEK | 22 | 47m | 0 | 22-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUMCHA-CHA | 20 | 47m | 0 | 20-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUMCHA-KUM | 54 | 49m | 0 | 54-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LABMAN-LAB | 64 | 50m | 0 | 64-71 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LABMAN-MAN | 29 | 15m | 0 | 29-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LAZMAN-LAZ | 27 | 4m | 0 | 27-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LAZREV-LAZ | 53 | 47m | 0 | 53-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LAZREV-REV | 17 | 50m | 0 | 24-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LOLBED-LOL | 91 | 50m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MAL | 79 | 47m | 1/85-85/11 | 79-85 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MOO | 16 | 47m | 0 | 16-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MICSEB-MIC | 21 | 49m | 0 | 21-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MICSEB-SEB | 70 | 49m | 0 | 70-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MITROM-MIT | 28 | 50m | 0 | 29-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MITROM-ROM | 64 | 47m | 0 | 64-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13NAGCHY-NAG | 93 | 34m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PETURB-PET | 57 | 47m | 0 | 57-62 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PETURB-URB | 38 | 24m | 0 | 38-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PULWIR-PUL | 25 | 49m | 0 | 25-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PULWIR-WIR | 63 | 49m | 0 | 63-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RAJHUT-HUT | 18 | 50m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RAJHUT-RAJ | 74 | 47m | 0 | 74-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-NDU | 15 | 50m | 0 | 15-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-SCH | 51 | 47m | 0 | 51-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SIMMAR-SIM | 14 | 35m | 0 | 14-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13STESCH-SCH | 9 | 4m | 0 | 9-18 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13STESCH-STE | 82 | 2m | 0 | 82-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WIEMON-WIE | 94 | 50m | 0 | 94-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZABSEV-SEV | 64 | 26m | 0 | 64-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZABSEV-ZAB | 28 | 50m | 0 | 28-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHACOR-ZHA | 15 | 49m | 0 | 15-83 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13GRABER-B | 20 | 50m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13GRABER-G | 78 | 50m | 2/80-80/12 | 79-80 | 2 | **FLOW_ABOVE** | 77 | flow above but bound 77c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL13KABPER-K | 72 | 50m | 0 | 72-74 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13KABPER-P | 27 | 45m | 0 | 27-28 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13KHOZHA-K | 82 | 50m | 0 | 82-83 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13KHOZHA-Z | 16 | 50m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PANFAL-F | 54 | 50m | 1/56-56/1 | 54-56 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| WTACHALLENGERMATCH-26JUL13PANFAL-P | 44 | 21m | 0 | 44-45 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PAPAND-A | 77 | 35m | 0 | 77-79 | — | **NO_FLOW** | 76 |  |
| WTACHALLENGERMATCH-26JUL13PAPAND-P | 22 | 47m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 20 | flow above but bound 20c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL13PENTHA-P | 76 | 48m | 1/77-77/33 | 76-77 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→77 |
| WTACHALLENGERMATCH-26JUL13PENTHA-T | 23 | 50m | 0 | 23-24 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 84 | 5m | 0 | 84-85 | — | **NO_FLOW** | 82 |  |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 15 | 50m | 6/16-16/152 | 15-16 | 1 | **FLOW_ABOVE** | 13 | flow above but bound 13c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL13RISPOH-P | 54 | 19m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13RISPOH-R | 46 | 48m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13SAINUG-N | 66 | 50m | 2/67-67/30 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| WTACHALLENGERMATCH-26JUL13SAINUG-S | 32 | 50m | 0 | 32-33 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13SHIHUA-H | 65 | 50m | 1/66-66/10 | 65-66 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| WTACHALLENGERMATCH-26JUL13SHIHUA-S | 33 | 50m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13TIKBEN-B | 59 | 34m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13TIKBEN-T | 39 | 14m | 0 | 39-41 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 50m | 0 | 48-49 | — | **NO_FLOW** | 46 |  |
| WTAMATCH-26JUL13AVAFET-AVA | 91 | 50m | 1/92-92/1 | 91-92 | 1 | **FLOW_ABOVE** | 92 | REPRICEABLE→92 |
| WTAMATCH-26JUL13AVAFET-FET | 8 | 50m | 3/9-9/260 | 8-9 | 1 | **FLOW_ABOVE** | 7 | flow above but bound 7c < flow -- chasing breaks goal |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 50m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 50m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13CHAJIM-CHA | 65 | 21m | 0 | 65-66 | — | **NO_FLOW** | 66 |  |
| WTAMATCH-26JUL13CHAJIM-JIM | 34 | 21m | 2/35-35/26 | 34-35 | 1 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| WTAMATCH-26JUL13CRIJEA-CRI | 65 | 48m | 0 | 65-66 | — | **NO_FLOW** | 66 |  |
| WTAMATCH-26JUL13CRIJEA-JEA | 34 | 27m | 0 | 34-35 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KAWWAL-KAW | 31 | 50m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KAWWAL-WAL | 67 | 50m | 0 | 67-69 | — | **NO_FLOW** | 69 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 88 | 50m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13LEPIBR-IBR | 43 | 14m | 0 | 43-44 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13LIUIPE-IPE | 19 | 50m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13LIUIPE-LIU | 80 | 50m | 1/81-81/10 | 80-81 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→81 |
| WTAMATCH-26JUL13MONMAS-MAS | 81 | 50m | 0 | 81-84 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13QUERUS-QUE | 28 | 50m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13QUERUS-RUS | 70 | 19m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13ROMKUL-KUL | 23 | 50m | 1/24-24/15 | 23-24 | 1 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| WTAMATCH-26JUL13ROMKUL-ROM | 76 | 50m | 12/76-77/136 | 76-77 | 0 | **FLOW_AT_LEVEL** | 77 |  |
| WTAMATCH-26JUL13SHEGAL-GAL | 37 | 50m | 1/38-38/5 | 37-38 | 1 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| WTAMATCH-26JUL13SHEGAL-SHE | 61 | 47m | 0 | 61-62 | — | **NO_FLOW** | 62 |  |
| WTAMATCH-26JUL13TIMANN-ANN | 58 | 50m | 1/60-60/0 | 58-60 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| WTAMATCH-26JUL13VALCOS-COS | 16 | 45m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13VALCOS-VAL | 81 | 50m | 1/85-85/1 | 81-85 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13PRICRI | 89 | 9 | **98** | 97 | +1 |
| ATPCHALLENGERMATCH-26JUL13BINFUE | 62 | 38 | **100** | 97 | +3 |
| ATPMATCH-26JUL13PASKRU | 64 | 37 | **101** | 97 | +4 |

## FLOW-STATE — 106 tracked game(s) ({'WAKING': 67, 'OPEN': 3, 'QUIET': 36}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL12SONSCH | ATP_MAIN | 2.267 | 1 | **OPEN** |
| ATPMATCH-26JUL13TABROD | ATP_MAIN | 0.867 | 1 | **OPEN** |
| ITFMATCH-26JUL13ASUKLU | ITF_M | 0.333 | 2 | **OPEN** |
| ITFMATCH-26JUL13BATSYC | ITF_M | 0.0 | 23 | **QUIET** |
| ITFMATCH-26JUL13BENWRI | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13BERPIA | ITF_M | 0.0 | 8 | **QUIET** |
| ITFMATCH-26JUL13BERWAL | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13CASMOL | ITF_M | 0.0 | 7 | **QUIET** |
| ITFMATCH-26JUL13DUTHAI | ITF_M | 0.0 | 38 | **QUIET** |
| ITFMATCH-26JUL13KOZHUS | ITF_M | 0.0 | 9 | **QUIET** |
| ITFMATCH-26JUL13LEAMEN | ITF_M | 0.0 | 52 | **QUIET** |
| ITFMATCH-26JUL13MARVAL | ITF_M | 0.0 | 31 | **QUIET** |
| ITFMATCH-26JUL13MCHAND | ITF_M | 0.0 | 74 | **QUIET** |
| ITFMATCH-26JUL13SARANG | ITF_M | 0.0 | 29 | **QUIET** |
| ITFMATCH-26JUL13SEGKAS | ITF_M | 0.0 | 33 | **QUIET** |
| ITFMATCH-26JUL13TAZHAR | ITF_M | 0.0 | 18 | **QUIET** |
| ITFMATCH-26JUL13TROYUN | ITF_M | 0.0 | 7 | **QUIET** |
| ITFMATCH-26JUL13VRTKLA | ITF_M | 0.0 | 41 | **QUIET** |
| ITFMATCH-26JUL13VULPAO | ITF_M | 0.0 | 32 | **QUIET** |
| ITFWMATCH-26JUL13BOEPOH | ITF_W | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL13BULEVT | ITF_W | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL13CEUKRE | ITF_W | 0.0 | 63 | **QUIET** |
| ITFWMATCH-26JUL13GADSVA | ITF_W | 0.0 | 9 | **QUIET** |
| ITFWMATCH-26JUL13IBRVER | ITF_W | 0.0 | 11 | **QUIET** |
| ITFWMATCH-26JUL13KARFER | ITF_W | 0.0 | 18 | **QUIET** |
| ITFWMATCH-26JUL13KMISUC | ITF_W | 0.0 | 41 | **QUIET** |
| ITFWMATCH-26JUL13KUMCHA | ITF_W | 0.0 | 25 | **QUIET** |
| ITFWMATCH-26JUL13LABMAN | ITF_W | 0.0 | 7 | **QUIET** |
| ITFWMATCH-26JUL13LAZMAN | ITF_W | 0.0 | 25 | **QUIET** |
| ITFWMATCH-26JUL13LAZREV | ITF_W | 0.0 | 22 | **QUIET** |
| ITFWMATCH-26JUL13MICSEB | ITF_W | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL13MITROM | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL13PULWIR | ITF_W | 0.0 | 11 | **QUIET** |
| ITFWMATCH-26JUL13RAJHUT | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL13SCHNDU | ITF_W | 0.0 | 33 | **QUIET** |
| ITFWMATCH-26JUL13SIMMAR | ITF_W | 0.0 | 60 | **QUIET** |
| ITFWMATCH-26JUL13STESCH | ITF_W | 0.0 | 9 | **QUIET** |
| ITFWMATCH-26JUL13ZABSEV | ITF_W | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL13ZHACOR | ITF_W | 0.0 | 68 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL12DEGEE | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13BINFUE | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13DONWES | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13KRASAL | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13KUZNIJ | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13PRICRI | ATP_CHALL | 1.233 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13YEVCAM | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 2 | **WAKING** |
| ATPMATCH-26JUL13COLSKA | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ATPMATCH-26JUL13FAUDAM | ATP_MAIN | 0.033 | 1 | **WAKING** |
| ATPMATCH-26JUL13MARMID | ATP_MAIN | 0.167 | 1 | **WAKING** |
| ATPMATCH-26JUL13PASKRU | ATP_MAIN | 0.133 | 1 | **WAKING** |
| ATPMATCH-26JUL13SANDAN | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL13BARURA | ITF_M | 7.5 | — | **WAKING** |
| ITFMATCH-26JUL13GARCIO | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL13GUNKUZ | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL13HASZAG | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL13HOSSIN | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL13MAYAER | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL13MEHJEF | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL13MOHKEZ | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL13PICLEM | ITF_M | 0.033 | 6 | **WAKING** |
| ITFMATCH-26JUL13PIELUE | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL13TIMCAR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL13URRDRA | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL13WITHUE | ITF_M | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13BALHEJ | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13CAKVOZ | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13DELBRO | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL13FEHKRO | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL13GIZVLA | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13GRORAS | ITF_W | 0.1 | 5 | **WAKING** |
| ITFWMATCH-26JUL13IVAKOP | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13KUHSEK | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL13LOLBED | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13MALMOO | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL13NAGCHY | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL13PETURB | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SVIART | ITF_W | 9.233 | — | **WAKING** |
| ITFWMATCH-26JUL13VELKOR | ITF_W | 5.667 | — | **WAKING** |
| ITFWMATCH-26JUL13WIEMON | ITF_W | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13GRABER | WTA_CHALL | 0.067 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13KABPER | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13KHOZHA | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PANFAL | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PAPAND | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PENTHA | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13RADREN | WTA_CHALL | 0.167 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13RISPOH | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13SAINUG | WTA_CHALL | 0.067 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13SHIHUA | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13TIKBEN | WTA_CHALL | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13AVAFET | WTA_MAIN | 0.1 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13CHAJIM | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13CRIJEA | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KAWWAL | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13LEPIBR | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13LIUIPE | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13MONMAS | WTA_MAIN | 0.0 | 3 | **WAKING** |
| WTAMATCH-26JUL13QUERUS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13ROMKUL | WTA_MAIN | 0.267 | 1 | **WAKING** |
| WTAMATCH-26JUL13SHEGAL | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13TIMANN | WTA_MAIN | 0.033 | 2 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 2 | **WAKING** |

## PATTERNS (sub-B) — 24
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL13BINFUE-FUE {"fill": 62, "age_min": 50, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXATPMATCH-26JUL13PASKRU-PAS {"fill": 64, "age_min": 50, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- reality_divergence: KXITFMATCH-26JUL13BARURA-URA {"kind": "resting_bid", "ref": 14.0, "market_mid": 44.0, "divergence": -30.0}
- reality_divergence: KXITFMATCH-26JUL13BATSYC-BAT {"kind": "resting_bid", "ref": 49.0, "market_mid": 75.5, "divergence": -26.5}
- reality_divergence: KXITFMATCH-26JUL13HOSSIN-HOS {"kind": "resting_bid", "ref": 51.0, "market_mid": 90.0, "divergence": -39.0}
- reality_divergence: KXITFMATCH-26JUL13LEAMEN-MEN {"kind": "resting_bid", "ref": 12.0, "market_mid": 44.5, "divergence": -32.5}
- reality_divergence: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 11.0, "market_mid": 48.0, "divergence": -37.0}
- reality_divergence: KXITFWMATCH-26JUL13CEUKRE-CEU {"kind": "resting_bid", "ref": 20.0, "market_mid": 53.5, "divergence": -33.5}
- reality_divergence: KXITFWMATCH-26JUL13CEUKRE-KRE {"kind": "resting_bid", "ref": 16.0, "market_mid": 46.0, "divergence": -30.0}
- reality_divergence: KXITFWMATCH-26JUL13ZHACOR-ZHA {"kind": "resting_bid", "ref": 15.0, "market_mid": 49.0, "divergence": -34.0}
- reality_divergence: KXITFMATCH-26JUL13MARVAL-VAL {"kind": "resting_bid", "ref": 35.0, "market_mid": 67.5, "divergence": -32.5}
- reality_divergence: KXITFMATCH-26JUL13SEGKAS-KAS {"kind": "resting_bid", "ref": 16.0, "market_mid": 49.5, "divergence": -33.5}
- reality_divergence: KXITFMATCH-26JUL13TAZHAR-TAZ {"kind": "resting_bid", "ref": 48.0, "market_mid": 76.5, "divergence": -28.5}
- reality_divergence: KXITFMATCH-26JUL13VRTKLA-KLA {"kind": "resting_bid", "ref": 19.0, "market_mid": 47.5, "divergence": -28.5}
- reality_divergence: KXITFWMATCH-26JUL13SIMMAR-SIM {"kind": "resting_bid", "ref": 14.0, "market_mid": 48.0, "divergence": -34.0}
- combined_over_goal_UNVERIFIED_BASIS: KXITFWMATCH-26JUL13SVIART {"combined": 101, "detail": "pair combined 101c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- reality_divergence: KXITFMATCH-26JUL13BARURA-URA {"kind": "resting_bid", "ref": 14.0, "market_mid": 73.0, "divergence": -59.0}
- reality_divergence: KXITFMATCH-26JUL13HOSSIN-HOS {"kind": "resting_bid", "ref": 59.0, "market_mid": 90.0, "divergence": -31.0}
- reality_divergence: KXITFMATCH-26JUL13LEAMEN-MEN {"kind": "resting_bid", "ref": 13.0, "market_mid": 41.0, "divergence": -28.0}
- reality_divergence: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 11.0, "market_mid": 48.0, "divergence": -37.0}
- reality_divergence: KXITFWMATCH-26JUL13CEUKRE-KRE {"kind": "resting_bid", "ref": 16.0, "market_mid": 47.5, "divergence": -31.5}
- reality_divergence: KXITFWMATCH-26JUL13ZHACOR-ZHA {"kind": "resting_bid", "ref": 15.0, "market_mid": 49.0, "divergence": -34.0}
- reality_divergence: KXITFMATCH-26JUL13SEGKAS-KAS {"kind": "resting_bid", "ref": 29.0, "market_mid": 66.0, "divergence": -37.0, "emitted_et": "2026-07-13 04:35:25 AM ET"}
- reality_divergence: KXITFWMATCH-26JUL13SIMMAR-SIM {"kind": "resting_bid", "ref": 14.0, "market_mid": 44.0, "divergence": -30.0, "emitted_et": "2026-07-13 04:35:25 AM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
