# Game explained — GIUBAR

License: LAW_INDEX read at `dcac4032`, SHA-256 `c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6`; laws L0 L8 L11 L18 L20 L22. Explanation lane only: pass-1 receipts and named custody rows; zero runs, zero passes, zero tuning, zero 804 reads.

Steps-Behind Law: assume the OS is always a few steps behind the market's finesse. This explanation states what was missed, what surprised, and what remains unexplained.

## Receipt bindings

- **R-LAW:** `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LAW_INDEX.md` @ commit `dcac4032`, SHA-256 `c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6`.
- **R-STORY:** `.claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/FOUR_STORIES.md`, SHA-256 `fae4b97437d9cfac75f7b84a9b677ba288c8b4e58f5e475eed45ea9a63812020`.
- **R-RESULT:** `.claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/FOUR_STORIES_RECEIPT.json`, SHA-256 `22381e774e538ed5bc4fe05f7fd50c64efc06d5f61c6f65eb65cde2851049f0d`.
- **R-CORPUS:** `.claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/CORPUS_INDEX.jsonl.gz`, SHA-256 `210951fa9c1bd8d255e6501f7507144311b297b811bd992dd04a1ab46ff37ba1`; row numbers are decompressed JSONL rows.
- **R-RANGE:** external custody `C:\Users\omigr\OMI-Workspace\.corpus-cache-v6\range_spectrum_v1.jsonl`, SHA-256 `1e9891acaaea23a73160aaa26b10b17c87270c1209d9a2a0a23a6a6c56434884`, 130935927 bytes; row/tick refs below.
- **R-HIST:** external custody `C:\Users\omigr\OMI-Workspace\.corpus-cache-v6\historical_events_materialized.csv`, SHA-256 `46741cded0ccb0a24302da4bc7b77f1bb3b82707a8cceaa272a902bae683339a`, 1041339 bytes; physical CSV line refs below.
- **R-PRINTS:** `.claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/TARGET_PRINTS_5.jsonl.gz`, SHA-256 `575784544073ec3e9e84818ffae68203b6d616d51868f65f3cd09559b3af198e`; rows are decompressed JSONL rows. Upstream full tape: `C:\Users\omigr\OMI-Window1-private\fit-local\prints.jsonl`, SHA-256 `e9b5a765b51ddbf0d65364c4f38744ad949ca3c675e5b3a0e472392fbcfabb55`.
- **R-TRUTH:** `c0056976:.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.json`, SHA-256 `f7bc71d8e615859db272d841e125bc4836a685d82bb2d6769762c9bc19e56729`; event row `KXATPCHALLENGERMATCH-26JUL12GIUBAR`, bell 1783876740 (TAPE_INFERENCE).
- **R-LINEAGE:** external custody `C:\Users\omigr\OMI-Workspace\.claude\window1_live_v4_replay\v54_walk5_live_20260821\FULL_DECISION_TRACE_5.jsonl.gz`, SHA-256 `085fbf04dbc16f8c76691a0823a5370061afc9d738b5eefda9eab92fef4ccbc4`, 55209610 bytes, 133626 rows; only lineage values already printed in R-STORY are used here.
- **R-BOOK-BAR:** external custody `C:\Users\omigr\OMI-Window1-private\fit-local\ticks\KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz`, SHA-256 `ccb153d06d07797687e6aeffeb8d2e12b87f12889947a1b660c85988e0fc7f25`, 541656 bytes, 60857 data rows.
- **R-BOOK-GIU:** external custody `C:\Users\omigr\OMI-Window1-private\fit-local\ticks\KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz`, SHA-256 `8cf05f73d43280be1b394c4241f2935bc872bfb2ab8c333a5e08b47d9783ce94`, 572375 bytes, 63256 data rows.

## 1. The story — hour 0 to bell (259 words; two-page guard passed)

Hour 0 opened as an unformed 31/67 anchor pair behind 5/95 and 4/95 books. The references briefly crossed toward 50/49 and then 44/76, but formation law correctly kept both sides silent. At 0.143889 hours both formations completed; the seven named comparisons had narrowed enough for 24 BAR / 65 GIU, with a 98-cent pair ceiling and neither post-only cap binding.

For most of the next twelve hours the machine followed the market downward in small revisions rather than predicting the late finesse: BAR cycled 22–25 and GIU 61–65. At 12.192778 hours BAR's book broke to a 19 bid while the rest was 20. The true print at 19 credited BAR. The sibling arithmetic then moved GIU from 61 to 59 as BAR's 19-cent entry became the pair commitment.

GIU credited at 59 at hour 12.479156, completing the pair at 78 and a 22-cent discount. That is a good capture, but not the ceiling. Before the provisional L11 bell, BAR later printed 16 and GIU 49; the tape's deepest lawful per-side pair was therefore 65, a 35-cent discount. We captured 19/59 and left 3 cents on BAR plus 10 on GIU.

What the OS missed was the size and timing of the last-hour two-sided collapse. The neighborhood did eventually reorient, but only after BAR had already fallen and the pair commitment forced the sibling response. After both credits, the derivation layer also kept writing PLACE_REST sentences even though the executor's credited-position guard suppressed those actions. The receipts prove a strong result and a semantic humility defect at the same time.

## 2. Turning points — 7 complete causal chains

### TP1 — 0.000000 hours from discovery (2026-07-12T04:42:20.000Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

BAR: R-BOOK-BAR#rows-1..1, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-1 = 5/95 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=BAR,ts<=1783831340.000 (0 rows)

GIU: R-BOOK-GIU#rows-1..1, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-1 = 4/95 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=GIU,ts<=1783831340.000 (0 rows)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"BAR":0,"GIU":0},"anchors_cents":{"BAR":31,"GIU":67}}` | R-STORY#line-11; raw cumulative prefixes above |
| opening_split | `{"sum_cents":98,"absolute_split_cents":36}` | R-STORY#line-11; raw cumulative prefixes above |
| drift | `{"BAR":{"current_cents":50,"drift_cents":19},"GIU":{"current_cents":49,"drift_cents":-18}}` | R-STORY#line-11; raw cumulative prefixes above |
| steps_stillness | `{"BAR":{"step_count":1,"last_step_cents":1,"still_seconds":0},"GIU":{"step_count":0,"last_step_cents":null,"still_seconds":0}}` | R-STORY#line-11; raw cumulative prefixes above |
| shape_survival | `{"BAR":{"directional_step_share":1,"observed_steps":1},"GIU":{"directional_step_share":null,"observed_steps":0}}` | R-STORY#line-11; raw cumulative prefixes above |
| ripeness | `{"BAR":{"continuous_evidence_mass":0.8,"observations":4,"prints":0},"GIU":{"continuous_evidence_mass":0.8,"observations":4,"prints":0}}` | R-STORY#line-11; raw cumulative prefixes above |
| lows_travel | `{"BAR":{"low_cents":49,"high_cents":50,"travel_cents":1},"GIU":{"low_cents":49,"high_cents":49,"travel_cents":0}}` | R-STORY#line-11; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":99,"spread_sum_cents":181,"dwell_seconds":{"BAR":0,"GIU":0}}` | R-STORY#line-11; raw cumulative prefixes above |
| divots | `{"BAR":{"count":0,"mean_depth_cents":null,"latest":null},"GIU":{"count":0,"mean_depth_cents":null,"latest":null}}` | R-STORY#line-11; raw cumulative prefixes above |
| depth_size | `{"BAR":{"bid_depth_5":6437,"ask_depth_5":6720,"bid_share":0.4892452686782701,"top_bid_size":200,"top_ask_size":207},"GIU":{"bid_depth_5":5937,"ask_depth_5":6220,"bid_share":0.4883606152833758,"top_bid_size":500,"top_ask_size":7}}` | R-STORY#line-11; raw cumulative prefixes above |
| volume | `{"BAR":{"print_count":0,"contracts":0},"GIU":{"print_count":0,"contracts":0}}` | R-STORY#line-11; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.9736842105263158,"drift_sum_cents":1,"both_legs_named":true}` | R-STORY#line-11; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-11; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":0,"hours_to_truth_bell":12.61111111111111,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-11; raw cumulative prefixes above |
| books | `{"BAR":{"bid_cents":5,"ask_cents":95,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-1"},"GIU":{"bid_cents":4,"ask_cents":95,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-1"}}` | R-STORY#line-11; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":0,"legs":{"BAR":{"credited":false,"entry_cents":null,"standing_target_cents":null},"GIU":{"credited":false,"entry_cents":null,"standing_target_cents":null}}}` | R-STORY#line-11; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":36,"leg0_anchor_cents":31,"leg1_anchor_cents":67,"leg0_drift_cents":19,"leg1_drift_cents":-18,"leg0_travel_cents":1,"leg1_travel_cents":0,"joint_mid_sum_cents":99,"joint_spread_cents":181,"inverse_coherence":0.9736842105263158,"volume_log1p":0,"hours_from_discovery":0,"divot_depth_cents":null,"oriented_leg_ids":["BAR","GIU"]}` [R-STORY#line-11; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26MAR05CECKYM (26MAR) | 0.583994 / 0.732877 | R-CORPUS#row-4109; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-5512; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N2 | KXATPCHALLENGERMATCH-26MAY14ANDMOL (26MAY) | 0.565053 / 0.945205 | R-CORPUS#row-5591; RANGE_SPECTRUM_PATH | R-RANGE#row-2520; AND anchor 25 (tick#29[1778761965,21,24,25]), low 23 (tick#30[1778762266,19,24,23]), close 39 (terminal tick#31[1778762567,36,39,39]); MOL anchor 87 (tick#27[1778761362,84,86,87]), low 61 (tick#31[1778762567,61,62,61]), close 61 (terminal tick#31[1778762567,61,62,61]) |
| N3 | KXATPCHALLENGERMATCH-26MAR05HEMGEA (26MAR) | 0.562739 / 0.732877 | R-CORPUS#row-4115; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-5511; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N4 | KXWTACHALLENGERMATCH-26JUN14LEOKUL (26JUN) | 0.526456 / 0.945205 | R-CORPUS#row-9693; RANGE_SPECTRUM_PATH | R-RANGE#row-4604; LEO anchor 46 (tick#48[1781416329,5,46,46]), low 46 (tick#48[1781416329,5,46,46]), close 55 (terminal tick#72[1781424913,59,64,55]); KUL anchor 63 (tick#48[1781416329,31,63,63]), low 40 (tick#60[1781420280,38,40,41]), close 40 (terminal tick#72[1781424913,38,40,40]) |
| N5 | KXATPCHALLENGERMATCH-26MAY10LOMNED (26MAY) | 0.511055 / 0.945205 | R-CORPUS#row-5374; RANGE_SPECTRUM_PATH | R-RANGE#row-2313; NED anchor 45 (tick#98[1778411214,19,35,45]), low 38 (tick#101[1778412119,30,37,38]), close 39 (terminal tick#109[1778414539,40,45,39]); LOM anchor 76 (tick#98[1778411214,63,79,76]), low 52 (tick#108[1778414229,45,51,52]), close 57 (terminal tick#109[1778414539,53,59,57]) |
| N6 | KXATPCHALLENGERMATCH-26JUN14BRIGON (26JUN) | 0.496949 / 0.945205 | R-CORPUS#row-3339; RANGE_SPECTRUM_PATH | R-RANGE#row-1485; BRI anchor 11 (tick#24[1781461671,11,95,11]), low 11 (tick#24[1781461671,11,95,11]), close 11 (terminal tick#27[1781462909,5,70,11]); GON anchor 94 (tick#23[1781461369,5,94,0]), low 84 (tick#27[1781462909,84,89,84]), close 84 (terminal tick#27[1781462909,84,89,84]) |
| N7 | KXATPCHALLENGERMATCH-26MAY31SCOHON (26MAY) | 0.495968 / 0.945205 | R-CORPUS#row-6115; RANGE_SPECTRUM_PATH | R-RANGE#row-3022; SCO anchor 13 (tick#62[1780204147,10,13,0]), low 9 (tick#63[1780204448,9,13,0]), close 13 (terminal tick#96[1780214399,9,13,13]); HON anchor 90 (tick#8[1780187867,10,90,0]), low 90 (tick#8[1780187867,10,90,0]), close 90 (terminal tick#96[1780214399,87,90,90]) |

**Derivation arithmetic → action → verbatim sentence.**

**BAR.** Formation progress 0.000000 < 1 overrides the computed candidate; lawful action is HOLD_REST@NONE.

> At 0.000000 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26MAR05CECKYM@0.583994, KXATPCHALLENGERMATCH-26MAY14ANDMOL@0.565053, KXATPCHALLENGERMATCH-26MAR05HEMGEA@0.562739, KXWTACHALLENGERMATCH-26JUN14LEOKUL@0.526456, KXATPCHALLENGERMATCH-26MAY10LOMNED@0.511055, KXATPCHALLENGERMATCH-26JUN14BRIGON@0.496949, KXATPCHALLENGERMATCH-26MAY31SCOHON@0.495968. BAR has anchor 31, neighborhood low ratio 0.9037242017632899, lineage target NONE, pair cap 98, and post-only cap 94. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=NONE; ACTIVE_TARGET_BEFORE_CENTS=NONE.

**GIU.** Formation progress 0.000000 < 1 overrides the computed candidate; lawful action is HOLD_REST@NONE.

> At 0.000000 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26MAR05CECKYM@0.583994, KXATPCHALLENGERMATCH-26MAY14ANDMOL@0.565053, KXATPCHALLENGERMATCH-26MAR05HEMGEA@0.562739, KXWTACHALLENGERMATCH-26JUN14LEOKUL@0.526456, KXATPCHALLENGERMATCH-26MAY10LOMNED@0.511055, KXATPCHALLENGERMATCH-26JUN14BRIGON@0.496949, KXATPCHALLENGERMATCH-26MAY31SCOHON@0.495968. GIU has anchor 67, neighborhood low ratio 0.8312374193068489, lineage target NONE, pair cap 98, and post-only cap 94. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=NONE; ACTIVE_TARGET_BEFORE_CENTS=NONE.

### TP3 — 0.143889 hours from discovery (2026-07-12T04:50:58.000Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

BAR: R-BOOK-BAR#rows-1..201, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-201 = 28/35 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=BAR,ts<=1783831858.000 (0 rows)

GIU: R-BOOK-GIU#rows-1..34, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-34 = 62/76 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=GIU,ts<=1783831858.000 (0 rows)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"BAR":1,"GIU":1},"anchors_cents":{"BAR":31,"GIU":67}}` | R-STORY#line-23; raw cumulative prefixes above |
| opening_split | `{"sum_cents":98,"absolute_split_cents":36}` | R-STORY#line-23; raw cumulative prefixes above |
| drift | `{"BAR":{"current_cents":31,"drift_cents":0},"GIU":{"current_cents":69,"drift_cents":2}}` | R-STORY#line-23; raw cumulative prefixes above |
| steps_stillness | `{"BAR":{"step_count":59,"last_step_cents":-1,"still_seconds":0},"GIU":{"step_count":8,"last_step_cents":2,"still_seconds":0}}` | R-STORY#line-23; raw cumulative prefixes above |
| shape_survival | `{"BAR":{"directional_step_share":0,"observed_steps":59},"GIU":{"directional_step_share":0.75,"observed_steps":8}}` | R-STORY#line-23; raw cumulative prefixes above |
| ripeness | `{"BAR":{"continuous_evidence_mass":0.9952830188679245,"observations":211,"prints":0},"GIU":{"continuous_evidence_mass":0.9791666666666666,"observations":47,"prints":0}}` | R-STORY#line-23; raw cumulative prefixes above |
| lows_travel | `{"BAR":{"low_cents":29,"high_cents":50,"travel_cents":21},"GIU":{"low_cents":49,"high_cents":76,"travel_cents":27}}` | R-STORY#line-23; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":100,"spread_sum_cents":21,"dwell_seconds":{"BAR":0,"GIU":0}}` | R-STORY#line-23; raw cumulative prefixes above |
| divots | `{"BAR":{"count":13,"mean_depth_cents":1.1538461538461537,"latest":{"timestamp_epoch":1783831702,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-153","floor_cents":30,"depth_cents":1}},"GIU":{"count":0,"mean_depth_cents":null,"latest":null}}` | R-STORY#line-23; raw cumulative prefixes above |
| depth_size | `{"BAR":{"bid_depth_5":2074,"ask_depth_5":828,"bid_share":0.7146795313576844,"top_bid_size":500,"top_ask_size":30},"GIU":{"bid_depth_5":902,"ask_depth_5":8257,"bid_share":0.0984823670706409,"top_bid_size":500,"top_ask_size":127}}` | R-STORY#line-23; raw cumulative prefixes above |
| volume | `{"BAR":{"print_count":0,"contracts":0},"GIU":{"print_count":0,"contracts":0}}` | R-STORY#line-23; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.33333333333333337,"drift_sum_cents":2,"both_legs_named":true}` | R-STORY#line-23; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-23; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":0.1438888888888889,"hours_to_truth_bell":12.467222222222222,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-23; raw cumulative prefixes above |
| books | `{"BAR":{"bid_cents":28,"ask_cents":35,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-201"},"GIU":{"bid_cents":62,"ask_cents":76,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-34"}}` | R-STORY#line-23; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":0,"legs":{"BAR":{"credited":false,"entry_cents":null,"standing_target_cents":null},"GIU":{"credited":false,"entry_cents":null,"standing_target_cents":null}}}` | R-STORY#line-23; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":36,"leg0_anchor_cents":31,"leg1_anchor_cents":67,"leg0_drift_cents":0,"leg1_drift_cents":2,"leg0_travel_cents":21,"leg1_travel_cents":27,"joint_mid_sum_cents":100,"joint_spread_cents":21,"inverse_coherence":0.33333333333333337,"volume_log1p":0,"hours_from_discovery":0.1438888888888889,"divot_depth_cents":1.1538461538461537,"oriented_leg_ids":["BAR","GIU"]}` [R-STORY#line-23; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26APR28JORCUK (26APR) | 0.827700 / 1.000000 | R-CORPUS#row-609; RANGE_SPECTRUM_PATH | R-RANGE#row-243; CUK anchor 31 (tick#1[1777334999,31,34,0]), low 16 (tick#86[1777364454,14,16,16]), close 32 (terminal tick#88[1777365391,30,32,32]); JOR anchor 68 (tick#1[1777334999,65,69,68]), low 68 (tick#1[1777334999,65,69,68]), close 68 (terminal tick#88[1777365391,68,70,68]) |
| N2 | KXATPCHALLENGERMATCH-26JUN11RIBROD (26JUN) | 0.815907 / 1.000000 | R-CORPUS#row-3279; RANGE_SPECTRUM_PATH | R-RANGE#row-1425; ROD anchor 34 (tick#1[1781163071,32,35,34]), low 13 (tick#94[1781193850,12,13,13]), close 32 (terminal tick#97[1781195089,31,32,32]); RIB anchor 68 (tick#1[1781163071,65,68,0]), low 64 (tick#10[1781166114,64,68,0]), close 68 (terminal tick#97[1781195089,68,69,68]) |
| N3 | KXATPCHALLENGERMATCH-26JUN30ROCBAS (26JUN) | 0.807130 / 1.000000 | R-CORPUS#row-3926; RANGE_SPECTRUM_PATH | R-RANGE#row-2057; BAS anchor 35 (tick#1[1782799305,32,35,0]), low 14 (tick#98[1782830378,12,14,14]), close 35 (terminal tick#110[1782834169,26,32,35]); ROC anchor 67 (tick#1[1782799305,65,67,67]), low 64 (tick#101[1782831297,65,68,64]), close 69 (terminal tick#110[1782834169,66,72,69]) |
| N4 | KXATPCHALLENGERMATCH-26JUL15ROMGAL (26JUL) | 0.803003 / 1.000000 | R-CORPUS#row-2800; RANGE_SPECTRUM_PATH | R-RANGE#row-950; ROM anchor 33 (tick#1[1784077375,32,33,33]), low 29 (tick#74[1784107259,26,32,29]), close 33 (terminal tick#76[1784108211,33,34,33]); GAL anchor 68 (tick#1[1784077375,66,68,68]), low 66 (tick#1[1784077375,66,68,68]), close 70 (terminal tick#76[1784108211,66,67,70]) |
| N5 | KXATPCHALLENGERMATCH-26MAY24BRURAH (26MAY) | 0.802749 / 1.000000 | R-CORPUS#row-5826; RANGE_SPECTRUM_PATH | R-RANGE#row-2751; RAH anchor 32 (tick#1[1779582633,28,32,0]), low 32 (tick#1[1779582633,28,32,0]), close 32 (terminal tick#96[1779611365,31,33,32]); BRU anchor 71 (tick#1[1779582633,71,72,0]), low 69 (tick#41[1779594706,69,72,72]), close 69 (terminal tick#96[1779611365,66,69,69]) |
| N6 | KXATPCHALLENGERMATCH-26JUL05HUEMAR (26JUL) | 0.799385 / 1.000000 | R-CORPUS#row-2296; RANGE_SPECTRUM_PATH | R-RANGE#row-447; MAR anchor 31 (tick#38[1783253838,31,35,0]), low 31 (tick#38[1783253838,31,35,0]), close 31 (terminal tick#60[1783264984,31,37,31]); HUE anchor 70 (tick#1[1783234903,60,70,0]), low 67 (tick#38[1783253838,65,67,70]), close 81 (terminal tick#60[1783264984,61,81,81]) |
| N7 | KXATPCHALLENGERMATCH-26JUL05PAPMBI (26JUL) | 0.797869 / 1.000000 | R-CORPUS#row-2322; RANGE_SPECTRUM_PATH | R-RANGE#row-473; PAP anchor 30 (tick#1[1783249107,33,35,30]), low 30 (tick#1[1783249107,33,35,30]), close 32 (terminal tick#66[1783279480,31,32,32]); MBI anchor 69 (tick#1[1783249107,64,68,69]), low 65 (tick#33[1783264984,65,67,67]), close 69 (terminal tick#66[1783279480,68,69,69]) |

**Derivation arithmetic → action → verbatim sentence.**

**BAR.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26APR28JORCUK:(0.827700×1.000000)×(16/31) + KXATPCHALLENGERMATCH-26JUN11RIBROD:(0.815907×1.000000)×(13/34) + KXATPCHALLENGERMATCH-26JUN30ROCBAS:(0.807130×1.000000)×(14/35) + KXATPCHALLENGERMATCH-26JUL15ROMGAL:(0.803003×1.000000)×(29/33) + KXATPCHALLENGERMATCH-26MAY24BRURAH:(0.802749×1.000000)×(32/32) + KXATPCHALLENGERMATCH-26JUL05HUEMAR:(0.799385×1.000000)×(31/31) + KXATPCHALLENGERMATCH-26JUL05PAPMBI:(0.797869×1.000000)×(30/30)) / 5.653745 = 0.737155735613. Raw round(31×0.737155735613)=23; mass=0.807677870008; blend with lineage 29 gives 24; min(pair cap 98, post-only cap 34) gives 24. Printed action PLACE_REST@24, active-before NONE.

> At 0.143889 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26APR28JORCUK@0.827700, KXATPCHALLENGERMATCH-26JUN11RIBROD@0.815907, KXATPCHALLENGERMATCH-26JUN30ROCBAS@0.807130, KXATPCHALLENGERMATCH-26JUL15ROMGAL@0.803003, KXATPCHALLENGERMATCH-26MAY24BRURAH@0.802749, KXATPCHALLENGERMATCH-26JUL05HUEMAR@0.799385, KXATPCHALLENGERMATCH-26JUL05PAPMBI@0.797869. BAR has anchor 31, neighborhood low ratio 0.7371557356131554, lineage target 29, pair cap 98, and post-only cap 34. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=24; ACTIVE_TARGET_BEFORE_CENTS=NONE.

**GIU.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26APR28JORCUK:(0.827700×1.000000)×(68/68) + KXATPCHALLENGERMATCH-26JUN11RIBROD:(0.815907×1.000000)×(64/68) + KXATPCHALLENGERMATCH-26JUN30ROCBAS:(0.807130×1.000000)×(64/67) + KXATPCHALLENGERMATCH-26JUL15ROMGAL:(0.803003×1.000000)×(66/68) + KXATPCHALLENGERMATCH-26MAY24BRURAH:(0.802749×1.000000)×(69/71) + KXATPCHALLENGERMATCH-26JUL05HUEMAR:(0.799385×1.000000)×(67/70) + KXATPCHALLENGERMATCH-26JUL05PAPMBI:(0.797869×1.000000)×(65/69)) / 5.653745 = 0.962701224654. Raw round(67×0.962701224654)=65; mass=0.807677870008; blend with lineage 63 gives 65; min(pair cap 98, post-only cap 75) gives 65. Printed action PLACE_REST@65, active-before NONE.

> At 0.143889 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26APR28JORCUK@0.827700, KXATPCHALLENGERMATCH-26JUN11RIBROD@0.815907, KXATPCHALLENGERMATCH-26JUN30ROCBAS@0.807130, KXATPCHALLENGERMATCH-26JUL15ROMGAL@0.803003, KXATPCHALLENGERMATCH-26MAY24BRURAH@0.802749, KXATPCHALLENGERMATCH-26JUL05HUEMAR@0.799385, KXATPCHALLENGERMATCH-26JUL05PAPMBI@0.797869. GIU has anchor 67, neighborhood low ratio 0.9627012246538177, lineage target 63, pair cap 98, and post-only cap 75. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=65; ACTIVE_TARGET_BEFORE_CENTS=NONE.

### TP6 — 2.970000 hours from discovery (2026-07-12T07:40:32.000Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

BAR: R-BOOK-BAR#rows-1..499, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-499 = 26/28 last 28; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=BAR,ts<=1783842032.000 (3 rows; last #row-10 e71dc0e3-35a2-409f-ec84-9144dd40e81b@28)

GIU: R-BOOK-GIU#rows-1..362, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-362 = 69/70 last 69; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=GIU,ts<=1783842032.000 (7 rows; last #row-9 b113f8de-209e-522a-6da2-c9ef40e91737@69)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"BAR":1,"GIU":1},"anchors_cents":{"BAR":31,"GIU":67}}` | R-STORY#line-41; raw cumulative prefixes above |
| opening_split | `{"sum_cents":98,"absolute_split_cents":36}` | R-STORY#line-41; raw cumulative prefixes above |
| drift | `{"BAR":{"current_cents":28,"drift_cents":-3},"GIU":{"current_cents":69,"drift_cents":2}}` | R-STORY#line-41; raw cumulative prefixes above |
| steps_stillness | `{"BAR":{"step_count":81,"last_step_cents":1,"still_seconds":59.23399996757507},"GIU":{"step_count":21,"last_step_cents":-1,"still_seconds":780.8380000591278}}` | R-STORY#line-41; raw cumulative prefixes above |
| shape_survival | `{"BAR":{"directional_step_share":0.6172839506172839,"observed_steps":81},"GIU":{"directional_step_share":0.5714285714285714,"observed_steps":21}}` | R-STORY#line-41; raw cumulative prefixes above |
| ripeness | `{"BAR":{"continuous_evidence_mass":0.9980237154150198,"observations":505,"prints":3},"GIU":{"continuous_evidence_mass":0.9972972972972973,"observations":369,"prints":7}}` | R-STORY#line-41; raw cumulative prefixes above |
| lows_travel | `{"BAR":{"low_cents":26,"high_cents":50,"travel_cents":24},"GIU":{"low_cents":49,"high_cents":76,"travel_cents":27}}` | R-STORY#line-41; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":97,"spread_sum_cents":3,"dwell_seconds":{"BAR":59.23399996757507,"GIU":780.8380000591278}}` | R-STORY#line-41; raw cumulative prefixes above |
| divots | `{"BAR":{"count":15,"mean_depth_cents":1.1333333333333333,"latest":{"timestamp_epoch":1783841801,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-437","floor_cents":26,"depth_cents":1}},"GIU":{"count":3,"mean_depth_cents":1,"latest":{"timestamp_epoch":1783833826,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-86","floor_cents":70,"depth_cents":1}}}` | R-STORY#line-41; raw cumulative prefixes above |
| depth_size | `{"BAR":{"bid_depth_5":2000,"ask_depth_5":3717,"bid_share":0.34983382893125764,"top_bid_size":192,"top_ask_size":514},"GIU":{"bid_depth_5":3749,"ask_depth_5":3222,"bid_share":0.5377994548845216,"top_bid_size":344,"top_ask_size":295}}` | R-STORY#line-41; raw cumulative prefixes above |
| volume | `{"BAR":{"print_count":3,"contracts":524},"GIU":{"print_count":7,"contracts":940}}` | R-STORY#line-41; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.8333333333333334,"drift_sum_cents":-1,"both_legs_named":true}` | R-STORY#line-41; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-41; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":2.97,"hours_to_truth_bell":9.641111111111112,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-41; raw cumulative prefixes above |
| books | `{"BAR":{"bid_cents":26,"ask_cents":28,"last_trade_cents":28,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-499"},"GIU":{"bid_cents":69,"ask_cents":70,"last_trade_cents":69,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-362"}}` | R-STORY#line-41; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":2,"legs":{"BAR":{"credited":false,"entry_cents":null,"standing_target_cents":22},"GIU":{"credited":false,"entry_cents":null,"standing_target_cents":65}}}` | R-STORY#line-41; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":36,"leg0_anchor_cents":31,"leg1_anchor_cents":67,"leg0_drift_cents":-3,"leg1_drift_cents":2,"leg0_travel_cents":24,"leg1_travel_cents":27,"joint_mid_sum_cents":97,"joint_spread_cents":3,"inverse_coherence":0.8333333333333334,"volume_log1p":7.289610521451167,"hours_from_discovery":2.97,"divot_depth_cents":1.0666666666666667,"oriented_leg_ids":["BAR","GIU"]}` [R-STORY#line-41; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26MAY10KOKMIC (26MAY) | 0.863593 / 1.000000 | R-CORPUS#row-5366; RANGE_SPECTRUM_PATH | R-RANGE#row-2305; MIC anchor 32 (tick#9[1778385543,30,32,0]), low 26 (tick#100[1778413325,18,24,26]), close 27 (terminal tick#104[1778414539,27,28,27]); KOK anchor 68 (tick#9[1778385543,68,70,0]), low 63 (tick#49[1778397593,63,66,68]), close 72 (terminal tick#104[1778414539,72,73,72]) |
| N2 | KXATPCHALLENGERMATCH-26MAY11TABBLA (26MAY) | 0.857914 / 1.000000 | R-CORPUS#row-5469; RANGE_SPECTRUM_PATH | R-RANGE#row-2401; BLA anchor 36 (tick#1[1778481868,33,35,36]), low 31 (tick#23[1778488545,31,33,36]), close 33 (terminal tick#101[1778514317,30,31,33]); TAB anchor 67 (tick#1[1778481868,65,67,0]), low 49 (tick#97[1778513072,49,51,51]), close 69 (terminal tick#101[1778514317,69,70,69]) |
| N3 | KXATPCHALLENGERMATCH-26JUL13ARSMAR (26JUL) | 0.856573 / 1.000000 | R-CORPUS#row-2692; RANGE_SPECTRUM_PATH | R-RANGE#row-842; ARS anchor 31 (tick#19[1783973296,31,33,33]), low 31 (tick#19[1783973296,31,33,33]), close 31 (terminal tick#56[1783986623,31,32,31]); MAR anchor 67 (tick#1[1783956978,67,68,67]), low 67 (tick#1[1783956978,67,68,67]), close 69 (terminal tick#56[1783986623,68,69,69]) |
| N4 | KXATPCHALLENGERMATCH-26APR28JORCUK (26APR) | 0.852798 / 1.000000 | R-CORPUS#row-609; RANGE_SPECTRUM_PATH | R-RANGE#row-243; CUK anchor 31 (tick#1[1777334999,31,34,0]), low 16 (tick#86[1777364454,14,16,16]), close 32 (terminal tick#88[1777365391,30,32,32]); JOR anchor 68 (tick#1[1777334999,65,69,68]), low 68 (tick#1[1777334999,65,69,68]), close 68 (terminal tick#88[1777365391,68,70,68]) |
| N5 | KXATPCHALLENGERMATCH-26JUN04VIRVUK (26JUN) | 0.850222 / 1.000000 | R-CORPUS#row-3028; RANGE_SPECTRUM_PATH | R-RANGE#row-1177; VUK anchor 31 (tick#1[1780542844,31,34,31]), low 28 (tick#42[1780556604,28,30,30]), close 29 (terminal tick#83[1780570331,28,29,29]); VIR anchor 66 (tick#1[1780542844,66,68,66]), low 66 (tick#1[1780542844,66,68,66]), close 72 (terminal tick#83[1780570331,71,72,72]) |
| N6 | KXATPCHALLENGERMATCH-26JUL07SKAPET (26JUL) | 0.847036 / 1.000000 | R-CORPUS#row-2494; RANGE_SPECTRUM_PATH | R-RANGE#row-644; PET anchor 32 (tick#1[1783415152,33,34,32]), low 28 (tick#51[1783444034,27,28,28]), close 28 (terminal tick#51[1783444034,27,28,28]); SKA anchor 69 (tick#1[1783415152,64,66,69]), low 61 (tick#50[1783443398,58,59,61]), close 71 (terminal tick#51[1783444034,73,74,71]) |
| N7 | KXATPCHALLENGERMATCH-26JUN16ERETAB (26JUN) | 0.844920 / 1.000000 | R-CORPUS#row-3488; RANGE_SPECTRUM_PATH | R-RANGE#row-1631; TAB anchor 31 (tick#1[1781577780,30,32,31]), low 17 (tick#74[1781607236,19,20,17]), close 34 (terminal tick#78[1781609106,33,34,34]); ERE anchor 70 (tick#1[1781577780,68,70,70]), low 62 (tick#76[1781608171,60,62,62]), close 68 (terminal tick#78[1781609106,66,67,68]) |

**Derivation arithmetic → action → verbatim sentence.**

**BAR.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAY10KOKMIC:(0.863593×1.000000)×(26/32) + KXATPCHALLENGERMATCH-26MAY11TABBLA:(0.857914×1.000000)×(31/36) + KXATPCHALLENGERMATCH-26JUL13ARSMAR:(0.856573×1.000000)×(31/31) + KXATPCHALLENGERMATCH-26APR28JORCUK:(0.852798×1.000000)×(16/31) + KXATPCHALLENGERMATCH-26JUN04VIRVUK:(0.850222×1.000000)×(28/31) + KXATPCHALLENGERMATCH-26JUL07SKAPET:(0.847036×1.000000)×(28/32) + KXATPCHALLENGERMATCH-26JUN16ERETAB:(0.844920×1.000000)×(17/31)) / 5.973057 = 0.788473716910. Raw round(31×0.788473716910)=24; mass=0.853293810280; blend with lineage 26 gives 24; min(pair cap 34, post-only cap 27) gives 24. Printed action REPRICE_REST@24, active-before 22.

> At 2.970000 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26MAY10KOKMIC@0.863593, KXATPCHALLENGERMATCH-26MAY11TABBLA@0.857914, KXATPCHALLENGERMATCH-26JUL13ARSMAR@0.856573, KXATPCHALLENGERMATCH-26APR28JORCUK@0.852798, KXATPCHALLENGERMATCH-26JUN04VIRVUK@0.850222, KXATPCHALLENGERMATCH-26JUL07SKAPET@0.847036, KXATPCHALLENGERMATCH-26JUN16ERETAB@0.844920. BAR has anchor 31, neighborhood low ratio 0.7884737169100859, lineage target 26, pair cap 34, and post-only cap 27. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=24; ACTIVE_TARGET_BEFORE_CENTS=22.

**GIU.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAY10KOKMIC:(0.863593×1.000000)×(63/68) + KXATPCHALLENGERMATCH-26MAY11TABBLA:(0.857914×1.000000)×(49/67) + KXATPCHALLENGERMATCH-26JUL13ARSMAR:(0.856573×1.000000)×(67/67) + KXATPCHALLENGERMATCH-26APR28JORCUK:(0.852798×1.000000)×(68/68) + KXATPCHALLENGERMATCH-26JUN04VIRVUK:(0.850222×1.000000)×(66/66) + KXATPCHALLENGERMATCH-26JUL07SKAPET:(0.847036×1.000000)×(61/69) + KXATPCHALLENGERMATCH-26JUN16ERETAB:(0.844920×1.000000)×(62/70)) / 5.973057 = 0.918173674999. Raw round(67×0.918173674999)=62; mass=0.853293810280; blend with lineage 69 gives 63; min(pair cap 77, post-only cap 69) gives 63. Printed action REPRICE_REST@63, active-before 65.

> At 2.970000 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26MAY10KOKMIC@0.863593, KXATPCHALLENGERMATCH-26MAY11TABBLA@0.857914, KXATPCHALLENGERMATCH-26JUL13ARSMAR@0.856573, KXATPCHALLENGERMATCH-26APR28JORCUK@0.852798, KXATPCHALLENGERMATCH-26JUN04VIRVUK@0.850222, KXATPCHALLENGERMATCH-26JUL07SKAPET@0.847036, KXATPCHALLENGERMATCH-26JUN16ERETAB@0.844920. GIU has anchor 67, neighborhood low ratio 0.9181736749988396, lineage target 69, pair cap 77, and post-only cap 69. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=63; ACTIVE_TARGET_BEFORE_CENTS=65.

### TP10 — 12.192778 hours from discovery (2026-07-12T16:53:54.000Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

BAR: R-BOOK-BAR#rows-1..16270, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-16270 = 19/24 last 27; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=BAR,ts<=1783875234.001 (15 rows; last #row-33 84a4d6b4-760e-5484-b81b-8504853e32dd@27)

GIU: R-BOOK-GIU#rows-1..13927, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-13927 = 80/82 last 69; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=GIU,ts<=1783875234.001 (15 rows; last #row-26 d2e1c0db-dea0-4f40-4719-3aca6666d06f@69)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"BAR":1,"GIU":1},"anchors_cents":{"BAR":31,"GIU":67}}` | R-STORY#line-65; raw cumulative prefixes above |
| opening_split | `{"sum_cents":98,"absolute_split_cents":36}` | R-STORY#line-65; raw cumulative prefixes above |
| drift | `{"BAR":{"current_cents":27,"drift_cents":-4},"GIU":{"current_cents":69,"drift_cents":2}}` | R-STORY#line-65; raw cumulative prefixes above |
| steps_stillness | `{"BAR":{"step_count":103,"last_step_cents":8,"still_seconds":0},"GIU":{"step_count":38,"last_step_cents":3,"still_seconds":894.5269999504089}}` | R-STORY#line-65; raw cumulative prefixes above |
| shape_survival | `{"BAR":{"directional_step_share":0.5825242718446602,"observed_steps":103},"GIU":{"directional_step_share":0.5263157894736842,"observed_steps":38}}` | R-STORY#line-65; raw cumulative prefixes above |
| ripeness | `{"BAR":{"continuous_evidence_mass":0.9999388341794605,"observations":16348,"prints":15},"GIU":{"continuous_evidence_mass":0.9999285663261661,"observations":13998,"prints":15}}` | R-STORY#line-65; raw cumulative prefixes above |
| lows_travel | `{"BAR":{"low_cents":19,"high_cents":50,"travel_cents":31},"GIU":{"low_cents":49,"high_cents":76,"travel_cents":27}}` | R-STORY#line-65; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":96,"spread_sum_cents":7,"dwell_seconds":{"BAR":0,"GIU":894.5269999504089}}` | R-STORY#line-65; raw cumulative prefixes above |
| divots | `{"BAR":{"count":18,"mean_depth_cents":1.5555555555555556,"latest":{"timestamp_epoch":1783875153,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-15612","floor_cents":27,"depth_cents":7}},"GIU":{"count":7,"mean_depth_cents":1.4285714285714286,"latest":{"timestamp_epoch":1783874339,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-2938","floor_cents":66,"depth_cents":3}}}` | R-STORY#line-65; raw cumulative prefixes above |
| depth_size | `{"BAR":{"bid_depth_5":14764,"ask_depth_5":35381,"bid_share":0.29442616412404027,"top_bid_size":1,"top_ask_size":5000},"GIU":{"bid_depth_5":22168,"ask_depth_5":41994,"bid_share":0.3455004519809233,"top_bid_size":9000,"top_ask_size":250}}` | R-STORY#line-65; raw cumulative prefixes above |
| volume | `{"BAR":{"print_count":15,"contracts":1687.3100000000002},"GIU":{"print_count":15,"contracts":1435.46}}` | R-STORY#line-65; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.7142857142857143,"drift_sum_cents":-2,"both_legs_named":true}` | R-STORY#line-65; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-65; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":12.192777777777778,"hours_to_truth_bell":0.41833333333333333,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-65; raw cumulative prefixes above |
| books | `{"BAR":{"bid_cents":19,"ask_cents":24,"last_trade_cents":27,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-16270"},"GIU":{"bid_cents":80,"ask_cents":82,"last_trade_cents":69,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-13927"}}` | R-STORY#line-65; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":2,"legs":{"BAR":{"credited":false,"entry_cents":null,"standing_target_cents":23},"GIU":{"credited":false,"entry_cents":null,"standing_target_cents":61}}}` | R-STORY#line-65; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":36,"leg0_anchor_cents":31,"leg1_anchor_cents":67,"leg0_drift_cents":-4,"leg1_drift_cents":2,"leg0_travel_cents":31,"leg1_travel_cents":27,"joint_mid_sum_cents":96,"joint_spread_cents":7,"inverse_coherence":0.7142857142857143,"volume_log1p":8.04679588468969,"hours_from_discovery":12.192777777777778,"divot_depth_cents":1.492063492063492,"oriented_leg_ids":["BAR","GIU"]}` [R-STORY#line-65; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26MAY10KOKMIC (26MAY) | 0.847201 / 1.000000 | R-CORPUS#row-5366; RANGE_SPECTRUM_PATH | R-RANGE#row-2305; MIC anchor 32 (tick#9[1778385543,30,32,0]), low 26 (tick#100[1778413325,18,24,26]), close 27 (terminal tick#104[1778414539,27,28,27]); KOK anchor 68 (tick#9[1778385543,68,70,0]), low 63 (tick#49[1778397593,63,66,68]), close 72 (terminal tick#104[1778414539,72,73,72]) |
| N2 | KXATPCHALLENGERMATCH-26APR28JORCUK (26APR) | 0.843966 / 1.000000 | R-CORPUS#row-609; RANGE_SPECTRUM_PATH | R-RANGE#row-243; CUK anchor 31 (tick#1[1777334999,31,34,0]), low 16 (tick#86[1777364454,14,16,16]), close 32 (terminal tick#88[1777365391,30,32,32]); JOR anchor 68 (tick#1[1777334999,65,69,68]), low 68 (tick#1[1777334999,65,69,68]), close 68 (terminal tick#88[1777365391,68,70,68]) |
| N3 | KXATPCHALLENGERMATCH-26JUN07WINGRA (26JUN) | 0.835594 / 1.000000 | R-CORPUS#row-3131; RANGE_SPECTRUM_PATH | R-RANGE#row-1280; WIN anchor 33 (tick#1[1780814337,29,33,0]), low 28 (tick#3[1780815273,28,34,0]), close 30 (terminal tick#100[1780848925,28,30,30]); GRA anchor 70 (tick#5[1780815876,66,70,0]), low 42 (tick#89[1780845261,42,43,46]), close 72 (terminal tick#100[1780848925,70,72,72]) |
| N4 | KXATPCHALLENGERMATCH-26APR23GIUALK (26APR) | 0.831261 / 1.000000 | R-CORPUS#row-403; RANGE_SPECTRUM_PATH | R-RANGE#row-56; GIU anchor 31 (tick#32[1776954710,31,33,0]), low 12 (tick#90[1776975333,11,12,12]), close 35 (terminal tick#95[1776976879,34,35,35]); ALK anchor 66 (tick#1[1776945283,67,69,66]), low 57 (tick#94[1776976569,56,57,57]), close 66 (terminal tick#95[1776976879,66,67,66]) |
| N5 | KXATPCHALLENGERMATCH-26JUN07SANCAM (26JUN) | 0.830791 / 1.000000 | R-CORPUS#row-3126; RANGE_SPECTRUM_PATH | R-RANGE#row-1275; CAM anchor 30 (tick#87[1780828758,20,30,30]), low 23 (tick#77[1780825384,23,44,0]), close 23 (terminal tick#89[1780829693,22,24,23]); SAN anchor 67 (tick#5[1780800617,62,67,67]), low 67 (tick#5[1780800617,62,67,67]), close 76 (terminal tick#89[1780829693,76,77,76]) |
| N6 | KXATPCHALLENGERMATCH-26MAY05BALVOE (26MAY) | 0.825295 / 1.000000 | R-CORPUS#row-5224; RANGE_SPECTRUM_PATH | R-RANGE#row-2174; VOE anchor 31 (tick#1[1777962838,29,31,31]), low 29 (tick#1[1777962838,29,31,31]), close 29 (terminal tick#102[1777993319,28,29,29]); BAL anchor 71 (tick#1[1777962838,68,71,71]), low 63 (tick#98[1777992113,65,79,63]), close 72 (terminal tick#102[1777993319,70,72,72]) |
| N7 | KXATPCHALLENGERMATCH-26JUN11RIBROD (26JUN) | 0.821318 / 1.000000 | R-CORPUS#row-3279; RANGE_SPECTRUM_PATH | R-RANGE#row-1425; ROD anchor 34 (tick#1[1781163071,32,35,34]), low 13 (tick#94[1781193850,12,13,13]), close 32 (terminal tick#97[1781195089,31,32,32]); RIB anchor 68 (tick#1[1781163071,65,68,0]), low 64 (tick#10[1781166114,64,68,0]), close 68 (terminal tick#97[1781195089,68,69,68]) |

**Derivation arithmetic → action → verbatim sentence.**

**BAR.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAY10KOKMIC:(0.847201×1.000000)×(26/32) + KXATPCHALLENGERMATCH-26APR28JORCUK:(0.843966×1.000000)×(16/31) + KXATPCHALLENGERMATCH-26JUN07WINGRA:(0.835594×1.000000)×(28/33) + KXATPCHALLENGERMATCH-26APR23GIUALK:(0.831261×1.000000)×(12/31) + KXATPCHALLENGERMATCH-26JUN07SANCAM:(0.830791×1.000000)×(23/30) + KXATPCHALLENGERMATCH-26MAY05BALVOE:(0.825295×1.000000)×(29/31) + KXATPCHALLENGERMATCH-26JUN11RIBROD:(0.821318×1.000000)×(13/34)) / 5.835426 = 0.664516462843. Raw round(31×0.664516462843)=21; mass=0.833632307049; blend with lineage 17 gives 20; min(pair cap 38, post-only cap 23) gives 20. Printed action REPRICE_REST@20, active-before 23.

> At 12.192778 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26MAY10KOKMIC@0.847201, KXATPCHALLENGERMATCH-26APR28JORCUK@0.843966, KXATPCHALLENGERMATCH-26JUN07WINGRA@0.835594, KXATPCHALLENGERMATCH-26APR23GIUALK@0.831261, KXATPCHALLENGERMATCH-26JUN07SANCAM@0.830791, KXATPCHALLENGERMATCH-26MAY05BALVOE@0.825295, KXATPCHALLENGERMATCH-26JUN11RIBROD@0.821318. BAR has anchor 31, neighborhood low ratio 0.6645164628434217, lineage target 17, pair cap 38, and post-only cap 23. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=20; ACTIVE_TARGET_BEFORE_CENTS=23.

**GIU.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAY10KOKMIC:(0.847201×1.000000)×(63/68) + KXATPCHALLENGERMATCH-26APR28JORCUK:(0.843966×1.000000)×(68/68) + KXATPCHALLENGERMATCH-26JUN07WINGRA:(0.835594×1.000000)×(42/70) + KXATPCHALLENGERMATCH-26APR23GIUALK:(0.831261×1.000000)×(57/66) + KXATPCHALLENGERMATCH-26JUN07SANCAM:(0.830791×1.000000)×(67/67) + KXATPCHALLENGERMATCH-26MAY05BALVOE:(0.825295×1.000000)×(63/71) + KXATPCHALLENGERMATCH-26JUN11RIBROD:(0.821318×1.000000)×(64/68)) / 5.835426 = 0.888407585749. Raw round(67×0.888407585749)=60; mass=0.833632307049; blend with lineage 69 gives 61; min(pair cap 76, post-only cap 81) gives 61. Printed action HOLD_REST@61, active-before 61.

> At 12.192778 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26MAY10KOKMIC@0.847201, KXATPCHALLENGERMATCH-26APR28JORCUK@0.843966, KXATPCHALLENGERMATCH-26JUN07WINGRA@0.835594, KXATPCHALLENGERMATCH-26APR23GIUALK@0.831261, KXATPCHALLENGERMATCH-26JUN07SANCAM@0.830791, KXATPCHALLENGERMATCH-26MAY05BALVOE@0.825295, KXATPCHALLENGERMATCH-26JUN11RIBROD@0.821318. GIU has anchor 67, neighborhood low ratio 0.888407585748667, lineage target 69, pair cap 76, and post-only cap 81. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=61; ACTIVE_TARGET_BEFORE_CENTS=61.

### TP11 — 12.198236 hours from discovery (2026-07-12T16:54:13.649Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

BAR: R-BOOK-BAR#rows-1..16418, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-16418 = 16/17 last 19; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=BAR,ts<=1783875253.650 (16 rows; last #row-34 22676ea3-972a-46e2-a3ef-d4dda2d1c002@19)

GIU: R-BOOK-GIU#rows-1..14103, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-14103 = 83/84 last 69; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=GIU,ts<=1783875253.650 (16 rows; last #row-35 7316d5e9-d993-79ba-f33a-b941c8d3c6a6@84)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"BAR":1,"GIU":1},"anchors_cents":{"BAR":31,"GIU":67}}` | R-STORY#line-71; raw cumulative prefixes above |
| opening_split | `{"sum_cents":98,"absolute_split_cents":36}` | R-STORY#line-71; raw cumulative prefixes above |
| drift | `{"BAR":{"current_cents":19,"drift_cents":-12},"GIU":{"current_cents":84,"drift_cents":17}}` | R-STORY#line-71; raw cumulative prefixes above |
| steps_stillness | `{"BAR":{"step_count":104,"last_step_cents":-8,"still_seconds":19.219000101089478},"GIU":{"step_count":39,"last_step_cents":15,"still_seconds":0}}` | R-STORY#line-71; raw cumulative prefixes above |
| shape_survival | `{"BAR":{"directional_step_share":0.5865384615384616,"observed_steps":104},"GIU":{"directional_step_share":0.5384615384615384,"observed_steps":39}}` | R-STORY#line-71; raw cumulative prefixes above |
| ripeness | `{"BAR":{"continuous_evidence_mass":0.9999391690492122,"observations":16438,"prints":16},"GIU":{"continuous_evidence_mass":0.9999291985273294,"observations":14123,"prints":16}}` | R-STORY#line-71; raw cumulative prefixes above |
| lows_travel | `{"BAR":{"low_cents":19,"high_cents":50,"travel_cents":31},"GIU":{"low_cents":49,"high_cents":84,"travel_cents":35}}` | R-STORY#line-71; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":103,"spread_sum_cents":2,"dwell_seconds":{"BAR":19.219000101089478,"GIU":0}}` | R-STORY#line-71; raw cumulative prefixes above |
| divots | `{"BAR":{"count":18,"mean_depth_cents":1.5555555555555556,"latest":{"timestamp_epoch":1783875153,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-15612","floor_cents":27,"depth_cents":7}},"GIU":{"count":7,"mean_depth_cents":1.4285714285714286,"latest":{"timestamp_epoch":1783874339,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-2938","floor_cents":66,"depth_cents":3}}}` | R-STORY#line-71; raw cumulative prefixes above |
| depth_size | `{"BAR":{"bid_depth_5":69462,"ask_depth_5":82550,"bid_share":0.456950767044707,"top_bid_size":5906,"top_ask_size":18500},"GIU":{"bid_depth_5":63418,"ask_depth_5":85982,"bid_share":0.42448460508701474,"top_bid_size":17000,"top_ask_size":18784}}` | R-STORY#line-71; raw cumulative prefixes above |
| volume | `{"BAR":{"print_count":16,"contracts":1688.3100000000002},"GIU":{"print_count":16,"contracts":1441.3400000000001}}` | R-STORY#line-71; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.8333333333333334,"drift_sum_cents":5,"both_legs_named":true}` | R-STORY#line-71; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-71; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":12.198236388895246,"hours_to_truth_bell":0.4128747222158644,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-71; raw cumulative prefixes above |
| books | `{"BAR":{"bid_cents":16,"ask_cents":17,"last_trade_cents":19,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-16418"},"GIU":{"bid_cents":83,"ask_cents":84,"last_trade_cents":69,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-14103"}}` | R-STORY#line-71; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":1,"entry_sum_cents":19,"standing_count":1,"legs":{"BAR":{"credited":true,"entry_cents":19,"standing_target_cents":null,"fill_receipt":"22676ea3-972a-46e2-a3ef-d4dda2d1c002","fill_timestamp_epoch":1783875234.432},"GIU":{"credited":false,"entry_cents":null,"standing_target_cents":61}}}` | R-STORY#line-71; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":36,"leg0_anchor_cents":31,"leg1_anchor_cents":67,"leg0_drift_cents":-12,"leg1_drift_cents":17,"leg0_travel_cents":31,"leg1_travel_cents":35,"joint_mid_sum_cents":103,"joint_spread_cents":2,"inverse_coherence":0.8333333333333334,"volume_log1p":8.04899592970587,"hours_from_discovery":12.198236388895246,"divot_depth_cents":1.492063492063492,"oriented_leg_ids":["BAR","GIU"]}` [R-STORY#line-71; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26JUL14KIRSEK (26JUL) | 0.888857 / 1.000000 | R-CORPUS#row-2764; RANGE_SPECTRUM_PATH | R-RANGE#row-914; KIR anchor 32 (tick#1[1784009568,30,31,32]), low 20 (tick#70[1784039795,20,21,21]), close 20 (terminal tick#71[1784040763,16,20,20]); SEK anchor 68 (tick#1[1784009568,68,70,68]), low 55 (tick#68[1784039169,52,61,55]), close 83 (terminal tick#71[1784040763,80,84,83]) |
| N2 | KXATPCHALLENGERMATCH-26JUN20HAREST (26JUN) | 0.875713 / 1.000000 | R-CORPUS#row-3617; RANGE_SPECTRUM_PATH | R-RANGE#row-1760; EST anchor 34 (tick#1[1781960568,32,34,34]), low 14 (tick#102[1781991081,14,16,16]), close 19 (terminal tick#108[1781992887,17,19,19]); HAR anchor 68 (tick#1[1781960568,67,68,68]), low 52 (tick#107[1781992586,51,52,52]), close 82 (terminal tick#108[1781992887,81,82,82]) |
| N3 | KXATPCHALLENGERMATCH-26APR27STAKRU (26APR) | 0.865666 / 1.000000 | R-CORPUS#row-570; RANGE_SPECTRUM_PATH | R-RANGE#row-205; STA anchor 32 (tick#1[1777245174,28,31,32]), low 12 (tick#100[1777276285,7,11,12]), close 16 (terminal tick#101[1777276608,14,15,16]); KRU anchor 69 (tick#1[1777245174,68,71,69]), low 64 (tick#94[1777274090,64,69,69]), close 86 (terminal tick#101[1777276608,83,84,86]) |
| N4 | KXATPCHALLENGERMATCH-26MAY10ROCJOH (26MAY) | 0.864001 / 1.000000 | R-CORPUS#row-5388; RANGE_SPECTRUM_PATH | R-RANGE#row-2327; ROC anchor 32 (tick#1[1778394883,30,32,32]), low 8 (tick#107[1778427219,8,18,8]), close 16 (terminal tick#174[1778447492,15,16,16]); JOH anchor 69 (tick#1[1778394883,66,69,0]), low 66 (tick#1[1778394883,66,69,0]), close 84 (terminal tick#174[1778447492,83,84,84]) |
| N5 | KXATPCHALLENGERMATCH-26MAY11JONRAW (26MAY) | 0.863040 / 1.000000 | R-CORPUS#row-5440; RANGE_SPECTRUM_PATH | R-RANGE#row-2374; RAW anchor 32 (tick#1[1778462632,31,32,32]), low 16 (tick#104[1778494924,15,17,16]), close 16 (terminal tick#104[1778494924,15,17,16]); JON anchor 69 (tick#1[1778462632,67,69,69]), low 62 (tick#94[1778491889,59,62,62]), close 85 (terminal tick#104[1778494924,83,84,85]) |
| N6 | KXATPCHALLENGERMATCH-26MAY19ORAJUS (26MAY) | 0.861698 / 1.000000 | R-CORPUS#row-5757; RANGE_SPECTRUM_PATH | R-RANGE#row-2686; ORA anchor 35 (tick#1[1779169477,34,35,35]), low 15 (tick#108[1779201959,15,16,15]), close 21 (terminal tick#109[1779202613,20,21,21]); JUS anchor 67 (tick#1[1779169477,66,67,67]), low 55 (tick#101[1779199798,52,56,55]), close 79 (terminal tick#109[1779202613,79,80,79]) |
| N7 | KXATPCHALLENGERMATCH-26JUN13TARROM (26JUN) | 0.859931 / 1.000000 | R-CORPUS#row-3332; RANGE_SPECTRUM_PATH | R-RANGE#row-1478; ROM anchor 34 (tick#1[1781316055,34,35,34]), low 16 (tick#101[1781346953,15,16,16]), close 19 (terminal tick#114[1781351207,18,19,19]); TAR anchor 66 (tick#1[1781316055,65,66,66]), low 51 (tick#110[1781349669,49,50,51]), close 82 (terminal tick#114[1781351207,81,82,82]) |

**Derivation arithmetic → action → verbatim sentence.**

**BAR.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUL14KIRSEK:(0.888857×1.000000)×(20/32) + KXATPCHALLENGERMATCH-26JUN20HAREST:(0.875713×1.000000)×(14/34) + KXATPCHALLENGERMATCH-26APR27STAKRU:(0.865666×1.000000)×(12/32) + KXATPCHALLENGERMATCH-26MAY10ROCJOH:(0.864001×1.000000)×(8/32) + KXATPCHALLENGERMATCH-26MAY11JONRAW:(0.863040×1.000000)×(16/32) + KXATPCHALLENGERMATCH-26MAY19ORAJUS:(0.861698×1.000000)×(15/35) + KXATPCHALLENGERMATCH-26JUN13TARROM:(0.859931×1.000000)×(16/34)) / 6.078907 = 0.437947378248. Raw round(31×0.437947378248)=14; mass=0.868415304047; blend with lineage 16 gives 14; min(pair cap 38, post-only cap 16) gives 14. Printed action PLACE_REST@14, active-before NONE.

> At 12.198236 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26JUL14KIRSEK@0.888857, KXATPCHALLENGERMATCH-26JUN20HAREST@0.875713, KXATPCHALLENGERMATCH-26APR27STAKRU@0.865666, KXATPCHALLENGERMATCH-26MAY10ROCJOH@0.864001, KXATPCHALLENGERMATCH-26MAY11JONRAW@0.863040, KXATPCHALLENGERMATCH-26MAY19ORAJUS@0.861698, KXATPCHALLENGERMATCH-26JUN13TARROM@0.859931. BAR has anchor 31, neighborhood low ratio 0.43794737824765906, lineage target 16, pair cap 38, and post-only cap 16. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=14; ACTIVE_TARGET_BEFORE_CENTS=NONE.

**GIU.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUL14KIRSEK:(0.888857×1.000000)×(55/68) + KXATPCHALLENGERMATCH-26JUN20HAREST:(0.875713×1.000000)×(52/68) + KXATPCHALLENGERMATCH-26APR27STAKRU:(0.865666×1.000000)×(64/69) + KXATPCHALLENGERMATCH-26MAY10ROCJOH:(0.864001×1.000000)×(66/69) + KXATPCHALLENGERMATCH-26MAY11JONRAW:(0.863040×1.000000)×(62/69) + KXATPCHALLENGERMATCH-26MAY19ORAJUS:(0.861698×1.000000)×(55/67) + KXATPCHALLENGERMATCH-26JUN13TARROM:(0.859931×1.000000)×(51/66)) / 6.078907 = 0.849709655146. Raw round(67×0.849709655146)=57; mass=0.868415304047; blend with lineage 69 gives 59; min(pair cap 80, post-only cap 83) gives 59. Printed action REPRICE_REST@59, active-before 61.

> At 12.198236 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26JUL14KIRSEK@0.888857, KXATPCHALLENGERMATCH-26JUN20HAREST@0.875713, KXATPCHALLENGERMATCH-26APR27STAKRU@0.865666, KXATPCHALLENGERMATCH-26MAY10ROCJOH@0.864001, KXATPCHALLENGERMATCH-26MAY11JONRAW@0.863040, KXATPCHALLENGERMATCH-26MAY19ORAJUS@0.861698, KXATPCHALLENGERMATCH-26JUN13TARROM@0.859931. GIU has anchor 67, neighborhood low ratio 0.8497096551456921, lineage target 69, pair cap 80, and post-only cap 83. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=59; ACTIVE_TARGET_BEFORE_CENTS=61.

### TP14 — 12.479156 hours from discovery (2026-07-12T17:11:04.961Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

BAR: R-BOOK-BAR#rows-1..23024, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-23024 = 16/30 last 18; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=BAR,ts<=1783876264.962 (33 rows; last #row-60 fd61fb31-54d7-7c6d-bfcd-0a0e2fc63da3@51)

GIU: R-BOOK-GIU#rows-1..21127, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-21127 = 61/76 last 76; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=GIU,ts<=1783876264.962 (26 rows; last #row-62 bfa108bf-25e8-43af-b92b-614d3379c9b3@59)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"BAR":1,"GIU":1},"anchors_cents":{"BAR":31,"GIU":67}}` | R-STORY#line-89; raw cumulative prefixes above |
| opening_split | `{"sum_cents":98,"absolute_split_cents":36}` | R-STORY#line-89; raw cumulative prefixes above |
| drift | `{"BAR":{"current_cents":36,"drift_cents":5},"GIU":{"current_cents":57,"drift_cents":-10}}` | R-STORY#line-89; raw cumulative prefixes above |
| steps_stillness | `{"BAR":{"step_count":134,"last_step_cents":1,"still_seconds":0.023999929428100586},"GIU":{"step_count":58,"last_step_cents":-2,"still_seconds":0}}` | R-STORY#line-89; raw cumulative prefixes above |
| shape_survival | `{"BAR":{"directional_step_share":0.417910447761194,"observed_steps":134},"GIU":{"directional_step_share":0.5,"observed_steps":58}}` | R-STORY#line-89; raw cumulative prefixes above |
| ripeness | `{"BAR":{"continuous_evidence_mass":0.9999566386263117,"observations":23061,"prints":33},"GIU":{"continuous_evidence_mass":0.9999527365535494,"observations":21157,"prints":26}}` | R-STORY#line-89; raw cumulative prefixes above |
| lows_travel | `{"BAR":{"low_cents":16,"high_cents":51,"travel_cents":35},"GIU":{"low_cents":49,"high_cents":86,"travel_cents":37}}` | R-STORY#line-89; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":93,"spread_sum_cents":29,"dwell_seconds":{"BAR":0.023999929428100586,"GIU":0}}` | R-STORY#line-89; raw cumulative prefixes above |
| divots | `{"BAR":{"count":26,"mean_depth_cents":3.6538461538461537,"latest":{"timestamp_epoch":1783876264.936,"receipt":"605c4b26-a526-7156-a530-b3ae22511439","floor_cents":35,"depth_cents":1}},"GIU":{"count":12,"mean_depth_cents":3.8333333333333335,"latest":{"timestamp_epoch":1783875969,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-19556","floor_cents":75,"depth_cents":1}}}` | R-STORY#line-89; raw cumulative prefixes above |
| depth_size | `{"BAR":{"bid_depth_5":431,"ask_depth_5":852,"bid_share":0.33593141075604055,"top_bid_size":279,"top_ask_size":10},"GIU":{"bid_depth_5":622,"ask_depth_5":606,"bid_share":0.506514657980456,"top_bid_size":505,"top_ask_size":14}}` | R-STORY#line-89; raw cumulative prefixes above |
| volume | `{"BAR":{"print_count":33,"contracts":6094.659999999999},"GIU":{"print_count":26,"contracts":2139.82}}` | R-STORY#line-89; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.6875,"drift_sum_cents":-5,"both_legs_named":true}` | R-STORY#line-89; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-89; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":12.479155555566152,"hours_to_truth_bell":0.13195555554495916,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-89; raw cumulative prefixes above |
| books | `{"BAR":{"bid_cents":16,"ask_cents":30,"last_trade_cents":18,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-23024"},"GIU":{"bid_cents":61,"ask_cents":76,"last_trade_cents":76,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-21127"}}` | R-STORY#line-89; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":2,"entry_sum_cents":78,"standing_count":0,"legs":{"BAR":{"credited":true,"entry_cents":19,"standing_target_cents":null,"fill_receipt":"22676ea3-972a-46e2-a3ef-d4dda2d1c002","fill_timestamp_epoch":1783875234.432},"GIU":{"credited":true,"entry_cents":59,"standing_target_cents":null,"fill_receipt":"bfa108bf-25e8-43af-b92b-614d3379c9b3","fill_timestamp_epoch":1783876264.96}}}` | R-STORY#line-89; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":36,"leg0_anchor_cents":31,"leg1_anchor_cents":67,"leg0_drift_cents":5,"leg1_drift_cents":-10,"leg0_travel_cents":35,"leg1_travel_cents":37,"joint_mid_sum_cents":93,"joint_spread_cents":29,"inverse_coherence":0.6875,"volume_log1p":9.016206928709066,"hours_from_discovery":12.479155555566152,"divot_depth_cents":3.7435897435897436,"oriented_leg_ids":["BAR","GIU"]}` [R-STORY#line-89; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26MAY18POUORL (26MAY) | 0.739737 / 1.000000 | R-CORPUS#row-5722; RANGE_SPECTRUM_PATH | R-RANGE#row-2651; ORL anchor 31 (tick#1[1779069915,31,32,31]), low 13 (tick#107[1779102988,12,13,13]), close 40 (terminal tick#114[1779105098,41,42,40]); POU anchor 68 (tick#1[1779069915,68,69,68]), low 49 (tick#97[1779099946,49,54,57]), close 60 (terminal tick#114[1779105098,57,58,60]) |
| N2 | KXATPCHALLENGERMATCH-26JUN28URRZEB (26JUN) | 0.739587 / 1.000000 | R-CORPUS#row-3825; RANGE_SPECTRUM_PATH | R-RANGE#row-1964; URR anchor 29 (tick#1[1782644543,25,29,0]), low 28 (tick#7[1782646356,24,28,0]), close 35 (terminal tick#109[1782678108,33,35,35]); ZEB anchor 70 (tick#1[1782644543,69,70,70]), low 36 (tick#101[1782675642,34,37,36]), close 67 (terminal tick#109[1782678108,66,67,67]) |
| N3 | KXATPCHALLENGERMATCH-26APR22STECOU (26APR) | 0.727597 / 1.000000 | R-CORPUS#row-391; RANGE_SPECTRUM_PATH | R-RANGE#row-45; STE anchor 36 (tick#1[1776859202,19,36,36]), low 15 (tick#97[1776888949,9,15,17]), close 45 (terminal tick#100[1776889869,36,47,45]); COU anchor 66 (tick#1[1776859202,66,79,66]), low 57 (tick#100[1776889869,56,64,57]), close 57 (terminal tick#100[1776889869,56,64,57]) |
| N4 | KXATPCHALLENGERMATCH-26JUL13KUZNIJ (26JUL) | 0.727270 / 1.000000 | R-CORPUS#row-2710; RANGE_SPECTRUM_PATH | R-RANGE#row-860; NIJ anchor 32 (tick#1[1783911249,32,35,32]), low 17 (tick#75[1783941403,19,20,17]), close 37 (terminal tick#76[1783942043,35,39,37]); KUZ anchor 68 (tick#1[1783911249,66,68,68]), low 62 (tick#76[1783942043,61,65,62]), close 62 (terminal tick#76[1783942043,61,65,62]) |
| N5 | KXATPCHALLENGERMATCH-26JUN15CHISMI (26JUN) | 0.725204 / 1.000000 | R-CORPUS#row-3418; RANGE_SPECTRUM_PATH | R-RANGE#row-1562; CHI anchor 34 (tick#1[1781503852,32,35,34]), low 34 (tick#1[1781503852,32,35,34]), close 38 (terminal tick#82[1781535823,38,39,38]); SMI anchor 67 (tick#1[1781503852,66,68,67]), low 32 (tick#78[1781534280,32,33,32]), close 62 (terminal tick#82[1781535823,60,61,62]) |
| N6 | KXATPCHALLENGERMATCH-26APR23GIUALK (26APR) | 0.724573 / 1.000000 | R-CORPUS#row-403; RANGE_SPECTRUM_PATH | R-RANGE#row-56; GIU anchor 31 (tick#32[1776954710,31,33,0]), low 12 (tick#90[1776975333,11,12,12]), close 35 (terminal tick#95[1776976879,34,35,35]); ALK anchor 66 (tick#1[1776945283,67,69,66]), low 57 (tick#94[1776976569,56,57,57]), close 66 (terminal tick#95[1776976879,66,67,66]) |
| N7 | KXATPCHALLENGERMATCH-26JUN09HEMMOR (26JUN) | 0.718848 / 1.000000 | R-CORPUS#row-3209; RANGE_SPECTRUM_PATH | R-RANGE#row-1357; HEM anchor 32 (tick#1[1780971680,32,35,32]), low 25 (tick#87[1781002411,24,25,25]), close 45 (terminal tick#96[1781005523,43,44,45]); MOR anchor 70 (tick#1[1780971680,63,67,70]), low 37 (tick#94[1781004586,35,37,37]), close 60 (terminal tick#96[1781005523,54,55,60]) |

**Derivation arithmetic → action → verbatim sentence.**

**BAR.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAY18POUORL:(0.739737×1.000000)×(13/31) + KXATPCHALLENGERMATCH-26JUN28URRZEB:(0.739587×1.000000)×(28/29) + KXATPCHALLENGERMATCH-26APR22STECOU:(0.727597×1.000000)×(15/36) + KXATPCHALLENGERMATCH-26JUL13KUZNIJ:(0.727270×1.000000)×(17/32) + KXATPCHALLENGERMATCH-26JUN15CHISMI:(0.725204×1.000000)×(34/34) + KXATPCHALLENGERMATCH-26APR23GIUALK:(0.724573×1.000000)×(12/31) + KXATPCHALLENGERMATCH-26JUN09HEMMOR:(0.718848×1.000000)×(25/32)) / 5.102815 = 0.642999445087. Raw round(31×0.642999445087)=20; mass=0.728973598647; blend with lineage 21 gives 20; min(pair cap 40, post-only cap 29) gives 20. Printed action PLACE_REST@20, active-before NONE.

> At 12.479156 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26MAY18POUORL@0.739737, KXATPCHALLENGERMATCH-26JUN28URRZEB@0.739587, KXATPCHALLENGERMATCH-26APR22STECOU@0.727597, KXATPCHALLENGERMATCH-26JUL13KUZNIJ@0.727270, KXATPCHALLENGERMATCH-26JUN15CHISMI@0.725204, KXATPCHALLENGERMATCH-26APR23GIUALK@0.724573, KXATPCHALLENGERMATCH-26JUN09HEMMOR@0.718848. BAR has anchor 31, neighborhood low ratio 0.6429994450865535, lineage target 21, pair cap 40, and post-only cap 29. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=20; ACTIVE_TARGET_BEFORE_CENTS=NONE.

**GIU.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAY18POUORL:(0.739737×1.000000)×(49/68) + KXATPCHALLENGERMATCH-26JUN28URRZEB:(0.739587×1.000000)×(36/70) + KXATPCHALLENGERMATCH-26APR22STECOU:(0.727597×1.000000)×(57/66) + KXATPCHALLENGERMATCH-26JUL13KUZNIJ:(0.727270×1.000000)×(62/68) + KXATPCHALLENGERMATCH-26JUN15CHISMI:(0.725204×1.000000)×(32/67) + KXATPCHALLENGERMATCH-26APR23GIUALK:(0.724573×1.000000)×(57/66) + KXATPCHALLENGERMATCH-26JUN09HEMMOR:(0.718848×1.000000)×(37/70)) / 5.102815 = 0.697062037612. Raw round(67×0.697062037612)=47; mass=0.728973598647; blend with lineage 69 gives 53; min(pair cap 80, post-only cap 75) gives 53. Printed action PLACE_REST@53, active-before NONE.

> At 12.479156 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26MAY18POUORL@0.739737, KXATPCHALLENGERMATCH-26JUN28URRZEB@0.739587, KXATPCHALLENGERMATCH-26APR22STECOU@0.727597, KXATPCHALLENGERMATCH-26JUL13KUZNIJ@0.727270, KXATPCHALLENGERMATCH-26JUN15CHISMI@0.725204, KXATPCHALLENGERMATCH-26APR23GIUALK@0.724573, KXATPCHALLENGERMATCH-26JUN09HEMMOR@0.718848. GIU has anchor 67, neighborhood low ratio 0.6970620376115971, lineage target 69, pair cap 80, and post-only cap 75. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=53; ACTIVE_TARGET_BEFORE_CENTS=NONE.

### TP19 — 12.611111 hours from discovery (2026-07-12T17:18:59.999Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

BAR: R-BOOK-BAR#rows-1..25738, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-25738 = 29/30 last 31; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=BAR,ts<=1783876740.000 (34 rows; last #row-68 437c7bb4-ed9f-5aaa-ffe8-302b293e4cff@31)

GIU: R-BOOK-GIU#rows-1..24204, terminal KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-24204 = 70/65 last 73; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL12GIUBAR,leg=GIU,ts<=1783876740.000 (31 rows; last #row-67 e82efe21-0a79-7bee-d0b2-46c9062c7324@73)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"BAR":1,"GIU":1},"anchors_cents":{"BAR":31,"GIU":67}}` | R-STORY#line-119; raw cumulative prefixes above |
| opening_split | `{"sum_cents":98,"absolute_split_cents":36}` | R-STORY#line-119; raw cumulative prefixes above |
| drift | `{"BAR":{"current_cents":31,"drift_cents":0},"GIU":{"current_cents":73,"drift_cents":6}}` | R-STORY#line-119; raw cumulative prefixes above |
| steps_stillness | `{"BAR":{"step_count":139,"last_step_cents":-20,"still_seconds":73.98099994659424},"GIU":{"step_count":74,"last_step_cents":1,"still_seconds":320}}` | R-STORY#line-119; raw cumulative prefixes above |
| shape_survival | `{"BAR":{"directional_step_share":0,"observed_steps":139},"GIU":{"directional_step_share":0.5135135135135135,"observed_steps":74}}` | R-STORY#line-119; raw cumulative prefixes above |
| ripeness | `{"BAR":{"continuous_evidence_mass":0.9999612042209808,"observations":25775,"prints":34},"GIU":{"continuous_evidence_mass":0.9999587407682469,"observations":24236,"prints":31}}` | R-STORY#line-119; raw cumulative prefixes above |
| lows_travel | `{"BAR":{"low_cents":16,"high_cents":51,"travel_cents":35},"GIU":{"low_cents":49,"high_cents":86,"travel_cents":37}}` | R-STORY#line-119; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":104,"spread_sum_cents":-4,"dwell_seconds":{"BAR":73.98099994659424,"GIU":320}}` | R-STORY#line-119; raw cumulative prefixes above |
| divots | `{"BAR":{"count":26,"mean_depth_cents":3.6538461538461537,"latest":{"timestamp_epoch":1783876264.936,"receipt":"605c4b26-a526-7156-a530-b3ae22511439","floor_cents":35,"depth_cents":1}},"GIU":{"count":14,"mean_depth_cents":3.857142857142857,"latest":{"timestamp_epoch":1783876419.54,"receipt":"a61b4b09-3c80-762b-c960-bfb18a9a4180","floor_cents":72,"depth_cents":1}}}` | R-STORY#line-119; raw cumulative prefixes above |
| depth_size | `{"BAR":{"bid_depth_5":13454,"ask_depth_5":40592,"bid_share":0.24893609147763016,"top_bid_size":608,"top_ask_size":13518},"GIU":{"bid_depth_5":15028,"ask_depth_5":41248,"bid_share":0.267041012154382,"top_bid_size":11918,"top_ask_size":1}}` | R-STORY#line-119; raw cumulative prefixes above |
| volume | `{"BAR":{"print_count":34,"contracts":6103.8899999999985},"GIU":{"print_count":31,"contracts":2164.28}}` | R-STORY#line-119; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.1428571428571429,"drift_sum_cents":6,"both_legs_named":true}` | R-STORY#line-119; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-119; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":12.61111111111111,"hours_to_truth_bell":0,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-119; raw cumulative prefixes above |
| books | `{"BAR":{"bid_cents":29,"ask_cents":30,"last_trade_cents":31,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-BAR.csv.gz#row-25738"},"GIU":{"bid_cents":70,"ask_cents":65,"last_trade_cents":73,"receipt":"KXATPCHALLENGERMATCH-26JUL12GIUBAR-GIU.csv.gz#row-24204"}}` | R-STORY#line-119; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":2,"entry_sum_cents":78,"standing_count":0,"legs":{"BAR":{"credited":true,"entry_cents":19,"standing_target_cents":null,"fill_receipt":"22676ea3-972a-46e2-a3ef-d4dda2d1c002","fill_timestamp_epoch":1783875234.432},"GIU":{"credited":true,"entry_cents":59,"standing_target_cents":null,"fill_receipt":"bfa108bf-25e8-43af-b92b-614d3379c9b3","fill_timestamp_epoch":1783876264.96}}}` | R-STORY#line-119; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":36,"leg0_anchor_cents":31,"leg1_anchor_cents":67,"leg0_drift_cents":0,"leg1_drift_cents":6,"leg0_travel_cents":35,"leg1_travel_cents":37,"joint_mid_sum_cents":104,"joint_spread_cents":-4,"inverse_coherence":0.1428571428571429,"volume_log1p":9.020289420224106,"hours_from_discovery":12.61111111111111,"divot_depth_cents":3.7554945054945055,"oriented_leg_ids":["BAR","GIU"]}` [R-STORY#line-119; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26JUN17BALRAT (26JUN) | 0.817771 / 1.000000 | R-CORPUS#row-3540; RANGE_SPECTRUM_PATH | R-RANGE#row-1683; RAT anchor 31 (tick#1[1781675181,30,31,0]), low 21 (tick#86[1781706078,21,22,21]), close 28 (terminal tick#90[1781707330,28,29,28]); BAL anchor 71 (tick#1[1781675181,69,70,71]), low 46 (tick#88[1781706681,45,47,46]), close 71 (terminal tick#90[1781707330,71,72,71]) |
| N2 | KXATPCHALLENGERMATCH-26JUN30ROCBAS (26JUN) | 0.808262 / 1.000000 | R-CORPUS#row-3926; RANGE_SPECTRUM_PATH | R-RANGE#row-2057; BAS anchor 35 (tick#1[1782799305,32,35,0]), low 14 (tick#98[1782830378,12,14,14]), close 35 (terminal tick#110[1782834169,26,32,35]); ROC anchor 67 (tick#1[1782799305,65,67,67]), low 64 (tick#101[1782831297,65,68,64]), close 69 (terminal tick#110[1782834169,66,72,69]) |
| N3 | KXATPCHALLENGERMATCH-26APR23GIUALK (26APR) | 0.805192 / 1.000000 | R-CORPUS#row-403; RANGE_SPECTRUM_PATH | R-RANGE#row-56; GIU anchor 31 (tick#32[1776954710,31,33,0]), low 12 (tick#90[1776975333,11,12,12]), close 35 (terminal tick#95[1776976879,34,35,35]); ALK anchor 66 (tick#1[1776945283,67,69,66]), low 57 (tick#94[1776976569,56,57,57]), close 66 (terminal tick#95[1776976879,66,67,66]) |
| N4 | KXATPCHALLENGERMATCH-26JUN07WINGRA (26JUN) | 0.798481 / 1.000000 | R-CORPUS#row-3131; RANGE_SPECTRUM_PATH | R-RANGE#row-1280; WIN anchor 33 (tick#1[1780814337,29,33,0]), low 28 (tick#3[1780815273,28,34,0]), close 30 (terminal tick#100[1780848925,28,30,30]); GRA anchor 70 (tick#5[1780815876,66,70,0]), low 42 (tick#89[1780845261,42,43,46]), close 72 (terminal tick#100[1780848925,70,72,72]) |
| N5 | KXATPCHALLENGERMATCH-26JUN30ROMCEC (26JUN) | 0.790660 / 1.000000 | R-CORPUS#row-3928; RANGE_SPECTRUM_PATH | R-RANGE#row-2059; ROM anchor 33 (tick#1[1782799305,33,35,33]), low 20 (tick#95[1782829411,20,22,20]), close 36 (terminal tick#110[1782834169,32,36,36]); CEC anchor 66 (tick#1[1782799305,65,66,66]), low 35 (tick#103[1782831938,33,34,35]), close 68 (terminal tick#110[1782834169,64,69,68]) |
| N6 | KXATPCHALLENGERMATCH-26JUN11RIBROD (26JUN) | 0.790130 / 1.000000 | R-CORPUS#row-3279; RANGE_SPECTRUM_PATH | R-RANGE#row-1425; ROD anchor 34 (tick#1[1781163071,32,35,34]), low 13 (tick#94[1781193850,12,13,13]), close 32 (terminal tick#97[1781195089,31,32,32]); RIB anchor 68 (tick#1[1781163071,65,68,0]), low 64 (tick#10[1781166114,64,68,0]), close 68 (terminal tick#97[1781195089,68,69,68]) |
| N7 | KXATPCHALLENGERMATCH-26MAY26DALSCH (26MAY) | 0.785274 / 1.000000 | R-CORPUS#row-5940; RANGE_SPECTRUM_PATH | R-RANGE#row-2857; DAL anchor 37 (tick#1[1779781875,34,37,0]), low 13 (tick#108[1779814530,13,14,13]), close 35 (terminal tick#113[1779816080,33,34,35]); SCH anchor 67 (tick#1[1779781875,63,65,67]), low 43 (tick#100[1779812066,43,44,47]), close 66 (terminal tick#113[1779816080,65,66,66]) |

**Derivation arithmetic → action → verbatim sentence.**

**BAR.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN17BALRAT:(0.817771×1.000000)×(21/31) + KXATPCHALLENGERMATCH-26JUN30ROCBAS:(0.808262×1.000000)×(14/35) + KXATPCHALLENGERMATCH-26APR23GIUALK:(0.805192×1.000000)×(12/31) + KXATPCHALLENGERMATCH-26JUN07WINGRA:(0.798481×1.000000)×(28/33) + KXATPCHALLENGERMATCH-26JUN30ROMCEC:(0.790660×1.000000)×(20/33) + KXATPCHALLENGERMATCH-26JUN11RIBROD:(0.790130×1.000000)×(13/34) + KXATPCHALLENGERMATCH-26MAY26DALSCH:(0.785274×1.000000)×(13/37)) / 5.595769 = 0.522478280880. Raw round(31×0.522478280880)=16; mass=0.799395600997; blend with lineage 21 gives 17; min(pair cap 40, post-only cap 29) gives 17. Printed action PLACE_REST@17, active-before NONE.

> At 12.611111 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26JUN17BALRAT@0.817771, KXATPCHALLENGERMATCH-26JUN30ROCBAS@0.808262, KXATPCHALLENGERMATCH-26APR23GIUALK@0.805192, KXATPCHALLENGERMATCH-26JUN07WINGRA@0.798481, KXATPCHALLENGERMATCH-26JUN30ROMCEC@0.790660, KXATPCHALLENGERMATCH-26JUN11RIBROD@0.790130, KXATPCHALLENGERMATCH-26MAY26DALSCH@0.785274. BAR has anchor 31, neighborhood low ratio 0.5224782808804869, lineage target 21, pair cap 40, and post-only cap 29. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=17; ACTIVE_TARGET_BEFORE_CENTS=NONE.

**GIU.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN17BALRAT:(0.817771×1.000000)×(46/71) + KXATPCHALLENGERMATCH-26JUN30ROCBAS:(0.808262×1.000000)×(64/67) + KXATPCHALLENGERMATCH-26APR23GIUALK:(0.805192×1.000000)×(57/66) + KXATPCHALLENGERMATCH-26JUN07WINGRA:(0.798481×1.000000)×(42/70) + KXATPCHALLENGERMATCH-26JUN30ROMCEC:(0.790660×1.000000)×(35/66) + KXATPCHALLENGERMATCH-26JUN11RIBROD:(0.790130×1.000000)×(64/68) + KXATPCHALLENGERMATCH-26MAY26DALSCH:(0.785274×1.000000)×(43/67)) / 5.595769 = 0.740434149177. Raw round(67×0.740434149177)=50; mass=0.799395600997; blend with lineage 69 gives 54; min(pair cap 80, post-only cap 64) gives 54. Printed action PLACE_REST@54, active-before NONE.

> At 12.611111 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL12GIUBAR. The named neighborhood is KXATPCHALLENGERMATCH-26JUN17BALRAT@0.817771, KXATPCHALLENGERMATCH-26JUN30ROCBAS@0.808262, KXATPCHALLENGERMATCH-26APR23GIUALK@0.805192, KXATPCHALLENGERMATCH-26JUN07WINGRA@0.798481, KXATPCHALLENGERMATCH-26JUN30ROMCEC@0.790660, KXATPCHALLENGERMATCH-26JUN11RIBROD@0.790130, KXATPCHALLENGERMATCH-26MAY26DALSCH@0.785274. GIU has anchor 67, neighborhood low ratio 0.7404341491771169, lineage target 69, pair cap 80, and post-only cap 64. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=54; ACTIVE_TARGET_BEFORE_CENTS=NONE.


## 3. Capture vs ceiling

Status: **PROVISIONAL_UNTIL_CC_RULES_BELL**. L11 bell 1783876740 from TAPE_INFERENCE; this explanation does not alter it.

| Side | Deepest lawful print | Moment | Receipt | Captured | Gap to ceiling |
|---|---:|---|---|---:|---:|
| BAR | 16 | 12.060350 h after formation; 2026-07-12T16:54:35.261Z | R-PRINTS#row-37; d491a073-04d2-66e9-2fc1-d805c6d5528d | 19 | 3 |
| GIU | 49 | 12.354732 h after formation; 2026-07-12T17:12:15.036Z | R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e | 59 | 10 |

Pair ceiling: 65¢, discount 35¢. Captured pair: 78, discount 22. Per-side minima need not be simultaneous; this is the deepest standing-rest opportunity each side's tape actually offered.

## 4. The surprise and humility ledger

### Every receipt-defined neighborhood-range departure

Audit convention: because pass 1 emitted no prediction interval, the expected range is the minimum-to-maximum normalized low of its seven named neighbors, mapped onto the target anchor. Every pass-1 stage whose later lawful true-print minimum left that envelope is listed; this is an explanation metric, not a model change.

| Stage | Side | Neighbor-low prediction | Realized | Departure | Realization receipt |
|---:|---|---:|---:|---:|---|
| 1 @ 0.000000h | BAR | 21.46..31.00 | 16 | DEEPER_THAN_ALL_NEIGHBORS by 5.46¢ | 2026-07-12T16:54:35.261Z; R-PRINTS#row-37; d491a073-04d2-66e9-2fc1-d805c6d5528d |
| 3 @ 0.143889h | GIU | 63.06..67.00 | 49 | DEEPER_THAN_ALL_NEIGHBORS by 14.06¢ | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 4 @ 0.670007h | GIU | 63.06..67.00 | 49 | DEEPER_THAN_ALL_NEIGHBORS by 14.06¢ | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 5 @ 2.905918h | GIU | 59.23..67.00 | 49 | DEEPER_THAN_ALL_NEIGHBORS by 10.23¢ | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 8 @ 8.998056h | GIU | 59.23..67.00 | 49 | DEEPER_THAN_ALL_NEIGHBORS by 10.23¢ | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 11 @ 12.198236h | GIU | 51.24..64.09 | 49 | DEEPER_THAN_ALL_NEIGHBORS by 2.24¢ | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 12 @ 12.204167h | GIU | 49.74..64.09 | 49 | DEEPER_THAN_ALL_NEIGHBORS by 0.74¢ | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 16 @ 12.480278h | BAR | 6.20..23.77 | 31 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 7.23¢ | 2026-07-12T17:19:00.000Z; R-PRINTS#row-68; 437c7bb4-ed9f-5aaa-ffe8-302b293e4cff |

### Every decision hindsight beats

A decision is listed when a later formation-lawful true print proves a different rest would have captured closer to the per-side ceiling, or when a credited leg still receives a new action sentence. This is hindsight, never a claim that the future row was knowable.

| Stage | Side | Printed decision | Hindsight-better action | Reading that could have licensed it | Realized receipt / defect |
|---:|---|---|---|---|---|
| 3 @ 0.143889h | BAR | PLACE_REST@24 | REST@16 | neighborhood low envelope 11.85..31.00 | 2026-07-12T16:54:35.261Z; R-PRINTS#row-37; d491a073-04d2-66e9-2fc1-d805c6d5528d |
| 3 @ 0.143889h | GIU | PLACE_REST@65 | REST@49 | lows_travel running low 49 | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 4 @ 0.670007h | BAR | REPRICE_REST@22 | REST@16 | neighborhood low envelope 11.85..31.00 | 2026-07-12T16:54:35.261Z; R-PRINTS#row-37; d491a073-04d2-66e9-2fc1-d805c6d5528d |
| 4 @ 0.670007h | GIU | REPRICE_REST@64 | REST@49 | lows_travel running low 49 | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 5 @ 2.905918h | BAR | HOLD_REST@22 | REST@16 | neighborhood low envelope 11.85..27.13 | 2026-07-12T16:54:35.261Z; R-PRINTS#row-37; d491a073-04d2-66e9-2fc1-d805c6d5528d |
| 5 @ 2.905918h | GIU | REPRICE_REST@65 | REST@49 | lows_travel running low 49 | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 6 @ 2.970000h | BAR | REPRICE_REST@24 | REST@16 | neighborhood low envelope 16.00..31.00 | 2026-07-12T16:54:35.261Z; R-PRINTS#row-37; d491a073-04d2-66e9-2fc1-d805c6d5528d |
| 6 @ 2.970000h | GIU | REPRICE_REST@63 | REST@49 | neighborhood low envelope 49.00..67.00 | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 7 @ 5.998889h | BAR | REPRICE_REST@25 | REST@16 | neighborhood low envelope 16.00..31.00 | 2026-07-12T16:54:35.261Z; R-PRINTS#row-37; d491a073-04d2-66e9-2fc1-d805c6d5528d |
| 7 @ 5.998889h | GIU | HOLD_REST@63 | REST@49 | neighborhood low envelope 49.00..67.00 | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 8 @ 8.998056h | BAR | REPRICE_REST@22 | REST@16 | neighborhood low envelope 11.85..30.06 | 2026-07-12T16:54:35.261Z; R-PRINTS#row-37; d491a073-04d2-66e9-2fc1-d805c6d5528d |
| 8 @ 8.998056h | GIU | REPRICE_REST@65 | REST@49 | lows_travel running low 49 | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 9 @ 12.000000h | BAR | REPRICE_REST@23 | REST@16 | neighborhood low envelope 12.40..29.00 | 2026-07-12T16:54:35.261Z; R-PRINTS#row-37; d491a073-04d2-66e9-2fc1-d805c6d5528d |
| 9 @ 12.000000h | GIU | REPRICE_REST@61 | REST@49 | neighborhood low envelope 49.00..67.00 | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 10 @ 12.192778h | BAR | REPRICE_REST@20 | REST@16 | neighborhood low envelope 11.85..29.00 | 2026-07-12T16:54:35.261Z; R-PRINTS#row-37; d491a073-04d2-66e9-2fc1-d805c6d5528d |
| 10 @ 12.192778h | GIU | HOLD_REST@61 | REST@49 | neighborhood low envelope 40.20..67.00 | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 11 @ 12.198236h | BAR | PLACE_REST@14 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 11 @ 12.198236h | GIU | REPRICE_REST@59 | REST@49 | lows_travel running low 49 | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 12 @ 12.204167h | BAR | PLACE_REST@14 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 12 @ 12.204167h | GIU | REPRICE_REST@57 | REST@49 | lows_travel running low 49 | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 13 @ 12.479149h | BAR | PLACE_REST@23 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 13 @ 12.479149h | GIU | REPRICE_REST@61 | REST@49 | neighborhood low envelope 45.02..65.94 | 2026-07-12T17:12:15.036Z; R-PRINTS#row-63; 32f3190d-6328-42bd-986c-a06460cddb2e |
| 14 @ 12.479156h | BAR | PLACE_REST@20 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 14 @ 12.479156h | GIU | PLACE_REST@53 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 15 @ 12.479167h | BAR | PLACE_REST@19 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 15 @ 12.479167h | GIU | PLACE_REST@62 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 16 @ 12.480278h | BAR | PLACE_REST@16 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 16 @ 12.480278h | GIU | PLACE_REST@63 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 17 @ 12.590561h | BAR | PLACE_REST@17 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 17 @ 12.590561h | GIU | PLACE_REST@54 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 18 @ 12.603056h | BAR | PLACE_REST@17 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 18 @ 12.603056h | GIU | PLACE_REST@54 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 19 @ 12.611111h | BAR | PLACE_REST@17 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 19 @ 12.611111h | GIU | PLACE_REST@54 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |

### What remains unexplained

- No receipt names the exogenous cause of the late BAR/GIU collapse; the stores contain market data, not player-status news.
- The bell is TAPE_INFERENCE, not a CC-ratified official time, so the ceiling remains provisional.
- The derivation receipt does not explain why a credited leg still receives a PLACE_REST sentence while the executor silently suppresses it.
