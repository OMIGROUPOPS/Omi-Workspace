# Game explained — URSPAL

License: LAW_INDEX read at `dcac4032`, SHA-256 `c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6`; laws L0 L8 L11 L18 L20 L22. Explanation lane only: pass-1 receipts and named custody rows; zero runs, zero passes, zero tuning, zero 804 reads.

Steps-Behind Law: assume the OS is always a few steps behind the market's finesse. This explanation states what was missed, what surprised, and what remains unexplained.

## Receipt bindings

- **R-LAW:** `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LAW_INDEX.md` @ commit `dcac4032`, SHA-256 `c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6`.
- **R-STORY:** `.claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/FOUR_STORIES.md`, SHA-256 `9e7dad007a17d075e8bacd5d1b32f9eeaebeeaa179f93866873d8173b06abfe6`.
- **R-RESULT:** `.claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/FOUR_STORIES_RECEIPT.json`, SHA-256 `22381e774e538ed5bc4fe05f7fd50c64efc06d5f61c6f65eb65cde2851049f0d`.
- **R-CORPUS:** `.claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/CORPUS_INDEX.jsonl.gz`, SHA-256 `210951fa9c1bd8d255e6501f7507144311b297b811bd992dd04a1ab46ff37ba1`; row numbers are decompressed JSONL rows.
- **R-RANGE:** external custody `C:\Users\omigr\OMI-Workspace\.corpus-cache-v6\range_spectrum_v1.jsonl`, SHA-256 `1e9891acaaea23a73160aaa26b10b17c87270c1209d9a2a0a23a6a6c56434884`, 130935927 bytes; row/tick refs below.
- **R-HIST:** external custody `C:\Users\omigr\OMI-Workspace\.corpus-cache-v6\historical_events_materialized.csv`, SHA-256 `46741cded0ccb0a24302da4bc7b77f1bb3b82707a8cceaa272a902bae683339a`, 1041339 bytes; physical CSV line refs below.
- **R-PRINTS:** `.claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/TARGET_PRINTS_5.jsonl.gz`, SHA-256 `575784544073ec3e9e84818ffae68203b6d616d51868f65f3cd09559b3af198e`; rows are decompressed JSONL rows. Upstream full tape: `C:\Users\omigr\OMI-Window1-private\fit-local\prints.jsonl`, SHA-256 `e9b5a765b51ddbf0d65364c4f38744ad949ca3c675e5b3a0e472392fbcfabb55`.
- **R-TRUTH:** `c0056976:.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.json`, SHA-256 `f7bc71d8e615859db272d841e125bc4836a685d82bb2d6769762c9bc19e56729`; event row `KXATPCHALLENGERMATCH-26JUL14URSPAL`, bell 1784045100 (TAPE_INFERENCE).
- **R-LINEAGE:** external custody `C:\Users\omigr\OMI-Workspace\.claude\window1_live_v4_replay\v54_walk5_live_20260821\FULL_DECISION_TRACE_5.jsonl.gz`, SHA-256 `085fbf04dbc16f8c76691a0823a5370061afc9d738b5eefda9eab92fef4ccbc4`, 55209610 bytes, 133626 rows; only lineage values already printed in R-STORY are used here.
- **R-BOOK-PAL:** external custody `C:\Users\omigr\OMI-Window1-private\fit-local\ticks\KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz`, SHA-256 `216e26887d7e83ffc9860d9cfb7e8ecd7f13c36b7545231aabf820c6f1517f47`, 754076 bytes, 97403 data rows.
- **R-BOOK-URS:** external custody `C:\Users\omigr\OMI-Window1-private\fit-local\ticks\KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz`, SHA-256 `6535f985d69bf285fbc0db3984aa78be6b27120b025590957053e9c2aa695af9`, 563975 bytes, 63603 data rows.

NEIGHBOR-GRAIN [NG-URSPAL]: receipt-bearing comparisons below are either RANGE_SPECTRUM_PATH polling paths (R-CORPUS + R-RANGE, approximately 100 ticks per leg) or HISTORICAL_EVENT_AGGREGATE rows (R-CORPUS + R-HIST, no intramatch path). RESOURCE-GAP [GAP-NG-URSPAL]: no raw-tape order-book depth receipt exists at the matched-neighbor stage; range-path best-five summaries are not raw depth.

## 1. The story — hour 0 to bell (219 words; two-page guard passed)

Hour 0 began unformed at 38/62 anchors behind symmetric 4/95 books. Formation took 0.704444 hours. The first lawful posture was 20 PAL / 59 URS; as the books settled, the joint picture moved that pair through 28/49 and then 31/51. Nothing in those early points foresaw the full late inversion.

At hour 12.024469 the pair stood 31 PAL / 49 URS. PAL printed 31 at 12.039239 and credited. With 31 committed, the sibling cap widened and URS was re-derived at 53, then 50. URS printed 46 at 12.669913 and completed the pair at 77, a 23-cent discount.

The realized tape kept moving after capture: PAL reached 30, while URS reached 28 immediately before the L11 bell. The provisional ceiling was therefore 58, or a 42-cent discount. The capture gave up 1 cent on PAL and 18 on URS. The large URS gap is the clearest case here of a machine following a collapse rather than anticipating its finesse.

The bell itself is not settled socially: the committed CC note says the recorded bell appears at least 48 minutes late relative to the external move. L11 still makes the truth-table epoch the only grading source, so this document does not move it; capture-versus-ceiling remains PROVISIONAL. As in GIUBAR, post-credit PLACE_REST sentences continued even though the credited guard prevented new rests.

## 2. Turning points — 7 complete causal chains

### TP1 — 0.000000 hours from discovery (2026-07-14T03:15:59.000Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

PAL: R-BOOK-PAL#rows-1..1, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-1 = 4/95 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=PAL,ts<=1783998959.000 (0 rows)

URS: R-BOOK-URS#rows-1..1, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-1 = 4/95 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=URS,ts<=1783998959.000 (0 rows)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"PAL":0,"URS":0},"anchors_cents":{"PAL":38,"URS":62}}` | R-STORY#line-136; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":24}` | R-STORY#line-136; raw cumulative prefixes above |
| drift | `{"PAL":{"current_cents":49,"drift_cents":11},"URS":{"current_cents":49,"drift_cents":-13}}` | R-STORY#line-136; raw cumulative prefixes above |
| steps_stillness | `{"PAL":{"step_count":0,"last_step_cents":null,"still_seconds":0},"URS":{"step_count":0,"last_step_cents":null,"still_seconds":0}}` | R-STORY#line-136; raw cumulative prefixes above |
| shape_survival | `{"PAL":{"directional_step_share":null,"observed_steps":0},"URS":{"directional_step_share":null,"observed_steps":0}}` | R-STORY#line-136; raw cumulative prefixes above |
| ripeness | `{"PAL":{"continuous_evidence_mass":0.5,"observations":1,"prints":0},"URS":{"continuous_evidence_mass":0.5,"observations":1,"prints":0}}` | R-STORY#line-136; raw cumulative prefixes above |
| lows_travel | `{"PAL":{"low_cents":49,"high_cents":49,"travel_cents":0},"URS":{"low_cents":49,"high_cents":49,"travel_cents":0}}` | R-STORY#line-136; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":98,"spread_sum_cents":182,"dwell_seconds":{"PAL":0,"URS":0}}` | R-STORY#line-136; raw cumulative prefixes above |
| divots | `{"PAL":{"count":0,"mean_depth_cents":null,"latest":null},"URS":{"count":0,"mean_depth_cents":null,"latest":null}}` | R-STORY#line-136; raw cumulative prefixes above |
| depth_size | `{"PAL":{"bid_depth_5":6771,"ask_depth_5":7214,"bid_share":0.48416160171612443,"top_bid_size":500,"top_ask_size":7},"URS":{"bid_depth_5":6731,"ask_depth_5":7214,"bid_share":0.4826819648619577,"top_bid_size":500,"top_ask_size":7}}` | R-STORY#line-136; raw cumulative prefixes above |
| volume | `{"PAL":{"print_count":0,"contracts":0},"URS":{"print_count":0,"contracts":0}}` | R-STORY#line-136; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.92,"drift_sum_cents":-2,"both_legs_named":true}` | R-STORY#line-136; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-136; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":0,"hours_to_truth_bell":12.816944444444445,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-136; raw cumulative prefixes above |
| books | `{"PAL":{"bid_cents":4,"ask_cents":95,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-1"},"URS":{"bid_cents":4,"ask_cents":95,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-1"}}` | R-STORY#line-136; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":0,"legs":{"PAL":{"credited":false,"entry_cents":null,"standing_target_cents":null},"URS":{"credited":false,"entry_cents":null,"standing_target_cents":null}}}` | R-STORY#line-136; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":24,"leg0_anchor_cents":38,"leg1_anchor_cents":62,"leg0_drift_cents":11,"leg1_drift_cents":-13,"leg0_travel_cents":0,"leg1_travel_cents":0,"joint_mid_sum_cents":98,"joint_spread_cents":182,"inverse_coherence":0.92,"volume_log1p":0,"hours_from_discovery":0,"divot_depth_cents":null,"oriented_leg_ids":["PAL","URS"]}` [R-STORY#line-136; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXWTACHALLENGERMATCH-26JUN14LEOKUL (26JUN) | 0.573552 / 0.945205 | R-CORPUS#row-9693; RANGE_SPECTRUM_PATH | R-RANGE#row-4604; LEO anchor 46 (tick#48[1781416329,5,46,46]), low 46 (tick#48[1781416329,5,46,46]), close 55 (terminal tick#72[1781424913,59,64,55]); KUL anchor 63 (tick#48[1781416329,31,63,63]), low 40 (tick#60[1781420280,38,40,41]), close 40 (terminal tick#72[1781424913,38,40,40]) |
| N2 | KXATPCHALLENGERMATCH-26MAR05CECKYM (26MAR) | 0.535713 / 0.732877 | R-CORPUS#row-4109; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-5512; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N3 | KXATPCHALLENGERMATCH-26MAY10LOMNED (26MAY) | 0.508680 / 0.945205 | R-CORPUS#row-5374; RANGE_SPECTRUM_PATH | R-RANGE#row-2313; NED anchor 45 (tick#98[1778411214,19,35,45]), low 38 (tick#101[1778412119,30,37,38]), close 39 (terminal tick#109[1778414539,40,45,39]); LOM anchor 76 (tick#98[1778411214,63,79,76]), low 52 (tick#108[1778414229,45,51,52]), close 57 (terminal tick#109[1778414539,53,59,57]) |
| N4 | KXATPCHALLENGERMATCH-26MAY14ANDMOL (26MAY) | 0.508414 / 0.945205 | R-CORPUS#row-5591; RANGE_SPECTRUM_PATH | R-RANGE#row-2520; AND anchor 25 (tick#29[1778761965,21,24,25]), low 23 (tick#30[1778762266,19,24,23]), close 39 (terminal tick#31[1778762567,36,39,39]); MOL anchor 87 (tick#27[1778761362,84,86,87]), low 61 (tick#31[1778762567,61,62,61]), close 61 (terminal tick#31[1778762567,61,62,61]) |
| N5 | KXATPCHALLENGERMATCH-26MAR05HEMGEA (26MAR) | 0.507603 / 0.732877 | R-CORPUS#row-4115; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-5511; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N6 | KXATPCHALLENGERMATCH-26MAY12HUEVAR (26MAY) | 0.477684 / 0.945205 | R-CORPUS#row-5502; RANGE_SPECTRUM_PATH | R-RANGE#row-2434; HUE anchor 38 (tick#56[1778591972,38,84,0]), low 21 (tick#75[1778597698,21,33,38]), close 21 (terminal tick#95[1778603748,16,24,21]); VAR anchor 64 (tick#55[1778591671,12,64,0]), low 64 (tick#55[1778591671,12,64,0]), close 86 (terminal tick#95[1778603748,76,86,86]) |
| N7 | KXATPCHALLENGERMATCH-26JUN14BRIGON (26JUN) | 0.477038 / 0.945205 | R-CORPUS#row-3339; RANGE_SPECTRUM_PATH | R-RANGE#row-1485; BRI anchor 11 (tick#24[1781461671,11,95,11]), low 11 (tick#24[1781461671,11,95,11]), close 11 (terminal tick#27[1781462909,5,70,11]); GON anchor 94 (tick#23[1781461369,5,94,0]), low 84 (tick#27[1781462909,84,89,84]), close 84 (terminal tick#27[1781462909,84,89,84]) |

**Derivation arithmetic → action → verbatim sentence.**

**PAL.** Formation progress 0.000000 < 1 overrides the computed candidate; lawful action is HOLD_REST@NONE.

> At 0.000000 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXWTACHALLENGERMATCH-26JUN14LEOKUL@0.573552, KXATPCHALLENGERMATCH-26MAR05CECKYM@0.535713, KXATPCHALLENGERMATCH-26MAY10LOMNED@0.508680, KXATPCHALLENGERMATCH-26MAY14ANDMOL@0.508414, KXATPCHALLENGERMATCH-26MAR05HEMGEA@0.507603, KXATPCHALLENGERMATCH-26MAY12HUEVAR@0.477684, KXATPCHALLENGERMATCH-26JUN14BRIGON@0.477038. PAL has anchor 38, neighborhood low ratio 0.8849307728686079, lineage target NONE, pair cap 98, and post-only cap 94. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=NONE; ACTIVE_TARGET_BEFORE_CENTS=NONE. <!-- CITATION-WELD:CW-18e7adad2816c434:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->

**URS.** Formation progress 0.000000 < 1 overrides the computed candidate; lawful action is HOLD_REST@NONE.

> At 0.000000 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXWTACHALLENGERMATCH-26JUN14LEOKUL@0.573552, KXATPCHALLENGERMATCH-26MAR05CECKYM@0.535713, KXATPCHALLENGERMATCH-26MAY10LOMNED@0.508680, KXATPCHALLENGERMATCH-26MAY14ANDMOL@0.508414, KXATPCHALLENGERMATCH-26MAR05HEMGEA@0.507603, KXATPCHALLENGERMATCH-26MAY12HUEVAR@0.477684, KXATPCHALLENGERMATCH-26JUN14BRIGON@0.477038. URS has anchor 62, neighborhood low ratio 0.8257716587180969, lineage target NONE, pair cap 98, and post-only cap 94. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=HOLD_REST; TARGET_CENTS=NONE; ACTIVE_TARGET_BEFORE_CENTS=NONE. <!-- CITATION-WELD:CW-2cb9104337a15659:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->

### TP2 — 0.704444 hours from discovery (2026-07-14T03:58:14.998Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

PAL: R-BOOK-PAL#rows-1..6, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-6 = 33/95 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=PAL,ts<=1784001494.998 (0 rows)

URS: R-BOOK-URS#rows-1..7, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-7 = 57/95 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=URS,ts<=1784001494.998 (0 rows)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"PAL":1,"URS":1},"anchors_cents":{"PAL":38,"URS":62}}` | R-STORY#line-142; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":24}` | R-STORY#line-142; raw cumulative prefixes above |
| drift | `{"PAL":{"current_cents":64,"drift_cents":26},"URS":{"current_cents":76,"drift_cents":14}}` | R-STORY#line-142; raw cumulative prefixes above |
| steps_stillness | `{"PAL":{"step_count":3,"last_step_cents":26,"still_seconds":0},"URS":{"step_count":3,"last_step_cents":14,"still_seconds":0}}` | R-STORY#line-142; raw cumulative prefixes above |
| shape_survival | `{"PAL":{"directional_step_share":0.6666666666666666,"observed_steps":3},"URS":{"directional_step_share":1,"observed_steps":3}}` | R-STORY#line-142; raw cumulative prefixes above |
| ripeness | `{"PAL":{"continuous_evidence_mass":0.875,"observations":7,"prints":0},"URS":{"continuous_evidence_mass":0.9090909090909091,"observations":10,"prints":0}}` | R-STORY#line-142; raw cumulative prefixes above |
| lows_travel | `{"PAL":{"low_cents":38,"high_cents":64,"travel_cents":26},"URS":{"low_cents":49,"high_cents":76,"travel_cents":27}}` | R-STORY#line-142; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":140,"spread_sum_cents":100,"dwell_seconds":{"PAL":0,"URS":0}}` | R-STORY#line-142; raw cumulative prefixes above |
| divots | `{"PAL":{"count":1,"mean_depth_cents":12,"latest":{"timestamp_epoch":1784001495,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-7","floor_cents":38,"depth_cents":12}},"URS":{"count":0,"mean_depth_cents":null,"latest":null}}` | R-STORY#line-142; raw cumulative prefixes above |
| depth_size | `{"PAL":{"bid_depth_5":7286,"ask_depth_5":7189,"bid_share":0.5033506044905008,"top_bid_size":500,"top_ask_size":7},"URS":{"bid_depth_5":7286,"ask_depth_5":7189,"bid_share":0.5033506044905008,"top_bid_size":500,"top_ask_size":7}}` | R-STORY#line-142; raw cumulative prefixes above |
| volume | `{"PAL":{"print_count":0,"contracts":0},"URS":{"print_count":0,"contracts":0}}` | R-STORY#line-142; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.024390243902439046,"drift_sum_cents":40,"both_legs_named":true}` | R-STORY#line-142; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-142; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":0.7044444444444444,"hours_to_truth_bell":12.1125,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-142; raw cumulative prefixes above |
| books | `{"PAL":{"bid_cents":33,"ask_cents":95,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-6"},"URS":{"bid_cents":57,"ask_cents":95,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-7"}}` | R-STORY#line-142; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":0,"legs":{"PAL":{"credited":false,"entry_cents":null,"standing_target_cents":null},"URS":{"credited":false,"entry_cents":null,"standing_target_cents":null}}}` | R-STORY#line-142; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":24,"leg0_anchor_cents":38,"leg1_anchor_cents":62,"leg0_drift_cents":26,"leg1_drift_cents":14,"leg0_travel_cents":26,"leg1_travel_cents":27,"joint_mid_sum_cents":140,"joint_spread_cents":100,"inverse_coherence":0.024390243902439046,"volume_log1p":0,"hours_from_discovery":0.7044444444444444,"divot_depth_cents":12,"oriented_leg_ids":["PAL","URS"]}` [R-STORY#line-142; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26MAR24GONFAR (26MAR) | 0.523887 / 0.787671 | R-CORPUS#row-4791; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-4779; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N2 | KXATPCHALLENGERMATCH-26MAR22PERORT (26MAR) | 0.520424 / 0.787671 | R-CORPUS#row-4665; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-4979; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N3 | KXATPCHALLENGERMATCH-26MAR29AVECOS (26MAR) | 0.519450 / 0.787671 | R-CORPUS#row-4953; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-4643; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N4 | KXATPCHALLENGERMATCH-26JAN19TORZEB (26JAN) | 0.519172 / 0.787671 | R-CORPUS#row-1795; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-1067; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N5 | KXATPCHALLENGERMATCH-26MAR30DUCRUB (26MAR) | 0.518565 / 0.787671 | R-CORPUS#row-5021; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-4576; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N6 | KXATPCHALLENGERMATCH-26MAR29TOBALV (26MAR) | 0.516957 / 0.787671 | R-CORPUS#row-5002; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-4641; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |
| N7 | KXATPCHALLENGERMATCH-26MAR22DEALV (26MAR) | 0.514711 / 0.787671 | R-CORPUS#row-4632; HISTORICAL_EVENT_AGGREGATE | R-HIST#line-4941; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt |

**Derivation arithmetic → action → verbatim sentence.**

**PAL.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAR24GONFAR:(0.523887×0.787671)×(1/55) + KXATPCHALLENGERMATCH-26MAR22PERORT:(0.520424×0.787671)×(1/58) + KXATPCHALLENGERMATCH-26MAR29AVECOS:(0.519450×0.787671)×(1/50) + KXATPCHALLENGERMATCH-26JAN19TORZEB:(0.519172×0.787671)×(1/49) + KXATPCHALLENGERMATCH-26MAR30DUCRUB:(0.518565×0.787671)×(1/52) + KXATPCHALLENGERMATCH-26MAR29TOBALV:(0.516957×0.787671)×(1/50) + KXATPCHALLENGERMATCH-26MAR22DEALV:(0.514711×0.787671)×(1/58)) / 2.861740 = 0.018900392872. Raw round(38×0.018900392872)=1; mass=0.408820059802; blend with lineage 33 gives 20; min(pair cap 98, post-only cap 94) gives 20. Printed action PLACE_REST@20, active-before NONE. <!-- CITATION-WELD:CW-84700ac8ce0bd97a:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=7 -->

> At 0.704444 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXATPCHALLENGERMATCH-26MAR24GONFAR@0.523887, KXATPCHALLENGERMATCH-26MAR22PERORT@0.520424, KXATPCHALLENGERMATCH-26MAR29AVECOS@0.519450, KXATPCHALLENGERMATCH-26JAN19TORZEB@0.519172, KXATPCHALLENGERMATCH-26MAR30DUCRUB@0.518565, KXATPCHALLENGERMATCH-26MAR29TOBALV@0.516957, KXATPCHALLENGERMATCH-26MAR22DEALV@0.514711. PAL has anchor 38, neighborhood low ratio 0.018900392872100692, lineage target 33, pair cap 98, and post-only cap 94. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=20; ACTIVE_TARGET_BEFORE_CENTS=NONE. <!-- CITATION-WELD:CW-2edf5adc42cb0c9e:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->

**URS.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAR24GONFAR:(0.523887×0.787671)×(80/80) + KXATPCHALLENGERMATCH-26MAR22PERORT:(0.520424×0.787671)×(79/79) + KXATPCHALLENGERMATCH-26MAR29AVECOS:(0.519450×0.787671)×(85/85) + KXATPCHALLENGERMATCH-26JAN19TORZEB:(0.519172×0.787671)×(78/85) + KXATPCHALLENGERMATCH-26MAR30DUCRUB:(0.518565×0.787671)×(84/84) + KXATPCHALLENGERMATCH-26MAR29TOBALV:(0.516957×0.787671)×(78/85) + KXATPCHALLENGERMATCH-26MAR22DEALV:(0.514711×0.787671)×(85/85)) / 2.861740 = 0.976514067697. Raw round(62×0.976514067697)=61; mass=0.408820059802; blend with lineage 57 gives 59; min(pair cap 98, post-only cap 94) gives 59. Printed action PLACE_REST@59, active-before NONE. <!-- CITATION-WELD:CW-c4beb64c04c476e0:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=7 -->

> At 0.704444 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXATPCHALLENGERMATCH-26MAR24GONFAR@0.523887, KXATPCHALLENGERMATCH-26MAR22PERORT@0.520424, KXATPCHALLENGERMATCH-26MAR29AVECOS@0.519450, KXATPCHALLENGERMATCH-26JAN19TORZEB@0.519172, KXATPCHALLENGERMATCH-26MAR30DUCRUB@0.518565, KXATPCHALLENGERMATCH-26MAR29TOBALV@0.516957, KXATPCHALLENGERMATCH-26MAR22DEALV@0.514711. URS has anchor 62, neighborhood low ratio 0.9765140676973814, lineage target 57, pair cap 98, and post-only cap 94. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=59; ACTIVE_TARGET_BEFORE_CENTS=NONE. <!-- CITATION-WELD:CW-d112a9c6f1c9b5bf:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->

### TP6 — 6.167399 hours from discovery (2026-07-14T09:26:01.636Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

PAL: R-BOOK-PAL#rows-1..2899, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-2899 = 35/41 last NONE; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=PAL,ts<=1784021161.636 (7 rows; last #row-4284 d82f2055-c54c-730c-de31-188fbda671d5@41)

URS: R-BOOK-URS#rows-1..1042, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-1042 = 60/64 last 64; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=URS,ts<=1784021161.636 (3 rows; last #row-4270 f825bd6e-531b-746c-73fe-a6e58079ca5f@64)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"PAL":1,"URS":1},"anchors_cents":{"PAL":38,"URS":62}}` | R-STORY#line-166; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":24}` | R-STORY#line-166; raw cumulative prefixes above |
| drift | `{"PAL":{"current_cents":40,"drift_cents":2},"URS":{"current_cents":64,"drift_cents":2}}` | R-STORY#line-166; raw cumulative prefixes above |
| steps_stillness | `{"PAL":{"step_count":331,"last_step_cents":-3,"still_seconds":0},"URS":{"step_count":9,"last_step_cents":-2,"still_seconds":3069.1640000343323}}` | R-STORY#line-166; raw cumulative prefixes above |
| shape_survival | `{"PAL":{"directional_step_share":0.4984894259818731,"observed_steps":331},"URS":{"directional_step_share":0.6666666666666666,"observed_steps":9}}` | R-STORY#line-166; raw cumulative prefixes above |
| ripeness | `{"PAL":{"continuous_evidence_mass":0.9996572995202193,"observations":2917,"prints":7},"URS":{"continuous_evidence_mass":0.9990448901623686,"observations":1046,"prints":3}}` | R-STORY#line-166; raw cumulative prefixes above |
| lows_travel | `{"PAL":{"low_cents":37,"high_cents":64,"travel_cents":27},"URS":{"low_cents":49,"high_cents":76,"travel_cents":27}}` | R-STORY#line-166; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":104,"spread_sum_cents":10,"dwell_seconds":{"PAL":0,"URS":3069.1640000343323}}` | R-STORY#line-166; raw cumulative prefixes above |
| divots | `{"PAL":{"count":124,"mean_depth_cents":1.0887096774193548,"latest":{"timestamp_epoch":1784021161.637,"receipt":"3e2f45fe-c163-7820-fac9-d005bd79b771","floor_cents":41,"depth_cents":1}},"URS":{"count":0,"mean_depth_cents":null,"latest":null}}` | R-STORY#line-166; raw cumulative prefixes above |
| depth_size | `{"PAL":{"bid_depth_5":1085,"ask_depth_5":933,"bid_share":0.5376610505450942,"top_bid_size":285,"top_ask_size":18},"URS":{"bid_depth_5":850,"ask_depth_5":1278,"bid_share":0.3994360902255639,"top_bid_size":3,"top_ask_size":106}}` | R-STORY#line-166; raw cumulative prefixes above |
| volume | `{"PAL":{"print_count":7,"contracts":224.86},"URS":{"print_count":3,"contracts":26.52}}` | R-STORY#line-166; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.19999999999999996,"drift_sum_cents":4,"both_legs_named":true}` | R-STORY#line-166; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-166; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":6.167399166689979,"hours_to_truth_bell":6.6495452777544655,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-166; raw cumulative prefixes above |
| books | `{"PAL":{"bid_cents":35,"ask_cents":41,"last_trade_cents":null,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-2899"},"URS":{"bid_cents":60,"ask_cents":64,"last_trade_cents":64,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-1042"}}` | R-STORY#line-166; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":2,"legs":{"PAL":{"credited":false,"entry_cents":null,"standing_target_cents":29},"URS":{"credited":false,"entry_cents":null,"standing_target_cents":52}}}` | R-STORY#line-166; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":24,"leg0_anchor_cents":38,"leg1_anchor_cents":62,"leg0_drift_cents":2,"leg1_drift_cents":2,"leg0_travel_cents":27,"leg1_travel_cents":27,"joint_mid_sum_cents":104,"joint_spread_cents":10,"inverse_coherence":0.19999999999999996,"volume_log1p":5.530935888224764,"hours_from_discovery":6.167399166689979,"divot_depth_cents":1.0887096774193548,"oriented_leg_ids":["PAL","URS"]}` [R-STORY#line-166; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26JUN09SHEBRU (26JUN) | 0.879734 / 1.000000 | R-CORPUS#row-3233; RANGE_SPECTRUM_PATH | R-RANGE#row-1381; SHE anchor 39 (tick#1[1780973227,37,39,39]), low 21 (tick#88[1781003977,23,24,21]), close 44 (terminal tick#92[1781005523,34,35,44]); BRU anchor 62 (tick#1[1780973227,61,63,62]), low 50 (tick#84[1781002729,46,47,50]), close 64 (terminal tick#92[1781005523,65,66,64]) |
| N2 | KXATPCHALLENGERMATCH-26JUN22TOBKRU (26JUN) | 0.852905 / 1.000000 | R-CORPUS#row-3687; RANGE_SPECTRUM_PATH | R-RANGE#row-1829; TOB anchor 38 (tick#1[1782113273,36,38,38]), low 32 (tick#70[1782134125,32,38,38]), close 36 (terminal tick#100[1782143718,34,35,36]); KRU anchor 64 (tick#1[1782113273,62,64,64]), low 49 (tick#97[1782142774,50,66,49]), close 64 (terminal tick#100[1782143718,65,66,64]) |
| N3 | KXATPCHALLENGERMATCH-26JUL02COUVAS (26JUL) | 0.852031 / 1.000000 | R-CORPUS#row-2223; RANGE_SPECTRUM_PATH | R-RANGE#row-374; COU anchor 40 (tick#1[1782966699,36,40,40]), low 39 (tick#13[1782970340,37,39,40]), close 41 (terminal tick#98[1782996155,34,40,41]); VAS anchor 64 (tick#1[1782966699,63,64,64]), low 63 (tick#1[1782966699,63,64,64]), close 65 (terminal tick#98[1782996155,51,63,65]) |
| N4 | KXATPCHALLENGERMATCH-26MAY17IANSEL (26MAY) | 0.851744 / 1.000000 | R-CORPUS#row-5676; RANGE_SPECTRUM_PATH | R-RANGE#row-2605; SEL anchor 42 (tick#30[1778984788,36,42,0]), low 28 (tick#107[1779007998,25,32,28]), close 42 (terminal tick#109[1779008606,39,42,42]); IAN anchor 64 (tick#7[1778977857,51,64,0]), low 43 (tick#99[1779005589,43,60,71]), close 59 (terminal tick#109[1779008606,57,64,59]) |
| N5 | KXATPCHALLENGERMATCH-26MAY07TOBMEN (26MAY) | 0.848424 / 1.000000 | R-CORPUS#row-5309; RANGE_SPECTRUM_PATH | R-RANGE#row-2254; TOB anchor 40 (tick#1[1778147193,37,39,40]), low 34 (tick#68[1778167472,34,37,37]), close 37 (terminal tick#113[1778181061,36,37,37]); MEN anchor 63 (tick#1[1778147193,61,63,63]), low 35 (tick#108[1778179550,34,35,35]), close 63 (terminal tick#113[1778181061,63,64,63]) |
| N6 | KXATPCHALLENGERMATCH-26APR28BARFUK (26APR) | 0.847423 / 1.000000 | R-CORPUS#row-579; RANGE_SPECTRUM_PATH | R-RANGE#row-214; FUK anchor 39 (tick#3[1777324778,39,42,0]), low 23 (tick#85[1777353647,20,23,23]), close 45 (terminal tick#87[1777354279,39,44,45]); BAR anchor 61 (tick#1[1777324130,63,66,61]), low 56 (tick#83[1777353035,53,56,56]), close 61 (terminal tick#87[1777354279,56,61,61]) |
| N7 | KXATPCHALLENGERMATCH-26JUN07EVAWAT (26JUN) | 0.847204 / 1.000000 | R-CORPUS#row-3083; RANGE_SPECTRUM_PATH | R-RANGE#row-1232; EVA anchor 40 (tick#1[1780806694,35,39,40]), low 40 (tick#1[1780806694,35,39,40]), close 44 (terminal tick#85[1780836771,31,44,44]); WAT anchor 62 (tick#1[1780806694,63,66,62]), low 56 (tick#42[1780821104,55,56,65]), close 65 (terminal tick#85[1780836771,52,65,65]) |

**Derivation arithmetic → action → verbatim sentence.**

**PAL.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN09SHEBRU:(0.879734×1.000000)×(21/39) + KXATPCHALLENGERMATCH-26JUN22TOBKRU:(0.852905×1.000000)×(32/38) + KXATPCHALLENGERMATCH-26JUL02COUVAS:(0.852031×1.000000)×(39/40) + KXATPCHALLENGERMATCH-26MAY17IANSEL:(0.851744×1.000000)×(28/42) + KXATPCHALLENGERMATCH-26MAY07TOBMEN:(0.848424×1.000000)×(34/40) + KXATPCHALLENGERMATCH-26APR28BARFUK:(0.847423×1.000000)×(23/39) + KXATPCHALLENGERMATCH-26JUN07EVAWAT:(0.847204×1.000000)×(40/40)) / 5.979464 = 0.779104009021. Raw round(38×0.779104009021)=30; mass=0.854209134953; blend with lineage 35 gives 31; min(pair cap 47, post-only cap 40) gives 31. Printed action REPRICE_REST@31, active-before 29. <!-- CITATION-WELD:CW-3fb040721405246a:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=7 -->

> At 6.167399 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXATPCHALLENGERMATCH-26JUN09SHEBRU@0.879734, KXATPCHALLENGERMATCH-26JUN22TOBKRU@0.852905, KXATPCHALLENGERMATCH-26JUL02COUVAS@0.852031, KXATPCHALLENGERMATCH-26MAY17IANSEL@0.851744, KXATPCHALLENGERMATCH-26MAY07TOBMEN@0.848424, KXATPCHALLENGERMATCH-26APR28BARFUK@0.847423, KXATPCHALLENGERMATCH-26JUN07EVAWAT@0.847204. PAL has anchor 38, neighborhood low ratio 0.7791040090205983, lineage target 35, pair cap 47, and post-only cap 40. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=31; ACTIVE_TARGET_BEFORE_CENTS=29. <!-- CITATION-WELD:CW-90b90ca37f650d1b:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->

**URS.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN09SHEBRU:(0.879734×1.000000)×(50/62) + KXATPCHALLENGERMATCH-26JUN22TOBKRU:(0.852905×1.000000)×(49/64) + KXATPCHALLENGERMATCH-26JUL02COUVAS:(0.852031×1.000000)×(63/64) + KXATPCHALLENGERMATCH-26MAY17IANSEL:(0.851744×1.000000)×(43/64) + KXATPCHALLENGERMATCH-26MAY07TOBMEN:(0.848424×1.000000)×(35/63) + KXATPCHALLENGERMATCH-26APR28BARFUK:(0.847423×1.000000)×(56/61) + KXATPCHALLENGERMATCH-26JUN07EVAWAT:(0.847204×1.000000)×(56/62)) / 5.979464 = 0.800736729849. Raw round(62×0.800736729849)=50; mass=0.854209134953; blend with lineage 60 gives 51; min(pair cap 70, post-only cap 63) gives 51. Printed action REPRICE_REST@51, active-before 52. <!-- CITATION-WELD:CW-6b6386f59c3f719b:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=7 -->

> At 6.167399 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXATPCHALLENGERMATCH-26JUN09SHEBRU@0.879734, KXATPCHALLENGERMATCH-26JUN22TOBKRU@0.852905, KXATPCHALLENGERMATCH-26JUL02COUVAS@0.852031, KXATPCHALLENGERMATCH-26MAY17IANSEL@0.851744, KXATPCHALLENGERMATCH-26MAY07TOBMEN@0.848424, KXATPCHALLENGERMATCH-26APR28BARFUK@0.847423, KXATPCHALLENGERMATCH-26JUN07EVAWAT@0.847204. URS has anchor 62, neighborhood low ratio 0.8007367298485394, lineage target 60, pair cap 70, and post-only cap 63. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=51; ACTIVE_TARGET_BEFORE_CENTS=52. <!-- CITATION-WELD:CW-474f2b50273a36f5:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->

### TP9 — 12.024469 hours from discovery (2026-07-14T15:17:27.088Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

PAL: R-BOOK-PAL#rows-1..36472, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-36472 = 40/42 last 44; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=PAL,ts<=1784042247.088 (21 rows; last #row-4330 2e314d90-9f0a-66ef-96ee-30b15ec1cc6d@33)

URS: R-BOOK-URS#rows-1..5940, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-5940 = 59/62 last 62; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=URS,ts<=1784042247.088 (21 rows; last #row-4320 a529177f-2dbf-74ab-6105-8f02b6f6c01b@61)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"PAL":1,"URS":1},"anchors_cents":{"PAL":38,"URS":62}}` | R-STORY#line-184; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":24}` | R-STORY#line-184; raw cumulative prefixes above |
| drift | `{"PAL":{"current_cents":33,"drift_cents":-5},"URS":{"current_cents":61,"drift_cents":-1}}` | R-STORY#line-184; raw cumulative prefixes above |
| steps_stillness | `{"PAL":{"step_count":343,"last_step_cents":-8,"still_seconds":0},"URS":{"step_count":24,"last_step_cents":-1,"still_seconds":607.5039999485016}}` | R-STORY#line-184; raw cumulative prefixes above |
| shape_survival | `{"PAL":{"directional_step_share":0.5014577259475219,"observed_steps":343},"URS":{"directional_step_share":0.4166666666666667,"observed_steps":24}}` | R-STORY#line-184; raw cumulative prefixes above |
| ripeness | `{"PAL":{"continuous_evidence_mass":0.9999725989861625,"observations":36494,"prints":21},"URS":{"continuous_evidence_mass":0.9998322710499832,"observations":5961,"prints":21}}` | R-STORY#line-184; raw cumulative prefixes above |
| lows_travel | `{"PAL":{"low_cents":33,"high_cents":64,"travel_cents":31},"URS":{"low_cents":49,"high_cents":76,"travel_cents":27}}` | R-STORY#line-184; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":94,"spread_sum_cents":5,"dwell_seconds":{"PAL":0,"URS":607.5039999485016}}` | R-STORY#line-184; raw cumulative prefixes above |
| divots | `{"PAL":{"count":128,"mean_depth_cents":1.109375,"latest":{"timestamp_epoch":1784042066.596,"receipt":"11b32855-2577-5868-896c-0afb9e64bb69","floor_cents":39,"depth_cents":2}},"URS":{"count":3,"mean_depth_cents":1.3333333333333333,"latest":{"timestamp_epoch":1784038938,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-5548","floor_cents":61,"depth_cents":1}}}` | R-STORY#line-184; raw cumulative prefixes above |
| depth_size | `{"PAL":{"bid_depth_5":3874,"ask_depth_5":4214,"bid_share":0.47898120672601385,"top_bid_size":5,"top_ask_size":40},"URS":{"bid_depth_5":14915,"ask_depth_5":5257,"bid_share":0.7393912353757683,"top_bid_size":156,"top_ask_size":263}}` | R-STORY#line-184; raw cumulative prefixes above |
| volume | `{"PAL":{"print_count":21,"contracts":754.49},"URS":{"print_count":21,"contracts":572.42}}` | R-STORY#line-184; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.1428571428571429,"drift_sum_cents":-6,"both_legs_named":true}` | R-STORY#line-184; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-184; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":12.024469166662957,"hours_to_truth_bell":0.7924752777814865,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-184; raw cumulative prefixes above |
| books | `{"PAL":{"bid_cents":40,"ask_cents":42,"last_trade_cents":44,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-36472"},"URS":{"bid_cents":59,"ask_cents":62,"last_trade_cents":62,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-5940"}}` | R-STORY#line-184; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":0,"entry_sum_cents":0,"standing_count":2,"legs":{"PAL":{"credited":false,"entry_cents":null,"standing_target_cents":26},"URS":{"credited":false,"entry_cents":null,"standing_target_cents":55}}}` | R-STORY#line-184; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":24,"leg0_anchor_cents":38,"leg1_anchor_cents":62,"leg0_drift_cents":-5,"leg1_drift_cents":-1,"leg0_travel_cents":31,"leg1_travel_cents":27,"joint_mid_sum_cents":94,"joint_spread_cents":5,"inverse_coherence":0.1428571428571429,"volume_log1p":7.191361556655478,"hours_from_discovery":12.024469166662957,"divot_depth_cents":1.2213541666666665,"oriented_leg_ids":["PAL","URS"]}` [R-STORY#line-184; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26JUN09SHEBRU (26JUN) | 0.830492 / 1.000000 | R-CORPUS#row-3233; RANGE_SPECTRUM_PATH | R-RANGE#row-1381; SHE anchor 39 (tick#1[1780973227,37,39,39]), low 21 (tick#88[1781003977,23,24,21]), close 44 (terminal tick#92[1781005523,34,35,44]); BRU anchor 62 (tick#1[1780973227,61,63,62]), low 50 (tick#84[1781002729,46,47,50]), close 64 (terminal tick#92[1781005523,65,66,64]) |
| N2 | KXATPCHALLENGERMATCH-26MAY07TOBMEN (26MAY) | 0.820336 / 1.000000 | R-CORPUS#row-5309; RANGE_SPECTRUM_PATH | R-RANGE#row-2254; TOB anchor 40 (tick#1[1778147193,37,39,40]), low 34 (tick#68[1778167472,34,37,37]), close 37 (terminal tick#113[1778181061,36,37,37]); MEN anchor 63 (tick#1[1778147193,61,63,63]), low 35 (tick#108[1778179550,34,35,35]), close 63 (terminal tick#113[1778181061,63,64,63]) |
| N3 | KXATPCHALLENGERMATCH-26APR28BARFUK (26APR) | 0.818661 / 1.000000 | R-CORPUS#row-579; RANGE_SPECTRUM_PATH | R-RANGE#row-214; FUK anchor 39 (tick#3[1777324778,39,42,0]), low 23 (tick#85[1777353647,20,23,23]), close 45 (terminal tick#87[1777354279,39,44,45]); BAR anchor 61 (tick#1[1777324130,63,66,61]), low 56 (tick#83[1777353035,53,56,56]), close 61 (terminal tick#87[1777354279,56,61,61]) |
| N4 | KXATPCHALLENGERMATCH-26JUN04BERHUS (26JUN) | 0.818583 / 1.000000 | R-CORPUS#row-3007; RANGE_SPECTRUM_PATH | R-RANGE#row-1156; BER anchor 40 (tick#1[1780551098,40,41,40]), low 25 (tick#94[1780582628,23,25,25]), close 39 (terminal tick#95[1780582929,37,39,39]); HUS anchor 61 (tick#1[1780551098,60,61,61]), low 55 (tick#70[1780574355,57,58,55]), close 60 (terminal tick#95[1780582929,60,62,60]) |
| N5 | KXATPCHALLENGERMATCH-26JUN01SEAKRU (26JUN) | 0.816194 / 1.000000 | R-CORPUS#row-2900; RANGE_SPECTRUM_PATH | R-RANGE#row-1049; KRU anchor 38 (tick#1[1780390615,39,42,38]), low 32 (tick#100[1780420667,36,40,32]), close 38 (terminal tick#101[1780420968,34,38,38]); SEA anchor 60 (tick#1[1780390615,58,60,60]), low 50 (tick#99[1780420365,50,52,50]), close 61 (terminal tick#101[1780420968,60,64,61]) |
| N6 | KXATPCHALLENGERMATCH-26JUN22TOBKRU (26JUN) | 0.814888 / 1.000000 | R-CORPUS#row-3687; RANGE_SPECTRUM_PATH | R-RANGE#row-1829; TOB anchor 38 (tick#1[1782113273,36,38,38]), low 32 (tick#70[1782134125,32,38,38]), close 36 (terminal tick#100[1782143718,34,35,36]); KRU anchor 64 (tick#1[1782113273,62,64,64]), low 49 (tick#97[1782142774,50,66,49]), close 64 (terminal tick#100[1782143718,65,66,64]) |
| N7 | KXATPCHALLENGERMATCH-26MAY25BICTOM (26MAY) | 0.810257 / 1.000000 | R-CORPUS#row-5877; RANGE_SPECTRUM_PATH | R-RANGE#row-2797; BIC anchor 39 (tick#1[1779702868,39,43,39]), low 39 (tick#1[1779702868,39,43,39]), close 40 (terminal tick#71[1779736099,39,40,40]); TOM anchor 53 (tick#1[1779702868,55,63,53]), low 30 (tick#66[1779734139,30,31,30]), close 60 (terminal tick#71[1779736099,60,61,60]) |

**Derivation arithmetic → action → verbatim sentence.**

**PAL.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN09SHEBRU:(0.830492×1.000000)×(21/39) + KXATPCHALLENGERMATCH-26MAY07TOBMEN:(0.820336×1.000000)×(34/40) + KXATPCHALLENGERMATCH-26APR28BARFUK:(0.818661×1.000000)×(23/39) + KXATPCHALLENGERMATCH-26JUN04BERHUS:(0.818583×1.000000)×(25/40) + KXATPCHALLENGERMATCH-26JUN01SEAKRU:(0.816194×1.000000)×(32/38) + KXATPCHALLENGERMATCH-26JUN22TOBKRU:(0.814888×1.000000)×(32/38) + KXATPCHALLENGERMATCH-26MAY25BICTOM:(0.810257×1.000000)×(39/39)) / 5.729411 = 0.754473310470. Raw round(38×0.754473310470)=29; mass=0.818487273462; blend with lineage 40 gives 31; min(pair cap 44, post-only cap 41) gives 31. Printed action REPRICE_REST@31, active-before 26. <!-- CITATION-WELD:CW-d9d58a59baba3b86:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=7 -->

> At 12.024469 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXATPCHALLENGERMATCH-26JUN09SHEBRU@0.830492, KXATPCHALLENGERMATCH-26MAY07TOBMEN@0.820336, KXATPCHALLENGERMATCH-26APR28BARFUK@0.818661, KXATPCHALLENGERMATCH-26JUN04BERHUS@0.818583, KXATPCHALLENGERMATCH-26JUN01SEAKRU@0.816194, KXATPCHALLENGERMATCH-26JUN22TOBKRU@0.814888, KXATPCHALLENGERMATCH-26MAY25BICTOM@0.810257. PAL has anchor 38, neighborhood low ratio 0.7544733104702407, lineage target 40, pair cap 44, and post-only cap 41. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=31; ACTIVE_TARGET_BEFORE_CENTS=26. <!-- CITATION-WELD:CW-8976c516e5f4fc98:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->

**URS.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN09SHEBRU:(0.830492×1.000000)×(50/62) + KXATPCHALLENGERMATCH-26MAY07TOBMEN:(0.820336×1.000000)×(35/63) + KXATPCHALLENGERMATCH-26APR28BARFUK:(0.818661×1.000000)×(56/61) + KXATPCHALLENGERMATCH-26JUN04BERHUS:(0.818583×1.000000)×(55/61) + KXATPCHALLENGERMATCH-26JUN01SEAKRU:(0.816194×1.000000)×(50/60) + KXATPCHALLENGERMATCH-26JUN22TOBKRU:(0.814888×1.000000)×(49/64) + KXATPCHALLENGERMATCH-26MAY25BICTOM:(0.810257×1.000000)×(30/53)) / 5.729411 = 0.764095047111. Raw round(62×0.764095047111)=47; mass=0.818487273462; blend with lineage 57 gives 49; min(pair cap 73, post-only cap 61) gives 49. Printed action REPRICE_REST@49, active-before 55. <!-- CITATION-WELD:CW-97e4fa1b3f489d55:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=7 -->

> At 12.024469 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXATPCHALLENGERMATCH-26JUN09SHEBRU@0.830492, KXATPCHALLENGERMATCH-26MAY07TOBMEN@0.820336, KXATPCHALLENGERMATCH-26APR28BARFUK@0.818661, KXATPCHALLENGERMATCH-26JUN04BERHUS@0.818583, KXATPCHALLENGERMATCH-26JUN01SEAKRU@0.816194, KXATPCHALLENGERMATCH-26JUN22TOBKRU@0.814888, KXATPCHALLENGERMATCH-26MAY25BICTOM@0.810257. URS has anchor 62, neighborhood low ratio 0.7640950471114415, lineage target 57, pair cap 73, and post-only cap 61. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=49; ACTIVE_TARGET_BEFORE_CENTS=55. <!-- CITATION-WELD:CW-1ac7e8f03f756741:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->

### TP10 — 12.039239 hours from discovery (2026-07-14T15:18:20.260Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

PAL: R-BOOK-PAL#rows-1..36472, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-36472 = 40/42 last 44; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=PAL,ts<=1784042300.260 (23 rows; last #row-4334 a0ab6a42-90d8-7196-c35d-b04880543fff@31)

URS: R-BOOK-URS#rows-1..5940, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-5940 = 59/62 last 62; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=URS,ts<=1784042300.260 (23 rows; last #row-4333 14e42970-635c-790f-0adb-638624bccd4a@68)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"PAL":1,"URS":1},"anchors_cents":{"PAL":38,"URS":62}}` | R-STORY#line-190; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":24}` | R-STORY#line-190; raw cumulative prefixes above |
| drift | `{"PAL":{"current_cents":31,"drift_cents":-7},"URS":{"current_cents":68,"drift_cents":6}}` | R-STORY#line-190; raw cumulative prefixes above |
| steps_stillness | `{"PAL":{"step_count":344,"last_step_cents":-2,"still_seconds":0},"URS":{"step_count":26,"last_step_cents":1,"still_seconds":0.18600010871887207}}` | R-STORY#line-190; raw cumulative prefixes above |
| shape_survival | `{"PAL":{"directional_step_share":0.502906976744186,"observed_steps":344},"URS":{"directional_step_share":0.6153846153846154,"observed_steps":26}}` | R-STORY#line-190; raw cumulative prefixes above |
| ripeness | `{"PAL":{"continuous_evidence_mass":0.9999726004877113,"observations":36496,"prints":23},"URS":{"continuous_evidence_mass":0.999832327297116,"observations":5963,"prints":23}}` | R-STORY#line-190; raw cumulative prefixes above |
| lows_travel | `{"PAL":{"low_cents":31,"high_cents":64,"travel_cents":33},"URS":{"low_cents":49,"high_cents":76,"travel_cents":27}}` | R-STORY#line-190; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":99,"spread_sum_cents":5,"dwell_seconds":{"PAL":0,"URS":0.18600010871887207}}` | R-STORY#line-190; raw cumulative prefixes above |
| divots | `{"PAL":{"count":128,"mean_depth_cents":1.109375,"latest":{"timestamp_epoch":1784042066.596,"receipt":"11b32855-2577-5868-896c-0afb9e64bb69","floor_cents":39,"depth_cents":2}},"URS":{"count":3,"mean_depth_cents":1.3333333333333333,"latest":{"timestamp_epoch":1784038938,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-5548","floor_cents":61,"depth_cents":1}}}` | R-STORY#line-190; raw cumulative prefixes above |
| depth_size | `{"PAL":{"bid_depth_5":3874,"ask_depth_5":4214,"bid_share":0.47898120672601385,"top_bid_size":5,"top_ask_size":40},"URS":{"bid_depth_5":14915,"ask_depth_5":5257,"bid_share":0.7393912353757683,"top_bid_size":156,"top_ask_size":263}}` | R-STORY#line-190; raw cumulative prefixes above |
| volume | `{"PAL":{"print_count":23,"contracts":778.49},"URS":{"print_count":23,"contracts":643.42}}` | R-STORY#line-190; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.9285714285714286,"drift_sum_cents":-1,"both_legs_named":true}` | R-STORY#line-190; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-190; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":12.03923888888624,"hours_to_truth_bell":0.7777055555582046,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-190; raw cumulative prefixes above |
| books | `{"PAL":{"bid_cents":40,"ask_cents":42,"last_trade_cents":44,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-36472"},"URS":{"bid_cents":59,"ask_cents":62,"last_trade_cents":62,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-5940"}}` | R-STORY#line-190; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":1,"entry_sum_cents":31,"standing_count":1,"legs":{"PAL":{"credited":true,"entry_cents":31,"standing_target_cents":null,"fill_receipt":"a0ab6a42-90d8-7196-c35d-b04880543fff","fill_timestamp_epoch":1784042300.26},"URS":{"credited":false,"entry_cents":null,"standing_target_cents":49}}}` | R-STORY#line-190; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":24,"leg0_anchor_cents":38,"leg1_anchor_cents":62,"leg0_drift_cents":-7,"leg1_drift_cents":6,"leg0_travel_cents":33,"leg1_travel_cents":27,"joint_mid_sum_cents":99,"joint_spread_cents":5,"inverse_coherence":0.9285714285714286,"volume_log1p":7.260459349427716,"hours_from_discovery":12.03923888888624,"divot_depth_cents":1.2213541666666665,"oriented_leg_ids":["PAL","URS"]}` [R-STORY#line-190; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26MAY03CIGMIG (26MAY) | 0.865085 / 1.000000 | R-CORPUS#row-5161; RANGE_SPECTRUM_PATH | R-RANGE#row-2123; CIG anchor 38 (tick#1[1777892660,36,38,38]), low 34 (tick#86[1777918376,34,35,36]), close 35 (terminal tick#95[1777921098,34,35,35]); MIG anchor 61 (tick#1[1777892660,61,63,61]), low 52 (tick#84[1777917773,45,68,52]), close 67 (terminal tick#95[1777921098,64,67,67]) |
| N2 | KXATPCHALLENGERMATCH-26APR28GEEXIL (26APR) | 0.859045 / 1.000000 | R-CORPUS#row-598; RANGE_SPECTRUM_PATH | R-RANGE#row-233; XIL anchor 39 (tick#1[1777382846,38,39,39]), low 32 (tick#74[1777412366,31,32,32]), close 32 (terminal tick#74[1777412366,31,32,32]); GEE anchor 61 (tick#1[1777382846,61,62,61]), low 59 (tick#12[1777386254,57,59,61]), close 69 (terminal tick#74[1777412366,67,69,69]) |
| N3 | KXATPCHALLENGERMATCH-26MAY09LAJKWON (26MAY) | 0.857967 / 1.000000 | R-CORPUS#row-5330; RANGE_SPECTRUM_PATH | R-RANGE#row-2275; LAJ anchor 38 (tick#4[1778282397,38,39,39]), low 21 (tick#101[1778311636,20,21,21]), close 29 (terminal tick#102[1778311938,28,29,29]); KWON anchor 63 (tick#1[1778281493,61,63,63]), low 61 (tick#1[1778281493,61,63,63]), close 72 (terminal tick#102[1778311938,71,72,72]) |
| N4 | KXATPCHALLENGERMATCH-26APR28TRADEJ (26APR) | 0.852126 / 1.000000 | R-CORPUS#row-641; RANGE_SPECTRUM_PATH | R-RANGE#row-271; TRA anchor 37 (tick#1[1777341797,36,37,37]), low 34 (tick#106[1777377945,33,34,34]), close 34 (terminal tick#106[1777377945,33,34,34]); DEJ anchor 62 (tick#1[1777341797,63,64,62]), low 26 (tick#100[1777375785,25,26,26]), close 66 (terminal tick#106[1777377945,66,67,66]) |
| N5 | KXATPCHALLENGERMATCH-26JUN02DURGOM (26JUN) | 0.851822 / 1.000000 | R-CORPUS#row-2935; RANGE_SPECTRUM_PATH | R-RANGE#row-1084; DUR anchor 40 (tick#1[1780383064,40,41,40]), low 29 (tick#108[1780415480,29,30,29]), close 29 (terminal tick#108[1780415480,29,30,29]); GOM anchor 62 (tick#1[1780383064,59,62,62]), low 51 (tick#101[1780413360,50,51,51]), close 71 (terminal tick#108[1780415480,70,71,71]) |
| N6 | KXATPCHALLENGERMATCH-26JUL07MARBER (26JUL) | 0.845249 / 1.000000 | R-CORPUS#row-2467; RANGE_SPECTRUM_PATH | R-RANGE#row-617; MAR anchor 40 (tick#1[1783402413,38,41,40]), low 23 (tick#56[1783432348,24,25,23]), close 31 (terminal tick#58[1783434326,30,31,31]); BER anchor 62 (tick#2[1783403714,59,62,0]), low 61 (tick#1[1783402413,59,61,0]), close 69 (terminal tick#58[1783434326,69,70,69]) |
| N7 | KXATPCHALLENGERMATCH-26MAY14RIEKEC (26MAY) | 0.843956 / 1.000000 | R-CORPUS#row-5622; RANGE_SPECTRUM_PATH | R-RANGE#row-2551; RIE anchor 39 (tick#1[1778720505,37,39,39]), low 34 (tick#81[1778744718,34,37,37]), close 36 (terminal tick#102[1778751065,36,38,36]); KEC anchor 62 (tick#1[1778720505,61,64,62]), low 51 (tick#101[1778750763,46,55,51]), close 64 (terminal tick#102[1778751065,62,63,64]) |

**Derivation arithmetic → action → verbatim sentence.**

**PAL.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAY03CIGMIG:(0.865085×1.000000)×(34/38) + KXATPCHALLENGERMATCH-26APR28GEEXIL:(0.859045×1.000000)×(32/39) + KXATPCHALLENGERMATCH-26MAY09LAJKWON:(0.857967×1.000000)×(21/38) + KXATPCHALLENGERMATCH-26APR28TRADEJ:(0.852126×1.000000)×(34/37) + KXATPCHALLENGERMATCH-26JUN02DURGOM:(0.851822×1.000000)×(29/40) + KXATPCHALLENGERMATCH-26JUL07MARBER:(0.845249×1.000000)×(23/40) + KXATPCHALLENGERMATCH-26MAY14RIEKEC:(0.843956×1.000000)×(34/39)) / 5.975251 = 0.765725434505. Raw round(38×0.765725434505)=29; mass=0.853607333910; blend with lineage 40 gives 31; min(pair cap 50, post-only cap 41) gives 31. Printed action PLACE_REST@31, active-before NONE. <!-- CITATION-WELD:CW-689e8098a0004960:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=7 -->

> At 12.039239 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXATPCHALLENGERMATCH-26MAY03CIGMIG@0.865085, KXATPCHALLENGERMATCH-26APR28GEEXIL@0.859045, KXATPCHALLENGERMATCH-26MAY09LAJKWON@0.857967, KXATPCHALLENGERMATCH-26APR28TRADEJ@0.852126, KXATPCHALLENGERMATCH-26JUN02DURGOM@0.851822, KXATPCHALLENGERMATCH-26JUL07MARBER@0.845249, KXATPCHALLENGERMATCH-26MAY14RIEKEC@0.843956. PAL has anchor 38, neighborhood low ratio 0.7657254345048753, lineage target 40, pair cap 50, and post-only cap 41. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=31; ACTIVE_TARGET_BEFORE_CENTS=NONE. <!-- CITATION-WELD:CW-89c9fcf7ec09c14f:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->

**URS.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26MAY03CIGMIG:(0.865085×1.000000)×(52/61) + KXATPCHALLENGERMATCH-26APR28GEEXIL:(0.859045×1.000000)×(59/61) + KXATPCHALLENGERMATCH-26MAY09LAJKWON:(0.857967×1.000000)×(61/63) + KXATPCHALLENGERMATCH-26APR28TRADEJ:(0.852126×1.000000)×(26/62) + KXATPCHALLENGERMATCH-26JUN02DURGOM:(0.851822×1.000000)×(51/62) + KXATPCHALLENGERMATCH-26JUL07MARBER:(0.845249×1.000000)×(61/62) + KXATPCHALLENGERMATCH-26MAY14RIEKEC:(0.843956×1.000000)×(51/62)) / 5.975251 = 0.833928672951. Raw round(62×0.833928672951)=52; mass=0.853607333910; blend with lineage 57 gives 53; min(pair cap 68, post-only cap 61) gives 53. Printed action REPRICE_REST@53, active-before 49. <!-- CITATION-WELD:CW-088574222b575dad:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=7 -->

> At 12.039239 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXATPCHALLENGERMATCH-26MAY03CIGMIG@0.865085, KXATPCHALLENGERMATCH-26APR28GEEXIL@0.859045, KXATPCHALLENGERMATCH-26MAY09LAJKWON@0.857967, KXATPCHALLENGERMATCH-26APR28TRADEJ@0.852126, KXATPCHALLENGERMATCH-26JUN02DURGOM@0.851822, KXATPCHALLENGERMATCH-26JUL07MARBER@0.845249, KXATPCHALLENGERMATCH-26MAY14RIEKEC@0.843956. URS has anchor 62, neighborhood low ratio 0.8339286729514561, lineage target 57, pair cap 68, and post-only cap 61. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=REPRICE_REST; TARGET_CENTS=53; ACTIVE_TARGET_BEFORE_CENTS=49. <!-- CITATION-WELD:CW-e5d8510bf2ff2285:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->

### TP12 — 12.669913 hours from discovery (2026-07-14T15:56:10.686Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

PAL: R-BOOK-PAL#rows-1..54070, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-54070 = 52/53 last 35; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=PAL,ts<=1784044570.687 (45 rows; last #row-4388 6d620831-524e-56c1-1f4f-b6d03416a401@53)

URS: R-BOOK-URS#rows-1..21127, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-21127 = 47/48 last 73; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=URS,ts<=1784044570.687 (51 rows; last #row-4390 f9f22164-4b85-5d86-6fc8-c0a4c1f2dbc7@46)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"PAL":1,"URS":1},"anchors_cents":{"PAL":38,"URS":62}}` | R-STORY#line-202; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":24}` | R-STORY#line-202; raw cumulative prefixes above |
| drift | `{"PAL":{"current_cents":35,"drift_cents":-3},"URS":{"current_cents":46,"drift_cents":-16}}` | R-STORY#line-202; raw cumulative prefixes above |
| steps_stillness | `{"PAL":{"step_count":370,"last_step_cents":-18,"still_seconds":21.687000036239624},"URS":{"step_count":71,"last_step_cents":-27,"still_seconds":0}}` | R-STORY#line-202; raw cumulative prefixes above |
| shape_survival | `{"PAL":{"directional_step_share":0.4972972972972973,"observed_steps":370},"URS":{"directional_step_share":0.4647887323943662,"observed_steps":71}}` | R-STORY#line-202; raw cumulative prefixes above |
| ripeness | `{"PAL":{"continuous_evidence_mass":0.9999815280035467,"observations":54135,"prints":45},"URS":{"continuous_evidence_mass":0.9999528235127613,"observations":21196,"prints":51}}` | R-STORY#line-202; raw cumulative prefixes above |
| lows_travel | `{"PAL":{"low_cents":30,"high_cents":64,"travel_cents":34},"URS":{"low_cents":46,"high_cents":77,"travel_cents":31}}` | R-STORY#line-202; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":81,"spread_sum_cents":2,"dwell_seconds":{"PAL":21.687000036239624,"URS":0}}` | R-STORY#line-202; raw cumulative prefixes above |
| divots | `{"PAL":{"count":131,"mean_depth_cents":1.1374045801526718,"latest":{"timestamp_epoch":1784044547.237,"receipt":"8248da1b-975f-7969-b998-b48bb5cd79ce","floor_cents":51,"depth_cents":1}},"URS":{"count":12,"mean_depth_cents":4.75,"latest":{"timestamp_epoch":1784043844.848,"receipt":"6edfee41-df09-7745-50ef-b02e576de07b","floor_cents":63,"depth_cents":2}}}` | R-STORY#line-202; raw cumulative prefixes above |
| depth_size | `{"PAL":{"bid_depth_5":34062,"ask_depth_5":58248,"bid_share":0.36899577510562237,"top_bid_size":13164,"top_ask_size":14684},"URS":{"bid_depth_5":23436,"ask_depth_5":35952,"bid_share":0.39462517680339465,"top_bid_size":500,"top_ask_size":14600}}` | R-STORY#line-202; raw cumulative prefixes above |
| volume | `{"PAL":{"print_count":45,"contracts":1128.49},"URS":{"print_count":51,"contracts":1567.11}}` | R-STORY#line-202; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.050000000000000044,"drift_sum_cents":-19,"both_legs_named":true}` | R-STORY#line-202; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-202; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":12.669913055565623,"hours_to_truth_bell":0.14703138887882233,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-202; raw cumulative prefixes above |
| books | `{"PAL":{"bid_cents":52,"ask_cents":53,"last_trade_cents":35,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-54070"},"URS":{"bid_cents":47,"ask_cents":48,"last_trade_cents":73,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-21127"}}` | R-STORY#line-202; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":2,"entry_sum_cents":77,"standing_count":0,"legs":{"PAL":{"credited":true,"entry_cents":31,"standing_target_cents":null,"fill_receipt":"a0ab6a42-90d8-7196-c35d-b04880543fff","fill_timestamp_epoch":1784042300.26},"URS":{"credited":true,"entry_cents":46,"standing_target_cents":null,"fill_receipt":"f9f22164-4b85-5d86-6fc8-c0a4c1f2dbc7","fill_timestamp_epoch":1784044570.687}}}` | R-STORY#line-202; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":24,"leg0_anchor_cents":38,"leg1_anchor_cents":62,"leg0_drift_cents":-3,"leg1_drift_cents":-16,"leg0_travel_cents":34,"leg1_travel_cents":31,"joint_mid_sum_cents":81,"joint_spread_cents":2,"inverse_coherence":0.050000000000000044,"volume_log1p":7.899746999199974,"hours_from_discovery":12.669913055565623,"divot_depth_cents":2.943702290076336,"oriented_leg_ids":["PAL","URS"]}` [R-STORY#line-202; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26JUN16PARROD (26JUN) | 0.704110 / 1.000000 | R-CORPUS#row-3516; RANGE_SPECTRUM_PATH | R-RANGE#row-1659; PAR anchor 38 (tick#1[1781607869,36,41,38]), low 38 (tick#1[1781607869,36,41,38]), close 38 (terminal tick#75[1781637335,37,41,38]); ROD anchor 62 (tick#1[1781607869,57,62,62]), low 51 (tick#49[1781626913,50,51,53]), close 55 (terminal tick#75[1781637335,60,63,55]) |
| N2 | KXATPCHALLENGERMATCH-26MAY25BICTOM (26MAY) | 0.702710 / 1.000000 | R-CORPUS#row-5877; RANGE_SPECTRUM_PATH | R-RANGE#row-2797; BIC anchor 39 (tick#1[1779702868,39,43,39]), low 39 (tick#1[1779702868,39,43,39]), close 40 (terminal tick#71[1779736099,39,40,40]); TOM anchor 53 (tick#1[1779702868,55,63,53]), low 30 (tick#66[1779734139,30,31,30]), close 60 (terminal tick#71[1779736099,60,61,60]) |
| N3 | KXATPCHALLENGERMATCH-26JUL05HIGZHU (26JUL) | 0.693792 / 1.000000 | R-CORPUS#row-2294; RANGE_SPECTRUM_PATH | R-RANGE#row-445; HIG anchor 40 (tick#1[1783237108,40,42,40]), low 38 (tick#16[1783244976,38,41,40]), close 41 (terminal tick#59[1783267211,51,55,41]); ZHU anchor 60 (tick#1[1783237108,57,59,60]), low 45 (tick#59[1783267211,44,48,45]), close 45 (terminal tick#59[1783267211,44,48,45]) |
| N4 | KXATPCHALLENGERMATCH-26MAY07TOBMEN (26MAY) | 0.689551 / 1.000000 | R-CORPUS#row-5309; RANGE_SPECTRUM_PATH | R-RANGE#row-2254; TOB anchor 40 (tick#1[1778147193,37,39,40]), low 34 (tick#68[1778167472,34,37,37]), close 37 (terminal tick#113[1778181061,36,37,37]); MEN anchor 63 (tick#1[1778147193,61,63,63]), low 35 (tick#108[1778179550,34,35,35]), close 63 (terminal tick#113[1778181061,63,64,63]) |
| N5 | KXATPCHALLENGERMATCH-26APR28BARFUK (26APR) | 0.685008 / 1.000000 | R-CORPUS#row-579; RANGE_SPECTRUM_PATH | R-RANGE#row-214; FUK anchor 39 (tick#3[1777324778,39,42,0]), low 23 (tick#85[1777353647,20,23,23]), close 45 (terminal tick#87[1777354279,39,44,45]); BAR anchor 61 (tick#1[1777324130,63,66,61]), low 56 (tick#83[1777353035,53,56,56]), close 61 (terminal tick#87[1777354279,56,61,61]) |
| N6 | KXATPCHALLENGERMATCH-26JUL12KARMAR (26JUL) | 0.684633 / 1.000000 | R-CORPUS#row-2651; RANGE_SPECTRUM_PATH | R-RANGE#row-801; KAR anchor 34 (tick#1[1783861542,41,42,34]), low 34 (tick#1[1783861542,41,42,34]), close 54 (terminal tick#64[1783891658,50,54,54]); MAR anchor 59 (tick#1[1783861542,58,59,59]), low 44 (tick#64[1783891658,45,49,44]), close 44 (terminal tick#64[1783891658,45,49,44]) |
| N7 | KXATPCHALLENGERMATCH-26JUN09SHEBRU (26JUN) | 0.684168 / 1.000000 | R-CORPUS#row-3233; RANGE_SPECTRUM_PATH | R-RANGE#row-1381; SHE anchor 39 (tick#1[1780973227,37,39,39]), low 21 (tick#88[1781003977,23,24,21]), close 44 (terminal tick#92[1781005523,34,35,44]); BRU anchor 62 (tick#1[1780973227,61,63,62]), low 50 (tick#84[1781002729,46,47,50]), close 64 (terminal tick#92[1781005523,65,66,64]) |

**Derivation arithmetic → action → verbatim sentence.**

**PAL.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN16PARROD:(0.704110×1.000000)×(38/38) + KXATPCHALLENGERMATCH-26MAY25BICTOM:(0.702710×1.000000)×(39/39) + KXATPCHALLENGERMATCH-26JUL05HIGZHU:(0.693792×1.000000)×(38/40) + KXATPCHALLENGERMATCH-26MAY07TOBMEN:(0.689551×1.000000)×(34/40) + KXATPCHALLENGERMATCH-26APR28BARFUK:(0.685008×1.000000)×(23/39) + KXATPCHALLENGERMATCH-26JUL12KARMAR:(0.684633×1.000000)×(34/34) + KXATPCHALLENGERMATCH-26JUN09SHEBRU:(0.684168×1.000000)×(21/39)) / 4.843972 = 0.848281306861. Raw round(38×0.848281306861)=32; mass=0.691995971572; blend with lineage 40 gives 34; min(pair cap 53, post-only cap 52) gives 34. Printed action PLACE_REST@34, active-before NONE. <!-- CITATION-WELD:CW-4b599f4872d310e7:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=7 -->

> At 12.669913 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXATPCHALLENGERMATCH-26JUN16PARROD@0.704110, KXATPCHALLENGERMATCH-26MAY25BICTOM@0.702710, KXATPCHALLENGERMATCH-26JUL05HIGZHU@0.693792, KXATPCHALLENGERMATCH-26MAY07TOBMEN@0.689551, KXATPCHALLENGERMATCH-26APR28BARFUK@0.685008, KXATPCHALLENGERMATCH-26JUL12KARMAR@0.684633, KXATPCHALLENGERMATCH-26JUN09SHEBRU@0.684168. PAL has anchor 38, neighborhood low ratio 0.8482813068614764, lineage target 40, pair cap 53, and post-only cap 52. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=34; ACTIVE_TARGET_BEFORE_CENTS=NONE. <!-- CITATION-WELD:CW-f2bbaa956bc32375:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->

**URS.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN16PARROD:(0.704110×1.000000)×(51/62) + KXATPCHALLENGERMATCH-26MAY25BICTOM:(0.702710×1.000000)×(30/53) + KXATPCHALLENGERMATCH-26JUL05HIGZHU:(0.693792×1.000000)×(45/60) + KXATPCHALLENGERMATCH-26MAY07TOBMEN:(0.689551×1.000000)×(35/63) + KXATPCHALLENGERMATCH-26APR28BARFUK:(0.685008×1.000000)×(56/61) + KXATPCHALLENGERMATCH-26JUL12KARMAR:(0.684633×1.000000)×(44/59) + KXATPCHALLENGERMATCH-26JUN09SHEBRU:(0.684168×1.000000)×(50/62)) / 4.843972 = 0.737320008859. Raw round(62×0.737320008859)=46; mass=0.691995971572; blend with lineage 57 gives 49; min(pair cap 68, post-only cap 47) gives 47. Printed action PLACE_REST@47, active-before NONE. <!-- CITATION-WELD:CW-ca48f94e7ed36e09:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=7 -->

> At 12.669913 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXATPCHALLENGERMATCH-26JUN16PARROD@0.704110, KXATPCHALLENGERMATCH-26MAY25BICTOM@0.702710, KXATPCHALLENGERMATCH-26JUL05HIGZHU@0.693792, KXATPCHALLENGERMATCH-26MAY07TOBMEN@0.689551, KXATPCHALLENGERMATCH-26APR28BARFUK@0.685008, KXATPCHALLENGERMATCH-26JUL12KARMAR@0.684633, KXATPCHALLENGERMATCH-26JUN09SHEBRU@0.684168. URS has anchor 62, neighborhood low ratio 0.7373200088592653, lineage target 57, pair cap 68, and post-only cap 47. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=47; ACTIVE_TARGET_BEFORE_CENTS=NONE. <!-- CITATION-WELD:CW-4f31135569aaac15:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->

### TP23 — 12.816944 hours from discovery (2026-07-14T16:04:59.998Z)

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

PAL: R-BOOK-PAL#rows-1..57990, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-57990 = 72/74 last 70; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=PAL,ts<=1784045099.998 (49 rows; last #row-4397 f4d14a23-7aa3-689f-56e9-d54efd68f04e@70)

URS: R-BOOK-URS#rows-1..25115, terminal KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-25115 = 26/28 last 28; R-PRINTS predicate event=KXATPCHALLENGERMATCH-26JUL14URSPAL,leg=URS,ts<=1784045099.998 (62 rows; last #row-4406 6de22134-fc2a-784a-f36c-b8bec0d6c5b8@28)

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
| anchor_settle | `{"formation_progress":{"PAL":1,"URS":1},"anchors_cents":{"PAL":38,"URS":62}}` | R-STORY#line-268; raw cumulative prefixes above |
| opening_split | `{"sum_cents":100,"absolute_split_cents":24}` | R-STORY#line-268; raw cumulative prefixes above |
| drift | `{"PAL":{"current_cents":70,"drift_cents":32},"URS":{"current_cents":28,"drift_cents":-34}}` | R-STORY#line-268; raw cumulative prefixes above |
| steps_stillness | `{"PAL":{"step_count":382,"last_step_cents":7,"still_seconds":270},"URS":{"step_count":92,"last_step_cents":-3,"still_seconds":106}}` | R-STORY#line-268; raw cumulative prefixes above |
| shape_survival | `{"PAL":{"directional_step_share":0.5052356020942408,"observed_steps":382},"URS":{"directional_step_share":0.4891304347826087,"observed_steps":92}}` | R-STORY#line-268; raw cumulative prefixes above |
| ripeness | `{"PAL":{"continuous_evidence_mass":0.9999827785144747,"observations":58066,"prints":49},"URS":{"continuous_evidence_mass":0.999960319034959,"observations":25200,"prints":62}}` | R-STORY#line-268; raw cumulative prefixes above |
| lows_travel | `{"PAL":{"low_cents":30,"high_cents":70,"travel_cents":40},"URS":{"low_cents":28,"high_cents":77,"travel_cents":49}}` | R-STORY#line-268; raw cumulative prefixes above |
| joint_state_spread_dwell | `{"mid_sum_cents":98,"spread_sum_cents":4,"dwell_seconds":{"PAL":270,"URS":106}}` | R-STORY#line-268; raw cumulative prefixes above |
| divots | `{"PAL":{"count":131,"mean_depth_cents":1.1374045801526718,"latest":{"timestamp_epoch":1784044547.237,"receipt":"8248da1b-975f-7969-b998-b48bb5cd79ce","floor_cents":51,"depth_cents":1}},"URS":{"count":15,"mean_depth_cents":5.333333333333333,"latest":{"timestamp_epoch":1784044799.196,"receipt":"a90f69c9-9a9e-5b40-bd39-3254c6a7faeb","floor_cents":31,"depth_cents":7}}}` | R-STORY#line-268; raw cumulative prefixes above |
| depth_size | `{"PAL":{"bid_depth_5":25185,"ask_depth_5":22331,"bid_share":0.5300319892246822,"top_bid_size":123,"top_ask_size":100},"URS":{"bid_depth_5":15369,"ask_depth_5":22323,"bid_share":0.4077523081821076,"top_bid_size":124,"top_ask_size":3177}}` | R-STORY#line-268; raw cumulative prefixes above |
| volume | `{"PAL":{"print_count":49,"contracts":1164.49},"URS":{"print_count":62,"contracts":2787.1099999999997}}` | R-STORY#line-268; raw cumulative prefixes above |
| sibling_state | `{"inverse_coherence":0.9701492537313433,"drift_sum_cents":-2,"both_legs_named":true}` | R-STORY#line-268; raw cumulative prefixes above |
| category | `{"category":"ATP_CHALL"}` | R-STORY#line-268; raw cumulative prefixes above |
| time_in_window | `{"hours_from_discovery":12.816944444444445,"hours_to_truth_bell":0,"bell_source":"TAPE_INFERENCE"}` | R-STORY#line-268; raw cumulative prefixes above |
| books | `{"PAL":{"bid_cents":72,"ask_cents":74,"last_trade_cents":70,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-PAL.csv.gz#row-57990"},"URS":{"bid_cents":26,"ask_cents":28,"last_trade_cents":28,"receipt":"KXATPCHALLENGERMATCH-26JUL14URSPAL-URS.csv.gz#row-25115"}}` | R-STORY#line-268; raw cumulative prefixes above |
| half_pair_state | `{"credited_count":2,"entry_sum_cents":77,"standing_count":0,"legs":{"PAL":{"credited":true,"entry_cents":31,"standing_target_cents":null,"fill_receipt":"a0ab6a42-90d8-7196-c35d-b04880543fff","fill_timestamp_epoch":1784042300.26},"URS":{"credited":true,"entry_cents":46,"standing_target_cents":null,"fill_receipt":"f9f22164-4b85-5d86-6fc8-c0a4c1f2dbc7","fill_timestamp_epoch":1784044570.687}}}` | R-STORY#line-268; raw cumulative prefixes above |

**Fingerprint.** `{"category":"ATP_CHALL","anchor_split_cents":24,"leg0_anchor_cents":38,"leg1_anchor_cents":62,"leg0_drift_cents":32,"leg1_drift_cents":-34,"leg0_travel_cents":40,"leg1_travel_cents":49,"joint_mid_sum_cents":98,"joint_spread_cents":4,"inverse_coherence":0.9701492537313433,"volume_log1p":8.282128869206334,"hours_from_discovery":12.816944444444445,"divot_depth_cents":3.2353689567430024,"oriented_leg_ids":["PAL","URS"]}` [R-STORY#line-268; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |
|---|---|---:|---|---|
| N1 | KXATPCHALLENGERMATCH-26JUN04CHOMIK (26JUN) | 0.846901 / 1.000000 | R-CORPUS#row-3011; RANGE_SPECTRUM_PATH | R-RANGE#row-1160; MIK anchor 38 (tick#1[1780538576,37,38,38]), low 36 (tick#35[1780550194,36,37,37]), close 69 (terminal tick#93[1780569411,68,70,69]); CHO anchor 63 (tick#1[1780538576,62,63,63]), low 31 (tick#93[1780569411,30,31,31]), close 31 (terminal tick#93[1780569411,30,31,31]) |
| N2 | KXATPCHALLENGERMATCH-26JUN01LAJRIE (26JUN) | 0.843725 / 1.000000 | R-CORPUS#row-2885; RANGE_SPECTRUM_PATH | R-RANGE#row-1034; LAJ anchor 36 (tick#1[1780363971,36,38,36]), low 33 (tick#99[1780393638,33,34,33]), close 65 (terminal tick#106[1780395749,65,66,65]); RIE anchor 64 (tick#1[1780363971,62,64,64]), low 26 (tick#105[1780395447,26,27,26]), close 35 (terminal tick#106[1780395749,34,35,35]) |
| N3 | KXATPCHALLENGERMATCH-26JUN22MARRAD (26JUN) | 0.836630 / 1.000000 | R-CORPUS#row-3675; RANGE_SPECTRUM_PATH | R-RANGE#row-1818; MAR anchor 37 (tick#96[1782140587,35,37,37]), low 37 (tick#96[1782140587,35,37,37]), close 79 (terminal tick#105[1782143718,78,79,79]); RAD anchor 59 (tick#1[1782111764,58,59,59]), low 21 (tick#105[1782143718,21,22,21]), close 21 (terminal tick#105[1782143718,21,22,21]) |
| N4 | KXATPCHALLENGERMATCH-26JUN27BALNAG (26JUN) | 0.832710 / 1.000000 | R-CORPUS#row-3767; RANGE_SPECTRUM_PATH | R-RANGE#row-1906; NAG anchor 37 (tick#1[1782537887,35,37,37]), low 29 (tick#101[1782568382,26,28,29]), close 69 (terminal tick#107[1782570193,68,69,69]); BAL anchor 66 (tick#1[1782537887,64,66,66]), low 31 (tick#107[1782570193,30,31,31]), close 31 (terminal tick#107[1782570193,30,31,31]) |
| N5 | KXATPCHALLENGERMATCH-26JUL14BICMIY (26JUL) | 0.832148 / 1.000000 | R-CORPUS#row-2741; RANGE_SPECTRUM_PATH | R-RANGE#row-891; BIC anchor 41 (tick#5[1784022712,37,40,41]), low 39 (tick#8[1784023950,38,39,41]), close 76 (terminal tick#60[1784053580,74,75,76]); MIY anchor 61 (tick#1[1784020810,60,61,61]), low 23 (tick#57[1784052285,22,23,23]), close 26 (terminal tick#60[1784053580,25,26,26]) |
| N6 | KXATPCHALLENGERMATCH-26APR27DHABEL (26APR) | 0.830363 / 1.000000 | R-CORPUS#row-523; RANGE_SPECTRUM_PATH | R-RANGE#row-163; BEL anchor 36 (tick#1[1777258097,34,36,36]), low 16 (tick#104[1777290238,16,19,18]), close 67 (terminal tick#121[1777295575,65,66,67]); DHA anchor 63 (tick#1[1777258097,63,65,63]), low 27 (tick#121[1777295575,34,35,27]), close 27 (terminal tick#121[1777295575,34,35,27]) |
| N7 | KXATPCHALLENGERMATCH-26MAY14BLACLA (26MAY) | 0.830227 / 1.000000 | R-CORPUS#row-5595; RANGE_SPECTRUM_PATH | R-RANGE#row-2524; BLA anchor 41 (tick#1[1778724131,39,41,41]), low 40 (tick#13[1778727781,38,40,41]), close 76 (terminal tick#104[1778755294,75,76,76]); CLA anchor 61 (tick#1[1778724131,59,61,61]), low 20 (tick#103[1778754993,19,20,20]), close 24 (terminal tick#104[1778755294,23,24,24]) |

**Derivation arithmetic → action → verbatim sentence.**

**PAL.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN04CHOMIK:(0.846901×1.000000)×(36/38) + KXATPCHALLENGERMATCH-26JUN01LAJRIE:(0.843725×1.000000)×(33/36) + KXATPCHALLENGERMATCH-26JUN22MARRAD:(0.836630×1.000000)×(37/37) + KXATPCHALLENGERMATCH-26JUN27BALNAG:(0.832710×1.000000)×(29/37) + KXATPCHALLENGERMATCH-26JUL14BICMIY:(0.832148×1.000000)×(39/41) + KXATPCHALLENGERMATCH-26APR27DHABEL:(0.830363×1.000000)×(16/36) + KXATPCHALLENGERMATCH-26MAY14BLACLA:(0.830227×1.000000)×(40/41)) / 5.852704 = 0.860391995390. Raw round(38×0.860391995390)=33; mass=0.836100628342; blend with lineage 40 gives 34; min(pair cap 53, post-only cap 73) gives 34. Printed action PLACE_REST@34, active-before NONE. <!-- CITATION-WELD:CW-3a71277e0148affa:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=7 -->

> At 12.816944 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXATPCHALLENGERMATCH-26JUN04CHOMIK@0.846901, KXATPCHALLENGERMATCH-26JUN01LAJRIE@0.843725, KXATPCHALLENGERMATCH-26JUN22MARRAD@0.836630, KXATPCHALLENGERMATCH-26JUN27BALNAG@0.832710, KXATPCHALLENGERMATCH-26JUL14BICMIY@0.832148, KXATPCHALLENGERMATCH-26APR27DHABEL@0.830363, KXATPCHALLENGERMATCH-26MAY14BLACLA@0.830227. PAL has anchor 38, neighborhood low ratio 0.8603919953902233, lineage target 40, pair cap 53, and post-only cap 73. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=34; ACTIVE_TARGET_BEFORE_CENTS=NONE. <!-- CITATION-WELD:CW-eaf44fad3f5af396:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->

**URS.** Σweighted-ratio / Σweight = (KXATPCHALLENGERMATCH-26JUN04CHOMIK:(0.846901×1.000000)×(31/63) + KXATPCHALLENGERMATCH-26JUN01LAJRIE:(0.843725×1.000000)×(26/64) + KXATPCHALLENGERMATCH-26JUN22MARRAD:(0.836630×1.000000)×(21/59) + KXATPCHALLENGERMATCH-26JUN27BALNAG:(0.832710×1.000000)×(31/66) + KXATPCHALLENGERMATCH-26JUL14BICMIY:(0.832148×1.000000)×(23/61) + KXATPCHALLENGERMATCH-26APR27DHABEL:(0.830363×1.000000)×(27/63) + KXATPCHALLENGERMATCH-26MAY14BLACLA:(0.830227×1.000000)×(20/61)) / 5.852704 = 0.408398139766. Raw round(62×0.408398139766)=25; mass=0.836100628342; blend with lineage 57 gives 30; min(pair cap 68, post-only cap 27) gives 27. Printed action PLACE_REST@27, active-before NONE. <!-- CITATION-WELD:CW-6e0049d6010eb2a6:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=7 -->

> At 12.816944 hours from discovery, all sixteen readers fired for KXATPCHALLENGERMATCH-26JUL14URSPAL. The named neighborhood is KXATPCHALLENGERMATCH-26JUN04CHOMIK@0.846901, KXATPCHALLENGERMATCH-26JUN01LAJRIE@0.843725, KXATPCHALLENGERMATCH-26JUN22MARRAD@0.836630, KXATPCHALLENGERMATCH-26JUN27BALNAG@0.832710, KXATPCHALLENGERMATCH-26JUL14BICMIY@0.832148, KXATPCHALLENGERMATCH-26APR27DHABEL@0.830363, KXATPCHALLENGERMATCH-26MAY14BLACLA@0.830227. URS has anchor 62, neighborhood low ratio 0.4083981397658032, lineage target 57, pair cap 68, and post-only cap 27. Resources consulted: CORPUS_CENSUS, HISTORICAL_EVENTS_MATERIALIZATION, CORPUS_EVENTS_V2, RANGE_SPECTRUM_V1, SUBSECOND_STORE, DO_SPACES_TICKS, DO_SPACES_TRADES, DO_SPACES_WS_DEPTH, EXTERNAL_CUSTODY_DUAL_BOOK, EXTERNAL_CUSTODY_DEPTH_RECORDER, EXTERNAL_CUSTODY_TRUE_PRINTS, BOOKMAKER_ODDS_STORE, MACRO_PROJECTION_DB, SHAPE_TAXONOMY_E269779B, FLOOR_DEPTH_8AB4F2D9, RIPENESS_41C1F724, TRUTH_TABLE_C0056976, HONEST_PAIR_FLOOR_TIMING, HONEST_DIVOT_ARRIVAL. ACTION=PLACE_REST; TARGET_CENTS=27; ACTIVE_TARGET_BEFORE_CENTS=NONE. <!-- CITATION-WELD:CW-31c5a1d7502e7113:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=26 -->


## 3. Capture vs ceiling

Status: **PROVISIONAL_UNTIL_CC_RULES_BELL**. L11 bell 1784045100 from TAPE_INFERENCE; this explanation does not alter it.

| Side | Deepest lawful print | Moment | Receipt | Captured | Gap to ceiling |
|---|---:|---|---|---:|---:|
| PAL | 30 | 11.345629 h after formation; 2026-07-14T15:18:59.263Z | R-PRINTS#row-4335; cd48d559-68f1-5b3d-a8e4-d3c3fc43401e | 31 | 1 |
| URS | 28 | 12.061707 h after formation; 2026-07-14T16:01:57.146Z | R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 | 46 | 18 |

Pair ceiling: 58¢, discount 42¢. Captured pair: 77, discount 23. Per-side minima need not be simultaneous; this is the deepest standing-rest opportunity each side's tape actually offered.

## 4. The surprise and humility ledger

### Every receipt-defined neighborhood-range departure

Audit convention: because pass 1 emitted no prediction interval, the expected range is the minimum-to-maximum normalized low of its seven named neighbors, mapped onto the target anchor. Every pass-1 stage whose later lawful true-print minimum left that envelope is listed; this is an explanation metric, not a model change.

| Stage | Side | Neighbor-low prediction | Realized | Departure | Realization receipt |
|---:|---|---:|---:|---:|---|
| 1 @ 0.000000h | URS | 39.37..62.00 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 11.37¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 2 @ 0.704444h | PAL | 0.66..0.78 | 30 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 29.22¢ | 2026-07-14T16:05:00.000Z; R-PRINTS#row-4335; cd48d559-68f1-5b3d-a8e4-d3c3fc43401e |
| 2 @ 0.704444h | URS | 56.89..62.00 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 28.89¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 3 @ 1.927276h | URS | 31.49..56.45 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 3.49¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 4 @ 2.986944h | URS | 31.49..56.45 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 3.49¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 5 @ 5.999722h | URS | 31.49..61.02 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 3.49¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 6 @ 6.167399h | URS | 34.44..61.03 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 6.44¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 7 @ 8.996667h | URS | 49.21..59.00 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 21.21¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 8 @ 11.985983h | URS | 47.47..60.06 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 19.47¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 9 @ 12.024469h | URS | 34.44..56.92 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 6.44¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 11 @ 12.663132h | PAL | 15.83..38.00 | 51 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 13.00¢ | 2026-07-14T16:05:00.000Z; R-PRINTS#row-4385; 71152ddf-a1c7-501d-5336-9d0540a73c82 |
| 11 @ 12.663132h | URS | 30.03..56.19 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 2.03¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 12 @ 12.669913h | PAL | 20.46..38.00 | 63 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 25.00¢ | 2026-07-14T16:05:00.000Z; R-PRINTS#row-4391; 0814e0fb-8801-57c8-7bd7-d01ed8c02352 |
| 12 @ 12.669913h | URS | 34.44..56.92 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 6.44¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 13 @ 12.670000h | PAL | 5.91..36.00 | 63 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 27.00¢ | 2026-07-14T16:05:00.000Z; R-PRINTS#row-4391; 0814e0fb-8801-57c8-7bd7-d01ed8c02352 |
| 13 @ 12.670000h | URS | 30.51..57.00 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 2.51¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 14 @ 12.671940h | PAL | 20.46..38.00 | 63 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 25.00¢ | 2026-07-14T16:05:00.000Z; R-PRINTS#row-4393; 2e220830-cad1-44a3-72f0-9552b9019c3e |
| 14 @ 12.671940h | URS | 33.07..61.02 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 5.07¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 15 @ 12.671944h | PAL | 16.15..36.00 | 63 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 27.00¢ | 2026-07-14T16:05:00.000Z; R-PRINTS#row-4393; 2e220830-cad1-44a3-72f0-9552b9019c3e |
| 15 @ 12.671944h | URS | 30.51..57.00 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 2.51¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 16 @ 12.673611h | PAL | 16.15..32.30 | 63 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 30.70¢ | 2026-07-14T16:05:00.000Z; R-PRINTS#row-4393; 2e220830-cad1-44a3-72f0-9552b9019c3e |
| 16 @ 12.673611h | URS | 30.51..61.07 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 2.51¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 17 @ 12.675315h | PAL | 25.33..38.00 | 63 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 25.00¢ | 2026-07-14T16:05:00.000Z; R-PRINTS#row-4393; 2e220830-cad1-44a3-72f0-9552b9019c3e |
| 17 @ 12.675315h | URS | 32.48..51.00 | 28 | DEEPER_THAN_ALL_NEIGHBORS by 4.48¢ | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 18 @ 12.677678h | PAL | 20.54..38.00 | 68 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 30.00¢ | 2026-07-14T16:05:00.000Z; R-PRINTS#row-4395; 3a8a52a9-646f-50b5-18e6-eca418ed356f |
| 19 @ 12.677778h | PAL | 25.33..38.00 | 68 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 30.00¢ | 2026-07-14T16:05:00.000Z; R-PRINTS#row-4395; 3a8a52a9-646f-50b5-18e6-eca418ed356f |
| 20 @ 12.678889h | PAL | 25.33..38.00 | 68 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 30.00¢ | 2026-07-14T16:05:00.000Z; R-PRINTS#row-4395; 3a8a52a9-646f-50b5-18e6-eca418ed356f |
| 21 @ 12.733388h | PAL | 24.36..38.00 | 70 | SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL by 32.00¢ | 2026-07-14T16:05:00.000Z; R-PRINTS#row-4397; f4d14a23-7aa3-689f-56e9-d54efd68f04e |

### Every decision hindsight beats

A decision is listed when a later formation-lawful true print proves a different rest would have captured closer to the per-side ceiling, or when a credited leg still receives a new action sentence. This is hindsight, never a claim that the future row was knowable.

| Stage | Side | Printed decision | Hindsight-better action | Reading that could have licensed it | Realized receipt / defect |
|---:|---|---|---|---|---|
| 2 @ 0.704444h | PAL | PLACE_REST@20 | REST@30 | NONE IN THE SIXTEEN — HINDSIGHT ONLY | 2026-07-14T15:18:59.263Z; R-PRINTS#row-4335; cd48d559-68f1-5b3d-a8e4-d3c3fc43401e |
| 2 @ 0.704444h | URS | PLACE_REST@59 | REST@28 | NONE IN THE SIXTEEN — HINDSIGHT ONLY | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 3 @ 1.927276h | PAL | REPRICE_REST@28 | REST@30 | neighborhood low envelope 14.78..35.15 | 2026-07-14T15:18:59.263Z; R-PRINTS#row-4335; cd48d559-68f1-5b3d-a8e4-d3c3fc43401e |
| 3 @ 1.927276h | URS | REPRICE_REST@49 | REST@28 | NONE IN THE SIXTEEN — HINDSIGHT ONLY | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 4 @ 2.986944h | PAL | HOLD_REST@28 | REST@30 | neighborhood low envelope 14.78..35.15 | 2026-07-14T15:18:59.263Z; R-PRINTS#row-4335; cd48d559-68f1-5b3d-a8e4-d3c3fc43401e |
| 4 @ 2.986944h | URS | HOLD_REST@49 | REST@28 | NONE IN THE SIXTEEN — HINDSIGHT ONLY | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 5 @ 5.999722h | PAL | REPRICE_REST@29 | REST@30 | neighborhood low envelope 20.46..35.15 | 2026-07-14T15:18:59.263Z; R-PRINTS#row-4335; cd48d559-68f1-5b3d-a8e4-d3c3fc43401e |
| 5 @ 5.999722h | URS | REPRICE_REST@52 | REST@28 | NONE IN THE SIXTEEN — HINDSIGHT ONLY | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 6 @ 6.167399h | PAL | REPRICE_REST@31 | REST@30 | neighborhood low envelope 20.46..38.00 | 2026-07-14T15:18:59.263Z; R-PRINTS#row-4335; cd48d559-68f1-5b3d-a8e4-d3c3fc43401e |
| 6 @ 6.167399h | URS | REPRICE_REST@51 | REST@28 | NONE IN THE SIXTEEN — HINDSIGHT ONLY | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 7 @ 8.996667h | PAL | REPRICE_REST@28 | REST@30 | neighborhood low envelope 15.83..38.00 | 2026-07-14T15:18:59.263Z; R-PRINTS#row-4335; cd48d559-68f1-5b3d-a8e4-d3c3fc43401e |
| 7 @ 8.996667h | URS | REPRICE_REST@55 | REST@28 | NONE IN THE SIXTEEN — HINDSIGHT ONLY | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 8 @ 11.985983h | PAL | REPRICE_REST@26 | REST@30 | neighborhood low envelope 15.83..32.00 | 2026-07-14T15:18:59.263Z; R-PRINTS#row-4335; cd48d559-68f1-5b3d-a8e4-d3c3fc43401e |
| 8 @ 11.985983h | URS | HOLD_REST@55 | REST@28 | NONE IN THE SIXTEEN — HINDSIGHT ONLY | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 9 @ 12.024469h | PAL | REPRICE_REST@31 | REST@30 | neighborhood low envelope 20.46..38.00 | 2026-07-14T15:18:59.263Z; R-PRINTS#row-4335; cd48d559-68f1-5b3d-a8e4-d3c3fc43401e |
| 9 @ 12.024469h | URS | REPRICE_REST@49 | REST@28 | NONE IN THE SIXTEEN — HINDSIGHT ONLY | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 10 @ 12.039239h | PAL | PLACE_REST@31 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 10 @ 12.039239h | URS | REPRICE_REST@53 | REST@28 | neighborhood low envelope 26.00..61.00 | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 11 @ 12.663132h | PAL | PLACE_REST@31 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 11 @ 12.663132h | URS | REPRICE_REST@50 | REST@28 | NONE IN THE SIXTEEN — HINDSIGHT ONLY | 2026-07-14T16:01:57.146Z; R-PRINTS#row-4399; 4b3658d8-7e56-5420-a06d-fa28d6aa5af9 |
| 12 @ 12.669913h | PAL | PLACE_REST@34 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 12 @ 12.669913h | URS | PLACE_REST@47 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 13 @ 12.670000h | PAL | PLACE_REST@28 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 13 @ 12.670000h | URS | PLACE_REST@47 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 14 @ 12.671940h | PAL | PLACE_REST@34 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 14 @ 12.671940h | URS | PLACE_REST@47 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 15 @ 12.671944h | PAL | PLACE_REST@32 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 15 @ 12.671944h | URS | PLACE_REST@45 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 16 @ 12.673611h | PAL | PLACE_REST@30 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 16 @ 12.673611h | URS | PLACE_REST@50 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 17 @ 12.675315h | PAL | PLACE_REST@36 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 17 @ 12.675315h | URS | PLACE_REST@36 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 18 @ 12.677678h | PAL | PLACE_REST@34 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 18 @ 12.677678h | URS | PLACE_REST@37 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 19 @ 12.677778h | PAL | PLACE_REST@37 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 19 @ 12.677778h | URS | PLACE_REST@37 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 20 @ 12.678889h | PAL | PLACE_REST@37 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 20 @ 12.678889h | URS | PLACE_REST@37 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 21 @ 12.733388h | PAL | PLACE_REST@34 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 21 @ 12.733388h | URS | PLACE_REST@32 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 22 @ 12.766152h | PAL | PLACE_REST@36 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 22 @ 12.766152h | URS | PLACE_REST@29 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 23 @ 12.816944h | PAL | PLACE_REST@34 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |
| 23 @ 12.816944h | URS | PLACE_REST@27 | NO_ACTION_CREDITED | half_pair_state.credited=true | sentence emitted; executor credited guard suppressed mutation |

### What remains unexplained

- The cause of URS falling from the sixties to 28 is absent from every connected market store.
- CC identified a likely late bell but did not replace L11's truth-table epoch; the lawful analysis window remains disputed but unchanged.
- Post-credit action sentences describe rests that the credited guard does not execute.
