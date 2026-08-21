# Game explained — DANPRA

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
- **R-TRUTH:** `c0056976:.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.json`, SHA-256 `f7bc71d8e615859db272d841e125bc4836a685d82bb2d6769762c9bc19e56729`; event row `KXATPMATCH-26JUL18DANPRA`, bell 1784373060 (TAPE_INFERENCE).
- **R-LINEAGE:** external custody `C:\Users\omigr\OMI-Workspace\.claude\window1_live_v4_replay\v54_walk5_live_20260821\FULL_DECISION_TRACE_5.jsonl.gz`, SHA-256 `085fbf04dbc16f8c76691a0823a5370061afc9d738b5eefda9eab92fef4ccbc4`, 55209610 bytes, 133626 rows; only lineage values already printed in R-STORY are used here.
- **R-BOOK-DAN:** external custody `C:\Users\omigr\OMI-Window1-private\fit-local\ticks\KXATPMATCH-26JUL18DANPRA-DAN.csv.gz`, SHA-256 `4880e507c83adef39f990b979f6b3f26514e9da506f1e9f156813b555e9b7537`, 321874 bytes, 36941 data rows.
- **R-BOOK-PRA:** external custody `C:\Users\omigr\OMI-Window1-private\fit-local\ticks\KXATPMATCH-26JUL18DANPRA-PRA.csv.gz`, SHA-256 `0e4b5032d4fb8430453a18e91377a2d177835254863dbb7baa8733bc74d8428f`, 314263 bytes, 32431 data rows.

## 1. The story — hour 0 to bell (222 words; two-page guard passed)

Hour 0 looked like a noisy 58/41 anchor pair, but formation lasted 4.321944 hours. The pre-formation tape wandered through 52/34, 52/60, and 71/60; formation law correctly kept every target absent. At formation completion, the first rests were 49 DAN / 36 PRA.

By hour 5.546949 the books had settled near 58/43 and the OS wanted 51/38. DAN then stayed near 59–62 while PRA stayed near 40–43. PRA's rest moved down to 31 and finally back to 33; DAN stayed 51. The displayed market thus held the operator's roughly 59/40 shape while the machine waited for the deeper dips its named May/June neighborhood had historically shown.

Those dips never arrived. The deepest lawful prints were 59 DAN and 41 PRA, summing to par. The provisional ceiling was therefore zero discount. Neither 51 nor 33 could fill; their final shortfalls were 8 cents per side. Hindsight could have completed at 59/41, but that would have bought no pair discount, so completion alone would not have improved the economic story.

The final arithmetic was coherent but overconfident about travel: 58×0.863019 blended with lineage 59 became 51; 41×0.788299 blended with lineage 40 became 33. The exact May/June terminal tape rows are below. What remains unexplained is why DANPRA survived without the neighborhood's typical dip; the receipts contain prices and books, not injury, scheduling, or participant-state causes.

## 2. Turning points — 8 complete causal chains

### TP1 — 0.000000 hours from discovery (2026-07-17T19:36:34.000Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

DAN: R-BOOK-DAN#rows-1..1, terminal KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-1 = 6/94 last NONE; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=DAN,ts<=1784316994.000 (0 rows)

PRA: R-BOOK-PRA#rows-1..1, terminal KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-1 = 6/94 last NONE; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=PRA,ts<=1784316994.000 (0 rows)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"DAN":0,"PRA":0},"anchors_cents":{"DAN":58,"PRA":41}}` | R-STORY#line-420; raw cumulative prefixes above |
| opening_split | `{"sum_cents":99,"absolute_split_cents":17}` | R-STORY#line-420; raw cumulative prefixes above |
| drift | `{"DAN":{"current_cents":50,"drift_cents":-8},"PRA":{"current_cents":50,"drift_cents":9}}` | R-STORY#line-420; raw cumulative prefixes above |
| steps_stillness | `{"DAN":{"step_count":0,"last_step_cents":null,"still_seconds":0},"PRA":{"step_count":0,"last_step_cents":null,"still_seconds":0}}` | R-STORY#line-420; raw cumulative prefixes above |
| shape_survival | `{"DAN":{"directional_step_share":null,"observed_steps":0},"PRA":{"directional_step_share":null,"observed_steps":0}}` | R-STORY#line-420; raw cumulative prefixes above |
| ripeness | `{"DAN":{"continuous_evidence_mass":0.5,"observations":1,"prints":0},"PRA":{"continuous_evidence_mass":0.5,"observations":1,"prints":0}}` | R-STORY#line-420; raw cumulative prefixes above |
| lows_travel | `{"DAN":{"low_cents":50,"high_cents":50,"travel_cents":0},"PRA":{"low_cents":50,"high_cents":50,"travel_cents":0}}` | R-STORY#line-420; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":100,"spread_sum_cents":176,"dwell_seconds":{"DAN":0,"PRA":0}}` | R-STORY#line-420; raw cumulative prefixes above |
| divots | `{"DAN":{"count":0,"mean_depth_cents":null,"latest":null},"PRA":{"count":0,"mean_depth_cents":null,"latest":null}}` | R-STORY#line-420; raw cumulative prefixes above |
| depth_size | `{"DAN":{"bid_depth_5":2926,"ask_depth_5":2977,"bid_share":0.4956801626291716,"top_bid_size":217,"top_ask_size":200},"PRA":{"bid_depth_5":2926,"ask_depth_5":2976,"bid_share":0.4957641477465266,"top_bid_size":217,"top_ask_size":200}}` | R-STORY#line-420; raw cumulative prefixes above |
| volume | `{"DAN":{"print_count":0,"contracts":0},"PRA":{"print_count":0,"contracts":0}}` | R-STORY#line-420; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.9444444444444444,"drift_sum_cents":1,"both_legs_named":true}` | R-STORY#line-420; raw cumulative prefixes above |
| category | `{"category":"ATP_MAIN"}` | R-STORY#line-420; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":0,"hours_to_truth_bell":15.573888888888888,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-420; raw cumulative prefixes above |
| books | `{"DAN":{"bid_cents":6,"ask_cents":94,"last_trade_cents":null,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-1"},"PRA":{"bid_cents":6,"ask_cents":94,"last_trade_cents":null,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-1"}}` | R-STORY#line-420; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":0,"legs":{"DAN":{"credited":false,"entry_cents":null,"standing_target_cents":null},"PRA":{"credited":false,"entry_cents":null,"standing_target_cents":null}}}` | R-STORY#line-420; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_MAIN","anchor_split_cents":17,"leg0_anchor_cents":41,"leg1_anchor_cents":58,"leg0_drift_cents":9,"leg1_drift_cents":-8,"leg0_travel_cents":0,"leg1_travel_cents":0,"joint_mid_sum_cents":100,"joint_spread_cents":176,"inverse_coherence":0.9444444444444444,"volume_log1p":0,"hours_from_discovery":0,"divot_depth_cents":null,"oriented_leg_ids":["PRA","DAN"]}` [R-STORY#line-420; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXWTACHALLENGERMATCH-26JUN14LEOKUL (26JUN) | 0.612638 / 0.945205 | R-CORPUS#row-9693; RANGE_SPECTRUM_PATH | R-RANGE#row-4604; LEO anchor 46 (tick#48[1781416329,5,46,46]), low 46 (tick#48[1781416329,5,46,46]), close 55 (terminal tick#72[1781424913,59,64,55]); KUL anchor 63 (tick#48[1781416329,31,63,63]), low 40 (tick#60[1781420280,38,40,41]), close 40 (terminal tick#72[1781424913,38,40,40]) |
| N2 | KXATPMATCH-26JAN08MMOKHA (26JAN) | 0.467466 / 0.732877 | R-CORPUS#row-6826; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-1953; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N3 | KXATPCHALLENGERMATCH-26MAR05CECKYM (26MAR) | 0.450936 / 0.732877 | R-CORPUS#row-4109; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-5512; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N4 | KXATPCHALLENGERMATCH-26MAY10LOMNED (26MAY) | 0.445283 / 0.945205 | R-CORPUS#row-5374; RANGE_SPECTRUM_PATH | R-RANGE#row-2313; NED anchor 45 (tick#98[1778411214,19,35,45]), low 38 (tick#101[1778412119,30,37,38]), close 39 (terminal tick#109[1778414539,40,45,39]); LOM anchor 76 (tick#98[1778411214,63,79,76]), low 52 (tick#108[1778414229,45,51,52]), close 57 (terminal tick#109[1778414539,53,59,57]) |
| N5 | KXATPCHALLENGERMATCH-26MAY12HUEVAR (26MAY) | 0.438847 / 0.945205 | R-CORPUS#row-5502; RANGE_SPECTRUM_PATH | R-RANGE#row-2434; HUE anchor 38 (tick#56[1778591972,38,84,0]), low 21 (tick#75[1778597698,21,33,38]), close 21 (terminal tick#95[1778603748,16,24,21]); VAR anchor 64 (tick#55[1778591671,12,64,0]), low 64 (tick#55[1778591671,12,64,0]), close 86 (terminal tick#95[1778603748,76,86,86]) |
| N6 | KXATPCHALLENGERMATCH-26MAR05HEMGEA (26MAR) | 0.434523 / 0.732877 | R-CORPUS#row-4115; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-5511; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N7 | KXATPCHALLENGERMATCH-26MAY31SCOHON (26MAY) | 0.433257 / 0.945205 | R-CORPUS#row-6115; RANGE_SPECTRUM_PATH | R-RANGE#row-3022; SCO anchor 13 (tick#62[1780204147,10,13,0]), low 9 (tick#63[1780204448,9,13,0]), close 13 (terminal tick#96[1780214399,9,13,13]); HON anchor 90 (tick#8[1780187867,10,90,0]), low 90 (tick#8[1780187867,10,90,0]), close 90 (terminal tick#96[1780214399,87,90,90]) |

**Derivation arithmetic → action → verbatim sentence.**

**DAN.** Formation progress 0.000000 < 1 overrides the computed candidate; lawful action is HOLD_REST@NONE.

> At 0.000000 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXWTACHALLENGERMATCH-26JUN14LEOKUL@0.612638, KXATPMATCH-26JAN08MMOKHA@0.467466, KXATPCHALLENGERMATCH-26MAR05CECKYM@0.450936, KXATPCHALLENGERMATCH-26MAY10LOMNED@0.445283, KXATPCHALLENGERMATCH-26MAY12HUEVAR@0.438847, KXATPCHALLENGERMATCH-26MAR05HEMGEA@0.434523, KXATPCHALLENGERMATCH-26MAY31SCOHON@0.433257. DAN has anchor 58, neighborhood low ratio 0.8675588326985113, lineage target NONE, pair cap 98, and post-only cap 93. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=NONE; ACTIVE_TARGET_BEFORE_CENTS=NONE.

**PRA.** Formation progress 0.000000 < 1 overrides the computed candidate; lawful action is HOLD_REST@NONE.

> At 0.000000 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXWTACHALLENGERMATCH-26JUN14LEOKUL@0.612638, KXATPMATCH-26JAN08MMOKHA@0.467466, KXATPCHALLENGERMATCH-26MAR05CECKYM@0.450936, KXATPCHALLENGERMATCH-26MAY10LOMNED@0.445283, KXATPCHALLENGERMATCH-26MAY12HUEVAR@0.438847, KXATPCHALLENGERMATCH-26MAR05HEMGEA@0.434523, KXATPCHALLENGERMATCH-26MAY31SCOHON@0.433257. PRA has anchor 41, neighborhood low ratio 0.8132580816047975, lineage target NONE, pair cap 98, and post-only cap 93. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=NONE; ACTIVE_TARGET_BEFORE_CENTS=NONE.

### TP4 — 2.633333 hours from discovery (2026-07-17T22:14:33.998Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

DAN: R-BOOK-DAN#rows-1..22, terminal KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-22 = 11/93 last NONE; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=DAN,ts<=1784326473.999 (0 rows)

PRA: R-BOOK-PRA#rows-1..16, terminal KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-16 = 9/60 last NONE; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=PRA,ts<=1784326473.999 (0 rows)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"DAN":0.6092936564046533,"PRA":0.6092936564046533},"anchors_cents":{"DAN":58,"PRA":41}}` | R-STORY#line-438; raw cumulative prefixes above |
| opening_split | `{"sum_cents":99,"absolute_split_cents":17}` | R-STORY#line-438; raw cumulative prefixes above |
| drift | `{"DAN":{"current_cents":52,"drift_cents":-6},"PRA":{"current_cents":34,"drift_cents":-7}}` | R-STORY#line-438; raw cumulative prefixes above |
| steps_stillness | `{"DAN":{"step_count":5,"last_step_cents":2,"still_seconds":0},"PRA":{"step_count":8,"last_step_cents":-17,"still_seconds":0}}` | R-STORY#line-438; raw cumulative prefixes above |
| shape_survival | `{"DAN":{"directional_step_share":0.4,"observed_steps":5},"PRA":{"directional_step_share":0.5,"observed_steps":8}}` | R-STORY#line-438; raw cumulative prefixes above |
| ripeness | `{"DAN":{"continuous_evidence_mass":0.9565217391304348,"observations":22,"prints":0},"PRA":{"continuous_evidence_mass":0.9444444444444444,"observations":17,"prints":0}}` | R-STORY#line-438; raw cumulative prefixes above |
| lows_travel | `{"DAN":{"low_cents":49,"high_cents":52,"travel_cents":3},"PRA":{"low_cents":34,"high_cents":51,"travel_cents":17}}` | R-STORY#line-438; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":86,"spread_sum_cents":133,"dwell_seconds":{"DAN":0,"PRA":0}}` | R-STORY#line-438; raw cumulative prefixes above |
| divots | `{"DAN":{"count":1,"mean_depth_cents":1,"latest":{"timestamp_epoch":1784317958,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-3","floor_cents":49,"depth_cents":1}},"PRA":{"count":2,"mean_depth_cents":1,"latest":{"timestamp_epoch":1784324849,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-10","floor_cents":50,"depth_cents":1}}}` | R-STORY#line-438; raw cumulative prefixes above |
| depth_size | `{"DAN":{"bid_depth_5":898,"ask_depth_5":1017,"bid_share":0.4689295039164491,"top_bid_size":50,"top_ask_size":127},"PRA":{"bid_depth_5":867,"ask_depth_5":1115,"bid_share":0.4374369323915237,"top_bid_size":22,"top_ask_size":110}}` | R-STORY#line-438; raw cumulative prefixes above |
| volume | `{"DAN":{"print_count":0,"contracts":0},"PRA":{"print_count":0,"contracts":0}}` | R-STORY#line-438; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.0714285714285714,"drift_sum_cents":-13,"both_legs_named":true}` | R-STORY#line-438; raw cumulative prefixes above |
| category | `{"category":"ATP_MAIN"}` | R-STORY#line-438; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":2.6333333333333333,"hours_to_truth_bell":12.940555555555555,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-438; raw cumulative prefixes above |
| books | `{"DAN":{"bid_cents":11,"ask_cents":93,"last_trade_cents":null,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-22"},"PRA":{"bid_cents":9,"ask_cents":60,"last_trade_cents":null,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-16"}}` | R-STORY#line-438; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":0,"legs":{"DAN":{"credited":false,"entry_cents":null,"standing_target_cents":null},"PRA":{"credited":false,"entry_cents":null,"standing_target_cents":null}}}` | R-STORY#line-438; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_MAIN","anchor_split_cents":17,"leg0_anchor_cents":41,"leg1_anchor_cents":58,"leg0_drift_cents":-7,"leg1_drift_cents":-6,"leg0_travel_cents":17,"leg1_travel_cents":3,"joint_mid_sum_cents":86,"joint_spread_cents":133,"inverse_coherence":0.0714285714285714,"volume_log1p":0,"hours_from_discovery":2.6333333333333333,"divot_depth_cents":1,"oriented_leg_ids":["PRA","DAN"]}` [R-STORY#line-438; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26MAY12HUEVAR (26MAY) | 0.531191 / 1.000000 | R-CORPUS#row-5502; RANGE_SPECTRUM_PATH | R-RANGE#row-2434; HUE anchor 38 (tick#56[1778591972,38,84,0]), low 21 (tick#75[1778597698,21,33,38]), close 21 (terminal tick#95[1778603748,16,24,21]); VAR anchor 64 (tick#55[1778591671,12,64,0]), low 64 (tick#55[1778591671,12,64,0]), close 86 (terminal tick#95[1778603748,76,86,86]) |
| N2 | KXATPCHALLENGERMATCH-26JUN16HUEZEI (26JUN) | 0.516745 / 1.000000 | R-CORPUS#row-3498; RANGE_SPECTRUM_PATH | R-RANGE#row-1641; ZEI anchor 47 (tick#33[1781609741,14,47,47]), low 35 (tick#78[1781627215,6,35,35]), close 35 (terminal tick#78[1781627215,6,35,35]); HUE anchor 68 (tick#33[1781609741,14,68,68]), low 65 (tick#74[1781625657,20,65,65]), close 65 (terminal tick#78[1781627215,65,95,65]) |
| N3 | KXATPCHALLENGERMATCH-26MAY14FERALE (26MAY) | 0.456790 / 1.000000 | R-CORPUS#row-5610; RANGE_SPECTRUM_PATH | R-RANGE#row-2539; ALE anchor 17 (tick#17[1778761362,17,93,0]), low 17 (tick#17[1778761362,17,93,0]), close 17 (terminal tick#21[1778762567,13,15,17]); FER anchor 77 (tick#6[1778758026,77,95,0]), low 77 (tick#6[1778758026,77,95,0]), close 84 (terminal tick#21[1778762567,83,84,84]) |
| N4 | KXATPMATCH-26JAN08MMOKHA (26JAN) | 0.447891 / 0.787671 | R-CORPUS#row-6826; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-1953; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N5 | KXWTACHALLENGERMATCH-26JUN14LEOKUL (26JUN) | 0.444003 / 1.000000 | R-CORPUS#row-9693; RANGE_SPECTRUM_PATH | R-RANGE#row-4604; LEO anchor 46 (tick#48[1781416329,5,46,46]), low 46 (tick#48[1781416329,5,46,46]), close 55 (terminal tick#72[1781424913,59,64,55]); KUL anchor 63 (tick#48[1781416329,31,63,63]), low 40 (tick#60[1781420280,38,40,41]), close 40 (terminal tick#72[1781424913,38,40,40]) |
| N6 | KXITFWMATCH-26JUL15TEPJOV (26JUL) | 0.440110 / 1.000000 | R-CORPUS#row-8771; RANGE_SPECTRUM_PATH | R-RANGE#row-6142; TEP anchor 44 (tick#109[1784091299,40,44,]), low 44 (tick#109[1784091299,40,44,]), close 44 (terminal tick#12598[1784118494,39,74,44]); JOV anchor 61 (tick#129[1784093072,56,61,]), low 61 (tick#129[1784093072,56,61,]), close 62 (terminal tick#10082[1784118494,38,62,62]) |
| N7 | KXATPMATCH-26MAY19BOSGAL (26MAY) | 0.434402 / 1.000000 | R-CORPUS#row-8378; RANGE_SPECTRUM_PATH | R-RANGE#row-3955; GAL anchor 42 (tick#1[1779248892,41,42,42]), low 36 (tick#97[1779277896,35,42,36]), close 36 (terminal tick#97[1779277896,35,42,36]); BOS anchor 59 (tick#1[1779248892,58,59,59]), low 57 (tick#22[1779255228,57,58,58]), close 59 (terminal tick#97[1779277896,55,62,59]) |

**Derivation arithmetic → action → verbatim sentence.**

**DAN.** Formation progress 0.609294 < 1 overrides the computed candidate; lawful action is HOLD_REST@NONE.

> At 2.633333 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPCHALLENGERMATCH-26MAY12HUEVAR@0.531191, KXATPCHALLENGERMATCH-26JUN16HUEZEI@0.516745, KXATPCHALLENGERMATCH-26MAY14FERALE@0.456790, KXATPMATCH-26JAN08MMOKHA@0.447891, KXWTACHALLENGERMATCH-26JUN14LEOKUL@0.444003, KXITFWMATCH-26JUL15TEPJOV@0.440110, KXATPMATCH-26MAY19BOSGAL@0.434402. DAN has anchor 58, neighborhood low ratio 0.9308902449388774, lineage target NONE, pair cap 98, and post-only cap 92. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=NONE; ACTIVE_TARGET_BEFORE_CENTS=NONE.

**PRA.** Formation progress 0.609294 < 1 overrides the computed candidate; lawful action is HOLD_REST@NONE.

> At 2.633333 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPCHALLENGERMATCH-26MAY12HUEVAR@0.531191, KXATPCHALLENGERMATCH-26JUN16HUEZEI@0.516745, KXATPCHALLENGERMATCH-26MAY14FERALE@0.456790, KXATPMATCH-26JAN08MMOKHA@0.447891, KXWTACHALLENGERMATCH-26JUN14LEOKUL@0.444003, KXITFWMATCH-26JUL15TEPJOV@0.440110, KXATPMATCH-26MAY19BOSGAL@0.434402. PRA has anchor 41, neighborhood low ratio 0.8296247789404916, lineage target NONE, pair cap 98, and post-only cap 59. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=NONE; ACTIVE_TARGET_BEFORE_CENTS=NONE.

### TP6 — 3.102778 hours from discovery (2026-07-17T22:42:44.000Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

DAN: R-BOOK-DAN#rows-1..32, terminal KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-32 = 11/93 last NONE; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=DAN,ts<=1784328164.001 (0 rows)

PRA: R-BOOK-PRA#rows-1..25, terminal KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-25 = 9/60 last 60; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=PRA,ts<=1784328164.001 (0 rows)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"DAN":0.7179124622405039,"PRA":0.7179124622405039},"anchors_cents":{"DAN":58,"PRA":41}}` | R-STORY#line-450; raw cumulative prefixes above |
| opening_split | `{"sum_cents":99,"absolute_split_cents":17}` | R-STORY#line-450; raw cumulative prefixes above |
| drift | `{"DAN":{"current_cents":52,"drift_cents":-6},"PRA":{"current_cents":60,"drift_cents":19}}` | R-STORY#line-450; raw cumulative prefixes above |
| steps_stillness | `{"DAN":{"step_count":11,"last_step_cents":1,"still_seconds":0},"PRA":{"step_count":9,"last_step_cents":26,"still_seconds":0}}` | R-STORY#line-450; raw cumulative prefixes above |
| shape_survival | `{"DAN":{"directional_step_share":0.45454545454545453,"observed_steps":11},"PRA":{"directional_step_share":0.5555555555555556,"observed_steps":9}}` | R-STORY#line-450; raw cumulative prefixes above |
| ripeness | `{"DAN":{"continuous_evidence_mass":0.9696969696969697,"observations":32,"prints":0},"PRA":{"continuous_evidence_mass":0.9615384615384616,"observations":25,"prints":0}}` | R-STORY#line-450; raw cumulative prefixes above |
| lows_travel | `{"DAN":{"low_cents":49,"high_cents":52,"travel_cents":3},"PRA":{"low_cents":34,"high_cents":60,"travel_cents":26}}` | R-STORY#line-450; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":112,"spread_sum_cents":133,"dwell_seconds":{"DAN":0,"PRA":0}}` | R-STORY#line-450; raw cumulative prefixes above |
| divots | `{"DAN":{"count":3,"mean_depth_cents":1,"latest":{"timestamp_epoch":1784328140,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-31","floor_cents":51,"depth_cents":1}},"PRA":{"count":2,"mean_depth_cents":1,"latest":{"timestamp_epoch":1784324849,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-10","floor_cents":50,"depth_cents":1}}}` | R-STORY#line-450; raw cumulative prefixes above |
| depth_size | `{"DAN":{"bid_depth_5":302,"ask_depth_5":1017,"bid_share":0.22896133434420016,"top_bid_size":50,"top_ask_size":127},"PRA":{"bid_depth_5":867,"ask_depth_5":110,"bid_share":0.887410440122825,"top_bid_size":22,"top_ask_size":105}}` | R-STORY#line-450; raw cumulative prefixes above |
| volume | `{"DAN":{"print_count":0,"contracts":0},"PRA":{"print_count":0,"contracts":0}}` | R-STORY#line-450; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.5,"drift_sum_cents":13,"both_legs_named":true}` | R-STORY#line-450; raw cumulative prefixes above |
| category | `{"category":"ATP_MAIN"}` | R-STORY#line-450; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":3.102777777777778,"hours_to_truth_bell":12.471111111111112,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-450; raw cumulative prefixes above |
| books | `{"DAN":{"bid_cents":11,"ask_cents":93,"last_trade_cents":null,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-32"},"PRA":{"bid_cents":9,"ask_cents":60,"last_trade_cents":60,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-25"}}` | R-STORY#line-450; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":0,"legs":{"DAN":{"credited":false,"entry_cents":null,"standing_target_cents":null},"PRA":{"credited":false,"entry_cents":null,"standing_target_cents":null}}}` | R-STORY#line-450; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_MAIN","anchor_split_cents":17,"leg0_anchor_cents":41,"leg1_anchor_cents":58,"leg0_drift_cents":19,"leg1_drift_cents":-6,"leg0_travel_cents":26,"leg1_travel_cents":3,"joint_mid_sum_cents":112,"joint_spread_cents":133,"inverse_coherence":0.5,"volume_log1p":0,"hours_from_discovery":3.102777777777778,"divot_depth_cents":1,"oriented_leg_ids":["PRA","DAN"]}` [R-STORY#line-450; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26JUN16HUEZEI (26JUN) | 0.578981 / 1.000000 | R-CORPUS#row-3498; RANGE_SPECTRUM_PATH | R-RANGE#row-1641; ZEI anchor 47 (tick#33[1781609741,14,47,47]), low 35 (tick#78[1781627215,6,35,35]), close 35 (terminal tick#78[1781627215,6,35,35]); HUE anchor 68 (tick#33[1781609741,14,68,68]), low 65 (tick#74[1781625657,20,65,65]), close 65 (terminal tick#78[1781627215,65,95,65]) |
| N2 | KXATPCHALLENGERMATCH-26JUN15HUEKOH (26JUN) | 0.556347 / 1.000000 | R-CORPUS#row-3446; RANGE_SPECTRUM_PATH | R-RANGE#row-1590; HUE anchor 54 (tick#38[1781525153,20,23,54]), low 23 (tick#38[1781525153,20,23,54]), close 74 (terminal tick#80[1781541178,76,95,74]); KOH anchor 66 (tick#31[1781522687,66,91,0]), low 50 (tick#43[1781526707,6,76,50]), close 50 (terminal tick#80[1781541178,7,29,50]) |
| N3 | KXWTACHALLENGERMATCH-26JUN14LEOKUL (26JUN) | 0.550659 / 1.000000 | R-CORPUS#row-9693; RANGE_SPECTRUM_PATH | R-RANGE#row-4604; LEO anchor 46 (tick#48[1781416329,5,46,46]), low 46 (tick#48[1781416329,5,46,46]), close 55 (terminal tick#72[1781424913,59,64,55]); KUL anchor 63 (tick#48[1781416329,31,63,63]), low 40 (tick#60[1781420280,38,40,41]), close 40 (terminal tick#72[1781424913,38,40,40]) |
| N4 | KXWTAMATCH-26JUN15BONNAV (26JUN) | 0.520688 / 1.000000 | R-CORPUS#row-11412; RANGE_SPECTRUM_PATH | R-RANGE#row-5244; BON anchor 49 (tick#2[1781519534,20,49,49]), low 19 (tick#4[1781520469,19,49,20]), close 58 (terminal tick#14[1781524549,47,59,58]); NAV anchor 65 (tick#2[1781519534,20,65,65]), low 53 (tick#14[1781524549,46,53,53]), close 53 (terminal tick#14[1781524549,46,53,53]) |
| N5 | KXATPMATCH-26JUN06VISYME (26JUN) | 0.517357 / 1.000000 | R-CORPUS#row-7374; RANGE_SPECTRUM_PATH | R-RANGE#row-3339; VIS anchor 14 (tick#3[1780743085,2,49,14]), low 3 (tick#4[1780743386,3,56,3]), close 32 (terminal tick#5[1780743706,8,21,32]); YME anchor 93 (tick#1[1780742483,86,94,93]), low 93 (tick#1[1780742483,86,94,93]), close 97 (terminal tick#5[1780743706,35,96,97]) |
| N6 | KXATPCHALLENGERMATCH-26MAY12HUEVAR (26MAY) | 0.509914 / 1.000000 | R-CORPUS#row-5502; RANGE_SPECTRUM_PATH | R-RANGE#row-2434; HUE anchor 38 (tick#56[1778591972,38,84,0]), low 21 (tick#75[1778597698,21,33,38]), close 21 (terminal tick#95[1778603748,16,24,21]); VAR anchor 64 (tick#55[1778591671,12,64,0]), low 64 (tick#55[1778591671,12,64,0]), close 86 (terminal tick#95[1778603748,76,86,86]) |
| N7 | KXATPCHALLENGERMATCH-26JUN01STRMOE (26JUN) | 0.493549 / 1.000000 | R-CORPUS#row-2906; RANGE_SPECTRUM_PATH | R-RANGE#row-1055; MOE anchor 41 (tick#38[1780321222,23,41,41]), low 37 (tick#51[1780325176,37,43,43]), close 44 (terminal tick#54[1780326103,43,44,44]); STR anchor 70 (tick#38[1780321222,67,90,70]), low 54 (tick#49[1780324561,54,55,55]), close 59 (terminal tick#54[1780326103,55,57,59]) |

**Derivation arithmetic → action → verbatim sentence.**

**DAN.** Formation progress 0.717912 < 1 overrides the computed candidate; lawful action is HOLD_REST@NONE.

> At 3.102778 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPCHALLENGERMATCH-26JUN16HUEZEI@0.578981, KXATPCHALLENGERMATCH-26JUN15HUEKOH@0.556347, KXWTACHALLENGERMATCH-26JUN14LEOKUL@0.550659, KXWTAMATCH-26JUN15BONNAV@0.520688, KXATPMATCH-26JUN06VISYME@0.517357, KXATPCHALLENGERMATCH-26MAY12HUEVAR@0.509914, KXATPCHALLENGERMATCH-26JUN01STRMOE@0.493549. DAN has anchor 58, neighborhood low ratio 0.8469782709223677, lineage target NONE, pair cap 98, and post-only cap 92. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=NONE; ACTIVE_TARGET_BEFORE_CENTS=NONE.

**PRA.** Formation progress 0.717912 < 1 overrides the computed candidate; lawful action is HOLD_REST@NONE.

> At 3.102778 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPCHALLENGERMATCH-26JUN16HUEZEI@0.578981, KXATPCHALLENGERMATCH-26JUN15HUEKOH@0.556347, KXWTACHALLENGERMATCH-26JUN14LEOKUL@0.550659, KXWTAMATCH-26JUN15BONNAV@0.520688, KXATPMATCH-26JUN06VISYME@0.517357, KXATPCHALLENGERMATCH-26MAY12HUEVAR@0.509914, KXATPCHALLENGERMATCH-26JUN01STRMOE@0.493549. PRA has anchor 41, neighborhood low ratio 0.6059651114167297, lineage target NONE, pair cap 98, and post-only cap 59. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=NONE; ACTIVE_TARGET_BEFORE_CENTS=NONE.

### TP11 — 4.321944 hours from discovery (2026-07-17T23:55:52.998Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

DAN: R-BOOK-DAN#rows-1..353, terminal KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-353 = 53/63 last NONE; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=DAN,ts<=1784332552.998 (0 rows)

PRA: R-BOOK-PRA#rows-1..466, terminal KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-466 = 37/45 last 60; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=PRA,ts<=1784332552.998 (2 rows; last #row-39159 cc203d88-9760-6653-0ded-e44b0613d406@60)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"DAN":1,"PRA":1},"anchors_cents":{"DAN":58,"PRA":41}}` | R-STORY#line-480; raw cumulative prefixes above |
| opening_split | `{"sum_cents":99,"absolute_split_cents":17}` | R-STORY#line-480; raw cumulative prefixes above |
| drift | `{"DAN":{"current_cents":58,"drift_cents":0},"PRA":{"current_cents":60,"drift_cents":19}}` | R-STORY#line-480; raw cumulative prefixes above |
| steps_stillness | `{"DAN":{"step_count":107,"last_step_cents":-1,"still_seconds":131},"PRA":{"step_count":9,"last_step_cents":26,"still_seconds":4389}}` | R-STORY#line-480; raw cumulative prefixes above |
| shape_survival | `{"DAN":{"directional_step_share":0,"observed_steps":107},"PRA":{"directional_step_share":0.5555555555555556,"observed_steps":9}}` | R-STORY#line-480; raw cumulative prefixes above |
| ripeness | `{"DAN":{"continuous_evidence_mass":0.9971751412429378,"observations":353,"prints":0},"PRA":{"continuous_evidence_mass":0.997867803837953,"observations":468,"prints":2}}` | R-STORY#line-480; raw cumulative prefixes above |
| lows_travel | `{"DAN":{"low_cents":49,"high_cents":71,"travel_cents":22},"PRA":{"low_cents":34,"high_cents":60,"travel_cents":26}}` | R-STORY#line-480; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":118,"spread_sum_cents":18,"dwell_seconds":{"DAN":131,"PRA":4389}}` | R-STORY#line-480; raw cumulative prefixes above |
| divots | `{"DAN":{"count":15,"mean_depth_cents":1,"latest":{"timestamp_epoch":1784331718,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-287","floor_cents":58,"depth_cents":1}},"PRA":{"count":2,"mean_depth_cents":1,"latest":{"timestamp_epoch":1784324849,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-10","floor_cents":50,"depth_cents":1}}}` | R-STORY#line-480; raw cumulative prefixes above |
| depth_size | `{"DAN":{"bid_depth_5":2196,"ask_depth_5":2999,"bid_share":0.42271414821944175,"top_bid_size":607,"top_ask_size":607},"PRA":{"bid_depth_5":2770,"ask_depth_5":2996,"bid_share":0.4804023586541797,"top_bid_size":500,"top_ask_size":107}}` | R-STORY#line-480; raw cumulative prefixes above |
| volume | `{"DAN":{"print_count":0,"contracts":0},"PRA":{"print_count":2,"contracts":9.86}}` | R-STORY#line-480; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.050000000000000044,"drift_sum_cents":19,"both_legs_named":true}` | R-STORY#line-480; raw cumulative prefixes above |
| category | `{"category":"ATP_MAIN"}` | R-STORY#line-480; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":4.321944444444444,"hours_to_truth_bell":11.251944444444444,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-480; raw cumulative prefixes above |
| books | `{"DAN":{"bid_cents":53,"ask_cents":63,"last_trade_cents":null,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-353"},"PRA":{"bid_cents":37,"ask_cents":45,"last_trade_cents":60,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-466"}}` | R-STORY#line-480; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":0,"legs":{"DAN":{"credited":false,"entry_cents":null,"standing_target_cents":null},"PRA":{"credited":false,"entry_cents":null,"standing_target_cents":null}}}` | R-STORY#line-480; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_MAIN","anchor_split_cents":17,"leg0_anchor_cents":41,"leg1_anchor_cents":58,"leg0_drift_cents":19,"leg1_drift_cents":0,"leg0_travel_cents":26,"leg1_travel_cents":22,"joint_mid_sum_cents":118,"joint_spread_cents":18,"inverse_coherence":0.050000000000000044,"volume_log1p":2.3850863145057892,"hours_from_discovery":4.321944444444444,"divot_depth_cents":1,"oriented_leg_ids":["PRA","DAN"]}` [R-STORY#line-480; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26JUN07ZEBMAR (26JUN) | 0.698506 / 1.000000 | R-CORPUS#row-3134; RANGE_SPECTRUM_PATH | R-RANGE#row-1283; ZEB anchor 44 (tick#6[1780835226,36,44,0]), low 37 (tick#40[1780846176,37,44,44]), close 60 (terminal tick#91[1780862311,20,59,60]); MAR anchor 63 (tick#26[1780841928,56,63,0]), low 62 (tick#40[1780846176,56,62,63]), close 80 (terminal tick#91[1780862311,40,85,80]) |
| N2 | KXITFMATCH-26JUL16DARJON (26JUL) | 0.674783 / 1.000000 | R-CORPUS#row-8632; RANGE_SPECTRUM_PATH | R-RANGE#row-6017; JON anchor 46 (tick#95[1784166500,41,46,]), low 46 (tick#95[1784166500,41,46,]), close 68 (terminal tick#1333[1784195154,41,61,68]); DAR anchor 61 (tick#1[1784166457,60,61,61]), low 58 (tick#679[1784170836,53,58,60]), close 58 (terminal tick#2557[1784195159,37,57,58]) |
| N3 | KXWTAMATCH-26JUN13MONTOM (26JUN) | 0.670199 / 1.000000 | R-CORPUS#row-11381; RANGE_SPECTRUM_PATH | R-RANGE#row-5214; TOM anchor 49 (tick#3[1781344542,17,49,49]), low 48 (tick#20[1781349669,48,52,64]), close 51 (terminal tick#31[1781353652,48,50,51]); MON anchor 68 (tick#3[1781344542,36,68,68]), low 50 (tick#31[1781353652,50,52,50]), close 50 (terminal tick#31[1781353652,50,52,50]) |
| N4 | KXWTACHALLENGERMATCH-26JUN02ZIDAVA (26JUN) | 0.667072 / 1.000000 | R-CORPUS#row-9549; RANGE_SPECTRUM_PATH | R-RANGE#row-4477; ZID anchor 46 (tick#4[1780422477,33,46,46]), low 39 (tick#7[1780423687,38,40,39]), close 48 (terminal tick#8[1780423988,52,55,48]); AVA anchor 65 (tick#4[1780422477,54,67,65]), low 51 (tick#5[1780422779,40,47,51]), close 52 (terminal tick#8[1780423988,45,49,52]) |
| N5 | KXATPMATCH-26MAY19BLASKA (26MAY) | 0.666282 / 1.000000 | R-CORPUS#row-8377; RANGE_SPECTRUM_PATH | R-RANGE#row-3954; SKA anchor 50 (tick#43[1779200400,50,77,50]), low 33 (tick#85[1779213999,33,46,45]), close 40 (terminal tick#92[1779216118,34,36,40]); BLA anchor 62 (tick#44[1779200704,21,65,62]), low 47 (tick#34[1779197666,47,93,0]), close 63 (terminal tick#92[1779216118,64,65,63]) |
| N6 | KXATPMATCH-26APR22BASOFN (26APR) | 0.663246 / 1.000000 | R-CORPUS#row-6249; RANGE_SPECTRUM_PATH | R-RANGE#row-3045; BAS anchor 41 (tick#1[1776835840,37,40,41]), low 34 (tick#102[1776866502,31,35,34]), close 37 (terminal tick#104[1776867105,37,38,37]); OFN anchor 66 (tick#1[1776835840,61,66,66]), low 50 (tick#99[1776865580,47,51,50]), close 64 (terminal tick#104[1776867105,63,64,64]) |
| N7 | KXATPMATCH-26JUN06WONMCC (26JUN) | 0.661187 / 1.000000 | R-CORPUS#row-7375; RANGE_SPECTRUM_PATH | R-RANGE#row-3340; MCC anchor 47 (tick#8[1780723469,37,54,47]), low 42 (tick#49[1780735849,40,42,43]), close 43 (terminal tick#99[1780750958,43,44,43]); WON anchor 59 (tick#11[1780724372,53,59,59]), low 57 (tick#19[1780726781,57,61,59]), close 57 (terminal tick#99[1780750958,56,57,57]) |

**Derivation arithmetic → action → verbatim sentence.**

**DAN.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN07ZEBMAR:(0.698506×1.000000)×(62/63) + KXITFMATCH-26JUL16DARJON:(0.674783×1.000000)×(58/61) + KXWTAMATCH-26JUN13MONTOM:(0.670199×1.000000)×(50/68) + KXWTACHALLENGERMATCH-26JUN02ZIDAVA:(0.667072×1.000000)×(51/65) + KXATPMATCH-26MAY19BLASKA:(0.666282×1.000000)×(47/62) + KXATPMATCH-26APR22BASOFN:(0.663246×1.000000)×(50/66) + KXATPMATCH-26JUN06WONMCC:(0.661187×1.000000)×(57/59)) / 4.701275 = 0.849029596061. Raw round(58×0.849029596061)=49; mass=0.671610782751; blend with lineage NONE gives 49; min(pair cap 98, post-only cap 62) gives 49. Printed action PLACE_REST@49, active-before NONE.

> At 4.321944 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPCHALLENGERMATCH-26JUN07ZEBMAR@0.698506, KXITFMATCH-26JUL16DARJON@0.674783, KXWTAMATCH-26JUN13MONTOM@0.670199, KXWTACHALLENGERMATCH-26JUN02ZIDAVA@0.667072, KXATPMATCH-26MAY19BLASKA@0.666282, KXATPMATCH-26APR22BASOFN@0.663246, KXATPMATCH-26JUN06WONMCC@0.661187. DAN has anchor 58, neighborhood low ratio 0.8490295960608119, lineage target NONE, pair cap 98, and post-only cap 62. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=49; ACTIVE_TARGET_BEFORE_CENTS=NONE.

**PRA.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN07ZEBMAR:(0.698506×1.000000)×(37/44) + KXITFMATCH-26JUL16DARJON:(0.674783×1.000000)×(46/46) + KXWTAMATCH-26JUN13MONTOM:(0.670199×1.000000)×(48/49) + KXWTACHALLENGERMATCH-26JUN02ZIDAVA:(0.667072×1.000000)×(39/46) + KXATPMATCH-26MAY19BLASKA:(0.666282×1.000000)×(33/50) + KXATPMATCH-26APR22BASOFN:(0.663246×1.000000)×(34/41) + KXATPMATCH-26JUN06WONMCC:(0.661187×1.000000)×(42/47)) / 4.701275 = 0.864626820625. Raw round(41×0.864626820625)=35; mass=0.671610782751; blend with lineage 37 gives 36; min(pair cap 98, post-only cap 44) gives 36. Printed action PLACE_REST@36, active-before NONE.

> At 4.321944 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPCHALLENGERMATCH-26JUN07ZEBMAR@0.698506, KXITFMATCH-26JUL16DARJON@0.674783, KXWTAMATCH-26JUN13MONTOM@0.670199, KXWTACHALLENGERMATCH-26JUN02ZIDAVA@0.667072, KXATPMATCH-26MAY19BLASKA@0.666282, KXATPMATCH-26APR22BASOFN@0.663246, KXATPMATCH-26JUN06WONMCC@0.661187. PRA has anchor 41, neighborhood low ratio 0.8646268206251957, lineage target 37, pair cap 98, and post-only cap 44. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=36; ACTIVE_TARGET_BEFORE_CENTS=NONE.

### TP12 — 5.546949 hours from discovery (2026-07-18T01:09:23.016Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

DAN: R-BOOK-DAN#rows-1..1468, terminal KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-1468 = 58/59 last NONE; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=DAN,ts<=1784336963.016 (0 rows)

PRA: R-BOOK-PRA#rows-1..1218, terminal KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-1218 = 42/43 last 60; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=PRA,ts<=1784336963.016 (3 rows; last #row-39160 5c3e4f2c-cb1c-7a8a-c61c-2f6597821fb9@43)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"DAN":1,"PRA":1},"anchors_cents":{"DAN":58,"PRA":41}}` | R-STORY#line-486; raw cumulative prefixes above |
| opening_split | `{"sum_cents":99,"absolute_split_cents":17}` | R-STORY#line-486; raw cumulative prefixes above |
| drift | `{"DAN":{"current_cents":58,"drift_cents":0},"PRA":{"current_cents":43,"drift_cents":2}}` | R-STORY#line-486; raw cumulative prefixes above |
| steps_stillness | `{"DAN":{"step_count":143,"last_step_cents":1,"still_seconds":2447.0169999599457},"PRA":{"step_count":10,"last_step_cents":-17,"still_seconds":0}}` | R-STORY#line-486; raw cumulative prefixes above |
| shape_survival | `{"DAN":{"directional_step_share":0,"observed_steps":143},"PRA":{"directional_step_share":0.5,"observed_steps":10}}` | R-STORY#line-486; raw cumulative prefixes above |
| ripeness | `{"DAN":{"continuous_evidence_mass":0.9993192648059904,"observations":1468,"prints":0},"PRA":{"continuous_evidence_mass":0.9991823385118561,"observations":1222,"prints":3}}` | R-STORY#line-486; raw cumulative prefixes above |
| lows_travel | `{"DAN":{"low_cents":49,"high_cents":71,"travel_cents":22},"PRA":{"low_cents":34,"high_cents":60,"travel_cents":26}}` | R-STORY#line-486; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":101,"spread_sum_cents":2,"dwell_seconds":{"DAN":2447.0169999599457,"PRA":0}}` | R-STORY#line-486; raw cumulative prefixes above |
| divots | `{"DAN":{"count":20,"mean_depth_cents":1,"latest":{"timestamp_epoch":1784332593,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-411","floor_cents":57,"depth_cents":1}},"PRA":{"count":2,"mean_depth_cents":1,"latest":{"timestamp_epoch":1784324849,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-10","floor_cents":50,"depth_cents":1}}}` | R-STORY#line-486; raw cumulative prefixes above |
| depth_size | `{"DAN":{"bid_depth_5":8931,"ask_depth_5":24188,"bid_share":0.2696639391285969,"top_bid_size":50,"top_ask_size":2000},"PRA":{"bid_depth_5":9047,"ask_depth_5":20131,"bid_share":0.31006237576256085,"top_bid_size":5,"top_ask_size":6094}}` | R-STORY#line-486; raw cumulative prefixes above |
| volume | `{"DAN":{"print_count":0,"contracts":0},"PRA":{"print_count":3,"contracts":10.16}}` | R-STORY#line-486; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.33333333333333337,"drift_sum_cents":2,"both_legs_named":true}` | R-STORY#line-486; raw cumulative prefixes above |
| category | `{"category":"ATP_MAIN"}` | R-STORY#line-486; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":5.546949166655541,"hours_to_truth_bell":10.02693972223335,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-486; raw cumulative prefixes above |
| books | `{"DAN":{"bid_cents":58,"ask_cents":59,"last_trade_cents":null,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-1468"},"PRA":{"bid_cents":42,"ask_cents":43,"last_trade_cents":60,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-1218"}}` | R-STORY#line-486; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":2,"legs":{"DAN":{"credited":false,"entry_cents":null,"standing_target_cents":49},"PRA":{"credited":false,"entry_cents":null,"standing_target_cents":36}}}` | R-STORY#line-486; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_MAIN","anchor_split_cents":17,"leg0_anchor_cents":41,"leg1_anchor_cents":58,"leg0_drift_cents":2,"leg1_drift_cents":0,"leg0_travel_cents":26,"leg1_travel_cents":22,"joint_mid_sum_cents":101,"joint_spread_cents":2,"inverse_coherence":0.33333333333333337,"volume_log1p":2.412335956953165,"hours_from_discovery":5.546949166655541,"divot_depth_cents":1,"oriented_leg_ids":["PRA","DAN"]}` [R-STORY#line-486; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPMATCH-26MAY18SMIGUI (26MAY) | 0.892864 / 1.000000 | R-CORPUS#row-8368; RANGE_SPECTRUM_PATH | R-RANGE#row-3945; GUI anchor 40 (tick#1[1779154299,39,40,40]), low 32 (tick#100[1779184652,29,36,32]), close 40 (terminal tick#103[1779185556,39,40,40]); SMI anchor 61 (tick#1[1779154299,60,61,61]), low 47 (tick#101[1779184954,45,48,47]), close 58 (terminal tick#103[1779185556,60,61,58]) |
| N2 | KXATPMATCH-26JUN22BROHOL (26JUN) | 0.877056 / 1.000000 | R-CORPUS#row-7564; RANGE_SPECTRUM_PATH | R-RANGE#row-3499; BRO anchor 44 (tick#1[1782108138,43,44,44]), low 44 (tick#1[1782108138,43,44,44]), close 44 (terminal tick#106[1782139943,38,46,44]); HOL anchor 56 (tick#1[1782108138,55,56,56]), low 42 (tick#99[1782137758,38,42,44]), close 58 (terminal tick#106[1782139943,56,61,58]) |
| N3 | KXATPMATCH-26MAY05KYPDRO (26MAY) | 0.874047 / 1.000000 | R-CORPUS#row-8155; RANGE_SPECTRUM_PATH | R-RANGE#row-3739; KYP anchor 38 (tick#1[1777948358,37,38,38]), low 26 (tick#108[1777980655,24,27,26]), close 38 (terminal tick#110[1777981258,38,39,38]); DRO anchor 62 (tick#1[1777948358,62,63,63]), low 55 (tick#103[1777979149,54,55,55]), close 65 (terminal tick#110[1777981258,61,64,65]) |
| N4 | KXATPMATCH-26JUL11NARGUE (26JUL) | 0.872536 / 1.000000 | R-CORPUS#row-7224; RANGE_SPECTRUM_PATH | R-RANGE#row-3199; GUE anchor 42 (tick#1[1783753495,39,41,42]), low 41 (tick#1[1783753495,39,41,42]), close 45 (terminal tick#84[1783782416,42,45,45]); NAR anchor 58 (tick#1[1783753495,57,58,58]), low 56 (tick#28[1783762335,55,56,56]), close 58 (terminal tick#84[1783782416,56,57,58]) |
| N5 | KXATPMATCH-26MAY17DUCBUT (26MAY) | 0.867986 / 1.000000 | R-CORPUS#row-8289; RANGE_SPECTRUM_PATH | R-RANGE#row-3866; DUC anchor 42 (tick#1[1778979666,41,42,42]), low 41 (tick#1[1778979666,41,42,42]), close 43 (terminal tick#96[1779008299,41,43,43]); BUT anchor 58 (tick#1[1778979666,57,58,58]), low 58 (tick#1[1778979666,57,58,58]), close 59 (terminal tick#96[1779008299,58,59,59]) |
| N6 | KXATPMATCH-26MAY06GIRCIL (26MAY) | 0.866585 / 1.000000 | R-CORPUS#row-8173; RANGE_SPECTRUM_PATH | R-RANGE#row-3756; GIR anchor 41 (tick#1[1778122753,40,41,41]), low 38 (tick#95[1778151126,38,40,41]), close 41 (terminal tick#101[1778152935,40,41,41]); CIL anchor 60 (tick#1[1778122753,59,60,60]), low 57 (tick#100[1778152632,57,59,57]), close 61 (terminal tick#101[1778152935,59,60,61]) |
| N7 | KXATPMATCH-26MAY18BUEBAX (26MAY) | 0.865427 / 1.000000 | R-CORPUS#row-8312; RANGE_SPECTRUM_PATH | R-RANGE#row-3889; BAX anchor 41 (tick#1[1779089948,41,42,41]), low 41 (tick#1[1779089948,41,42,41]), close 47 (terminal tick#94[1779118345,46,47,47]); BUE anchor 58 (tick#1[1779089948,57,58,58]), low 52 (tick#57[1779106915,52,53,54]), close 57 (terminal tick#94[1779118345,56,57,57]) |

**Derivation arithmetic → action → verbatim sentence.**

**DAN.** Σweighted-ratio / Σweight = (KXATPMATCH-26MAY18SMIGUI:(0.892864×1.000000)×(47/61) + KXATPMATCH-26JUN22BROHOL:(0.877056×1.000000)×(42/56) + KXATPMATCH-26MAY05KYPDRO:(0.874047×1.000000)×(55/62) + KXATPMATCH-26JUL11NARGUE:(0.872536×1.000000)×(56/58) + KXATPMATCH-26MAY17DUCBUT:(0.867986×1.000000)×(58/58) + KXATPMATCH-26MAY06GIRCIL:(0.866585×1.000000)×(57/60) + KXATPMATCH-26MAY18BUEBAX:(0.865427×1.000000)×(52/58)) / 6.116502 = 0.887875435759. Raw round(58×0.887875435759)=51; mass=0.873785982586; blend with lineage NONE gives 51; min(pair cap 63, post-only cap 58) gives 51. Printed action REPRICE_REST@51, active-before 49.

> At 5.546949 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPMATCH-26MAY18SMIGUI@0.892864, KXATPMATCH-26JUN22BROHOL@0.877056, KXATPMATCH-26MAY05KYPDRO@0.874047, KXATPMATCH-26JUL11NARGUE@0.872536, KXATPMATCH-26MAY17DUCBUT@0.867986, KXATPMATCH-26MAY06GIRCIL@0.866585, KXATPMATCH-26MAY18BUEBAX@0.865427. DAN has anchor 58, neighborhood low ratio 0.8878754357587486, lineage target NONE, pair cap 63, and post-only cap 58. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=51; ACTIVE_TARGET_BEFORE_CENTS=49.

**PRA.** Σweighted-ratio / Σweight = (KXATPMATCH-26MAY18SMIGUI:(0.892864×1.000000)×(32/40) + KXATPMATCH-26JUN22BROHOL:(0.877056×1.000000)×(44/44) + KXATPMATCH-26MAY05KYPDRO:(0.874047×1.000000)×(26/38) + KXATPMATCH-26JUL11NARGUE:(0.872536×1.000000)×(41/42) + KXATPMATCH-26MAY17DUCBUT:(0.867986×1.000000)×(41/42) + KXATPMATCH-26MAY06GIRCIL:(0.866585×1.000000)×(38/41) + KXATPMATCH-26MAY18BUEBAX:(0.865427×1.000000)×(41/41)) / 6.116502 = 0.908536402952. Raw round(41×0.908536402952)=37; mass=0.873785982586; blend with lineage 42 gives 38; min(pair cap 50, post-only cap 42) gives 38. Printed action REPRICE_REST@38, active-before 36.

> At 5.546949 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPMATCH-26MAY18SMIGUI@0.892864, KXATPMATCH-26JUN22BROHOL@0.877056, KXATPMATCH-26MAY05KYPDRO@0.874047, KXATPMATCH-26JUL11NARGUE@0.872536, KXATPMATCH-26MAY17DUCBUT@0.867986, KXATPMATCH-26MAY06GIRCIL@0.866585, KXATPMATCH-26MAY18BUEBAX@0.865427. PRA has anchor 41, neighborhood low ratio 0.9085364029522934, lineage target 42, pair cap 50, and post-only cap 42. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=38; ACTIVE_TARGET_BEFORE_CENTS=36.

### TP15 — 8.999167 hours from discovery (2026-07-18T04:36:31.001Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

DAN: R-BOOK-DAN#rows-1..9797, terminal KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-9797 = 58/60 last 60; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=DAN,ts<=1784349391.001 (6 rows; last #row-39172 d390becc-c334-6f67-14f5-5077b91a9818@60)

PRA: R-BOOK-PRA#rows-1..2641, terminal KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-2641 = 40/41 last 41; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=PRA,ts<=1784349391.001 (10 rows; last #row-39173 cefe72fc-2103-5af5-6c3b-65d73ac6f58c@41)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"DAN":1,"PRA":1},"anchors_cents":{"DAN":58,"PRA":41}}` | R-STORY#line-504; raw cumulative prefixes above |
| opening_split | `{"sum_cents":99,"absolute_split_cents":17}` | R-STORY#line-504; raw cumulative prefixes above |
| drift | `{"DAN":{"current_cents":60,"drift_cents":2},"PRA":{"current_cents":41,"drift_cents":0}}` | R-STORY#line-504; raw cumulative prefixes above |
| steps_stillness | `{"DAN":{"step_count":145,"last_step_cents":1,"still_seconds":2823},"PRA":{"step_count":16,"last_step_cents":-1,"still_seconds":6831}}` | R-STORY#line-504; raw cumulative prefixes above |
| shape_survival | `{"DAN":{"directional_step_share":0.45517241379310347,"observed_steps":145},"PRA":{"directional_step_share":0,"observed_steps":16}}` | R-STORY#line-504; raw cumulative prefixes above |
| ripeness | `{"DAN":{"continuous_evidence_mass":0.9998981151299032,"observations":9814,"prints":6},"PRA":{"continuous_evidence_mass":0.9996229260935143,"observations":2651,"prints":10}}` | R-STORY#line-504; raw cumulative prefixes above |
| lows_travel | `{"DAN":{"low_cents":49,"high_cents":71,"travel_cents":22},"PRA":{"low_cents":34,"high_cents":60,"travel_cents":26}}` | R-STORY#line-504; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":101,"spread_sum_cents":3,"dwell_seconds":{"DAN":2823,"PRA":6831}}` | R-STORY#line-504; raw cumulative prefixes above |
| divots | `{"DAN":{"count":20,"mean_depth_cents":1,"latest":{"timestamp_epoch":1784332593,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-411","floor_cents":57,"depth_cents":1}},"PRA":{"count":2,"mean_depth_cents":1,"latest":{"timestamp_epoch":1784324849,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-10","floor_cents":50,"depth_cents":1}}}` | R-STORY#line-504; raw cumulative prefixes above |
| depth_size | `{"DAN":{"bid_depth_5":10206,"ask_depth_5":30980,"bid_share":0.24780265138639343,"top_bid_size":1543,"top_ask_size":2938},"PRA":{"bid_depth_5":10957,"ask_depth_5":16583,"bid_share":0.3978576615831518,"top_bid_size":1095,"top_ask_size":1424}}` | R-STORY#line-504; raw cumulative prefixes above |
| volume | `{"DAN":{"print_count":6,"contracts":418.62},"PRA":{"print_count":10,"contracts":173.57}}` | R-STORY#line-504; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.33333333333333337,"drift_sum_cents":2,"both_legs_named":true}` | R-STORY#line-504; raw cumulative prefixes above |
| category | `{"category":"ATP_MAIN"}` | R-STORY#line-504; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":8.999166666666667,"hours_to_truth_bell":6.574722222222222,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-504; raw cumulative prefixes above |
| books | `{"DAN":{"bid_cents":58,"ask_cents":60,"last_trade_cents":60,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-9797"},"PRA":{"bid_cents":40,"ask_cents":41,"last_trade_cents":41,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-2641"}}` | R-STORY#line-504; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":2,"legs":{"DAN":{"credited":false,"entry_cents":null,"standing_target_cents":51},"PRA":{"credited":false,"entry_cents":null,"standing_target_cents":35}}}` | R-STORY#line-504; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_MAIN","anchor_split_cents":17,"leg0_anchor_cents":41,"leg1_anchor_cents":58,"leg0_drift_cents":0,"leg1_drift_cents":2,"leg0_travel_cents":26,"leg1_travel_cents":22,"joint_mid_sum_cents":101,"joint_spread_cents":3,"inverse_coherence":0.33333333333333337,"volume_log1p":6.385514752400848,"hours_from_discovery":8.999166666666667,"divot_depth_cents":1,"oriented_leg_ids":["PRA","DAN"]}` [R-STORY#line-504; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPMATCH-26MAY18SMIGUI (26MAY) | 0.901130 / 1.000000 | R-CORPUS#row-8368; RANGE_SPECTRUM_PATH | R-RANGE#row-3945; GUI anchor 40 (tick#1[1779154299,39,40,40]), low 32 (tick#100[1779184652,29,36,32]), close 40 (terminal tick#103[1779185556,39,40,40]); SMI anchor 61 (tick#1[1779154299,60,61,61]), low 47 (tick#101[1779184954,45,48,47]), close 58 (terminal tick#103[1779185556,60,61,58]) |
| N2 | KXATPMATCH-26JUN22BROHOL (26JUN) | 0.900563 / 1.000000 | R-CORPUS#row-7564; RANGE_SPECTRUM_PATH | R-RANGE#row-3499; BRO anchor 44 (tick#1[1782108138,43,44,44]), low 44 (tick#1[1782108138,43,44,44]), close 44 (terminal tick#106[1782139943,38,46,44]); HOL anchor 56 (tick#1[1782108138,55,56,56]), low 42 (tick#99[1782137758,38,42,44]), close 58 (terminal tick#106[1782139943,56,61,58]) |
| N3 | KXATPMATCH-26MAY05KYPDRO (26MAY) | 0.898295 / 1.000000 | R-CORPUS#row-8155; RANGE_SPECTRUM_PATH | R-RANGE#row-3739; KYP anchor 38 (tick#1[1777948358,37,38,38]), low 26 (tick#108[1777980655,24,27,26]), close 38 (terminal tick#110[1777981258,38,39,38]); DRO anchor 62 (tick#1[1777948358,62,63,63]), low 55 (tick#103[1777979149,54,55,55]), close 65 (terminal tick#110[1777981258,61,64,65]) |
| N4 | KXATPMATCH-26MAY18TOMECH (26MAY) | 0.881065 / 1.000000 | R-CORPUS#row-8371; RANGE_SPECTRUM_PATH | R-RANGE#row-3948; TOM anchor 42 (tick#1[1779093595,41,42,42]), low 20 (tick#101[1779124299,20,23,24]), close 39 (terminal tick#105[1779125558,38,39,39]); ECH anchor 59 (tick#1[1779093595,58,59,59]), low 59 (tick#1[1779093595,58,59,59]), close 62 (terminal tick#105[1779125558,61,62,62]) |
| N5 | KXATPMATCH-26MAY06GIRCIL (26MAY) | 0.880759 / 1.000000 | R-CORPUS#row-8173; RANGE_SPECTRUM_PATH | R-RANGE#row-3756; GIR anchor 41 (tick#1[1778122753,40,41,41]), low 38 (tick#95[1778151126,38,40,41]), close 41 (terminal tick#101[1778152935,40,41,41]); CIL anchor 60 (tick#1[1778122753,59,60,60]), low 57 (tick#100[1778152632,57,59,57]), close 61 (terminal tick#101[1778152935,59,60,61]) |
| N6 | KXATPMATCH-26MAY06ARNMUN (26MAY) | 0.874761 / 1.000000 | R-CORPUS#row-8160; RANGE_SPECTRUM_PATH | R-RANGE#row-3744; MUN anchor 44 (tick#1[1778045985,43,44,44]), low 26 (tick#108[1778078300,25,26,26]), close 41 (terminal tick#115[1778080426,41,43,41]); ARN anchor 58 (tick#1[1778045985,57,58,58]), low 46 (tick#111[1778079203,46,47,47]), close 57 (terminal tick#115[1778080426,57,59,57]) |
| N7 | KXATPMATCH-26JUN17TIEAUG (26JUN) | 0.873472 / 1.000000 | R-CORPUS#row-7507; RANGE_SPECTRUM_PATH | R-RANGE#row-3452; TIE anchor 43 (tick#1[1781674880,42,43,43]), low 30 (tick#88[1781706380,31,32,30]), close 39 (terminal tick#91[1781707330,39,40,39]); AUG anchor 59 (tick#1[1781674880,58,59,59]), low 55 (tick#65[1781697698,55,56,56]), close 61 (terminal tick#91[1781707330,60,61,61]) |

**Derivation arithmetic → action → verbatim sentence.**

**DAN.** Σweighted-ratio / Σweight = (KXATPMATCH-26MAY18SMIGUI:(0.901130×1.000000)×(47/61) + KXATPMATCH-26JUN22BROHOL:(0.900563×1.000000)×(42/56) + KXATPMATCH-26MAY05KYPDRO:(0.898295×1.000000)×(55/62) + KXATPMATCH-26MAY18TOMECH:(0.881065×1.000000)×(59/59) + KXATPMATCH-26MAY06GIRCIL:(0.880759×1.000000)×(57/60) + KXATPMATCH-26MAY06ARNMUN:(0.874761×1.000000)×(46/58) + KXATPMATCH-26JUN17TIEAUG:(0.873472×1.000000)×(55/59)) / 6.210046 = 0.868339253408. Raw round(58×0.868339253408)=50; mass=0.887149416711; blend with lineage 58 gives 51; min(pair cap 64, post-only cap 59) gives 51. Printed action HOLD_REST@51, active-before 51.

> At 8.999167 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPMATCH-26MAY18SMIGUI@0.901130, KXATPMATCH-26JUN22BROHOL@0.900563, KXATPMATCH-26MAY05KYPDRO@0.898295, KXATPMATCH-26MAY18TOMECH@0.881065, KXATPMATCH-26MAY06GIRCIL@0.880759, KXATPMATCH-26MAY06ARNMUN@0.874761, KXATPMATCH-26JUN17TIEAUG@0.873472. DAN has anchor 58, neighborhood low ratio 0.868339253408408, lineage target 58, pair cap 64, and post-only cap 59. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=51; ACTIVE_TARGET_BEFORE_CENTS=51.

**PRA.** Σweighted-ratio / Σweight = (KXATPMATCH-26MAY18SMIGUI:(0.901130×1.000000)×(32/40) + KXATPMATCH-26JUN22BROHOL:(0.900563×1.000000)×(44/44) + KXATPMATCH-26MAY05KYPDRO:(0.898295×1.000000)×(26/38) + KXATPMATCH-26MAY18TOMECH:(0.881065×1.000000)×(20/42) + KXATPMATCH-26MAY06GIRCIL:(0.880759×1.000000)×(38/41) + KXATPMATCH-26MAY06ARNMUN:(0.874761×1.000000)×(26/44) + KXATPMATCH-26JUN17TIEAUG:(0.873472×1.000000)×(30/43)) / 6.210046 = 0.740455334731. Raw round(41×0.740455334731)=30; mass=0.887149416711; blend with lineage 40 gives 31; min(pair cap 48, post-only cap 40) gives 31. Printed action REPRICE_REST@31, active-before 35.

> At 8.999167 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPMATCH-26MAY18SMIGUI@0.901130, KXATPMATCH-26JUN22BROHOL@0.900563, KXATPMATCH-26MAY05KYPDRO@0.898295, KXATPMATCH-26MAY18TOMECH@0.881065, KXATPMATCH-26MAY06GIRCIL@0.880759, KXATPMATCH-26MAY06ARNMUN@0.874761, KXATPMATCH-26JUN17TIEAUG@0.873472. PRA has anchor 41, neighborhood low ratio 0.7404553347306683, lineage target 40, pair cap 48, and post-only cap 40. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=31; ACTIVE_TARGET_BEFORE_CENTS=35.

### TP18 — 15.572778 hours from discovery (2026-07-18T11:10:56.000Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

DAN: R-BOOK-DAN#rows-1..11561, terminal KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-11561 = 58/61 last 62; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=DAN,ts<=1784373056.001 (37 rows; last #row-39216 7728af84-d245-5ebc-ebbb-f41f19a003f2@62)

PRA: R-BOOK-PRA#rows-1..3803, terminal KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-3803 = 39/42 last 41; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=PRA,ts<=1784373056.001 (22 rows; last #row-39209 ec74ef83-2b94-6f08-a334-f4ad2697ac48@41)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"DAN":1,"PRA":1},"anchors_cents":{"DAN":58,"PRA":41}}` | R-STORY#line-522; raw cumulative prefixes above |
| opening_split | `{"sum_cents":99,"absolute_split_cents":17}` | R-STORY#line-522; raw cumulative prefixes above |
| drift | `{"DAN":{"current_cents":62,"drift_cents":4},"PRA":{"current_cents":41,"drift_cents":0}}` | R-STORY#line-522; raw cumulative prefixes above |
| steps_stillness | `{"DAN":{"step_count":152,"last_step_cents":2,"still_seconds":587},"PRA":{"step_count":22,"last_step_cents":-1,"still_seconds":3806.713000059128}}` | R-STORY#line-522; raw cumulative prefixes above |
| shape_survival | `{"DAN":{"directional_step_share":0.4605263157894737,"observed_steps":152},"PRA":{"directional_step_share":0,"observed_steps":22}}` | R-STORY#line-522; raw cumulative prefixes above |
| ripeness | `{"DAN":{"continuous_evidence_mass":0.9999137856711785,"observations":11598,"prints":37},"PRA":{"continuous_evidence_mass":0.9997387669801463,"observations":3827,"prints":22}}` | R-STORY#line-522; raw cumulative prefixes above |
| lows_travel | `{"DAN":{"low_cents":49,"high_cents":71,"travel_cents":22},"PRA":{"low_cents":34,"high_cents":60,"travel_cents":26}}` | R-STORY#line-522; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":103,"spread_sum_cents":6,"dwell_seconds":{"DAN":587,"PRA":3806.713000059128}}` | R-STORY#line-522; raw cumulative prefixes above |
| divots | `{"DAN":{"count":21,"mean_depth_cents":1.0476190476190477,"latest":{"timestamp_epoch":1784372462,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-11386","floor_cents":60,"depth_cents":2}},"PRA":{"count":2,"mean_depth_cents":1,"latest":{"timestamp_epoch":1784324849,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-10","floor_cents":50,"depth_cents":1}}}` | R-STORY#line-522; raw cumulative prefixes above |
| depth_size | `{"DAN":{"bid_depth_5":13801,"ask_depth_5":13465,"bid_share":0.5061615198415609,"top_bid_size":624,"top_ask_size":2},"PRA":{"bid_depth_5":14194,"ask_depth_5":19890,"bid_share":0.4164417321910574,"top_bid_size":2,"top_ask_size":536}}` | R-STORY#line-522; raw cumulative prefixes above |
| volume | `{"DAN":{"print_count":37,"contracts":3322.08},"PRA":{"print_count":22,"contracts":612.06}}` | R-STORY#line-522; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.19999999999999996,"drift_sum_cents":4,"both_legs_named":true}` | R-STORY#line-522; raw cumulative prefixes above |
| category | `{"category":"ATP_MAIN"}` | R-STORY#line-522; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":15.572777777777778,"hours_to_truth_bell":0.0011111111111111111,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-522; raw cumulative prefixes above |
| books | `{"DAN":{"bid_cents":58,"ask_cents":61,"last_trade_cents":62,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-11561"},"PRA":{"bid_cents":39,"ask_cents":42,"last_trade_cents":41,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-3803"}}` | R-STORY#line-522; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":2,"legs":{"DAN":{"credited":false,"entry_cents":null,"standing_target_cents":51},"PRA":{"credited":false,"entry_cents":null,"standing_target_cents":31}}}` | R-STORY#line-522; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_MAIN","anchor_split_cents":17,"leg0_anchor_cents":41,"leg1_anchor_cents":58,"leg0_drift_cents":0,"leg1_drift_cents":4,"leg0_travel_cents":26,"leg1_travel_cents":22,"joint_mid_sum_cents":103,"joint_spread_cents":6,"inverse_coherence":0.19999999999999996,"volume_log1p":8.27770173836347,"hours_from_discovery":15.572777777777778,"divot_depth_cents":1.0238095238095237,"oriented_leg_ids":["PRA","DAN"]}` [R-STORY#line-522; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPMATCH-26MAY18SMIGUI (26MAY) | 0.850795 / 1.000000 | R-CORPUS#row-8368; RANGE_SPECTRUM_PATH | R-RANGE#row-3945; GUI anchor 40 (tick#1[1779154299,39,40,40]), low 32 (tick#100[1779184652,29,36,32]), close 40 (terminal tick#103[1779185556,39,40,40]); SMI anchor 61 (tick#1[1779154299,60,61,61]), low 47 (tick#101[1779184954,45,48,47]), close 58 (terminal tick#103[1779185556,60,61,58]) |
| N2 | KXATPMATCH-26MAY06ARNMUN (26MAY) | 0.848746 / 1.000000 | R-CORPUS#row-8160; RANGE_SPECTRUM_PATH | R-RANGE#row-3744; MUN anchor 44 (tick#1[1778045985,43,44,44]), low 26 (tick#108[1778078300,25,26,26]), close 41 (terminal tick#115[1778080426,41,43,41]); ARN anchor 58 (tick#1[1778045985,57,58,58]), low 46 (tick#111[1778079203,46,47,47]), close 57 (terminal tick#115[1778080426,57,59,57]) |
| N3 | KXATPMATCH-26JUN22BROHOL (26JUN) | 0.839650 / 1.000000 | R-CORPUS#row-7564; RANGE_SPECTRUM_PATH | R-RANGE#row-3499; BRO anchor 44 (tick#1[1782108138,43,44,44]), low 44 (tick#1[1782108138,43,44,44]), close 44 (terminal tick#106[1782139943,38,46,44]); HOL anchor 56 (tick#1[1782108138,55,56,56]), low 42 (tick#99[1782137758,38,42,44]), close 58 (terminal tick#106[1782139943,56,61,58]) |
| N4 | KXATPMATCH-26MAY05KYPDRO (26MAY) | 0.837937 / 1.000000 | R-CORPUS#row-8155; RANGE_SPECTRUM_PATH | R-RANGE#row-3739; KYP anchor 38 (tick#1[1777948358,37,38,38]), low 26 (tick#108[1777980655,24,27,26]), close 38 (terminal tick#110[1777981258,38,39,38]); DRO anchor 62 (tick#1[1777948358,62,63,63]), low 55 (tick#103[1777979149,54,55,55]), close 65 (terminal tick#110[1777981258,61,64,65]) |
| N5 | KXATPMATCH-26MAY05DELDEJ (26MAY) | 0.837534 / 1.000000 | R-CORPUS#row-8150; RANGE_SPECTRUM_PATH | R-RANGE#row-3735; DEL anchor 44 (tick#1[1777951673,43,44,44]), low 38 (tick#98[1777980956,36,38,38]), close 45 (terminal tick#99[1777981258,38,39,45]); DEJ anchor 57 (tick#1[1777951673,56,57,57]), low 53 (tick#96[1777980354,53,56,53]), close 61 (terminal tick#99[1777981258,61,62,61]) |
| N6 | KXATPMATCH-26JUN17TIEAUG (26JUN) | 0.829066 / 1.000000 | R-CORPUS#row-7507; RANGE_SPECTRUM_PATH | R-RANGE#row-3452; TIE anchor 43 (tick#1[1781674880,42,43,43]), low 30 (tick#88[1781706380,31,32,30]), close 39 (terminal tick#91[1781707330,39,40,39]); AUG anchor 59 (tick#1[1781674880,58,59,59]), low 55 (tick#65[1781697698,55,56,56]), close 61 (terminal tick#91[1781707330,60,61,61]) |
| N7 | KXATPMATCH-26JUN29RINTAR (26JUN) | 0.828717 / 1.000000 | R-CORPUS#row-7765; RANGE_SPECTRUM_PATH | R-RANGE#row-3682; TAR anchor 43 (tick#1[1782709928,42,43,43]), low 38 (tick#82[1782739754,38,39,39]), close 40 (terminal tick#84[1782741710,42,43,40]); RIN anchor 59 (tick#1[1782709928,58,59,59]), low 58 (tick#1[1782709928,58,59,59]), close 59 (terminal tick#84[1782741710,57,59,59]) |

**Derivation arithmetic → action → verbatim sentence.**

**DAN.** Σweighted-ratio / Σweight = (KXATPMATCH-26MAY18SMIGUI:(0.850795×1.000000)×(47/61) + KXATPMATCH-26MAY06ARNMUN:(0.848746×1.000000)×(46/58) + KXATPMATCH-26JUN22BROHOL:(0.839650×1.000000)×(42/56) + KXATPMATCH-26MAY05KYPDRO:(0.837937×1.000000)×(55/62) + KXATPMATCH-26MAY05DELDEJ:(0.837534×1.000000)×(53/57) + KXATPMATCH-26JUN17TIEAUG:(0.829066×1.000000)×(55/59) + KXATPMATCH-26JUN29RINTAR:(0.828717×1.000000)×(58/59)) / 5.872445 = 0.863018957908. Raw round(58×0.863018957908)=50; mass=0.838920697100; blend with lineage 59 gives 51; min(pair cap 68, post-only cap 60) gives 51. Printed action HOLD_REST@51, active-before 51.

> At 15.572778 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPMATCH-26MAY18SMIGUI@0.850795, KXATPMATCH-26MAY06ARNMUN@0.848746, KXATPMATCH-26JUN22BROHOL@0.839650, KXATPMATCH-26MAY05KYPDRO@0.837937, KXATPMATCH-26MAY05DELDEJ@0.837534, KXATPMATCH-26JUN17TIEAUG@0.829066, KXATPMATCH-26JUN29RINTAR@0.828717. DAN has anchor 58, neighborhood low ratio 0.8630189579082452, lineage target 59, pair cap 68, and post-only cap 60. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=51; ACTIVE_TARGET_BEFORE_CENTS=51.

**PRA.** Σweighted-ratio / Σweight = (KXATPMATCH-26MAY18SMIGUI:(0.850795×1.000000)×(32/40) + KXATPMATCH-26MAY06ARNMUN:(0.848746×1.000000)×(26/44) + KXATPMATCH-26JUN22BROHOL:(0.839650×1.000000)×(44/44) + KXATPMATCH-26MAY05KYPDRO:(0.837937×1.000000)×(26/38) + KXATPMATCH-26MAY05DELDEJ:(0.837534×1.000000)×(38/44) + KXATPMATCH-26JUN17TIEAUG:(0.829066×1.000000)×(30/43) + KXATPMATCH-26JUN29RINTAR:(0.828717×1.000000)×(38/43)) / 5.872445 = 0.788298640137. Raw round(41×0.788298640137)=32; mass=0.838920697100; blend with lineage 40 gives 33; min(pair cap 48, post-only cap 41) gives 33. Printed action REPRICE_REST@33, active-before 31.

> At 15.572778 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPMATCH-26MAY18SMIGUI@0.850795, KXATPMATCH-26MAY06ARNMUN@0.848746, KXATPMATCH-26JUN22BROHOL@0.839650, KXATPMATCH-26MAY05KYPDRO@0.837937, KXATPMATCH-26MAY05DELDEJ@0.837534, KXATPMATCH-26JUN17TIEAUG@0.829066, KXATPMATCH-26JUN29RINTAR@0.828717. PRA has anchor 41, neighborhood low ratio 0.7882986401366968, lineage target 40, pair cap 48, and post-only cap 41. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=33; ACTIVE_TARGET_BEFORE_CENTS=31.

### TP19 — 15.573889 hours from discovery (2026-07-18T11:11:00.000Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

DAN: R-BOOK-DAN#rows-1..11561, terminal KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-11561 = 58/61 last 62; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=DAN,ts<=1784373060.000 (37 rows; last #row-39216 7728af84-d245-5ebc-ebbb-f41f19a003f2@62)

PRA: R-BOOK-PRA#rows-1..3806, terminal KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-3806 = 39/42 last 41; R-PRINTS predicate event=KXATPMATCH-26JUL18DANPRA,leg=PRA,ts<=1784373060.000 (22 rows; last #row-39209 ec74ef83-2b94-6f08-a334-f4ad2697ac48@41)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"DAN":1,"PRA":1},"anchors_cents":{"DAN":58,"PRA":41}}` | R-STORY#line-528; raw cumulative prefixes above |
| opening_split | `{"sum_cents":99,"absolute_split_cents":17}` | R-STORY#line-528; raw cumulative prefixes above |
| drift | `{"DAN":{"current_cents":62,"drift_cents":4},"PRA":{"current_cents":41,"drift_cents":0}}` | R-STORY#line-528; raw cumulative prefixes above |
| steps_stillness | `{"DAN":{"step_count":152,"last_step_cents":2,"still_seconds":591},"PRA":{"step_count":22,"last_step_cents":-1,"still_seconds":3810.713000059128}}` | R-STORY#line-528; raw cumulative prefixes above |
| shape_survival | `{"DAN":{"directional_step_share":0.4605263157894737,"observed_steps":152},"PRA":{"directional_step_share":0,"observed_steps":22}}` | R-STORY#line-528; raw cumulative prefixes above |
| ripeness | `{"DAN":{"continuous_evidence_mass":0.9999137856711785,"observations":11598,"prints":37},"PRA":{"continuous_evidence_mass":0.9997389715478987,"observations":3830,"prints":22}}` | R-STORY#line-528; raw cumulative prefixes above |
| lows_travel | `{"DAN":{"low_cents":49,"high_cents":71,"travel_cents":22},"PRA":{"low_cents":34,"high_cents":60,"travel_cents":26}}` | R-STORY#line-528; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":103,"spread_sum_cents":6,"dwell_seconds":{"DAN":591,"PRA":3810.713000059128}}` | R-STORY#line-528; raw cumulative prefixes above |
| divots | `{"DAN":{"count":21,"mean_depth_cents":1.0476190476190477,"latest":{"timestamp_epoch":1784372462,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-11386","floor_cents":60,"depth_cents":2}},"PRA":{"count":2,"mean_depth_cents":1,"latest":{"timestamp_epoch":1784324849,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-10","floor_cents":50,"depth_cents":1}}}` | R-STORY#line-528; raw cumulative prefixes above |
| depth_size | `{"DAN":{"bid_depth_5":13801,"ask_depth_5":13465,"bid_share":0.5061615198415609,"top_bid_size":624,"top_ask_size":2},"PRA":{"bid_depth_5":14194,"ask_depth_5":24056,"bid_share":0.3710849673202614,"top_bid_size":2,"top_ask_size":536}}` | R-STORY#line-528; raw cumulative prefixes above |
| volume | `{"DAN":{"print_count":37,"contracts":3322.08},"PRA":{"print_count":22,"contracts":612.06}}` | R-STORY#line-528; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.19999999999999996,"drift_sum_cents":4,"both_legs_named":true}` | R-STORY#line-528; raw cumulative prefixes above |
| category | `{"category":"ATP_MAIN"}` | R-STORY#line-528; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":15.573888888888888,"hours_to_truth_bell":0,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-528; raw cumulative prefixes above |
| books | `{"DAN":{"bid_cents":58,"ask_cents":61,"last_trade_cents":62,"receipt":"KXATPMATCH-26JUL18DANPRA-DAN.csv.gz#row-11561"},"PRA":{"bid_cents":39,"ask_cents":42,"last_trade_cents":41,"receipt":"KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-3806"}}` | R-STORY#line-528; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":2,"legs":{"DAN":{"credited":false,"entry_cents":null,"standing_target_cents":51},"PRA":{"credited":false,"entry_cents":null,"standing_target_cents":33}}}` | R-STORY#line-528; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_MAIN","anchor_split_cents":17,"leg0_anchor_cents":41,"leg1_anchor_cents":58,"leg0_drift_cents":0,"leg1_drift_cents":4,"leg0_travel_cents":26,"leg1_travel_cents":22,"joint_mid_sum_cents":103,"joint_spread_cents":6,"inverse_coherence":0.19999999999999996,"volume_log1p":8.27770173836347,"hours_from_discovery":15.573888888888888,"divot_depth_cents":1.0238095238095237,"oriented_leg_ids":["PRA","DAN"]}` [R-STORY#line-528; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPMATCH-26MAY18SMIGUI (26MAY) | 0.850794 / 1.000000 | R-CORPUS#row-8368; RANGE_SPECTRUM_PATH | R-RANGE#row-3945; GUI anchor 40 (tick#1[1779154299,39,40,40]), low 32 (tick#100[1779184652,29,36,32]), close 40 (terminal tick#103[1779185556,39,40,40]); SMI anchor 61 (tick#1[1779154299,60,61,61]), low 47 (tick#101[1779184954,45,48,47]), close 58 (terminal tick#103[1779185556,60,61,58]) |
| N2 | KXATPMATCH-26MAY06ARNMUN (26MAY) | 0.848744 / 1.000000 | R-CORPUS#row-8160; RANGE_SPECTRUM_PATH | R-RANGE#row-3744; MUN anchor 44 (tick#1[1778045985,43,44,44]), low 26 (tick#108[1778078300,25,26,26]), close 41 (terminal tick#115[1778080426,41,43,41]); ARN anchor 58 (tick#1[1778045985,57,58,58]), low 46 (tick#111[1778079203,46,47,47]), close 57 (terminal tick#115[1778080426,57,59,57]) |
| N3 | KXATPMATCH-26JUN22BROHOL (26JUN) | 0.839648 / 1.000000 | R-CORPUS#row-7564; RANGE_SPECTRUM_PATH | R-RANGE#row-3499; BRO anchor 44 (tick#1[1782108138,43,44,44]), low 44 (tick#1[1782108138,43,44,44]), close 44 (terminal tick#106[1782139943,38,46,44]); HOL anchor 56 (tick#1[1782108138,55,56,56]), low 42 (tick#99[1782137758,38,42,44]), close 58 (terminal tick#106[1782139943,56,61,58]) |
| N4 | KXATPMATCH-26MAY05KYPDRO (26MAY) | 0.837935 / 1.000000 | R-CORPUS#row-8155; RANGE_SPECTRUM_PATH | R-RANGE#row-3739; KYP anchor 38 (tick#1[1777948358,37,38,38]), low 26 (tick#108[1777980655,24,27,26]), close 38 (terminal tick#110[1777981258,38,39,38]); DRO anchor 62 (tick#1[1777948358,62,63,63]), low 55 (tick#103[1777979149,54,55,55]), close 65 (terminal tick#110[1777981258,61,64,65]) |
| N5 | KXATPMATCH-26MAY05DELDEJ (26MAY) | 0.837532 / 1.000000 | R-CORPUS#row-8150; RANGE_SPECTRUM_PATH | R-RANGE#row-3735; DEL anchor 44 (tick#1[1777951673,43,44,44]), low 38 (tick#98[1777980956,36,38,38]), close 45 (terminal tick#99[1777981258,38,39,45]); DEJ anchor 57 (tick#1[1777951673,56,57,57]), low 53 (tick#96[1777980354,53,56,53]), close 61 (terminal tick#99[1777981258,61,62,61]) |
| N6 | KXATPMATCH-26JUN17TIEAUG (26JUN) | 0.829065 / 1.000000 | R-CORPUS#row-7507; RANGE_SPECTRUM_PATH | R-RANGE#row-3452; TIE anchor 43 (tick#1[1781674880,42,43,43]), low 30 (tick#88[1781706380,31,32,30]), close 39 (terminal tick#91[1781707330,39,40,39]); AUG anchor 59 (tick#1[1781674880,58,59,59]), low 55 (tick#65[1781697698,55,56,56]), close 61 (terminal tick#91[1781707330,60,61,61]) |
| N7 | KXATPMATCH-26JUN29RINTAR (26JUN) | 0.828715 / 1.000000 | R-CORPUS#row-7765; RANGE_SPECTRUM_PATH | R-RANGE#row-3682; TAR anchor 43 (tick#1[1782709928,42,43,43]), low 38 (tick#82[1782739754,38,39,39]), close 40 (terminal tick#84[1782741710,42,43,40]); RIN anchor 59 (tick#1[1782709928,58,59,59]), low 58 (tick#1[1782709928,58,59,59]), close 59 (terminal tick#84[1782741710,57,59,59]) |

**Derivation arithmetic → action → verbatim sentence.**

**DAN.** Σweighted-ratio / Σweight = (KXATPMATCH-26MAY18SMIGUI:(0.850794×1.000000)×(47/61) + KXATPMATCH-26MAY06ARNMUN:(0.848744×1.000000)×(46/58) + KXATPMATCH-26JUN22BROHOL:(0.839648×1.000000)×(42/56) + KXATPMATCH-26MAY05KYPDRO:(0.837935×1.000000)×(55/62) + KXATPMATCH-26MAY05DELDEJ:(0.837532×1.000000)×(53/57) + KXATPMATCH-26JUN17TIEAUG:(0.829065×1.000000)×(55/59) + KXATPMATCH-26JUN29RINTAR:(0.828715×1.000000)×(58/59)) / 5.872434 = 0.863018957908. Raw round(58×0.863018957908)=50; mass=0.838919100981; blend with lineage 59 gives 51; min(pair cap 66, post-only cap 60) gives 51. Printed action HOLD_REST@51, active-before 51.

> At 15.573889 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPMATCH-26MAY18SMIGUI@0.850794, KXATPMATCH-26MAY06ARNMUN@0.848744, KXATPMATCH-26JUN22BROHOL@0.839648, KXATPMATCH-26MAY05KYPDRO@0.837935, KXATPMATCH-26MAY05DELDEJ@0.837532, KXATPMATCH-26JUN17TIEAUG@0.829065, KXATPMATCH-26JUN29RINTAR@0.828715. DAN has anchor 58, neighborhood low ratio 0.8630189579082453, lineage target 59, pair cap 66, and post-only cap 60. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=51; ACTIVE_TARGET_BEFORE_CENTS=51.

**PRA.** Σweighted-ratio / Σweight = (KXATPMATCH-26MAY18SMIGUI:(0.850794×1.000000)×(32/40) + KXATPMATCH-26MAY06ARNMUN:(0.848744×1.000000)×(26/44) + KXATPMATCH-26JUN22BROHOL:(0.839648×1.000000)×(44/44) + KXATPMATCH-26MAY05KYPDRO:(0.837935×1.000000)×(26/38) + KXATPMATCH-26MAY05DELDEJ:(0.837532×1.000000)×(38/44) + KXATPMATCH-26JUN17TIEAUG:(0.829065×1.000000)×(30/43) + KXATPMATCH-26JUN29RINTAR:(0.828715×1.000000)×(38/43)) / 5.872434 = 0.788298640137. Raw round(41×0.788298640137)=32; mass=0.838919100981; blend with lineage 40 gives 33; min(pair cap 48, post-only cap 41) gives 33. Printed action HOLD_REST@33, active-before 33.

> At 15.573889 hours from discovery, all sixteen readers fired for KXATPMATCH-26JUL18DANPRA. The named neighborhood is KXATPMATCH-26MAY18SMIGUI@0.850794, KXATPMATCH-26MAY06ARNMUN@0.848744, KXATPMATCH-26JUN22BROHOL@0.839648, KXATPMATCH-26MAY05KYPDRO@0.837935, KXATPMATCH-26MAY05DELDEJ@0.837532, KXATPMATCH-26JUN17TIEAUG@0.829065, KXATPMATCH-26JUN29RINTAR@0.828715. PRA has anchor 41, neighborhood low ratio 0.7882986401366968, lineage target 40, pair cap 48, and post-only cap 41. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=33; ACTIVE_TARGET_BEFORE_CENTS=33.


## 3. Capture vs ceiling

Status: **PROVISIONAL_UNTIL_CC_RULES_BELL**. L11 bell 1784373060 from TAPE_INFERENCE; this explanation does not alter it.

| Side | Deepest lawful print | Moment | Receipt | Captured | Gap to ceiling |
|---|---:|---|---|---:|---:|
| DAN | 59 | 1.876048 h after formation; 2026-07-18T01:48:26.774Z | R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 | NONE | NONE; final rest 51, shortfall 8 |
| PRA | 41 | 2.778047 h after formation; 2026-07-18T02:42:33.971Z | R-PRINTS#row-39165; 54075ae0-14e4-6484-d298-207ef219837f | NONE | NONE; final rest 33, shortfall 8 |

Pair ceiling: 100¢, discount 0¢. Captured pair: NONE, discount NONE. Per-side minima need not be simultaneous; this is the deepest standing-rest opportunity each side's tape actually offered.

## 4. The surprise and humility ledger

### Every receipt-defined neighborhood-range departure

Audit convention: because pass 1 emitted no prediction interval, the expected range is the minimum-to-maximum normalized low of its seven named neighbors, mapped onto the target anchor. Every pass-1 stage whose later lawful true-print minimum left that envelope is listed; this is an explanation metric, not a model change.

| Stage | Side | Neighbor-low prediction | Realized | Departure | Realization receipt |
|---:|---|---:|---:|---:|---|
| 1 @ 0.000000h | DAN | 36.83..58.00 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 2 @ 0.267778h | DAN | 36.83..58.00 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 3 @ 0.299444h | DAN | 36.83..58.00 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 4 @ 2.633333h | DAN | 36.83..58.00 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 5 @ 2.928611h | DAN | 36.83..58.00 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 6 @ 3.102778h | DAN | 36.83..58.00 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 7 @ 3.102821h | DAN | 36.83..58.00 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 8 @ 3.158889h | DAN | 42.53..58.00 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 9 @ 3.911944h | DAN | 42.18..58.00 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 10 @ 4.225000h | DAN | 42.65..58.00 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 11 @ 4.321944h | DAN | 42.65..57.08 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.92¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 12 @ 5.546949h | DAN | 43.50..58.00 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 13 @ 5.962778h | DAN | 43.50..58.00 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 14 @ 6.197993h | DAN | 43.50..57.02 | 59 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 1.98¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39162; 64c0a5d8-6433-51fe-50cc-0434ba1ef366 |
| 15 @ 8.999167h | DAN | 43.50..58.00 | 60 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 2.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39174; bdf858ea-f622-7ff2-3775-1605f38a4176 |
| 16 @ 11.952500h | DAN | 43.50..58.00 | 60 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 2.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39189; fe31d706-a2f6-5cc2-4c5b-800622f881ee |
| 17 @ 14.914167h | DAN | 43.50..58.00 | 60 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 2.00¢ | 2026-07-18T11:11:00.000Z; R-PRINTS#row-39202; 1efa02ce-156f-542a-f619-5f5d1fcc2bd5 |

### Every decision hindsight beats

A decision is listed when a later formation-lawful true print proves a different rest would have captured closer to the per-side ceiling, or when a credited leg still receives a new action sentence. This is hindsight, never a claim that the future row was knowable.

| Stage | Side | Printed decision | Hindsight-better action | Reading that could have licensed it | Realized receipt / defect |
|---:|---|---|---|---|---|
| 11 @ 4.321944h | DAN | PLACE_REST@49 | REST@59 | lows_travel running low 49 | 2026-07-18T01:48:26.774Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 11 @ 4.321944h | PRA | PLACE_REST@36 | REST@41 | neighborhood low envelope 27.06..41.00 | 2026-07-18T02:42:33.971Z; R-PRINTS#row-39165; 54075ae0-14e4-6484-d298-207ef219837f |
| 12 @ 5.546949h | DAN | REPRICE_REST@51 | REST@59 | lows_travel running low 49 | 2026-07-18T01:48:26.774Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 12 @ 5.546949h | PRA | REPRICE_REST@38 | REST@41 | neighborhood low envelope 28.05..41.00 | 2026-07-18T02:42:33.971Z; R-PRINTS#row-39165; 54075ae0-14e4-6484-d298-207ef219837f |
| 13 @ 5.962778h | DAN | HOLD_REST@51 | REST@59 | lows_travel running low 49 | 2026-07-18T01:48:26.774Z; R-PRINTS#row-39161; 868ebd99-045b-41ce-52f3-d6ed304390d2 |
| 13 @ 5.962778h | PRA | HOLD_REST@38 | REST@41 | neighborhood low envelope 28.05..41.00 | 2026-07-18T02:42:33.971Z; R-PRINTS#row-39165; 54075ae0-14e4-6484-d298-207ef219837f |
| 14 @ 6.197993h | DAN | HOLD_REST@51 | REST@59 | lows_travel running low 49 | 2026-07-18T02:13:01.176Z; R-PRINTS#row-39162; 64c0a5d8-6433-51fe-50cc-0434ba1ef366 |
| 14 @ 6.197993h | PRA | REPRICE_REST@35 | REST@41 | neighborhood low envelope 24.23..41.00 | 2026-07-18T02:42:33.971Z; R-PRINTS#row-39165; 54075ae0-14e4-6484-d298-207ef219837f |
| 15 @ 8.999167h | DAN | HOLD_REST@51 | REST@60 | lows_travel running low 49 | 2026-07-18T04:47:43.834Z; R-PRINTS#row-39174; bdf858ea-f622-7ff2-3775-1605f38a4176 |
| 15 @ 8.999167h | PRA | REPRICE_REST@31 | REST@41 | neighborhood low envelope 19.52..41.00 | 2026-07-18T05:18:55.842Z; R-PRINTS#row-39175; 5198619d-86a7-7a35-0757-8819a46a6cc8 |
| 16 @ 11.952500h | DAN | HOLD_REST@51 | REST@60 | lows_travel running low 49 | 2026-07-18T08:23:40.969Z; R-PRINTS#row-39189; fe31d706-a2f6-5cc2-4c5b-800622f881ee |
| 16 @ 11.952500h | PRA | HOLD_REST@31 | REST@41 | neighborhood low envelope 19.52..41.00 | 2026-07-18T10:07:29.287Z; R-PRINTS#row-39198; 6a5b1a68-a916-4763-e3ac-786bf85a68fa |
| 17 @ 14.914167h | DAN | HOLD_REST@51 | REST@60 | lows_travel running low 49 | 2026-07-18T10:47:25.685Z; R-PRINTS#row-39202; 1efa02ce-156f-542a-f619-5f5d1fcc2bd5 |
| 17 @ 14.914167h | PRA | HOLD_REST@31 | REST@41 | neighborhood low envelope 19.52..41.00 | 2026-07-18T10:46:45.389Z; R-PRINTS#row-39201; 8a925a9f-1f2c-4ee4-eb77-e488e41c5b3c |

### What remains unexplained

- No connected resource explains why the 59/40 shape survived while the named May/June games dipped.
- The neighborhood uses full historical path summaries; it has no participant-state or match-context causal variable.
- The bell is TAPE_INFERENCE and awaits CC ratification.


## 5. DANPRA 51/33 and the May/June tapes at the same stage

DAN: round(58×0.863018957908)=50; mass 0.838919100981 blends lineage 59 to 51; caps 66/60 leave 51. PRA: round(41×0.788298640137)=32; the same mass blends lineage 40 to 33; caps 48/41 leave 33.

"Same stage" here means each neighbor's terminal/right-edge row because the query point is DANPRA's provisional bell. These are the exact May/June source rows, not paraphrased outcomes:

| Neighbor | Score | Receipts | Terminal tape facts |
|---|---:|---|---|
| KXATPMATCH-26MAY18SMIGUI | 0.850794 | R-CORPUS#row-8368; R-RANGE#row-3945 | GUI: anchor 40, low 32, close 40; same-stage terminal tick#103 [1779185556,39,40,40]; SMI: anchor 61, low 47, close 58; same-stage terminal tick#103 [1779185556,60,61,58] |
| KXATPMATCH-26MAY06ARNMUN | 0.848744 | R-CORPUS#row-8160; R-RANGE#row-3744 | MUN: anchor 44, low 26, close 41; same-stage terminal tick#115 [1778080426,41,43,41]; ARN: anchor 58, low 46, close 57; same-stage terminal tick#115 [1778080426,57,59,57] |
| KXATPMATCH-26JUN22BROHOL | 0.839648 | R-CORPUS#row-7564; R-RANGE#row-3499 | BRO: anchor 44, low 44, close 44; same-stage terminal tick#106 [1782139943,38,46,44]; HOL: anchor 56, low 42, close 58; same-stage terminal tick#106 [1782139943,56,61,58] |
| KXATPMATCH-26MAY05KYPDRO | 0.837935 | R-CORPUS#row-8155; R-RANGE#row-3739 | KYP: anchor 38, low 26, close 38; same-stage terminal tick#110 [1777981258,38,39,38]; DRO: anchor 62, low 55, close 65; same-stage terminal tick#110 [1777981258,61,64,65] |
| KXATPMATCH-26MAY05DELDEJ | 0.837532 | R-CORPUS#row-8150; R-RANGE#row-3735 | DEL: anchor 44, low 38, close 45; same-stage terminal tick#99 [1777981258,38,39,45]; DEJ: anchor 57, low 53, close 61; same-stage terminal tick#99 [1777981258,61,62,61] |
| KXATPMATCH-26JUN17TIEAUG | 0.829065 | R-CORPUS#row-7507; R-RANGE#row-3452 | TIE: anchor 43, low 30, close 39; same-stage terminal tick#91 [1781707330,39,40,39]; AUG: anchor 59, low 55, close 61; same-stage terminal tick#91 [1781707330,60,61,61] |
| KXATPMATCH-26JUN29RINTAR | 0.828715 | R-CORPUS#row-7765; R-RANGE#row-3682 | TAR: anchor 43, low 38, close 40; same-stage terminal tick#84 [1782741710,42,43,40]; RIN: anchor 59, low 58, close 59; same-stage terminal tick#84 [1782741710,57,59,59] |

The neighborhood's lows licensed 51/33; its terminal rows show that those games generally recovered toward their anchors. DANPRA never supplied the antecedent dip, so recovery behavior was not enough to make the rests reachable.
