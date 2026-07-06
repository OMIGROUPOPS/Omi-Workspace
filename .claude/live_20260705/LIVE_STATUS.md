# LIVE VALIDATION — rolling status

- cycle 102 @ **2026-07-06 04:07:35 AM ET** | build `f9499f3` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 65088 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 4 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 23:50:46 | **walk_cap_breach** | KXITFWMATCH-26JUL06SIMCIR-SIM | buy 83c > ceiling 73c (conception 69 + cap) ref=join_bid |
| 01:01:56 | **combined_over_goal** | KXITFWMATCH-26JUL06TODSAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 01:12:30 | **combined_over_goal** | KXITFWMATCH-26JUL06VAJRAM | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |
| 03:38:20 | **combined_over_goal** | KXITFWMATCH-26JUL06DZJMCK | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 41 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:51 | ITFWMATCH-26JUL06PASCOP-PAS | ITF_W | underdog | 12 | 8 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:51 | ITFWMATCH-26JUL06LUCGAD-GAD | ITF_W | underdog | 37 | 33 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:52 | ITFWMATCH-26JUL06PASCOP-COP | ITF_W | leader | 85 | 83 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:59 | ITFWMATCH-26JUL06BRESAF-BRE | ITF_W | leader | 63 | 61 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:04 | ITFWMATCH-26JUL06SIMCIR-CIR | ITF_W | underdog | 16 | 12 | +4 (place_cell) | -30.0 | pre | pair | 97 | EARNED |
| 00:04 | ITFWMATCH-26JUL06SACLAZ-LAZ | ITF_W | underdog | 19 | 11 | +8 (place_cell) | — | pre | single |  | PENDING |
| 00:05 | ITFWMATCH-26JUL06HOSFEH-FEH | ITF_W | underdog | 61 | 63 | -2 (place_cell) | — | pre | single |  | PENDING |
| 00:06 | ITFWMATCH-26JUL06VAJRAM-VAJ | ITF_W | leader | 82 | 74 | +8 (place_cell) | — | pre | pair | 101 | PENDING |
| 00:10 | ITFWMATCH-26JUL06LUCGAD-LUC | ITF_W | leader | 60 | 60 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:17 | ITFMATCH-26JUL06GENAZO-AZO | ITF_M | underdog | 16 | 9 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:22 | ITFMATCH-26JUL06VULCOU-COU | ITF_M | ? | 16 | 10 | +6 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:33 | ITFWMATCH-26JUL06WONIBR-IBR | ITF_W | leader | 65 | 52 | +13 (place_cell) | — | pre | single |  | PENDING |
| 00:33 | ITFWMATCH-26JUL06SIMCIR-SIM | ITF_W | leader | 81 | 81 | +0 (place_cell) | 26.5 | pre | pair | 97 | GIFT_CLASS |
| 00:34 | ITFWMATCH-26JUL06KARBAS-BAS | ITF_W | underdog | 26 | 26 | +0 (place_cell) | — | pre | single |  | PENDING |
| 00:47 | ITFWMATCH-26JUL06TODSAG-TOD | ITF_W | leader | 68 | 62 | +6 (place_cell) | — | pre | pair | 98 | PENDING |
| 00:55 | ITFWMATCH-26JUL06ZRNLUE-LUE | ITF_W | underdog | 69 | 6 | +63 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:00 | ITFMATCH-26JUL06VULCOU-VUL | ITF_M | leader | 81 | 80 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:00 | ITFMATCH-26JUL06BEASCO-SCO | ITF_M | underdog | 33 | 21 | +12 (place_cell) | — | pre | single |  | PENDING |
| 01:01 | ITFWMATCH-26JUL06TODSAG-SAG | ITF_W | ? | 30 | 25 | +5 (place_cell) | — | pre | pair | 98 | PENDING |
| 01:05 | ITFWMATCH-26JUL06BRESAF-SAF | ITF_W | underdog | 34 | 32 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:12 | ITFWMATCH-26JUL06VAJRAM-RAM | ITF_W | ? | 19 | 9 | +10 (place_cell) | — | pre | pair | 101 | PENDING |
| 01:22 | ITFWMATCH-26JUL06POPSOL-POP | ITF_W | underdog | 36 | 21 | +15 (place_cell) | — | pre | single |  | PENDING |
| 01:23 | ITFMATCH-26JUL06GENAZO-GEN | ITF_M | leader | 81 | 73 | +8 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:44 | ATPCHALLENGERMATCH-26JUL06VILBOC-V | ATP_CHALL | leader | 75 | 72 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 01:51 | ATPCHALLENGERMATCH-26JUL06NIJRAH-R | ATP_CHALL | underdog | 40 | 37 | +3 (place_cell) | — | pre | single |  | PENDING |
| 02:21 | ITFWMATCH-26JUL06WAGYOU-YOU | ITF_W | leader | 63 | 49 | +14 (place_cell) | — | pre | single |  | PENDING |
| 03:05 | ITFWMATCH-26JUL06ZRNLUE-ZRN | ITF_W | ? | 28 | 2 | +26 (place_cell) | — | pre | pair | 97 | PENDING |
| 03:16 | ITFWMATCH-26JUL06BOIBOY-BOI | ITF_W | leader | 77 | 75 | +2 (place_cell) | — | pre | single |  | PENDING |
| 03:29 | ITFMATCH-26JUL06SALNGW-NGW | ITF_M | ? | 39 | 32 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 03:31 | ITFWMATCH-26JUL06KULGON-GON | ITF_W | ? | 22 | 16 | +6 (place_cell) | — | pre | single |  | PENDING |
| 03:34 | ITFMATCH-26JUL06HERNAG-HER | ITF_M | ? | 70 | 49 | +21 (place_cell) | — | pre | single |  | PENDING |
| 03:38 | ITFWMATCH-26JUL06DZJMCK-DZJ | ITF_W | leader | 77 | 41 | +36 (place_cell) | — | pre | pair | 99 | PENDING |
| 03:38 | ITFWMATCH-26JUL06DZJMCK-MCK | ITF_W | underdog | 22 | 12 | +10 (place_cell) | — | pre | pair | 99 | PENDING |
| 03:39 | ITFWMATCH-26JUL06JOSKUM-JOS | ITF_W | underdog | 67 | 79 | -12 (place_cell) | — | pre | single |  | PENDING |
| 03:39 | ITFWMATCH-26JUL06HEDCHI-CHI | ITF_W | underdog | 51 | 20 | +31 (place_cell) | — | pre | pair | 95 | PENDING |
| 03:41 | ITFWMATCH-26JUL06VLADIL-VLA | ITF_W | underdog | 41 | 34 | +7 (place_cell) | — | pre | single |  | PENDING |
| 03:50 | ITFWMATCH-26JUL06HEDCHI-HED | ITF_W | underdog | 44 | 13 | +31 (place_cell) | — | pre | pair | 95 | PENDING |
| 03:55 | ITFMATCH-26JUL06SALNGW-SAL | ITF_M | leader | 58 | 48 | +10 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:00 | ATPCHALLENGERMATCH-26JUL06PRIORA-P | ATP_CHALL | leader | 56 | 54 | +2 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 04:01 | ITFMATCH-26JUL06LARJIM-LAR | ITF_M | underdog | 40 | 31 | +9 (place_cell) | — | pre | single |  | PENDING |
| 04:07 | ITFWMATCH-26JUL06DIANIK-NIK | ITF_W | leader | 52 | 49 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 211 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 67, 'FLOW_AT_LEVEL': 13, 'NO_FLOW': 131} | repriceable now: true 39 / false 172 | **cumulative bid_grade lines: 1446 (repriceable true 158 / false 1288)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06BASHOE-B | 47 | 37m | 1/50-50/20 | 47-50 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ATPCHALLENGERMATCH-26JUL06BASHOE-H | 51 | 37m | 1/52-52/46 | 51-52 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ATPCHALLENGERMATCH-26JUL06CAMDE-CA | 58 | 164m | 5/61-63/423 | 60-61 | 3 | **FLOW_ABOVE** | 59 | REPRICEABLE→59 |
| ATPCHALLENGERMATCH-26JUL06CAMDE-DE | 39 | 187m | 1/41-41/17 | 39-40 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ATPCHALLENGERMATCH-26JUL06CHEYEV-C | 61 | 67m | 2/62-62/25 | 61-62 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→62 |
| ATPCHALLENGERMATCH-26JUL06CHEYEV-Y | 37 | 67m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DALCAR-C | 3 | 157m | 11/4-4/622 | 3-4 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→4 |
| ATPCHALLENGERMATCH-26JUL06DALCAR-D | 96 | 157m | 8/97-97/359 | 96-97 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→97 |
| ATPCHALLENGERMATCH-26JUL06DELWAL-D | 27 | 127m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DELWAL-W | 71 | 127m | 1/71-71/9 | 71-73 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DONCIZ-C | 24 | 7m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-E | 95 | 97m | 0 | 95-96 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-S | 4 | 97m | 0 | 4-5 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-G | 71 | 157m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | 26 | 137m | 2/27-27/523 | 27-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-H | 35 | 97m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-P | 61 | 97m | 2/67-67/29 | 63-67 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06IVADIN-D | 20 | 37m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06IVADIN-I | 78 | 37m | 0 | 78-80 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 6 | 247m | 34/8-9/1670 | 6-8 | 2 | **FLOW_ABOVE** | 5 | flow above but bound 5c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06KRACRI-K | 92 | 206m | 13/92-94/519 | 92-94 | 0 | **FLOW_AT_LEVEL** | 91 |  |
| ATPCHALLENGERMATCH-26JUL06KUZSTR-K | 73 | 67m | 1/74-74/32 | 73-74 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ATPCHALLENGERMATCH-26JUL06KUZSTR-S | 26 | 67m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARBER-B | 58 | 157m | 3/59-59/133 | 59-59 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ATPCHALLENGERMATCH-26JUL06MARBER-M | 40 | 157m | 5/41-42/196 | 40-42 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ATPCHALLENGERMATCH-26JUL06MARHAM-H | 5 | 97m | 0 | 5-6 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARHAM-M | 94 | 83m | 1/95-95/0 | 94-95 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→95 |
| ATPCHALLENGERMATCH-26JUL06NIJRAH-N | 57 | 133m | 5/60-60/168 | 59-59 | 3 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06OPIPET-O | 26 | 67m | 1/27-27/0 | 26-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ATPCHALLENGERMATCH-26JUL06OPIPET-P | 71 | 7m | 0 | 72-72 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PAPJAN-P | 53 | 127m | 2/55-55/54 | 54-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-M | 53 | 26m | 1/55-55/100 | 53-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-P | 45 | 26m | 10/47-47/1046 | 45-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ATPCHALLENGERMATCH-26JUL06POLHAI-H | 68 | 7m | 0 | 68-70 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POLHAI-P | 31 | 7m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POTFEL-F | 58 | 157m | 2/60-60/181 | 58-60 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ATPCHALLENGERMATCH-26JUL06POTFEL-P | 40 | 157m | 1/42-42/15 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 222m | 22/42-45/2489 | 44-43 | 2 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 6m | 1/45-45/10 | 44-43 | 5 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 61 | 97m | 0 | 65-69 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 32 | 95m | 0 | 32-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-B | 36 | 127m | 1/37-37/7 | 36-37 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-S | 61 | 127m | 0 | 61-64 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-M | 10 | 156m | 1/10-10/0 | 10-12 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-S | 88 | 157m | 1/90-90/0 | 88-90 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 187m | 1/35-35/349 | 33-34 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ATPCHALLENGERMATCH-26JUL06STALEC-S | 64 | 152m | 6/66-67/166 | 64-66 | 2 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06VALZHU-V | 71 | 37m | 0 | 71-75 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06VALZHU-Z | 27 | 37m | 0 | 27-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 22 | 143m | 12/27-30/462 | 27-25 | 5 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 22 | 66m | 5/28-30/125 | 27-25 | 6 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06WALNEU-N | 28 | 5m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06WALNEU-W | 70 | 7m | 0 | 70-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06WEHVAN-V | 42 | 48m | 0 | 45-46 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-D | 42 | 97m | 1/44-44/11 | 42-44 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-Z | 56 | 97m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL06DECOB-COB | 23 | 7m | 1/24-24/39 | 23-24 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| ITFMATCH-26JUL06ALEREG-ALE | 51 | 3m | 0 | 51-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALEREG-REG | 40 | 4m | 0 | 40-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-ALI | 87 | 1m | 0 | 90-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-MIS | 6 | 95m | 0 | 6-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BEASCO-BEA | 64 | 181m | 51/66-83/1993 | 73-66 | 2 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BEASCO-BEA | 64 | 9m | 20/66-76/1239 | 73-66 | 2 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BONFAU-FAU | 25 | 95m | 0 | 25-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06CASBAY-CAS | 6 | 124m | 0 | 6-95 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-DUG | 63 | 83m | 0 | 63-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-HOF | 20 | 82m | 0 | 20-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUHCAR-CAR | 12 | 5m | 0 | 12-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUHCAR-DUH | 83 | 8m | 0 | 83-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-ELD | 64 | 113m | 1/69-69/2 | 64-69 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-HAU | 31 | 8m | 0 | 31-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GANVER-GAN | 20 | 7m | 0 | 46-52 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GARCIO-CIO | 39 | 8m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GARCIO-GAR | 56 | 15m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 156m | 99/1-19/6692 | 18-3 | -15 | **FLOW_AT_LEVEL** | 16 |  |
| ITFMATCH-26JUL06HERNAG-NAG | 27 | 7m | 0 | 27-51 | — | **NO_FLOW** | 27 |  |
| ITFMATCH-26JUL06HOSGAT-GAT | 38 | 8m | 0 | 38-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HOSGAT-HOS | 55 | 8m | 0 | 55-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06JAIHEN-JAI | 45 | 5m | 0 | 45-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-KAS | 64 | 0m | 0 | 64-70 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-LIL | 31 | 13m | 1/35-35/18 | 31-35 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ITFMATCH-26JUL06LARJIM-JIM | 57 | 4m | 0 | 61-66 | — | **NO_FLOW** | 57 |  |
| ITFMATCH-26JUL06LAZVAC-LAZ | 55 | 1m | 0 | 55-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LAZVAC-VAC | 39 | 93m | 0 | 39-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 32 | 84m | 0 | 32-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-THE | 65 | 152m | 0 | 65-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MEHCOU-COU | 52 | 2m | 0 | 52-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MEHCOU-MEH | 26 | 19m | 0 | 26-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-BEC | 87 | 7m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-ROJ | 10 | 7m | 0 | 10-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALBRE-BRE | 6 | 156m | 3/11-11/29 | 6-8 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALBRE-SAL | 89 | 152m | 1/94-94/21 | 89-93 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06STAGUI-GUI | 22 | 2m | 0 | 22-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STAGUI-STA | 22 | 2m | 0 | 22-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STEAUN-AUN | 14 | 6m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STEAUN-STE | 82 | 7m | 0 | 82-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TEUHAS-HAS | 26 | 3m | 0 | 62-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TEUHAS-TEU | 33 | 5m | 0 | 33-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TIMJEF-JEF | 70 | 19m | 0 | 70-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TIMJEF-TIM | 19 | 19m | 0 | 19-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRA | 24 | 64m | 0 | 24-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRU | 66 | 67m | 0 | 66-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-AND | 23 | 13m | 0 | 23-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-TSI | 58 | 13m | 0 | 58-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ADKFER-ADK | 53 | 82m | 0 | 53-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ADKFER-FER | 18 | 82m | 0 | 18-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 51m | 0 | 28-31 | — | **NO_FLOW** | 20 |  |
| ITFWMATCH-26JUL06BOSTOP-BOS | 67 | 35m | 2/68-68/4 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFWMATCH-26JUL06BOSTOP-TOP | 33 | 127m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 178m | 413/21-58/23545 | 51-22 | -13 | **FLOW_AT_LEVEL** | 34 |  |
| ITFWMATCH-26JUL06BUYALV-ALV | 22 | 58m | 0 | 22-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BUYALV-BUY | 54 | 19m | 0 | 54-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DIANIK-DIA | 44 | 47m | 0 | 44-53 | — | **NO_FLOW** | 45 |  |
| ITFWMATCH-26JUL06EWAMAN-EWA | 66 | 20m | 0 | 66-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EWAMAN-MAN | 20 | 49m | 0 | 20-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-GAL | 76 | 107m | 1/80-80/2 | 76-80 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL06GALTSE-TSE | 21 | 118m | 0 | 21-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-GAN | 83 | 95m | 0 | 83-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-PUI | 11 | 88m | 0 | 11-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 5 | 0m | 0 | 94-58 | — | **NO_FLOW** | 36 |  |
| ITFWMATCH-26JUL06ILIEBE-EBE | 52 | 126m | 0 | 52-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ILIEBE-ILI | 38 | 57m | 0 | 38-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06IVAKUH-IVA | 62 | 164m | 10/63-64/546 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL06IVAKUH-KUH | 37 | 185m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06JOSKUM-KUM | 30 | 1m | 9/71-77/54 | 75-35 | 41 | **FLOW_ABOVE** | 30 | flow above but bound 30c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARBAS-KAR | 71 | 212m | 5/75-76/40 | 71-72 | 4 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARBAS-KAR | 67 | 115m | 0 | 71-72 | — | **NO_FLOW** | 71 |  |
| ITFWMATCH-26JUL06KARVIS-KAR | 77 | 2m | 0 | 77-87 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARVIS-VIS | 14 | 95m | 0 | 14-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOTCHI-KOT | 33 | 100m | 0 | 33-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOVDAE-DAE | 18 | 37m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOVDAE-KOV | 75 | 36m | 0 | 75-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 36m | 0 | 76-79 | — | **NO_FLOW** | 75 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 36m | 0 | 76-79 | — | **NO_FLOW** | 75 |  |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 224m | 3895/23-99/459986 | 99-24 | -14 | **FLOW_AT_LEVEL** | 37 |  |
| ITFWMATCH-26JUL06LUKNOE-LUK | 69 | 108m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUKNOE-NOE | 25 | 216m | 1/31-31/4 | 25-30 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06MARGLU-GLU | 65 | 6m | 0 | 65-71 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MARGLU-MAR | 28 | 5m | 0 | 28-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-ENC | 51 | 54m | 0 | 51-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-MCA | 42 | 43m | 0 | 42-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MILHER-HER | 14 | 54m | 0 | 14-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MILHER-MIL | 65 | 19m | 0 | 65-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKASAK-OKA | 26 | 19m | 0 | 26-53 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-OKU | 54 | 52m | 0 | 54-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-PRI | 39 | 54m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PACLOV-LOV | 45 | 26m | 7/46-47/654 | 45-46 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL06PACLOV-PAC | 56 | 126m | 1/56-56/50 | 56-57 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 127m | 1942/1-13/312225 | 14-1 | -7 | **FLOW_AT_LEVEL** | 12 |  |
| ITFWMATCH-26JUL06PEEPAH-PAH | 58 | 79m | 0 | 58-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PEEPAH-PEE | 37 | 104m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PIERAD-PIE | 58 | 56m | 0 | 58-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PIERAD-RAD | 27 | 58m | 0 | 27-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PODLUK-LUK | 68 | 54m | 0 | 68-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PODLUK-POD | 26 | 56m | 0 | 26-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06POPSOL-SOL | 61 | 165m | 8/66-75/47 | 65-63 | 5 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06POPSOL-SOL | 59 | 96m | 1/66-66/4 | 65-63 | 7 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06POZMLA-MLA | 5 | 19m | 0 | 5-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-NIJ | 30 | 36m | 0 | 30-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-PRI | 63 | 36m | 0 | 63-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06RICMIT-MIT | 7 | 186m | 18/8-90/167 | 7-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFWMATCH-26JUL06SACLAZ-SAC | 78 | 247m | 102/79-90/1628 | 80-80 | 1 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 174m | 15490/3-90/1258555 | 83-5 | -11 | **FLOW_AT_LEVEL** | 16 |  |
| ITFWMATCH-26JUL06SPIMED-MED | 5 | 156m | 1/14-14/14 | 5-14 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06SPIMED-SPI | 86 | 108m | 3/95-95/25 | 86-95 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-SCH | 6 | 124m | 0 | 6-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-TEI | 76 | 2m | 0 | 76-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TRIVOR-TRI | 8 | 114m | 0 | 8-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TRIVOR-VOR | 63 | 1m | 0 | 63-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-EVA | 36 | 12m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-URR | 61 | 7m | 0 | 61-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 174m | 1621/3-26/210133 | 20-4 | -12 | **FLOW_AT_LEVEL** | 15 |  |
| ITFWMATCH-26JUL06VIRKOV-KOV | 29 | 18m | 0 | 29-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VIRKOV-VIR | 56 | 51m | 0 | 56-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VLADIL-DIL | 56 | 26m | 3/62-64/66 | 60-60 | 6 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06WAGYOU-WAG | 34 | 75m | 0 | 34-54 | — | **NO_FLOW** | 34 |  |
| ITFWMATCH-26JUL06WAGYOU-WAG | 34 | 2m | 0 | 34-54 | — | **NO_FLOW** | 34 |  |
| ITFWMATCH-26JUL06WONIBR-WON | 32 | 173m | 16/72-92/49 | 80-57 | 40 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ARANIL-A | 73 | 84m | 1/75-75/56 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| WTACHALLENGERMATCH-26JUL06ARANIL-N | 25 | 97m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 74 | 7m | 0 | 74-76 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 24 | 7m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BLIAND-A | 35 | 7m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BLIAND-B | 64 | 7m | 0 | 64-65 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BOUKOT-B | 22 | 187m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| WTACHALLENGERMATCH-26JUL06BOUKOT-K | 77 | 179m | 3/78-79/638 | 77-78 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| WTACHALLENGERMATCH-26JUL06BULSTR-B | 71 | 187m | 2/71-74/23 | 71-74 | 0 | **FLOW_AT_LEVEL** | 68 |  |
| WTACHALLENGERMATCH-26JUL06BULSTR-S | 27 | 122m | 2/28-29/56 | 27-29 | 1 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06GRAMAS-G | 32 | 97m | 1/33-33/100 | 32-33 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→33 |
| WTACHALLENGERMATCH-26JUL06GRAMAS-M | 67 | 97m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 41 | 187m | 1/43-43/28 | 41-43 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| WTACHALLENGERMATCH-26JUL06HERNGU-N | 58 | 51m | 3/59-59/950 | 58-59 | 1 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06HESPAL-H | 30 | 97m | 0 | 30-31 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HESPAL-P | 69 | 98m | 1/70-70/24 | 69-70 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| WTACHALLENGERMATCH-26JUL06LEWMAR-L | 55 | 97m | 0 | 55-57 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06LEWMAR-M | 43 | 97m | 1/44-44/12 | 43-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| WTACHALLENGERMATCH-26JUL06MATPUT-M | 9 | 97m | 1/9-9/0 | 9-10 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MATPUT-P | 89 | 97m | 2/91-91/35 | 90-91 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→91 |
| WTACHALLENGERMATCH-26JUL06MONPOP-M | 46 | 43m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MONPOP-P | 54 | 185m | 2/55-55/1177 | 54-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| WTACHALLENGERMATCH-26JUL06NOHBUR-B | 22 | 117m | 5/24-24/472 | 23-23 | 2 | **FLOW_ABOVE** | 21 | flow above but bound 21c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06NOHBUR-N | 75 | 7m | 0 | 75-76 | — | **NO_FLOW** | 73 |  |
| WTACHALLENGERMATCH-26JUL06OLIUCH-O | 59 | 7m | 2/61-61/247 | 60-60 | 2 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06OLIUCH-U | 39 | 67m | 5/40-40/247 | 40-40 | 1 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ROMSEM-R | 42 | 67m | 0 | 43-44 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06ROMSEM-S | 56 | 98m | 1/57-57/8 | 56-57 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| WTACHALLENGERMATCH-26JUL06WALKAW-K | 43 | 7m | 0 | 43-44 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06WALKAW-W | 55 | 7m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06WERSAL-S | 67 | 7m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06WERSAL-W | 31 | 7m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL06KRUKOS-KRU | 31 | 127m | 52/31-32/5520 | 32-32 | 0 | **FLOW_AT_LEVEL** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06KARBAS | 26 | 72 | **98** | 97 | +1 |
| ITFWMATCH-26JUL06SACLAZ | 19 | 80 | **99** | 97 | +2 |
| ITFMATCH-26JUL06BEASCO | 33 | 66 | **99** | 97 | +2 |
| ITFWMATCH-26JUL06POPSOL | 36 | 63 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06NIJRAH | 40 | 59 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06PRIORA | 56 | 43 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06VILBOC | 75 | 25 | **100** | 97 | +3 |
| ITFWMATCH-26JUL06KULGON | 22 | 79 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06VLADIL | 41 | 60 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06JOSKUM | 67 | 35 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06DIANIK | 52 | 53 | **105** | 97 | +8 |
| ITFMATCH-26JUL06LARJIM | 40 | 66 | **106** | 97 | +9 |
| ITFWMATCH-26JUL06BOIBOY | 77 | 31 | **108** | 97 | +11 |
| ITFWMATCH-26JUL06WAGYOU | 63 | 54 | **117** | 97 | +20 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 58 | **119** | 97 | +22 |
| ITFMATCH-26JUL06HERNAG | 70 | 51 | **121** | 97 | +24 |
| ITFWMATCH-26JUL06WONIBR | 65 | 57 | **122** | 97 | +25 |

## PATTERNS (sub-B) — 14
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SIMCIR-SIM {"price": 84, "ceiling": 73, "emitted_et": "2026-07-06 04:07:35 AM ET"}
- deep_neg_fv: KXITFWMATCH-26JUL06SIMCIR-CIR {"entry_minus_fv_burst": -30.0, "emitted_et": "2026-07-06 04:07:35 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL06SACLAZ-LAZ {"fill": 19, "age_min": 243, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 242, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 214, "mode": "SET_BELOW_FLOW(prints 40c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06KARBAS-BAS {"fill": 26, "age_min": 213, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFMATCH-26JUL06BEASCO-SCO {"fill": 33, "age_min": 187, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06POPSOL-POP {"fill": 36, "age_min": 165, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VILBOC-VIL {"fill": 75, "age_min": 143, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06NIJRAH-RAH {"fill": 40, "age_min": 136, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06WAGYOU-YOU {"fill": 63, "age_min": 107, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06BOIBOY-BOI {"fill": 77, "age_min": 51, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06KULGON-GON {"fill": 22, "age_min": 36, "mode": "STARVATION(no prints since post)", "emitted_et": "2026-07-06 04:07:35 AM ET"}
- half_arm_aging: KXITFMATCH-26JUL06HERNAG-HER {"fill": 70, "age_min": 33, "mode": "STARVATION(no prints since post)", "emitted_et": "2026-07-06 04:07:35 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
