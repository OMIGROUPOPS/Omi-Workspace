# Game explained — LAJSVA

License: LAW_INDEX read at `dcac4032`, SHA-256 `c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6`; laws L0 L8 L11 L18 L20 L22. Explanation lane only: pass-1 receipts and named custody rows; zero runs, zero passes, zero tuning, zero 804 reads.

Steps-Behind Law: assume the OS is always a few steps behind the market's finesse. This explanation states what was missed, what surprised, and what remains unexplained.

## Receipt bindings

- **R-LAW:** `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LAW_INDEX.md` @ commit `dcac4032`, SHA-256 `c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6`.
- **R-STORY:** `.claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/FOUR_STORIES.md`, SHA-256 `5492ff6d66add7ef96c7c1dae3a7d96f6f48db0f0bb3ec00591e54e2767cba07`.
- **R-RESULT:** `.claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/FOUR_STORIES_RECEIPT.json`, SHA-256 `22381e774e538ed5bc4fe05f7fd50c64efc06d5f61c6f65eb65cde2851049f0d`.
- **R-CORPUS:** `.claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/CORPUS_INDEX.jsonl.gz`, SHA-256 `210951fa9c1bd8d255e6501f7507144311b297b811bd992dd04a1ab46ff37ba1`; row numbers are decompressed JSONL rows.
- **R-RANGE:** external custody `C:\Users\omigr\OMI-Workspace\.corpus-cache-v6\range_spectrum_v1.jsonl`, SHA-256 `1e9891acaaea23a73160aaa26b10b17c87270c1209d9a2a0a23a6a6c56434884`, 130935927 bytes; row/tick refs below.
- **R-HIST:** external custody `C:\Users\omigr\OMI-Workspace\.corpus-cache-v6\historical_events_materialized.csv`, SHA-256 `46741cded0ccb0a24302da4bc7b77f1bb3b82707a8cceaa272a902bae683339a`, 1041339 bytes; physical CSV line refs below.
- **R-PRINTS:** `.claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/TARGET_PRINTS_5.jsonl.gz`, SHA-256 `575784544073ec3e9e84818ffae68203b6d616d51868f65f3cd09559b3af198e`; rows are decompressed JSONL rows. Upstream full tape: `C:\Users\omigr\OMI-Window1-private\fit-local\prints.jsonl`, SHA-256 `e9b5a765b51ddbf0d65364c4f38744ad949ca3c675e5b3a0e472392fbcfabb55`.
- **R-TRUTH:** `c0056976:.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.json`, SHA-256 `f7bc71d8e615859db272d841e125bc4836a685d82bb2d6769762c9bc19e56729`; event row `KXATPCHALLENGERMATCH-26JUL14LAJSVA`, bell 1784078400 (MACHINE_RECEIPT).
- **R-LINEAGE:** external custody `C:\Users\omigr\OMI-Workspace\.claude\window1_live_v4_replay\v54_walk5_live_20260821\FULL_DECISION_TRACE_5.jsonl.gz`, SHA-256 `085fbf04dbc16f8c76691a0823a5370061afc9d738b5eefda9eab92fef4ccbc4`, 55209610 bytes, 133626 rows; only lineage values already printed in R-STORY are used here.
- **R-BOOK-LAJ:** external custody `C:\Users\omigr\OMI-Window1-private\fit-local\ticks\KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz`, SHA-256 `f8445932163996dd1f2fdccc7dfcb5e14f412dc84ae4dc18b7da8dfb304c59ff`, 1735409 bytes, 218561 data rows.
- **R-BOOK-SVA:** external custody `C:\Users\omigr\OMI-Window1-private\fit-local\ticks\KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz`, SHA-256 `48b087d31d1e701f8a84e45d34db59b4f17d15cb2a6237c4ebf80956a897e196`, 1695341 bytes, 208297 data rows.

## 1. The story — hour 0 to bell (242 words; two-page guard passed)

Hour 0 opened around 59/41 and formed quickly, at 0.077778 hours. The first lawful pair was 47 LAJ / 35 SVA. At 2.432880 hours the OS briefly came up to 52/33, then spent the rest of the game oscillating mostly between 47–49 on LAJ and 32–37 on SVA as the named neighborhood changed.

The market was more stable than those eventual-low comparisons. LAJ's deepest lawful pre-bell print was 51 and SVA's was 41, so the tape did offer 92 in separate formation-lawful moments: an 8-cent provisional ceiling that would have preserved the +6 floor. The OS captured neither because its late rests were 47/36, nine cents deeper in total than the two realized lows.

At the bell the final seven neighbors produced weighted low ratios 0.775197 and 0.861969. With anchors 59/41, those ratios, the 53/41 lineage, and the declared neighborhood mass rounded to 47/36; neither pair cap nor post-only cap caused the miss. The miss was therefore in the neighborhood's eventual-low expectation, not in a placement constant.

No reweighting of those same seven neighbors can simultaneously lift the low-side ratio enough for 41 and the high-side ratio enough for 51; the convex receipt proof is below. A new same-stage survival corpus table might change that answer, but pass 1 contains no such table and this lane is forbidden to build or test one. The truthful answer is: the existing declared neighborhood cannot preserve +6, and a corpus adjustment is plausible but unproved.

## 2. Turning points — 7 complete causal chains

### TP1 — 0.000000 hours from discovery (2026-07-14T05:35:23.000Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

LAJ: R-BOOK-LAJ#rows-1..1, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-1 = 5/86 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=LAJ,ts<=1784007323.000 (0 rows)

SVA: R-BOOK-SVA#rows-1..1, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-1 = 5/86 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=SVA,ts<=1784007323.000 (0 rows)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"LAJ":0,"SVA":0},"anchors_cents":{"LAJ":59,"SVA":41}}` | R-STORY#line-285; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":18}` | R-STORY#line-285; raw cumulative prefixes above |
| drift | `{"LAJ":{"current_cents":45,"drift_cents":-14},"SVA":{"current_cents":45,"drift_cents":4}}` | R-STORY#line-285; raw cumulative prefixes above |
| steps_stillness | `{"LAJ":{"step_count":0,"last_step_cents":null,"still_seconds":0},"SVA":{"step_count":0,"last_step_cents":null,"still_seconds":0}}` | R-STORY#line-285; raw cumulative prefixes above |
| shape_survival | `{"LAJ":{"directional_step_share":null,"observed_steps":0},"SVA":{"directional_step_share":null,"observed_steps":0}}` | R-STORY#line-285; raw cumulative prefixes above |
| ripeness | `{"LAJ":{"continuous_evidence_mass":0.5,"observations":1,"prints":0},"SVA":{"continuous_evidence_mass":0.5,"observations":1,"prints":0}}` | R-STORY#line-285; raw cumulative prefixes above |
| lows_travel | `{"LAJ":{"low_cents":45,"high_cents":45,"travel_cents":0},"SVA":{"low_cents":45,"high_cents":45,"travel_cents":0}}` | R-STORY#line-285; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":90,"spread_sum_cents":162,"dwell_seconds":{"LAJ":0,"SVA":0}}` | R-STORY#line-285; raw cumulative prefixes above |
| divots | `{"LAJ":{"count":0,"mean_depth_cents":null,"latest":null},"SVA":{"count":0,"mean_depth_cents":null,"latest":null}}` | R-STORY#line-285; raw cumulative prefixes above |
| depth_size | `{"LAJ":{"bid_depth_5":9042,"ask_depth_5":311,"bid_share":0.9667486368010264,"top_bid_size":250,"top_ask_size":99},"SVA":{"bid_depth_5":9192,"ask_depth_5":316,"bid_share":0.9667648296171645,"top_bid_size":250,"top_ask_size":99}}` | R-STORY#line-285; raw cumulative prefixes above |
| volume | `{"LAJ":{"print_count":0,"contracts":0},"SVA":{"print_count":0,"contracts":0}}` | R-STORY#line-285; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.4736842105263158,"drift_sum_cents":-10,"both_legs_named":true}` | R-STORY#line-285; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-285; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":0,"hours_to_truth_bell":19.74361111111111,"bell_source":"MACHINE_RECEIPT"}` | R-STORY#line-285; raw cumulative prefixes above |
| books | `{"LAJ":{"bid_cents":5,"ask_cents":86,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-1"},"SVA":{"bid_cents":5,"ask_cents":86,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-1"}}` | R-STORY#line-285; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":0,"legs":{"LAJ":{"credited":false,"entry_cents":null,"standing_target_cents":null},"SVA":{"credited":false,"entry_cents":null,"standing_target_cents":null}}}` | R-STORY#line-285; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":18,"leg0_anchor_cents":41,"leg1_anchor_cents":59,"leg0_drift_cents":4,"leg1_drift_cents":-14,"leg0_travel_cents":0,"leg1_travel_cents":0,"joint_mid_sum_cents":90,"joint_spread_cents":162,"inverse_coherence":0.4736842105263158,"volume_log1p":0,"hours_from_discovery":0,"divot_depth_cents":null,"oriented_leg_ids":["SVA","LAJ"]}` [R-STORY#line-285; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXWTACHALLENGERMATCH-26JUN14LEOKUL (26JUN) | 0.543595 / 0.945205 | R-CORPUS#row-9693; RANGE_SPECTRUM_PATH | R-RANGE#row-4604; LEO anchor 46 (tick#48[1781416329,5,46,46]), low 46 (tick#48[1781416329,5,46,46]), close 55 (terminal tick#72[1781424913,59,64,55]); KUL anchor 63 (tick#48[1781416329,31,63,63]), low 40 (tick#60[1781420280,38,40,41]), close 40 (terminal tick#72[1781424913,38,40,40]) |
| N2 | KXATPCHALLENGERMATCH-26MAR05CECKYM (26MAR) | 0.477093 / 0.732877 | R-CORPUS#row-4109; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-5512; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N3 | KXATPCHALLENGERMATCH-26MAY12HUEVAR (26MAY) | 0.465430 / 0.945205 | R-CORPUS#row-5502; RANGE_SPECTRUM_PATH | R-RANGE#row-2434; HUE anchor 38 (tick#56[1778591972,38,84,0]), low 21 (tick#75[1778597698,21,33,38]), close 21 (terminal tick#95[1778603748,16,24,21]); VAR anchor 64 (tick#55[1778591671,12,64,0]), low 64 (tick#55[1778591671,12,64,0]), close 86 (terminal tick#95[1778603748,76,86,86]) |
| N4 | KXATPCHALLENGERMATCH-26MAY10LOMNED (26MAY) | 0.463316 / 0.945205 | R-CORPUS#row-5374; RANGE_SPECTRUM_PATH | R-RANGE#row-2313; NED anchor 45 (tick#98[1778411214,19,35,45]), low 38 (tick#101[1778412119,30,37,38]), close 39 (terminal tick#109[1778414539,40,45,39]); LOM anchor 76 (tick#98[1778411214,63,79,76]), low 52 (tick#108[1778414229,45,51,52]), close 57 (terminal tick#109[1778414539,53,59,57]) |
| N5 | KXATPCHALLENGERMATCH-26MAY31SCOHON (26MAY) | 0.454443 / 0.945205 | R-CORPUS#row-6115; RANGE_SPECTRUM_PATH | R-RANGE#row-3022; SCO anchor 13 (tick#62[1780204147,10,13,0]), low 9 (tick#63[1780204448,9,13,0]), close 13 (terminal tick#96[1780214399,9,13,13]); HON anchor 90 (tick#8[1780187867,10,90,0]), low 90 (tick#8[1780187867,10,90,0]), close 90 (terminal tick#96[1780214399,87,90,90]) |
| N6 | KXATPCHALLENGERMATCH-26FEB22KUKLOF (26FEB) | 0.436078 / 0.732877 | R-CORPUS#row-1471; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-751; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N7 | KXATPCHALLENGERMATCH-26MAR05HEMGEA (26MAR) | 0.432228 / 0.732877 | R-CORPUS#row-4115; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-5511; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |

**Derivation arithmetic → action → verbatim sentence.**

**LAJ.** Formation progress 0.000000 < 1 overrides the computed candidate; lawful action is HOLD_REST@NONE.

> At 0.000000 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXWTACHALLENGERMATCH-26JUN14LEOKUL@0.543595, KXATPCHALLENGERMATCH-26MAR05CECKYM@0.477093, KXATPCHALLENGERMATCH-26MAY12HUEVAR@0.465430, KXATPCHALLENGERMATCH-26MAY10LOMNED@0.463316, KXATPCHALLENGERMATCH-26MAY31SCOHON@0.454443, KXATPCHALLENGERMATCH-26FEB22KUKLOF@0.436078, KXATPCHALLENGERMATCH-26MAR05HEMGEA@0.432228. LAJ has anchor 59, neighborhood low ratio 0.8767344685011376, lineage target NONE, pair cap 98, and post-only cap 85. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=NONE; ACTIVE_TARGET_BEFORE_CENTS=NONE.

**SVA.** Formation progress 0.000000 < 1 overrides the computed candidate; lawful action is HOLD_REST@NONE.

> At 0.000000 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXWTACHALLENGERMATCH-26JUN14LEOKUL@0.543595, KXATPCHALLENGERMATCH-26MAR05CECKYM@0.477093, KXATPCHALLENGERMATCH-26MAY12HUEVAR@0.465430, KXATPCHALLENGERMATCH-26MAY10LOMNED@0.463316, KXATPCHALLENGERMATCH-26MAY31SCOHON@0.454443, KXATPCHALLENGERMATCH-26FEB22KUKLOF@0.436078, KXATPCHALLENGERMATCH-26MAR05HEMGEA@0.432228. SVA has anchor 41, neighborhood low ratio 0.7652290138431287, lineage target NONE, pair cap 98, and post-only cap 85. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=NONE; ACTIVE_TARGET_BEFORE_CENTS=NONE.

### TP3 — 0.077778 hours from discovery (2026-07-14T05:40:03.000Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

LAJ: R-BOOK-LAJ#rows-1..51, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-51 = 54/86 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=LAJ,ts<=1784007603.001 (0 rows)

SVA: R-BOOK-SVA#rows-1..57, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-57 = 36/86 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=SVA,ts<=1784007603.001 (0 rows)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"LAJ":1,"SVA":1},"anchors_cents":{"LAJ":59,"SVA":41}}` | R-STORY#line-297; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":18}` | R-STORY#line-297; raw cumulative prefixes above |
| drift | `{"LAJ":{"current_cents":70,"drift_cents":11},"SVA":{"current_cents":61,"drift_cents":20}}` | R-STORY#line-297; raw cumulative prefixes above |
| steps_stillness | `{"LAJ":{"step_count":14,"last_step_cents":11,"still_seconds":0},"SVA":{"step_count":17,"last_step_cents":20,"still_seconds":0}}` | R-STORY#line-297; raw cumulative prefixes above |
| shape_survival | `{"LAJ":{"directional_step_share":0.42857142857142855,"observed_steps":14},"SVA":{"directional_step_share":0.4117647058823529,"observed_steps":17}}` | R-STORY#line-297; raw cumulative prefixes above |
| ripeness | `{"LAJ":{"continuous_evidence_mass":0.9818181818181818,"observations":54,"prints":0},"SVA":{"continuous_evidence_mass":0.9836065573770492,"observations":60,"prints":0}}` | R-STORY#line-297; raw cumulative prefixes above |
| lows_travel | `{"LAJ":{"low_cents":44,"high_cents":70,"travel_cents":26},"SVA":{"low_cents":41,"high_cents":61,"travel_cents":20}}` | R-STORY#line-297; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":131,"spread_sum_cents":82,"dwell_seconds":{"LAJ":0,"SVA":0}}` | R-STORY#line-297; raw cumulative prefixes above |
| divots | `{"LAJ":{"count":2,"mean_depth_cents":2,"latest":{"timestamp_epoch":1784007487,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-45","floor_cents":45,"depth_cents":1}},"SVA":{"count":4,"mean_depth_cents":1.5,"latest":{"timestamp_epoch":1784007487,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-50","floor_cents":45,"depth_cents":1}}}` | R-STORY#line-297; raw cumulative prefixes above |
| depth_size | `{"LAJ":{"bid_depth_5":2439,"ask_depth_5":311,"bid_share":0.8869090909090909,"top_bid_size":500,"top_ask_size":99},"SVA":{"bid_depth_5":2439,"ask_depth_5":316,"bid_share":0.8852994555353902,"top_bid_size":500,"top_ask_size":99}}` | R-STORY#line-297; raw cumulative prefixes above |
| volume | `{"LAJ":{"print_count":0,"contracts":0},"SVA":{"print_count":0,"contracts":0}}` | R-STORY#line-297; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.03125,"drift_sum_cents":31,"both_legs_named":true}` | R-STORY#line-297; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-297; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":0.07777777777777778,"hours_to_truth_bell":19.66583333333333,"bell_source":"MACHINE_RECEIPT"}` | R-STORY#line-297; raw cumulative prefixes above |
| books | `{"LAJ":{"bid_cents":54,"ask_cents":86,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-51"},"SVA":{"bid_cents":36,"ask_cents":86,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-57"}}` | R-STORY#line-297; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":0,"legs":{"LAJ":{"credited":false,"entry_cents":null,"standing_target_cents":null},"SVA":{"credited":false,"entry_cents":null,"standing_target_cents":null}}}` | R-STORY#line-297; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":18,"leg0_anchor_cents":41,"leg1_anchor_cents":59,"leg0_drift_cents":20,"leg1_drift_cents":11,"leg0_travel_cents":20,"leg1_travel_cents":26,"joint_mid_sum_cents":131,"joint_spread_cents":82,"inverse_coherence":0.03125,"volume_log1p":0,"hours_from_discovery":0.07777777777777778,"divot_depth_cents":1.75,"oriented_leg_ids":["SVA","LAJ"]}` [R-STORY#line-297; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26MAY03HUEDOS (26MAY) | 0.570339 / 1.000000 | R-CORPUS#row-5169; RANGE_SPECTRUM_PATH | R-RANGE#row-2131; DOS anchor 34 (tick#1[1777884804,9,62,34]), low 34 (tick#1[1777884804,9,62,34]), close 37 (terminal tick#95[1777913230,9,49,37]); HUE anchor 90 (tick#1[1777884804,68,90,90]), low 66 (tick#29[1777893263,33,90,66]), close 90 (terminal tick#95[1777913230,49,90,90]) |
| N2 | KXATPCHALLENGERMATCH-26JUN14RIBREC (26JUN) | 0.563420 / 1.000000 | R-CORPUS#row-3388; RANGE_SPECTRUM_PATH | R-RANGE#row-1532; REC anchor 44 (tick#1[1781398808,44,54,0]), low 44 (tick#1[1781398808,44,54,0]), close 53 (terminal tick#85[1781430166,40,42,53]); RIB anchor 77 (tick#5[1781400034,23,77,0]), low 43 (tick#42[1781414186,43,79,77]), close 60 (terminal tick#85[1781430166,58,60,60]) |
| N3 | KXATPCHALLENGERMATCH-26JUN01STRMOE (26JUN) | 0.563382 / 1.000000 | R-CORPUS#row-2906; RANGE_SPECTRUM_PATH | R-RANGE#row-1055; MOE anchor 41 (tick#38[1780321222,23,41,41]), low 37 (tick#51[1780325176,37,43,43]), close 44 (terminal tick#54[1780326103,43,44,44]); STR anchor 70 (tick#38[1780321222,67,90,70]), low 54 (tick#49[1780324561,54,55,55]), close 59 (terminal tick#54[1780326103,55,57,59]) |
| N4 | KXATPCHALLENGERMATCH-26JUN17KICHUE (26JUN) | 0.549556 / 1.000000 | R-CORPUS#row-3564; RANGE_SPECTRUM_PATH | R-RANGE#row-1707; HUE anchor 43 (tick#26[1781703299,6,43,43]), low 14 (tick#81[1781721759,12,50,14]), close 25 (terminal tick#87[1781723567,26,33,25]); KIC anchor 68 (tick#26[1781703299,5,88,68]), low 62 (tick#29[1781704206,61,80,62]), close 73 (terminal tick#87[1781723567,66,73,73]) |
| N5 | KXATPCHALLENGERMATCH-26JUN23ANDHUE (26JUN) | 0.549476 / 1.000000 | R-CORPUS#row-3695; RANGE_SPECTRUM_PATH | R-RANGE#row-1837; HUE anchor 54 (tick#1[1782368100,23,53,54]), low 45 (tick#6[1782391324,45,47,52]), close 45 (terminal tick#12[1782393167,31,43,45]); AND anchor 77 (tick#1[1782368100,56,77,77]), low 56 (tick#1[1782368100,56,77,77]), close 78 (terminal tick#12[1782393167,56,78,78]) |
| N6 | KXWTAMATCH-26JUN23SEBORT (26JUN) | 0.542438 / 1.000000 | R-CORPUS#row-11587; RANGE_SPECTRUM_PATH | R-RANGE#row-5413; SEB anchor 54 (tick#5[1782212066,15,48,54]), low 54 (tick#5[1782212066,15,48,54]), close 54 (terminal tick#5[1782212066,15,48,54]); ORT anchor 68 (tick#2[1782210800,12,88,68]), low 60 (tick#4[1782211749,59,73,60]), close 74 (terminal tick#5[1782212066,69,73,74]) |
| N7 | KXATPCHALLENGERMATCH-26JUN07ZEBMAR (26JUN) | 0.531993 / 1.000000 | R-CORPUS#row-3134; RANGE_SPECTRUM_PATH | R-RANGE#row-1283; ZEB anchor 44 (tick#6[1780835226,36,44,0]), low 37 (tick#40[1780846176,37,44,44]), close 60 (terminal tick#91[1780862311,20,59,60]); MAR anchor 63 (tick#26[1780841928,56,63,0]), low 62 (tick#40[1780846176,56,62,63]), close 80 (terminal tick#91[1780862311,40,85,80]) |

**Derivation arithmetic → action → verbatim sentence.**

**LAJ.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAY03HUEDOS:(0.570339×1.000000)×(66/90) + KXATPCHALLENGERMATCH-26JUN14RIBREC:(0.563420×1.000000)×(43/77) + KXATPCHALLENGERMATCH-26JUN01STRMOE:(0.563382×1.000000)×(54/70) + KXATPCHALLENGERMATCH-26JUN17KICHUE:(0.549556×1.000000)×(62/68) + KXATPCHALLENGERMATCH-26JUN23ANDHUE:(0.549476×1.000000)×(56/77) + KXWTAMATCH-26JUN23SEBORT:(0.542438×1.000000)×(60/68) + KXATPCHALLENGERMATCH-26JUN07ZEBMAR:(0.531993×1.000000)×(62/63)) / 3.870603 = 0.793248273899. Raw round(59×0.793248273899)=47; mass=0.552943353423; blend with lineage NONE gives 47; min(pair cap 98, post-only cap 85) gives 47. Printed action PLACE_REST@47, active-before NONE.

> At 0.077778 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXATPCHALLENGERMATCH-26MAY03HUEDOS@0.570339, KXATPCHALLENGERMATCH-26JUN14RIBREC@0.563420, KXATPCHALLENGERMATCH-26JUN01STRMOE@0.563382, KXATPCHALLENGERMATCH-26JUN17KICHUE@0.549556, KXATPCHALLENGERMATCH-26JUN23ANDHUE@0.549476, KXWTAMATCH-26JUN23SEBORT@0.542438, KXATPCHALLENGERMATCH-26JUN07ZEBMAR@0.531993. LAJ has anchor 59, neighborhood low ratio 0.7932482738988199, lineage target NONE, pair cap 98, and post-only cap 85. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=47; ACTIVE_TARGET_BEFORE_CENTS=NONE.

**SVA.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAY03HUEDOS:(0.570339×1.000000)×(34/34) + KXATPCHALLENGERMATCH-26JUN14RIBREC:(0.563420×1.000000)×(44/44) + KXATPCHALLENGERMATCH-26JUN01STRMOE:(0.563382×1.000000)×(37/41) + KXATPCHALLENGERMATCH-26JUN17KICHUE:(0.549556×1.000000)×(14/43) + KXATPCHALLENGERMATCH-26JUN23ANDHUE:(0.549476×1.000000)×(45/54) + KXWTAMATCH-26JUN23SEBORT:(0.542438×1.000000)×(54/54) + KXATPCHALLENGERMATCH-26JUN07ZEBMAR:(0.531993×1.000000)×(37/44)) / 3.870603 = 0.844517963419. Raw round(41×0.844517963419)=35; mass=0.552943353423; blend with lineage NONE gives 35; min(pair cap 98, post-only cap 85) gives 35. Printed action PLACE_REST@35, active-before NONE.

> At 0.077778 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXATPCHALLENGERMATCH-26MAY03HUEDOS@0.570339, KXATPCHALLENGERMATCH-26JUN14RIBREC@0.563420, KXATPCHALLENGERMATCH-26JUN01STRMOE@0.563382, KXATPCHALLENGERMATCH-26JUN17KICHUE@0.549556, KXATPCHALLENGERMATCH-26JUN23ANDHUE@0.549476, KXWTAMATCH-26JUN23SEBORT@0.542438, KXATPCHALLENGERMATCH-26JUN07ZEBMAR@0.531993. SVA has anchor 41, neighborhood low ratio 0.8445179634185196, lineage target NONE, pair cap 98, and post-only cap 85. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=35; ACTIVE_TARGET_BEFORE_CENTS=NONE.

### TP5 — 2.432880 hours from discovery (2026-07-14T08:01:21.368Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

LAJ: R-BOOK-LAJ#rows-1..183, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-183 = 59/62 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=LAJ,ts<=1784016081.368 (1 rows; last #row-4268 51ffb46a-c62c-6890-aa69-cd9970de51c6@62)

SVA: R-BOOK-SVA#rows-1..192, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-192 = 37/41 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=SVA,ts<=1784016081.368 (0 rows)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"LAJ":1,"SVA":1},"anchors_cents":{"LAJ":59,"SVA":41}}` | R-STORY#line-309; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":18}` | R-STORY#line-309; raw cumulative prefixes above |
| drift | `{"LAJ":{"current_cents":62,"drift_cents":3},"SVA":{"current_cents":39,"drift_cents":-2}}` | R-STORY#line-309; raw cumulative prefixes above |
| steps_stillness | `{"LAJ":{"step_count":31,"last_step_cents":2,"still_seconds":0},"SVA":{"step_count":22,"last_step_cents":1,"still_seconds":2769.367000102997}}` | R-STORY#line-309; raw cumulative prefixes above |
| shape_survival | `{"LAJ":{"directional_step_share":0.4838709677419355,"observed_steps":31},"SVA":{"directional_step_share":0.5909090909090909,"observed_steps":22}}` | R-STORY#line-309; raw cumulative prefixes above |
| ripeness | `{"LAJ":{"continuous_evidence_mass":0.9945945945945946,"observations":184,"prints":1},"SVA":{"continuous_evidence_mass":0.9948186528497409,"observations":192,"prints":0}}` | R-STORY#line-309; raw cumulative prefixes above |
| lows_travel | `{"LAJ":{"low_cents":44,"high_cents":70,"travel_cents":26},"SVA":{"low_cents":38,"high_cents":61,"travel_cents":23}}` | R-STORY#line-309; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":101,"spread_sum_cents":7,"dwell_seconds":{"LAJ":0,"SVA":2769.367000102997}}` | R-STORY#line-309; raw cumulative prefixes above |
| divots | `{"LAJ":{"count":3,"mean_depth_cents":1.6666666666666667,"latest":{"timestamp_epoch":1784011407,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-143","floor_cents":60,"depth_cents":1}},"SVA":{"count":4,"mean_depth_cents":1.5,"latest":{"timestamp_epoch":1784007487,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-50","floor_cents":45,"depth_cents":1}}}` | R-STORY#line-309; raw cumulative prefixes above |
| depth_size | `{"LAJ":{"bid_depth_5":5209,"ask_depth_5":4278,"bid_share":0.5490671445135449,"top_bid_size":800,"top_ask_size":2},"SVA":{"bid_depth_5":4131,"ask_depth_5":5373,"bid_share":0.4346590909090909,"top_bid_size":800,"top_ask_size":843}}` | R-STORY#line-309; raw cumulative prefixes above |
| volume | `{"LAJ":{"print_count":1,"contracts":3},"SVA":{"print_count":0,"contracts":0}}` | R-STORY#line-309; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.8333333333333334,"drift_sum_cents":1,"both_legs_named":true}` | R-STORY#line-309; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-309; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":2.4328797222508323,"hours_to_truth_bell":17.31073138886028,"bell_source":"MACHINE_RECEIPT"}` | R-STORY#line-309; raw cumulative prefixes above |
| books | `{"LAJ":{"bid_cents":59,"ask_cents":62,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-183"},"SVA":{"bid_cents":37,"ask_cents":41,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-192"}}` | R-STORY#line-309; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":2,"legs":{"LAJ":{"credited":false,"entry_cents":null,"standing_target_cents":47},"SVA":{"credited":false,"entry_cents":null,"standing_target_cents":34}}}` | R-STORY#line-309; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":18,"leg0_anchor_cents":41,"leg1_anchor_cents":59,"leg0_drift_cents":-2,"leg1_drift_cents":3,"leg0_travel_cents":23,"leg1_travel_cents":26,"joint_mid_sum_cents":101,"joint_spread_cents":7,"inverse_coherence":0.8333333333333334,"volume_log1p":1.3862943611198906,"hours_from_discovery":2.4328797222508323,"divot_depth_cents":1.5833333333333335,"oriented_leg_ids":["SVA","LAJ"]}` [R-STORY#line-309; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26JUN29STAGHA (26JUN) | 0.892611 / 1.000000 | R-CORPUS#row-3877; RANGE_SPECTRUM_PATH | R-RANGE#row-2010; GHA anchor 42 (tick#1[1782698685,40,41,42]), low 38 (tick#7[1782700547,38,40,42]), close 38 (terminal tick#89[1782728570,38,40,38]); STA anchor 59 (tick#1[1782698685,58,59,59]), low 46 (tick#88[1782728249,43,46,46]), close 62 (terminal tick#89[1782728570,60,62,62]) |
| N2 | KXATPCHALLENGERMATCH-26MAY25GOMSAK (26MAY) | 0.875800 / 1.000000 | R-CORPUS#row-5893; RANGE_SPECTRUM_PATH | R-RANGE#row-2811; GOM anchor 42 (tick#3[1779678151,41,42,0]), low 40 (tick#4[1779678466,40,42,0]), close 40 (terminal tick#92[1779708384,39,40,40]); SAK anchor 59 (tick#1[1779677526,56,58,59]), low 46 (tick#91[1779708054,45,47,46]), close 61 (terminal tick#92[1779708384,59,61,61]) |
| N3 | KXATPCHALLENGERMATCH-26JUL11GIUDAM (26JUL) | 0.875289 / 1.000000 | R-CORPUS#row-2603; RANGE_SPECTRUM_PATH | R-RANGE#row-753; DAM anchor 42 (tick#1[1783745871,41,42,42]), low 31 (tick#92[1783776472,29,31,31]), close 41 (terminal tick#94[1783777409,40,41,41]); GIU anchor 59 (tick#1[1783745871,58,59,59]), low 51 (tick#90[1783775532,51,52,51]), close 60 (terminal tick#94[1783777409,59,60,60]) |
| N4 | KXATPCHALLENGERMATCH-26JUL13VUKBRO (26JUL) | 0.872677 / 1.000000 | R-CORPUS#row-2731; RANGE_SPECTRUM_PATH | R-RANGE#row-881; VUK anchor 41 (tick#1[1783964503,41,43,41]), low 32 (tick#68[1783993775,26,27,32]), close 37 (terminal tick#70[1783994716,36,37,37]); BRO anchor 59 (tick#1[1783964503,57,59,59]), low 56 (tick#40[1783983230,57,58,56]), close 65 (terminal tick#70[1783994716,64,65,65]) |
| N5 | KXATPCHALLENGERMATCH-26APR20DOUJUB (26APR) | 0.865672 / 1.000000 | R-CORPUS#row-341; RANGE_SPECTRUM_PATH | R-RANGE#row-2; DOU anchor 43 (tick#1[1776786312,41,43,43]), low 16 (tick#13[1776789951,16,18,16]), close 36 (terminal tick#14[1776790253,30,32,36]); JUB anchor 59 (tick#1[1776786312,57,59,59]), low 57 (tick#1[1776786312,57,59,59]), close 68 (terminal tick#14[1776790253,66,69,68]) |
| N6 | KXATPCHALLENGERMATCH-26MAY14RIEKEC (26MAY) | 0.864827 / 1.000000 | R-CORPUS#row-5622; RANGE_SPECTRUM_PATH | R-RANGE#row-2551; RIE anchor 39 (tick#1[1778720505,37,39,39]), low 34 (tick#81[1778744718,34,37,37]), close 36 (terminal tick#102[1778751065,36,38,36]); KEC anchor 62 (tick#1[1778720505,61,64,62]), low 51 (tick#101[1778750763,46,55,51]), close 64 (terminal tick#102[1778751065,62,63,64]) |
| N7 | KXATPCHALLENGERMATCH-26MAY28MONMAY (26MAY) | 0.862405 / 1.000000 | R-CORPUS#row-6019; RANGE_SPECTRUM_PATH | R-RANGE#row-2931; MAY anchor 42 (tick#1[1780055836,40,42,42]), low 36 (tick#60[1780073626,36,41,36]), close 40 (terminal tick#96[1780084471,40,41,40]); MON anchor 59 (tick#1[1780055836,57,59,59]), low 55 (tick#72[1780077241,55,62,57]), close 60 (terminal tick#96[1780084471,60,62,60]) |

**Derivation arithmetic → action → verbatim sentence.**

**LAJ.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN29STAGHA:(0.892611×1.000000)×(46/59) + KXATPCHALLENGERMATCH-26MAY25GOMSAK:(0.875800×1.000000)×(46/59) + KXATPCHALLENGERMATCH-26JUL11GIUDAM:(0.875289×1.000000)×(51/59) + KXATPCHALLENGERMATCH-26JUL13VUKBRO:(0.872677×1.000000)×(56/59) + KXATPCHALLENGERMATCH-26APR20DOUJUB:(0.865672×1.000000)×(57/59) + KXATPCHALLENGERMATCH-26MAY14RIEKEC:(0.864827×1.000000)×(51/62) + KXATPCHALLENGERMATCH-26MAY28MONMAY:(0.862405×1.000000)×(55/59)) / 6.109280 = 0.870040914339. Raw round(59×0.870040914339)=51; mass=0.872754337169; blend with lineage 59 gives 52; min(pair cap 65, post-only cap 61) gives 52. Printed action REPRICE_REST@52, active-before 47.

> At 2.432880 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXATPCHALLENGERMATCH-26JUN29STAGHA@0.892611, KXATPCHALLENGERMATCH-26MAY25GOMSAK@0.875800, KXATPCHALLENGERMATCH-26JUL11GIUDAM@0.875289, KXATPCHALLENGERMATCH-26JUL13VUKBRO@0.872677, KXATPCHALLENGERMATCH-26APR20DOUJUB@0.865672, KXATPCHALLENGERMATCH-26MAY14RIEKEC@0.864827, KXATPCHALLENGERMATCH-26MAY28MONMAY@0.862405. LAJ has anchor 59, neighborhood low ratio 0.870040914339228, lineage target 59, pair cap 65, and post-only cap 61. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=52; ACTIVE_TARGET_BEFORE_CENTS=47.

**SVA.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN29STAGHA:(0.892611×1.000000)×(38/42) + KXATPCHALLENGERMATCH-26MAY25GOMSAK:(0.875800×1.000000)×(40/42) + KXATPCHALLENGERMATCH-26JUL11GIUDAM:(0.875289×1.000000)×(31/42) + KXATPCHALLENGERMATCH-26JUL13VUKBRO:(0.872677×1.000000)×(32/41) + KXATPCHALLENGERMATCH-26APR20DOUJUB:(0.865672×1.000000)×(16/43) + KXATPCHALLENGERMATCH-26MAY14RIEKEC:(0.864827×1.000000)×(34/39) + KXATPCHALLENGERMATCH-26MAY28MONMAY:(0.862405×1.000000)×(36/42)) / 6.109280 = 0.783090968655. Raw round(41×0.783090968655)=32; mass=0.872754337169; blend with lineage 37 gives 33; min(pair cap 52, post-only cap 40) gives 33. Printed action REPRICE_REST@33, active-before 34.

> At 2.432880 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXATPCHALLENGERMATCH-26JUN29STAGHA@0.892611, KXATPCHALLENGERMATCH-26MAY25GOMSAK@0.875800, KXATPCHALLENGERMATCH-26JUL11GIUDAM@0.875289, KXATPCHALLENGERMATCH-26JUL13VUKBRO@0.872677, KXATPCHALLENGERMATCH-26APR20DOUJUB@0.865672, KXATPCHALLENGERMATCH-26MAY14RIEKEC@0.864827, KXATPCHALLENGERMATCH-26MAY28MONMAY@0.862405. SVA has anchor 41, neighborhood low ratio 0.7830909686553392, lineage target 37, pair cap 52, and post-only cap 40. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=33; ACTIVE_TARGET_BEFORE_CENTS=34.

### TP9 — 8.139269 hours from discovery (2026-07-14T13:43:44.368Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

LAJ: R-BOOK-LAJ#rows-1..3277, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-3277 = 53/54 last 62; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=LAJ,ts<=1784036624.368 (10 rows; last #row-4303 d2b2edfa-5b0e-5afc-6f15-a9dc9fe4d9fa@54)

SVA: R-BOOK-SVA#rows-1..2134, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-2134 = 45/46 last 43; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=SVA,ts<=1784036624.368 (7 rows; last #row-4277 7ce91f26-56b8-4d78-4cec-f918b65af90d@43)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"LAJ":1,"SVA":1},"anchors_cents":{"LAJ":59,"SVA":41}}` | R-STORY#line-333; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":18}` | R-STORY#line-333; raw cumulative prefixes above |
| drift | `{"LAJ":{"current_cents":55,"drift_cents":-4},"SVA":{"current_cents":43,"drift_cents":2}}` | R-STORY#line-333; raw cumulative prefixes above |
| steps_stillness | `{"LAJ":{"step_count":37,"last_step_cents":1,"still_seconds":0},"SVA":{"step_count":40,"last_step_cents":1,"still_seconds":16406.36899995804}}` | R-STORY#line-333; raw cumulative prefixes above |
| shape_survival | `{"LAJ":{"directional_step_share":0.5135135135135135,"observed_steps":37},"SVA":{"directional_step_share":0.5,"observed_steps":40}}` | R-STORY#line-333; raw cumulative prefixes above |
| ripeness | `{"LAJ":{"continuous_evidence_mass":0.9996958637469586,"observations":3287,"prints":10},"SVA":{"continuous_evidence_mass":0.9995331465919701,"observations":2141,"prints":7}}` | R-STORY#line-333; raw cumulative prefixes above |
| lows_travel | `{"LAJ":{"low_cents":44,"high_cents":70,"travel_cents":26},"SVA":{"low_cents":38,"high_cents":61,"travel_cents":23}}` | R-STORY#line-333; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":98,"spread_sum_cents":2,"dwell_seconds":{"LAJ":0,"SVA":16406.36899995804}}` | R-STORY#line-333; raw cumulative prefixes above |
| divots | `{"LAJ":{"count":6,"mean_depth_cents":1.3333333333333333,"latest":{"timestamp_epoch":1784036624.369,"receipt":"25f578e2-2621-5c77-7bca-5deba0d13eca","floor_cents":54,"depth_cents":1}},"SVA":{"count":8,"mean_depth_cents":1.25,"latest":{"timestamp_epoch":1784020202,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-301","floor_cents":40,"depth_cents":1}}}` | R-STORY#line-333; raw cumulative prefixes above |
| depth_size | `{"LAJ":{"bid_depth_5":10504,"ask_depth_5":17473,"bid_share":0.37545126353790614,"top_bid_size":1941,"top_ask_size":1558},"SVA":{"bid_depth_5":11497,"ask_depth_5":15603,"bid_share":0.42424354243542434,"top_bid_size":1614,"top_ask_size":697}}` | R-STORY#line-333; raw cumulative prefixes above |
| volume | `{"LAJ":{"print_count":10,"contracts":2286.4700000000003},"SVA":{"print_count":7,"contracts":132}}` | R-STORY#line-333; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.7142857142857143,"drift_sum_cents":-2,"both_legs_named":true}` | R-STORY#line-333; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-333; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":8.13926916665501,"hours_to_truth_bell":11.6043419444561,"bell_source":"MACHINE_RECEIPT"}` | R-STORY#line-333; raw cumulative prefixes above |
| books | `{"LAJ":{"bid_cents":53,"ask_cents":54,"last_trade_cents":62,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-3277"},"SVA":{"bid_cents":45,"ask_cents":46,"last_trade_cents":43,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-2134"}}` | R-STORY#line-333; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":2,"legs":{"LAJ":{"credited":false,"entry_cents":null,"standing_target_cents":48},"SVA":{"credited":false,"entry_cents":null,"standing_target_cents":32}}}` | R-STORY#line-333; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":18,"leg0_anchor_cents":41,"leg1_anchor_cents":59,"leg0_drift_cents":2,"leg1_drift_cents":-4,"leg0_travel_cents":23,"leg1_travel_cents":26,"joint_mid_sum_cents":98,"joint_spread_cents":2,"inverse_coherence":0.7142857142857143,"volume_log1p":7.791303786900457,"hours_from_discovery":8.13926916665501,"divot_depth_cents":1.2916666666666665,"oriented_leg_ids":["SVA","LAJ"]}` [R-STORY#line-333; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26JUN02CREVAS (26JUN) | 0.908933 / 1.000000 | R-CORPUS#row-2927; RANGE_SPECTRUM_PATH | R-RANGE#row-1076; CRE anchor 42 (tick#20[1780374255,40,42,0]), low 41 (tick#31[1780377596,41,42,42]), close 44 (terminal tick#103[1780399374,40,44,44]); VAS anchor 57 (tick#1[1780368511,56,57,57]), low 35 (tick#101[1780398765,35,36,35]), close 56 (terminal tick#103[1780399374,55,58,56]) |
| N2 | KXATPCHALLENGERMATCH-26JUN30BLASTA (26JUN) | 0.886494 / 1.000000 | R-CORPUS#row-3887; RANGE_SPECTRUM_PATH | R-RANGE#row-2019; STA anchor 40 (tick#51[1782800226,40,42,0]), low 30 (tick#103[1782816415,29,30,30]), close 44 (terminal tick#106[1782817359,42,45,44]); BLA anchor 58 (tick#1[1782784997,58,61,58]), low 55 (tick#98[1782814871,57,58,55]), close 57 (terminal tick#106[1782817359,56,59,57]) |
| N3 | KXATPCHALLENGERMATCH-26JUN01BOYJIA (26JUN) | 0.884158 / 1.000000 | R-CORPUS#row-2855; RANGE_SPECTRUM_PATH | R-RANGE#row-1005; JIA anchor 44 (tick#1[1780291915,44,45,44]), low 36 (tick#105[1780323354,33,36,36]), close 46 (terminal tick#108[1780324259,45,46,46]); BOY anchor 56 (tick#1[1780291915,55,56,56]), low 41 (tick#100[1780321833,40,42,41]), close 55 (terminal tick#108[1780324259,54,55,55]) |
| N4 | KXATPCHALLENGERMATCH-26MAY10ROCSAF (26MAY) | 0.879240 / 1.000000 | R-CORPUS#row-5389; RANGE_SPECTRUM_PATH | R-RANGE#row-2328; ROC anchor 42 (tick#1[1778483084,42,45,42]), low 41 (tick#81[1778509396,41,44,44]), close 46 (terminal tick#97[1778514317,45,48,46]); SAF anchor 59 (tick#1[1778483084,55,58,59]), low 41 (tick#96[1778514008,40,45,41]), close 55 (terminal tick#97[1778514317,52,55,55]) |
| N5 | KXATPCHALLENGERMATCH-26JUL14IVAGIU (26JUL) | 0.878212 / 1.000000 | R-CORPUS#row-2761; RANGE_SPECTRUM_PATH | R-RANGE#row-911; GIU anchor 43 (tick#1[1784012693,43,46,0]), low 43 (tick#1[1784012693,43,46,0]), close 46 (terminal tick#69[1784046481,43,50,46]); IVA anchor 56 (tick#1[1784012693,54,57,56]), low 33 (tick#66[1784043882,33,34,33]), close 55 (terminal tick#69[1784046481,52,56,55]) |
| N6 | KXATPCHALLENGERMATCH-26JUN02FOROPE (26JUN) | 0.864995 / 1.000000 | R-CORPUS#row-2938; RANGE_SPECTRUM_PATH | R-RANGE#row-1087; FOR anchor 40 (tick#1[1780380011,40,41,40]), low 40 (tick#1[1780380011,40,41,40]), close 47 (terminal tick#32[1780389410,44,62,47]); OPE anchor 59 (tick#1[1780380011,58,59,59]), low 54 (tick#25[1780387294,54,56,54]), close 56 (terminal tick#32[1780389410,52,58,56]) |
| N7 | KXATPCHALLENGERMATCH-26MAY15COPBLA (26MAY) | 0.864019 / 1.000000 | R-CORPUS#row-5637; RANGE_SPECTRUM_PATH | R-RANGE#row-2566; BLA anchor 41 (tick#1[1778810699,40,41,41]), low 33 (tick#98[1778839949,27,29,33]), close 46 (terminal tick#100[1778840552,45,46,46]); COP anchor 60 (tick#1[1778810699,59,60,60]), low 55 (tick#100[1778840552,54,55,55]), close 55 (terminal tick#100[1778840552,54,55,55]) |

**Derivation arithmetic → action → verbatim sentence.**

**LAJ.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN02CREVAS:(0.908933×1.000000)×(35/57) + KXATPCHALLENGERMATCH-26JUN30BLASTA:(0.886494×1.000000)×(55/58) + KXATPCHALLENGERMATCH-26JUN01BOYJIA:(0.884158×1.000000)×(41/56) + KXATPCHALLENGERMATCH-26MAY10ROCSAF:(0.879240×1.000000)×(41/59) + KXATPCHALLENGERMATCH-26JUL14IVAGIU:(0.878212×1.000000)×(33/56) + KXATPCHALLENGERMATCH-26JUN02FOROPE:(0.864995×1.000000)×(54/59) + KXATPCHALLENGERMATCH-26MAY15COPBLA:(0.864019×1.000000)×(55/60)) / 6.166051 = 0.771694957309. Raw round(59×0.771694957309)=46; mass=0.880864434647; blend with lineage 53 gives 47; min(pair cap 67, post-only cap 53) gives 47. Printed action REPRICE_REST@47, active-before 48.

> At 8.139269 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXATPCHALLENGERMATCH-26JUN02CREVAS@0.908933, KXATPCHALLENGERMATCH-26JUN30BLASTA@0.886494, KXATPCHALLENGERMATCH-26JUN01BOYJIA@0.884158, KXATPCHALLENGERMATCH-26MAY10ROCSAF@0.879240, KXATPCHALLENGERMATCH-26JUL14IVAGIU@0.878212, KXATPCHALLENGERMATCH-26JUN02FOROPE@0.864995, KXATPCHALLENGERMATCH-26MAY15COPBLA@0.864019. LAJ has anchor 59, neighborhood low ratio 0.7716949573094922, lineage target 53, pair cap 67, and post-only cap 53. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=47; ACTIVE_TARGET_BEFORE_CENTS=48.

**SVA.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN02CREVAS:(0.908933×1.000000)×(41/42) + KXATPCHALLENGERMATCH-26JUN30BLASTA:(0.886494×1.000000)×(30/40) + KXATPCHALLENGERMATCH-26JUN01BOYJIA:(0.884158×1.000000)×(36/44) + KXATPCHALLENGERMATCH-26MAY10ROCSAF:(0.879240×1.000000)×(41/42) + KXATPCHALLENGERMATCH-26JUL14IVAGIU:(0.878212×1.000000)×(43/43) + KXATPCHALLENGERMATCH-26JUN02FOROPE:(0.864995×1.000000)×(40/40) + KXATPCHALLENGERMATCH-26MAY15COPBLA:(0.864019×1.000000)×(33/41)) / 6.166051 = 0.903739997078. Raw round(41×0.903739997078)=37; mass=0.880864434647; blend with lineage 41 gives 37; min(pair cap 51, post-only cap 45) gives 37. Printed action REPRICE_REST@37, active-before 32.

> At 8.139269 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXATPCHALLENGERMATCH-26JUN02CREVAS@0.908933, KXATPCHALLENGERMATCH-26JUN30BLASTA@0.886494, KXATPCHALLENGERMATCH-26JUN01BOYJIA@0.884158, KXATPCHALLENGERMATCH-26MAY10ROCSAF@0.879240, KXATPCHALLENGERMATCH-26JUL14IVAGIU@0.878212, KXATPCHALLENGERMATCH-26JUN02FOROPE@0.864995, KXATPCHALLENGERMATCH-26MAY15COPBLA@0.864019. SVA has anchor 41, neighborhood low ratio 0.9037399970776597, lineage target 41, pair cap 51, and post-only cap 45. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=37; ACTIVE_TARGET_BEFORE_CENTS=32.

### TP16 — 14.996111 hours from discovery (2026-07-14T20:35:08.999Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

LAJ: R-BOOK-LAJ#rows-1..7432, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-7432 = 52/53 last 53; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=LAJ,ts<=1784061309.000 (58 rows; last #row-5277 d202ad7a-b717-55f1-7b5c-baf269194b7a@53)

SVA: R-BOOK-SVA#rows-1..8231, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-8231 = 47/48 last 48; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=SVA,ts<=1784061309.000 (43 rows; last #row-5270 21b895ce-d8de-550c-e613-bc6aa23cb4a0@48)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"LAJ":1,"SVA":1},"anchors_cents":{"LAJ":59,"SVA":41}}` | R-STORY#line-375; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":18}` | R-STORY#line-375; raw cumulative prefixes above |
| drift | `{"LAJ":{"current_cents":53,"drift_cents":-6},"SVA":{"current_cents":48,"drift_cents":7}}` | R-STORY#line-375; raw cumulative prefixes above |
| steps_stillness | `{"LAJ":{"step_count":62,"last_step_cents":2,"still_seconds":1103.6589999198914},"SVA":{"step_count":74,"last_step_cents":-1,"still_seconds":857.9189999103546}}` | R-STORY#line-375; raw cumulative prefixes above |
| shape_survival | `{"LAJ":{"directional_step_share":0.532258064516129,"observed_steps":62},"SVA":{"directional_step_share":0.5,"observed_steps":74}}` | R-STORY#line-375; raw cumulative prefixes above |
| ripeness | `{"LAJ":{"continuous_evidence_mass":0.999866506474436,"observations":7490,"prints":58},"SVA":{"continuous_evidence_mass":0.999879168680522,"observations":8275,"prints":43}}` | R-STORY#line-375; raw cumulative prefixes above |
| lows_travel | `{"LAJ":{"low_cents":44,"high_cents":70,"travel_cents":26},"SVA":{"low_cents":38,"high_cents":61,"travel_cents":23}}` | R-STORY#line-375; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":101,"spread_sum_cents":2,"dwell_seconds":{"LAJ":1103.6589999198914,"SVA":857.9189999103546}}` | R-STORY#line-375; raw cumulative prefixes above |
| divots | `{"LAJ":{"count":10,"mean_depth_cents":1.3,"latest":{"timestamp_epoch":1784060205,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-7069","floor_cents":51,"depth_cents":2}},"SVA":{"count":15,"mean_depth_cents":1.1333333333333333,"latest":{"timestamp_epoch":1784059165.491,"receipt":"110e9044-bbe7-5ae9-392b-164ecc25495b","floor_cents":48,"depth_cents":1}}}` | R-STORY#line-375; raw cumulative prefixes above |
| depth_size | `{"LAJ":{"bid_depth_5":11606,"ask_depth_5":14496,"bid_share":0.4446402574515363,"top_bid_size":79,"top_ask_size":262},"SVA":{"bid_depth_5":18209,"ask_depth_5":13940,"bid_share":0.5663939780397524,"top_bid_size":367,"top_ask_size":325}}` | R-STORY#line-375; raw cumulative prefixes above |
| volume | `{"LAJ":{"print_count":58,"contracts":4921.2300000000005},"SVA":{"print_count":43,"contracts":1578.5200000000004}}` | R-STORY#line-375; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.9285714285714286,"drift_sum_cents":1,"both_legs_named":true}` | R-STORY#line-375; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-375; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":14.99611111111111,"hours_to_truth_bell":4.7475,"bell_source":"MACHINE_RECEIPT"}` | R-STORY#line-375; raw cumulative prefixes above |
| books | `{"LAJ":{"bid_cents":52,"ask_cents":53,"last_trade_cents":53,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-7432"},"SVA":{"bid_cents":47,"ask_cents":48,"last_trade_cents":48,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-8231"}}` | R-STORY#line-375; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":2,"legs":{"LAJ":{"credited":false,"entry_cents":null,"standing_target_cents":49},"SVA":{"credited":false,"entry_cents":null,"standing_target_cents":34}}}` | R-STORY#line-375; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":18,"leg0_anchor_cents":41,"leg1_anchor_cents":59,"leg0_drift_cents":7,"leg1_drift_cents":-6,"leg0_travel_cents":23,"leg1_travel_cents":26,"joint_mid_sum_cents":101,"joint_spread_cents":2,"inverse_coherence":0.9285714285714286,"volume_log1p":8.77967283384282,"hours_from_discovery":14.99611111111111,"divot_depth_cents":1.2166666666666668,"oriented_leg_ids":["SVA","LAJ"]}` [R-STORY#line-375; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26MAY10ROCSAF (26MAY) | 0.893136 / 1.000000 | R-CORPUS#row-5389; RANGE_SPECTRUM_PATH | R-RANGE#row-2328; ROC anchor 42 (tick#1[1778483084,42,45,42]), low 41 (tick#81[1778509396,41,44,44]), close 46 (terminal tick#97[1778514317,45,48,46]); SAF anchor 59 (tick#1[1778483084,55,58,59]), low 41 (tick#96[1778514008,40,45,41]), close 55 (terminal tick#97[1778514317,52,55,55]) |
| N2 | KXATPCHALLENGERMATCH-26JUN18HEICHO (26JUN) | 0.891602 / 1.000000 | R-CORPUS#row-3592; RANGE_SPECTRUM_PATH | R-RANGE#row-1735; CHO anchor 40 (tick#1[1781762704,38,40,40]), low 26 (tick#93[1781792880,24,26,26]), close 45 (terminal tick#94[1781793519,44,45,45]); HEI anchor 61 (tick#1[1781762704,60,61,61]), low 56 (tick#94[1781793519,55,56,56]), close 56 (terminal tick#94[1781793519,55,56,56]) |
| N3 | KXATPCHALLENGERMATCH-26MAY15COPBLA (26MAY) | 0.891050 / 1.000000 | R-CORPUS#row-5637; RANGE_SPECTRUM_PATH | R-RANGE#row-2566; BLA anchor 41 (tick#1[1778810699,40,41,41]), low 33 (tick#98[1778839949,27,29,33]), close 46 (terminal tick#100[1778840552,45,46,46]); COP anchor 60 (tick#1[1778810699,59,60,60]), low 55 (tick#100[1778840552,54,55,55]), close 55 (terminal tick#100[1778840552,54,55,55]) |
| N4 | KXATPCHALLENGERMATCH-26APR25FELKEN (26APR) | 0.886645 / 1.000000 | R-CORPUS#row-435; RANGE_SPECTRUM_PATH | R-RANGE#row-80; KEN anchor 41 (tick#1[1777110369,40,41,41]), low 34 (tick#108[1777143380,34,35,34]), close 46 (terminal tick#111[1777144286,43,48,46]); FEL anchor 60 (tick#1[1777110369,59,60,60]), low 34 (tick#105[1777142132,33,35,34]), close 54 (terminal tick#111[1777144286,52,56,54]) |
| N5 | KXATPCHALLENGERMATCH-26JUN29GLIMAY (26JUN) | 0.885674 / 1.000000 | R-CORPUS#row-3847; RANGE_SPECTRUM_PATH | R-RANGE#row-1984; MAY anchor 41 (tick#1[1782745932,40,41,41]), low 37 (tick#12[1782752064,37,38,38]), close 50 (terminal tick#63[1782776177,49,50,50]); GLI anchor 59 (tick#1[1782745932,58,59,59]), low 52 (tick#62[1782775573,49,51,52]), close 52 (terminal tick#63[1782776177,51,52,52]) |
| N6 | KXATPCHALLENGERMATCH-26JUL08PIRDZU (26JUL) | 0.883400 / 1.000000 | R-CORPUS#row-2528; RANGE_SPECTRUM_PATH | R-RANGE#row-678; DZU anchor 42 (aggregate-field-only), low 44 (tick#1[1783518549,43,44,44]), close 53 (terminal tick#41[1783536310,52,53,53]); PIR anchor 59 (aggregate-field-only), low 38 (tick#38[1783535069,37,38,38]), close 48 (terminal tick#41[1783536310,47,48,48]) |
| N7 | KXATPCHALLENGERMATCH-26JUN01MIDKOL (26JUN) | 0.878525 / 1.000000 | R-CORPUS#row-2893; RANGE_SPECTRUM_PATH | R-RANGE#row-1042; MID anchor 40 (tick#1[1780293123,39,40,40]), low 33 (tick#100[1780323052,32,34,33]), close 50 (terminal tick#104[1780324259,48,50,50]); KOL anchor 61 (tick#1[1780293123,60,61,61]), low 49 (tick#98[1780322437,48,49,49]), close 52 (terminal tick#104[1780324259,49,53,52]) |

**Derivation arithmetic → action → verbatim sentence.**

**LAJ.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAY10ROCSAF:(0.893136×1.000000)×(41/59) + KXATPCHALLENGERMATCH-26JUN18HEICHO:(0.891602×1.000000)×(56/61) + KXATPCHALLENGERMATCH-26MAY15COPBLA:(0.891050×1.000000)×(55/60) + KXATPCHALLENGERMATCH-26APR25FELKEN:(0.886645×1.000000)×(34/60) + KXATPCHALLENGERMATCH-26JUN29GLIMAY:(0.885674×1.000000)×(52/59) + KXATPCHALLENGERMATCH-26JUL08PIRDZU:(0.883400×1.000000)×(38/59) + KXATPCHALLENGERMATCH-26JUN01MIDKOL:(0.878525×1.000000)×(49/61)) / 6.210032 = 0.775143466947. Raw round(59×0.775143466947)=46; mass=0.887147476166; blend with lineage 53 gives 47; min(pair cap 65, post-only cap 52) gives 47. Printed action REPRICE_REST@47, active-before 49.

> At 14.996111 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXATPCHALLENGERMATCH-26MAY10ROCSAF@0.893136, KXATPCHALLENGERMATCH-26JUN18HEICHO@0.891602, KXATPCHALLENGERMATCH-26MAY15COPBLA@0.891050, KXATPCHALLENGERMATCH-26APR25FELKEN@0.886645, KXATPCHALLENGERMATCH-26JUN29GLIMAY@0.885674, KXATPCHALLENGERMATCH-26JUL08PIRDZU@0.883400, KXATPCHALLENGERMATCH-26JUN01MIDKOL@0.878525. LAJ has anchor 59, neighborhood low ratio 0.7751434669474249, lineage target 53, pair cap 65, and post-only cap 52. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=47; ACTIVE_TARGET_BEFORE_CENTS=49.

**SVA.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAY10ROCSAF:(0.893136×1.000000)×(41/42) + KXATPCHALLENGERMATCH-26JUN18HEICHO:(0.891602×1.000000)×(26/40) + KXATPCHALLENGERMATCH-26MAY15COPBLA:(0.891050×1.000000)×(33/41) + KXATPCHALLENGERMATCH-26APR25FELKEN:(0.886645×1.000000)×(34/41) + KXATPCHALLENGERMATCH-26JUN29GLIMAY:(0.885674×1.000000)×(37/41) + KXATPCHALLENGERMATCH-26JUL08PIRDZU:(0.883400×1.000000)×(44/42) + KXATPCHALLENGERMATCH-26JUN01MIDKOL:(0.878525×1.000000)×(33/40)) / 6.210032 = 0.862053843088. Raw round(41×0.862053843088)=35; mass=0.887147476166; blend with lineage 41 gives 36; min(pair cap 50, post-only cap 47) gives 36. Printed action REPRICE_REST@36, active-before 34.

> At 14.996111 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXATPCHALLENGERMATCH-26MAY10ROCSAF@0.893136, KXATPCHALLENGERMATCH-26JUN18HEICHO@0.891602, KXATPCHALLENGERMATCH-26MAY15COPBLA@0.891050, KXATPCHALLENGERMATCH-26APR25FELKEN@0.886645, KXATPCHALLENGERMATCH-26JUN29GLIMAY@0.885674, KXATPCHALLENGERMATCH-26JUL08PIRDZU@0.883400, KXATPCHALLENGERMATCH-26JUN01MIDKOL@0.878525. SVA has anchor 41, neighborhood low ratio 0.8620538430883022, lineage target 41, pair cap 50, and post-only cap 47. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=36; ACTIVE_TARGET_BEFORE_CENTS=34.

### TP18 — 19.732778 hours from discovery (2026-07-15T01:19:21.000Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

LAJ: R-BOOK-LAJ#rows-1..65821, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-65821 = 51/53 last 53; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=LAJ,ts<=1784078361.001 (284 rows; last #row-5718 0875d51a-28de-7b64-5244-34d3a7989b9d@53)

SVA: R-BOOK-SVA#rows-1..70554, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-70554 = 48/49 last 48; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=SVA,ts<=1784078361.001 (258 rows; last #row-5713 ad09816b-4df9-4db0-5269-7ec8a7979f64@48)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"LAJ":1,"SVA":1},"anchors_cents":{"LAJ":59,"SVA":41}}` | R-STORY#line-387; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":18}` | R-STORY#line-387; raw cumulative prefixes above |
| drift | `{"LAJ":{"current_cents":53,"drift_cents":-6},"SVA":{"current_cents":48,"drift_cents":7}}` | R-STORY#line-387; raw cumulative prefixes above |
| steps_stillness | `{"LAJ":{"step_count":189,"last_step_cents":-1,"still_seconds":287.06500005722046},"SVA":{"step_count":190,"last_step_cents":2,"still_seconds":627.875}}` | R-STORY#line-387; raw cumulative prefixes above |
| shape_survival | `{"LAJ":{"directional_step_share":0.5079365079365079,"observed_steps":189},"SVA":{"directional_step_share":0.49473684210526314,"observed_steps":190}}` | R-STORY#line-387; raw cumulative prefixes above |
| ripeness | `{"LAJ":{"continuous_evidence_mass":0.9999848748392952,"observations":66114,"prints":284},"SVA":{"continuous_evidence_mass":0.999985878498602,"observations":70813,"prints":258}}` | R-STORY#line-387; raw cumulative prefixes above |
| lows_travel | `{"LAJ":{"low_cents":44,"high_cents":70,"travel_cents":26},"SVA":{"low_cents":38,"high_cents":61,"travel_cents":23}}` | R-STORY#line-387; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":101,"spread_sum_cents":3,"dwell_seconds":{"LAJ":287.06500005722046,"SVA":627.875}}` | R-STORY#line-387; raw cumulative prefixes above |
| divots | `{"LAJ":{"count":27,"mean_depth_cents":1.4814814814814814,"latest":{"timestamp_epoch":1784077995,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-64964","floor_cents":51,"depth_cents":3}},"SVA":{"count":25,"mean_depth_cents":1.2,"latest":{"timestamp_epoch":1784077697.569,"receipt":"d288c555-1eb9-4546-781f-1118581622ff","floor_cents":46,"depth_cents":2}}}` | R-STORY#line-387; raw cumulative prefixes above |
| depth_size | `{"LAJ":{"bid_depth_5":13508,"ask_depth_5":14520,"bid_share":0.48194662480376765,"top_bid_size":6802,"top_ask_size":5778},"SVA":{"bid_depth_5":14172,"ask_depth_5":15311,"bid_share":0.48068378387545363,"top_bid_size":77,"top_ask_size":7392}}` | R-STORY#line-387; raw cumulative prefixes above |
| volume | `{"LAJ":{"print_count":284,"contracts":35258.04000000001},"SVA":{"print_count":258,"contracts":16530.560000000005}}` | R-STORY#line-387; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.9285714285714286,"drift_sum_cents":1,"both_legs_named":true}` | R-STORY#line-387; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-387; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":19.732777777777777,"hours_to_truth_bell":0.010833333333333334,"bell_source":"MACHINE_RECEIPT"}` | R-STORY#line-387; raw cumulative prefixes above |
| books | `{"LAJ":{"bid_cents":51,"ask_cents":53,"last_trade_cents":53,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-65821"},"SVA":{"bid_cents":48,"ask_cents":49,"last_trade_cents":48,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-70554"}}` | R-STORY#line-387; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":2,"legs":{"LAJ":{"credited":false,"entry_cents":null,"standing_target_cents":48},"SVA":{"credited":false,"entry_cents":null,"standing_target_cents":36}}}` | R-STORY#line-387; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":18,"leg0_anchor_cents":41,"leg1_anchor_cents":59,"leg0_drift_cents":7,"leg1_drift_cents":-6,"leg0_travel_cents":23,"leg1_travel_cents":26,"joint_mid_sum_cents":101,"joint_spread_cents":3,"inverse_coherence":0.9285714285714286,"volume_log1p":10.854944635889366,"hours_from_discovery":19.732777777777777,"divot_depth_cents":1.3407407407407406,"oriented_leg_ids":["SVA","LAJ"]}` [R-STORY#line-387; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26JUN18HEICHO (26JUN) | 0.879950 / 1.000000 | R-CORPUS#row-3592; RANGE_SPECTRUM_PATH | R-RANGE#row-1735; CHO anchor 40 (tick#1[1781762704,38,40,40]), low 26 (tick#93[1781792880,24,26,26]), close 45 (terminal tick#94[1781793519,44,45,45]); HEI anchor 61 (tick#1[1781762704,60,61,61]), low 56 (tick#94[1781793519,55,56,56]), close 56 (terminal tick#94[1781793519,55,56,56]) |
| N2 | KXATPCHALLENGERMATCH-26MAY10ROCSAF (26MAY) | 0.873451 / 1.000000 | R-CORPUS#row-5389; RANGE_SPECTRUM_PATH | R-RANGE#row-2328; ROC anchor 42 (tick#1[1778483084,42,45,42]), low 41 (tick#81[1778509396,41,44,44]), close 46 (terminal tick#97[1778514317,45,48,46]); SAF anchor 59 (tick#1[1778483084,55,58,59]), low 41 (tick#96[1778514008,40,45,41]), close 55 (terminal tick#97[1778514317,52,55,55]) |
| N3 | KXATPCHALLENGERMATCH-26JUL08PIRDZU (26JUL) | 0.871856 / 1.000000 | R-CORPUS#row-2528; RANGE_SPECTRUM_PATH | R-RANGE#row-678; DZU anchor 42 (aggregate-field-only), low 44 (tick#1[1783518549,43,44,44]), close 53 (terminal tick#41[1783536310,52,53,53]); PIR anchor 59 (aggregate-field-only), low 38 (tick#38[1783535069,37,38,38]), close 48 (terminal tick#41[1783536310,47,48,48]) |
| N4 | KXATPCHALLENGERMATCH-26MAY15COPBLA (26MAY) | 0.871411 / 1.000000 | R-CORPUS#row-5637; RANGE_SPECTRUM_PATH | R-RANGE#row-2566; BLA anchor 41 (tick#1[1778810699,40,41,41]), low 33 (tick#98[1778839949,27,29,33]), close 46 (terminal tick#100[1778840552,45,46,46]); COP anchor 60 (tick#1[1778810699,59,60,60]), low 55 (tick#100[1778840552,54,55,55]), close 55 (terminal tick#100[1778840552,54,55,55]) |
| N5 | KXATPCHALLENGERMATCH-26APR25FELKEN (26APR) | 0.867103 / 1.000000 | R-CORPUS#row-435; RANGE_SPECTRUM_PATH | R-RANGE#row-80; KEN anchor 41 (tick#1[1777110369,40,41,41]), low 34 (tick#108[1777143380,34,35,34]), close 46 (terminal tick#111[1777144286,43,48,46]); FEL anchor 60 (tick#1[1777110369,59,60,60]), low 34 (tick#105[1777142132,33,35,34]), close 54 (terminal tick#111[1777144286,52,56,54]) |
| N6 | KXATPCHALLENGERMATCH-26JUN01MIDKOL (26JUN) | 0.867044 / 1.000000 | R-CORPUS#row-2893; RANGE_SPECTRUM_PATH | R-RANGE#row-1042; MID anchor 40 (tick#1[1780293123,39,40,40]), low 33 (tick#100[1780323052,32,34,33]), close 50 (terminal tick#104[1780324259,48,50,50]); KOL anchor 61 (tick#1[1780293123,60,61,61]), low 49 (tick#98[1780322437,48,49,49]), close 52 (terminal tick#104[1780324259,49,53,52]) |
| N7 | KXATPCHALLENGERMATCH-26JUN29GLIMAY (26JUN) | 0.866154 / 1.000000 | R-CORPUS#row-3847; RANGE_SPECTRUM_PATH | R-RANGE#row-1984; MAY anchor 41 (tick#1[1782745932,40,41,41]), low 37 (tick#12[1782752064,37,38,38]), close 50 (terminal tick#63[1782776177,49,50,50]); GLI anchor 59 (tick#1[1782745932,58,59,59]), low 52 (tick#62[1782775573,49,51,52]), close 52 (terminal tick#63[1782776177,51,52,52]) |

**Derivation arithmetic → action → verbatim sentence.**

**LAJ.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN18HEICHO:(0.879950×1.000000)×(56/61) + KXATPCHALLENGERMATCH-26MAY10ROCSAF:(0.873451×1.000000)×(41/59) + KXATPCHALLENGERMATCH-26JUL08PIRDZU:(0.871856×1.000000)×(38/59) + KXATPCHALLENGERMATCH-26MAY15COPBLA:(0.871411×1.000000)×(55/60) + KXATPCHALLENGERMATCH-26APR25FELKEN:(0.867103×1.000000)×(34/60) + KXATPCHALLENGERMATCH-26JUN01MIDKOL:(0.867044×1.000000)×(49/61) + KXATPCHALLENGERMATCH-26JUN29GLIMAY:(0.866154×1.000000)×(52/59)) / 6.096968 = 0.775196922168. Raw round(59×0.775196922168)=46; mass=0.870995448259; blend with lineage 53 gives 47; min(pair cap 63, post-only cap 52) gives 47. Printed action REPRICE_REST@47, active-before 48.

> At 19.732778 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXATPCHALLENGERMATCH-26JUN18HEICHO@0.879950, KXATPCHALLENGERMATCH-26MAY10ROCSAF@0.873451, KXATPCHALLENGERMATCH-26JUL08PIRDZU@0.871856, KXATPCHALLENGERMATCH-26MAY15COPBLA@0.871411, KXATPCHALLENGERMATCH-26APR25FELKEN@0.867103, KXATPCHALLENGERMATCH-26JUN01MIDKOL@0.867044, KXATPCHALLENGERMATCH-26JUN29GLIMAY@0.866154. LAJ has anchor 59, neighborhood low ratio 0.7751969221675985, lineage target 53, pair cap 63, and post-only cap 52. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=47; ACTIVE_TARGET_BEFORE_CENTS=48.

**SVA.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN18HEICHO:(0.879950×1.000000)×(26/40) + KXATPCHALLENGERMATCH-26MAY10ROCSAF:(0.873451×1.000000)×(41/42) + KXATPCHALLENGERMATCH-26JUL08PIRDZU:(0.871856×1.000000)×(44/42) + KXATPCHALLENGERMATCH-26MAY15COPBLA:(0.871411×1.000000)×(33/41) + KXATPCHALLENGERMATCH-26APR25FELKEN:(0.867103×1.000000)×(34/41) + KXATPCHALLENGERMATCH-26JUN01MIDKOL:(0.867044×1.000000)×(33/40) + KXATPCHALLENGERMATCH-26JUN29GLIMAY:(0.866154×1.000000)×(37/41)) / 6.096968 = 0.861968945995. Raw round(41×0.861968945995)=35; mass=0.870995448259; blend with lineage 41 gives 36; min(pair cap 51, post-only cap 48) gives 36. Printed action HOLD_REST@36, active-before 36.

> At 19.732778 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXATPCHALLENGERMATCH-26JUN18HEICHO@0.879950, KXATPCHALLENGERMATCH-26MAY10ROCSAF@0.873451, KXATPCHALLENGERMATCH-26JUL08PIRDZU@0.871856, KXATPCHALLENGERMATCH-26MAY15COPBLA@0.871411, KXATPCHALLENGERMATCH-26APR25FELKEN@0.867103, KXATPCHALLENGERMATCH-26JUN01MIDKOL@0.867044, KXATPCHALLENGERMATCH-26JUN29GLIMAY@0.866154. SVA has anchor 41, neighborhood low ratio 0.8619689459949985, lineage target 41, pair cap 51, and post-only cap 48. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=36; ACTIVE_TARGET_BEFORE_CENTS=36.

### TP20 — 19.732851 hours from discovery (2026-07-15T01:19:21.263Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

LAJ: R-BOOK-LAJ#rows-1..65821, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-65821 = 51/53 last 53; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=LAJ,ts<=1784078361.264 (285 rows; last #row-5719 177840ec-68b2-6dd4-fc63-f042a347f92d@53)

SVA: R-BOOK-SVA#rows-1..70554, terminal KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-70554 = 48/49 last 48; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14LAJSVA,leg=SVA,ts<=1784078361.264 (258 rows; last #row-5713 ad09816b-4df9-4db0-5269-7ec8a7979f64@48)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"LAJ":1,"SVA":1},"anchors_cents":{"LAJ":59,"SVA":41}}` | R-STORY#line-399; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":18}` | R-STORY#line-399; raw cumulative prefixes above |
| drift | `{"LAJ":{"current_cents":53,"drift_cents":-6},"SVA":{"current_cents":48,"drift_cents":7}}` | R-STORY#line-399; raw cumulative prefixes above |
| steps_stillness | `{"LAJ":{"step_count":189,"last_step_cents":-1,"still_seconds":287.3289999961853},"SVA":{"step_count":190,"last_step_cents":2,"still_seconds":628.1389999389648}}` | R-STORY#line-399; raw cumulative prefixes above |
| shape_survival | `{"LAJ":{"directional_step_share":0.5079365079365079,"observed_steps":189},"SVA":{"directional_step_share":0.49473684210526314,"observed_steps":190}}` | R-STORY#line-399; raw cumulative prefixes above |
| ripeness | `{"LAJ":{"continuous_evidence_mass":0.9999848750680622,"observations":66115,"prints":285},"SVA":{"continuous_evidence_mass":0.999985878498602,"observations":70813,"prints":258}}` | R-STORY#line-399; raw cumulative prefixes above |
| lows_travel | `{"LAJ":{"low_cents":44,"high_cents":70,"travel_cents":26},"SVA":{"low_cents":38,"high_cents":61,"travel_cents":23}}` | R-STORY#line-399; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":101,"spread_sum_cents":3,"dwell_seconds":{"LAJ":287.3289999961853,"SVA":628.1389999389648}}` | R-STORY#line-399; raw cumulative prefixes above |
| divots | `{"LAJ":{"count":27,"mean_depth_cents":1.4814814814814814,"latest":{"timestamp_epoch":1784077995,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-64964","floor_cents":51,"depth_cents":3}},"SVA":{"count":25,"mean_depth_cents":1.2,"latest":{"timestamp_epoch":1784077697.569,"receipt":"d288c555-1eb9-4546-781f-1118581622ff","floor_cents":46,"depth_cents":2}}}` | R-STORY#line-399; raw cumulative prefixes above |
| depth_size | `{"LAJ":{"bid_depth_5":13508,"ask_depth_5":14520,"bid_share":0.48194662480376765,"top_bid_size":6802,"top_ask_size":5778},"SVA":{"bid_depth_5":14172,"ask_depth_5":15311,"bid_share":0.48068378387545363,"top_bid_size":77,"top_ask_size":7392}}` | R-STORY#line-399; raw cumulative prefixes above |
| volume | `{"LAJ":{"print_count":285,"contracts":35261.69000000001},"SVA":{"print_count":258,"contracts":16530.560000000005}}` | R-STORY#line-399; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.9285714285714286,"drift_sum_cents":1,"both_legs_named":true}` | R-STORY#line-399; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-399; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":19.732851111094156,"hours_to_truth_bell":0.01076000001695421,"bell_source":"MACHINE_RECEIPT"}` | R-STORY#line-399; raw cumulative prefixes above |
| books | `{"LAJ":{"bid_cents":51,"ask_cents":53,"last_trade_cents":53,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-65821"},"SVA":{"bid_cents":48,"ask_cents":49,"last_trade_cents":48,"receipt":"KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA.csv.gz#row-70554"}}` | R-STORY#line-399; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":2,"legs":{"LAJ":{"credited":false,"entry_cents":null,"standing_target_cents":47},"SVA":{"credited":false,"entry_cents":null,"standing_target_cents":36}}}` | R-STORY#line-399; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":18,"leg0_anchor_cents":41,"leg1_anchor_cents":59,"leg0_drift_cents":7,"leg1_drift_cents":-6,"leg0_travel_cents":23,"leg1_travel_cents":26,"joint_mid_sum_cents":101,"joint_spread_cents":3,"inverse_coherence":0.9285714285714286,"volume_log1p":10.855015110876327,"hours_from_discovery":19.732851111094156,"divot_depth_cents":1.3407407407407406,"oriented_leg_ids":["SVA","LAJ"]}` [R-STORY#line-399; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26JUN18HEICHO (26JUN) | 0.879950 / 1.000000 | R-CORPUS#row-3592; RANGE_SPECTRUM_PATH | R-RANGE#row-1735; CHO anchor 40 (tick#1[1781762704,38,40,40]), low 26 (tick#93[1781792880,24,26,26]), close 45 (terminal tick#94[1781793519,44,45,45]); HEI anchor 61 (tick#1[1781762704,60,61,61]), low 56 (tick#94[1781793519,55,56,56]), close 56 (terminal tick#94[1781793519,55,56,56]) |
| N2 | KXATPCHALLENGERMATCH-26MAY10ROCSAF (26MAY) | 0.873450 / 1.000000 | R-CORPUS#row-5389; RANGE_SPECTRUM_PATH | R-RANGE#row-2328; ROC anchor 42 (tick#1[1778483084,42,45,42]), low 41 (tick#81[1778509396,41,44,44]), close 46 (terminal tick#97[1778514317,45,48,46]); SAF anchor 59 (tick#1[1778483084,55,58,59]), low 41 (tick#96[1778514008,40,45,41]), close 55 (terminal tick#97[1778514317,52,55,55]) |
| N3 | KXATPCHALLENGERMATCH-26JUL08PIRDZU (26JUL) | 0.871855 / 1.000000 | R-CORPUS#row-2528; RANGE_SPECTRUM_PATH | R-RANGE#row-678; DZU anchor 42 (aggregate-field-only), low 44 (tick#1[1783518549,43,44,44]), close 53 (terminal tick#41[1783536310,52,53,53]); PIR anchor 59 (aggregate-field-only), low 38 (tick#38[1783535069,37,38,38]), close 48 (terminal tick#41[1783536310,47,48,48]) |
| N4 | KXATPCHALLENGERMATCH-26MAY15COPBLA (26MAY) | 0.871411 / 1.000000 | R-CORPUS#row-5637; RANGE_SPECTRUM_PATH | R-RANGE#row-2566; BLA anchor 41 (tick#1[1778810699,40,41,41]), low 33 (tick#98[1778839949,27,29,33]), close 46 (terminal tick#100[1778840552,45,46,46]); COP anchor 60 (tick#1[1778810699,59,60,60]), low 55 (tick#100[1778840552,54,55,55]), close 55 (terminal tick#100[1778840552,54,55,55]) |
| N5 | KXATPCHALLENGERMATCH-26APR25FELKEN (26APR) | 0.867102 / 1.000000 | R-CORPUS#row-435; RANGE_SPECTRUM_PATH | R-RANGE#row-80; KEN anchor 41 (tick#1[1777110369,40,41,41]), low 34 (tick#108[1777143380,34,35,34]), close 46 (terminal tick#111[1777144286,43,48,46]); FEL anchor 60 (tick#1[1777110369,59,60,60]), low 34 (tick#105[1777142132,33,35,34]), close 54 (terminal tick#111[1777144286,52,56,54]) |
| N6 | KXATPCHALLENGERMATCH-26JUN01MIDKOL (26JUN) | 0.867043 / 1.000000 | R-CORPUS#row-2893; RANGE_SPECTRUM_PATH | R-RANGE#row-1042; MID anchor 40 (tick#1[1780293123,39,40,40]), low 33 (tick#100[1780323052,32,34,33]), close 50 (terminal tick#104[1780324259,48,50,50]); KOL anchor 61 (tick#1[1780293123,60,61,61]), low 49 (tick#98[1780322437,48,49,49]), close 52 (terminal tick#104[1780324259,49,53,52]) |
| N7 | KXATPCHALLENGERMATCH-26JUN29GLIMAY (26JUN) | 0.866153 / 1.000000 | R-CORPUS#row-3847; RANGE_SPECTRUM_PATH | R-RANGE#row-1984; MAY anchor 41 (tick#1[1782745932,40,41,41]), low 37 (tick#12[1782752064,37,38,38]), close 50 (terminal tick#63[1782776177,49,50,50]); GLI anchor 59 (tick#1[1782745932,58,59,59]), low 52 (tick#62[1782775573,49,51,52]), close 52 (terminal tick#63[1782776177,51,52,52]) |

**Derivation arithmetic → action → verbatim sentence.**

**LAJ.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN18HEICHO:(0.879950×1.000000)×(56/61) + KXATPCHALLENGERMATCH-26MAY10ROCSAF:(0.873450×1.000000)×(41/59) + KXATPCHALLENGERMATCH-26JUL08PIRDZU:(0.871855×1.000000)×(38/59) + KXATPCHALLENGERMATCH-26MAY15COPBLA:(0.871411×1.000000)×(55/60) + KXATPCHALLENGERMATCH-26APR25FELKEN:(0.867102×1.000000)×(34/60) + KXATPCHALLENGERMATCH-26JUN01MIDKOL:(0.867043×1.000000)×(49/61) + KXATPCHALLENGERMATCH-26JUN29GLIMAY:(0.866153×1.000000)×(52/59)) / 6.096965 = 0.775196922168. Raw round(59×0.775196922168)=46; mass=0.870995044583; blend with lineage 53 gives 47; min(pair cap 63, post-only cap 52) gives 47. Printed action HOLD_REST@47, active-before 47.

> At 19.732851 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXATPCHALLENGERMATCH-26JUN18HEICHO@0.879950, KXATPCHALLENGERMATCH-26MAY10ROCSAF@0.873450, KXATPCHALLENGERMATCH-26JUL08PIRDZU@0.871855, KXATPCHALLENGERMATCH-26MAY15COPBLA@0.871411, KXATPCHALLENGERMATCH-26APR25FELKEN@0.867102, KXATPCHALLENGERMATCH-26JUN01MIDKOL@0.867043, KXATPCHALLENGERMATCH-26JUN29GLIMAY@0.866153. LAJ has anchor 59, neighborhood low ratio 0.7751969221675983, lineage target 53, pair cap 63, and post-only cap 52. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=47; ACTIVE_TARGET_BEFORE_CENTS=47.

**SVA.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN18HEICHO:(0.879950×1.000000)×(26/40) + KXATPCHALLENGERMATCH-26MAY10ROCSAF:(0.873450×1.000000)×(41/42) + KXATPCHALLENGERMATCH-26JUL08PIRDZU:(0.871855×1.000000)×(44/42) + KXATPCHALLENGERMATCH-26MAY15COPBLA:(0.871411×1.000000)×(33/41) + KXATPCHALLENGERMATCH-26APR25FELKEN:(0.867102×1.000000)×(34/41) + KXATPCHALLENGERMATCH-26JUN01MIDKOL:(0.867043×1.000000)×(33/40) + KXATPCHALLENGERMATCH-26JUN29GLIMAY:(0.866153×1.000000)×(37/41)) / 6.096965 = 0.861968945995. Raw round(41×0.861968945995)=35; mass=0.870995044583; blend with lineage 41 gives 36; min(pair cap 52, post-only cap 48) gives 36. Printed action HOLD_REST@36, active-before 36.

> At 19.732851 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14LAJSVA. The named neighborhood is KXATPCHALLENGERMATCH-26JUN18HEICHO@0.879950, KXATPCHALLENGERMATCH-26MAY10ROCSAF@0.873450, KXATPCHALLENGERMATCH-26JUL08PIRDZU@0.871855, KXATPCHALLENGERMATCH-26MAY15COPBLA@0.871411, KXATPCHALLENGERMATCH-26APR25FELKEN@0.867102, KXATPCHALLENGERMATCH-26JUN01MIDKOL@0.867043, KXATPCHALLENGERMATCH-26JUN29GLIMAY@0.866153. SVA has anchor 41, neighborhood low ratio 0.8619689459949983, lineage target 41, pair cap 52, and post-only cap 48. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=36; ACTIVE_TARGET_BEFORE_CENTS=36.


## 3. Capture vs ceiling

Status: **PROVISIONAL_UNTIL_CC_RULES_BELL**. L11 bell 1784078400 from MACHINE_RECEIPT; this explanation does not alter it.

| Side | Deepest lawful print | Moment | Receipt | Captured | Gap to ceiling |
|---|---:|---|---|---:|---:|
| LAJ | 51 | 14.588950 h after formation; 2026-07-14T20:15:23.219Z | R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 | NONE | NONE; final rest 47, shortfall 4 |
| SVA | 41 | 3.499675 h after formation; 2026-07-14T09:10:01.830Z | R-PRINTS#row-4271; 95992e7f-c30f-6ca9-7bac-082bc6399668 | NONE | NONE; final rest 36, shortfall 5 |

Pair ceiling: 92¢, discount 8¢. Captured pair: NONE, discount NONE. Per-side minima need not be simultaneous; this is the deepest standing-rest opportunity each side's tape actually offered.

## 4. The surprise and humility ledger

### Every receipt-defined neighborhood-range departure

Audit convention: because pass 1 emitted no prediction interval, the expected range is the minimum-to-maximum normalized low of its seven named neighbors, mapped onto the target anchor. Every pass-1 stage whose later lawful true-print minimum left that envelope is listed; this is an explanation metric, not a model change.

| Stage | Side | Neighbor-low prediction | Realized | Departure | Realization receipt |
|---:|---|---:|---:|---:|---|
| 4 @ 0.078056h | SVA | 22.08..40.02 | 41 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 0.98¢ | 2026-07-15T01:20:00.000Z; R-PRINTS#row-4271; 95992e7f-c30f-6ca9-7bac-082bc6399668 |
| 5 @ 2.432880h | SVA | 15.26..39.05 | 41 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.95¢ | 2026-07-15T01:20:00.000Z; R-PRINTS#row-4271; 95992e7f-c30f-6ca9-7bac-082bc6399668 |
| 6 @ 2.970278h | SVA | 15.26..39.05 | 41 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.95¢ | 2026-07-15T01:20:00.000Z; R-PRINTS#row-4271; 95992e7f-c30f-6ca9-7bac-082bc6399668 |
| 8 @ 5.996667h | SVA | 22.45..41.00 | 45 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 4.00¢ | 2026-07-15T01:20:00.000Z; R-PRINTS#row-4338; 013d5fa3-3749-40b6-f180-fc6b42c0e326 |
| 9 @ 8.139269h | SVA | 30.75..41.00 | 45 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 4.00¢ | 2026-07-15T01:20:00.000Z; R-PRINTS#row-4338; 013d5fa3-3749-40b6-f180-fc6b42c0e326 |
| 10 @ 8.140556h | SVA | 22.45..41.00 | 45 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 4.00¢ | 2026-07-15T01:20:00.000Z; R-PRINTS#row-4338; 013d5fa3-3749-40b6-f180-fc6b42c0e326 |
| 11 @ 8.144167h | SVA | 22.45..41.00 | 45 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 4.00¢ | 2026-07-15T01:20:00.000Z; R-PRINTS#row-4338; 013d5fa3-3749-40b6-f180-fc6b42c0e326 |
| 12 @ 8.866667h | SVA | 26.65..41.00 | 45 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 4.00¢ | 2026-07-15T01:20:00.000Z; R-PRINTS#row-4338; 013d5fa3-3749-40b6-f180-fc6b42c0e326 |
| 13 @ 8.997500h | SVA | 22.08..40.02 | 45 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 4.98¢ | 2026-07-15T01:20:00.000Z; R-PRINTS#row-4338; 013d5fa3-3749-40b6-f180-fc6b42c0e326 |
| 14 @ 11.998056h | SVA | 23.69..40.07 | 45 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 4.93¢ | 2026-07-15T01:20:00.000Z; R-PRINTS#row-5602; 2ce0ce6a-df98-6075-9abc-e0e7cf733a6e |
| 15 @ 12.608611h | SVA | 22.08..40.02 | 45 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 4.98¢ | 2026-07-15T01:20:00.000Z; R-PRINTS#row-5602; 2ce0ce6a-df98-6075-9abc-e0e7cf733a6e |
| 16 @ 14.996111h | SVA | 26.65..42.95 | 45 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 2.05¢ | 2026-07-15T01:20:00.000Z; R-PRINTS#row-5602; 2ce0ce6a-df98-6075-9abc-e0e7cf733a6e |
| 17 @ 17.994444h | SVA | 23.69..42.95 | 45 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 2.05¢ | 2026-07-15T01:20:00.000Z; R-PRINTS#row-5602; 2ce0ce6a-df98-6075-9abc-e0e7cf733a6e |

### Every decision hindsight beats

A decision is listed when a later formation-lawful true print proves a different rest would have captured closer to the per-side ceiling, or when a credited leg still receives a new action sentence. This is hindsight, never a claim that the future row was knowable.

| Stage | Side | Printed decision | Hindsight-better action | Reading that could have licensed it | Realized receipt / defect |
|---:|---|---|---|---|---|
| 3 @ 0.077778h | LAJ | PLACE_REST@47 | REST@51 | neighborhood low envelope 32.95..58.06 | 2026-07-14T20:15:23.219Z; R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 |
| 3 @ 0.077778h | SVA | PLACE_REST@35 | REST@41 | neighborhood low envelope 13.35..41.00 | 2026-07-14T09:10:01.830Z; R-PRINTS#row-4271; 95992e7f-c30f-6ca9-7bac-082bc6399668 |
| 4 @ 0.078056h | LAJ | HOLD_REST@47 | REST@51 | neighborhood low envelope 36.23..56.15 | 2026-07-14T20:15:23.219Z; R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 |
| 4 @ 0.078056h | SVA | REPRICE_REST@34 | REST@41 | lows_travel running low 39 | 2026-07-14T09:10:01.830Z; R-PRINTS#row-4271; 95992e7f-c30f-6ca9-7bac-082bc6399668 |
| 5 @ 2.432880h | LAJ | REPRICE_REST@52 | REST@51 | neighborhood low envelope 46.00..57.00 | 2026-07-14T20:15:23.219Z; R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 |
| 5 @ 2.432880h | SVA | REPRICE_REST@33 | REST@41 | lows_travel running low 38 | 2026-07-14T09:10:01.830Z; R-PRINTS#row-4271; 95992e7f-c30f-6ca9-7bac-082bc6399668 |
| 6 @ 2.970278h | LAJ | HOLD_REST@52 | REST@51 | neighborhood low envelope 46.00..57.00 | 2026-07-14T20:15:23.219Z; R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 |
| 6 @ 2.970278h | SVA | HOLD_REST@33 | REST@41 | lows_travel running low 38 | 2026-07-14T09:10:01.830Z; R-PRINTS#row-4271; 95992e7f-c30f-6ca9-7bac-082bc6399668 |
| 7 @ 3.577453h | LAJ | REPRICE_REST@50 | REST@51 | neighborhood low envelope 31.47..57.07 | 2026-07-14T20:15:23.219Z; R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 |
| 7 @ 3.577453h | SVA | REPRICE_REST@35 | REST@41 | neighborhood low envelope 22.45..41.00 | 2026-07-14T09:10:09.484Z; R-PRINTS#row-4272; 62c5acca-20b5-609e-9743-315bb552232f |
| 8 @ 5.996667h | LAJ | REPRICE_REST@48 | REST@51 | neighborhood low envelope 31.47..57.07 | 2026-07-14T20:15:23.219Z; R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 |
| 8 @ 5.996667h | SVA | REPRICE_REST@32 | REST@45 | lows_travel running low 38 | 2026-07-14T15:19:54.350Z; R-PRINTS#row-4338; 013d5fa3-3749-40b6-f180-fc6b42c0e326 |
| 9 @ 8.139269h | LAJ | REPRICE_REST@47 | REST@51 | neighborhood low envelope 34.77..55.95 | 2026-07-14T20:15:23.219Z; R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 |
| 9 @ 8.139269h | SVA | REPRICE_REST@37 | REST@45 | lows_travel running low 38 | 2026-07-14T15:19:54.350Z; R-PRINTS#row-4338; 013d5fa3-3749-40b6-f180-fc6b42c0e326 |
| 10 @ 8.140556h | LAJ | REPRICE_REST@48 | REST@51 | neighborhood low envelope 31.47..57.07 | 2026-07-14T20:15:23.219Z; R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 |
| 10 @ 8.140556h | SVA | REPRICE_REST@32 | REST@45 | lows_travel running low 38 | 2026-07-14T15:19:54.350Z; R-PRINTS#row-4338; 013d5fa3-3749-40b6-f180-fc6b42c0e326 |
| 11 @ 8.144167h | LAJ | HOLD_REST@48 | REST@51 | neighborhood low envelope 31.47..57.07 | 2026-07-14T20:15:23.219Z; R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 |
| 11 @ 8.144167h | SVA | HOLD_REST@32 | REST@45 | lows_travel running low 38 | 2026-07-14T15:19:54.350Z; R-PRINTS#row-4338; 013d5fa3-3749-40b6-f180-fc6b42c0e326 |
| 12 @ 8.866667h | LAJ | REPRICE_REST@47 | REST@51 | neighborhood low envelope 34.77..55.95 | 2026-07-14T20:15:23.219Z; R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 |
| 12 @ 8.866667h | SVA | REPRICE_REST@37 | REST@45 | lows_travel running low 38 | 2026-07-14T15:19:54.350Z; R-PRINTS#row-4338; 013d5fa3-3749-40b6-f180-fc6b42c0e326 |
| 13 @ 8.997500h | LAJ | REPRICE_REST@48 | REST@51 | neighborhood low envelope 33.43..56.15 | 2026-07-14T20:15:23.219Z; R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 |
| 13 @ 8.997500h | SVA | REPRICE_REST@35 | REST@45 | lows_travel running low 38 | 2026-07-14T15:19:54.350Z; R-PRINTS#row-4338; 013d5fa3-3749-40b6-f180-fc6b42c0e326 |
| 14 @ 11.998056h | LAJ | HOLD_REST@48 | REST@51 | neighborhood low envelope 33.43..54.16 | 2026-07-14T20:15:23.219Z; R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 |
| 14 @ 11.998056h | SVA | HOLD_REST@35 | REST@45 | lows_travel running low 38 | 2026-07-15T00:03:30.907Z; R-PRINTS#row-5602; 2ce0ce6a-df98-6075-9abc-e0e7cf733a6e |
| 15 @ 12.608611h | LAJ | REPRICE_REST@49 | REST@51 | neighborhood low envelope 33.43..56.15 | 2026-07-14T20:15:23.219Z; R-PRINTS#row-5267; 7fb0df36-2082-795a-5cb6-f311235289d1 |
| 15 @ 12.608611h | SVA | REPRICE_REST@34 | REST@45 | lows_travel running low 38 | 2026-07-15T00:03:30.907Z; R-PRINTS#row-5602; 2ce0ce6a-df98-6075-9abc-e0e7cf733a6e |
| 16 @ 14.996111h | LAJ | REPRICE_REST@47 | REST@51 | neighborhood low envelope 33.43..54.16 | 2026-07-15T01:13:10.967Z; R-PRINTS#row-5699; a637e367-61b6-6156-3b06-3b75335131f5 |
| 16 @ 14.996111h | SVA | REPRICE_REST@36 | REST@45 | lows_travel running low 38 | 2026-07-15T00:03:30.907Z; R-PRINTS#row-5602; 2ce0ce6a-df98-6075-9abc-e0e7cf733a6e |
| 17 @ 17.994444h | LAJ | REPRICE_REST@48 | REST@51 | neighborhood low envelope 38.00..54.16 | 2026-07-15T01:13:10.967Z; R-PRINTS#row-5699; a637e367-61b6-6156-3b06-3b75335131f5 |
| 17 @ 17.994444h | SVA | HOLD_REST@36 | REST@45 | lows_travel running low 38 | 2026-07-15T00:03:30.907Z; R-PRINTS#row-5602; 2ce0ce6a-df98-6075-9abc-e0e7cf733a6e |
| 18 @ 19.732778h | LAJ | REPRICE_REST@47 | REST@53 | neighborhood low envelope 33.43..54.16 | 2026-07-15T01:19:21.264Z; R-PRINTS#row-5719; 177840ec-68b2-6dd4-fc63-f042a347f92d |

### What remains unexplained

- The receipts do not explain why both legs remained shallower than the neighborhood's weighted eventual lows.
- Pass 1 has no same-elapsed-stage survival table, so a corpus remedy cannot be claimed without a forbidden new analysis pass.
- The two per-side minima occurred at different times; the 92-cent ceiling is a standing-rest opportunity, not a simultaneous displayed pair.


## 5. LAJSVA 47/36 causal chain and adjustment answer

The last turning point above is the full receipt chain. In short: LAJ used ratio 0.775196922168, so round(59×ratio)=46; mass 0.870995044583 blended lineage 53 to 47, and caps 63/52 left 47. SVA used ratio 0.861968945995, so round(41×ratio)=35; the same declared mass blended lineage 41 to 36. That is exactly 47/36.

To preserve +6, both sides had to capture at a sum no greater than 94. R-PRINTS proves the tape offered LAJ 51 + SVA 41 = 92, so 51/41 would have completed at +8. For the final seven alone, the SVA raw target needs normalized low at least 0.987805 to round to 41, while LAJ needs at least 0.855932 to round to 51. Under every nonnegative reweighting of those same seven that meets the low-side requirement, the maximum attainable high-side ratio is 0.741831 (best convex witness KXATPCHALLENGERMATCH-26JUL08PIRDZU@0.588000 + KXATPCHALLENGERMATCH-26JUN29GLIMAY@0.412000), below 0.855932. **Therefore no declared-similarity reweighting of the final seven preserves +6.**

A corpus adjustment could only be claimed after adding and testing a same-elapsed-stage survival table. Pass 1 contains no such table. This no-rerun lane therefore stamps the corpus answer **UNPROVED**, not yes.
