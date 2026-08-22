# W1 GROUND TRUTH — CORRECTIONS LEDGER (append-only; the table @ c0056976 is never edited)

Reading law: every reader of W1_GROUND_TRUTH_TABLE applies the entries below before grading (L11). Entries are operator-ruled; evidence linked.

## W1TT-C-001 — 26JUL12GIUBAR bell (2026-08-21)
- Ruling: bell = **1783874300 ±60 s** (book-signature), operator relay 2026-08-21; evidence F-VS-037, `GIUBAR_BELL_BAND.json` @ a2c8d842.
- Before: bell 1783876740 (TAPE_INFERENCE ±30 min); BAR floor 16 / close 31, fill 21 PRE_BELL_VALID; GIU floor 49 / close 73, fill 69; COMPLETE 90¢ Δ10.
- After (restated line): span 1783831858..1783874300 · BAR open 31.5, floor **27** @1783841801, close **32** @1783864581, 8 prints, fill 21 @1783875779 **POST_BELL_INVALID** · GIU open 67, floor **66** @1783869375, close **66** @1783872611, 14 prints, fill 69 @1783841972 PRE_BELL_VALID · offered 27+66 = 93 (7¢ under par) · **pair_state PARTIAL_FOR_REASON**, locked delta null · leg ruler GIU 66−69 = −3.
- Downstream: WALK5 game ruler 2/9¢ over 4 final; functionable-v6 GIUBAR (fills 19 @1783875234, 59 @1783876264) both POST_BELL → NEITHER; F24's 32/66 coincide with the corrected closes by accident of an earlier read (method ruling F-VS-023 unchanged).

## W1TT-C-002 — 26JUL14URSPAL bell (2026-08-21)
- Ruling: bell = **1784042247 ±60 s** (tape signature: first mirrored prints PAL 33 / URS 67 at 15:17:27Z), operator relay 2026-08-21; evidence F-VS-031/044/046, `TRUE_BELLS_WALK5.json` @ 0ad0d95e, `REPRODUCTION_AUDIT_d521f9dd.json` @ 17202441.
- Before: bell 1784045100 (TAPE_INFERENCE ±30 min, 47.5 min late); PAL floor 40 / close 41, fill 40; URS floor 57 / close 61, fill 57; COMPLETE 97¢ Δ3.
- After (restated line): span 1784001495..1784042247 · PAL open 38, floor **39** @1784042066, close 41 @1784042108, 20 prints, fill 40 @1784041997 PRE_BELL_VALID (249 s before bell) · URS open 62, floor 57 @1784032697, close 61 @1784041639, 21 prints, fill 57 @1784032697 PRE_BELL_VALID · offered 39+57 = 96 (4¢ under par) · **pair_state COMPLETE_UNDER_PAR_VALID 97¢ Δ3** (unchanged) · leg ruler PAL +1, URS +4.
- Downstream: four-game ledger — GIUBAR PARTIAL (W1TT-C-001), URSPAL COMPLETE 97¢ Δ3, LAJSVA COMPLETE 94¢ Δ6, DANPRA NEITHER, CRIJEA EXCLUDED (walkover) → game ruler **2 completes / 9¢ over 4 gradeable**; leg ruler GIU −3, PAL +1, URS +4, SVA +7, LAJ 0 = **9¢ over 5 valid legs**. Functionable-v6 URSPAL fills 31 @1784042300 and 46 @1784044570 are POST_BELL → NEITHER; lawful ceiling 96¢ (Δ4), v6 capture 0 of 4¢; F-V53-059 URSPAL ceiling void; F-VS-046 closed.
