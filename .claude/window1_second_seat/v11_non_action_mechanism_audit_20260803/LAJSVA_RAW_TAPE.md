# LAJSVA RAW TAPE — both legs in tandem, discovery → true bell
License LAW_INDEX @ 35842b42 (41784e6a…); L6 L8 L11 L18 L20 L22. Event KXATPCHALLENGERMATCH-26JUL14LAJSVA. Discovery 1784007323 · formation end LAJ/SVA 1784007603 · true bell 1784078400 (machine receipt). Corrections W1TT-C-001/002 do not touch this game.
Sources: dual-book ticks KXATPCHALLENGERMATCH-26JUL14LAJSVA-{LAJ,SVA}.csv.gz (one row per change in best bid / best ask / last trade), prints.jsonl true prints, reflex pass = walk trace FULL_DECISION_TRACE_5 (champion byte-equal), v6 pass-1 = FOUR_STORIES @d521f9dd full 20-stage action list (LAJ then SVA per stage).
Kalshi reconciliation (GET /trade-api/v2/markets/trades by ticker): API trades LAJ 18691 / SVA 15290; tape true prints 33981 (in span 543); matched by trade_id 33981; unmatched 0.
SVA kiss check: last rest action before the fill = REFLEX REPRICE_REST@41 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-352 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL at 1784020209; fill print 1784020209.484 (two prints 41c×6 and 41c×10, taker hit the BID); store ordering in the fill second (19 SVA book receipts at 1784020209): row-344 a 41 bid of size 16 appears · row-345 reflex REPRICE@41 joins it (queue ahead 16) · rows 346–348 bid 41 size 116→100 · row-349/350 bid back to 40 (reflex REPRICE@40) · row-351/352 bid 41 size 2502 (reflex REPRICE@41) · rows 353–356 hold 41. Verdict: kiss PASS under L0/L9 by store ordering (a rest at 41 precedes the print in sequence); strictly-after at sub-second NOT PROVABLE — the recorder clock is 1-s resolution and the 41-rest flapped 41→40→41 inside that second; the 16 contracts printed equal the 16-lot that stood ahead of the rest (F-VS-054).

epoch | Δs from discovery | leg | best_bid | best_ask | last_trade | trade | marker | source
---|---|---|---|---|---|---|---|---
1784007323.000 | 0.000 | * |  |  |  |  | DISCOVERY (recorder open) | c0056976
1784007323.000 | 0.000 | LAJ | 5 | 86 | 0 |  |  | ticks#row-1
1784007323.000 | 0.000 | SVA | 5 | 86 | 0 |  |  | ticks#row-1
1784007333.000 | 10.000 | LAJ | 5 | 85 | 0 |  |  | ticks#row-3
1784007334.000 | 11.000 | SVA | 5 | 85 | 0 |  |  | ticks#row-6
1784007335.000 | 12.000 | LAJ | 5 | 84 | 0 |  |  | ticks#row-7
1784007335.000 | 12.000 | SVA | 5 | 84 | 0 |  |  | ticks#row-10
1784007401.000 | 78.000 | LAJ | 5 | 90 | 0 |  |  | ticks#row-17
1784007401.000 | 78.000 | LAJ | 5 | 91 | 0 |  |  | ticks#row-19
1784007401.000 | 78.000 | SVA | 5 | 90 | 0 |  |  | ticks#row-19
1784007401.000 | 78.000 | SVA | 5 | 91 | 0 |  |  | ticks#row-21
1784007409.000 | 86.000 | LAJ | 5 | 90 | 0 |  |  | ticks#row-26
1784007409.000 | 86.000 | SVA | 5 | 90 | 0 |  |  | ticks#row-28
1784007436.000 | 113.000 | LAJ | 5 | 89 | 0 |  |  | ticks#row-29
1784007437.000 | 114.000 | LAJ | 5 | 88 | 0 |  |  | ticks#row-33
1784007437.000 | 114.000 | SVA | 5 | 89 | 0 |  |  | ticks#row-34
1784007453.000 | 130.000 | SVA | 5 | 88 | 0 |  |  | ticks#row-38
1784007486.000 | 163.000 | LAJ | 5 | 87 | 0 |  |  | ticks#row-41
1784007486.000 | 163.000 | SVA | 5 | 87 | 0 |  |  | ticks#row-46
1784007487.000 | 164.000 | LAJ | 5 | 86 | 0 |  |  | ticks#row-45
1784007487.000 | 164.000 | SVA | 5 | 86 | 0 |  |  | ticks#row-50
1784007603.000 | 280.000 | LAJ |  |  |  |  | FORMATION END | c0056976
1784007603.000 | 280.000 | SVA |  |  |  |  | FORMATION END | c0056976
1784007603.000 | 280.000 | LAJ | 54 | 86 | 0 |  |  | ticks#row-51
1784007603.000 | 280.000 | LAJ | 54 | 64 | 0 |  |  | ticks#row-52
1784007603.000 | 280.000 | SVA | 36 | 86 | 0 |  |  | ticks#row-57
1784007603.000 | 280.000 | SVA | 36 | 46 | 0 |  |  | ticks#row-58
1784007604.000 | 281.000 | LAJ | 55 | 64 | 0 |  |  | ticks#row-58
1784007604.000 | 281.000 | SVA | 36 | 43 | 0 |  |  | ticks#row-64
1784007604.002 | 281.002 | SVA |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@34 (before 35) | FOUR_STORIES
1784007640.000 | 317.000 | SVA | 36 | 42 | 0 |  |  | ticks#row-74
1784007640.000 | 317.000 | LAJ |  |  |  |  | REFLEX PLACE_REST@55 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-70 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784007640.000 | 317.000 | SVA |  |  |  |  | REFLEX PLACE_REST@36 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-74 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784007670.000 | 347.000 | SVA | 36 | 41 | 0 |  |  | ticks#row-81
1784007763.000 | 440.000 | SVA | 36 | 40 | 0 |  |  | ticks#row-84
1784010254.000 | 2931.000 | LAJ | 56 | 64 | 0 |  |  | ticks#row-81
1784010254.000 | 2931.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@56 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-82 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784010255.000 | 2932.000 | LAJ | 57 | 64 | 0 |  |  | ticks#row-87
1784010255.000 | 2932.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@57 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-88 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784010486.000 | 3163.000 | LAJ | 58 | 64 | 0 |  |  | ticks#row-100
1784010486.000 | 3163.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@58 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-101 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784010487.000 | 3164.000 | LAJ | 59 | 64 | 0 |  |  | ticks#row-105
1784010487.000 | 3164.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@59 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-106 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784010972.000 | 3649.000 | LAJ | 60 | 64 | 0 |  |  | ticks#row-123
1784010972.000 | 3649.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@60 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-124 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784011052.000 | 3729.000 | LAJ | 60 | 63 | 0 |  |  | ticks#row-137
1784011052.000 | 3729.000 | SVA | 37 | 40 | 0 |  |  | ticks#row-127
1784011052.000 | 3729.000 | SVA |  |  |  |  | REFLEX REPRICE_REST@37 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-128 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784011407.000 | 4084.000 | LAJ | 58 | 63 | 0 |  |  | ticks#row-143
1784011407.000 | 4084.000 | LAJ | 59 | 63 | 0 |  |  | ticks#row-144
1784011407.000 | 4084.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@58 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-144 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784011407.000 | 4084.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@59 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-145 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784012624.000 | 5301.000 | LAJ | 59 | 64 | 0 |  |  | ticks#row-147
1784012624.000 | 5301.000 | SVA | 36 | 40 | 0 |  |  | ticks#row-148
1784012624.000 | 5301.000 | SVA |  |  |  |  | REFLEX REPRICE_REST@36 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-149 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784012635.000 | 5312.000 | LAJ | 59 | 63 | 0 |  |  | ticks#row-157
1784012635.000 | 5312.000 | SVA | 37 | 40 | 0 |  |  | ticks#row-164
1784012635.000 | 5312.000 | SVA |  |  |  |  | REFLEX REPRICE_REST@37 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-165 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784013312.000 | 5989.000 | SVA | 37 | 41 | 0 |  |  | ticks#row-174
1784013560.000 | 6237.000 | LAJ | 59 | 62 | 0 |  |  | ticks#row-166
1784016081.367 | 8758.367 | LAJ |  |  | 62 | 62c x 3.0 taker=yes trade_id=51ffb46a-c62c-6890-aa69-cd9970de51c6 |  | prints.jsonl
1784016081.368 | 8758.368 | LAJ |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@52 (before 47) | FOUR_STORIES
1784016081.368 | 8758.368 | SVA |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@33 (before 34) | FOUR_STORIES
1784016082.000 | 8759.000 | LAJ | 59 | 62 | 62 |  |  | ticks#row-184
1784016084.000 | 8761.000 | LAJ | 60 | 62 | 62 |  |  | ticks#row-186
1784016084.000 | 8761.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@60 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-187 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784017359.000 | 10036.000 | LAJ | 60 | 61 | 62 |  |  | ticks#row-227
1784020153.000 | 12830.000 | SVA | 38 | 41 | 0 |  |  | ticks#row-223
1784020153.000 | 12830.000 | SVA | 37 | 41 | 0 |  |  | ticks#row-230
1784020153.000 | 12830.000 | SVA | 37 | 40 | 0 |  |  | ticks#row-233
1784020153.000 | 12830.000 | SVA |  |  |  |  | REFLEX REPRICE_REST@38 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-224 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020153.000 | 12830.000 | SVA |  |  |  |  | REFLEX REPRICE_REST@37 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-231 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020161.000 | 12838.000 | SVA | 38 | 40 | 0 |  |  | ticks#row-238
1784020161.000 | 12838.000 | SVA |  |  |  |  | REFLEX REPRICE_REST@38 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-239 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020166.000 | 12843.000 | LAJ | 59 | 61 | 62 |  |  | ticks#row-315
1784020166.000 | 12843.000 | SVA | 38 | 41 | 0 |  |  | ticks#row-247
1784020166.000 | 12843.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@59 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-316 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020167.000 | 12844.000 | LAJ | 59 | 60 | 62 |  |  | ticks#row-318
1784020167.000 | 12844.000 | SVA | 40 | 41 | 0 |  |  | ticks#row-249
1784020167.000 | 12844.000 | SVA |  |  |  |  | REFLEX REPRICE_REST@40 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-250 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020180.000 | 12857.000 | LAJ | 58 | 60 | 62 |  |  | ticks#row-333
1784020180.000 | 12857.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@58 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-334 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020196.000 | 12873.000 | LAJ | 58 | 59 | 62 |  |  | ticks#row-377
1784020196.000 | 12873.000 | LAJ | 58 | 60 | 62 |  |  | ticks#row-387
1784020201.830 | 12878.830 | SVA |  |  | 41 | 41c x 27.0 taker=yes trade_id=95992e7f-c30f-6ca9-7bac-082bc6399668 |  | prints.jsonl
1784020201.830 | 12878.830 | SVA |  |  |  |  | FLOOR PRINT 41c (lawful pre-bell minimum) | REPRODUCTION_AUDIT_d521f9dd
1784020201.831 | 12878.831 | LAJ |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@50 (before 52) | FOUR_STORIES
1784020201.831 | 12878.831 | SVA |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@35 (before 33) | FOUR_STORIES
1784020202.000 | 12879.000 | LAJ | 58 | 59 | 62 |  |  | ticks#row-394
1784020202.000 | 12879.000 | SVA | 40 | 41 | 41 |  |  | ticks#row-302
1784020205.000 | 12882.000 | LAJ | 56 | 59 | 62 |  |  | ticks#row-416
1784020205.000 | 12882.000 | LAJ | 56 | 58 | 62 |  |  | ticks#row-427
1784020205.000 | 12882.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@56 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-417 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020209.000 | 12886.000 | SVA | 40 | 42 | 41 |  |  | ticks#row-342
1784020209.000 | 12886.000 | SVA | 41 | 42 | 41 |  |  | ticks#row-344
1784020209.000 | 12886.000 | SVA | 40 | 42 | 41 |  |  | ticks#row-349
1784020209.000 | 12886.000 | SVA | 41 | 42 | 41 |  |  | ticks#row-351
1784020209.000 | 12886.000 | SVA |  |  |  |  | REFLEX REPRICE_REST@41 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-345 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020209.000 | 12886.000 | SVA |  |  |  |  | REFLEX REPRICE_REST@40 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-350 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020209.000 | 12886.000 | SVA |  |  |  |  | REFLEX REPRICE_REST@41 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-352 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020209.484 | 12886.484 | SVA |  |  |  |  | FILL (reflex/champion) 41c credited | MARKET_EVENT_LEDGER_5
1784020209.484 | 12886.484 | SVA |  |  | 41 | 41c x 6.0 taker=yes trade_id=d97f0682-a7e3-64f5-9751-dd8c5fcf09f4 |  | prints.jsonl
1784020209.484 | 12886.484 | SVA |  |  | 41 | 41c x 10.0 taker=yes trade_id=62c5acca-20b5-609e-9743-315bb552232f |  | prints.jsonl
1784020210.000 | 12887.000 | LAJ | 56 | 57 | 62 |  |  | ticks#row-466
1784020214.879 | 12891.879 | SVA |  |  | 42 | 42c x 11.0 taker=yes trade_id=4f1edd6e-4e43-6394-4176-9cafeb1e897a |  | prints.jsonl
1784020214.879 | 12891.879 | SVA |  |  | 42 | 42c x 33.0 taker=yes trade_id=0e9f25d9-d3ad-6be1-6802-49be7a5c57a9 |  | prints.jsonl
1784020215.000 | 12892.000 | LAJ | 55 | 57 | 62 |  |  | ticks#row-473
1784020215.000 | 12892.000 | SVA | 41 | 43 | 41 |  |  | ticks#row-366
1784020215.000 | 12892.000 | SVA | 42 | 43 | 41 |  |  | ticks#row-368
1784020215.000 | 12892.000 | SVA | 42 | 43 | 42 |  |  | ticks#row-369
1784020215.000 | 12892.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@55 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-474 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020216.830 | 12893.830 | SVA |  |  | 43 | 43c x 16.0 taker=yes trade_id=6a125304-0f14-4aa4-5dfd-3d57fd746a9d |  | prints.jsonl
1784020218.000 | 12895.000 | SVA | 42 | 43 | 43 |  |  | ticks#row-394
1784020218.595 | 12895.595 | SVA |  |  | 43 | 43c x 29.0 taker=yes trade_id=7ce91f26-56b8-4d78-4cec-f918b65af90d |  | prints.jsonl
1784020219.000 | 12896.000 | LAJ | 54 | 57 | 62 |  |  | ticks#row-505
1784020219.000 | 12896.000 | SVA | 42 | 46 | 43 |  |  | ticks#row-402
1784020219.000 | 12896.000 | SVA | 43 | 46 | 43 |  |  | ticks#row-403
1784020219.000 | 12896.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@54 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-506 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020220.000 | 12897.000 | LAJ | 55 | 57 | 62 |  |  | ticks#row-555
1784020220.000 | 12897.000 | SVA | 43 | 45 | 43 |  |  | ticks#row-453
1784020220.000 | 12897.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@55 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-556 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020222.000 | 12899.000 | SVA | 43 | 46 | 43 |  |  | ticks#row-479
1784020223.000 | 12900.000 | LAJ | 54 | 57 | 62 |  |  | ticks#row-581
1784020223.000 | 12900.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@54 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-582 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020224.000 | 12901.000 | LAJ | 55 | 57 | 62 |  |  | ticks#row-595
1784020224.000 | 12901.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@55 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-596 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020239.000 | 12916.000 | LAJ | 55 | 56 | 62 |  |  | ticks#row-680
1784020239.000 | 12916.000 | SVA | 44 | 46 | 43 |  |  | ticks#row-547
1784020243.000 | 12920.000 | LAJ | 55 | 57 | 62 |  |  | ticks#row-702
1784020243.000 | 12920.000 | LAJ | 55 | 56 | 62 |  |  | ticks#row-708
1784020243.000 | 12920.000 | SVA | 43 | 46 | 43 |  |  | ticks#row-566
1784020243.000 | 12920.000 | SVA | 45 | 46 | 43 |  |  | ticks#row-573
1784020244.000 | 12921.000 | SVA | 45 | 47 | 43 |  |  | ticks#row-579
1784020254.000 | 12931.000 | LAJ | 54 | 56 | 62 |  |  | ticks#row-743
1784020254.000 | 12931.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@54 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-744 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020258.000 | 12935.000 | SVA | 44 | 47 | 43 |  |  | ticks#row-593
1784020273.000 | 12950.000 | SVA | 44 | 46 | 43 |  |  | ticks#row-601
1784020282.000 | 12959.000 | SVA | 44 | 45 | 43 |  |  | ticks#row-605
1784020286.000 | 12963.000 | SVA | 44 | 46 | 43 |  |  | ticks#row-612
1784020293.000 | 12970.000 | SVA | 44 | 47 | 43 |  |  | ticks#row-627
1784020300.000 | 12977.000 | LAJ | 54 | 55 | 62 |  |  | ticks#row-794
1784020436.000 | 13113.000 | SVA | 44 | 46 | 43 |  |  | ticks#row-651
1784020499.000 | 13176.000 | LAJ | 53 | 55 | 62 |  |  | ticks#row-883
1784020499.000 | 13176.000 | LAJ | 52 | 55 | 62 |  |  | ticks#row-889
1784020499.000 | 13176.000 | LAJ | 53 | 55 | 62 |  |  | ticks#row-891
1784020499.000 | 13176.000 | SVA | 44 | 47 | 43 |  |  | ticks#row-686
1784020499.000 | 13176.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@53 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-884 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020499.000 | 13176.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@52 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-890 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020499.000 | 13176.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@53 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-892 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020523.000 | 13200.000 | LAJ | 53 | 56 | 62 |  |  | ticks#row-915
1784020588.000 | 13265.000 | LAJ | 53 | 57 | 62 |  |  | ticks#row-1009
1784020596.000 | 13273.000 | LAJ | 53 | 56 | 62 |  |  | ticks#row-1017
1784020655.000 | 13332.000 | LAJ | 54 | 56 | 62 |  |  | ticks#row-1048
1784020655.000 | 13332.000 | LAJ | 55 | 56 | 62 |  |  | ticks#row-1049
1784020655.000 | 13332.000 | LAJ | 54 | 56 | 62 |  |  | ticks#row-1058
1784020655.000 | 13332.000 | SVA | 44 | 45 | 43 |  |  | ticks#row-799
1784020655.000 | 13332.000 | SVA | 44 | 46 | 43 |  |  | ticks#row-805
1784020655.000 | 13332.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@54 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-1049 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020655.000 | 13332.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@55 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-1050 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020655.000 | 13332.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@54 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-1059 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020656.000 | 13333.000 | LAJ | 54 | 57 | 62 |  |  | ticks#row-1064
1784020662.000 | 13339.000 | LAJ | 55 | 57 | 62 |  |  | ticks#row-1082
1784020662.000 | 13339.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@55 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-1083 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020664.000 | 13341.000 | LAJ | 55 | 58 | 62 |  |  | ticks#row-1093
1784020685.000 | 13362.000 | LAJ | 55 | 57 | 62 |  |  | ticks#row-1114
1784020690.000 | 13367.000 | LAJ | 54 | 57 | 62 |  |  | ticks#row-1131
1784020690.000 | 13367.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@54 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-1132 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020716.000 | 13393.000 | LAJ | 54 | 56 | 62 |  |  | ticks#row-1165
1784020716.000 | 13393.000 | SVA | 45 | 46 | 43 |  |  | ticks#row-866
1784020741.000 | 13418.000 | SVA | 45 | 47 | 43 |  |  | ticks#row-877
1784020772.000 | 13449.000 | LAJ | 54 | 55 | 62 |  |  | ticks#row-1189
1784020884.000 | 13561.000 | LAJ | 53 | 55 | 62 |  |  | ticks#row-1234
1784020884.000 | 13561.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@53 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-1235 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784020969.000 | 13646.000 | SVA | 45 | 46 | 43 |  |  | ticks#row-894
1784021019.000 | 13696.000 | SVA | 44 | 46 | 43 |  |  | ticks#row-912
1784021317.000 | 13994.000 | SVA | 45 | 46 | 43 |  |  | ticks#row-926
1784021400.000 | 14077.000 | SVA | 44 | 46 | 43 |  |  | ticks#row-944
1784023349.000 | 16026.000 | SVA | 45 | 46 | 43 |  |  | ticks#row-974
1784024118.000 | 16795.000 | LAJ | 52 | 55 | 62 |  |  | ticks#row-1601
1784024118.000 | 16795.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@52 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-1602 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784024362.000 | 17039.000 | LAJ | 53 | 55 | 62 |  |  | ticks#row-1635
1784024362.000 | 17039.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@53 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-1636 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784024857.000 | 17534.000 | LAJ | 53 | 54 | 62 |  |  | ticks#row-1692
1784028911.001 | 21588.001 | LAJ |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@48 (before 50) | FOUR_STORIES
1784028911.001 | 21588.001 | SVA |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@32 (before 35) | FOUR_STORIES
1784036624.368 | 29301.368 | LAJ |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@47 (before 48) | FOUR_STORIES
1784036624.368 | 29301.368 | SVA |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@37 (before 32) | FOUR_STORIES
1784036624.370 | 29301.370 | LAJ |  |  | 54 | 54c x 34.0 taker=yes trade_id=d2b2edfa-5b0e-5afc-6f15-a9dc9fe4d9fa |  | prints.jsonl
1784036624.370 | 29301.370 | LAJ |  |  | 55 | 55c x 400.0 taker=yes trade_id=c460dede-c539-5053-4ee5-b1798e4fc180 |  | prints.jsonl
1784036624.370 | 29301.370 | LAJ |  |  | 55 | 55c x 11.0 taker=yes trade_id=8c8d3f1f-7480-5fee-4f24-f5042430bf72 |  | prints.jsonl
1784036624.370 | 29301.370 | LAJ |  |  | 54 | 54c x 1500.0 taker=yes trade_id=752e6758-ea72-5ba9-515c-fc21c2edb9c0 |  | prints.jsonl
1784036624.370 | 29301.370 | LAJ |  |  | 55 | 55c x 257.47 taker=yes trade_id=405a3051-6aa6-5c93-7713-c2707ff9b770 |  | prints.jsonl
1784036624.370 | 29301.370 | LAJ |  |  | 55 | 55c x 9.0 taker=yes trade_id=26625491-8adf-5bb3-6104-6fd892e4e994 |  | prints.jsonl
1784036624.370 | 29301.370 | LAJ |  |  | 54 | 54c x 24.0 taker=yes trade_id=25f578e2-2621-5c77-7bca-5deba0d13eca |  | prints.jsonl
1784036624.370 | 29301.370 | LAJ |  |  | 55 | 55c x 25.0 taker=yes trade_id=1d3d7152-7c2d-528b-5765-5de4a988c6cc |  | prints.jsonl
1784036624.370 | 29301.370 | LAJ |  |  | 55 | 55c x 23.0 taker=yes trade_id=1ab18bbb-8e86-5d2c-66c2-3d81548ac707 |  | prints.jsonl
1784036629.002 | 29306.002 | LAJ |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@48 (before 47) | FOUR_STORIES
1784036629.002 | 29306.002 | SVA |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@32 (before 37) | FOUR_STORIES
1784036642.000 | 29319.000 | LAJ | 53 | 55 | 62 |  |  | ticks#row-3281
1784036642.000 | 29319.000 | LAJ | 53 | 55 | 54 |  |  | ticks#row-3285
1784036642.000 | 29319.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-3288
1784036643.000 | 29320.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3297
1784036643.000 | 29320.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@54 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-3298 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784037555.000 | 30232.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3465
1784037576.000 | 30253.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3473
1784037629.000 | 30306.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3480
1784037637.000 | 30314.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3481
1784037676.000 | 30353.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3485
1784037698.000 | 30375.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3490
1784037740.000 | 30417.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3495
1784037768.000 | 30445.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3499
1784037801.000 | 30478.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3501
1784037816.000 | 30493.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3503
1784037862.000 | 30539.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3509
1784037884.000 | 30561.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3515
1784037926.000 | 30603.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3518
1784037939.000 | 30616.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3521
1784037984.000 | 30661.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3524
1784037996.000 | 30673.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3526
1784038032.000 | 30709.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3532
1784038056.000 | 30733.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3535
1784038092.000 | 30769.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3541
1784038116.000 | 30793.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3547
1784038150.000 | 30827.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3551
1784038172.000 | 30849.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3555
1784038213.000 | 30890.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3562
1784038242.000 | 30919.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3567
1784038271.000 | 30948.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3575
1784038303.000 | 30980.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3581
1784038391.000 | 31068.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3609
1784038426.000 | 31103.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3616
1784038450.000 | 31127.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3619
1784038490.000 | 31167.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3626
1784038514.000 | 31191.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3629
1784038546.000 | 31223.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3632
1784038571.000 | 31248.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3635
1784038605.000 | 31282.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3640
1784038633.000 | 31310.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3647
1784038664.000 | 31341.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3653
1784038695.000 | 31372.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3659
1784038717.000 | 31394.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3663
1784038751.000 | 31428.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3670
1784038776.000 | 31453.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3676
1784038815.000 | 31492.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3682
1784038845.000 | 31522.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3688
1784038872.000 | 31549.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3691
1784038873.000 | 31550.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3693
1784039061.000 | 31738.000 | SVA | 45 | 47 | 43 |  |  | ticks#row-2414
1784039091.000 | 31768.000 | SVA | 45 | 46 | 43 |  |  | ticks#row-2419
1784039188.000 | 31865.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3737
1784039194.000 | 31871.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3738
1784039238.000 | 31915.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3741
1784039243.000 | 31920.000 | SVA | 45 | 46 | 46 |  |  | ticks#row-2436
1784039243.001 | 31920.001 | LAJ |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@47 (before 48) | FOUR_STORIES
1784039243.001 | 31920.001 | SVA |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@37 (before 32) | FOUR_STORIES
1784039243.522 | 31920.522 | SVA |  |  | 46 | 46c x 2.09 taker=yes trade_id=7a17e4a0-5a27-71e4-458b-28a11d7f08f9 |  | prints.jsonl
1784039256.000 | 31933.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3745
1784039353.000 | 32030.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3754
1784039377.000 | 32054.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3757
1784039422.000 | 32099.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3760
1784039436.000 | 32113.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3762
1784039592.000 | 32269.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3769
1784039628.000 | 32305.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3778
1784039714.000 | 32391.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3783
1784039714.000 | 32391.000 | LAJ |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@48 (before 47) | FOUR_STORIES
1784039714.000 | 32391.000 | SVA |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@35 (before 37) | FOUR_STORIES
1784039738.000 | 32415.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3786
1784039889.000 | 32566.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3801
1784039915.000 | 32592.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3804
1784039949.000 | 32626.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3813
1784039973.000 | 32650.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3816
1784040084.000 | 32761.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3820
1784040099.000 | 32776.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3825
1784040139.000 | 32816.000 | LAJ | 54 | 56 | 55 |  |  | ticks#row-3829
1784040160.000 | 32837.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-3831
1784040617.157 | 33294.157 | LAJ |  |  | 55 | 55c x 176.26 taker=yes trade_id=fd590b16-f1c8-4f29-5288-53f7cbef2348 |  | prints.jsonl
1784041336.938 | 34013.938 | LAJ |  |  | 55 | 55c x 46.0 taker=yes trade_id=c6212bf7-33e6-5688-665e-e40b3ef5d6c8 |  | prints.jsonl
1784041336.938 | 34013.938 | LAJ |  |  | 55 | 55c x 60.26 taker=yes trade_id=8330dcf3-424a-5a69-5265-cc62c66bcf9e |  | prints.jsonl
1784041336.938 | 34013.938 | LAJ |  |  | 55 | 55c x 70.0 taker=yes trade_id=43a6f6bc-5d25-5d74-5b67-3baaf59d6882 |  | prints.jsonl
1784042390.148 | 35067.148 | LAJ |  |  | 55 | 55c x 20.23 taker=yes trade_id=42382329-65c1-729a-0afd-3aa80264255f |  | prints.jsonl
1784042394.350 | 35071.350 | SVA |  |  | 45 | 45c x 5.0 taker=no trade_id=db95a67b-d0c6-4121-e667-a38b31fe770d |  | prints.jsonl
1784042394.350 | 35071.350 | SVA |  |  | 45 | 45c x 100.0 taker=no trade_id=a5e7fe3f-ea60-4f4e-d8fc-613567455ad6 |  | prints.jsonl
1784042394.350 | 35071.350 | SVA |  |  | 45 | 45c x 10.0 taker=no trade_id=6e9f3275-2305-44fb-e742-5bdfa76e7a02 |  | prints.jsonl
1784042394.350 | 35071.350 | SVA |  |  | 45 | 45c x 326.0 taker=no trade_id=013d5fa3-3749-40b6-f180-fc6b42c0e326 |  | prints.jsonl
1784042677.000 | 35354.000 | SVA | 44 | 45 | 45 |  |  | ticks#row-2556
1784043401.258 | 36078.258 | LAJ |  |  | 55 | 55c x 8.0 taker=yes trade_id=356411d8-972d-526a-1694-ec31aa0de4db |  | prints.jsonl
1784044914.764 | 37591.764 | SVA |  |  | 45 | 45c x 10.0 taker=yes trade_id=19b51a5b-e009-4338-e19b-7decad24f3ae |  | prints.jsonl
1784044934.000 | 37611.000 | SVA | 44 | 46 | 45 |  |  | ticks#row-2713
1784046290.725 | 38967.725 | LAJ |  |  | 55 | 55c x 61.0 taker=yes trade_id=3b81f16a-7bdd-6bf2-cb2c-5473cb37292f |  | prints.jsonl
1784046337.759 | 39014.759 | LAJ |  |  | 55 | 55c x 2.0 taker=yes trade_id=7d1742b3-55a1-5ace-30cb-0f7b340941df |  | prints.jsonl
1784046904.139 | 39581.139 | SVA |  |  | 46 | 46c x 22.72 taker=yes trade_id=262c3128-86be-4566-fb20-be6efc1e5a96 |  | prints.jsonl
1784046911.000 | 39588.000 | SVA | 44 | 46 | 46 |  |  | ticks#row-2822
1784047470.581 | 40147.581 | LAJ |  |  | 55 | 55c x 8.81 taker=yes trade_id=57af8f64-f051-44d2-e57b-30f502271257 |  | prints.jsonl
1784048290.000 | 40967.000 | SVA | 45 | 46 | 46 |  |  | ticks#row-2888
1784049442.390 | 42119.390 | SVA |  |  | 46 | 46c x 20.94 taker=yes trade_id=4be59c74-26e6-7b56-76fe-346d88e25a22 |  | prints.jsonl
1784049607.000 | 42284.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-4308
1784049607.000 | 42284.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-4310
1784049607.000 | 42284.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@53 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-4309 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784049607.000 | 42284.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@54 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-4311 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784049675.000 | 42352.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-4332
1784049675.000 | 42352.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@53 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-4333 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784049681.820 | 42358.820 | LAJ |  |  | 55 | 55c x 5.0 taker=yes trade_id=6f42d45a-2f8e-48cb-f50c-a7069cd33e4f |  | prints.jsonl
1784049813.000 | 42490.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-4350
1784049813.000 | 42490.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@54 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-4351 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784049953.000 | 42630.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-4397
1784049953.000 | 42630.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@53 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-4398 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784049994.000 | 42671.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-4408
1784049994.000 | 42671.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@54 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-4409 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784049995.000 | 42672.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-4413
1784049995.000 | 42672.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@53 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-4414 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784050014.000 | 42691.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-4430
1784050014.000 | 42691.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@54 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-4431 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784050148.000 | 42825.000 | SVA | 45 | 47 | 46 |  |  | ticks#row-3008
1784050148.000 | 42825.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-3009
1784050148.000 | 42825.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-3012
1784050148.138 | 42825.138 | SVA |  |  | 46 | 46c x 10.0 taker=yes trade_id=9d975a6e-4a6c-7857-50b5-42d414cbf969 |  | prints.jsonl
1784050148.138 | 42825.138 | SVA |  |  | 47 | 47c x 0.45 taker=yes trade_id=395faa67-2c27-775f-4149-02d90396acd9 |  | prints.jsonl
1784050216.591 | 42893.591 | LAJ |  |  | 55 | 55c x 1.76 taker=yes trade_id=db086ba6-a6c6-5b33-d2dd-72b963b34ebb |  | prints.jsonl
1784050691.000 | 43368.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-4470
1784050691.000 | 43368.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@53 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-4471 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784050693.000 | 43370.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-4490
1784050693.000 | 43370.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-4494
1784050695.000 | 43372.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-4518
1784050695.000 | 43372.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@54 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-4519 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784050739.000 | 43416.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-4540
1784050739.000 | 43416.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@53 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-4541 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784050815.000 | 43492.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-4547
1784050816.000 | 43493.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-4559
1784050816.000 | 43493.000 | LAJ | 54 | 55 | 55 |  |  | ticks#row-4569
1784050816.000 | 43493.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@54 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-4570 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784050817.000 | 43494.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-4584
1784050817.000 | 43494.000 | LAJ |  |  |  |  | REFLEX REPRICE_REST@53 receipt=KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-4585 reason=V54_UNDECIDED_CHAMPION_BYTE_EQUAL | FULL_DECISION_TRACE_5
1784050818.000 | 43495.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-4600
1784050973.063 | 43650.063 | LAJ |  |  | 54 | 54c x 44.85 taker=yes trade_id=16abd619-09aa-7b19-502f-1c8dda90dac9 |  | prints.jsonl
1784052471.000 | 45148.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-4738
1784052471.000 | 45148.000 | SVA | 46 | 47 | 46 |  |  | ticks#row-3212
1784052707.741 | 45384.741 | SVA |  |  | 48 | 48c x 29.0 taker=yes trade_id=ddaa0876-739a-5206-64f0-c67ce5214974 |  | prints.jsonl
1784052707.741 | 45384.741 | SVA |  |  | 47 | 47c x 10.0 taker=yes trade_id=b2bb4e7c-8569-5cbe-470b-2fb7c5c08769 |  | prints.jsonl
1784052707.741 | 45384.741 | SVA |  |  | 49 | 49c x 23.36 taker=yes trade_id=1867e6ee-ef00-50ae-7077-590d01e11a4f |  | prints.jsonl
1784052714.000 | 45391.000 | SVA | 46 | 48 | 46 |  |  | ticks#row-3213
1784052714.000 | 45391.000 | SVA | 46 | 49 | 47 |  |  | ticks#row-3214
1784052714.000 | 45391.000 | SVA | 46 | 49 | 49 |  |  | ticks#row-3216
1784052714.000 | 45391.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3219
1784052714.000 | 45391.000 | LAJ |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@49 (before 48) | FOUR_STORIES
1784052714.000 | 45391.000 | SVA |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@34 (before 35) | FOUR_STORIES
1784052715.000 | 45392.000 | SVA | 48 | 49 | 49 |  |  | ticks#row-3230
1784052830.356 | 45507.356 | LAJ |  |  |  |  | FILL (reflex/champion) 53c credited | MARKET_EVENT_LEDGER_5
1784052830.356 | 45507.356 | LAJ |  |  | 53 | 53c x 1.0 taker=no trade_id=8c5eeb51-910b-6b5f-ae42-307d486841f4 |  | prints.jsonl
1784052831.000 | 45508.000 | LAJ | 53 | 54 | 53 |  |  | ticks#row-4775
1784052893.000 | 45570.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-4785
1784052893.780 | 45570.780 | LAJ |  |  | 54 | 54c x 7.0 taker=yes trade_id=8f62ac39-dd22-5995-e488-472fbfe80c8d |  | prints.jsonl
1784053049.355 | 45726.355 | LAJ |  |  | 54 | 54c x 0.89 taker=yes trade_id=347cd4a9-594e-5015-a625-b24d5e10eeb1 |  | prints.jsonl
1784053181.914 | 45858.914 | SVA |  |  | 49 | 49c x 1.97 taker=yes trade_id=e32f98b8-2347-4925-5f41-85a84458f5ac |  | prints.jsonl
1784053308.883 | 45985.883 | LAJ |  |  | 54 | 54c x 35.88 taker=yes trade_id=9bef4f54-6c46-432d-0aa2-3eb05f0d11fd |  | prints.jsonl
1784053432.584 | 46109.584 | SVA |  |  | 48 | 48c x 1.86 taker=no trade_id=776d26c5-a98a-5e71-89f6-a1418db1f1f6 |  | prints.jsonl
1784053483.000 | 46160.000 | SVA | 48 | 49 | 48 |  |  | ticks#row-3262
1784053484.058 | 46161.058 | SVA |  |  | 49 | 49c x 9.85 taker=yes trade_id=6c041ef5-471f-7629-b46e-347e39120720 |  | prints.jsonl
1784053532.000 | 46209.000 | SVA | 48 | 49 | 49 |  |  | ticks#row-3264
1784053533.839 | 46210.839 | SVA |  |  | 49 | 49c x 3.94 taker=yes trade_id=e5d83f6a-935f-5bad-06f2-43d69b1e9b78 |  | prints.jsonl
1784053789.341 | 46466.341 | SVA |  |  | 49 | 49c x 29.55 taker=yes trade_id=1fbf4212-9a9b-60f5-d5d2-51844f7c2234 |  | prints.jsonl
1784053884.338 | 46561.338 | SVA |  |  | 49 | 49c x 1.97 taker=yes trade_id=b5de5684-82f3-47d1-5c5c-40b3a3edc200 |  | prints.jsonl
1784054351.679 | 47028.679 | LAJ |  |  | 54 | 54c x 45.0 taker=yes trade_id=c0670c5a-a56a-5f71-2717-2075d7fdc355 |  | prints.jsonl
1784054477.613 | 47154.613 | LAJ |  |  | 53 | 53c x 2.05 taker=no trade_id=41e29560-595b-58df-f51e-a3332bd8e568 |  | prints.jsonl
1784054479.000 | 47156.000 | LAJ | 53 | 54 | 53 |  |  | ticks#row-4930
1784054945.165 | 47622.165 | LAJ |  |  | 54 | 54c x 18.0 taker=yes trade_id=bfcb18aa-9a92-5c35-b3fa-5c24213cb3b9 |  | prints.jsonl
1784054945.716 | 47622.716 | SVA |  |  | 49 | 49c x 9.85 taker=yes trade_id=5c224dbe-78c3-6291-c61b-595bc7622e64 |  | prints.jsonl
1784054954.000 | 47631.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-4971
1784055102.322 | 47779.322 | SVA |  |  | 49 | 49c x 9.85 taker=yes trade_id=1c7f9247-c83b-453d-276c-2f12251dffd8 |  | prints.jsonl
1784055160.532 | 47837.532 | SVA |  |  | 49 | 49c x 2.0 taker=yes trade_id=8533a410-3a7f-6a9d-f03b-00c00a6b5634 |  | prints.jsonl
1784055238.526 | 47915.526 | LAJ |  |  | 54 | 54c x 71.76 taker=yes trade_id=38871412-f5f2-7761-6d19-0bf63806f2f1 |  | prints.jsonl
1784055368.000 | 48045.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3315
1784055402.000 | 48079.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3325
1784055406.000 | 48083.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3342
1784055406.000 | 48083.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3351
1784055423.000 | 48100.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3398
1784055423.000 | 48100.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3413
1784055423.000 | 48100.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3418
1784055423.000 | 48100.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3420
1784055430.000 | 48107.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3428
1784055430.000 | 48107.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3435
1784055430.000 | 48107.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3439
1784055430.000 | 48107.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3440
1784055435.000 | 48112.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3448
1784055435.000 | 48112.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3455
1784055435.000 | 48112.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3459
1784055435.000 | 48112.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3460
1784055437.000 | 48114.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3468
1784055437.000 | 48114.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3473
1784055450.000 | 48127.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3537
1784055450.000 | 48127.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3540
1784055450.000 | 48127.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3551
1784055450.000 | 48127.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3558
1784055454.000 | 48131.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3572
1784055454.000 | 48131.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3574
1784055456.000 | 48133.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3583
1784055457.000 | 48134.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3596
1784055472.000 | 48149.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3621
1784055472.000 | 48149.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3623
1784055472.000 | 48149.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3653
1784055472.000 | 48149.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3654
1784055477.000 | 48154.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3659
1784055477.000 | 48154.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3668
1784055477.000 | 48154.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3673
1784055477.000 | 48154.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3674
1784055489.000 | 48166.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3704
1784055489.000 | 48166.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3711
1784055495.000 | 48172.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3725
1784055495.000 | 48172.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3735
1784055495.000 | 48172.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3742
1784055495.000 | 48172.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3751
1784055496.000 | 48173.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3761
1784055496.000 | 48173.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3765
1784055496.000 | 48173.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3768
1784055496.000 | 48173.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3769
1784055499.000 | 48176.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3783
1784055499.000 | 48176.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3789
1784055499.000 | 48176.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3793
1784055499.000 | 48176.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3803
1784055500.000 | 48177.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3811
1784055500.000 | 48177.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3812
1784055502.000 | 48179.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3823
1784055502.000 | 48179.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3831
1784055502.000 | 48179.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3838
1784055502.000 | 48179.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3845
1784055569.270 | 48246.270 | LAJ |  |  | 54 | 54c x 17.0 taker=yes trade_id=7122a280-e6fa-4c3d-093b-5669c31ffbd5 |  | prints.jsonl
1784055578.000 | 48255.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3902
1784055578.000 | 48255.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3910
1784055578.000 | 48255.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3913
1784055578.000 | 48255.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3914
1784055581.000 | 48258.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3940
1784055581.000 | 48258.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3944
1784055593.000 | 48270.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-3958
1784055593.000 | 48270.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-3983
1784055606.000 | 48283.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4032
1784055606.000 | 48283.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4040
1784055606.000 | 48283.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4044
1784055606.000 | 48283.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4046
1784055607.000 | 48284.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4052
1784055607.000 | 48284.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4059
1784055612.000 | 48289.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4074
1784055612.000 | 48289.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4085
1784055612.000 | 48289.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4088
1784055612.000 | 48289.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4089
1784055622.000 | 48299.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4107
1784055622.000 | 48299.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4121
1784055622.000 | 48299.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4123
1784055622.000 | 48299.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4132
1784055622.000 | 48299.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4135
1784055622.000 | 48299.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4143
1784055622.000 | 48299.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4146
1784055622.000 | 48299.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4147
1784055624.000 | 48301.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4162
1784055624.000 | 48301.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4165
1784055630.000 | 48307.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4199
1784055630.000 | 48307.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4203
1784055631.000 | 48308.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4214
1784055631.000 | 48308.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4224
1784055652.000 | 48329.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4285
1784055652.000 | 48329.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4299
1784055671.000 | 48348.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4366
1784055671.000 | 48348.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4385
1784055675.000 | 48352.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4397
1784055676.000 | 48353.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4398
1784055688.000 | 48365.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4423
1784055688.000 | 48365.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4425
1784055690.000 | 48367.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4429
1784055690.000 | 48367.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4437
1784055690.000 | 48367.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4442
1784055690.000 | 48367.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4445
1784055691.000 | 48368.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4449
1784055691.000 | 48368.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4455
1784055692.000 | 48369.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4463
1784055692.000 | 48369.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4469
1784055695.000 | 48372.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4523
1784055695.000 | 48372.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4528
1784055695.000 | 48372.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4536
1784055695.000 | 48372.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4540
1784055700.000 | 48377.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4555
1784055700.000 | 48377.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4563
1784055700.000 | 48377.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4569
1784055700.000 | 48377.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4574
1784055700.000 | 48377.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4587
1784055700.000 | 48377.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4590
1784055700.000 | 48377.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4593
1784055700.000 | 48377.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4594
1784055703.000 | 48380.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4604
1784055703.000 | 48380.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4605
1784055705.000 | 48382.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4613
1784055705.000 | 48382.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4616
1784055705.000 | 48382.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4621
1784055705.000 | 48382.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4622
1784055713.000 | 48390.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4688
1784055713.000 | 48390.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4701
1784055715.000 | 48392.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4713
1784055715.000 | 48392.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4718
1784055716.000 | 48393.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4730
1784055716.000 | 48393.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4735
1784055724.000 | 48401.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4750
1784055724.000 | 48401.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4758
1784055724.000 | 48401.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4763
1784055724.000 | 48401.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4766
1784055725.000 | 48402.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4796
1784055725.000 | 48402.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4818
1784055725.000 | 48402.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4821
1784055725.000 | 48402.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4837
1784055725.000 | 48402.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4840
1784055725.000 | 48402.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4843
1784055733.000 | 48410.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4916
1784055733.000 | 48410.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4924
1784055733.000 | 48410.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4928
1784055733.000 | 48410.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4933
1784055733.000 | 48410.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4937
1784055733.000 | 48410.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4943
1784055735.000 | 48412.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4964
1784055735.000 | 48412.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4971
1784055735.000 | 48412.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4975
1784055735.000 | 48412.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4982
1784055736.000 | 48413.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4985
1784055736.000 | 48413.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4988
1784055736.000 | 48413.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-4993
1784055736.000 | 48413.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-4995
1784055738.000 | 48415.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5002
1784055738.000 | 48415.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5012
1784055738.000 | 48415.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5017
1784055738.000 | 48415.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5019
1784055743.000 | 48420.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5042
1784055743.000 | 48420.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5043
1784055751.000 | 48428.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5108
1784055752.000 | 48429.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5125
1784055753.000 | 48430.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5135
1784055753.000 | 48430.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5136
1784055753.000 | 48430.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5139
1784055753.000 | 48430.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5146
1784055753.000 | 48430.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5149
1784055753.000 | 48430.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5155
1784055758.000 | 48435.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5192
1784055758.000 | 48435.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5204
1784055758.000 | 48435.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5207
1784055758.000 | 48435.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5215
1784055761.000 | 48438.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5222
1784055761.000 | 48438.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5231
1784055761.000 | 48438.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5236
1784055761.000 | 48438.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5240
1784055761.000 | 48438.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5243
1784055762.000 | 48439.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5262
1784055762.000 | 48439.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5265
1784055762.000 | 48439.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5273
1784055763.000 | 48440.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5290
1784055763.000 | 48440.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5292
1784055774.000 | 48451.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5356
1784055774.000 | 48451.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5359
1784055774.000 | 48451.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5371
1784055774.000 | 48451.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5374
1784055774.000 | 48451.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5376
1784055774.000 | 48451.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5387
1784055774.000 | 48451.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5389
1784055774.000 | 48451.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5396
1784055777.000 | 48454.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5403
1784055777.000 | 48454.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5421
1784055777.000 | 48454.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5424
1784055777.000 | 48454.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5427
1784055777.000 | 48454.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5430
1784055777.000 | 48454.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5450
1784055779.000 | 48456.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5459
1784055779.000 | 48456.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5463
1784055780.000 | 48457.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5474
1784055780.000 | 48457.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5478
1784055785.000 | 48462.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5526
1784055785.000 | 48462.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5535
1784055785.000 | 48462.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5540
1784055785.000 | 48462.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5543
1784055787.000 | 48464.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5553
1784055787.000 | 48464.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5559
1784055787.000 | 48464.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5564
1784055787.000 | 48464.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5566
1784055787.000 | 48464.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5572
1784055787.000 | 48464.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5574
1784055788.000 | 48465.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5582
1784055788.000 | 48465.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5589
1784055789.000 | 48466.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5602
1784055789.000 | 48466.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5614
1784055791.000 | 48468.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5623
1784055791.000 | 48468.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5630
1784055791.000 | 48468.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5636
1784055791.000 | 48468.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5637
1784055796.000 | 48473.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5680
1784055796.000 | 48473.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5686
1784055796.000 | 48473.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5694
1784055796.000 | 48473.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5698
1784055801.000 | 48478.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5719
1784055801.000 | 48478.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5722
1784055805.000 | 48482.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5769
1784055805.000 | 48482.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5770
1784055816.000 | 48493.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5856
1784055816.000 | 48493.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5874
1784055820.000 | 48497.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5883
1784055820.000 | 48497.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5892
1784055820.000 | 48497.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5915
1784055820.000 | 48497.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5922
1784055820.000 | 48497.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5929
1784055820.000 | 48497.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5941
1784055821.000 | 48498.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5949
1784055821.000 | 48498.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5961
1784055823.000 | 48500.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-5970
1784055823.000 | 48500.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-5971
1784055828.000 | 48505.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6010
1784055828.000 | 48505.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6017
1784055828.000 | 48505.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6022
1784055828.000 | 48505.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6023
1784055831.000 | 48508.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6029
1784055831.000 | 48508.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6045
1784055832.000 | 48509.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6049
1784055832.000 | 48509.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6050
1784055847.000 | 48524.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6188
1784055847.000 | 48524.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6192
1784055847.000 | 48524.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6196
1784055847.000 | 48524.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6204
1784055847.000 | 48524.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6206
1784055847.000 | 48524.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6209
1784055849.000 | 48526.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6222
1784055849.000 | 48526.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6244
1784055852.000 | 48529.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6269
1784055852.000 | 48529.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6271
1784055854.000 | 48531.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6278
1784055854.000 | 48531.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6286
1784055854.000 | 48531.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6292
1784055854.000 | 48531.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6294
1784055857.000 | 48534.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6302
1784055857.000 | 48534.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6309
1784055857.000 | 48534.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6320
1784055857.000 | 48534.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6321
1784055857.000 | 48534.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6332
1784055857.000 | 48534.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6334
1784055860.000 | 48537.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6346
1784055860.000 | 48537.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6384
1784055863.000 | 48540.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6393
1784055863.000 | 48540.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6401
1784055863.000 | 48540.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6416
1784055863.000 | 48540.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6421
1784055863.000 | 48540.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6431
1784055863.000 | 48540.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6433
1784055863.000 | 48540.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6435
1784055863.000 | 48540.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6438
1784055865.147 | 48542.147 | LAJ |  |  | 54 | 54c x 12.0 taker=yes trade_id=bda2c419-1102-6939-ac97-bcbcf48d4849 |  | prints.jsonl
1784055866.000 | 48543.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6452
1784055866.000 | 48543.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6455
1784055866.000 | 48543.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6459
1784055866.000 | 48543.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6460
1784055872.000 | 48549.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6524
1784055872.000 | 48549.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6525
1784055872.000 | 48549.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6532
1784055872.000 | 48549.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6535
1784055876.000 | 48553.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6575
1784055876.000 | 48553.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6576
1784055880.000 | 48557.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6590
1784055881.000 | 48558.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6599
1784055881.000 | 48558.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6605
1784055881.000 | 48558.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6606
1784055887.000 | 48564.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6624
1784055887.000 | 48564.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6636
1784055887.000 | 48564.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6639
1784055887.000 | 48564.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6640
1784055890.000 | 48567.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6644
1784055890.000 | 48567.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6655
1784055890.000 | 48567.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6657
1784055890.000 | 48567.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6662
1784055890.000 | 48567.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6667
1784055890.000 | 48567.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6668
1784055892.000 | 48569.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6675
1784055892.000 | 48569.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6690
1784055892.000 | 48569.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6699
1784055893.000 | 48570.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6710
1784055895.000 | 48572.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6749
1784055895.000 | 48572.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6761
1784055897.000 | 48574.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6775
1784055897.000 | 48574.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6792
1784055899.000 | 48576.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6821
1784055899.000 | 48576.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6825
1784055899.000 | 48576.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6826
1784055899.000 | 48576.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6828
1784055899.000 | 48576.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-6831
1784055899.000 | 48576.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-6832
1784056265.730 | 48942.730 | LAJ |  |  | 53 | 53c x 10.0 taker=no trade_id=221c75ec-e04b-7ff3-4f2f-013037704534 |  | prints.jsonl
1784056359.827 | 49036.827 | LAJ |  |  | 54 | 54c x 17.0 taker=yes trade_id=83e50b07-f557-6102-0dd9-6eace3470403 |  | prints.jsonl
1784056549.000 | 49226.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-7784
1784056549.000 | 49226.000 | SVA | 48 | 49 | 49 |  |  | ticks#row-7788
1784056549.492 | 49226.492 | SVA |  |  | 48 | 48c x 10.0 taker=yes trade_id=8cf65117-f1aa-6bc2-e13f-2f0e7f135917 |  | prints.jsonl
1784056549.492 | 49226.492 | SVA |  |  | 49 | 49c x 3.34 taker=yes trade_id=35d9ddca-dfa3-6741-fa1e-c9bc101f8a74 |  | prints.jsonl
1784056821.343 | 49498.343 | SVA |  |  | 48 | 48c x 9.85 taker=no trade_id=f3fe75e2-1c24-742b-ae81-f030ee7413b5 |  | prints.jsonl
1784056847.000 | 49524.000 | SVA | 48 | 49 | 48 |  |  | ticks#row-7798
1784057122.344 | 49799.344 | LAJ |  |  | 54 | 54c x 26.91 taker=yes trade_id=99032ac6-47e7-447a-0737-31b411eadbf7 |  | prints.jsonl
1784057369.000 | 50046.000 | SVA | 46 | 49 | 48 |  |  | ticks#row-7808
1784057405.034 | 50082.034 | SVA |  |  | 49 | 49c x 29.55 taker=yes trade_id=9b26ac09-ed57-5705-2380-e383214ae4a8 |  | prints.jsonl
1784057472.000 | 50149.000 | SVA | 46 | 49 | 49 |  |  | ticks#row-7814
1784057496.000 | 50173.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-7829
1784057620.549 | 50297.549 | LAJ |  |  | 54 | 54c x 17.94 taker=yes trade_id=39419c15-37ef-7f72-cf3e-f078d7f9ce6b |  | prints.jsonl
1784057654.568 | 50331.568 | LAJ |  |  | 54 | 54c x 26.91 taker=yes trade_id=5888099f-58b3-5a3e-671b-5b14fce49593 |  | prints.jsonl
1784057826.742 | 50503.742 | LAJ |  |  | 54 | 54c x 521.02 taker=yes trade_id=bda8e553-45bb-5226-3d5a-ad4f936f77ab |  | prints.jsonl
1784057826.742 | 50503.742 | LAJ |  |  | 54 | 54c x 17.2 taker=yes trade_id=9a63985c-ba6a-516d-3f39-c2c89672feb4 |  | prints.jsonl
1784057844.199 | 50521.199 | SVA |  |  | 49 | 49c x 98.52 taker=yes trade_id=c44df234-210b-6cc5-5f4f-541ac4f15670 |  | prints.jsonl
1784057850.933 | 50527.933 | LAJ |  |  | 54 | 54c x 89.7 taker=yes trade_id=940c75eb-971e-719d-ff3a-fdf12dc74c14 |  | prints.jsonl
1784057881.000 | 50558.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-7868
1784057940.585 | 50617.585 | LAJ |  |  | 54 | 54c x 75.35 taker=yes trade_id=eecc4ad1-c97e-5b41-84e6-9665f489c464 |  | prints.jsonl
1784058214.645 | 50891.645 | SVA |  |  | 48 | 48c x 40.2 taker=yes trade_id=40eaa0fd-4490-7dcc-fbb6-36facb7122c2 |  | prints.jsonl
1784058283.000 | 50960.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-7885
1784058287.852 | 50964.852 | LAJ |  |  | 54 | 54c x 35.88 taker=yes trade_id=7fe73aea-4b12-69ad-f250-bda595019584 |  | prints.jsonl
1784058461.088 | 51138.088 | SVA |  |  | 48 | 48c x 19.0 taker=yes trade_id=319734fa-8b54-7878-75c1-dba7c775d04a |  | prints.jsonl
1784058478.280 | 51155.280 | LAJ |  |  | 54 | 54c x 350.0 taker=yes trade_id=fc726a43-53f2-7631-1ed5-7cbdc8313e60 |  | prints.jsonl
1784058522.908 | 51199.908 | SVA |  |  | 48 | 48c x 100.5 taker=yes trade_id=de3aa832-ee8c-4ca4-4467-fa99c1058022 |  | prints.jsonl
1784058589.866 | 51266.866 | SVA |  |  | 48 | 48c x 30.0 taker=yes trade_id=44c8a15b-3874-7c9c-be8b-a41bf904550a |  | prints.jsonl
1784058663.452 | 51340.452 | LAJ |  |  | 54 | 54c x 44.0 taker=yes trade_id=2a916ad9-cf50-7658-a428-ed641ae685f5 |  | prints.jsonl
1784058769.910 | 51446.910 | SVA |  |  | 48 | 48c x 339.71 taker=yes trade_id=9c3bed3f-38ac-4370-6650-386ccf08318a |  | prints.jsonl
1784059165.000 | 51842.000 | SVA | 47 | 49 | 48 |  |  | ticks#row-7929
1784059165.000 | 51842.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-7931
1784059165.000 | 51842.000 | SVA | 48 | 49 | 49 |  |  | ticks#row-7935
1784059165.492 | 51842.492 | SVA |  |  | 49 | 49c x 49.3 taker=yes trade_id=235a910b-97e3-587d-39d2-8e2dc8057cac |  | prints.jsonl
1784059165.492 | 51842.492 | SVA |  |  | 48 | 48c x 10.0 taker=yes trade_id=110e9044-bbe7-5ae9-392b-164ecc25495b |  | prints.jsonl
1784059349.534 | 52026.534 | SVA |  |  | 49 | 49c x 16.15 taker=yes trade_id=f883a9c0-d05f-4a61-b09c-b55c822283e0 |  | prints.jsonl
1784059596.401 | 52273.401 | LAJ |  |  | 54 | 54c x 56.0 taker=yes trade_id=4b1b7056-d8d8-7858-b47d-352f691a71d5 |  | prints.jsonl
1784059596.401 | 52273.401 | LAJ |  |  | 54 | 54c x 74.0 taker=yes trade_id=37aaaedd-8923-782b-a39a-05b734f3261c |  | prints.jsonl
1784059613.000 | 52290.000 | LAJ | 51 | 54 | 54 |  |  | ticks#row-6963
1784059613.000 | 52290.000 | LAJ | 51 | 53 | 54 |  |  | ticks#row-6964
1784059613.000 | 52290.000 | LAJ | 51 | 53 | 53 |  |  | ticks#row-6965
1784059613.618 | 52290.618 | LAJ |  |  | 53 | 53c x 5.95 taker=no trade_id=9bf97090-1bdf-515f-a444-1bc67c9a2ffc |  | prints.jsonl
1784059809.905 | 52486.905 | LAJ |  |  | 53 | 53c x 0.03 taker=yes trade_id=c39c15c9-0e8c-40fd-76a4-b2e4aade8fa0 |  | prints.jsonl
1784060123.219 | 52800.219 | LAJ |  |  | 51 | 51c x 100.0 taker=no trade_id=7fb0df36-2082-795a-5cb6-f311235289d1 |  | prints.jsonl
1784060123.219 | 52800.219 | LAJ |  |  |  |  | FLOOR PRINT 51c (lawful pre-bell minimum) | REPRODUCTION_AUDIT_d521f9dd
1784060154.000 | 52831.000 | LAJ | 51 | 53 | 51 |  |  | ticks#row-7027
1784060205.000 | 52882.000 | LAJ | 51 | 53 | 53 |  |  | ticks#row-7070
1784060205.341 | 52882.341 | LAJ |  |  | 53 | 53c x 45.66 taker=yes trade_id=b1014e0a-3ce3-4b85-55b5-6a064e875626 |  | prints.jsonl
1784060264.000 | 52941.000 | LAJ | 52 | 53 | 53 |  |  | ticks#row-7109
1784060264.754 | 52941.754 | LAJ |  |  | 53 | 53c x 142.0 taker=yes trade_id=61f02ecc-4517-54fd-5b38-461b31e9724e |  | prints.jsonl
1784060317.000 | 52994.000 | SVA | 46 | 49 | 49 |  |  | ticks#row-8075
1784060324.000 | 53001.000 | SVA | 46 | 48 | 49 |  |  | ticks#row-8085
1784060451.000 | 53128.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-8102
1784060451.000 | 53128.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-8103
1784060451.081 | 53128.081 | SVA |  |  | 48 | 48c x 50.0 taker=yes trade_id=21b895ce-d8de-550c-e613-bc6aa23cb4a0 |  | prints.jsonl
1784060801.451 | 53478.451 | LAJ |  |  | 53 | 53c x 16.0 taker=yes trade_id=4ed92b6e-cb8b-4e65-d288-1a416533703a |  | prints.jsonl
1784060956.369 | 53633.369 | LAJ |  |  | 53 | 53c x 137.0 taker=yes trade_id=d0ea7c56-3e6f-7069-903d-1f7e755e7096 |  | prints.jsonl
1784061209.349 | 53886.349 | LAJ |  |  | 53 | 53c x 8.0 taker=yes trade_id=f3d34fc9-3653-6985-861c-92f7bdb4462e |  | prints.jsonl
1784061260.024 | 53937.024 | LAJ |  |  | 53 | 53c x 3.0 taker=yes trade_id=fe6cd817-d79b-4469-0aa3-ce6aa845e0da |  | prints.jsonl
1784061277.085 | 53954.085 | LAJ |  |  | 53 | 53c x 63.93 taker=yes trade_id=8699b441-6b57-4115-cada-fe7d2374f432 |  | prints.jsonl
1784061282.239 | 53959.239 | LAJ |  |  | 53 | 53c x 8.41 taker=yes trade_id=d202ad7a-b717-55f1-7b5c-baf269194b7a |  | prints.jsonl
1784061282.239 | 53959.239 | LAJ |  |  | 53 | 53c x 28.12 taker=yes trade_id=6e6cba3e-b2b0-5f7f-4a31-380547fd8c3e |  | prints.jsonl
1784061309.000 | 53986.000 | LAJ |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@47 (before 49) | FOUR_STORIES
1784061309.000 | 53986.000 | SVA |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@36 (before 34) | FOUR_STORIES
1784061324.886 | 54001.886 | LAJ |  |  | 53 | 53c x 18.26 taker=yes trade_id=2b234315-6240-4ad7-462a-18ea7b8135da |  | prints.jsonl
1784061559.458 | 54236.458 | SVA |  |  | 48 | 48c x 10.0 taker=yes trade_id=a9c49576-e46e-791c-b87a-54dc12f43a50 |  | prints.jsonl
1784061791.000 | 54468.000 | LAJ | 52 | 53 | 54 |  |  | ticks#row-7453
1784061791.296 | 54468.296 | LAJ |  |  | 53 | 53c x 100.0 taker=yes trade_id=c2e7255d-2f9c-7094-c62b-f72addbccff7 |  | prints.jsonl
1784061791.296 | 54468.296 | LAJ |  |  | 53 | 53c x 100.0 taker=yes trade_id=bdab20a7-9f40-7b76-dd2c-0001989dea5d |  | prints.jsonl
1784061791.296 | 54468.296 | LAJ |  |  | 53 | 53c x 38.0 taker=yes trade_id=7e22c185-0ac8-7440-c33a-9899dcd232dd |  | prints.jsonl
1784061791.296 | 54468.296 | LAJ |  |  | 53 | 53c x 3.62 taker=yes trade_id=790422f3-5634-79ef-c0e8-d412e4dc757a |  | prints.jsonl
1784061791.296 | 54468.296 | LAJ |  |  | 54 | 54c x 31.79 taker=yes trade_id=289d6142-2c5f-736c-dcc8-e6512bb0f9e7 |  | prints.jsonl
1784061838.254 | 54515.254 | SVA |  |  | 48 | 48c x 20.1 taker=yes trade_id=efa6fc12-4e2e-645c-c099-b48e3af4d3d8 |  | prints.jsonl
1784062032.000 | 54709.000 | LAJ | 53 | 53 | 54 |  |  | ticks#row-7462
1784062185.205 | 54862.205 | SVA |  |  | 48 | 48c x 1.98 taker=yes trade_id=67ca198c-1f96-6c5c-24b8-9e1b872c0060 |  | prints.jsonl
1784062373.502 | 55050.502 | LAJ |  |  | 54 | 54c x 134.55 taker=yes trade_id=e128238c-958b-63e8-24f0-b353954f2e97 |  | prints.jsonl
1784062548.612 | 55225.612 | LAJ |  |  | 54 | 54c x 0.08 taker=yes trade_id=69dec8bc-b104-4633-25a2-e2f3848c39d9 |  | prints.jsonl
1784062744.194 | 55421.194 | LAJ |  |  | 54 | 54c x 14.0 taker=yes trade_id=f0866bc6-3fd8-5dbf-d9a1-7b8202bb4e45 |  | prints.jsonl
1784062823.239 | 55500.239 | SVA |  |  | 48 | 48c x 58.5 taker=yes trade_id=b0ed48d9-681a-58b8-78e0-9319fed349c4 |  | prints.jsonl
1784062881.951 | 55558.951 | LAJ |  |  | 54 | 54c x 301.4 taker=yes trade_id=c0c28eca-d388-7367-8635-e18229e8886d |  | prints.jsonl
1784063206.941 | 55883.941 | LAJ |  |  | 54 | 54c x 379.0 taker=yes trade_id=f06486c2-8022-68b3-d082-b0d15f7e4152 |  | prints.jsonl
1784063206.941 | 55883.941 | LAJ |  |  | 54 | 54c x 317.83 taker=yes trade_id=9e36798a-ca78-6b2f-df31-dd6c1c6fdf01 |  | prints.jsonl
1784063206.941 | 55883.941 | LAJ |  |  | 54 | 54c x 4.17 taker=yes trade_id=951df49a-55c3-6f94-fb9d-b62cead44ac8 |  | prints.jsonl
1784063298.775 | 55975.775 | LAJ |  |  | 54 | 54c x 23.99 taker=yes trade_id=a0a68a1d-aa8a-4fe0-9e88-00fe63e248a6 |  | prints.jsonl
1784063298.775 | 55975.775 | LAJ |  |  | 54 | 54c x 29.83 taker=yes trade_id=9672fd82-1687-488c-9366-e8144567353c |  | prints.jsonl
1784063309.648 | 55986.648 | LAJ |  |  | 54 | 54c x 10.53 taker=yes trade_id=8d56afad-732a-4b4c-81d2-f941054b32e6 |  | prints.jsonl
1784063324.000 | 56001.000 | LAJ | 53 | 53 | 53 |  |  | ticks#row-7911
1784063324.384 | 56001.384 | LAJ |  |  | 53 | 53c x 14.0 taker=no trade_id=6cea82d7-72c1-61bc-c0e8-793cd9ff3d8a |  | prints.jsonl
1784063455.651 | 56132.651 | SVA |  |  | 48 | 48c x 4.63 taker=yes trade_id=70b85606-8ea0-5c0f-3a01-016524c2fef2 |  | prints.jsonl
1784063455.651 | 56132.651 | SVA |  |  | 48 | 48c x 5.42 taker=yes trade_id=307a7e56-a04e-561c-31a7-0bb58af04eb0 |  | prints.jsonl
1784063668.200 | 56345.200 | LAJ |  |  | 54 | 54c x 11.0 taker=yes trade_id=a0b087ad-93ca-7eb4-7394-abf65aeff58e |  | prints.jsonl
1784063677.000 | 56354.000 | LAJ | 53 | 53 | 54 |  |  | ticks#row-7923
1784063677.678 | 56354.678 | SVA |  |  | 48 | 48c x 29.0 taker=yes trade_id=cee69c81-48c6-5c03-e8e2-3407202472f9 |  | prints.jsonl
1784063677.678 | 56354.678 | SVA |  |  | 48 | 48c x 43.0 taker=yes trade_id=b5cce8d0-67e9-5c8a-ca38-ab6f5cbf456a |  | prints.jsonl
1784063677.678 | 56354.678 | SVA |  |  | 48 | 48c x 82.63 taker=yes trade_id=92e9c2c6-7849-5527-dcfd-63b675081556 |  | prints.jsonl
1784063677.678 | 56354.678 | SVA |  |  | 48 | 48c x 107.0 taker=yes trade_id=64c9eefe-4a31-5f73-ec3c-ae5810485799 |  | prints.jsonl
1784063677.678 | 56354.678 | SVA |  |  | 48 | 48c x 5.37 taker=yes trade_id=5fdd32be-8160-5d6f-ff55-74d8b524ba96 |  | prints.jsonl
1784063677.678 | 56354.678 | SVA |  |  | 48 | 48c x 24.0 taker=yes trade_id=3030514f-349b-53b7-c5ac-3aec6d5d5d7e |  | prints.jsonl
1784063677.678 | 56354.678 | SVA |  |  | 48 | 48c x 59.0 taker=yes trade_id=0d3b6682-885e-586f-f98b-68cbca2ccea1 |  | prints.jsonl
1784063690.550 | 56367.550 | SVA |  |  | 48 | 48c x 4.02 taker=yes trade_id=83aef682-5a49-4ccb-62e3-b739e19a3f86 |  | prints.jsonl
1784063730.110 | 56407.110 | LAJ |  |  | 53 | 53c x 64.35 taker=no trade_id=5402dc0a-6ad1-6e34-259c-28f8ca524d6a |  | prints.jsonl
1784063753.000 | 56430.000 | LAJ | 53 | 53 | 53 |  |  | ticks#row-7945
1784063753.253 | 56430.253 | SVA |  |  | 48 | 48c x 20.1 taker=yes trade_id=1e705148-e1ed-7b7b-142d-16efb8e14e9e |  | prints.jsonl
1784063779.000 | 56456.000 | LAJ | 53 | 53 | 54 |  |  | ticks#row-7957
1784063779.047 | 56456.047 | LAJ |  |  | 54 | 54c x 17.0 taker=yes trade_id=0a65605d-f6de-5ca8-9425-683eb12b72ea |  | prints.jsonl
1784063904.993 | 56581.993 | LAJ |  |  | 54 | 54c x 41.92 taker=yes trade_id=e8267b59-f19b-5c1c-988c-07626cc5dd71 |  | prints.jsonl
1784063904.993 | 56581.993 | LAJ |  |  | 54 | 54c x 100.0 taker=yes trade_id=a2d54b55-c0f9-5a5b-b638-c8097b494ab2 |  | prints.jsonl
1784063904.993 | 56581.993 | LAJ |  |  | 54 | 54c x 37.48 taker=yes trade_id=0f6eaee7-97de-5444-86db-ead408828e5e |  | prints.jsonl
1784063905.821 | 56582.821 | LAJ |  |  | 54 | 54c x 61.0 taker=yes trade_id=e3d71d48-4417-5804-c5c2-179e075defda |  | prints.jsonl
1784063905.821 | 56582.821 | LAJ |  |  | 54 | 54c x 4.08 taker=yes trade_id=7910c53e-c1a3-5d50-ccd4-3924a4e6be49 |  | prints.jsonl
1784063905.821 | 56582.821 | LAJ |  |  | 54 | 54c x 114.32 taker=yes trade_id=6c8abed8-5568-54cc-cb8b-ba02a365d662 |  | prints.jsonl
1784063906.047 | 56583.047 | LAJ |  |  | 54 | 54c x 112.68 taker=yes trade_id=a9362010-b760-4594-4c8b-2d96c03c5b1e |  | prints.jsonl
1784063906.047 | 56583.047 | LAJ |  |  | 54 | 54c x 61.0 taker=yes trade_id=59a56d65-cd8d-40d5-5ecf-f330b7b3de9e |  | prints.jsonl
1784063906.047 | 56583.047 | LAJ |  |  | 54 | 54c x 4.72 taker=yes trade_id=38f9913b-6e47-49b5-6c9c-739664cba9d4 |  | prints.jsonl
1784063906.047 | 56583.047 | LAJ |  |  | 54 | 54c x 1.0 taker=yes trade_id=187b0296-9531-4450-56ac-0cc06e6b12d4 |  | prints.jsonl
1784063917.921 | 56594.921 | LAJ |  |  | 54 | 54c x 17.94 taker=yes trade_id=013b25e1-26ab-5e2d-4aba-d06baa0dbfb4 |  | prints.jsonl
1784063924.274 | 56601.274 | LAJ |  |  | 54 | 54c x 34.57 taker=yes trade_id=e8f0280e-acaf-48a1-9f1d-b18fc13497a4 |  | prints.jsonl
1784063928.962 | 56605.962 | LAJ |  |  | 54 | 54c x 87.0 taker=yes trade_id=14881df9-9017-40c5-583a-68c748be1368 |  | prints.jsonl
1784063931.157 | 56608.157 | LAJ |  |  | 54 | 54c x 100.46 taker=yes trade_id=d14b50b2-6d77-5b55-a801-2243e048fa40 |  | prints.jsonl
1784063936.000 | 56613.000 | LAJ | 53 | 53 | 55 |  |  | ticks#row-8021
1784063936.697 | 56613.697 | LAJ |  |  | 54 | 54c x 25.0 taker=yes trade_id=9fed7449-3794-7a3b-9cf0-f9930ba64b25 |  | prints.jsonl
1784063936.697 | 56613.697 | LAJ |  |  | 54 | 54c x 46.0 taker=yes trade_id=9bc4f0cf-5624-7b8f-aaa9-872aa1345e2b |  | prints.jsonl
1784063936.697 | 56613.697 | LAJ |  |  | 54 | 54c x 18.0 taker=yes trade_id=85e9774d-4917-7ece-8a82-2f44547cfe16 |  | prints.jsonl
1784063936.697 | 56613.697 | LAJ |  |  | 54 | 54c x 120.31 taker=yes trade_id=1755de94-eecf-7821-bc4b-223b5166e5f4 |  | prints.jsonl
1784063936.697 | 56613.697 | LAJ |  |  | 54 | 54c x 46.0 taker=yes trade_id=09dc4730-fc6d-7cad-8700-7ec19f20c7c0 |  | prints.jsonl
1784063936.697 | 56613.697 | LAJ |  |  | 55 | 55c x 13.55 taker=yes trade_id=04c9d105-d264-7ac0-b15c-2e2ae6f649a5 |  | prints.jsonl
1784063938.071 | 56615.071 | LAJ |  |  | 55 | 55c x 148.11 taker=yes trade_id=be199f47-ec98-68e0-65a3-97fce1585ded |  | prints.jsonl
1784063940.844 | 56617.844 | LAJ |  |  | 54 | 54c x 46.0 taker=yes trade_id=eacc0d54-f603-44b1-708b-b8ccad702578 |  | prints.jsonl
1784063940.844 | 56617.844 | LAJ |  |  | 55 | 55c x 17.13 taker=yes trade_id=9fc3ccbd-fefc-4bb4-63b8-070dea2df879 |  | prints.jsonl
1784063940.844 | 56617.844 | LAJ |  |  | 54 | 54c x 5.0 taker=yes trade_id=6a43573a-04cc-41d7-5ac3-a1a43d080cbf |  | prints.jsonl
1784063940.844 | 56617.844 | LAJ |  |  | 54 | 54c x 20.0 taker=yes trade_id=59709ec5-c1c8-4e3c-6b79-53af810b8263 |  | prints.jsonl
1784063943.176 | 56620.176 | LAJ |  |  | 55 | 55c x 35.23 taker=yes trade_id=c3e48cb4-0210-6060-cc56-f0b6438020ad |  | prints.jsonl
1784063956.630 | 56633.630 | LAJ |  |  | 55 | 55c x 158.98 taker=yes trade_id=726488d7-c9bc-7e28-fe98-c426c1c3b1fd |  | prints.jsonl
1784063956.630 | 56633.630 | LAJ |  |  | 55 | 55c x 17.28 taker=yes trade_id=346c7bd6-b565-7410-c684-9359c711e145 |  | prints.jsonl
1784063960.808 | 56637.808 | LAJ |  |  | 54 | 54c x 20.0 taker=yes trade_id=fba1a379-3408-6597-1cea-f2ac580ab264 |  | prints.jsonl
1784063960.808 | 56637.808 | LAJ |  |  | 54 | 54c x 46.0 taker=yes trade_id=89cad0cd-5e92-611f-0599-01043499764a |  | prints.jsonl
1784063960.808 | 56637.808 | LAJ |  |  | 55 | 55c x 110.26 taker=yes trade_id=16b88136-6229-6690-262e-fa3300c628a5 |  | prints.jsonl
1784063986.000 | 56663.000 | LAJ | 53 | 53 | 54 |  |  | ticks#row-8069
1784063986.872 | 56663.872 | LAJ |  |  | 54 | 54c x 35.88 taker=yes trade_id=82a3a5a5-6b9f-40d4-e7b3-54e707f8b27d |  | prints.jsonl
1784063993.605 | 56670.605 | LAJ |  |  | 54 | 54c x 10.12 taker=yes trade_id=fb8b58ed-7413-44e0-53cf-03c71ad0ee95 |  | prints.jsonl
1784063993.605 | 56670.605 | LAJ |  |  | 55 | 55c x 78.17 taker=yes trade_id=5089017a-fa1d-430c-6856-c78e1f9d1279 |  | prints.jsonl
1784064080.716 | 56757.716 | SVA |  |  | 48 | 48c x 2.01 taker=yes trade_id=ed0837f5-7ea5-56bf-78d8-9357d7b83a4e |  | prints.jsonl
1784064139.000 | 56816.000 | LAJ | 53 | 53 | 55 |  |  | ticks#row-8079
1784064139.342 | 56816.342 | LAJ |  |  | 55 | 55c x 1.76 taker=yes trade_id=d779d0c5-5191-6e90-7ece-b219c13cf439 |  | prints.jsonl
1784064174.389 | 56851.389 | LAJ |  |  | 55 | 55c x 17.0 taker=yes trade_id=f6c960e6-2c91-79d8-dfeb-c4797167c261 |  | prints.jsonl
1784064242.103 | 56919.103 | SVA |  |  | 48 | 48c x 112.0 taker=yes trade_id=db1b5bef-b810-4c22-79b1-93b1ebb9bcef |  | prints.jsonl
1784064242.103 | 56919.103 | SVA |  |  | 48 | 48c x 77.0 taker=yes trade_id=d1528c1e-cf38-47b3-4fba-523509557da6 |  | prints.jsonl
1784064242.103 | 56919.103 | SVA |  |  | 48 | 48c x 94.0 taker=yes trade_id=d0426729-74c9-42dc-7075-8c01bd886176 |  | prints.jsonl
1784064242.103 | 56919.103 | SVA |  |  | 48 | 48c x 40.0 taker=yes trade_id=8d72e0cd-522d-4a8b-63d1-dcbeb81bfd35 |  | prints.jsonl
1784064242.103 | 56919.103 | SVA |  |  | 48 | 48c x 38.0 taker=yes trade_id=85b41d66-d6cb-4eaf-62ec-9f7836742dd3 |  | prints.jsonl
1784064242.103 | 56919.103 | SVA |  |  | 48 | 48c x 240.84 taker=yes trade_id=65f792e2-424e-476f-48cb-2b0fa9a1026b |  | prints.jsonl
1784064242.103 | 56919.103 | SVA |  |  | 48 | 48c x 138.0 taker=yes trade_id=611f417c-6d3d-490b-420c-b2fde823d877 |  | prints.jsonl
1784064242.103 | 56919.103 | SVA |  |  | 48 | 48c x 10.0 taker=yes trade_id=60942dcc-5a67-4a6e-7e3b-95f89b9af0fe |  | prints.jsonl
1784064242.103 | 56919.103 | SVA |  |  | 48 | 48c x 100.0 taker=yes trade_id=5af2e283-f9b0-427e-4357-22ea51f72aff |  | prints.jsonl
1784064242.103 | 56919.103 | SVA |  |  | 48 | 48c x 67.0 taker=yes trade_id=5ac18ce4-3f36-416e-4987-cc4786f724bb |  | prints.jsonl
1784064242.103 | 56919.103 | SVA |  |  | 48 | 48c x 0.24 taker=yes trade_id=4acfa3ac-2841-4eab-439f-82f732c1b56e |  | prints.jsonl
1784064242.103 | 56919.103 | SVA |  |  | 48 | 48c x 10.0 taker=yes trade_id=30c8ff73-6034-45b9-6055-9a309687a0c3 |  | prints.jsonl
1784064242.103 | 56919.103 | SVA |  |  | 48 | 48c x 78.0 taker=yes trade_id=09dc5150-5736-49b2-42d0-8edd460709f7 |  | prints.jsonl
1784064382.000 | 57059.000 | LAJ | 53 | 53 | 54 |  |  | ticks#row-8184
1784064382.512 | 57059.512 | LAJ |  |  | 54 | 54c x 17.94 taker=yes trade_id=77a5cab4-5a3f-5bbf-d5bc-be9c7930152f |  | prints.jsonl
1784064393.159 | 57070.159 | SVA |  |  | 48 | 48c x 100.5 taker=yes trade_id=2f6e69f9-5cd2-5f83-0eb3-55a75beadf0b |  | prints.jsonl
1784064404.051 | 57081.051 | LAJ |  |  | 54 | 54c x 10.65 taker=yes trade_id=5648473a-dc23-5a47-5729-2a52e620c5b3 |  | prints.jsonl
1784064503.790 | 57180.790 | SVA |  |  | 48 | 48c x 8.8 taker=yes trade_id=37a8ef1a-4686-6457-bb6c-4c40f244bb9b |  | prints.jsonl
1784064542.414 | 57219.414 | LAJ |  |  | 54 | 54c x 5.0 taker=yes trade_id=73adfa6c-4ee7-435b-a620-344a42a8c87f |  | prints.jsonl
1784064556.180 | 57233.180 | LAJ |  |  | 54 | 54c x 50.23 taker=yes trade_id=71252a5d-3db3-4287-b0eb-b8d886e6fc4b |  | prints.jsonl
1784064571.112 | 57248.112 | LAJ |  |  | 54 | 54c x 82.0 taker=yes trade_id=af17ac43-b9b7-5ed3-5c02-78290bf58f1b |  | prints.jsonl
1784064601.482 | 57278.482 | SVA |  |  | 48 | 48c x 18.65 taker=yes trade_id=ecdf8b1e-6c0a-5e37-4faf-dd1bfec48b67 |  | prints.jsonl
1784064610.304 | 57287.304 | SVA |  |  | 48 | 48c x 7.21 taker=yes trade_id=71e73311-646e-48c3-c73f-d10ff56f7d47 |  | prints.jsonl
1784064610.304 | 57287.304 | SVA |  |  | 48 | 48c x 53.09 taker=yes trade_id=670193f5-8f7a-40e1-e58f-adcbb823d310 |  | prints.jsonl
1784064631.142 | 57308.142 | LAJ |  |  | 54 | 54c x 17.94 taker=yes trade_id=bd5525a6-f4db-4f57-1ff1-90dbeded0aa7 |  | prints.jsonl
1784064637.000 | 57314.000 | LAJ | 53 | 53 | 52 |  |  | ticks#row-8316
1784064637.939 | 57314.939 | LAJ |  |  | 52 | 52c x 6.0 taker=no trade_id=bddcb29b-acbf-6b2a-e487-13f42e2fe323 |  | prints.jsonl
1784064637.939 | 57314.939 | LAJ |  |  | 52 | 52c x 23.0 taker=no trade_id=b7492423-dd98-69b5-c9bb-9ecfc5bad3b3 |  | prints.jsonl
1784064637.939 | 57314.939 | LAJ |  |  | 53 | 53c x 71.65 taker=no trade_id=a69949dd-9105-6ad4-d142-f48067f7e102 |  | prints.jsonl
1784064637.939 | 57314.939 | LAJ |  |  | 52 | 52c x 1.29 taker=no trade_id=6632d978-8de0-6023-efb7-81b0954b3048 |  | prints.jsonl
1784064675.000 | 57352.000 | LAJ | 53 | 53 | 55 |  |  | ticks#row-8328
1784064675.785 | 57352.785 | LAJ |  |  | 54 | 54c x 491.24 taker=yes trade_id=eb1139f9-d66b-601f-6091-99cfa9f2d72f |  | prints.jsonl
1784064675.785 | 57352.785 | LAJ |  |  | 54 | 54c x 100.0 taker=yes trade_id=db692bd5-e1d1-6be1-5bb7-fba58cae5c04 |  | prints.jsonl
1784064675.785 | 57352.785 | LAJ |  |  | 55 | 55c x 389.0 taker=yes trade_id=d121a8e4-dea8-67ca-4c99-91f5565f3e61 |  | prints.jsonl
1784064675.785 | 57352.785 | LAJ |  |  | 55 | 55c x 566.92 taker=yes trade_id=923c64d2-4dc6-63ad-5f69-496218e807e7 |  | prints.jsonl
1784064675.785 | 57352.785 | LAJ |  |  | 54 | 54c x 1.0 taker=yes trade_id=8e938be6-d15f-6378-7144-b71c1d89bead |  | prints.jsonl
1784064675.785 | 57352.785 | LAJ |  |  | 55 | 55c x 3179.48 taker=yes trade_id=8b49f641-b40b-669c-5a2c-133b4246e504 |  | prints.jsonl
1784064675.785 | 57352.785 | LAJ |  |  | 55 | 55c x 393.0 taker=yes trade_id=82c43d8a-cb9a-6f31-571e-d0e9be12b24d |  | prints.jsonl
1784064675.785 | 57352.785 | LAJ |  |  | 54 | 54c x 54.0 taker=yes trade_id=3b4d9c23-51d8-6d63-7e22-2b121dc968a7 |  | prints.jsonl
1784064675.785 | 57352.785 | LAJ |  |  | 54 | 54c x 22.0 taker=yes trade_id=22cefafb-3c99-6b78-4935-a5de9383cbe2 |  | prints.jsonl
1784064696.280 | 57373.280 | SVA |  |  | 48 | 48c x 2.01 taker=yes trade_id=077c45f0-160e-5ba9-f2a0-ee11634e5940 |  | prints.jsonl
1784064780.580 | 57457.580 | SVA |  |  | 48 | 48c x 6.03 taker=yes trade_id=68c0a06d-237a-4739-1820-6cada2b9e5e4 |  | prints.jsonl
1784064938.000 | 57615.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-8984
1784064938.441 | 57615.441 | SVA |  |  | 48 | 48c x 708.0 taker=yes trade_id=f4fb06ec-75c6-541d-0bb3-c9ef900f8f5d |  | prints.jsonl
1784064938.441 | 57615.441 | SVA |  |  | 49 | 49c x 46.0 taker=yes trade_id=ef09636e-6d50-5ccc-0ef2-9b345fe58a8c |  | prints.jsonl
1784064938.441 | 57615.441 | SVA |  |  | 49 | 49c x 847.21 taker=yes trade_id=ea78e7f2-116e-5d99-1cb0-5ad69d365b98 |  | prints.jsonl
1784064938.441 | 57615.441 | SVA |  |  | 48 | 48c x 26.0 taker=yes trade_id=e6128a58-44d6-58d2-328e-102c71cebeb0 |  | prints.jsonl
1784064938.441 | 57615.441 | SVA |  |  | 48 | 48c x 416.0 taker=yes trade_id=c05f39fe-283c-50bd-2c70-f64ddb7ac82b |  | prints.jsonl
1784064938.441 | 57615.441 | SVA |  |  | 49 | 49c x 566.93 taker=yes trade_id=a5a3d181-ac20-590e-2cd9-5cb7622f6b0a |  | prints.jsonl
1784064938.441 | 57615.441 | SVA |  |  | 48 | 48c x 64.0 taker=yes trade_id=7db65350-fb7b-5f77-331c-f05b21248e21 |  | prints.jsonl
1784064938.441 | 57615.441 | SVA |  |  | 49 | 49c x 150.16 taker=yes trade_id=7166173f-b76f-54a9-1aaf-f0d2ad813c08 |  | prints.jsonl
1784064938.441 | 57615.441 | SVA |  |  | 48 | 48c x 10.0 taker=yes trade_id=6765532a-7e65-58aa-3892-87a5ed1601ad |  | prints.jsonl
1784064938.441 | 57615.441 | SVA |  |  | 48 | 48c x 43.0 taker=yes trade_id=66b8d417-adb0-57f7-2074-0953a221a6f2 |  | prints.jsonl
1784064938.441 | 57615.441 | SVA |  |  | 49 | 49c x 41.0 taker=yes trade_id=4b05c943-9621-5ede-37e6-ce362406bf23 |  | prints.jsonl
1784064938.441 | 57615.441 | SVA |  |  | 49 | 49c x 392.15 taker=yes trade_id=45100071-64c8-5b7f-2a96-ea853dce37a0 |  | prints.jsonl
1784064938.441 | 57615.441 | SVA |  |  | 48 | 48c x 86.87 taker=yes trade_id=32475c83-075e-52f1-1f66-25be925603e4 |  | prints.jsonl
1784064938.441 | 57615.441 | SVA |  |  | 48 | 48c x 21.0 taker=yes trade_id=0d959b04-a601-544d-254a-16fa0bb21418 |  | prints.jsonl
1784064967.040 | 57644.040 | SVA |  |  | 48 | 48c x 10.0 taker=yes trade_id=f96f9c45-0df3-4f93-b22e-e4b3cb856a70 |  | prints.jsonl
1784064987.000 | 57664.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-9006
1784064987.755 | 57664.755 | SVA |  |  | 48 | 48c x 20.1 taker=yes trade_id=457e709a-6cd3-5b27-bd75-eb6736ee0f40 |  | prints.jsonl
1784065103.000 | 57780.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-9017
1784065103.000 | 57780.000 | SVA | 46 | 47 | 48 |  |  | ticks#row-9018
1784065103.000 | 57780.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-9019
1784065103.178 | 57780.178 | SVA |  |  | 47 | 47c x 49.15 taker=no trade_id=05fa6e92-ea48-71f3-06e7-2a850b82c7b5 |  | prints.jsonl
1784065140.000 | 57817.000 | LAJ | 53 | 53 | 54 |  |  | ticks#row-8475
1784065140.442 | 57817.442 | LAJ |  |  | 54 | 54c x 32.31 taker=yes trade_id=3834ce9b-a72d-6305-9b0e-2b14c5736c14 |  | prints.jsonl
1784065502.147 | 58179.147 | SVA |  |  | 47 | 47c x 26.0 taker=yes trade_id=de6c6d27-36ba-79bf-bdb6-542b08c7f534 |  | prints.jsonl
1784065502.147 | 58179.147 | SVA |  |  | 47 | 47c x 11.0 taker=yes trade_id=d5ac8c91-bb05-7c38-8e1b-0c4c7b68f30e |  | prints.jsonl
1784065502.147 | 58179.147 | SVA |  |  | 48 | 48c x 26.04 taker=yes trade_id=cb6be9a7-1fbf-707f-8877-3f16488d0e25 |  | prints.jsonl
1784065502.147 | 58179.147 | SVA |  |  | 47 | 47c x 20.85 taker=yes trade_id=bd115ecd-f296-7ea5-94dd-f4d1047d8841 |  | prints.jsonl
1784065502.147 | 58179.147 | SVA |  |  | 47 | 47c x 172.0 taker=yes trade_id=7d9a9a10-e6f3-7f37-90d3-6f5960adeced |  | prints.jsonl
1784065503.000 | 58180.000 | SVA | 46 | 48 | 47 |  |  | ticks#row-9084
1784065503.000 | 58180.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-9086
1784065503.000 | 58180.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-9087
1784065513.665 | 58190.665 | LAJ |  |  | 54 | 54c x 26.91 taker=yes trade_id=9f467bea-76b1-60cd-d5b2-d963641e8ff8 |  | prints.jsonl
1784065515.000 | 58192.000 | LAJ | 53 | 53 | 53 |  |  | ticks#row-8565
1784065515.665 | 58192.665 | LAJ |  |  | 53 | 53c x 26.91 taker=yes trade_id=09737e7b-5d10-63dc-fc63-bba3580dc365 |  | prints.jsonl
1784065519.552 | 58196.552 | SVA |  |  | 48 | 48c x 2.01 taker=yes trade_id=6c90ea58-2747-70df-6fdf-9422eeecfa7d |  | prints.jsonl
1784065545.749 | 58222.749 | SVA |  |  | 48 | 48c x 4.0 taker=yes trade_id=f694647a-002f-56f7-9eda-197a258bf389 |  | prints.jsonl
1784065747.000 | 58424.000 | LAJ | 53 | 53 | 54 |  |  | ticks#row-8582
1784065747.373 | 58424.373 | LAJ |  |  | 54 | 54c x 163.81 taker=yes trade_id=f7c09b90-d206-6a9f-05c1-553197a5d750 |  | prints.jsonl
1784065747.373 | 58424.373 | LAJ |  |  | 54 | 54c x 87.78 taker=yes trade_id=a560965e-05c1-6fb1-3c86-53e44fbf9f60 |  | prints.jsonl
1784065747.373 | 58424.373 | LAJ |  |  | 54 | 54c x 46.0 taker=yes trade_id=7dc2d930-d533-6be4-2b70-33d1ff4d5526 |  | prints.jsonl
1784065747.373 | 58424.373 | LAJ |  |  | 54 | 54c x 32.0 taker=yes trade_id=65c10f45-1140-6336-091c-35dd28933d2f |  | prints.jsonl
1784065747.373 | 58424.373 | LAJ |  |  | 53 | 53c x 395.09 taker=yes trade_id=58d76d2c-e778-693c-0bcf-20864681935d |  | prints.jsonl
1784065803.715 | 58480.715 | SVA |  |  | 48 | 48c x 84.05 taker=yes trade_id=85e2e9bf-746b-747a-3749-68b1c609816f |  | prints.jsonl
1784065803.715 | 58480.715 | SVA |  |  | 48 | 48c x 13.95 taker=yes trade_id=1f3b71af-cc27-7fe3-208c-acc331d01c8d |  | prints.jsonl
1784065812.777 | 58489.777 | LAJ |  |  | 54 | 54c x 89.7 taker=yes trade_id=b21b5938-26ba-4e27-9516-7856acae76ac |  | prints.jsonl
1784065871.930 | 58548.930 | SVA |  |  | 48 | 48c x 1.0 taker=yes trade_id=b8e0e3d0-37ee-67de-a004-66ffb68e07c5 |  | prints.jsonl
1784065899.873 | 58576.873 | SVA |  |  | 48 | 48c x 9.0 taker=yes trade_id=e7737776-d6a2-630a-d714-1c8312a47979 |  | prints.jsonl
1784065899.873 | 58576.873 | SVA |  |  | 48 | 48c x 1.05 taker=yes trade_id=1df1698f-58fd-6b0c-f009-a108815ca864 |  | prints.jsonl
1784065940.831 | 58617.831 | SVA |  |  | 48 | 48c x 10.05 taker=yes trade_id=ee96d353-ffc1-4828-2306-2f9f659225dc |  | prints.jsonl
1784065962.297 | 58639.297 | LAJ |  |  | 52 | 52c x 7.0 taker=no trade_id=57f09e91-1ce9-4d7a-357f-bd8868bb5269 |  | prints.jsonl
1784065973.000 | 58650.000 | LAJ | 53 | 53 | 52 |  |  | ticks#row-8779
1784066010.525 | 58687.525 | LAJ |  |  | 54 | 54c x 0.35 taker=yes trade_id=eb8840dc-835a-4137-0a8b-cc6bdcc8ec6c |  | prints.jsonl
1784066019.000 | 58696.000 | LAJ | 53 | 53 | 54 |  |  | ticks#row-8782
1784066435.776 | 59112.776 | LAJ |  |  | 54 | 54c x 179.4 taker=yes trade_id=d13501f5-b002-7837-3fa3-cb88e391fce8 |  | prints.jsonl
1784066747.569 | 59424.569 | SVA |  |  | 48 | 48c x 11.0 taker=yes trade_id=0b20b1f0-fb39-76d8-104e-de2eb494be38 |  | prints.jsonl
1784066792.924 | 59469.924 | LAJ |  |  | 54 | 54c x 17.0 taker=yes trade_id=7f644fdf-c0ae-58e3-1cc4-845d58209104 |  | prints.jsonl
1784066796.272 | 59473.272 | SVA |  |  | 48 | 48c x 60.3 taker=yes trade_id=64f132b5-ed75-7be8-9e06-9301ac87692c |  | prints.jsonl
1784066843.851 | 59520.851 | LAJ |  |  | 54 | 54c x 4.89 taker=yes trade_id=9436397a-a22a-440f-58ce-bd10fd973d6c |  | prints.jsonl
1784067035.260 | 59712.260 | LAJ |  |  | 54 | 54c x 44.0 taker=yes trade_id=24a4e148-b04e-4e93-af7b-ff02d2691bf7 |  | prints.jsonl
1784067287.701 | 59964.701 | SVA |  |  | 48 | 48c x 16.49 taker=yes trade_id=41f00c1f-a9ea-4266-078e-323dec2eb0b0 |  | prints.jsonl
1784067287.701 | 59964.701 | SVA |  |  | 48 | 48c x 1.6 taker=yes trade_id=03a94e3b-97a5-4624-045b-14c9902f779c |  | prints.jsonl
1784067456.029 | 60133.029 | LAJ |  |  | 54 | 54c x 3.0 taker=yes trade_id=a71ebc0f-ed02-4857-be78-c53d78e93057 |  | prints.jsonl
1784067458.973 | 60135.973 | LAJ |  |  | 54 | 54c x 17.94 taker=yes trade_id=39365143-ad36-7d07-9e0f-308a56be0063 |  | prints.jsonl
1784067512.334 | 60189.334 | LAJ |  |  | 54 | 54c x 178.55 taker=yes trade_id=ddffa0fb-fd9e-60c7-fade-407ba18f52bf |  | prints.jsonl
1784067740.854 | 60417.854 | LAJ |  |  | 54 | 54c x 18.49 taker=yes trade_id=973a7a4f-f5f4-618d-7b6b-c9984960573f |  | prints.jsonl
1784067740.854 | 60417.854 | LAJ |  |  | 54 | 54c x 31.51 taker=yes trade_id=6f097166-39a6-6cab-5291-d05c59e70fff |  | prints.jsonl
1784067761.738 | 60438.738 | SVA |  |  | 48 | 48c x 378.51 taker=yes trade_id=be18d2ee-e3ae-6cfa-6b53-7016df7015f4 |  | prints.jsonl
1784067761.738 | 60438.738 | SVA |  |  | 48 | 48c x 616.57 taker=yes trade_id=6a8e47b8-963f-6e3e-602f-c4a0316a814f |  | prints.jsonl
1784067761.738 | 60438.738 | SVA |  |  | 48 | 48c x 10.0 taker=yes trade_id=4cd0906b-5d4f-6a23-6658-9cd073fbb40c |  | prints.jsonl
1784068152.675 | 60829.675 | SVA |  |  | 48 | 48c x 53.0 taker=yes trade_id=d3eac155-b15f-57f5-daf5-148fe5065c73 |  | prints.jsonl
1784068152.675 | 60829.675 | SVA |  |  | 48 | 48c x 7.64 taker=yes trade_id=a99f9a9d-1416-56e6-faa9-3480dea160fa |  | prints.jsonl
1784068152.675 | 60829.675 | SVA |  |  | 48 | 48c x 20.0 taker=yes trade_id=9504f89d-7eef-5242-e260-e80d53f7c547 |  | prints.jsonl
1784068152.675 | 60829.675 | SVA |  |  | 48 | 48c x 46.0 taker=yes trade_id=30a78c04-9866-5bc6-d05d-0d8d806b06d0 |  | prints.jsonl
1784068404.000 | 61081.000 | LAJ | 53 | 53 | 53 |  |  | ticks#row-9970
1784068404.776 | 61081.776 | LAJ |  |  | 53 | 53c x 5.48 taker=yes trade_id=1d3ef516-4185-7e05-3df7-a7b8ed216b3a |  | prints.jsonl
1784068555.621 | 61232.621 | LAJ |  |  | 53 | 53c x 18.26 taker=yes trade_id=e54c6b44-ffed-5e51-4cb1-6e31590134ae |  | prints.jsonl
1784068590.728 | 61267.728 | LAJ |  |  | 53 | 53c x 45.66 taker=yes trade_id=28c994f9-5c11-7ead-cc7b-7d9fe0864bf2 |  | prints.jsonl
1784068597.758 | 61274.758 | LAJ |  |  | 53 | 53c x 29.0 taker=yes trade_id=2db48950-27d9-5c9d-ef87-ffec3667c282 |  | prints.jsonl
1784068601.983 | 61278.983 | SVA |  |  | 48 | 48c x 12.06 taker=yes trade_id=3da0bd39-21d6-7d8a-b237-6dced5b71d16 |  | prints.jsonl
1784068606.784 | 61283.784 | SVA |  |  | 48 | 48c x 117.3 taker=yes trade_id=ee794b8c-efee-46da-adba-bcf60d2c37a6 |  | prints.jsonl
1784068606.784 | 61283.784 | SVA |  |  | 48 | 48c x 39.0 taker=yes trade_id=c36d0f41-8be8-4ebe-8ceb-25715ef969b3 |  | prints.jsonl
1784068606.784 | 61283.784 | SVA |  |  | 48 | 48c x 44.7 taker=yes trade_id=bc33dda9-e212-4e50-991e-b6d40db72921 |  | prints.jsonl
1784068631.944 | 61308.944 | LAJ |  |  | 53 | 53c x 4.6 taker=yes trade_id=749b604f-c381-79e9-a19c-97795e5b9ed2 |  | prints.jsonl
1784068631.944 | 61308.944 | LAJ |  |  | 53 | 53c x 20.0 taker=yes trade_id=702eb68d-a4b3-7c55-843d-7d6f45131817 |  | prints.jsonl
1784068631.944 | 61308.944 | LAJ |  |  | 53 | 53c x 113.42 taker=yes trade_id=18a80d7f-4a5f-7618-b3b0-c2dc0b47277b |  | prints.jsonl
1784068631.944 | 61308.944 | LAJ |  |  | 53 | 53c x 83.0 taker=yes trade_id=01f6833b-8097-7ae2-af37-3384e4430d16 |  | prints.jsonl
1784068659.378 | 61336.378 | LAJ |  |  | 53 | 53c x 18.26 taker=yes trade_id=d2c5f380-4443-5478-746f-d71b3344fb3f |  | prints.jsonl
1784068746.672 | 61423.672 | LAJ |  |  | 54 | 54c x 0.51 taker=yes trade_id=fde4aaea-e71c-723d-a7cd-0c47fb16c08f |  | prints.jsonl
1784068746.672 | 61423.672 | LAJ |  |  | 53 | 53c x 85.32 taker=yes trade_id=eaad86c2-306f-71a8-bd14-b38a6c9bafaf |  | prints.jsonl
1784068746.672 | 61423.672 | LAJ |  |  | 54 | 54c x 63.0 taker=yes trade_id=e3eae0c3-1e66-7ef8-86dd-cce36af75e69 |  | prints.jsonl
1784068746.672 | 61423.672 | LAJ |  |  | 54 | 54c x 23.0 taker=yes trade_id=96835cf9-17e9-7063-9a30-b1b88ccaba0a |  | prints.jsonl
1784068746.672 | 61423.672 | LAJ |  |  | 54 | 54c x 111.35 taker=yes trade_id=60c82987-e99e-7417-a826-fabad58913d0 |  | prints.jsonl
1784068748.000 | 61425.000 | LAJ | 53 | 53 | 54 |  |  | ticks#row-10207
1784068774.000 | 61451.000 | LAJ | 53 | 53 | 53 |  |  | ticks#row-10258
1784068774.193 | 61451.193 | LAJ |  |  | 53 | 53c x 89.7 taker=yes trade_id=0b9990ec-7dcc-4ca3-934b-e45ab444c197 |  | prints.jsonl
1784069110.300 | 61787.300 | SVA |  |  | 48 | 48c x 2.01 taker=yes trade_id=68eded80-0396-6bf8-d23d-836f88df1351 |  | prints.jsonl
1784069209.105 | 61886.105 | SVA |  |  | 48 | 48c x 5.0 taker=yes trade_id=5401d65d-f50a-5f9c-ae5a-40575f05d749 |  | prints.jsonl
1784069432.870 | 62109.870 | LAJ |  |  | 53 | 53c x 0.3 taker=yes trade_id=8a39a425-7dd4-7e2f-9af9-28ac61c47223 |  | prints.jsonl
1784069432.877 | 62109.877 | LAJ |  |  | 53 | 53c x 1.55 taker=yes trade_id=f230493f-4ff8-5657-1b0f-ca121c00a617 |  | prints.jsonl
1784069442.208 | 62119.208 | SVA |  |  | 48 | 48c x 50.0 taker=yes trade_id=ab2c1c6f-7f7a-696a-4407-56e20f88d7da |  | prints.jsonl
1784069442.208 | 62119.208 | SVA |  |  | 48 | 48c x 36.29 taker=yes trade_id=9f9fe87a-1cfe-6758-4b0e-9a27292d070d |  | prints.jsonl
1784069442.208 | 62119.208 | SVA |  |  | 48 | 48c x 22.0 taker=yes trade_id=886dc19f-fb1d-6769-7276-afbb421bd2a3 |  | prints.jsonl
1784069442.208 | 62119.208 | SVA |  |  | 48 | 48c x 22.0 taker=yes trade_id=850688cc-9b65-6c04-4790-df61fc8ef49d |  | prints.jsonl
1784069442.208 | 62119.208 | SVA |  |  | 48 | 48c x 10.0 taker=yes trade_id=17b261bc-0e1d-6c55-7d0a-bd6394fdca46 |  | prints.jsonl
1784069442.208 | 62119.208 | SVA |  |  | 48 | 48c x 24.36 taker=yes trade_id=149c6d4c-496c-677a-58e1-0321cb527b6f |  | prints.jsonl
1784069507.436 | 62184.436 | SVA |  |  | 48 | 48c x 163.36 taker=yes trade_id=d5bdce5b-e717-5506-05aa-b478188df0c3 |  | prints.jsonl
1784069507.436 | 62184.436 | SVA |  |  | 48 | 48c x 155.0 taker=yes trade_id=d36040f5-e879-5d5a-1d11-bf2649737c62 |  | prints.jsonl
1784069507.436 | 62184.436 | SVA |  |  | 48 | 48c x 147.0 taker=yes trade_id=4ce5fd56-8e96-5a06-18d3-146fabdf5412 |  | prints.jsonl
1784069507.436 | 62184.436 | SVA |  |  | 48 | 48c x 24.64 taker=yes trade_id=2466a396-f830-564a-327c-02594f4e2373 |  | prints.jsonl
1784069531.338 | 62208.338 | SVA |  |  | 48 | 48c x 20.1 taker=yes trade_id=8f5c434e-c0f3-61e6-aa73-93918e565243 |  | prints.jsonl
1784069551.710 | 62228.710 | SVA |  |  | 48 | 48c x 2.0 taker=yes trade_id=f44b2067-56db-5bde-40ae-77f1161f3deb |  | prints.jsonl
1784069614.285 | 62291.285 | LAJ |  |  | 53 | 53c x 545.0 taker=yes trade_id=38b1f359-46a0-6c1f-a9ee-10f606c8cdf7 |  | prints.jsonl
1784069760.158 | 62437.158 | LAJ |  |  | 53 | 53c x 500.0 taker=yes trade_id=c62c6e7c-f8df-6245-9a9b-c9ede07ee86f |  | prints.jsonl
1784070014.000 | 62691.000 | LAJ | 52 | 53 | 53 |  |  | ticks#row-10930
1784070208.192 | 62885.192 | LAJ |  |  | 53 | 53c x 909.0 taker=yes trade_id=04f8ae51-df93-4155-ccd0-e64e13e6e617 |  | prints.jsonl
1784070216.000 | 62893.000 | LAJ | 51 | 53 | 53 |  |  | ticks#row-11016
1784070216.000 | 62893.000 | SVA | 47 | 49 | 48 |  |  | ticks#row-12825
1784070216.000 | 62893.000 | SVA | 47 | 49 | 49 |  |  | ticks#row-12827
1784070216.275 | 62893.275 | SVA |  |  | 49 | 49c x 77.0 taker=yes trade_id=fd8e0c18-88fd-431f-b2c0-45565a58dee9 |  | prints.jsonl
1784070216.275 | 62893.275 | SVA |  |  | 48 | 48c x 37.0 taker=yes trade_id=eb68ed5f-1e17-4fd4-b785-b7e4eb97fb1e |  | prints.jsonl
1784070216.275 | 62893.275 | SVA |  |  | 48 | 48c x 10.0 taker=yes trade_id=5a342f1c-8e68-4ed6-81d2-62927f72b801 |  | prints.jsonl
1784070216.275 | 62893.275 | SVA |  |  | 48 | 48c x 75.0 taker=yes trade_id=3ea68701-f20a-4bce-82a7-7bcbb44b8afe |  | prints.jsonl
1784070226.396 | 62903.396 | LAJ |  |  | 53 | 53c x 120.0 taker=yes trade_id=49787a62-1cbf-7c49-3795-bfe1a743a4af |  | prints.jsonl
1784070272.810 | 62949.810 | LAJ |  |  | 53 | 53c x 219.2 taker=yes trade_id=f4afc1fc-051f-42c5-19c7-add845ad6297 |  | prints.jsonl
1784070388.373 | 63065.373 | SVA |  |  | 49 | 49c x 9.85 taker=yes trade_id=1bf467bd-9085-76bb-bb16-03d3f1d7dfbd |  | prints.jsonl
1784070420.637 | 63097.637 | SVA |  |  | 49 | 49c x 86.7 taker=yes trade_id=3007e180-f7fd-7217-370e-20b921403ed9 |  | prints.jsonl
1784070500.085 | 63177.085 | SVA |  |  | 49 | 49c x 94.58 taker=yes trade_id=2fd2f5b2-38cd-758b-87d4-d3ae2eb4774d |  | prints.jsonl
1784070539.924 | 63216.924 | LAJ |  |  | 53 | 53c x 181.0 taker=yes trade_id=f10d1b97-efdb-7f31-4b30-7c025b56f493 |  | prints.jsonl
1784070783.546 | 63460.546 | SVA |  |  | 49 | 49c x 10.0 taker=yes trade_id=9a9073aa-e849-71bb-98b0-c60c98ade23d |  | prints.jsonl
1784071061.274 | 63738.274 | LAJ |  |  | 53 | 53c x 1.82 taker=yes trade_id=2186f460-3f0f-73f5-c03b-e096ca0226e7 |  | prints.jsonl
1784071136.533 | 63813.533 | SVA |  |  | 49 | 49c x 39.4 taker=yes trade_id=e3993759-7241-6b67-ab1f-5dd39c4a5659 |  | prints.jsonl
1784071507.980 | 64184.980 | SVA |  |  | 49 | 49c x 9.85 taker=yes trade_id=50744fa0-4f05-627f-ad55-3ce6009aa80d |  | prints.jsonl
1784071609.419 | 64286.419 | SVA |  |  | 49 | 49c x 39.19 taker=yes trade_id=b5f7286d-f479-48b7-5012-0fb915c3695d |  | prints.jsonl
1784071671.644 | 64348.644 | LAJ |  |  | 53 | 53c x 5.0 taker=yes trade_id=e96bfcaa-b1df-66a1-8769-09c27e0d72df |  | prints.jsonl
1784071840.162 | 64517.162 | LAJ |  |  | 53 | 53c x 89.0 taker=yes trade_id=0b5422c8-3b73-5c39-9c8d-e4f0b3782dab |  | prints.jsonl
1784072001.360 | 64678.360 | LAJ |  |  | 53 | 53c x 9.13 taker=yes trade_id=bf37b0a0-5ec3-70c1-753a-7dce32229523 |  | prints.jsonl
1784072035.532 | 64712.532 | LAJ |  |  | 53 | 53c x 182.66 taker=yes trade_id=d28fd04a-1a83-5b3d-014e-522e705f6687 |  | prints.jsonl
1784072102.998 | 64779.998 | LAJ |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@48 (before 47) | FOUR_STORIES
1784072166.000 | 64843.000 | LAJ | 52 | 53 | 53 |  |  | ticks#row-14069
1784072166.000 | 64843.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-13951
1784072169.000 | 64846.000 | SVA | 46 | 48 | 49 |  |  | ticks#row-14020
1784072169.000 | 64846.000 | SVA | 46 | 49 | 49 |  |  | ticks#row-14024
1784072169.000 | 64846.000 | SVA | 46 | 48 | 49 |  |  | ticks#row-14054
1784072171.000 | 64848.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-14097
1784072185.000 | 64862.000 | SVA | 46 | 48 | 49 |  |  | ticks#row-14564
1784072188.000 | 64865.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-14594
1784072192.000 | 64869.000 | SVA | 46 | 48 | 49 |  |  | ticks#row-14822
1784072195.000 | 64872.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-15222
1784072195.000 | 64872.000 | SVA | 46 | 48 | 49 |  |  | ticks#row-15228
1784072201.000 | 64878.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-15288
1784072201.000 | 64878.000 | SVA | 46 | 48 | 49 |  |  | ticks#row-15297
1784072207.000 | 64884.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-15363
1784072207.000 | 64884.000 | SVA | 46 | 48 | 49 |  |  | ticks#row-15381
1784072210.000 | 64887.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-15429
1784072211.000 | 64888.000 | SVA | 46 | 48 | 49 |  |  | ticks#row-15437
1784072213.000 | 64890.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-15658
1784072213.000 | 64890.000 | SVA | 46 | 48 | 49 |  |  | ticks#row-15668
1784072224.000 | 64901.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-16305
1784072226.000 | 64903.000 | SVA | 46 | 48 | 49 |  |  | ticks#row-16311
1784072226.000 | 64903.000 | SVA | 47 | 48 | 49 |  |  | ticks#row-16316
1784072226.000 | 64903.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-16327
1784072226.553 | 64903.553 | SVA |  |  | 48 | 48c x 1.0 taker=yes trade_id=1c5d17cb-e4d2-7c77-27d8-b1e39f3927a4 |  | prints.jsonl
1784072238.000 | 64915.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-16726
1784072242.000 | 64919.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-16806
1784072247.000 | 64924.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-16897
1784072250.000 | 64927.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-16987
1784072251.413 | 64928.413 | SVA |  |  | 48 | 48c x 9.81 taker=yes trade_id=ecfe945b-09e5-4cd8-84fc-170bced3979c |  | prints.jsonl
1784072251.413 | 64928.413 | SVA |  |  | 48 | 48c x 191.2 taker=yes trade_id=3f5cccd4-674a-45a7-a6ce-2f961cdf44a4 |  | prints.jsonl
1784072252.886 | 64929.886 | SVA |  |  | 48 | 48c x 150.76 taker=yes trade_id=2620d8aa-1781-70bc-f3a4-e624faf41720 |  | prints.jsonl
1784072253.000 | 64930.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-17102
1784072256.000 | 64933.000 | LAJ | 52 | 53 | 52 |  |  | ticks#row-15960
1784072256.000 | 64933.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-17163
1784072256.000 | 64933.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-17172
1784072256.707 | 64933.707 | LAJ |  |  | 52 | 52c x 283.18 taker=no trade_id=a5652a86-a7d4-5bcc-de98-c896f7ba240f |  | prints.jsonl
1784072259.000 | 64936.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-18206
1784072261.000 | 64938.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-18257
1784072262.000 | 64939.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-18537
1784072265.000 | 64942.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-18930
1784072267.000 | 64944.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-18973
1784072276.000 | 64953.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-19156
1784072280.000 | 64957.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-19210
1784072296.000 | 64973.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-19643
1784072299.000 | 64976.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-19669
1784072299.000 | 64976.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-19686
1784072299.000 | 64976.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-19755
1784072305.000 | 64982.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-19974
1784072305.446 | 64982.446 | SVA |  |  | 48 | 48c x 40.2 taker=yes trade_id=7e5ece7e-d6c9-5e78-8312-f6232c90c750 |  | prints.jsonl
1784072308.000 | 64985.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-20004
1784072308.000 | 64985.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-20011
1784072309.000 | 64986.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-20403
1784072317.000 | 64994.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-20949
1784072321.000 | 64998.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-21597
1784072323.000 | 65000.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-21723
1784072325.000 | 65002.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-21774
1784072338.226 | 65015.226 | LAJ |  |  | 53 | 53c x 91.33 taker=yes trade_id=35733633-8871-69ec-705d-f547b63b980e |  | prints.jsonl
1784072340.000 | 65017.000 | LAJ | 52 | 53 | 53 |  |  | ticks#row-18838
1784072343.587 | 65020.587 | LAJ |  |  | 53 | 53c x 990.96 taker=yes trade_id=d8345727-c019-43fb-1b61-dc687db37e03 |  | prints.jsonl
1784072343.587 | 65020.587 | LAJ |  |  | 53 | 53c x 1200.0 taker=yes trade_id=a5d584cd-cdda-4528-02ed-8f59062d4b44 |  | prints.jsonl
1784072343.587 | 65020.587 | LAJ |  |  | 53 | 53c x 844.04 taker=yes trade_id=2e23829c-ea71-4e94-2254-e8ff2c5b3682 |  | prints.jsonl
1784072345.000 | 65022.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-22074
1784072357.319 | 65034.319 | SVA |  |  | 48 | 48c x 10.05 taker=yes trade_id=748fb7af-b7a1-7cfa-651d-fe3409f1b4b8 |  | prints.jsonl
1784072408.059 | 65085.059 | LAJ |  |  | 54 | 54c x 209.9 taker=yes trade_id=8bd6b824-c0d1-7a95-ec88-74b75ac29613 |  | prints.jsonl
1784072412.943 | 65089.943 | LAJ |  |  | 54 | 54c x 35.0 taker=yes trade_id=644c02f9-035d-41e9-54b2-1af527c7a34f |  | prints.jsonl
1784072421.000 | 65098.000 | LAJ | 52 | 53 | 54 |  |  | ticks#row-20212
1784072432.000 | 65109.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-20229
1784072434.841 | 65111.841 | SVA |  |  | 48 | 48c x 46.0 taker=yes trade_id=4828c11f-3c5c-5325-519c-cc3fb6d2f4b2 |  | prints.jsonl
1784072434.841 | 65111.841 | SVA |  |  | 48 | 48c x 151.0 taker=yes trade_id=3ad1062f-020e-50a3-4747-97f56c1c6c31 |  | prints.jsonl
1784072438.251 | 65115.251 | LAJ |  |  | 54 | 54c x 4.48 taker=yes trade_id=ee04bf64-4a8d-7d21-b930-0dd3606cd09b |  | prints.jsonl
1784072461.907 | 65138.907 | LAJ |  |  | 54 | 54c x 4.3 taker=yes trade_id=f9520aa6-8a6d-639d-48d4-1113a83c114f |  | prints.jsonl
1784072496.564 | 65173.564 | SVA |  |  | 48 | 48c x 201.01 taker=yes trade_id=1c7bffc6-d406-6ba3-3b40-92d744d32a9d |  | prints.jsonl
1784072500.868 | 65177.868 | LAJ |  |  | 54 | 54c x 44.85 taker=yes trade_id=ec264de1-46b5-7e09-118c-b5acbe6a90fb |  | prints.jsonl
1784072501.000 | 65178.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-20309
1784072501.000 | 65178.000 | SVA | 46 | 47 | 48 |  |  | ticks#row-22424
1784072501.526 | 65178.526 | LAJ |  |  | 54 | 54c x 46.0 taker=yes trade_id=975f66a5-ddb6-5ce9-bbaa-09c300953d6b |  | prints.jsonl
1784072501.526 | 65178.526 | LAJ |  |  | 54 | 54c x 1200.0 taker=yes trade_id=7220a5bc-fbb2-50f7-bece-03572e9a2c5d |  | prints.jsonl
1784072501.526 | 65178.526 | LAJ |  |  | 54 | 54c x 46.0 taker=yes trade_id=4b0744a6-089e-51f1-b476-073f46630e9d |  | prints.jsonl
1784072501.526 | 65178.526 | LAJ |  |  | 54 | 54c x 60.47 taker=yes trade_id=2fe0de10-f305-5f11-a03c-4264ef97d383 |  | prints.jsonl
1784072501.526 | 65178.526 | LAJ |  |  | 54 | 54c x 343.53 taker=yes trade_id=25176c13-6bac-52f8-9720-1a7ce2e0a392 |  | prints.jsonl
1784072501.526 | 65178.526 | LAJ |  |  | 54 | 54c x 89.0 taker=yes trade_id=20eb0275-7a4b-5c03-b611-9772b5d83538 |  | prints.jsonl
1784072504.000 | 65181.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-20342
1784072507.000 | 65184.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-20457
1784072525.000 | 65202.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-20847
1784072529.000 | 65206.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-20869
1784072545.000 | 65222.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-21017
1784072550.000 | 65227.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-21053
1784072554.764 | 65231.764 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=4b4fb7d7-1dc3-6d53-a572-f4c5659e3f11 |  | prints.jsonl
1784072554.764 | 65231.764 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=41474bf2-5717-6840-a711-9e67c315159f |  | prints.jsonl
1784072554.764 | 65231.764 | SVA |  |  | 47 | 47c x 15.49 taker=yes trade_id=235acea0-7775-6255-bfc2-8e196c0841cd |  | prints.jsonl
1784072554.764 | 65231.764 | SVA |  |  | 47 | 47c x 5.0 taker=yes trade_id=22689708-1672-6ffe-969e-349b31ec0d7d |  | prints.jsonl
1784072557.000 | 65234.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-21227
1784072558.000 | 65235.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-21246
1784072560.000 | 65237.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-23360
1784072562.000 | 65239.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-21470
1784072564.000 | 65241.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-21488
1784072571.209 | 65248.209 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=e47afcb7-5da0-6bda-d8bd-4df5fe0379c4 |  | prints.jsonl
1784072571.209 | 65248.209 | SVA |  |  | 47 | 47c x 612.0 taker=yes trade_id=d67f39db-0ef6-6d11-cba0-ab4c9d36afaa |  | prints.jsonl
1784072571.209 | 65248.209 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=714098aa-0ee0-6f08-ca0a-79d2679678bd |  | prints.jsonl
1784072571.209 | 65248.209 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=25840cd8-0ed5-67a7-ea56-eb6aed4cdeaa |  | prints.jsonl
1784072591.000 | 65268.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-21970
1784072593.000 | 65270.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-22003
1784072610.367 | 65287.367 | SVA |  |  | 47 | 47c x 12.05 taker=yes trade_id=56d6a526-7548-63db-ab47-3050761946ee |  | prints.jsonl
1784072610.367 | 65287.367 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=42242a1d-8032-672b-aa0f-fd135f2adcd9 |  | prints.jsonl
1784072610.367 | 65287.367 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=3b3dd3f3-e4c3-6d9b-abf6-054400c04825 |  | prints.jsonl
1784072657.868 | 65334.868 | SVA |  |  | 47 | 47c x 5.0 taker=yes trade_id=9fe48bb4-1798-5ecf-06e4-2e3e882456a6 |  | prints.jsonl
1784072675.025 | 65352.025 | SVA |  |  | 47 | 47c x 73.62 taker=yes trade_id=f35aa660-8b27-42fc-6e20-85e230545827 |  | prints.jsonl
1784072675.025 | 65352.025 | SVA |  |  | 47 | 47c x 28.95 taker=yes trade_id=6c041c71-3f90-4c7b-7758-d821c54c62c6 |  | prints.jsonl
1784072693.000 | 65370.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-23369
1784072696.000 | 65373.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-23382
1784072705.000 | 65382.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-23466
1784072708.000 | 65385.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-23485
1784072715.000 | 65392.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-23626
1784072715.000 | 65392.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-23630
1784072715.000 | 65392.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-23633
1784072717.000 | 65394.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-23669
1784072719.440 | 65396.440 | SVA |  |  | 47 | 47c x 239.0 taker=yes trade_id=dc9701be-5b8d-5416-765d-3f6cb1dd9dc1 |  | prints.jsonl
1784072719.440 | 65396.440 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=a7d67153-4ec9-5f36-5c81-8d8ab3b6c699 |  | prints.jsonl
1784072719.440 | 65396.440 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=729847ea-c8b6-5c7b-5b10-449bcdb3ce50 |  | prints.jsonl
1784072719.440 | 65396.440 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=60a9ca03-0099-506f-6113-2c0cfdd0d02b |  | prints.jsonl
1784072726.000 | 65403.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-23806
1784072729.000 | 65406.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-23819
1784072732.000 | 65409.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-23889
1784072734.000 | 65411.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-23904
1784072749.000 | 65426.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-24145
1784072752.000 | 65429.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-24263
1784072754.377 | 65431.377 | LAJ |  |  | 54 | 54c x 23.32 taker=yes trade_id=d448f77b-65ec-65f0-99dc-94d78e2844c2 |  | prints.jsonl
1784072754.719 | 65431.719 | LAJ |  |  | 54 | 54c x 1.0 taker=yes trade_id=b77848b4-65b0-6ff4-3d5d-fc2aec36b102 |  | prints.jsonl
1784072771.000 | 65448.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-24596
1784072772.000 | 65449.000 | SVA | 46 | 47 | 48 |  |  | ticks#row-29191
1784072772.774 | 65449.774 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=eaea902c-8533-5404-c668-4684e43270d2 |  | prints.jsonl
1784072772.774 | 65449.774 | SVA |  |  | 48 | 48c x 12.0 taker=yes trade_id=78c7fd7d-7028-50d7-d860-8902fe3dc3c2 |  | prints.jsonl
1784072772.774 | 65449.774 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=4382243c-4e49-5a67-f5d8-1d07a71c5207 |  | prints.jsonl
1784072772.774 | 65449.774 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=02982f21-aca7-54d3-f052-21263a5c900e |  | prints.jsonl
1784072773.000 | 65450.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-24621
1784072790.000 | 65467.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-24890
1784072793.000 | 65470.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-24910
1784072806.000 | 65483.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-25134
1784072809.000 | 65486.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-25150
1784072812.000 | 65489.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-25190
1784072812.000 | 65489.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-30155
1784072812.179 | 65489.179 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=e347e2bc-6310-6829-3d76-1b2767418488 |  | prints.jsonl
1784072812.179 | 65489.179 | SVA |  |  | 47 | 47c x 23.0 taker=yes trade_id=80dcb293-2905-690e-104e-64ef2c79de40 |  | prints.jsonl
1784072814.000 | 65491.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-25207
1784072821.000 | 65498.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-25329
1784072824.000 | 65501.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-25398
1784072829.150 | 65506.150 | SVA |  |  | 47 | 47c x 29.0 taker=yes trade_id=8fb80c48-7304-5262-73b5-6c06d79efc4e |  | prints.jsonl
1784072833.450 | 65510.450 | SVA |  |  | 47 | 47c x 17.0 taker=yes trade_id=9b3b4553-12d8-7d02-b886-fab71a349f76 |  | prints.jsonl
1784072833.450 | 65510.450 | SVA |  |  | 47 | 47c x 13.77 taker=yes trade_id=25f525c6-6421-750b-93b1-680005164dd6 |  | prints.jsonl
1784072838.000 | 65515.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-25608
1784072841.000 | 65518.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-25622
1784072844.926 | 65521.926 | SVA |  |  | 47 | 47c x 226.79 taker=yes trade_id=b5f6a401-43b4-5e9b-8aba-8660755f135f |  | prints.jsonl
1784072844.926 | 65521.926 | SVA |  |  | 47 | 47c x 46.0 taker=yes trade_id=a57b4778-3acd-5b0e-ad5c-fd3eccd1e7d3 |  | prints.jsonl
1784072844.926 | 65521.926 | SVA |  |  | 47 | 47c x 97.0 taker=yes trade_id=8bc3d251-bf45-50f4-9419-06001b14f9fc |  | prints.jsonl
1784072844.926 | 65521.926 | SVA |  |  | 47 | 47c x 20.0 taker=yes trade_id=38058a71-ea12-5efb-9e3c-2c27498629e0 |  | prints.jsonl
1784072851.000 | 65528.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-25774
1784072854.000 | 65531.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-25893
1784072863.000 | 65540.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-26126
1784072864.000 | 65541.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-26140
1784072868.003 | 65545.003 | SVA |  |  | 47 | 47c x 25.02 taker=yes trade_id=38cbd12e-23b7-4ca2-7f70-d967f20fb8a2 |  | prints.jsonl
1784072872.000 | 65549.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-26242
1784072875.000 | 65552.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-26275
1784072880.650 | 65557.650 | LAJ |  |  | 54 | 54c x 892.0 taker=yes trade_id=862aab94-07b5-5cad-3a55-13ee8efc540a |  | prints.jsonl
1784072883.000 | 65560.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-26355
1784072885.000 | 65562.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-26379
1784072886.574 | 65563.574 | SVA |  |  | 47 | 47c x 9.0 taker=yes trade_id=59e88063-7ec9-496d-4f7b-2c0ae90c4f49 |  | prints.jsonl
1784072904.000 | 65581.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-26591
1784072907.000 | 65584.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-26615
1784072922.000 | 65599.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-26989
1784072929.000 | 65606.000 | SVA | 46 | 47 | 46 |  |  | ticks#row-34362
1784072929.745 | 65606.745 | SVA |  |  | 46 | 46c x 10.0 taker=no trade_id=859d0b03-e896-7204-4bcf-779952649b3e |  | prints.jsonl
1784072934.000 | 65611.000 | SVA | 46 | 47 | 49 |  |  | ticks#row-35424
1784072934.696 | 65611.696 | SVA |  |  | 48 | 48c x 100.0 taker=yes trade_id=d0f94ab7-2a97-492b-19bd-b750d05f7ee0 |  | prints.jsonl
1784072934.696 | 65611.696 | SVA |  |  | 49 | 49c x 43.43 taker=yes trade_id=9df60a45-b70d-481f-1fbb-e6176a494671 |  | prints.jsonl
1784072934.696 | 65611.696 | SVA |  |  | 49 | 49c x 228.98 taker=yes trade_id=535c9e29-69b0-4a81-1d29-229a918b8b58 |  | prints.jsonl
1784072991.771 | 65668.771 | SVA |  |  | 48 | 48c x 22.11 taker=yes trade_id=13ed2e64-69e8-40a9-216c-c874d57802d4 |  | prints.jsonl
1784072992.000 | 65669.000 | SVA | 46 | 47 | 48 |  |  | ticks#row-36967
1784073012.000 | 65689.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-31252
1784073017.000 | 65694.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-31445
1784073020.000 | 65697.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-31483
1784073028.000 | 65705.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-38436
1784073028.084 | 65705.084 | SVA |  |  | 47 | 47c x 22.83 taker=yes trade_id=d2a42732-36d5-7774-12a5-9fb3542828e2 |  | prints.jsonl
1784073031.000 | 65708.000 | SVA | 46 | 47 | 46 |  |  | ticks#row-38451
1784073031.654 | 65708.654 | SVA |  |  | 46 | 46c x 10.0 taker=no trade_id=f613e9da-b4ba-6a70-95d0-617c5c702d36 |  | prints.jsonl
1784073044.000 | 65721.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-31947
1784073047.000 | 65724.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-32029
1784073052.000 | 65729.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-32153
1784073052.000 | 65729.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-39030
1784073052.490 | 65729.490 | SVA |  |  | 47 | 47c x 822.21 taker=yes trade_id=8a09f0c7-cf06-5672-a38c-6ec9a7c44ffe |  | prints.jsonl
1784073060.000 | 65737.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-32351
1784073066.000 | 65743.000 | SVA | 46 | 47 | 46 |  |  | ticks#row-39876
1784073066.552 | 65743.552 | SVA |  |  | 46 | 46c x 8.8 taker=no trade_id=de7ff925-4ce2-4584-8300-d6795b8adb36 |  | prints.jsonl
1784073066.891 | 65743.891 | SVA |  |  | 47 | 47c x 30.77 taker=yes trade_id=1ec67354-219f-5fc6-6032-4f70de7552f6 |  | prints.jsonl
1784073068.000 | 65745.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-39884
1784073069.007 | 65746.007 | LAJ |  |  | 54 | 54c x 12.0 taker=yes trade_id=c7bc1cc5-93db-5772-74e7-dc20d611dff5 |  | prints.jsonl
1784073069.007 | 65746.007 | LAJ |  |  | 54 | 54c x 5.0 taker=yes trade_id=1a047947-89d9-528d-6ff1-fbda03ddfe74 |  | prints.jsonl
1784073071.000 | 65748.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-32639
1784073074.000 | 65751.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-32659
1784073079.000 | 65756.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-32750
1784073083.000 | 65760.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-33117
1784073088.000 | 65765.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-33186
1784073091.000 | 65768.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-33197
1784073091.000 | 65768.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-33199
1784073091.000 | 65768.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-33227
1784073093.000 | 65770.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-33258
1784073096.000 | 65773.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-33281
1784073099.000 | 65776.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-33323
1784073102.000 | 65779.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-33436
1784073102.000 | 65779.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-33448
1784073102.000 | 65779.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-33490
1784073105.000 | 65782.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-33519
1784073108.000 | 65785.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-33553
1784073111.000 | 65788.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-33584
1784073114.000 | 65791.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-33593
1784073118.000 | 65795.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-33628
1784073120.000 | 65797.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-33646
1784073120.000 | 65797.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-33656
1784073121.000 | 65798.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-33772
1784073123.000 | 65800.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-33791
1784073124.000 | 65801.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-33838
1784073124.000 | 65801.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-33852
1784073126.000 | 65803.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-33915
1784073129.000 | 65806.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-33961
1784073132.000 | 65809.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-34004
1784073136.000 | 65813.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-34054
1784073138.000 | 65815.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-34066
1784073138.000 | 65815.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-34075
1784073139.000 | 65816.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-34101
1784073142.000 | 65819.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-34152
1784073144.000 | 65821.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-34346
1784073151.000 | 65828.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-34471
1784073154.000 | 65831.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-34816
1784073154.000 | 65831.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-34825
1784073154.000 | 65831.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-34877
1784073156.000 | 65833.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-34906
1784073159.000 | 65836.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-35056
1784073168.000 | 65845.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-35236
1784073171.000 | 65848.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-35396
1784073186.000 | 65863.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-35607
1784073186.000 | 65863.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-35610
1784073186.000 | 65863.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-35613
1784073189.000 | 65866.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-36264
1784073193.000 | 65870.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-36325
1784073198.000 | 65875.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-37616
1784073202.000 | 65879.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-37767
1784073210.000 | 65887.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-38202
1784073210.000 | 65887.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-38217
1784073210.000 | 65887.000 | SVA | 46 | 47 | 48 |  |  | ticks#row-42326
1784073210.115 | 65887.115 | SVA |  |  | 48 | 48c x 0.2 taker=yes trade_id=a1db9d2b-fb39-55be-cae8-a6f0a72479d4 |  | prints.jsonl
1784073215.000 | 65892.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-38319
1784073215.000 | 65892.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-38470
1784073221.000 | 65898.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-38734
1784073221.000 | 65898.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-38844
1784073224.000 | 65901.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-38913
1784073224.000 | 65901.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-38921
1784073227.000 | 65904.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-39112
1784073228.000 | 65905.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-39139
1784073231.000 | 65908.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-39266
1784073232.000 | 65909.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-39360
1784073236.584 | 65913.584 | SVA |  |  | 48 | 48c x 80.4 taker=yes trade_id=03c32a55-4d59-710e-b98d-cbb5ae14138c |  | prints.jsonl
1784073240.000 | 65917.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-39596
1784073240.000 | 65917.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-39610
1784073245.000 | 65922.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-39714
1784073245.000 | 65922.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-39727
1784073248.000 | 65925.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-39946
1784073248.000 | 65925.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-39960
1784073249.000 | 65926.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-40055
1784073249.000 | 65926.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-40069
1784073253.000 | 65930.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-40204
1784073253.000 | 65930.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-40215
1784073262.000 | 65939.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-40592
1784073262.000 | 65939.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-40602
1784073264.000 | 65941.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-40813
1784073264.000 | 65941.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-40824
1784073267.000 | 65944.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-40896
1784073268.000 | 65945.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-40905
1784073271.000 | 65948.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-40987
1784073271.000 | 65948.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-41002
1784073273.363 | 65950.363 | SVA |  |  | 48 | 48c x 10.05 taker=yes trade_id=660bfaed-57b9-5826-2fc8-17d7751e6794 |  | prints.jsonl
1784073274.000 | 65951.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-41070
1784073274.000 | 65951.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-41078
1784073277.000 | 65954.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-41145
1784073277.000 | 65954.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-41154
1784073278.342 | 65955.342 | SVA |  |  | 48 | 48c x 4.02 taker=yes trade_id=f02571a0-905d-7852-2169-6886821afef0 |  | prints.jsonl
1784073279.068 | 65956.068 | SVA |  |  | 48 | 48c x 5.33 taker=yes trade_id=b9dd8fbe-d889-49a6-efa8-84fc5775ed68 |  | prints.jsonl
1784073279.068 | 65956.068 | SVA |  |  | 48 | 48c x 4.72 taker=yes trade_id=1b0ad4bd-d5d2-4a30-c5ac-731a029faf97 |  | prints.jsonl
1784073283.000 | 65960.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-41356
1784073283.000 | 65960.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-41366
1784073286.000 | 65963.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-41460
1784073286.000 | 65963.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-41470
1784073289.000 | 65966.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-41565
1784073289.000 | 65966.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-41579
1784073292.000 | 65969.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-41674
1784073292.000 | 65969.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-41688
1784073295.000 | 65972.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-41768
1784073295.000 | 65972.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-41786
1784073298.000 | 65975.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-41884
1784073298.000 | 65975.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-41902
1784073305.000 | 65982.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-42130
1784073305.000 | 65982.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-42142
1784073308.000 | 65985.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-42388
1784073308.000 | 65985.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-42410
1784073312.000 | 65989.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-42517
1784073312.000 | 65989.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-42527
1784073316.000 | 65993.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-42745
1784073316.000 | 65993.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-42761
1784073316.290 | 65993.290 | SVA |  |  | 46 | 46c x 102.57 taker=no trade_id=26654fdc-1e52-6d1c-4669-7fed1026dbba |  | prints.jsonl
1784073319.000 | 65996.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-42933
1784073319.000 | 65996.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-42936
1784073319.000 | 65996.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-42937
1784073319.000 | 65996.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-42947
1784073321.000 | 65998.000 | SVA | 46 | 47 | 46 |  |  | ticks#row-46182
1784073325.000 | 66002.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-43225
1784073325.000 | 66002.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-43232
1784073327.000 | 66004.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-43298
1784073327.000 | 66004.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-43311
1784073329.000 | 66006.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-43381
1784073329.000 | 66006.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-43394
1784073329.755 | 66006.755 | LAJ |  |  | 54 | 54c x 81.45 taker=yes trade_id=265dc698-cac7-578a-f65d-bd0d6455005d |  | prints.jsonl
1784073334.000 | 66011.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-43580
1784073334.000 | 66011.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-43587
1784073338.000 | 66015.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-43882
1784073338.000 | 66015.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-43896
1784073341.000 | 66018.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-44353
1784073342.000 | 66019.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-44412
1784073348.000 | 66025.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-44843
1784073348.000 | 66025.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-44857
1784073351.000 | 66028.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-45331
1784073351.000 | 66028.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-45346
1784073357.000 | 66034.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-45486
1784073357.000 | 66034.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-45522
1784073360.000 | 66037.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-45552
1784073372.000 | 66049.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-45891
1784073372.000 | 66049.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-45893
1784073372.000 | 66049.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-45907
1784073372.526 | 66049.526 | LAJ |  |  | 54 | 54c x 5.38 taker=yes trade_id=a0eea534-909b-4efa-beea-944e4638700d |  | prints.jsonl
1784073376.000 | 66053.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-45947
1784073384.000 | 66061.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-46156
1784073385.000 | 66062.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-46194
1784073385.000 | 66062.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-46207
1784073386.000 | 66063.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-46289
1784073386.000 | 66063.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-46342
1784073387.000 | 66064.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-46368
1784073387.000 | 66064.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-46385
1784073390.000 | 66067.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-47798
1784073399.000 | 66076.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-47974
1784073428.570 | 66105.570 | LAJ |  |  | 54 | 54c x 10.0 taker=yes trade_id=f52aa0f9-92c3-7ed2-47d0-8ec1ccec80a1 |  | prints.jsonl
1784073440.000 | 66117.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-50960
1784073440.000 | 66117.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-50970
1784073489.591 | 66166.591 | LAJ |  |  | 54 | 54c x 1136.83 taker=yes trade_id=ee773ac1-cd5e-670d-b398-d425f45399cc |  | prints.jsonl
1784073489.591 | 66166.591 | LAJ |  |  | 54 | 54c x 46.0 taker=yes trade_id=e05fd7e9-eeca-61ac-b21a-f32cfab75b83 |  | prints.jsonl
1784073489.591 | 66166.591 | LAJ |  |  | 54 | 54c x 252.17 taker=yes trade_id=d11780ed-f02b-637e-8c33-5d80e8fb42a9 |  | prints.jsonl
1784073489.591 | 66166.591 | LAJ |  |  | 54 | 54c x 5.0 taker=yes trade_id=b2bf126a-bc86-60db-9671-df2b1212fa1b |  | prints.jsonl
1784073489.591 | 66166.591 | LAJ |  |  | 54 | 54c x 1200.0 taker=yes trade_id=5b6c56dc-9890-6873-a34b-d502908e849b |  | prints.jsonl
1784073498.000 | 66175.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-53229
1784073505.000 | 66182.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-53386
1784073508.000 | 66185.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-53417
1784073509.000 | 66186.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-53433
1784073511.000 | 66188.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-53465
1784073513.000 | 66190.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-53492
1784073513.000 | 66190.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-53494
1784073513.000 | 66190.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-53504
1784073516.000 | 66193.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-53513
1784073518.000 | 66195.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-53578
1784073521.000 | 66198.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-53600
1784073526.000 | 66203.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-53655
1784073528.000 | 66205.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-53665
1784073531.000 | 66208.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-53724
1784073534.000 | 66211.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-53757
1784073538.000 | 66215.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-53799
1784073542.000 | 66219.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-53825
1784073545.000 | 66222.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-53885
1784073548.000 | 66225.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-53911
1784073550.000 | 66227.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-55685
1784073550.963 | 66227.963 | SVA |  |  | 47 | 47c x 2.05 taker=yes trade_id=098f9225-0ada-4527-3e07-aa2d141686c4 |  | prints.jsonl
1784073551.000 | 66228.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-53951
1784073554.000 | 66231.000 | LAJ | 53 | 54 | 54 |  |  | ticks#row-53982
1784073667.000 | 66344.000 | SVA | 46 | 48 | 47 |  |  | ticks#row-58529
1784073667.000 | 66344.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-58532
1784073685.000 | 66362.000 | SVA | 46 | 48 | 47 |  |  | ticks#row-59052
1784073685.000 | 66362.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-59054
1784073691.000 | 66368.000 | LAJ | 53 | 55 | 54 |  |  | ticks#row-54912
1784073691.000 | 66368.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-54914
1784073691.059 | 66368.059 | LAJ |  |  | 54 | 54c x 46.0 taker=yes trade_id=f6eb7fe7-bf48-767d-5d31-56c6df219979 |  | prints.jsonl
1784073691.059 | 66368.059 | LAJ |  |  | 55 | 55c x 129.0 taker=yes trade_id=03a2b9cc-d97f-7118-6a58-a8cbeebee99d |  | prints.jsonl
1784073693.665 | 66370.665 | LAJ |  |  | 55 | 55c x 567.66 taker=yes trade_id=f9dd3bdc-aa17-7529-3ddd-0b418eaede23 |  | prints.jsonl
1784073693.665 | 66370.665 | LAJ |  |  | 55 | 55c x 242.0 taker=yes trade_id=d9fc39fa-f5ef-7f30-38ff-6bf64a031a8d |  | prints.jsonl
1784073693.665 | 66370.665 | LAJ |  |  | 55 | 55c x 597.34 taker=yes trade_id=a736a772-6a67-7306-3b31-53a71620e260 |  | prints.jsonl
1784073695.000 | 66372.000 | LAJ | 52 | 55 | 55 |  |  | ticks#row-55115
1784073695.000 | 66372.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-55122
1784073695.000 | 66372.000 | LAJ | 52 | 55 | 55 |  |  | ticks#row-55129
1784073695.000 | 66372.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-55141
1784073695.000 | 66372.000 | LAJ | 52 | 55 | 55 |  |  | ticks#row-55163
1784073695.000 | 66372.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-55167
1784073697.000 | 66374.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-55197
1784073697.000 | 66374.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-59272
1784073700.000 | 66377.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-55248
1784073700.000 | 66377.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-59289
1784073703.000 | 66380.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-55265
1784073703.000 | 66380.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-59418
1784073703.000 | 66380.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-59435
1784073703.000 | 66380.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-59446
1784073706.000 | 66383.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-55310
1784073706.000 | 66383.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-59466
1784073709.000 | 66386.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-55325
1784073709.000 | 66386.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-59564
1784073712.000 | 66389.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-59571
1784073713.000 | 66390.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-55384
1784073715.000 | 66392.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-55410
1784073717.000 | 66394.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-59672
1784073719.000 | 66396.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-55461
1784073719.000 | 66396.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-59686
1784073722.000 | 66399.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-55488
1784073723.000 | 66400.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-59787
1784073725.000 | 66402.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-55542
1784073725.000 | 66402.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-59793
1784073728.000 | 66405.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-55560
1784073728.000 | 66405.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-59884
1784073731.000 | 66408.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-59890
1784073732.000 | 66409.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-55593
1784073734.000 | 66411.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-55610
1784073735.000 | 66412.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-59972
1784073740.000 | 66417.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-55648
1784073740.000 | 66417.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-59982
1784073742.000 | 66419.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-55667
1784073743.000 | 66420.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-60053
1784073745.000 | 66422.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-55713
1784073745.000 | 66422.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-60059
1784073748.000 | 66425.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57183
1784073749.000 | 66426.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-60177
1784073749.000 | 66426.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-60183
1784073750.000 | 66427.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-57211
1784073753.000 | 66430.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57269
1784073753.000 | 66430.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-60268
1784073755.000 | 66432.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-57304
1784073755.000 | 66432.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-60289
1784073757.000 | 66434.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57326
1784073758.000 | 66435.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-60370
1784073760.000 | 66437.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-57375
1784073760.000 | 66437.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-60374
1784073763.000 | 66440.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57391
1784073763.000 | 66440.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-60454
1784073766.000 | 66443.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-57425
1784073766.000 | 66443.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-60464
1784073769.000 | 66446.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57437
1784073769.000 | 66446.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-60517
1784073769.000 | 66446.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-60522
1784073769.000 | 66446.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-60525
1784073771.000 | 66448.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-60544
1784073772.000 | 66449.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-57483
1784073774.000 | 66451.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57504
1784073774.000 | 66451.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-60622
1784073777.000 | 66454.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-60641
1784073778.000 | 66455.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-57544
1784073781.000 | 66458.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57554
1784073782.000 | 66459.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-60873
1784073786.000 | 66463.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-60893
1784073787.000 | 66464.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-57599
1784073790.000 | 66467.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57608
1784073790.000 | 66467.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-60961
1784073793.000 | 66470.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-57644
1784073793.000 | 66470.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-60967
1784073800.000 | 66477.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57660
1784073801.000 | 66478.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-61039
1784073805.000 | 66482.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-57704
1784073805.000 | 66482.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-61042
1784073808.000 | 66485.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57717
1784073808.000 | 66485.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-61108
1784073810.000 | 66487.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-61123
1784073810.907 | 66487.907 | SVA |  |  | 46 | 46c x 23.0 taker=no trade_id=5b2fe820-2a30-64d4-9fae-c3b48afb65f4 |  | prints.jsonl
1784073810.907 | 66487.907 | SVA |  |  | 45 | 45c x 80.64 taker=no trade_id=2ce0ce6a-df98-6075-9abc-e0e7cf733a6e |  | prints.jsonl
1784073810.907 | 66487.907 | SVA |  |  | 46 | 46c x 23.0 taker=no trade_id=0be2456d-ee44-628c-8dd2-95f82fc9c035 |  | prints.jsonl
1784073811.000 | 66488.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-57752
1784073813.000 | 66490.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57765
1784073814.000 | 66491.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-61198
1784073816.000 | 66493.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-61208
1784073817.000 | 66494.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-57808
1784073819.000 | 66496.000 | SVA | 46 | 47 | 46 |  |  | ticks#row-61251
1784073819.000 | 66496.000 | SVA | 45 | 47 | 46 |  |  | ticks#row-61252
1784073819.000 | 66496.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-61254
1784073820.000 | 66497.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57830
1784073820.000 | 66497.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-61275
1784073820.000 | 66497.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-61312
1784073825.000 | 66502.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-57884
1784073825.000 | 66502.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-61330
1784073826.000 | 66503.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57895
1784073826.000 | 66503.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-61403
1784073827.000 | 66504.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-61424
1784073828.000 | 66505.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-57965
1784073829.000 | 66506.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-57979
1784073829.000 | 66506.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-61514
1784073829.000 | 66506.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-61518
1784073829.000 | 66506.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-61522
1784073830.000 | 66507.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58013
1784073830.000 | 66507.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-61542
1784073832.000 | 66509.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58020
1784073832.000 | 66509.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-61650
1784073834.000 | 66511.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58048
1784073834.000 | 66511.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-61669
1784073835.000 | 66512.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58060
1784073835.000 | 66512.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58079
1784073835.000 | 66512.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58083
1784073835.000 | 66512.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-61716
1784073835.000 | 66512.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-61748
1784073835.000 | 66512.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-61764
1784073837.000 | 66514.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58203
1784073837.000 | 66514.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58204
1784073837.000 | 66514.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58209
1784073837.000 | 66514.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-61782
1784073840.000 | 66517.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58241
1784073847.000 | 66524.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58276
1784073848.000 | 66525.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58282
1784073849.000 | 66526.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58303
1784073849.000 | 66526.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58306
1784073851.000 | 66528.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58350
1784073853.000 | 66530.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58355
1784073853.000 | 66530.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58372
1784073853.000 | 66530.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58374
1784073856.000 | 66533.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58430
1784073860.000 | 66537.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58438
1784073861.000 | 66538.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58469
1784073861.000 | 66538.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58470
1784073867.000 | 66544.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58543
1784073871.000 | 66548.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58548
1784073873.165 | 66550.165 | SVA |  |  | 45 | 45c x 204.0 taker=no trade_id=f6ebf1bd-f95c-5dfd-19fe-ca06270a797a |  | prints.jsonl
1784073873.165 | 66550.165 | SVA |  |  | 46 | 46c x 23.0 taker=no trade_id=9a2c2bd6-119d-5ae0-0c50-8b3caa91db2e |  | prints.jsonl
1784073873.165 | 66550.165 | SVA |  |  | 46 | 46c x 23.0 taker=no trade_id=4cc4c0d6-e6e1-5abf-1327-5e8f9742233b |  | prints.jsonl
1784073875.000 | 66552.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58575
1784073875.000 | 66552.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-62545
1784073875.000 | 66552.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-62553
1784073879.000 | 66556.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58587
1784073879.000 | 66556.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-62615
1784073879.000 | 66556.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-62624
1784073879.000 | 66556.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-62634
1784073881.000 | 66558.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58615
1784073881.000 | 66558.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-62647
1784073881.000 | 66558.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-62662
1784073881.000 | 66558.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-62666
1784073885.000 | 66562.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58656
1784073885.000 | 66562.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-62731
1784073887.000 | 66564.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58696
1784073887.000 | 66564.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-62746
1784073889.000 | 66566.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-58729
1784073889.000 | 66566.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-62804
1784073890.000 | 66567.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-58794
1784073890.000 | 66567.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-62826
1784073891.000 | 66568.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59044
1784073892.000 | 66569.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-62942
1784073893.000 | 66570.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-59085
1784073893.000 | 66570.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-62958
1784073895.000 | 66572.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59097
1784073895.000 | 66572.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-63050
1784073896.000 | 66573.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-59160
1784073896.000 | 66573.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-63056
1784073898.000 | 66575.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59203
1784073898.000 | 66575.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-63172
1784073902.000 | 66579.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-63182
1784073903.000 | 66580.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-59236
1784073910.000 | 66587.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59248
1784073910.000 | 66587.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-63227
1784073913.101 | 66590.101 | SVA |  |  | 47 | 47c x 10.0 taker=yes trade_id=a725cebc-7100-62f8-4ce2-bb9b95704808 |  | prints.jsonl
1784073917.000 | 66594.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-59281
1784073917.000 | 66594.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-63251
1784073921.000 | 66598.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59319
1784073921.000 | 66598.000 | SVA | 45 | 47 | 45 |  |  | ticks#row-63300
1784073923.000 | 66600.000 | SVA | 46 | 47 | 45 |  |  | ticks#row-63324
1784073924.000 | 66601.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-59349
1784073924.000 | 66601.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-63354
1784073926.000 | 66603.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59354
1784073926.000 | 66603.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-63400
1784073927.000 | 66604.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-59381
1784073927.000 | 66604.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-63409
1784073928.000 | 66605.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59389
1784073928.000 | 66605.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-63484
1784073929.000 | 66606.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-59441
1784073929.000 | 66606.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-63510
1784073931.000 | 66608.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59452
1784073931.000 | 66608.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-63636
1784073934.000 | 66611.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-59537
1784073934.000 | 66611.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-63653
1784073936.000 | 66613.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59576
1784073936.000 | 66613.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-63770
1784073937.000 | 66614.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-59615
1784073937.000 | 66614.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-63788
1784073939.000 | 66616.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59638
1784073939.000 | 66616.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-63873
1784073943.000 | 66620.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-59670
1784073943.000 | 66620.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-63883
1784073948.000 | 66625.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59680
1784073949.000 | 66626.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-63941
1784073951.000 | 66628.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-59712
1784073951.000 | 66628.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-63952
1784073952.000 | 66629.000 | LAJ | 52 | 55 | 55 |  |  | ticks#row-59747
1784073952.000 | 66629.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-59754
1784073956.000 | 66633.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59768
1784073956.000 | 66633.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-59771
1784073956.000 | 66633.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59777
1784073956.000 | 66633.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-59778
1784073957.000 | 66634.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-59788
1784073959.000 | 66636.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-60145
1784073966.000 | 66643.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-60221
1784073969.000 | 66646.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-60322
1784073971.000 | 66648.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-60327
1784073973.000 | 66650.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-60375
1784073974.000 | 66651.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-60389
1784073978.000 | 66655.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-65299
1784073983.000 | 66660.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-65314
1784073986.000 | 66663.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-60521
1784073988.000 | 66665.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-60542
1784073997.000 | 66674.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-60608
1784073999.000 | 66676.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-60610
1784073999.000 | 66676.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-65457
1784074002.000 | 66679.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-65469
1784074003.000 | 66680.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-60672
1784074006.000 | 66683.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-60700
1784074006.000 | 66683.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-65535
1784074008.000 | 66685.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-60745
1784074008.000 | 66685.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-65559
1784074012.000 | 66689.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-60814
1784074012.000 | 66689.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-65656
1784074015.000 | 66692.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-60889
1784074015.000 | 66692.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-65664
1784074017.000 | 66694.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-60922
1784074017.000 | 66694.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-65757
1784074022.000 | 66699.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-65772
1784074025.000 | 66702.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-60988
1784074029.000 | 66706.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-61010
1784074030.000 | 66707.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-65849
1784074033.000 | 66710.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-61078
1784074033.000 | 66710.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-65867
1784074037.000 | 66714.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-61103
1784074037.000 | 66714.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-65936
1784074040.000 | 66717.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-61132
1784074040.000 | 66717.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-65939
1784074044.000 | 66721.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-61168
1784074044.000 | 66721.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-65997
1784074048.000 | 66725.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-66021
1784074049.000 | 66726.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-61264
1784074053.000 | 66730.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-61294
1784074053.000 | 66730.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-66103
1784074053.000 | 66730.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-66120
1784074054.000 | 66731.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-66149
1784074057.000 | 66734.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-66177
1784074058.000 | 66735.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-61340
1784074060.000 | 66737.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-61379
1784074060.000 | 66737.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-66481
1784074062.000 | 66739.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-66487
1784074064.000 | 66741.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-61443
1784074067.000 | 66744.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-61468
1784074068.000 | 66745.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-61490
1784074068.000 | 66745.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-61493
1784074068.000 | 66745.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-61494
1784074068.000 | 66745.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-66565
1784074068.000 | 66745.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-66572
1784074069.000 | 66746.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-66581
1784074077.000 | 66754.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-66584
1784074078.000 | 66755.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-66606
1784074081.000 | 66758.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-66611
1784074089.000 | 66766.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-66714
1784074091.000 | 66768.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-66723
1784074094.000 | 66771.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-66771
1784074096.000 | 66773.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-66775
1784074100.000 | 66777.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-66868
1784074103.000 | 66780.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-66876
1784074107.000 | 66784.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-66939
1784074109.000 | 66786.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-66946
1784074112.000 | 66789.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-67000
1784074112.000 | 66789.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-67003
1784074112.000 | 66789.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-67008
1784074115.000 | 66792.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-67012
1784074119.000 | 66796.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-67071
1784074120.000 | 66797.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-67075
1784074123.000 | 66800.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-67155
1784074126.000 | 66803.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-67183
1784074130.000 | 66807.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-67234
1784074130.000 | 66807.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-67248
1784074133.000 | 66810.000 | LAJ | 52 | 55 | 55 |  |  | ticks#row-62788
1784074133.000 | 66810.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-62795
1784074133.000 | 66810.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-62806
1784074134.000 | 66811.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-62808
1784074135.000 | 66812.000 | LAJ | 52 | 55 | 55 |  |  | ticks#row-62831
1784074136.000 | 66813.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-62838
1784074136.000 | 66813.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-62856
1784074136.000 | 66813.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-62860
1784074139.000 | 66816.000 | LAJ | 52 | 55 | 55 |  |  | ticks#row-62886
1784074140.000 | 66817.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-62934
1784074143.000 | 66820.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-62947
1784074144.000 | 66821.000 | LAJ | 53 | 55 | 55 |  |  | ticks#row-62956
1784074144.000 | 66821.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-67487
1784074147.000 | 66824.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-67510
1784074158.000 | 66835.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-67653
1784074158.000 | 66835.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-67658
1784074158.000 | 66835.000 | SVA | 45 | 47 | 47 |  |  | ticks#row-67660
1784074159.000 | 66836.000 | SVA | 46 | 47 | 47 |  |  | ticks#row-67697
1784074162.000 | 66839.000 | LAJ | 52 | 55 | 55 |  |  | ticks#row-63224
1784074163.000 | 66840.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-63256
1784074165.000 | 66842.000 | LAJ | 53 | 54 | 55 |  |  | ticks#row-63264
1784074166.000 | 66843.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-63296
1784074238.557 | 66915.557 | LAJ |  |  | 55 | 55c x 41.0 taker=yes trade_id=e367da90-1900-67a2-5ddb-77dd2066978f |  | prints.jsonl
1784074238.557 | 66915.557 | LAJ |  |  | 54 | 54c x 5.0 taker=yes trade_id=47e0779c-ee2d-62f9-45e7-7d0693d270ba |  | prints.jsonl
1784074240.000 | 66917.000 | LAJ | 52 | 55 | 55 |  |  | ticks#row-63327
1784074361.879 | 67038.879 | SVA |  |  | 47 | 47c x 36.0 taker=yes trade_id=5573f1eb-3208-4ce0-1c9e-b677f8380a4c |  | prints.jsonl
1784074369.000 | 67046.000 | SVA | 46 | 48 | 47 |  |  | ticks#row-67883
1784074377.658 | 67054.658 | LAJ |  |  | 55 | 55c x 90.1 taker=yes trade_id=df7f5d73-d910-521e-4ac6-3d5b772ef2ff |  | prints.jsonl
1784074454.584 | 67131.584 | LAJ |  |  | 52 | 52c x 6.0 taker=no trade_id=bd1c171e-ba9c-594d-ac68-8730a548ccec |  | prints.jsonl
1784074454.584 | 67131.584 | LAJ |  |  | 52 | 52c x 23.0 taker=no trade_id=aeb6a349-9398-5162-8bcc-56951a5f857f |  | prints.jsonl
1784074459.000 | 67136.000 | LAJ | 52 | 55 | 52 |  |  | ticks#row-63340
1784074845.986 | 67522.986 | LAJ |  |  | 52 | 52c x 17.0 taker=no trade_id=e6427071-1b34-7451-66dd-b73049607b4c |  | prints.jsonl
1784074845.986 | 67522.986 | LAJ |  |  | 52 | 52c x 23.0 taker=no trade_id=b433e0b9-aae7-725e-587b-c817e1a8e7de |  | prints.jsonl
1784074845.986 | 67522.986 | LAJ |  |  | 52 | 52c x 261.4 taker=no trade_id=260ff9a1-8b69-7900-7de2-c1aa384d2a4b |  | prints.jsonl
1784074966.859 | 67643.859 | LAJ |  |  | 55 | 55c x 25.0 taker=yes trade_id=2f6240ac-2b37-75e2-6916-7207e9d546f4 |  | prints.jsonl
1784074972.000 | 67649.000 | LAJ | 52 | 55 | 55 |  |  | ticks#row-63360
1784075134.460 | 67811.460 | LAJ |  |  | 55 | 55c x 100.47 taker=yes trade_id=43da1084-2573-7792-3b4a-6c3d9333387c |  | prints.jsonl
1784075145.689 | 67822.689 | LAJ |  |  | 55 | 55c x 3.0 taker=yes trade_id=c206a1a6-f947-7ff6-d826-27dcc56a3198 |  | prints.jsonl
1784075180.644 | 67857.644 | LAJ |  |  | 52 | 52c x 2250.64 taker=no trade_id=f467334a-4bdb-7257-1821-5e7d3d3b45a9 |  | prints.jsonl
1784075180.644 | 67857.644 | LAJ |  |  | 52 | 52c x 472.0 taker=no trade_id=f2732703-9080-7d9a-0a9f-9c69ef1b38b6 |  | prints.jsonl
1784075180.644 | 67857.644 | LAJ |  |  | 52 | 52c x 312.36 taker=no trade_id=b85a54ff-1df5-76a4-327a-22795a68d207 |  | prints.jsonl
1784075258.567 | 67935.567 | LAJ |  |  | 55 | 55c x 1.0 taker=yes trade_id=09d24930-2ea7-6e7e-9176-69bbfd0f1d04 |  | prints.jsonl
1784075258.715 | 67935.715 | LAJ |  |  | 55 | 55c x 8.8 taker=yes trade_id=a184776c-f407-7ffe-9dac-a9dae3b3cee4 |  | prints.jsonl
1784075389.031 | 68066.031 | LAJ |  |  | 52 | 52c x 100.47 taker=no trade_id=a080c715-4173-598f-8067-c1bd6648f2c9 |  | prints.jsonl
1784075423.000 | 68100.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-63415
1784075431.000 | 68108.000 | LAJ | 52 | 55 | 55 |  |  | ticks#row-63418
1784075495.529 | 68172.529 | LAJ |  |  | 52 | 52c x 87.0 taker=no trade_id=97b1d246-fe3b-44a7-e876-12183914a779 |  | prints.jsonl
1784075497.633 | 68174.633 | LAJ |  |  | 55 | 55c x 12.0 taker=yes trade_id=85f4c19b-53d3-78c2-a911-28c6361c5738 |  | prints.jsonl
1784075498.000 | 68175.000 | LAJ | 52 | 55 | 52 |  |  | ticks#row-63441
1784075503.000 | 68180.000 | LAJ | 52 | 55 | 55 |  |  | ticks#row-63449
1784075559.367 | 68236.367 | SVA |  |  | 46 | 46c x 11.0 taker=no trade_id=05d4b045-0344-7283-68b8-3585a668368d |  | prints.jsonl
1784075563.000 | 68240.000 | SVA | 46 | 48 | 46 |  |  | ticks#row-68135
1784075568.398 | 68245.398 | LAJ |  |  | 55 | 55c x 8.0 taker=yes trade_id=2d33aa6e-4bef-615a-721e-29335943ae94 |  | prints.jsonl
1784075646.928 | 68323.928 | LAJ |  |  | 55 | 55c x 43.0 taker=yes trade_id=6484352e-62db-64f2-2903-ff9d092b286c |  | prints.jsonl
1784075826.000 | 68503.000 | LAJ | 52 | 54 | 55 |  |  | ticks#row-63480
1784076030.924 | 68707.924 | SVA |  |  | 46 | 46c x 12.0 taker=no trade_id=e9d094be-54cc-483f-7dc0-79634de02435 |  | prints.jsonl
1784076030.924 | 68707.924 | SVA |  |  | 46 | 46c x 23.0 taker=no trade_id=cfb605e4-c30e-463e-778b-09b133395512 |  | prints.jsonl
1784076030.924 | 68707.924 | SVA |  |  | 46 | 46c x 23.0 taker=no trade_id=797513b4-ede1-4953-4e8d-939de3f0f9f4 |  | prints.jsonl
1784076030.924 | 68707.924 | SVA |  |  | 46 | 46c x 78.0 taker=no trade_id=2c5532e1-abcc-409b-52e6-3940e968a6f8 |  | prints.jsonl
1784076084.112 | 68761.112 | LAJ |  |  | 54 | 54c x 10.0 taker=yes trade_id=7558b851-6cb3-56ea-da16-f63e8549bb0c |  | prints.jsonl
1784076171.538 | 68848.538 | SVA |  |  | 48 | 48c x 21.0 taker=yes trade_id=fdb25850-33ea-5a53-7fd1-757b8040607d |  | prints.jsonl
1784076171.538 | 68848.538 | SVA |  |  | 49 | 49c x 157.0 taker=yes trade_id=9e78293e-b24b-5487-60ce-d78d9ac4ac15 |  | prints.jsonl
1784076171.538 | 68848.538 | SVA |  |  | 48 | 48c x 5.0 taker=yes trade_id=22bb57ab-bca6-5257-5514-6c931991fcf5 |  | prints.jsonl
1784076172.000 | 68849.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-63498
1784076172.000 | 68849.000 | SVA | 46 | 49 | 46 |  |  | ticks#row-68305
1784076172.000 | 68849.000 | SVA | 46 | 49 | 49 |  |  | ticks#row-68307
1784076173.000 | 68850.000 | SVA | 46 | 48 | 49 |  |  | ticks#row-68333
1784076186.718 | 68863.718 | SVA |  |  | 48 | 48c x 2.0 taker=yes trade_id=1e7a7442-4e43-77cb-c45a-5a8b8fd095cf |  | prints.jsonl
1784076191.000 | 68868.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-68396
1784076216.000 | 68893.000 | SVA | 46 | 48 | 46 |  |  | ticks#row-68402
1784076216.508 | 68893.508 | SVA |  |  | 46 | 46c x 18.65 taker=no trade_id=10c351d3-bd3a-42e4-a1e7-24bafee04715 |  | prints.jsonl
1784076222.660 | 68899.660 | LAJ |  |  | 52 | 52c x 89.7 taker=no trade_id=6ae002e6-df2b-5653-d1cc-a0acec00bbe9 |  | prints.jsonl
1784076248.000 | 68925.000 | LAJ | 52 | 54 | 52 |  |  | ticks#row-63563
1784076277.000 | 68954.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-68510
1784076277.684 | 68954.684 | SVA |  |  | 48 | 48c x 15.0 taker=yes trade_id=33cde49f-e247-4b03-3b78-ae5328da71e4 |  | prints.jsonl
1784076322.705 | 68999.705 | LAJ |  |  | 54 | 54c x 14.0 taker=yes trade_id=6a284eab-854e-66df-2f8b-ed722ea117ed |  | prints.jsonl
1784076333.000 | 69010.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-63579
1784076508.000 | 69185.000 | SVA | 46 | 48 | 46 |  |  | ticks#row-68867
1784076508.803 | 69185.803 | SVA |  |  | 46 | 46c x 4.35 taker=no trade_id=8ce44fd7-3bf6-550c-867b-0398f5c7cf9d |  | prints.jsonl
1784076508.803 | 69185.803 | SVA |  |  | 46 | 46c x 3.42 taker=no trade_id=82df0b0a-d3d4-5bac-ba36-c4ab8bbf1093 |  | prints.jsonl
1784076508.803 | 69185.803 | SVA |  |  | 46 | 46c x 23.0 taker=no trade_id=2d597c06-4e5d-5ade-ad6c-c0ba978d1a52 |  | prints.jsonl
1784076533.595 | 69210.595 | LAJ |  |  | 54 | 54c x 12.85 taker=yes trade_id=85588ed5-cf7a-6a34-7090-73b1bcf1fac4 |  | prints.jsonl
1784076533.595 | 69210.595 | LAJ |  |  | 54 | 54c x 32.0 taker=yes trade_id=36d56b30-719e-6acb-77bf-d453734f3315 |  | prints.jsonl
1784076545.568 | 69222.568 | LAJ |  |  | 52 | 52c x 3.0 taker=no trade_id=6b2938cf-5193-5e57-84c6-e7d7016409d5 |  | prints.jsonl
1784076548.000 | 69225.000 | LAJ | 52 | 54 | 52 |  |  | ticks#row-63800
1784076558.000 | 69235.000 | SVA | 46 | 47 | 46 |  |  | ticks#row-68946
1784076564.093 | 69241.093 | LAJ |  |  | 52 | 52c x 5.0 taker=no trade_id=39ea32f3-a20f-5573-06b8-a91600ffaa25 |  | prints.jsonl
1784076579.000 | 69256.000 | SVA | 46 | 48 | 46 |  |  | ticks#row-68985
1784076705.526 | 69382.526 | LAJ |  |  | 54 | 54c x 1.79 taker=yes trade_id=7f4cbf2e-c939-7e53-1620-08111c1526f0 |  | prints.jsonl
1784076713.000 | 69390.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-63996
1784076744.000 | 69421.000 | SVA | 46 | 47 | 46 |  |  | ticks#row-69018
1784076745.000 | 69422.000 | SVA | 46 | 48 | 46 |  |  | ticks#row-69033
1784076754.917 | 69431.917 | LAJ |  |  | 54 | 54c x 2.7 taker=yes trade_id=e786503b-e9ad-4f47-3c16-e8e3f8730ea8 |  | prints.jsonl
1784076792.287 | 69469.287 | LAJ |  |  | 54 | 54c x 10.76 taker=yes trade_id=7781caf5-cc41-6e13-9ae4-b40c0e7e3194 |  | prints.jsonl
1784076819.844 | 69496.844 | LAJ |  |  | 54 | 54c x 5.25 taker=yes trade_id=a8c5cc88-f5e5-427e-458c-ac997839e138 |  | prints.jsonl
1784076819.844 | 69496.844 | LAJ |  |  | 54 | 54c x 30.75 taker=yes trade_id=a0549bda-6bfd-45a3-712a-9ec481aab924 |  | prints.jsonl
1784076855.698 | 69532.698 | LAJ |  |  | 54 | 54c x 3.64 taker=yes trade_id=2163b8f2-f511-560e-c610-d7a51c6f8ae8 |  | prints.jsonl
1784076953.000 | 69630.000 | SVA | 45 | 48 | 46 |  |  | ticks#row-69079
1784076960.000 | 69637.000 | SVA | 46 | 48 | 46 |  |  | ticks#row-69096
1784076961.099 | 69638.099 | LAJ |  |  | 54 | 54c x 0.05 taker=yes trade_id=57e47f2b-60e8-6d71-1009-09e3e46992c2 |  | prints.jsonl
1784077104.827 | 69781.827 | LAJ |  |  | 54 | 54c x 3.0 taker=yes trade_id=0d331637-ffd1-4a50-6f79-840b2ebf2288 |  | prints.jsonl
1784077132.154 | 69809.154 | LAJ |  |  | 54 | 54c x 43.0 taker=yes trade_id=5accd531-9a65-69c8-23c5-fdf44fb8c090 |  | prints.jsonl
1784077132.154 | 69809.154 | LAJ |  |  | 54 | 54c x 7.0 taker=yes trade_id=099d941e-ab30-6d04-1e1b-5ed3d8a2b463 |  | prints.jsonl
1784077135.326 | 69812.326 | SVA |  |  | 48 | 48c x 8.0 taker=yes trade_id=b586ab1c-cb63-763b-8c7a-3190e53435e8 |  | prints.jsonl
1784077135.326 | 69812.326 | SVA |  |  | 48 | 48c x 62.0 taker=yes trade_id=075ff086-e3a0-79c9-91f6-2513e02c9a1c |  | prints.jsonl
1784077181.442 | 69858.442 | SVA |  |  | 46 | 46c x 7.77 taker=no trade_id=48b2181d-2639-68b2-7341-47212b3f508f |  | prints.jsonl
1784077181.442 | 69858.442 | SVA |  |  | 46 | 46c x 23.0 taker=no trade_id=2ff85200-a82e-6a2f-77d4-a20d4c29243a |  | prints.jsonl
1784077234.000 | 69911.000 | LAJ | 51 | 54 | 54 |  |  | ticks#row-64390
1784077234.000 | 69911.000 | SVA | 46 | 49 | 46 |  |  | ticks#row-69134
1784077236.000 | 69913.000 | SVA | 47 | 49 | 46 |  |  | ticks#row-69136
1784077236.894 | 69913.894 | LAJ |  |  | 54 | 54c x 22.42 taker=yes trade_id=207eca75-37d0-4d23-f314-36323cc3f71a |  | prints.jsonl
1784077242.560 | 69919.560 | LAJ |  |  | 53 | 53c x 89.0 taker=yes trade_id=28d2071a-a98f-48e1-0283-f62864ef63f7 |  | prints.jsonl
1784077244.000 | 69921.000 | SVA | 46 | 49 | 46 |  |  | ticks#row-69148
1784077247.000 | 69924.000 | LAJ | 51 | 53 | 54 |  |  | ticks#row-64450
1784077247.428 | 69924.428 | SVA |  |  | 49 | 49c x 24.63 taker=yes trade_id=d71fad8f-2aef-7f47-4106-e7094d945771 |  | prints.jsonl
1784077268.000 | 69945.000 | LAJ | 51 | 53 | 53 |  |  | ticks#row-64524
1784077268.329 | 69945.329 | LAJ |  |  | 54 | 54c x 140.0 taker=yes trade_id=2b70fba7-2d03-5da8-b1e7-7c0aaaca16a6 |  | prints.jsonl
1784077291.000 | 69968.000 | LAJ | 51 | 54 | 53 |  |  | ticks#row-64536
1784077291.000 | 69968.000 | SVA | 46 | 49 | 49 |  |  | ticks#row-69238
1784077292.530 | 69969.530 | LAJ |  |  | 54 | 54c x 36.0 taker=yes trade_id=3a588f7f-4540-4e78-0d27-f88624773140 |  | prints.jsonl
1784077293.000 | 69970.000 | LAJ | 51 | 54 | 54 |  |  | ticks#row-64538
1784077447.136 | 70124.136 | SVA |  |  | 49 | 49c x 224.37 taker=yes trade_id=e8e69361-4f53-6943-b8dc-cc3959d36785 |  | prints.jsonl
1784077447.136 | 70124.136 | SVA |  |  | 49 | 49c x 575.26 taker=yes trade_id=a36de684-f8bb-692b-adda-c8741e93489d |  | prints.jsonl
1784077447.136 | 70124.136 | SVA |  |  | 49 | 49c x 46.0 taker=yes trade_id=70b5fe51-5337-6305-908e-b2338d91f903 |  | prints.jsonl
1784077447.136 | 70124.136 | SVA |  |  | 49 | 49c x 139.6 taker=yes trade_id=6f0ed9cf-5b9b-6937-8941-278809222899 |  | prints.jsonl
1784077527.000 | 70204.000 | LAJ | 51 | 53 | 54 |  |  | ticks#row-64546
1784077527.000 | 70204.000 | SVA | 46 | 48 | 49 |  |  | ticks#row-69241
1784077557.477 | 70234.477 | LAJ |  |  | 54 | 54c x 22.0 taker=yes trade_id=47a8040c-d43c-7cbc-115b-23d9c9702a54 |  | prints.jsonl
1784077557.477 | 70234.477 | LAJ |  |  | 53 | 53c x 28.0 taker=yes trade_id=3a31125e-5a29-7716-15fe-5c6997a137ff |  | prints.jsonl
1784077564.000 | 70241.000 | LAJ | 52 | 53 | 54 |  |  | ticks#row-64582
1784077571.000 | 70248.000 | LAJ | 52 | 54 | 53 |  |  | ticks#row-64623
1784077571.000 | 70248.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-64625
1784077572.736 | 70249.736 | SVA |  |  | 48 | 48c x 46.0 taker=yes trade_id=dff4cf6a-db4a-4ea7-c8c4-0f489626561e |  | prints.jsonl
1784077572.736 | 70249.736 | SVA |  |  | 48 | 48c x 5.0 taker=yes trade_id=ca016eaa-6559-4231-fff3-a18ac672e0a8 |  | prints.jsonl
1784077572.736 | 70249.736 | SVA |  |  | 48 | 48c x 10.91 taker=yes trade_id=bb28272c-e5b5-481f-cbc8-922fbccc6f9b |  | prints.jsonl
1784077572.736 | 70249.736 | SVA |  |  | 48 | 48c x 46.0 taker=yes trade_id=ba7b2595-ab79-4047-c193-9b8143d3751a |  | prints.jsonl
1784077572.736 | 70249.736 | SVA |  |  | 48 | 48c x 16.09 taker=yes trade_id=8ffd67e0-f6e9-4b5e-fe7d-d3deb6114a99 |  | prints.jsonl
1784077601.424 | 70278.424 | SVA |  |  | 48 | 48c x 9.98 taker=yes trade_id=3ecef548-8c59-77fb-c731-7e7de927adb3 |  | prints.jsonl
1784077641.000 | 70318.000 | SVA | 46 | 48 | 48 |  |  | ticks#row-69474
1784077697.569 | 70374.569 | SVA |  |  | 46 | 46c x 9.85 taker=no trade_id=d288c555-1eb9-4546-781f-1118581622ff |  | prints.jsonl
1784077706.812 | 70383.812 | LAJ |  |  | 54 | 54c x 61.0 taker=yes trade_id=5eb8f517-686c-5eac-f6c4-4c5c5692f204 |  | prints.jsonl
1784077713.571 | 70390.571 | LAJ |  |  | 54 | 54c x 10.0 taker=yes trade_id=55dd68b3-f850-777c-270c-e19d810f4990 |  | prints.jsonl
1784077733.125 | 70410.125 | SVA |  |  | 48 | 48c x 50.0 taker=yes trade_id=041c03db-de11-4a87-3a93-c18c584adaf7 |  | prints.jsonl
1784077772.949 | 70449.949 | LAJ |  |  | 54 | 54c x 26.0 taker=yes trade_id=c1d53bc8-b3d8-6954-fe09-12c93138fa08 |  | prints.jsonl
1784077787.439 | 70464.439 | SVA |  |  | 48 | 48c x 26.13 taker=yes trade_id=be41e447-595d-5fc3-d5c4-fad453826e13 |  | prints.jsonl
1784077809.454 | 70486.454 | LAJ |  |  | 52 | 52c x 17.91 taker=no trade_id=089886da-edc2-5a68-479f-60c20685f1bc |  | prints.jsonl
1784077818.000 | 70495.000 | LAJ | 52 | 54 | 52 |  |  | ticks#row-64650
1784077830.000 | 70507.000 | LAJ | 52 | 53 | 52 |  |  | ticks#row-64700
1784077853.606 | 70530.606 | LAJ |  |  | 53 | 53c x 16.0 taker=yes trade_id=b061985b-045a-79fe-14b1-2cfb7e8baa75 |  | prints.jsonl
1784077853.606 | 70530.606 | LAJ |  |  | 53 | 53c x 5.0 taker=yes trade_id=7f4075f8-8df8-73e6-18c8-0ccad91cc330 |  | prints.jsonl
1784077860.000 | 70537.000 | LAJ | 52 | 53 | 53 |  |  | ticks#row-64730
1784077862.688 | 70539.688 | LAJ |  |  | 53 | 53c x 25.0 taker=yes trade_id=9562d9d8-6c76-6e26-0a24-fc868b787015 |  | prints.jsonl
1784077872.343 | 70549.343 | LAJ |  |  | 54 | 54c x 439.01 taker=yes trade_id=a3841d85-a2a0-4214-c31c-e3e502ab3c30 |  | prints.jsonl
1784077872.343 | 70549.343 | LAJ |  |  | 53 | 53c x 91.0 taker=yes trade_id=61b85327-9e68-4d2b-cd46-105c1a0d0e45 |  | prints.jsonl
1784077872.343 | 70549.343 | LAJ |  |  | 53 | 53c x 5.0 taker=yes trade_id=3ea88a86-fe72-464a-fad0-fe66ebf85c59 |  | prints.jsonl
1784077872.343 | 70549.343 | LAJ |  |  | 53 | 53c x 5.0 taker=yes trade_id=1cc96b27-c625-445d-f120-545ef8f9a3e6 |  | prints.jsonl
1784077875.278 | 70552.278 | LAJ |  |  | 54 | 54c x 126.0 taker=yes trade_id=2081f5cd-a698-4154-5b3f-bef70e2c4aa8 |  | prints.jsonl
1784077878.000 | 70555.000 | LAJ | 52 | 54 | 53 |  |  | ticks#row-64749
1784077878.000 | 70555.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-64751
1784077915.980 | 70592.980 | SVA |  |  | 48 | 48c x 3.0 taker=yes trade_id=ad339603-3882-6806-d8a1-4880859b57a7 |  | prints.jsonl
1784077979.348 | 70656.348 | LAJ |  |  | 54 | 54c x 10.0 taker=yes trade_id=6a399344-0af8-4824-129d-bcf5d185d2b0 |  | prints.jsonl
1784077990.000 | 70667.000 | LAJ | 52 | 54 | 51 |  |  | ticks#row-64929
1784077990.968 | 70667.968 | LAJ |  |  | 51 | 51c x 140.0 taker=no trade_id=a637e367-61b6-6156-3b06-3b75335131f5 |  | prints.jsonl
1784077995.000 | 70672.000 | LAJ | 52 | 54 | 54 |  |  | ticks#row-64965
1784077995.000 | 70672.000 | LAJ | 52 | 53 | 54 |  |  | ticks#row-64972
1784077995.104 | 70672.104 | LAJ |  |  | 54 | 54c x 10.0 taker=yes trade_id=a4fcb488-34dc-4624-5a64-8109da67a4e8 |  | prints.jsonl
1784078073.000 | 70750.000 | LAJ | 52 | 53 | 53 |  |  | ticks#row-65353
1784078073.936 | 70750.936 | LAJ |  |  | 53 | 53c x 35.0 taker=yes trade_id=61896a00-4810-4d11-e2a3-f26c395cdd31 |  | prints.jsonl
1784078149.000 | 70826.000 | SVA | 47 | 48 | 48 |  |  | ticks#row-70458
1784078149.013 | 70826.013 | SVA |  |  | 48 | 48c x 36.0 taker=yes trade_id=dfe3f42f-6d5e-5fb9-4715-5e16524abe06 |  | prints.jsonl
1784078149.013 | 70826.013 | SVA |  |  | 48 | 48c x 2.0 taker=yes trade_id=40cb987b-5c1a-5f3a-4abf-7ad4b6b7931b |  | prints.jsonl
1784078149.013 | 70826.013 | SVA |  |  | 48 | 48c x 10.0 taker=yes trade_id=0e54128f-8bae-5aad-73ab-72febf2935b0 |  | prints.jsonl
1784078164.092 | 70841.092 | LAJ |  |  | 53 | 53c x 46.0 taker=yes trade_id=dcec4a8f-b9ae-57d4-9ecf-f77a0e97b527 |  | prints.jsonl
1784078164.092 | 70841.092 | LAJ |  |  | 53 | 53c x 11.0 taker=yes trade_id=b494964f-9c64-5c89-a3f2-d9e24ac07f41 |  | prints.jsonl
1784078164.092 | 70841.092 | LAJ |  |  | 53 | 53c x 30.0 taker=yes trade_id=50e2f213-041f-585e-99c0-e038ea4b8272 |  | prints.jsonl
1784078164.092 | 70841.092 | LAJ |  |  | 53 | 53c x 46.0 taker=yes trade_id=35aa2d7e-591a-5f65-9442-46a0a27733b6 |  | prints.jsonl
1784078182.996 | 70859.996 | SVA |  |  | 48 | 48c x 6.0 taker=yes trade_id=5ba55c2c-2b4e-4725-29d1-83559de0eb1e |  | prints.jsonl
1784078219.000 | 70896.000 | SVA | 47 | 49 | 48 |  |  | ticks#row-70500
1784078219.000 | 70896.000 | SVA | 48 | 49 | 48 |  |  | ticks#row-70501
1784078219.745 | 70896.745 | SVA |  |  | 48 | 48c x 100.0 taker=yes trade_id=ad09816b-4df9-4db0-5269-7ec8a7979f64 |  | prints.jsonl
1784078219.745 | 70896.745 | SVA |  |  | 48 | 48c x 10.0 taker=yes trade_id=68accc46-04ea-43a1-7a32-8ee3b94f3697 |  | prints.jsonl
1784078219.745 | 70896.745 | SVA |  |  | 48 | 48c x 4.0 taker=yes trade_id=367adcc8-4b82-46c9-5e5d-2fe95ad2cc1a |  | prints.jsonl
1784078219.745 | 70896.745 | SVA |  |  | 48 | 48c x 5.0 taker=yes trade_id=06c68266-02a9-49a1-4ea1-c5ea94775db9 |  | prints.jsonl
1784078228.382 | 70905.382 | LAJ |  |  | 53 | 53c x 46.0 taker=yes trade_id=c15875c8-b739-4ba9-37d8-649211a06c32 |  | prints.jsonl
1784078228.382 | 70905.382 | LAJ |  |  | 53 | 53c x 44.0 taker=yes trade_id=a5fc1f6f-5960-42df-39ac-c7a490f8a7d5 |  | prints.jsonl
1784078270.000 | 70947.000 | LAJ | 51 | 53 | 53 |  |  | ticks#row-65769
1784078285.295 | 70962.295 | LAJ |  |  | 53 | 53c x 51.0 taker=yes trade_id=9420cb7d-1202-4310-1d3b-cf0ce23357a1 |  | prints.jsonl
1784078285.295 | 70962.295 | LAJ |  |  | 53 | 53c x 2.0 taker=yes trade_id=613bd0fc-c180-4783-3830-395e83066805 |  | prints.jsonl
1784078359.938 | 71036.938 | LAJ |  |  | 53 | 53c x 5.0 taker=yes trade_id=0875d51a-28de-7b64-5244-34d3a7989b9d |  | prints.jsonl
1784078361.001 | 71038.001 | LAJ |  |  |  |  | V6-PASS1 (full 20-stage list, FOUR_STORIES @d521f9dd) REPRICE_REST@47 (before 48) | FOUR_STORIES
1784078361.265 | 71038.265 | LAJ |  |  | 53 | 53c x 3.65 taker=yes trade_id=177840ec-68b2-6dd4-fc63-f042a347f92d |  | prints.jsonl
1784078400.000 | 71077.000 | * |  |  |  |  | TRUE BELL (machine receipt, 18 receipts zero spread) | c0056976
