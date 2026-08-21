#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const stream = require("stream/promises");
const zlib = require("zlib");
const groundTruthWindowAdapter = require("./window1_ground_truth_window_adapter.js");
const v52rExamAdapter = require("./window1_v52r_exam_adapter.js");
const v52sMechanism = require("./window1_v52s_joint_budget_yield_priority.js");
const v52sExamAdapter = require("./window1_v52s_exam_adapter.js");
const v53Organ = require("./window1_v53_understanding_organ.js");
const v53Bounds = require("./window1_v53_understanding_bounds.js");
const v53ReadBound = require("./window1_v53_read_licensed_bound.js");
const v53RiserArming = require("./window1_v53_riser_arming_law.js");
const v54PairModel = require("./window1_v54_pair_model.js");
const V36_COMMIT = "bfde0d8d1135f5c5f48a5f3d619ab30050efab83";
const REACH_COMMIT = "57daf3c15ad618098a810566d24127df8f17f3f9";
const GAP_COMMIT = "b581cbb58f660939ed9b0c2e88ddc42163dbab9a";
const DIVOT_COMMIT = "d1ac94973252e2f8c28ba32374c29ff7bd605a7e";
const COUNTERFACTUAL_COMMIT = "2b45d14688a0ec05d14ab4975759f1a986398da5";
const FALLER_ANATOMY_COMMIT = "c3961e2c2134aac7ea977d7ab4bb65bf7a263cc4";
const CAUSAL_REACH_COMMIT = "d3db740f143646614bc10778c0b4e27fa519dcd8";
const RISER_FRONTIER_COMMIT = "084df12553928677869bd2857516caa3f0490416";
const LEVEL_POLICY_COMMIT = "cca7c6c1554344711e2ddb32f3d3e2175c44711e";
const V41_COMMIT = "96d33316b0c0020b46b71569fcdbadeaa97a64e3";
const DEEP_GAP_CENSUS_COMMIT = "645e035bce12a4dcaf4cb7f10a3767fa898652a0";
const FULL_BOOK_PNL_COMMIT = "a30f5ccdf0c4233b30bf4017af48707f0db8ff1f";
const ARM_FIRST_EVIDENCE_COMMIT = "9ddfe8c6fec868cf07f92c54c878fe9208253451";
const LOOSEN_ONE_CENT_COMMIT = "52275c9d63be90eb16febd1d2cb10db00bd829c7";
const V43_COMMIT = "01a58334e90acffd4bb0fb17b6ceed17c4f51bbd";
const V45_COMMIT = "3bda0a5476c7fc845891928795f709feff8caabf";
const V43_RECALIBRATION_COMMIT = "b503e4edc2184e8958c97980c2e1769a077bfdd9";
const V43_RESIDUAL_DOCKET_COMMIT = "6934634efcc32cdb26dbe927ce8398a66aa50e92";
const STRICT_ASK_FOOTPRINT_COMMIT = "aa884cc5a1f9465a219d0913dbc237a33bc3a063";
const SURECH_RENDER_COMMIT = "8877c2d519c26b4e54f283ebebcee4933113d100";
const V47_COMMIT = "fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34";
const TRADES_TRUTH_RECUT_COMMIT = "e995c81b39174cc67bffcf568390b8d069e5fd8a";
const STANDABILITY_V2_COMMIT = "fe4747cd915830dc16f41c6bbec5e0ca1c14d99c";
const HERKAZ_EXEMPLAR_COMMIT = "b9673399c36fb9e5c14940610e3bf43fd2614c19";
const SUBSTITUTION_AUDIT_COMMIT = "bc0ce289a0bec90e137fe5638e0d629a88c651bf";
const DECISION_CHAIN_81_COMMIT = "4b9fcb794b7acecc8fe064ea2647159e81472025";
const IDENTITY_81_COMMIT = "653b7f1393adfec23d749de09dfef7591be8397a";
const CAUSAL_FLOOR_CONVICTION_COMMIT = "f36798fc84ea2fb466750212a69bed021d74a772";
const SEALED_V47_EXAM_COMMIT = "2bae89318273cc92fc75a7cbca679fc77496b3a7";
const V49B_COMMIT = "47b51fd20f3b0b821d27b63b15a576e36103562e";
const V52_COMMIT = "e20fbe6ce8bfe2619b6718e7554087fd9b900f0f";
const V52B_COMMIT = "98d07986fd916c1d75beb45095c75752bbc65102";
const V52C_COMMIT = "08ce27c0a297ed707cfd89aa29e60be223c9df7f";
const V52D_PARENT_COMMIT = "9f00b35f414d3f9a4011886bb8cb4e6cbe7da474";
const V52D_COMMIT = "893ee4c6860179a82c4b42439cf4a94cb2bcc97f";
const V52E_COMMIT = "b09aa22b301205d5d44d683497cf3edc5b177cf8";
const V52E_SPAN_AUDIT_COMMIT = "11f0fe0e04c315b555a0f02e4c8d44388328039e";
const V52F_PARENT_COMMIT = "4716657a18519d5b90705eb20030a66f5491a91b";
const V52F_COMMIT = "c235363e404c44873d43caa1626bd4ca927eb645";
const V52G_COMMIT = "ab841995f0cefa6011cf839fabf44057188111c4";
const V52H_COMMIT = "b43d7cde56aac5fe5cc553419286119adf378d6d";
const V52I_SOURCE_IMPLEMENTATION_COMMIT = "17623dce8efe139f0825226a5bf07aba7a9a2a7a";
const V52I_COMMIT = "576c705fb0a3fd9b48910738632119fa3fdc2da2";
const V52J_COMMIT = "604ab3e730efe5c649b7820a3daa3a34bec2033d";
const V52K_COMMIT = "de266f2e2e0a3cdeb27db046fcfba08db091c22f";
const V52L_COMMIT = "6678fd0c13dcc4de2bc153bbf769f5a2a9227ccc";
const V52M_COMMIT = "da4fd13b2c2ba068ceefc7ba10d6dee6c7667626";
const V52N_COMMIT = "74a702c8b100dedcba69a3637531ce6d77896eb2";
const V52O_COMMIT = "fe9387b2832f499b3cf9ed6d64ac576c098d15f0";
const V52P_COMMIT = "020b775cc59ddc4238d33113adf8e6e79e8bb97d";
const V52Q_COMMIT = "a059264d447ce071fd24f2cda4d9c3ea57aefa09";
const TRD5_COMMIT = "71de534a3f9e21faf569cd487d9aae735a084e7a";
const TRD5_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/GATE_POLICY_EVAL_LIVE_COORDS.json";
const LOW1_COMMIT = "ab609761c5df44097f46ad2364f539bbd0751d54";
const LOW1_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DOWN_TARGET_FRONTIER.json";
const RIPENESS_COMMIT = "41c1f7244af3afa4dade63bc9824808090ada41d";
const ANCHOR_DISCREPANCY_COMMIT = "620fe4c1";
const ANCHOR_DISCREPANCY_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/INSTRUMENT_PARITY_AND_LIVE_CLOCK.json";
const SHAPE_TAXONOMY_COMMIT = "e269779b0ec025d55f67d576e3cfb0cb575d5890";
const SHAPE_FLOOR_DEPTH_COMMIT = "8ab4f2d9e8c831235dc7cb4570c88daa3caded50";
const SHAPE_TAXONOMY_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/SHAPE_TAXONOMY_BUILD1.json";
const SHAPE_TAXONOMY_CSV_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/SHAPE_TAXONOMY_BUILD1.csv";
const SHAPE_FLOOR_DEPTH_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/PER_SHAPE_FLOOR_DEPTH_TABLES.json";
const RIPENESS_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RECOGNITION_OPERATING_POINT.json";
const GREEK_INSTRUMENTS_COMMIT = "2d48e4ee65e2d4b320accafcd4ac39669591d64b";
const OFFER_DENOMINATOR_COMMIT = "22441e058f9efa7ea8c3065334a238ec8786416f";
const MACHINE_PALANTIR_COMMIT = "9929e91802dc0e0f7ed1af50c5526b2c9a730c7c";
const REFLEX_CENSUS_COMMIT = "1d5564b5cdd25de32cfa9244cf21486245ab5b55";
const STABILITY_ONSET_COMMIT = "9eff493b48a21af2706895dc4a1aa27e6fae684c";
const FIVE_GAME_TAPE_PACK_COMMIT = "c09bde99bf6e529b24688bcc0deefd75be9530fd";
const V52_PRE_REPAIR_SCORE_TRACE_HASHES = {
  "ACTION_TRACE.jsonl.gz": "4f64d3b646d9aef09729746607e0db2a7d10a1e719ef33d537476aecdcd540bd",
  "ATTRIBUTION_FULL_BOOK_LEDGER.jsonl.gz": "f62d79491ce45bf67e28240a26249336305af1fe2a65ebd6511051072c08243b",
  "ATTRIBUTION_MARKET_EVENT_LEDGER.jsonl.gz": "1b36149eb9a6ebdea982bc689f426b8b32b07dfeaaff9b7eb73228cc77d753bd",
  "ATTRIBUTION_SCORECARD.json": "f0789e09eefb8bdc6b16f4c4c58aa17bb892819acb342f89b2180b8de443155b",
  "ATTRIBUTION_STRICT_EVENT_LEDGER.jsonl.gz": "d07d442f610f647c624f82fdad635177d76406987317b918f6d37d32e0f0ba9a",
  "BIRTH_LICENSE_ACTION_LEDGER.jsonl.gz": "865a0f6f159cf560aef0d381c8bfabb43a9eded6a6a9e6d88493058cbed42ff0",
  "CATEGORY_X_BELL_CONFIDENCE.json": "f91671d84d7ec8fd3d0ed9fee858a38c9501e323310d14dceadaa795a9dafa19",
  "DECISION_TRACE_1608.jsonl.gz": "81b48a7f0e3dd73e9a6ac6b55332337110173fcf262abf636d6ed65c99418aca",
  "DOCTRINE_81_GAME_LEDGER.jsonl.gz": "27b4b4aaa74a0434455bb72ed4bca271c7be7bc7f2783424ca76cbd0e02b87ce",
  "DOCTRINE_81_LEG_LEDGER.jsonl.gz": "193a84f8b60464061731dcd2809a49a6878a5e10eebad8f08e0a96d3f63df665",
  "FAITHFUL_STAND_AT_P_ACTION_LEDGER.jsonl.gz": "32c7c6eb7dea883c027ffd3bd68826e4f974ced3d8b81a8272c9b869226a47a6",
  "FRONTIER.json": "4e8e3e4ad397d0c1c23f31732cd9cd8572c21ac28bb7bd3618ef5645709cd1c9",
  "FULL_BOOK_PNL.json": "6afbc117e447c7e069c5a07b6305fe8d6691518911358d4e1e3e34c9f01b5571",
  "MARKET_EVENT_LEDGER.jsonl.gz": "43d345a4ac18d6f9ca69ce12149396c790190291ed582f5340795618023266f0",
  "MARKET_GRADE_SCORECARD.json": "249a15d6bcad191fe9f5fd38533c9de6af8ffb2e2cafe8abdbaa985a52b48827",
  "PERSISTENT_JOIN_LEDGER.jsonl.gz": "de7bdbeb9691377b4f65927e21a29357e7c4b6423be97cb376a54e2c814eac7d",
  "REGRET_GAUGE.json": "9e4426598ff309de18fe9300dc9d1d66c69505e5352637afaa56bc07dcfd9a29",
  "STABILITY_ONSET_LEDGER.jsonl.gz": "dfefb61e43062f5a5934b77d869386e0b6e829a5844245f414569bb971a8dc73",
  "STAGE1_DECISION_TRACE.jsonl.gz": "c009004846f730e7ae8f701ed6583e855dde44cc46f9a0c25fad9e5052e6964f",
  "STRICT_BUILD_VERIFICATION_SCORECARD.json": "5ef0579bcae93e4ccad2fe65b0208aa10eb78c4d3abf097066a36c0a9adb498a",
  "STRICT_EVENT_LEDGER.jsonl.gz": "79d188166509a52ca3bbbb6c5f22004af62801faf8562bfe96dfb08eb4d1db9d",
  "THREE_STATE_CENSUS.json": "c9d13798d9599972681d2cc4cf95221b3ec3662941e0e0dbc440803bc221f587",
  "THREE_STATE_EVENT_LEDGER.jsonl.gz": "aa2b5a353858326d4c3d06cb8da6f47fa7c3393822b78ad197e6fd9218793ed9",
  "V47_V49B_DIFFERENTIAL_LEDGER.jsonl.gz": "ef13704b5b4c473a767ee62d46e1baaaccfdf497b36618588334dbb4e65f34a5",
  "V49B_V52_DIFFERENTIAL_LEDGER.jsonl.gz": "91e9b717fcb64184ac8dd13d10af81fee411a7b77ab565ca0ea05cfa56dc950d",
};
const V36_PACKAGE = ".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806";
const GAP_PACKAGE = ".claude/window1_live_v4_replay/v36_gap_to_union_reach_20260807";
const OUT_REL = ".claude/window1_live_v4_replay/v38_maker_only_machine_20260807";
const EXPECTED_REACH = { events: 804, legs: 1608, reachable_games: 785, no_reach_games: 19, under_par_games: 637, locked_cents: 5253, union_legs: 1570 };

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const variant = arg("--variant", "v38");
const isV39 = variant === "v39";
const isV40 = variant === "v40";
const isV41 = variant === "v41";
const isV42 = variant === "v42";
const isV43 = variant === "v43";
const isV45 = variant === "v45";
const isV46 = variant === "v46";
const isV47 = variant === "v47";
const isV48 = variant === "v48";
const isV49 = variant === "v49";
const isV52c = variant === "v52c";
const isV52d = variant === "v52d";
const isV52eExam = variant === "v52e804";
const isV52rExam = variant === "v52r804";
const isV52sExam = variant === "v52s804";
const isV52FullExam = isV52eExam || isV52rExam || isV52sExam;
const isV52f = variant === "v52f";
const isV52g = variant === "v52g";
const isV52h = variant === "v52h";
const isV52i = variant === "v52i";
const isV52j = variant === "v52j";
const isV52k = variant === "v52k";
const isV52l = variant === "v52l";
const isV52m = variant === "v52m";
const isV52n = variant === "v52n";
const isV52o = variant === "v52o";
const isV52p = variant === "v52p";
const isV52q = variant === "v52q";
const isV52r = variant === "v52r" || isV52rExam;
const isV5302 = variant === "v53-02";
const isV5303 = variant === "v53-03";
const isV5304 = variant === "v53-04";
const isV54 = variant === "v54";
const isV53 = variant === "v53" || isV5302 || isV5303 || isV5304 || isV54;
const isV52Ripeness = isV52p || isV52q;
const isV52MacroRecognition = isV52m || isV52n || isV52o || isV52Ripeness || isV52r;
const isV52CausalOnset = isV52l || isV52MacroRecognition || isV52sExam || isV53;
const isV52DepthValidation = isV52i || isV52j || isV52k;
const isV52e = variant === "v52e" || isV52eExam || isV52f || isV52g || isV52h || isV52DepthValidation || isV52CausalOnset;
const isV52b = variant === "v52b";
const isV52FullRead = isV52c || isV52d || isV52e;
const isV52ReadAuthority = isV52b || isV52FullRead;
const isV52 = variant === "v52" || isV52ReadAuthority;
const isV49b = variant === "v49b" || isV52;
const isTradeTruthVariant = isV48 || isV49 || isV49b;
const isV45Family = isV45 || isV46 || isV47 || isTradeTruthVariant;
const isAttribution = isV43 || isV45Family;
const hasDeepGap = isV42 || isAttribution;
const isMaker41 = isV41 || hasDeepGap;
const isPlacementStack = isV39 || isV40 || isMaker41;
if (!["v38", "v39", "v40", "v41", "v42", "v43", "v45", "v46", "v47", "v48", "v49", "v49b", "v52", "v52b", "v52c", "v52d", "v52e", "v52e804", "v52f", "v52g", "v52h", "v52i", "v52j", "v52k", "v52l", "v52m", "v52n", "v52o", "v52p", "v52q", "v52r", "v52r804", "v52s804", "v53", "v53-02", "v53-03", "v53-04", "v54"].includes(variant)) throw new Error(`unknown variant ${variant}`);
const policy = isV54 ? v54PairModel : isV5304 ? v53RiserArming : isV5303 ? v53ReadBound : isV5302 ? v53Bounds : isV53 ? v53Organ : require(isV52sExam ? "./window1_v52h_remove_pair_lows_precondition.js" : isV52r ? "./window1_v52r_assembled_policy.js" : isV52q ? "./window1_v52q_anchor_correction.js" : isV52p ? "./window1_v52p_ripeness_gated_role_binding.js" : isV52o ? "./window1_v52o_benchmarked_role_instrument.js" : isV52n ? "./window1_v52n_recognition_confidence_gates.js" : isV52m ? "./window1_v52m_macro_recognition.js" : isV52l ? "./window1_v52h_remove_pair_lows_precondition.js" : isV52k ? "./window1_v52k_library_backed_evidence.js" : isV52j ? "./window1_v52j_role_conditioned_level_selection.js" : isV52i ? "./window1_v52i_depth_informed_level_selection.js" : isV52h ? "./window1_v52h_remove_pair_lows_precondition.js" : isV52g ? "./window1_v52g_joint_target_conservation.js" : isV52f ? "./window1_v52f_pair_entry_conservation.js" : isV52e ? "./window1_v52e_palantir_wiring.js" : isV52d ? "./window1_v52d_disagreement_referee.js" : isV52c ? "./window1_v52c_full_post_onset_read.js" : isV52b ? "./window1_v52b_read_level_authority.js" : isV52 ? "./window1_v52_judgment_gate.js" : isV49b ? "./window1_v49b_faithful_stand_at_p.js" : isV49 ? "./window1_v49_evidenced_level_standing.js" : isV48 ? "./window1_v48_trades_as_truth.js" : isV47 ? "./window1_v47_same_tick_arm.js" : isV46 ? "./window1_v46_pair_gated_gap_credit.js" : isV45 ? "./window1_v45_guard_release_sibling_credit.js" : isV43 ? "./window1_v43_composed_machine.js" : isV42 ? "./window1_v42_deep_gap_feasibility_guard.js" : isV41 ? "./window1_v41_maker_machine.js" : isV40 ? "./window1_v40_incumbent_direction_placement_stack.js" : isV39 ? "./window1_v39_corrected_placement_stack.js" : "./window1_v38_maker_only_machine.js");
const v5304ArmingLawId = arg("--v53-arming-law", "A2_FIRST_TRUE_DIVOT_AND_RESUME");
const v5304ArmingLaw = isV5304 ? policy.configureArmingLaw(v5304ArmingLawId) : null;
const frozenV52Policy = isV52b ? require("./window1_v52_judgment_gate.js") : null;
const frozenV52bPolicy = isV52FullRead ? require("./window1_v52b_read_level_authority.js") : null;
const frozenV52cPolicy = (isV52d || isV52e) ? require("./window1_v52c_full_post_onset_read.js") : null;
const frozenV52dPolicy = isV52e ? require("./window1_v52d_disagreement_referee.js") : null;
const frozenV52ePolicy = (isV52f || isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ? require("./window1_v52e_palantir_wiring.js") : null;
const frozenV52fPolicy = (isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ? require("./window1_v52f_pair_entry_conservation.js") : null;
const frozenV52gPolicy = (isV52h || isV52DepthValidation || isV52CausalOnset) ? require("./window1_v52g_joint_target_conservation.js") : null;
const frozenV52hPolicy = (isV52DepthValidation || isV52CausalOnset) ? require("./window1_v52h_remove_pair_lows_precondition.js") : null;
const onsetPolicy = isV52 ? require("./window1_v52_stability_onset.js") : null;
const causalOnsetPolicy = isV52CausalOnset ? require("./window1_v52l_causal_stability_onset.js") : null;
const v43Policy = isV45Family ? require("./window1_v43_composed_machine.js") : null;
const repo = path.resolve(arg("--repo", "."));
const groundTruthWindowBinding = isV52CausalOnset ? groundTruthWindowAdapter.loadGroundTruthTable(repo) : null;
const v36Root = path.resolve(arg("--v36-root", "C:/tmp/omi-v36-frozen-bfde"));
const reachRoot = path.resolve(arg("--reach-root", "C:/tmp/omi-reach-57daf3"));
const gapRoot = path.resolve(arg("--gap-root", isPlacementStack ? "C:/tmp/omi-v36-gap-reach-20260807" : repo));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const v52hNamedOnly = isV52h && arg("--named-only", "false") === "true";
const v52jNamedOnly = isV52j && arg("--named-only", "false") === "true";
const v52kNamedOnly = isV52k && arg("--named-only", "false") === "true";
const stage = arg("--stage", "full");
const isV54Tune804 = isV54 && stage === "tune804";
const isV54CheckSet = isV54 && stage === "checkset12";
const v5303Output = stage === "pins5" ? ".claude/window1_live_v4_replay/v53_03_read_licensed_bound_pins_smoke_20260820" : ".claude/window1_live_v4_replay/v53_03_read_licensed_bound_stage1_20260820";
const v5304Output = stage === "pins5" ? ".claude/window1_live_v4_replay/v53_04_riser_arming_law_pins_smoke_20260820" : ".claude/window1_live_v4_replay/v53_04_riser_arming_law_stage1_20260820";
const v54Output = stage === "pins5"
  ? ".claude/window1_live_v4_replay/v54_pair_model_iteration_01_pins_20260821"
  : isV54CheckSet
    ? ".claude/window1_live_v4_replay/v54_pair_model_iteration_01_check_set_12_20260821"
    : ".claude/window1_live_v4_replay/v54_pair_model_iteration_01_804_20260821";
const output = path.resolve(arg("--output", path.join(repo, isV54 ? v54Output : isV5304 ? v5304Output : isV5303 ? v5303Output : isV5302 ? ".claude/window1_live_v4_replay/v53_02_understanding_bounds_stage1_20260820" : isV53 ? ".claude/window1_live_v4_replay/v53_understanding_organ_stage1_20260819" : isV52sExam ? ".claude/window1_live_v4_replay/v52s_joint_budget_yield_priority_804_20260819" : isV52rExam ? ".claude/window1_live_v4_replay/v52r_disposition_804_20260818" : isV52r ? ".claude/window1_live_v4_replay/v52r_assembled_policy_20260818" : isV52q ? ".claude/window1_live_v4_replay/v52q_anchor_correction_20260818" : isV52p ? ".claude/window1_live_v4_replay/v52p_ripeness_gated_role_binding_20260817" : isV52o ? ".claude/window1_live_v4_replay/v52o_benchmarked_role_instrument_20260817" : isV52n ? ".claude/window1_live_v4_replay/v52n_recognition_confidence_gates_20260817" : isV52m ? ".claude/window1_live_v4_replay/v52m_macro_recognition_20260817" : isV52l ? ".claude/window1_live_v4_replay/v52l_causal_stability_onset_20260814" : isV52eExam ? ".claude/window1_live_v4_replay/v52e_disposition_804_20260813" : v52kNamedOnly ? ".claude/window1_live_v4_replay/v52k_guegom_named_observation_20260814" : isV52k ? ".claude/window1_live_v4_replay/v52k_library_backed_evidence_20260814" : v52jNamedOnly ? ".claude/window1_live_v4_replay/v52j_guegom_named_observation_20260813" : isV52j ? ".claude/window1_live_v4_replay/v52j_role_conditioned_level_selection_20260813" : isV52i ? ".claude/window1_live_v4_replay/v52i_depth_informed_level_selection_20260813" : v52hNamedOnly ? ".claude/window1_live_v4_replay/v52h_smiila_named_observation_20260813" : isV52h ? ".claude/window1_live_v4_replay/v52h_remove_pair_lows_precondition_20260813" : isV52g ? ".claude/window1_live_v4_replay/v52g_joint_target_conservation_20260813" : isV52f ? ".claude/window1_live_v4_replay/v52f_pair_entry_conservation_20260813" : isV52e ? ".claude/window1_live_v4_replay/v52e_palantir_wiring_20260812" : isV52d ? ".claude/window1_live_v4_replay/v52d_disagreement_referee_20260812" : isV52c ? ".claude/window1_live_v4_replay/v52c_full_post_onset_read_20260812" : isV52b ? ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812" : isV52 ? ".claude/window1_live_v4_replay/v52_judgment_gate_20260812" : isV49b ? ".claude/window1_live_v4_replay/v49b_faithful_stand_at_p_20260811" : isV49 ? ".claude/window1_live_v4_replay/v49_evidenced_level_standing_20260810" : isV48 ? ".claude/window1_live_v4_replay/v48_trades_as_truth_20260810" : isV47 ? ".claude/window1_live_v4_replay/v47_same_tick_arm_20260810" : isV46 ? ".claude/window1_live_v4_replay/v46_pair_gated_gap_credit_20260810" : isV45 ? ".claude/window1_live_v4_replay/v45_guard_release_sibling_credit_20260809" : isV43 ? ".claude/window1_live_v4_replay/v43_composed_machine_20260809" : isV42 ? ".claude/window1_live_v4_replay/v42_deep_gap_feasibility_guard_20260809" : isV41 ? ".claude/window1_live_v4_replay/v41_maker_machine_20260808" : isV40 ? ".claude/window1_live_v4_replay/v40_incumbent_direction_placement_stack_20260808" : isV39 ? ".claude/window1_live_v4_replay/v39_corrected_placement_stack_20260807" : OUT_REL)));
const compare = arg("--compare", null) ? path.resolve(arg("--compare", null)) : null;
const sanityReceiptPath = arg("--sanity-receipt", null) ? path.resolve(arg("--sanity-receipt", null)) : null;
if (isV52 && !["stage1", "full", "cohort30", "pins5", "disposition804", "tune804", "checkset12"].includes(stage)) throw new Error(`invalid V52 stage ${stage}`);
if (isV52eExam && stage !== "disposition804") throw new Error(`V52e full exam requires disposition804 stage, got ${stage}`);
if (isV52rExam && stage !== "disposition804") throw new Error(`V52r full exam requires disposition804 stage, got ${stage}`);
if (isV52sExam && stage !== "disposition804") throw new Error(`V52s full exam requires disposition804 stage, got ${stage}`);
const V52_FLOW_EVENTS = new Set(["26JUL16MERDRO", "26JUL12POLKUH", "26JUL19ARSMAR", "26JUL13SANDAN", "26JUL14PUTJEA"]);

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function shaBytes(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function shaCanonicalRows(rows) {
  const hash = crypto.createHash("sha256");
  for (const row of rows) {
    const bytes = Buffer.from(canonical(row));
    hash.update(String(bytes.length)); hash.update(":"); hash.update(bytes); hash.update("\n");
  }
  return hash.digest("hex");
}
function fileHash(file) { return shaBytes(fs.readFileSync(file)); }
function localLine(relativePath, needle) {
  const lines = fs.readFileSync(path.join(repo, relativePath), "utf8").split(/\r?\n/);
  const index = lines.findIndex((line) => line.includes(needle));
  ensure(index >= 0, `line anchor absent ${relativePath}:${needle}`);
  return index + 1;
}
function write(name, bytes) { fs.writeFileSync(path.join(output, name), bytes); }
function writeManifest(dir) {
  const names = fs.readdirSync(dir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(dir, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: fileHash(path.join(dir, name)), bytes: fs.statSync(path.join(dir, name)).size }])) }));
}
function gzipRows(rows) {
  const lines = rows.map((row) => JSON.stringify(row)).join("\n");
  return zlib.gzipSync(Buffer.from(`${lines}${lines ? "\n" : ""}`), { level: 9, mtime: 0 });
}
async function writeGzipRowsFile(file, rows, compressionLevel = 9) {
  async function* encode() { for await (const row of rows) yield `${JSON.stringify(row)}\n`; }
  await stream.pipeline(encode(), zlib.createGzip({ level: compressionLevel, mtime: 0 }), fs.createWriteStream(file));
}
let activeExamTraceNormalizer = null;
let activeExamTraceStats = null;
function accumulateExamTraceStats(row) {
  const stats = activeExamTraceStats;
  if (!stats) return;
  stats.rows += 1;
  if (row.palantir) stats.palantir_consumption_rows += 1;
  if (row.palantir?.continuous_at_decision_time) stats.continuous_rows += 1;
  if (row.palantir?.priors_gate === true) stats.priors_gate_true_rows += 1;
  for (const node of ["N2", "N4", "N5"]) {
    if (row.palantir?.[node]) stats[`${node}_rows`] += 1;
    for (const provenance of row.palantir?.[node]?.provenance ?? []) if (provenance.asset_id) stats.provenance_asset_ids.add(provenance.asset_id);
  }
  if (row.palantir?.N4?.grid) stats.N4_grid_rows += 1;
  if (row.level?.machine_read?.palantir_rescue === true) stats.N4_rescue_rows += 1;
  if (row.coherence?.disagreement_adjudication?.status === "ADJUDICATED_N5_STRICTLY_STRONGER_VALIDATED_BASE_RATE") stats.N5_adjudication_rows += 1;
  if (row.blocked_clause) {
    stats.by_block_reason[row.blocked_clause] = (stats.by_block_reason[row.blocked_clause] || 0) + 1;
    const key = `${row.category}|${row.blocked_clause}`;
    stats.by_category_x_block_reason[key] = (stats.by_category_x_block_reason[key] || 0) + 1;
  }
}
function makeLosslessTraceNormalizer() {
  const sequenceByLeg = new Map();
  const fields = [
    "event_id", "leg_identity", "category", "price_region", "sequence", "timestamp_epoch", "hours_from_discovery", "t_minus_scheduled_seconds", "t_minus_actual_bell_seconds", "t_minus_pre_match_boundary_seconds", "receipt",
    "bid", "ask", "last_traded", "spread", "ask_dwell_seconds", "top_ask_size", "bid_depth_5", "ask_depth_5",
    "onset_passed", "onset_candidate", "onset_timestamp_epoch",
    "read_passed", "read_state", "quote_path_state", "pressure_state", "read_evidence_class", "read_span_seconds", "read_evidence_receipts", "read_book_receipts", "read_print_receipts", "read_comparable_book_transitions", "read_comparable_print_transitions", "read_rising_score", "read_falling_score", "last_directional_evidence_kind", "last_directional_evidence_receipt", "last_directional_evidence_magnitude_cents",
    "own_post_onset_low_cents", "own_low_receipt", "sibling_post_onset_low_cents", "sibling_low_receipt", "lows_sum_cents", "lows_under_par", "disagreement_firing", "disagreement_clear", "adjudication_status", "adjudication_winner", "adjudication_loser",
    "level_passed", "level_target_cents", "level_authority", "machine_read_target_cents", "machine_read_authority", "palantir_rescue",
    "palantir_manifest_sha256", "N2_cell_n", "N2_cell_share", "N4_grid_covered", "N4_grid_discount_cents", "N4_zone_category_share", "N4_zone_price_share", "N5_mirror_rate", "N5_vindication_rate", "palantir_continuous", "priors_gate",
    "gate_verdict", "blocked_clause", "incumbent_action", "incumbent_reason", "order_before_cents", "final_action", "final_target_cents", "reason",
  ];
  return {
    normalize(row) {
      const sequence = (sequenceByLeg.get(row.leg_identity) ?? 0) + 1; sequenceByLeg.set(row.leg_identity, sequence);
      const e = row.read?.full_post_onset_evidence, a = row.coherence?.disagreement_adjudication, p = row.palantir, grid = p?.N4?.grid;
      const values = [
        row.event_id, row.leg_identity, row.category, row.price_region, sequence, row.timestamp_epoch, row.hours_from_discovery, row.t_minus_scheduled_seconds, row.t_minus_actual_bell_seconds, row.t_minus_pre_match_boundary_seconds, row.receipt,
        row.observation?.bid, row.observation?.ask, row.observation?.last_traded, row.observation?.spread, row.observation?.ask_dwell_seconds, row.observation?.top_ask_size, row.observation?.bid_depth_5, row.observation?.ask_depth_5,
        row.onset?.passed, row.onset?.selected_candidate, row.onset?.timestamp_epoch,
        row.read?.passed, row.read?.state, row.read?.quote_path_state, row.read?.pressure_state, row.read?.evidence, e?.span_seconds, e?.consulted?.evidence_receipts, e?.consulted?.book_receipts, e?.consulted?.print_receipts, e?.consulted?.comparable_book_transitions, e?.consulted?.comparable_print_transitions, e?.weighted_scores_cents?.rising, e?.weighted_scores_cents?.falling, e?.last_directional_evidence?.kind, e?.last_directional_evidence?.receipt, e?.last_directional_evidence?.magnitude_cents,
        row.diary?.own_post_onset_true_trade_low_cents, row.diary?.own_receipt, row.diary?.sibling_post_onset_true_trade_low_cents, row.diary?.sibling_receipt, row.coherence?.post_onset_running_lows_sum_cents, row.coherence?.lows_under_par, row.coherence?.disagreement_firing, row.coherence?.disagreement_clear, a?.status, a?.winner?.state ?? a?.winner, a?.loser?.state ?? a?.loser,
        row.level?.passed, row.level?.target_cents, row.level?.authority, row.level?.machine_read?.target_cents, row.level?.machine_read?.authority, row.level?.machine_read?.palantir_rescue === true,
        p?.manifest?.sha256, p?.N2?.cell_base_rate?.n, p?.N2?.cell_base_rate?.share, Boolean(grid), grid?.discount_cents ?? grid?.p75_dip ?? null, p?.N4?.zone?.category?.share, p?.N4?.zone?.starting_price_split?.share, p?.N5?.mirror_coherence_base_rate?.rate, p?.N5?.one_eyed_vindication_base_rate?.rate, p?.continuous_at_decision_time, p?.priors_gate,
        row.gate_verdict, row.blocked_clause, row.incumbent_action, row.incumbent_reason, row.order_before_cents, row.final_action, row.final_target_cents, row.reason,
      ];
      return values.map((value) => value === undefined ? null : value);
    },
    entries() { return [{ format: "RECEIPT_GRAIN_DECISION_DIARY_V1", fields, reconstruction: "Each array position maps to fields[index]. Source book/print payload and frozen policy reconstruct deeper duplicated evidence objects; no decision receipt is omitted." }]; },
    legs() { return sequenceByLeg.size; },
    rows() { return [...sequenceByLeg.values()].reduce((sum, value) => sum + value, 0); },
  };
}
function compactV54TraceRow(row) {
  const ownId = row.leg_identity?.split("|").at(-1) ?? null;
  const ownView = ownId ? row.game_view?.legs?.[ownId] ?? null : null;
  return {
    event_id: row.event_id,
    leg_identity: row.leg_identity,
    category: row.category,
    price_region: row.price_region,
    timestamp_epoch: row.timestamp_epoch,
    hours_from_discovery: row.hours_from_discovery,
    t_minus_scheduled_seconds: row.t_minus_scheduled_seconds,
    t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds,
    t_minus_pre_match_boundary_seconds: row.t_minus_pre_match_boundary_seconds,
    receipt: row.receipt,
    observation: row.observation,
    onset: row.onset ? { passed: row.onset.passed, selected_candidate: row.onset.selected_candidate, timestamp_epoch: row.onset.timestamp_epoch } : null,
    read: row.read ? { passed: row.read.passed, state: row.read.state, quote_path_state: row.read.quote_path_state, pressure_state: row.read.pressure_state, receipt: row.read.receipt } : null,
    pair_model: row.v54_pair_model,
    own_game_view: ownView,
    plan: row.plan,
    joint_license: row.joint_license,
    conservation_input_identity: row.conservation_input_identity,
    pair_entry_conservation: row.pair_entry_conservation,
    joint_target_conservation: row.joint_target_conservation,
    lineage_decision: row.lineage_decision,
    lineage_target_cents: row.lineage_target_cents,
    gate_verdict: row.gate_verdict,
    blocked_clause: row.blocked_clause,
    order_before_cents: row.order_before_cents,
    final_action: row.final_action,
    final_target_cents: row.final_target_cents,
    reason: row.reason,
  };
}
function v54LicenseSpans(traceRows) {
  const spans = [];
  const rowsByLeg = new Map();
  for (const row of traceRows) {
    if (!rowsByLeg.has(row.leg_identity)) rowsByLeg.set(row.leg_identity, []);
    rowsByLeg.get(row.leg_identity).push(row);
  }
  for (const [legIdentity, rows] of [...rowsByLeg].sort(([a], [b]) => a.localeCompare(b))) {
    rows.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
    let current = null;
    for (const row of rows) {
      const compact = compactV54TraceRow(row);
      const polarity = compact.pair_model?.polarity ?? null;
      const compactPolarity = polarity ? {
        tag: polarity.tag,
        strengthening_leg_id: polarity.strengthening_leg_id,
        fading_leg_id: polarity.fading_leg_id,
        reason: polarity.reason,
        evidence_directions: Object.fromEntries(Object.entries(polarity.evidence ?? {}).map(([id, evidence]) => [id, { role: evidence.role?.value ?? null, pressure_direction: evidence.pressure_direction, joint_state_direction: evidence.joint_state_direction, travel_direction: evidence.travel_direction }])),
      } : null;
      const semantic = {
        event_id: compact.event_id,
        leg_identity: compact.leg_identity,
        category: compact.category,
        price_region: compact.price_region,
        onset_passed: compact.onset?.passed ?? null,
        read: compact.read ? { passed: compact.read.passed, state: compact.read.state, quote_path_state: compact.read.quote_path_state, pressure_state: compact.read.pressure_state } : null,
        pair_model: compact.pair_model ? { enabled: compact.pair_model.enabled, polarity: compactPolarity, window: compact.pair_model.window, applied: compact.pair_model.applied, reason: compact.pair_model.reason } : null,
        plan: compact.plan ? { model: compact.plan.model, polarity: compactPolarity, windows: compact.plan.windows, l16_anchor_targets_cents: compact.plan.l16_anchor_targets_cents, undecided_fallback: compact.plan.undecided_fallback, fading_path: compact.plan.fading_path, strengthening_path: compact.plan.strengthening_path } : null,
        joint_license: compact.joint_license ? { law: compact.joint_license.law, model: compact.joint_license.model, complete: compact.joint_license.complete, polarity: compactPolarity, windows: compact.joint_license.windows, both_levels: compact.joint_license.both_levels, budget_split: compact.joint_license.budget_split, adjustments: compact.joint_license.adjustments, action: compact.joint_license.action, sentence_action_assertion: compact.joint_license.sentence_action_assertion, sentence_template: compact.joint_license.sentence?.replace(/At receipt [^,]+,/, "At receipt {RECEIPT},") ?? null } : null,
        conservation_input_identity: compact.conservation_input_identity,
        pair_entry_conservation: compact.pair_entry_conservation,
        joint_target_conservation: compact.joint_target_conservation,
        lineage_decision: compact.lineage_decision,
        lineage_target_cents: compact.lineage_target_cents,
        gate_verdict: compact.gate_verdict,
        blocked_clause: compact.blocked_clause,
        order_before_cents: compact.order_before_cents,
        final_action: compact.final_action,
        final_target_cents: compact.final_target_cents,
        reason: compact.reason,
      };
      const signature = shaBytes(Buffer.from(canonical(semantic)));
      const receiptDigest = shaBytes(Buffer.from(canonical(compact)));
      if (!current || current.semantic_sha256 !== signature) {
        if (current) spans.push(current);
        current = {
          event_id: compact.event_id,
          leg_identity: legIdentity,
          category: compact.category,
          price_region: compact.price_region,
          semantic_sha256: signature,
          semantic,
          representative_sentence: compact.joint_license?.sentence ?? null,
          first_timestamp_epoch: compact.timestamp_epoch,
          first_hours_from_discovery: compact.hours_from_discovery,
          first_t_minus_scheduled_seconds: compact.t_minus_scheduled_seconds,
          first_t_minus_actual_bell_seconds: compact.t_minus_actual_bell_seconds,
          first_receipt: compact.receipt,
          last_timestamp_epoch: compact.timestamp_epoch,
          last_hours_from_discovery: compact.hours_from_discovery,
          last_t_minus_scheduled_seconds: compact.t_minus_scheduled_seconds,
          last_t_minus_actual_bell_seconds: compact.t_minus_actual_bell_seconds,
          last_receipt: compact.receipt,
          receipt_count: 0,
          receipt_digest_chain_sha256: crypto.createHash("sha256"),
        };
      }
      current.receipt_count += 1;
      current.last_timestamp_epoch = compact.timestamp_epoch;
      current.last_hours_from_discovery = compact.hours_from_discovery;
      current.last_t_minus_scheduled_seconds = compact.t_minus_scheduled_seconds;
      current.last_t_minus_actual_bell_seconds = compact.t_minus_actual_bell_seconds;
      current.last_receipt = compact.receipt;
      current.receipt_digest_chain_sha256.update(`${compact.receipt}|${receiptDigest}\n`);
    }
    if (current) spans.push(current);
  }
  return spans.map((span) => ({ ...span, receipt_digest_chain_sha256: span.receipt_digest_chain_sha256.digest("hex") }));
}
function appendV54LicenseSpan(spans, traceRow) {
  const next = v54LicenseSpans([traceRow])[0];
  ensure(next, `V54 compact license span missing ${traceRow.leg_identity}@${traceRow.receipt}`);
  const prior = spans.at(-1);
  if (prior && prior.leg_identity === next.leg_identity && prior.semantic_sha256 === next.semantic_sha256) {
    prior.last_timestamp_epoch = next.last_timestamp_epoch;
    prior.last_t_minus_scheduled_seconds = next.last_t_minus_scheduled_seconds;
    prior.last_t_minus_actual_bell_seconds = next.last_t_minus_actual_bell_seconds;
    prior.last_receipt = next.last_receipt;
    prior.receipt_count += next.receipt_count;
    prior.receipt_digest_chain_sha256 = shaBytes(Buffer.from(`${prior.receipt_digest_chain_sha256}|${next.receipt_digest_chain_sha256}`));
    return prior;
  }
  spans.push(next);
  return next;
}
function makeTraceChunkWriter(dir, eventsPerChunk = 8, normalizer = null, filePrefix = "V52E_FULL_DECISION_TRACE_804_CHUNK", compressionLevel = 9) {
  let rows = [], eventIds = [], ordinal = 0;
  const chunks = [];
  const flush = async () => {
    if (!rows.length) return;
    ordinal += 1;
    const name = `${filePrefix}_${String(ordinal).padStart(3, "0")}.jsonl.gz`;
    await writeGzipRowsFile(path.join(dir, name), rows, compressionLevel);
    chunks.push({ name, events: [...eventIds], event_count: eventIds.length, row_count: rows.length, sha256: fileHash(path.join(dir, name)), bytes: fs.statSync(path.join(dir, name)).size });
    rows = []; eventIds = [];
  };
  return {
    async append(eventId, eventRows) {
      eventIds.push(eventId);
      for (const row of eventRows) rows.push(normalizer ? normalizer.normalize(row) : row);
      if (eventIds.length >= eventsPerChunk) await flush();
    },
    async finish() { await flush(); return chunks; },
  };
}
function readRows(file) {
  const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim();
  return text ? text.split(/\r?\n/).map(JSON.parse) : [];
}
function readRowsBytes(bytes) {
  const text = zlib.gunzipSync(bytes).toString("utf8").trim();
  return text ? text.split(/\r?\n/).map(JSON.parse) : [];
}
function compactV52rExamEvent(event) {
  return {
    event_id: event.event_id,
    category: event.category,
    starting_price_split: event.starting_price_split,
    bell_confidence: event.bell_confidence,
    ...(event.v52s_joint_budget_receipt_summary ? { v52s_joint_budget_receipt_summary: event.v52s_joint_budget_receipt_summary } : {}),
    legs: Object.fromEntries(Object.entries(event.legs).map(([legId, leg]) => [legId, {
      leg_id: leg.leg_id,
      leg_identity: leg.leg_identity,
      ticker: leg.ticker,
      credited: leg.credited,
      entry_cents: leg.entry_cents,
      fill_timestamp_epoch: leg.fill_timestamp_epoch,
      fill_receipt: leg.fill_receipt ?? null,
      fill_class: leg.fill_class ?? null,
      terminal_reason: leg.terminal_reason,
      judgment_gate_blocks: leg.judgment_gate_blocks ?? {},
    }])),
  };
}
function gitHead(root) {
  return require("child_process").execFileSync("git", ["-c", `safe.directory=${path.resolve(root).replaceAll("\\", "/")}`, "rev-parse", "HEAD"], { cwd: root, encoding: "utf8" }).trim();
}
function gitShow(commit, relativePath) {
  return require("child_process").execFileSync("git", ["show", `${commit}:${relativePath}`], { cwd: repo, maxBuffer: 256 * 1024 * 1024 });
}
function loadN9CleanStore() {
  const adapter = require("./window1_n9_clean_store.js");
  const manifestPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/MACHINE_PALANTIR.json";
  const manifestBytes = gitShow(MACHINE_PALANTIR_COMMIT, manifestPath);
  const manifest = JSON.parse(manifestBytes);
  const load = (id, commit, relativePath) => {
    const bytes = gitShow(commit, relativePath);
    const entry = manifest.store_CLEAN.find((row) => row.id === id);
    ensure(entry && String(entry.sha).split(/[ +/]/).some((token) => commit.startsWith(token)), `${id} manifest commit binding mismatch`);
    return { data: JSON.parse(bytes), source: { inventory: "store_CLEAN", commit, path: relativePath, sha256: shaBytes(bytes), bytes: bytes.length, status: entry.status } };
  };
  const p1 = load("P1", "2f59130e6ffe9c1ef54b79c10a57b06f8c4cc279", ".claude/seqfloor_20260708/recut_cells.json");
  const p2 = load("P2", "35ac1f5b1ce345427bbeaa1b8bc6ee85c1db8d14", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DECISION_AUDIT.json");
  const p4 = load("P4", "12d67c8ac58992e6634c5c32ac8e710980533e07", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/READ_ORGAN_FORWARD_TRUTH.json");
  const p6 = load("P6", "096241ae9512bc20fec7bf89b199551622a4c482", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/OVERPAY_CENSUS.json");
  const p11 = load("P11", "6bc169bfcc448d6df8a6cd0b8dae5638e3853ebf", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/HIDDEN_BOOK_CENSUS.json");
  const p12 = load("P12", "f40ac8eae23b021bbe9c60e867ee0a2df24b731a", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DIVOT_ARRIVAL_AUDIT.json");
  const p13sealed = load("P13", "b26cf54803d85567f799bfdafe2bfe75403bbe2f", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/SEALED_REGRET_GAUGE_238.json");
  const p13cap = load("P13", "a20e1a85976aefee6a6f0567957174133b692df6", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/CAPBOUND_ANATOMY_TAIL_CHECK.json");
  const p14 = load("P14", "78b5cbd40ad7188466ac04d56467b2946b247b75", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RISER_DEPTH_SIGNAL_RANK.json");
  const assets = {
    __manifest: { commit: MACHINE_PALANTIR_COMMIT, path: manifestPath, sha256: shaBytes(manifestBytes), bytes: manifestBytes.length },
    P1: { data: p1.data, sources: [p1.source] }, P2: { data: p2.data, sources: [p2.source] }, P4: { data: p4.data, sources: [p4.source] }, P6: { data: p6.data, sources: [p6.source] }, P11: { data: p11.data, sources: [p11.source] }, P12: { data: p12.data, sources: [p12.source] },
    P13: { data: { sealed: p13sealed.data, decision: p2.data, cap: p13cap.data }, sources: [p13sealed.source, { ...p2.source, asset_id: "P13_SHARED_P2_SOURCE" }, p13cap.source] },
    P14: { data: p14.data, sources: [p14.source] },
  };
  const cleanStore = adapter.makeCleanStore(manifest, assets);
  if (!isV52DepthValidation) return { store: cleanStore, manifest, manifestBytes, assets };
  const validationAdapter = require("./window1_v52i_under_validation_store.js");
  const greekPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/GREEK_INSTRUMENTS.json";
  const greekManifestPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/MACHINE_PALANTIR.json";
  const greekBytes = gitShow(GREEK_INSTRUMENTS_COMMIT, greekPath);
  const greekManifestBytes = gitShow(GREEK_INSTRUMENTS_COMMIT, greekManifestPath);
  const greek = JSON.parse(greekBytes), greekManifest = JSON.parse(greekManifestBytes);
  const g3Entry = (greekManifest.candidates_UNVALIDATED_CANDIDATE || []).find((row) => row.id === "G3");
  ensure(g3Entry && String(g3Entry.status).startsWith("UNVALIDATED-CANDIDATE"), "G3 source candidate status changed");
  ensure(greek.C_vega_gamma?.depth_cells && greek.C_vega_gamma?.recovery_within_60min, "G3 depth/recovery surface absent");
  const p1Source = assets.P1.sources[0];
  const candidates = {
    G_GRID_LEVEL_DISCOUNT: {
      entry: { id: "G_GRID_LEVEL_DISCOUNT", name: "G-grid cell-conditional discount weighting role", status: "UNDER-VALIDATION_V52I", prior_asset_id: "P1", prior_asset_status: assets.P1.entry?.status ?? manifest.store_CLEAN.find((row) => row.id === "P1")?.status, role_status_before_V52i: "UNVALIDATED_CANDIDATE_BEHAVIORAL_WEIGHTING_ROLE", canonical_P1_status_unchanged: true },
      data: assets.P1.data,
      sources: [{ ...p1Source, inventory: "inventory_UNDER_VALIDATION_V52I", source_asset_id: "P1", operator_binding_commit: V52H_COMMIT }],
    },
    G3_DIP_RECOVERY_GRADIENT: {
      entry: { id: "G3_DIP_RECOVERY_GRADIENT", name: g3Entry.name, status: "UNDER-VALIDATION_V52I", prior_asset_id: "G3", prior_asset_status: g3Entry.status, canonical_candidate_registry_unchanged: true },
      data: greek.C_vega_gamma,
      sources: [{ inventory: "inventory_UNDER_VALIDATION_V52I", commit: GREEK_INSTRUMENTS_COMMIT, path: greekPath, sha256: shaBytes(greekBytes), bytes: greekBytes.length, status: "UNDER-VALIDATION_V52I", source_asset_id: "G3", source_manifest_path: greekManifestPath, source_manifest_sha256: shaBytes(greekManifestBytes) }],
    },
  };
  const store = validationAdapter.makeUnderValidationStore(cleanStore, candidates);
  return { store, manifest, manifestBytes, assets, greek: { commit: GREEK_INSTRUMENTS_COMMIT, path: greekPath, bytes: greekBytes, sha256: shaBytes(greekBytes), manifest_path: greekManifestPath, manifest_sha256: shaBytes(greekManifestBytes), source_entry: g3Entry }, candidates };
}
function safeOutput(dir) {
  const resolved = path.resolve(dir);
  ensure(path.basename(resolved).includes(isV54 ? "v54" : isV53 ? "v53" : isV52 ? "v52" : isV49b ? "v49b" : isV49 ? "v49" : isV48 ? "v48" : isV47 ? "v47" : isV46 ? "v46" : isV45 ? "v45" : isV43 ? "v43" : isV42 ? "v42" : isV41 ? "v41" : isV40 ? "v40" : isV39 ? "v39" : "v38"), `unsafe output ${resolved}`);
  ensure(resolved !== repo && resolved !== path.parse(resolved).root, `unsafe output ${resolved}`);
  fs.rmSync(resolved, { recursive: true, force: true });
  fs.mkdirSync(resolved, { recursive: true });
}
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function percentile(values, q) {
  const x = values.filter(Number.isFinite).sort((a, b) => a - b);
  return x.length ? x[Math.max(0, Math.ceil(q * x.length) - 1)] : null;
}
function distribution(values) {
  const x = values.filter(Number.isFinite);
  return { n: x.length, null_n: values.length - x.length, sum: x.reduce((a, b) => a + b, 0), min: x.length ? Math.min(...x) : null, p25: percentile(x, .25), median: percentile(x, .5), p75: percentile(x, .75), p90: percentile(x, .9), max: x.length ? Math.max(...x) : null };
}
function countBy(rows, fn) {
  const out = {};
  for (const row of rows) { const key = String(fn(row)); out[key] = (out[key] || 0) + 1; }
  return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}
function clockFields(ts, base) {
  return {
    timestamp_epoch: ts,
    hours_from_discovery: Number.isFinite(base.discovery_epoch ?? base.left) ? (ts - (base.discovery_epoch ?? base.left)) / 3600 : null,
    t_minus_scheduled_seconds: Number.isFinite(base.scheduled) ? base.scheduled - ts : null,
    t_minus_actual_bell_seconds: Number.isFinite(base.actual_bell) ? base.actual_bell - ts : null,
    t_minus_pre_match_boundary_seconds: base.right - ts,
  };
}

function pairBudgetSplit(leg, sibling) {
  const row = (side) => side.credited
    ? { leg_identity: side.leg_identity, state: "BOUGHT_SIDE", cents: side.entry_cents }
    : side.active_order
      ? { leg_identity: side.leg_identity, state: "STANDING_SIDE", cents: side.active_order.target_cents }
      : { leg_identity: side.leg_identity, state: "UNSET_SIDE", cents: null };
  return [row(leg), row(sibling)].sort((a, b) => a.leg_identity.localeCompare(b.leg_identity));
}

function notePairBudgetRevision(leg, sibling, row, cause, license = null) {
  const record = leg.pair_budget_record;
  if (!record) return;
  const split = pairBudgetSplit(leg, sibling);
  const known = split.filter((side) => Number.isInteger(side.cents));
  const joint = known.length === 2 ? known[0].cents + known[1].cents : null;
  if (Number.isInteger(joint)) ensure(joint <= 99, `V52g joint target violation ${record.event_id} ${joint} at ${row.receipt}`);
  const prior = record.current_joint_split;
  if (prior && canonical(prior) === canonical(split)) return;
  const hasLicensedStanding = split.some((side) => side.state === "STANDING_SIDE");
  if (!record.born_at && hasLicensedStanding) record.born_at = { timestamp_epoch: row.ts, receipt: row.receipt };
  if (!record.born_at) return;
  const revision = {
    revision: record.revisions.length + 1,
    timestamp_epoch: row.ts,
    receipt: row.receipt,
    cause,
    evaluated_leg_identity: leg.leg_identity,
    prior_joint_split: prior,
    current_joint_split: split,
    joint_target_sum_cents: joint,
    joint_identity_pass: joint === null || joint <= 99,
    license_fields: {
      onset: license?.onset ?? null,
      read: license?.read ?? null,
      diary: license?.diary ?? null,
      coherence: license?.coherence ?? null,
      level: license?.level ?? null,
      palantir: license?.palantir ?? null,
      pair_entry_conservation: license?.pair_entry_conservation ?? null,
      joint_target_conservation: license?.joint_target_conservation ?? {
        clause: "CLAUSE_6_ORDER_FREE_JOINT_TARGET_CONSERVATION",
        reached: true,
        passed: joint === null || joint <= 99,
        reason: `PAIR_BUDGET_RECORD_REVISION_${cause}`,
        current_joint_split: split,
        joint_target_sum_cents: joint,
      },
    },
  };
  record.current_joint_split = split;
  record.revisions.push(revision);
}

function v52sSide(leg) {
  if (leg.credited) return { leg_identity: leg.leg_identity, state: "BOUGHT_SIDE", entry_cents: leg.entry_cents };
  if (!leg.active_order) return { leg_identity: leg.leg_identity, state: "UNSET_SIDE" };
  return {
    leg_identity: leg.leg_identity,
    state: "STANDING_SIDE",
    default_target_cents: leg.active_order.v52s_default_target_cents ?? leg.active_order.target_cents,
    post_onset_session_low_cents: leg.post_onset_true_trade_low_cents,
    best_ask_cents: leg.prior_book?.ask ?? null,
    pair_cap_cents: leg.pair_cap_cents,
  };
}

function v52sEventView(leg, sibling) {
  return { event_id: leg.event_id, legs: { [leg.leg_identity]: leg, [sibling.leg_identity]: sibling }, v52s_joint_budget_receipt_summary: leg.v52s_joint_budget_receipt_summary };
}

function reconcileV52s(event, row, actions, base, cause, allowLifts = true) {
  if (!base.v52s_enabled) return null;
  const legs = Object.values(event.legs).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity));
  const summary = event.v52s_joint_budget_receipt_summary;
  summary.phase_evaluations += 1;
  if (summary.last_receipt !== row.receipt) { summary.unique_receipts += 1; summary.last_receipt = row.receipt; }
  const sides = legs.map(v52sSide);
  const knownSides = sides.filter((side) => side.state === "BOUGHT_SIDE" ? Number.isInteger(side.entry_cents) : side.state === "STANDING_SIDE" && Number.isInteger(side.default_target_cents));
  if (knownSides.length < 2) {
    summary.vacuous_unset_counterpart_evaluations += 1;
    summary.digest.update(`${row.receipt}|${row.ts}|${cause}|VACUOUS_UNSET_COUNTERPART\n`);
    return null;
  }
  const before = legs.map((leg) => ({ leg_identity: leg.leg_identity, target_cents: leg.credited ? leg.entry_cents : (leg.active_order?.target_cents ?? null), default_target_cents: leg.active_order?.v52s_default_target_cents ?? null }));
  const allocation = v52sMechanism.allocate(sides, { allow_lifts: allowLifts });
  const changes = [];
  for (const assigned of allocation.allocations) {
    const leg = legs.find((side) => side.leg_identity === assigned.leg_identity);
    if (!leg.active_order || !Number.isInteger(assigned.allocated_target_cents)) continue;
    const prior = leg.active_order.target_cents;
    const wasLifted = leg.active_order.v52s_lift_active === true;
    const isLifted = assigned.lift_active;
    leg.active_order.target_cents = assigned.allocated_target_cents;
    leg.active_order.v52s_lift_active = isLifted;
    leg.active_order.v52s_lift_cents = assigned.lift_cents;
    leg.active_order.v52s_depth_source_low_cents = assigned.post_onset_session_low_cents;
    if (prior !== assigned.allocated_target_cents) {
      const kind = wasLifted && !isLifted ? "V52S_YIELD_TO_SENIOR_DEFAULT" : isLifted ? "V52S_DEPTH_LIFT" : "V52S_DEFAULT_RESTORE";
      const change = { kind, event_id: event.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, cause, target_before_cents: prior, target_after_cents: assigned.allocated_target_cents, default_target_cents: assigned.default_target_cents, running_post_onset_session_low_cents: assigned.post_onset_session_low_cents, desired_depth_target_cents: assigned.desired_depth_target_cents, lift_cents: assigned.lift_cents, slack_before_lifts_cents: allocation.slack_before_lifts_cents, slack_after_lifts_cents: allocation.slack_after_lifts_cents, joint_target_sum_cents: allocation.joint_target_sum_cents, invariant_pass: allocation.invariant_pass };
      actions.push(change); changes.push(change);
    }
  }
  const after = legs.map((leg) => ({ leg_identity: leg.leg_identity, target_cents: leg.credited ? leg.entry_cents : (leg.active_order?.target_cents ?? null), default_target_cents: leg.active_order?.v52s_default_target_cents ?? null, lift_active: leg.active_order?.v52s_lift_active === true }));
  summary.lift_events += changes.filter((change) => change.kind === "V52S_DEPTH_LIFT").length;
  summary.yield_events += changes.filter((change) => change.kind === "V52S_YIELD_TO_SENIOR_DEFAULT").length;
  summary.invariant_violations += allocation.invariant_pass ? 0 : 1;
  summary.max_joint_target_sum_cents = Number.isInteger(allocation.joint_target_sum_cents) ? Math.max(summary.max_joint_target_sum_cents ?? 0, allocation.joint_target_sum_cents) : summary.max_joint_target_sum_cents;
  summary.digest.update(`${row.receipt}|${row.ts}|${cause}|${allowLifts ? 1 : 0}|${allocation.default_joint_sum_cents}|${allocation.slack_before_lifts_cents}|${allocation.slack_after_lifts_cents}|${allocation.joint_target_sum_cents}|${after.map((side) => `${side.leg_identity}:${side.target_cents}:${side.default_target_cents}:${side.lift_active ? 1 : 0}`).join(",")}\n`);
  if (changes.length && legs[0].pair_budget_record) notePairBudgetRevision(legs[0], legs[1], row, `V52S_${cause}`, legs.find((side) => side.active_order)?.active_order?.birth_license ?? null);
  return allocation;
}
function parseEt(value) {
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!m) return null;
  let hour = +m[4]; if (m[7] === "AM" && hour === 12) hour = 0; if (m[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(hour).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}
function parseCsv(text) {
  const lines = text.trimEnd().split(/\r?\n/); const header = lines.shift().split(",");
  return { header, rows: lines.filter(Boolean).map((line) => line.split(",")) };
}

function loadTape(ticker) {
  const file = path.join(privateRoot, "fit-local/ticks", `${ticker}.csv.gz`);
  ensure(fs.existsSync(file), `missing tape ${ticker}`);
  const bytes = fs.readFileSync(file);
  const parsed = parseCsv(zlib.gunzipSync(bytes).toString("utf8"));
  const ix = Object.fromEntries(parsed.header.map((value, index) => [value, index]));
  const out = [];
  for (let n = 0; n < parsed.rows.length; n += 1) {
    const values = parsed.rows[n], ts = parseEt(values[ix.ts_et]);
    if (!Number.isFinite(ts)) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bp = integer(values[ix[`bid_${level}`]]), bs = positive(values[ix[`bid_${level}_sz`]]);
      const ap = integer(values[ix[`ask_${level}`]]), as = positive(values[ix[`ask_${level}_sz`]]);
      if (bp !== null && bs !== null) bids.push([bp, bs]);
      if (ap !== null && as !== null) asks.push([ap, as]);
    }
    if (!bids.length || !asks.length) continue;
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    const bidDepth = bids.reduce((sum, x) => sum + x[1], 0), askDepth = asks.reduce((sum, x) => sum + x[1], 0);
    out.push({ kind: "BOOK", ticker, ts, ordinal: n + 2, receipt: `${ticker}.csv.gz#row-${n + 2}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_bid_size: bids[0][1], top_ask_size: asks[0][1], bid_depth_5: bidDepth, ask_depth_5: askDepth, depth_ratio: bidDepth / (bidDepth + askDepth), last_trade: integer(values[ix.last_trade]) });
  }
  out.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  let ask = null, askSince = null;
  for (const row of out) { if (row.ask !== ask) { ask = row.ask; askSince = row.ts; } row.ask_dwell_seconds = row.ts - askSince; }
  return { rows: out, sha256: shaBytes(bytes), bytes: bytes.length };
}

async function loadPrints(tickerBounds) {
  const file = path.join(privateRoot, "fit-local/prints.jsonl");
  ensure(fs.existsSync(file), "missing private prints");
  const hash = crypto.createHash("sha256"), byTicker = new Map([...tickerBounds].map(([ticker]) => [ticker, []]));
  const seen = new Map([...tickerBounds].map(([ticker]) => [ticker, new Set()]));
  let rawRows = 0, admitted = 0, duplicates = 0;
  const input = fs.createReadStream(file, { highWaterMark: 1024 * 1024 });
  input.on("data", (chunk) => hash.update(chunk));
  const rl = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of rl) {
    if (!line) continue;
    rawRows += 1;
    const row = JSON.parse(line), bound = tickerBounds.get(row.ticker);
    if (!bound || !row.true_print) continue;
    const ts = Date.parse(row.exchange_ts) / 1000;
    if (!Number.isFinite(ts) || ts < bound.left || ts > bound.right) continue;
    if (!row.trade_id || seen.get(row.ticker).has(row.trade_id)) { duplicates += 1; continue; }
    seen.get(row.ticker).add(row.trade_id);
    admitted += 1;
    byTicker.get(row.ticker).push({ kind: "PRINT", ticker: row.ticker, ts, ordinal: admitted, receipt: row.receipt_id, price: integer(row.price_cents), size: positive(row.size), taker_side: row.taker_side, taker_book_side: row.taker_book_side, trade_id: row.trade_id });
  }
  for (const rows of byTicker.values()) rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  return { byTicker, receipt: { path_class: "PRIVATE_FIT_DEVELOPMENT_PRINTS_HASH_ONLY", sha256: hash.digest("hex"), bytes: fs.statSync(file).size, raw_rows: rawRows, admitted_unique_v36_window_prints: admitted, duplicate_trade_id_rows_rejected: duplicates } };
}

function armSibling(sibling, filled, row, actions, base) {
  sibling.pair_cap_cents = 99 - filled.entry_cents;
  actions.push({ kind: "PAIR_ARM", event_id: sibling.event_id, leg_identity: sibling.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, first_fill_cents: filled.entry_cents, pair_cap_cents: sibling.pair_cap_cents });
  if (sibling.active_order && sibling.active_order.target_cents > sibling.pair_cap_cents) {
    const prior = sibling.active_order.target_cents;
    if (policy.lawfulCent(sibling.pair_cap_cents)) {
      const priorOrder = sibling.active_order;
      sibling.active_order = { ...priorOrder, target_cents: sibling.pair_cap_cents, ...(base.v52s_enabled ? { v52s_default_target_cents: Math.min(priorOrder.v52s_default_target_cents ?? prior, sibling.pair_cap_cents), v52s_lift_active: false, v52s_lift_cents: 0 } : {}), action_ts: row.ts, action_receipt: row.receipt, source_state: "PAIR_CAP" };
      actions.push({ kind: "PAIR_CAP_REPRICE", event_id: sibling.event_id, leg_identity: sibling.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, prior_target_cents: prior, target_cents: sibling.pair_cap_cents, birth_license: priorOrder.birth_license ?? null, judgment_gate: isV52 ? { enabled: true, verdict: "LICENSED_EXISTING_REST_PAIR_CAP_REPRICE" } : null });
    } else {
      sibling.active_order = null;
      actions.push({ kind: "PAIR_CAP_CANCEL", event_id: sibling.event_id, leg_identity: sibling.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, prior_target_cents: prior });
    }
  }
  notePairBudgetRevision(filled, sibling, row, "BOUGHT_SIDE_CREDIT_AND_PAIR_CAP_ARM", filled.active_order?.birth_license ?? null);
}

function fillLeg(leg, sibling, row, fillClass, actions, base, normalizedClauses = {}) {
  leg.credited = true; leg.entry_cents = leg.active_order.target_cents; leg.action_timestamp_epoch = leg.active_order.action_ts; leg.fill_timestamp_epoch = row.ts; leg.fill_class = fillClass; leg.fill_source_state = leg.active_order.source_state; leg.terminal_reason = fillClass;
  if (leg.active_order.gap_credit) {
    leg.gap_credit_fill = { ...leg.active_order.gap_credit, fill_timestamp_epoch: row.ts, fill_receipt: row.receipt, fill_class: fillClass, entry_cents: leg.entry_cents };
  }
  actions.push({ kind: "FILL", event_id: leg.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, entry_cents: leg.entry_cents, fill_class: fillClass, fill_source_state: leg.fill_source_state, evidence: row.kind === "PRINT" ? { kind: "PRINT", trade_id: row.trade_id, price_cents: row.price, size: row.size, taker_side: row.taker_side, taker_book_side: row.taker_book_side } : { kind: "QUOTE_TOUCH", bid: row.bid, ask: row.ask, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size } });
  armSibling(sibling, leg, row, actions, base);
  releaseV45GuardAtSiblingCredit(sibling, leg, row, actions, base, normalizedClauses);
  if (base.v52s_enabled) reconcileV52s(v52sEventView(leg, sibling), row, actions, base, "POST_CREDIT_PAIR_CAP_REALLOCATE", true);
}

function takeLeg(leg, sibling, row, actions, base, decision) {
  leg.credited = true; leg.entry_cents = row.ask; leg.action_timestamp_epoch = row.ts; leg.fill_timestamp_epoch = row.ts; leg.fill_class = "PROVEN_TAKER_V36_MATURE_EVIDENCE_FLOOR"; leg.fill_source_state = leg.last_combined_state; leg.terminal_reason = leg.fill_class;
  leg.active_order = null;
  actions.push({ kind: "FILL", event_id: leg.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, entry_cents: leg.entry_cents, fill_class: leg.fill_class, fill_source_state: leg.fill_source_state, decision_reason: decision.reason, evidence: { kind: "DISPLAYED_ASK_TAKE", bid: row.bid, ask: row.ask, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size } });
  armSibling(sibling, leg, row, actions, base);
}

function receiptObservation(row) {
  return { bid: row.bid, ask: row.ask, last_traded: row.last_trade, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size, bid_depth_5: row.bid_depth_5, ask_depth_5: row.ask_depth_5 };
}

function noteV42Guard(leg, decision, row, base, actions, triggerLegIdentity) {
  if (!decision.guard) return;
  leg.deep_gap_guard_evaluations += 1;
  const withheld = Boolean(decision.guard.withheld);
  if (withheld) leg.deep_gap_withheld_evaluations += 1;
  if (withheld && !leg.deep_gap_withhold_active) {
    leg.deep_gap_withhold_episodes += 1;
    leg.deep_gap_first_withhold ||= { ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, guard: decision.guard, v41_decision: decision.v41_decision };
    actions.push({ kind: "DEEP_GAP_WITHHOLD_START", event_id: base.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, guard: decision.guard, v41_action: decision.v41_decision?.action ?? null, v41_target_cents: decision.v41_decision?.target_cents ?? null });
  }
  if (!withheld && leg.deep_gap_withhold_active) {
    leg.deep_gap_lifts += 1;
    leg.deep_gap_last_lift = { ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, guard: decision.guard, v41_decision: decision.v41_decision };
    actions.push({ kind: "DEEP_GAP_WITHHOLD_LIFT", event_id: base.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, guard: decision.guard, v41_action: decision.v41_decision?.action ?? null, v41_target_cents: decision.v41_decision?.target_cents ?? null });
  }
  leg.deep_gap_withhold_active = withheld;
  if (withheld) leg.deep_gap_last_withhold = { ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, guard: decision.guard, v41_decision: decision.v41_decision };
}

function applyRestDecision(leg, sibling, row, decision, combinedState, detail, actions, base, triggerLegIdentity) {
  if (["PLACE_REST", "REPRICE_REST"].includes(decision.action)) {
    leg.active_order = { target_cents: decision.target_cents, ...(base.v52s_enabled ? { v52s_default_target_cents: decision.target_cents, v52s_lift_active: false, v52s_lift_cents: 0 } : {}), action_ts: row.ts, action_receipt: row.receipt, source_state: combinedState, ...(decision.gap_credit?.authorized ? { gap_credit: { ...decision.gap_credit, event_id: base.event_id, leg_identity: leg.leg_identity, authorization_timestamp_epoch: row.ts, authorization_receipt: row.receipt } } : {}), ...(decision.evidenced_standing ? { evidenced_standing: decision.evidenced_standing } : {}), ...(decision.doctrine_standing ? { doctrine_standing: decision.doctrine_standing } : {}), ...(decision.birth_license ? { birth_license: decision.birth_license } : {}) };
    leg.first_action ||= detail;
    actions.push({ kind: decision.gap_credit?.authorized ? "GAP_CREDIT_REPRICE_DOWN" : decision.action, event_id: base.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, target_cents: decision.target_cents, state: combinedState, reason: decision.reason, pulse_floor_cents: detail?.pulse_floor?.floor_cents ?? null, guard: decision.guard ?? null, gap_credit: decision.gap_credit ?? null, evidenced_standing: decision.evidenced_standing ?? null, doctrine_standing: decision.doctrine_standing ?? null, birth_license: decision.birth_license ?? null, judgment_gate: decision.judgment_gate ?? null });
  } else if (decision.action === "CANCEL_REST") {
    leg.active_order = null;
    actions.push({ kind: "CANCEL_REST", event_id: base.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, reason: decision.reason, guard: decision.guard ?? null });
  } else if (decision.action === "TAKE") {
    leg.first_action ||= detail;
    takeLeg(leg, sibling, row, actions, base, decision);
  }
  if (["PLACE_REST", "REPRICE_REST", "CANCEL_REST"].includes(decision.action)) notePairBudgetRevision(leg, sibling, row, decision.action, decision.birth_license ?? null);
}

function releaseV45GuardAtSiblingCredit(withheldLeg, creditedLeg, row, actions, base, normalizedClauses) {
  if (!normalizedClauses.release_guard_on_sibling_credit || !withheldLeg.deep_gap_withhold_active || withheldLeg.credited) return;
  const before = withheldLeg.active_order?.target_cents ?? null;
  const ownInputs = withheldLeg.last_placement_inputs;
  withheldLeg.post_credit_guard_release_attempts += 1;
  if (!ownInputs) {
    withheldLeg.post_credit_guard_release_no_book += 1;
    actions.push({ kind: "POST_CREDIT_GUARD_RELEASE_NO_OWN_BOOK", event_id: base.event_id, leg_identity: withheldLeg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, credited_sibling_leg_identity: creditedLeg.leg_identity, sibling_entry_cents: creditedLeg.entry_cents, fixed_pair_cap_cents: withheldLeg.pair_cap_cents });
    withheldLeg.deep_gap_withhold_active = false;
    return;
  }
  const inputs = { ...ownInputs, activeTarget: before, pairCap: withheldLeg.pair_cap_cents, siblingBestAsk: creditedLeg.prior_book?.ask ?? ownInputs.siblingBestAsk, siblingCredited: true, ...(normalizedClauses.joint_target_conservation ? { siblingEntryCents: creditedLeg.entry_cents, siblingStandingTarget: null } : {}), clauses: normalizedClauses };
  let decision = policy.decide(inputs);
  ensure(decision.guard === null, `V45 guard authority survived sibling credit ${withheldLeg.leg_identity}`);
  // V52n previously documented this inherited wrapper behavior: later frozen
  // layers can preserve guard=null while dropping V45's receipt bit.  Restore
  // the bit only; action, target, predicates, and order state remain unchanged.
  if (decision.guard_authority_terminated !== true) {
    ensure(base.v52s_enabled || isV54, `V45 guard termination receipt missing ${withheldLeg.leg_identity}`);
    decision = { ...decision, guard_authority: "TERMINATED_AT_SIBLING_CREDIT", guard_authority_terminated: true, receipt_only_inherited_guard_stamp_repair: true };
  }
  withheldLeg.deep_gap_withhold_active = false;
  withheldLeg.deep_gap_lifts += 1;
  withheldLeg.post_credit_guard_releases += 1;
  const release = { ...clockFields(row.ts, base), receipt: row.receipt, credited_sibling_leg_identity: creditedLeg.leg_identity, sibling_entry_cents: creditedLeg.entry_cents, fixed_pair_cap_cents: withheldLeg.pair_cap_cents, prior_withhold: withheldLeg.deep_gap_last_withhold, own_book_receipt: ownInputs.book.receipt, own_book: receiptObservation(ownInputs.book), order_before_cents: before, decision, order_after_cents: null };
  actions.push({ kind: "POST_CREDIT_GUARD_AUTHORITY_TERMINATED", event_id: base.event_id, leg_identity: withheldLeg.leg_identity, ...release });
  const detail = { ...clockFields(row.ts, base), receipt: row.receipt, ordinal: row.ordinal, observation: receiptObservation(ownInputs.book), sibling_observation: creditedLeg.prior_book ? receiptObservation(creditedLeg.prior_book) : null, combined_state: ownInputs.state, pulse_floor: { floor_cents: ownInputs.pulseFloor }, pair_cap_cents: withheldLeg.pair_cap_cents, order_before_cents: before, decision, post_credit_guard_release: true, order_after_cents: null };
  applyRestDecision(withheldLeg, creditedLeg, row, decision, ownInputs.state, detail, actions, base, creditedLeg.leg_identity);
  detail.order_after_cents = withheldLeg.active_order?.target_cents ?? null;
  release.order_after_cents = detail.order_after_cents;
  withheldLeg.post_credit_guard_release = release;
  withheldLeg.last_decision = detail;
}

function reevaluateV42WithSiblingBook(withheldLeg, triggeringLeg, row, actions, base) {
  if (row.kind !== "BOOK" || !withheldLeg.deep_gap_withhold_active || !withheldLeg.last_placement_inputs || withheldLeg.credited) return;
  const before = withheldLeg.active_order?.target_cents ?? null;
  const incumbentBefore = base.v52s_enabled ? (withheldLeg.active_order?.v52s_default_target_cents ?? before) : before;
  const siblingStanding = base.v52s_enabled ? (triggeringLeg.active_order?.v52s_default_target_cents ?? triggeringLeg.active_order?.target_cents ?? null) : (triggeringLeg.active_order?.target_cents ?? null);
  const inputs = { ...withheldLeg.last_placement_inputs, activeTarget: incumbentBefore, pairCap: withheldLeg.pair_cap_cents, siblingBestAsk: row.ask, ...(withheldLeg.last_placement_inputs.clauses?.joint_target_conservation ? { siblingStandingTarget: siblingStanding, siblingEntryCents: triggeringLeg.entry_cents, siblingCredited: triggeringLeg.credited } : {}) };
  const decision = policy.decide(inputs);
  noteV42Guard(withheldLeg, decision, row, base, actions, triggeringLeg.leg_identity);
  if (decision.guard?.withheld) return;
  const ownBook = withheldLeg.last_placement_inputs.book;
  const detail = { ...clockFields(row.ts, base), receipt: row.receipt, ordinal: row.ordinal, observation: receiptObservation(ownBook), sibling_observation: receiptObservation(row), combined_state: withheldLeg.last_placement_inputs.state, pulse_floor: { floor_cents: withheldLeg.last_placement_inputs.pulseFloor }, pair_cap_cents: withheldLeg.pair_cap_cents, order_before_cents: before, decision, re_evaluated_on_sibling_receipt: true, order_after_cents: null };
  if (base.v52s_enabled && ["PLACE_REST", "REPRICE_REST", "CANCEL_REST", "TAKE"].includes(decision.action)) reconcileV52s(v52sEventView(withheldLeg, triggeringLeg), row, actions, base, "PRE_CROSS_LEG_SENIOR_TARGET_MUTATION_YIELD", false);
  applyRestDecision(withheldLeg, triggeringLeg, row, decision, withheldLeg.last_placement_inputs.state, detail, actions, base, triggeringLeg.leg_identity);
  if (base.v52s_enabled) reconcileV52s(v52sEventView(withheldLeg, triggeringLeg), row, actions, base, "POST_CROSS_LEG_SENIOR_TARGET_MUTATION_REALLOCATE", true);
  detail.order_after_cents = withheldLeg.active_order?.target_cents ?? null;
  withheldLeg.last_decision = detail;
}

function simulate(base, tapes, prints, mode, clauses = {}) {
  const ids = Object.keys(base.legs).sort(), actions = [], joinQualifications = [];
  const causalOnsetMode = isV52CausalOnset && base.v52_onset_mode === "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT";
  const normalizedClauses = policy.normalizedClauses ? policy.normalizedClauses(clauses) : (isV42 ? { arm_at_first_evidence: false, deep_gap_guard: true, loosen_one_cent: false } : {});
  const event = { event_id: base.event_id, category: base.category, starting_price_split: base.starting_price_split, bell_confidence: base.bell_confidence, edge_source_field: base.edge_source_field, w1_left_epoch: base.left, w1_right_epoch: base.right, mode, clauses: normalizedClauses, legs: {} };
  if (normalizedClauses.joint_target_conservation) event.pair_budget_record = { event_id: base.event_id, born_at: null, current_joint_split: null, revisions: [] };
  if (base.v52s_enabled) event.v52s_joint_budget_receipt_summary = { phase_evaluations: 0, unique_receipts: 0, last_receipt: null, vacuous_unset_counterpart_evaluations: 0, lift_events: 0, yield_events: 0, invariant_violations: 0, max_joint_target_sum_cents: null, digest: crypto.createHash("sha256") };
  for (const id of ids) {
    const meta = base.legs[id], reach = meta.reach;
    event.legs[id] = { ...meta, reach: undefined, event_id: base.event_id, credited: false, entry_cents: null, fill_class: null, fill_source_state: null, action_timestamp_epoch: null, fill_timestamp_epoch: null, pair_cap_cents: null, active_order: null, prior_book: null, directional: [], pulse_visits: [], recent_trade_rows: [], prior_true_trade_low_cents: null, prior_true_trade_low_receipt: null, post_onset_true_trade_low_cents: null, post_onset_true_trade_low_receipt: null, judgment_gate_evaluations: 0, judgment_gate_posts: 0, judgment_gate_blocks: {}, judgment_first_post: null, judgment_first_block: null, judgment_trace_rows: [], exact_bid_first_receipt: new Map(), evidenced_standing_level_cents: null, evidenced_standing_authority: null, evidenced_standing_decisions: 0, evidenced_standing_first: null, evidenced_standing_last: null, pulse_floor_cents: null, pulse_floor_ever: false, current_bid_level: null, current_bid_since: null, current_bid_last_trade_hit: false, current_bid_last_trade_hit_receipt: null, book_last_trade_hits_by_level: new Map(), seller_hits_by_level: new Map(), persistent_join_level: null, persistent_join_receipt: null, persistent_join_evidence_receipt: null, persistent_join_timestamp_epoch: null, post_join_book_last_trade_receipts: 0, post_join_certified_seller_hits_at_level: 0, running_seller_hit_low: null, running_qualified_ask_low: null, running_qualified_ask_low_unabsorbed: false, running_qualified_ask_low_reformed_nonfalling: false, latest_new_low_evidence_ts: null, downward_evidence_rows: [], last_combined_state: "SETTLED", last_disagreement: false, classifier_rows: 0, classifier_state_counts: { FALLING: 0, RISING: 0, SETTLED: 0 }, classifier_opposed_rows: 0, classifier_agreement_rows: 0, decision_count: 0, state_counts: { FALLING: 0, RISING: 0, SETTLED: 0 }, action_counts: {}, disagreement_count: 0, first_decision: null, last_decision: null, first_action: null, terminal_reason: null, last_placement_inputs: null, deep_gap_guard_evaluations: 0, deep_gap_withheld_evaluations: 0, deep_gap_withhold_episodes: 0, deep_gap_lifts: 0, deep_gap_withhold_active: false, deep_gap_first_withhold: null, deep_gap_last_withhold: null, deep_gap_last_lift: null, post_credit_guard_release_attempts: 0, post_credit_guard_releases: 0, post_credit_guard_release_no_book: 0, post_credit_guard_reapplication_prevented_receipts: 0, post_credit_guard_release: null, gap_credit_eligible_receipts: 0, gap_credit_authorized_walks: 0, gap_credit_sibling_uncredited_refusals: 0, gap_credit_no_lawful_reprice: 0, gap_credit_first: null, gap_credit_last: null, gap_credit_fill: null, union_reach_cents: reach.union_reach_cents, union_first_evidence_timestamp_epoch: reach.union_first_evidence_timestamp_epoch, reach_sources: reach.union_sources, reach_inside_v36_edge: reach.union_first_evidence_timestamp_epoch >= base.left && reach.union_first_evidence_timestamp_epoch <= base.right, reach_snapshot: null };
    event.legs[id].v54_license_spans = [];
    event.legs[id].v54_assertion_failures = {};
    if (isV52ReadAuthority) Object.assign(event.legs[id], {
      post_onset_observed_min_cents: null,
      post_onset_observed_max_cents: null,
      post_onset_first_observation: null,
      post_onset_last_observation: null,
      ...(isV52FullRead ? { post_onset_read_state: policy.emptyReadState(meta.v52_onset?.selected?.timestamp_epoch ?? null) } : {}),
      ...(isV52MacroRecognition ? { v52m_shape_state: policy.emptyShapeState() } : {}),
      ...(isV53 ? { v53_state: policy.emptyLegState(meta.v52_onset?.selected?.timestamp_epoch ?? null) } : {}),
    });
    if (event.pair_budget_record) event.legs[id].pair_budget_record = event.pair_budget_record;
    if (event.v52s_joint_budget_receipt_summary) event.legs[id].v52s_joint_budget_receipt_summary = event.v52s_joint_budget_receipt_summary;
  }
  const timeline = [];
  for (const id of ids) {
    for (const row of tapes.get(id)) timeline.push({ ...row, leg_id: id });
    for (const row of prints.get(id)) timeline.push({ ...row, leg_id: id });
  }
  timeline.sort((a, b) => a.ts - b.ts || (a.kind === "PRINT" ? 0 : 1) - (b.kind === "PRINT" ? 0 : 1) || a.ordinal - b.ordinal || a.leg_id.localeCompare(b.leg_id));
  for (const row of timeline) {
    if (row.ts < base.left || row.ts > base.right) continue;
    const leg = event.legs[row.leg_id], sibling = event.legs[ids.find((id) => id !== row.leg_id)];
    if (base.v52s_enabled) reconcileV52s(event, row, actions, base, "PRE_MARKET_RECEIPT", true);
    if ((isV40 || isMaker41) && Number.isFinite(leg.persistent_join_timestamp_epoch) && row.ts > leg.persistent_join_timestamp_epoch) {
      if (row.kind === "PRINT" && row.taker_side === "no" && row.price === leg.persistent_join_level) leg.post_join_certified_seller_hits_at_level += 1;
      if (row.kind === "BOOK" && row.bid === leg.persistent_join_level && row.last_trade === leg.persistent_join_level) leg.post_join_book_last_trade_receipts += 1;
    }
    if (leg.credited) {
      if (normalizedClauses.deep_gap_guard && row.kind === "BOOK") {
        leg.prior_book = row;
        reevaluateV42WithSiblingBook(sibling, leg, row, actions, base);
        if (base.v52s_enabled) reconcileV52s(event, row, actions, base, "POST_CREDITED_SIDE_BOOK_REEVALUATION", true);
      }
      continue;
    }
    if (isV52MacroRecognition && row.kind === "PRINT") policy.observeTruePrint(leg.v52m_shape_state, row);
    if (isV52ReadAuthority && leg.v52_onset?.selected && row.ts >= leg.v52_onset.selected.timestamp_epoch) {
      const observed = row.kind === "PRINT" ? [row.price] : [row.bid, row.ask];
      for (const cents of observed.filter(Number.isInteger)) {
        leg.post_onset_observed_min_cents = leg.post_onset_observed_min_cents === null ? cents : Math.min(leg.post_onset_observed_min_cents, cents);
        leg.post_onset_observed_max_cents = leg.post_onset_observed_max_cents === null ? cents : Math.max(leg.post_onset_observed_max_cents, cents);
      }
      const observation = { timestamp_epoch: row.ts, receipt: row.receipt, kind: row.kind, prices_cents: observed.filter(Number.isInteger) };
      leg.post_onset_first_observation ||= observation;
      leg.post_onset_last_observation = observation;
      if (normalizedClauses.full_post_onset_evidence_horizon) policy.observePostOnsetEvidence(leg.post_onset_read_state, row);
      if (isV53) policy.observePostOnset(leg.v53_state, row);
    }
    if (row.kind === "PRINT") {
      if (isV5304) policy.observeRiserPrint(leg.v53_state, row, leg.prior_book, sibling.prior_book, leg.last_combined_state);
      const selectedOnset = leg.v52_onset?.selected;
      if (isV52 && selectedOnset && row.ts >= selectedOnset.timestamp_epoch
          && (leg.post_onset_true_trade_low_cents === null || row.price < leg.post_onset_true_trade_low_cents)) {
        leg.post_onset_true_trade_low_cents = row.price;
        leg.post_onset_true_trade_low_receipt = row.receipt;
      }
      leg.recent_trade_rows.push({ ts: row.ts, ordinal: row.ordinal, price: row.price, receipt: row.receipt, trade_id: row.trade_id });
      leg.recent_trade_rows = leg.recent_trade_rows.filter((print) => print.ts <= row.ts && print.ts >= row.ts - policy.LOOKBACK_SECONDS);
      if (mode === "STRICT_PRINT_CROSS" && policy.strictPrintCross(leg.active_order, row)) {
        fillLeg(leg, sibling, row, "STRICT_PRINT_CROSS_SELLER_AGGRESSED_SIZE_FIVE", actions, base, normalizedClauses); continue;
      }
      if (mode === "MARKET_TRADES_AS_TRUTH" && policy.tradeTruthCredit(leg.active_order, row)) {
        fillLeg(leg, sibling, row, "MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST", actions, base, normalizedClauses); continue;
      }
      if (mode === "MARKET_UNION_REACH" && leg.active_order && policy.strictPrintCross(leg.active_order, row)) {
        fillLeg(leg, sibling, row, "MARKET_REACH_PRINT_CROSS", actions, base, normalizedClauses); continue;
      }
      if (mode === "MARKET_UNION_REACH" && policy.tradedAtLevel(leg.active_order, row)) {
        fillLeg(leg, sibling, row, "MARKET_REACH_TRADED_AT_LEVEL", actions, base, normalizedClauses); continue;
      }
      if (leg.prior_true_trade_low_cents === null || row.price < leg.prior_true_trade_low_cents) {
        leg.prior_true_trade_low_cents = row.price;
        leg.prior_true_trade_low_receipt = row.receipt;
      }
      if (row.taker_side === "no") {
        const sellerHitMadeNewLow = leg.running_seller_hit_low === null || row.price < leg.running_seller_hit_low;
        leg.seller_hits_by_level.set(row.price, (leg.seller_hits_by_level.get(row.price) || 0) + 1);
        leg.running_seller_hit_low = leg.running_seller_hit_low === null ? row.price : Math.min(leg.running_seller_hit_low, row.price);
        leg.downward_evidence_rows.push({ ts: row.ts, ordinal: row.ordinal, price: row.price, kind: "SELLER_HIT_TRUE_PRINT", receipt: row.receipt });
        if (sellerHitMadeNewLow) leg.latest_new_low_evidence_ts = row.ts;
      }
      if (row.taker_side === "no" || row.taker_side === "yes") leg.directional = [{ ts: row.ts, ordinal: row.ordinal, direction: row.taker_side === "no" ? "FALLING" : "RISING", kind: row.taker_side === "no" ? "SELLER_HIT_PRINT" : "BUYER_LIFT_PRINT", receipt: row.receipt }];
      if (base.v52s_enabled) reconcileV52s(event, row, actions, base, "POST_PRINT_DEPTH_EVIDENCE_FOR_NEXT_RECEIPT", true);
      continue;
    }
    if (mode === "MARKET_UNION_REACH" && policy.quoteTouch(leg.active_order, row)) {
      fillLeg(leg, sibling, row, "MARKET_REACH_QUOTE_TOUCH_10S_SIZE_FIVE", actions, base, normalizedClauses);
      if (normalizedClauses.deep_gap_guard) { leg.prior_book = row; reevaluateV42WithSiblingBook(sibling, leg, row, actions, base); }
      continue;
    }
    leg.recent_trade_rows = leg.recent_trade_rows.filter((print) => print.ts <= row.ts && print.ts >= row.ts - policy.LOOKBACK_SECONDS);
    const recentTradeLow = leg.recent_trade_rows.length ? Math.min(...leg.recent_trade_rows.map((print) => print.price)) : null;
    const prior = leg.prior_book, newLowAsk = Boolean(prior && row.ask < prior.ask), newHighBid = Boolean(prior && row.bid > prior.bid);
    const priorExactBidEvidence = leg.exact_bid_first_receipt.get(row.bid) ?? null;
    if (leg.current_bid_level !== row.bid) {
      leg.current_bid_level = row.bid;
      leg.current_bid_since = row.ts;
      leg.current_bid_last_trade_hit = false;
      leg.current_bid_last_trade_hit_receipt = null;
    }
    if (!leg.exact_bid_first_receipt.has(row.bid)) leg.exact_bid_first_receipt.set(row.bid, { level_cents: row.bid, receipt: row.receipt, timestamp_epoch: row.ts });
    if (row.last_trade === row.bid) {
      leg.current_bid_last_trade_hit = true;
      leg.current_bid_last_trade_hit_receipt ||= row.receipt;
      leg.book_last_trade_hits_by_level.set(row.bid, (leg.book_last_trade_hits_by_level.get(row.bid) || 0) + 1);
    }
    if (!prior || row.ask !== prior.ask) leg.pulse_visits.push({ ts: row.ts, ordinal: row.ordinal, ask: row.ask, receipt: row.receipt });
    leg.pulse_visits = policy.trimPulseVisits(leg.pulse_visits, row.ts);
    const pulse = policy.trailingPulseFloor(leg.pulse_visits, row.ts);
    leg.pulse_floor_cents = pulse.floor_cents; if (Number.isInteger(pulse.floor_cents)) leg.pulse_floor_ever = true;
    if (newLowAsk && newHighBid) leg.directional = [{ ts: row.ts, ordinal: row.ordinal, direction: "SETTLED", kind: "QUOTE_PATH_INTERNAL_CONFLICT", receipt: row.receipt }];
    else if (newLowAsk) leg.directional = [{ ts: row.ts, ordinal: row.ordinal, direction: "FALLING", kind: "NEW_LOW_ASK", receipt: row.receipt }];
    else if (newHighBid) leg.directional = [{ ts: row.ts, ordinal: row.ordinal, direction: "RISING", kind: "NEW_HIGH_BID", receipt: row.receipt }];
    const quote = normalizedClauses.full_post_onset_evidence_horizon ? policy.fullPostOnsetRead(leg.post_onset_read_state, row) : policy.quotePathState(leg.directional, row.ts);
    const pressure = policy.pressureState(row.depth_ratio);
    const combinedRaw = policy.combineState(quote, pressure);
    const palantir = normalizedClauses.palantir_priors ? policy.continuousConsultation({ category: base.category, priceRegion: leg.price_region, startingPriceSplit: base.starting_price_split, combinedState: combinedRaw.state, quoteState: quote.state, pressureState: pressure, siblingState: sibling.last_combined_state, siblingReadEvidence: sibling.last_read_evidence ?? null, row, clauses: normalizedClauses }) : null;
    const referee = normalizedClauses.disagreement_referee ? policy.adjudicateDisagreement({ quote, pressure, row, readState: leg.post_onset_read_state, siblingState: sibling.last_combined_state, palantir }) : null;
    const combinedBase = normalizedClauses.full_post_onset_evidence_horizon ? { ...combinedRaw, authority: policy.fullPostOnsetAuthority(combinedRaw) } : combinedRaw;
    const combined = referee?.resolved ? { ...combinedBase, state: referee.winner.reading, authority: referee.winner.evidence_class === "VALIDATED_N5_PRIOR" ? "V52E_N5_PRIOR_INFORMED_TIE_ADJUDICATION" : "V52D_DISAGREEMENT_REFEREE_STRICTLY_STRONGER_BACKING", disagreement_adjudication: referee } : referee ? { ...combinedBase, disagreement_adjudication: referee } : combinedBase;
    const fullReadEvidence = quote.full_post_onset_evidence?.last_directional_evidence ?? quote.full_post_onset_evidence?.last_evidence ?? null;
    const directionalEvidence = normalizedClauses.full_post_onset_evidence_horizon ? (fullReadEvidence ? { ts: fullReadEvidence.timestamp_epoch, receipt: fullReadEvidence.receipt, kind: fullReadEvidence.kind } : null) : leg.directional.find((evidence) => evidence.receipt === quote.receipt) ?? null;
    leg.last_combined_state = combined.state;
    if (isV5304) policy.observeRiserBook(leg.v53_state, row, prior, combined.state);
    leg.last_read_evidence = { state: combined.state, receipt: quote.receipt ?? row.receipt, quote_path_state: quote.state, pressure_state: pressure, directional_evidence_timestamp_epoch: directionalEvidence?.ts ?? null, directional_evidence_receipt: directionalEvidence?.receipt ?? null, directional_evidence_kind: directionalEvidence?.kind ?? null };
    leg.last_disagreement = combined.disagreement;
    leg.classifier_rows += 1;
    leg.classifier_state_counts[combined.state] += 1;
    if (combined.disagreement) leg.classifier_opposed_rows += 1;
    if (combined.authority === "QUOTE_PATH_AND_JUL6_PRESSURE_AGREE") leg.classifier_agreement_rows += 1;
    const joinLevelBeforeReceipt = leg.persistent_join_level;
    const v41Join = isMaker41 ? policy.persistenceJoinUpdate({ state: combined.state, bid: row.bid, residencySeconds: row.ts - leg.current_bid_since, currentJoinLevel: joinLevelBeforeReceipt, clauses: normalizedClauses }) : null;
    const persistentLevelTrigger = isMaker41 ? v41Join.armed : isPlacementStack && row.ts - leg.current_bid_since >= policy.PERSISTENT_LEVEL_SECONDS && leg.current_bid_last_trade_hit;
    if (isPlacementStack && persistentLevelTrigger) {
      if (isMaker41 ? v41Join.changed : leg.persistent_join_level === null || row.bid < leg.persistent_join_level) {
        leg.persistent_join_level = row.bid;
        leg.persistent_join_receipt = row.receipt;
        leg.persistent_join_evidence_receipt = isMaker41 ? row.receipt : leg.current_bid_last_trade_hit_receipt;
        leg.persistent_join_timestamp_epoch = row.ts;
        leg.post_join_book_last_trade_receipts = 0;
        leg.post_join_certified_seller_hits_at_level = 0;
      }
    }
    if (policy.qualifyingAskEvidence && policy.qualifyingAskEvidence(row)) {
      if (leg.running_qualified_ask_low === null || row.ask < leg.running_qualified_ask_low) {
        leg.running_qualified_ask_low = row.ask;
        leg.running_qualified_ask_low_unabsorbed = combined.state === "FALLING";
        leg.running_qualified_ask_low_reformed_nonfalling = combined.state !== "FALLING";
        leg.latest_new_low_evidence_ts = row.ts;
        if (combined.state === "FALLING") leg.downward_evidence_rows.push({ ts: row.ts, ordinal: row.ordinal, price: row.ask, kind: "QUALIFYING_ASK_LOW_CREATED_WHILE_FALLING", receipt: row.receipt });
      }
    }
    leg.downward_evidence_rows = leg.downward_evidence_rows.filter((evidence) => evidence.ts <= row.ts && evidence.ts >= row.ts - policy.LOOKBACK_SECONDS);
    const receiptLocalEvidenceFloor = leg.downward_evidence_rows.length ? Math.min(...leg.downward_evidence_rows.map((evidence) => evidence.price)) : null;
    const runningFloors = [leg.running_seller_hit_low, leg.running_qualified_ask_low].filter(Number.isInteger);
    const runningEvidenceFloor = runningFloors.length ? Math.min(...runningFloors) : null;
    const floorMature = Number.isFinite(leg.latest_new_low_evidence_ts) && row.ts - leg.latest_new_low_evidence_ts >= policy.LOOKBACK_SECONDS;
    const activeEvidenceFloor = policy.matureDirectionalEvidenceFloor ? policy.matureDirectionalEvidenceFloor({ state: combined.state, runningEvidenceFloor, receiptLocalEvidenceFloor, reformedQualifyingAskFloor: leg.running_qualified_ask_low, reformedQualifyingAskAuthority: leg.running_qualified_ask_low_reformed_nonfalling, floorMature }) : null;
    const causalOwnReachLowCandidates = [leg.running_seller_hit_low, leg.running_qualified_ask_low].filter(Number.isInteger);
    const causalOwnReachLow = causalOwnReachLowCandidates.length ? Math.min(...causalOwnReachLowCandidates) : null;
    const wtaInverseFalling = isPlacementStack && combined.state === "RISING" && String(base.category).startsWith("WTA") && sibling.last_combined_state === "FALLING";
    const before = leg.active_order?.target_cents ?? null;
    const incumbentBefore = base.v52s_enabled ? (leg.active_order?.v52s_default_target_cents ?? before) : before;
    const askGapCents = prior && Number.isInteger(prior.ask) && Number.isInteger(row.ask) ? prior.ask - row.ask : null;
    const doctrineP = leg.v49b_doctrine?.level_cents;
    const doctrineEvidence = [];
    if (isV49b && Number.isInteger(doctrineP)) {
      if (Number.isInteger(leg.prior_true_trade_low_cents) && leg.prior_true_trade_low_cents <= doctrineP) doctrineEvidence.push({ source: "PRIOR_TRUE_TRADE_AT_OR_BELOW_P", price_cents: leg.prior_true_trade_low_cents, receipt: leg.prior_true_trade_low_receipt });
      const exactBid = leg.exact_bid_first_receipt.get(doctrineP);
      if (exactBid && exactBid.timestamp_epoch <= row.ts) doctrineEvidence.push({ source: "OWN_BEST_BID_REACHED_EXACT_P", price_cents: doctrineP, receipt: exactBid.receipt, timestamp_epoch: exactBid.timestamp_epoch });
      if (Number.isFinite(leg.v49b_doctrine.frozen_evidence_timestamp_epoch) && leg.v49b_doctrine.frozen_evidence_timestamp_epoch <= row.ts) doctrineEvidence.push({ source: "HASH_BOUND_PRE_WINDOW_CAUSAL_EVIDENCE", evidence_type: leg.v49b_doctrine.frozen_evidence_type, timestamp_epoch: leg.v49b_doctrine.frozen_evidence_timestamp_epoch, binding_commit: IDENTITY_81_COMMIT });
    }
    const doctrineStanding = isV49b && leg.v49b_doctrine ? { ...leg.v49b_doctrine, authorized: doctrineEvidence.length > 0, causal_evidence: doctrineEvidence, evaluated_timestamp_epoch: row.ts, evaluated_receipt: row.receipt } : null;
    const onset = leg.v52_onset?.selected ?? null;
    const onsetReached = Boolean(onset && row.ts >= onset.timestamp_epoch);
    const ripenessSpan = (isV52Ripeness || isV52r) ? groundTruthWindowBinding.byEvent.get(base.event_id) : null;
    const anchorLeg = (isV52q || isV52r) ? ripenessSpan?.legs?.[leg.leg_id] : null;
    const macroRecognition = isV52MacroRecognition ? policy.classifyShapeState(leg.v52m_shape_state, {
      timestamp_epoch: row.ts,
      receipt: row.receipt,
      category: base.category,
      confidence_gate_enabled: clauses.recognition_confidence_gate === true,
      role_instrument_enabled: clauses.benchmarked_role_instrument === true,
      ripeness_role_binding_enabled: clauses.ripeness_role_binding === true,
      anchor_correction_enabled: clauses.anchor_correction === true,
      assembled_policy_enabled: clauses.assembled_policy === true,
      post_onset_epoch: onset?.timestamp_epoch ?? null,
      formation_end_epoch: (isV52Ripeness || isV52r) ? (clauses.anchor_correction === true ? (anchorLeg?.formation_end_epoch ?? null) : ripenessSpan?.span_start_epoch) : base.left,
      verified_span_end_epoch: (isV52Ripeness || isV52r) ? ripenessSpan?.span_end_epoch : base.right,
      scheduled_span_end_epoch: base.scheduled,
      ...((isV52q || isV52r) ? {
        published_anchor_cents: anchorLeg?.open_postformation_cents ?? null,
        published_anchor_receipt: `${groundTruthWindowBinding.binding.source_commit}:${groundTruthWindowBinding.binding.source_path}#${base.event_id}|${leg.leg_id}`,
      } : {}),
    }) : null;
    const ownDiary = leg.post_onset_true_trade_low_cents;
    const siblingDiary = sibling.post_onset_true_trade_low_cents;
    const lowsSum = Number.isInteger(ownDiary) && Number.isInteger(siblingDiary) ? ownDiary + siblingDiary : null;
    let diaryTarget = Number.isInteger(ownDiary) ? ownDiary : null;
    if (Number.isInteger(diaryTarget) && Number.isInteger(leg.pair_cap_cents)) diaryTarget = Math.min(diaryTarget, leg.pair_cap_cents);
    if (Number.isInteger(diaryTarget) && Number.isInteger(row.ask)) diaryTarget = Math.min(diaryTarget, row.ask - 1);
    if (!policy.lawfulCent(diaryTarget)) diaryTarget = null;
    const birthLicense = isV52 ? {
      onset: {
        passed: onsetReached,
        selected_candidate: causalOnsetMode ? (onsetReached ? onset.candidate : null) : (onset?.candidate ?? null),
        timestamp_epoch: causalOnsetMode ? (onsetReached ? onset.timestamp_epoch : null) : (onset?.timestamp_epoch ?? null),
        t_minus_scheduled_seconds: onset && (!causalOnsetMode || onsetReached) && Number.isFinite(base.scheduled) ? base.scheduled - onset.timestamp_epoch : null,
        t_minus_actual_bell_seconds: onset && (!causalOnsetMode || onsetReached) && Number.isFinite(base.actual_bell) ? base.actual_bell - onset.timestamp_epoch : null,
        candidates: !causalOnsetMode || onsetReached ? (leg.v52_onset?.candidates ?? null) : null,
      },
      read: {
        passed: Boolean(quote.receipt),
        state: combined.state,
        quote_path_state: quote.state,
        pressure_state: pressure,
        receipt: quote.receipt,
        evidence: quote.evidence,
        ...(normalizedClauses.full_post_onset_evidence_horizon ? { full_post_onset_evidence: quote.full_post_onset_evidence } : {}),
      },
      diary: {
        passed: Number.isInteger(ownDiary),
        own_post_onset_true_trade_low_cents: ownDiary,
        own_receipt: leg.post_onset_true_trade_low_receipt,
        sibling_post_onset_true_trade_low_cents: siblingDiary,
        sibling_receipt: sibling.post_onset_true_trade_low_receipt,
        displayed_bid_consumed: false,
      },
      coherence: {
        post_onset_running_lows_sum_cents: lowsSum,
        lows_under_par: Number.isInteger(lowsSum) && lowsSum < 100,
        disagreement_firing: combined.disagreement,
        sibling_credited: sibling.credited,
        disagreement_clear: !combined.disagreement || sibling.credited || referee?.resolved === true,
        ...(referee ? { disagreement_adjudication: referee } : {}),
      },
      level: {
        target_cents: diaryTarget,
        own_diary_cents: ownDiary,
        pair_cap_cents: leg.pair_cap_cents,
        post_only_ask_bound_cents: Number.isInteger(row.ask) ? row.ask - 1 : null,
        authority: "POST_ONSET_RUNNING_TRUE_TRADE_LOW_DIARY",
        displayed_bid_consumed: false,
        ...(isV52MacroRecognition ? { macro_recognition: macroRecognition } : {}),
        ...(isV52ReadAuthority ? {
          machine_read_evidence: {
            evaluation_timestamp_epoch: row.ts,
            evaluation_receipt: row.receipt,
            directional_evidence_timestamp_epoch: directionalEvidence?.ts ?? null,
            directional_evidence_receipt: directionalEvidence?.receipt ?? null,
            directional_evidence_kind: directionalEvidence?.kind ?? null,
            combined_state: combined.state,
            quote_path_state: quote.state,
            pressure_state: pressure,
            direction_authority: combined.authority,
            disagreement: combined.disagreement,
            post_onset_observation_bounds: {
              min_cents: leg.post_onset_observed_min_cents,
              max_cents: leg.post_onset_observed_max_cents,
              first: leg.post_onset_first_observation,
              last: leg.post_onset_last_observation,
            },
            current_book: receiptObservation(row),
            receipt_local_inputs: {
              pulse_floor_cents: pulse.floor_cents,
              persistent_join_level_cents: leg.persistent_join_level,
              causal_own_reach_low_cents: causalOwnReachLow,
              active_evidence_floor_cents: activeEvidenceFloor,
              recent_true_trade_low_cents: recentTradeLow,
              prior_true_trade_low_cents: leg.prior_true_trade_low_cents,
            },
            ...(normalizedClauses.full_post_onset_evidence_horizon ? { post_onset_read: quote.full_post_onset_evidence } : {}),
          },
        } : {}),
      },
      scavenger: { enabled: false, reason: "V52_SCAVENGER_SPECCED_OFF" },
      ...(palantir ? { palantir } : {}),
    } : null;
    const v53States = isV53 ? Object.fromEntries(ids.map((id) => [id, event.legs[id].v53_state])) : null;
    const v54GroundTruth = isV54 ? groundTruthWindowBinding.byEvent.get(base.event_id) : null;
    const v53Context = isV53 ? {
      event_id: base.event_id,
      category: base.category,
      row,
      states: v53States,
      shape_taxonomy_commit: SHAPE_TAXONOMY_COMMIT,
      shape_taxonomy_path: SHAPE_TAXONOMY_PATH,
      trd5_commit: TRD5_COMMIT,
      ...(isV54 ? {
        formation_anchors: Object.fromEntries(ids.map((id) => [id, {
          value_cents: v54GroundTruth?.legs?.[id]?.open_postformation_cents ?? null,
          formation_end_epoch: v54GroundTruth?.legs?.[id]?.formation_end_epoch ?? null,
          source_receipt: `c0056976#${base.event_id}|${id}`,
        }])),
        joint_reads: Object.fromEntries(ids.map((id) => [id, event.legs[id].last_read_evidence ?? null])),
        machine_states: Object.fromEntries(ids.map((id) => [id, event.legs[id].last_combined_state ?? null])),
        positions: Object.fromEntries(ids.map((id) => [id, {
          entry_cents: event.legs[id].credited ? event.legs[id].entry_cents : null,
          standing_target_cents: event.legs[id].active_order?.target_cents ?? null,
        }])),
      } : {}),
    } : null;
    const v53GameView = isV53 ? policy.buildGameView(v53States, v53Context) : null;
    const v53Plan = isV53 ? policy.buildPlan(v53GameView, v53Context) : null;
    const placementInputs = { legId: row.leg_id, state: combined.state, category: base.category, priceRegion: leg.price_region, book: row, priorAsk: prior?.ask ?? null, askGapCents, activeTarget: incumbentBefore, activeOrderBirthLicense: leg.active_order?.birth_license ?? null, pairCap: leg.pair_cap_cents, pulseFloor: pulse.floor_cents, persistentJoinLevel: isPlacementStack ? leg.persistent_join_level : null, wtaInverseFalling, causalOwnReachLow, activeEvidenceFloor, floorFirstFlickerLive: activeEvidenceFloor === leg.running_qualified_ask_low && leg.running_qualified_ask_low_unabsorbed, floorMature, recentTradeLow, priorTrueTradeLow: leg.prior_true_trade_low_cents, priorTrueTradeLowReceipt: leg.prior_true_trade_low_receipt, priorExactBidEvidence, evidencedStandingLevel: leg.evidenced_standing_level_cents, evidencedStandingAuthority: leg.evidenced_standing_authority, doctrineStanding, birthLicense, v53GameView, v53Plan, siblingBestAsk: normalizedClauses.deep_gap_guard ? (sibling.prior_book?.ask ?? null) : undefined, siblingEntryCents: sibling.entry_cents, siblingCredited: sibling.credited, siblingStandingTarget: base.v52s_enabled ? (sibling.active_order?.v52s_default_target_cents ?? sibling.active_order?.target_cents ?? null) : (sibling.active_order?.target_cents ?? null), clauses: normalizedClauses };
    leg.last_placement_inputs = placementInputs;
    const atomicReceiptDecision = !isV53 && (isV47 || isTradeTruthVariant) && normalizedClauses.same_tick_arm ? policy.decideReceipt({ ...placementInputs, currentJoinLevel: joinLevelBeforeReceipt, residencySeconds: row.ts - leg.current_bid_since }) : null;
    if (atomicReceiptDecision) ensure(atomicReceiptDecision.effective_join_level_cents === leg.persistent_join_level, `V47 atomic join mismatch ${leg.leg_identity} ${row.receipt}`);
    if (isV49) {
      leg.evidenced_standing_level_cents = atomicReceiptDecision.next_evidenced_standing_level_cents;
      leg.evidenced_standing_authority = atomicReceiptDecision.next_evidenced_standing_authority ?? leg.evidenced_standing_authority;
    }
    const decision = atomicReceiptDecision ? { ...atomicReceiptDecision.decision, ...(isV49 ? { evidenced_standing: { enabled: atomicReceiptDecision.evidenced_level_standing_enabled, raised: atomicReceiptDecision.raised_to_evidenced_level, evidence: atomicReceiptDecision.evidence } } : {}) } : policy.decide(placementInputs);
    if (causalOnsetMode && decision.birth_license?.onset) decision.birth_license.onset = {
      ...decision.birth_license.onset,
      binding_status: "V52L_CAUSAL_PREFIX",
      binding_changed_by_V52l: true,
      causal_prefix_receipt_law: leg.v52_onset?.causal_prefix_receipt_law ?? null,
      maximum_consumed_timestamp_epoch: onsetReached ? (leg.v52_onset?.maximum_consumed_timestamp_epoch ?? row.ts) : row.ts,
      right_edge_consumed: leg.v52_onset?.right_edge_consumed ?? null,
      full_span_fit: leg.v52_onset?.full_span_fit ?? null,
    };
    if (isV52) {
      leg.judgment_gate_evaluations += 1;
      const incumbent = decision.unguarded_decision ?? null;
      const isPost = ["PLACE_REST", "REPRICE_REST"].includes(decision.action);
      if (isPost) {
        leg.judgment_gate_posts += 1;
        leg.judgment_first_post ||= { ...clockFields(row.ts, base), receipt: row.receipt, action: decision.action, target_cents: decision.target_cents, birth_license: decision.birth_license };
      }
      const failure = decision.judgment_gate?.failure ?? null;
      if (failure) {
        leg.judgment_gate_blocks[failure] = (leg.judgment_gate_blocks[failure] || 0) + 1;
        leg.judgment_first_block ||= { ...clockFields(row.ts, base), receipt: row.receipt, failure, birth_license: decision.birth_license };
      }
      const wouldPost = before === null || ["PLACE_REST", "REPRICE_REST"].includes(incumbent?.action) || ["PLACE_REST", "REPRICE_REST"].includes(incumbent?.unguarded_decision?.action);
      const traceThisDecision = (base.v52_flow_trace && (isV52ReadAuthority || wouldPost)) || (base.v54_compact_trace && wouldPost);
      if (traceThisDecision) {
        const traceRow = {
          event_id: base.event_id,
          leg_identity: leg.leg_identity,
          category: base.category,
          price_region: leg.price_region,
          ...clockFields(row.ts, base),
          receipt: row.receipt,
          observation: receiptObservation(row),
          onset: decision.birth_license?.onset ?? null,
          read: decision.birth_license?.read ?? null,
          diary: decision.birth_license?.diary ?? null,
          coherence: decision.birth_license?.coherence ?? null,
          level: decision.birth_license?.level ?? null,
          ...(isV53 ? {
            game_view: decision.birth_license?.game_view ?? null,
            plan: decision.birth_license?.plan ?? null,
            lineage_decision: decision.lineage_decision ?? null,
            lineage_target_cents: decision.lineage_target_cents ?? null,
            v53_monotone_lift: decision.v53_monotone_lift ?? null,
            v53_read_licensed_bound: decision.v53_read_licensed_bound ?? null,
            v53_riser_arming: decision.v53_riser_arming ?? null,
            v54_pair_model: decision.v54_pair_model ?? null,
            conservation_input_identity: decision.conservation_input_identity ?? null,
            joint_license: decision.joint_license ?? decision.birth_license?.joint_license ?? null,
          } : {}),
          ...(isV52MacroRecognition ? { macro_recognition: decision.macro_recognition ?? decision.birth_license?.level?.macro_recognition ?? null, recognition_confidence_gate: decision.macro_recognition?.recognition_confidence_gate ?? decision.birth_license?.level?.macro_recognition?.recognition_confidence_gate ?? null, per_shape_floor_depth: decision.per_shape_floor_depth ?? decision.birth_license?.level?.per_shape_floor_depth ?? null, benchmarked_role_instrument: decision.benchmarked_role_instrument ?? decision.birth_license?.level?.benchmarked_role_instrument ?? null, assembled_policy: decision.assembled_policy ?? decision.birth_license?.level?.assembled_policy ?? null, ripeness_role_binding: (decision.macro_recognition ?? decision.birth_license?.level?.macro_recognition ?? null)?.ripeness ?? null } : {}),
          ...((isV52f || isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ? { pair_entry_conservation: decision.birth_license?.pair_entry_conservation ?? null } : {}),
          ...((isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ? { joint_target_conservation: decision.birth_license?.joint_target_conservation ?? null } : {}),
          ...((isV52h || isV52DepthValidation || isV52CausalOnset) ? { clause_4_market_proof_precondition: decision.birth_license?.clause_4_market_proof_precondition ?? null } : {}),
          ...(isV52i ? { depth_informed_level_selection: decision.birth_license?.level?.depth_informed_level_selection ?? decision.depth_informed_level_selection ?? null } : {}),
          ...(isV52j ? { role_conditioned_level_selection: decision.birth_license?.level?.role_conditioned_level_selection ?? decision.role_conditioned_level_selection ?? null } : {}),
          ...(isV52k ? { library_backed_level_evidence: decision.birth_license?.level?.library_backed_level_evidence ?? decision.library_backed_level_evidence ?? null } : {}),
          scavenger: decision.birth_license?.scavenger ?? null,
          palantir: decision.birth_license?.palantir ?? null,
          gate_verdict: decision.judgment_gate?.verdict ?? null,
          blocked_clause: failure,
          incumbent_action: incumbent?.action ?? null,
          incumbent_reason: incumbent?.reason ?? null,
          order_before_cents: before,
          final_action: decision.action,
          final_target_cents: decision.target_cents,
          reason: decision.reason,
        };
        if (base.v54_compact_trace) {
          const postRows = isPost ? [{ leg_identity: leg.leg_identity, receipt: row.receipt, timestamp_epoch: row.ts, birth_license: decision.birth_license }] : [];
          mergeV54AssertionFailures(leg.v54_assertion_failures, auditV54Receipts([traceRow], postRows));
          appendV54LicenseSpan(leg.v54_license_spans, traceRow);
        } else if (isV52FullExam) {
          accumulateExamTraceStats(traceRow);
          leg.judgment_trace_rows.push(activeExamTraceNormalizer.normalize(traceRow));
        } else leg.judgment_trace_rows.push(traceRow);
      }
    }
    if (isV49 && decision.evidenced_standing?.raised) {
      leg.evidenced_standing_decisions += 1;
      const evidenceReceipt = { ...clockFields(row.ts, base), receipt: row.receipt, order_before_cents: before, order_after_cents: decision.target_cents, evidence: decision.evidenced_standing.evidence };
      leg.evidenced_standing_first ||= evidenceReceipt;
      leg.evidenced_standing_last = evidenceReceipt;
    }
    let postCreditGuardBypass = null;
    if (isV45Family && normalizedClauses.release_guard_on_sibling_credit && sibling.credited) {
      const counterfactual = v43Policy.decide({ ...placementInputs, siblingCredited: false, clauses: { ...normalizedClauses, release_guard_on_sibling_credit: false } });
      if (counterfactual.guard?.withheld && !decision.guard?.withheld) {
        leg.post_credit_guard_reapplication_prevented_receipts += 1;
        postCreditGuardBypass = { ...clockFields(row.ts, base), receipt: row.receipt, credited_sibling_leg_identity: sibling.leg_identity, sibling_entry_cents: sibling.entry_cents, fixed_pair_cap_cents: leg.pair_cap_cents, prior_withhold: leg.deep_gap_last_withhold, own_book_receipt: row.receipt, own_book: receiptObservation(row), order_before_cents: before, V43_counterfactual_decision: counterfactual, V45_decision: decision, order_after_cents: null, mechanism: "POST_CREDIT_GUARD_REAPPLICATION_PREVENTED" };
        if (!leg.post_credit_guard_release) {
          leg.post_credit_guard_releases += 1;
          leg.post_credit_guard_release = postCreditGuardBypass;
          actions.push({ kind: "POST_CREDIT_GUARD_REAPPLICATION_PREVENTED", event_id: base.event_id, leg_identity: leg.leg_identity, ...postCreditGuardBypass });
        }
      }
    }
    if (normalizedClauses.deep_gap_guard) noteV42Guard(leg, decision, row, base, actions, leg.leg_identity);
    if (decision.gap_credit?.eligible) {
      leg.gap_credit_eligible_receipts += 1;
      const gapReceipt = { event_id: base.event_id, leg_identity: leg.leg_identity, category: base.category, price_region: leg.price_region, ...clockFields(row.ts, base), receipt: row.receipt, prior_ask_cents: prior?.ask ?? null, current_ask_cents: row.ask, ask_gap_cents: askGapCents, order_before_cents: before, pair_cap_cents: leg.pair_cap_cents, sibling_leg_identity: sibling.leg_identity, sibling_credited: sibling.credited, sibling_entry_cents: sibling.entry_cents, decision: decision.gap_credit, order_after_cents: decision.gap_credit.authorized ? decision.target_cents : before };
      leg.gap_credit_first ||= gapReceipt;
      leg.gap_credit_last = gapReceipt;
      if (decision.gap_credit.authorized) leg.gap_credit_authorized_walks += 1;
      else if (decision.gap_credit.reason === "V46_GAP_CREDIT_REFUSED_SIBLING_NOT_CREDITED") leg.gap_credit_sibling_uncredited_refusals += 1;
      else leg.gap_credit_no_lawful_reprice += 1;
      actions.push({ kind: decision.gap_credit.authorized ? "GAP_CREDIT_AUTHORIZED" : "GAP_CREDIT_REFUSED", ...gapReceipt });
    }
    if (isPlacementStack && decision.placement?.sanity_bound_applied) leg.sanity_bound_rows += 1;
    leg.prior_book = row; leg.decision_count += 1; leg.state_counts[combined.state] += 1; if (combined.disagreement) leg.disagreement_count += 1; leg.action_counts[decision.action] = (leg.action_counts[decision.action] || 0) + 1;
    const detail = { ...clockFields(row.ts, base), receipt: row.receipt, ordinal: row.ordinal, observation: receiptObservation(row), sibling_observation: sibling.prior_book ? receiptObservation(sibling.prior_book) : null, quote_path_state: quote.state, pressure_state: pressure, combined_state: combined.state, direction_authority: combined.authority, disagreement: combined.disagreement, pulse_floor: pulse, persistent_level_join: { level_cents: leg.persistent_join_level, receipt: leg.persistent_join_receipt, evidence_receipt: leg.persistent_join_evidence_receipt, timestamp_epoch: leg.persistent_join_timestamp_epoch, current_bid_residency_seconds: row.ts - leg.current_bid_since, book_last_trade_equals_bid_receipts: leg.book_last_trade_hits_by_level.get(row.bid) || 0, certified_seller_aggressed_prints_at_current_bid: leg.seller_hits_by_level.get(row.bid) || 0, post_join_book_last_trade_receipts: leg.post_join_book_last_trade_receipts, post_join_certified_seller_hits_at_level: leg.post_join_certified_seller_hits_at_level }, wta_other_expression_falling: wtaInverseFalling, causal_own_reach_low_cents: causalOwnReachLow, active_evidence_floor_cents: activeEvidenceFloor, floor_mature: floorMature, pair_cap_cents: leg.pair_cap_cents, order_before_cents: before, decision, order_after_cents: null };
    leg.first_decision ||= detail; leg.last_decision = detail;
    if (base.v52s_enabled && ["PLACE_REST", "REPRICE_REST", "CANCEL_REST", "TAKE"].includes(decision.action)) reconcileV52s(event, row, actions, base, "PRE_SENIOR_TARGET_MUTATION_YIELD", false);
    applyRestDecision(leg, sibling, row, decision, combined.state, detail, actions, base, leg.leg_identity);
    if (base.v52s_enabled) reconcileV52s(event, row, actions, base, "POST_SENIOR_TARGET_MUTATION_REALLOCATE", true);
    detail.order_after_cents = leg.active_order?.target_cents ?? null;
    if (isV47 && v41Join?.changed) {
      const sameReceiptPost = ["PLACE_REST", "REPRICE_REST"].includes(decision.action) && detail.order_after_cents === v41Join.level_cents;
      const alreadyAtLevel = decision.action === "HOLD_REST" && before === v41Join.level_cents && detail.order_after_cents === v41Join.level_cents;
      joinQualifications.push({
        event_id: base.event_id,
        leg_identity: leg.leg_identity,
        category: base.category,
        price_region: leg.price_region,
        bell_confidence: base.bell_confidence,
        mode,
        qualification_timestamp_epoch: row.ts,
        qualification_receipt: row.receipt,
        qualification_level_cents: v41Join.level_cents,
        residency_seconds: row.ts - leg.current_bid_since,
        clause_same_tick_arm: normalizedClauses.same_tick_arm,
        order_before_cents: before,
        decision_action: decision.action,
        decision_reason: decision.reason,
        order_after_cents: detail.order_after_cents,
        guard_withheld: Boolean(decision.guard?.withheld),
        disposition: sameReceiptPost ? "POSTED_ON_QUALIFYING_RECEIPT" : alreadyAtLevel ? "ALREADY_RESTING_AT_QUALIFIED_LEVEL" : decision.guard?.withheld ? "UNCHANGED_GUARD_WITHHELD" : "UNCHANGED_LAW_DID_NOT_POST_QUALIFIED_LEVEL",
        scheduler_latency_seconds: sameReceiptPost || alreadyAtLevel ? 0 : null,
      });
    }
    if (postCreditGuardBypass && leg.post_credit_guard_release === postCreditGuardBypass) postCreditGuardBypass.order_after_cents = detail.order_after_cents;
    if (Number.isInteger(detail.order_after_cents) && detail.order_after_cents >= row.ask) leg.sanity_violation_rows += 1;
    if (row.ts <= leg.union_first_evidence_timestamp_epoch) leg.reach_snapshot = { ...detail };

    // A sibling best-ask change is a new receipt for the V42 clause.  Only a
    // leg actively withheld by V42 is re-evaluated cross-leg; all other V41
    // streams retain their exact incumbent receipt path.
    if (normalizedClauses.deep_gap_guard) {
      reevaluateV42WithSiblingBook(sibling, leg, row, actions, base);
      if (base.v52s_enabled) reconcileV52s(event, row, actions, base, "POST_SIBLING_BOOK_REEVALUATION", true);
    }
  }
  for (const leg of Object.values(event.legs)) {
    leg.resting_target_at_edge_cents = leg.credited ? null : (leg.active_order?.target_cents ?? null);
    leg.first_action_timestamp_epoch = leg.first_action?.timestamp_epoch ?? null;
    if (!leg.credited) leg.terminal_reason = leg.decision_count === 0 ? "NO_TWO_SIDED_BOOK_DECISION_INSIDE_V36_EDGE" : leg.active_order ? "REST_UNFILLED_AT_HARD_PREBELL_EDGE" : "NO_LAWFUL_REST_AT_HARD_PREBELL_EDGE";
    leg.final_state = leg.credited ? "CREDITED" : leg.active_order ? "RESTING_UNFILLED" : "NEVER_PLACED_OR_CANCELLED";
    leg.persistent_join_book_last_trade_receipts = leg.persistent_join_level === null ? 0 : (leg.book_last_trade_hits_by_level.get(leg.persistent_join_level) || 0);
    leg.persistent_join_certified_seller_aggressed_prints = leg.persistent_join_level === null ? 0 : (leg.seller_hits_by_level.get(leg.persistent_join_level) || 0);
    delete leg.active_order; delete leg.prior_book; delete leg.directional; delete leg.pulse_visits; delete leg.recent_trade_rows; delete leg.exact_bid_first_receipt; delete leg.first_action; delete leg.seller_hits_by_level; delete leg.book_last_trade_hits_by_level; delete leg.downward_evidence_rows; delete leg.last_placement_inputs; delete leg.deep_gap_withhold_active; delete leg.post_onset_read_state; delete leg.pair_budget_record; delete leg.v52s_joint_budget_receipt_summary; delete leg.v53_state;
  }
  if (event.v52s_joint_budget_receipt_summary) {
    const summary = event.v52s_joint_budget_receipt_summary;
    event.v52s_joint_budget_receipt_summary = { phase_evaluations: summary.phase_evaluations, unique_receipts: summary.unique_receipts, vacuous_unset_counterpart_evaluations: summary.vacuous_unset_counterpart_evaluations, lift_events: summary.lift_events, yield_events: summary.yield_events, invariant_violations: summary.invariant_violations, max_joint_target_sum_cents: summary.max_joint_target_sum_cents, receipt_chain_sha256: summary.digest.digest("hex"), both_clock_fields_on_every_lift_or_yield: actions.filter((row) => row.kind.startsWith("V52S_")).every((row) => Object.hasOwn(row, "t_minus_scheduled_seconds") && Object.hasOwn(row, "t_minus_actual_bell_seconds")) };
  }
  const legs = Object.values(event.legs);
  event.completed_pair = legs.every((leg) => leg.credited);
  event.combined_entry_cents = event.completed_pair ? legs.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
  event.pair_under_par = event.completed_pair && event.combined_entry_cents < 100;
  return { event, actions, joinQualifications };
}

function score(events) {
  const legs = events.flatMap((event) => Object.values(event.legs));
  const completed = events.filter((event) => event.completed_pair), under = completed.filter((event) => event.pair_under_par);
  const frontier = {};
  for (const [name, predicate] of Object.entries({ LE_93: (x) => x <= 93, LE_95: (x) => x <= 95, LE_97: (x) => x <= 97, LT_100: (x) => x < 100, ANY_PRICE: () => true })) frontier[name] = completed.filter((event) => predicate(event.combined_entry_cents)).length;
  return { D: events.length, legs: legs.length, acted_legs: legs.filter((leg) => leg.first_action_timestamp_epoch !== null).length, credited_legs: legs.filter((leg) => leg.credited).length, completed_pairs: completed.length, under_par_pairs: under.length, locked_cents_per_contract: under.reduce((sum, event) => sum + 100 - event.combined_entry_cents, 0), locked_cents_five_lot: under.reduce((sum, event) => sum + (100 - event.combined_entry_cents) * 5, 0), maker_fill_classes: countBy(legs.filter((leg) => leg.credited), (leg) => leg.fill_class), frontier, conservation: { D: events.length, legs: legs.length, pass: events.length === 804 && legs.length === 1608 } };
}

function gradeV54Events(events, groundTruth) {
  const rows = events.map((event) => {
    const window = groundTruth.byEvent.get(event.event_id);
    ensure(window, `V54 ground-truth row absent ${event.event_id}`);
    if (!window.scoring_eligible) return { event_id: event.event_id, category: event.category, state: "UNKNOWN_BELL_NON_GRADEABLE", combined_entry_cents: null, valid_credited_legs: [] };
    const validCreditedLegs = Object.entries(event.legs).filter(([legId, leg]) => {
      ensure(window.legs[legId], `V54 ground-truth leg absent ${event.event_id}|${legId}`);
      return leg.credited && Number.isFinite(leg.fill_timestamp_epoch) && leg.fill_timestamp_epoch >= window.span_start_epoch && leg.fill_timestamp_epoch <= window.span_end_epoch;
    }).map(([, leg]) => leg);
    const combined = validCreditedLegs.length === 2 ? validCreditedLegs.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
    const state = validCreditedLegs.length === 2 ? (combined < 100 ? "COMPLETE_AT_DELTA" : "COMPLETE_AT_LOSS") : validCreditedLegs.length === 1 ? "PARTIAL_FOR_REASON" : "NEITHER_FOR_REASON";
    return { event_id: event.event_id, category: event.category, state, combined_entry_cents: combined, valid_credited_legs: validCreditedLegs };
  });
  const eligible = rows.filter((row) => row.state !== "UNKNOWN_BELL_NON_GRADEABLE");
  const completed = eligible.filter((row) => ["COMPLETE_AT_DELTA", "COMPLETE_AT_LOSS"].includes(row.state));
  const under = eligible.filter((row) => row.state === "COMPLETE_AT_DELTA");
  const frontier = {};
  for (const [name, predicate] of Object.entries({ LE_93: (x) => x <= 93, LE_95: (x) => x <= 95, LE_97: (x) => x <= 97, LT_100: (x) => x < 100, ANY_PRICE: () => true })) frontier[name] = completed.filter((row) => predicate(row.combined_entry_cents)).length;
  return { rows, score: { D: rows.length, scoring_D: eligible.length, unknown_bell: rows.length - eligible.length, credited_legs: eligible.reduce((sum, row) => sum + row.valid_credited_legs.length, 0), completed_pairs: completed.length, under_par_pairs: under.length, completed_at_loss: completed.length - under.length, locked_cents_per_contract: under.reduce((sum, row) => sum + 100 - row.combined_entry_cents, 0), locked_cents_five_lot: under.reduce((sum, row) => sum + (100 - row.combined_entry_cents) * 5, 0), frontier } };
}

function selectV54DecisionStories(baseByEvent, pins, count = 30) {
  const pinIds = new Set(pins.map((row) => row.event_id));
  const selected = [...pinIds];
  const seed = shaBytes(Buffer.from("V54_01_DECISION_STORIES|d449889e|L19A_FIXED_804", "utf8"));
  const byCategory = new Map();
  for (const base of [...baseByEvent.values()].filter((row) => !pinIds.has(row.event_id))) {
    if (!byCategory.has(base.category)) byCategory.set(base.category, []);
    byCategory.get(base.category).push(base.event_id);
  }
  for (const rows of byCategory.values()) rows.sort((a, b) => shaBytes(Buffer.from(`${seed}|${a}`)).localeCompare(shaBytes(Buffer.from(`${seed}|${b}`))) || a.localeCompare(b));
  const categories = [...byCategory.keys()].sort();
  let cursor = 0;
  while (selected.length < count) {
    const category = categories[cursor % categories.length];
    const row = byCategory.get(category).shift();
    if (row) selected.push(row);
    cursor += 1;
    ensure(cursor < 100000, "V54 decision-story selection failed to converge");
  }
  return { seed_sha256: seed, method: "FIVE_STANDING_PINS_PLUS_CATEGORY_ROUND_ROBIN_SHA256_RANK", event_ids: selected.sort() };
}

function auditV54Receipts(traceRows, postActions) {
  return {
    no_pre_onset_inputs: postActions.filter((row) => !row.birth_license?.onset?.passed).map((row) => `${row.leg_identity}@${row.receipt}`),
    no_span_fraction_inputs: postActions.filter((row) => row.birth_license?.game_view?.provenance?.no_span_fraction_consumed !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
    no_static_depth_targets: postActions.filter((row) => row.birth_license?.game_view?.provenance?.no_static_depth_target_consumed !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
    complete_license_on_every_bid: postActions.filter((row) => !(row.birth_license?.game_view && row.birth_license?.plan?.licensed && row.birth_license?.level && row.birth_license?.pair_entry_conservation && row.birth_license?.joint_target_conservation)).map((row) => `${row.leg_identity}@${row.receipt}`),
    pair_polarity_type_invariant: traceRows.filter((row) => {
      const p = row.v54_pair_model?.polarity;
      return !(p?.tag === "UNDECIDED"
        ? p.strengthening_leg_id === null && p.fading_leg_id === null
        : p?.tag === "DECIDED" && p.strengthening_leg_id && p.fading_leg_id && p.strengthening_leg_id !== p.fading_leg_id);
    }).map((row) => `${row.leg_identity}@${row.receipt}`),
    no_same_label_pair_representable: traceRows.filter((row) => row.v54_pair_model?.polarity?.tag === "DECIDED" && row.v54_pair_model.polarity.strengthening_leg_id === row.v54_pair_model.polarity.fading_leg_id).map((row) => `${row.leg_identity}@${row.receipt}`),
    joint_license_complete_coherent_and_readable_on_every_bid: postActions.filter((row) => {
      const license = row.birth_license?.joint_license, split = license?.budget_split;
      return !(license?.law === "L23_PAIR_UNIT_PROOF" && license.complete === true && typeof license.sentence === "string" && license.sentence.trim().length > 0 && license.sentence_action_assertion?.equal === true && split && Number.isInteger(split.sum_cents) && split.sum_cents <= 99);
    }).map((row) => `${row.leg_identity}@${row.receipt}`),
    sentence_action_equal_on_every_written_license: traceRows.filter((row) => typeof row.joint_license?.sentence === "string" && row.joint_license.sentence_action_assertion?.equal !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
    fading_path_byte_equal_to_lineage: traceRows.filter((row) => row.v54_pair_model?.reason !== "V54_FORMATION_NOT_SETTLED_NO_POST" && row.v54_pair_model?.window === "LATE" && row.v54_pair_model?.polarity?.tag === "DECIDED" && row.leg_identity.endsWith(`|${row.v54_pair_model.polarity.fading_leg_id}`) && (row.final_action !== row.lineage_decision?.action || row.final_target_cents !== row.lineage_target_cents)).map((row) => `${row.leg_identity}@${row.receipt}`),
    undecided_path_byte_equal_to_lineage: traceRows.filter((row) => row.v54_pair_model?.reason !== "V54_FORMATION_NOT_SETTLED_NO_POST" && row.v54_pair_model?.polarity?.tag === "UNDECIDED" && (row.final_action !== row.lineage_decision?.action || row.final_target_cents !== row.lineage_target_cents)).map((row) => `${row.leg_identity}@${row.receipt}`),
    preformation_gate_only_nulls_lineage: traceRows.filter((row) => row.v54_pair_model?.reason === "V54_FORMATION_NOT_SETTLED_NO_POST" && (!['HOLD_REST', 'CANCEL_REST'].includes(row.final_action) || row.final_target_cents !== null)).map((row) => `${row.leg_identity}@${row.receipt}`),
    conservation_inputs_byte_equal: traceRows.filter((row) => row.conservation_input_identity?.byte_equal !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
    no_pre_formation_anchor_consumption: postActions.filter((row) => {
      const own = row.birth_license?.game_view?.legs?.[row.leg_identity.split("|").at(-1)];
      return Number.isFinite(own?.l16_formation_anchor?.formation_end_epoch) && row.timestamp_epoch < own.l16_formation_anchor.formation_end_epoch;
    }).map((row) => `${row.leg_identity}@${row.receipt}`),
    l16_anchor_provenance_on_strengthening_bids: postActions.filter((row) => row.birth_license?.level?.v54_pair_model?.applied === true && row.birth_license?.game_view?.provenance?.formation_anchor?.law !== "L16").map((row) => `${row.leg_identity}@${row.receipt}`),
    joint_target_at_or_below_99_per_receipt: traceRows.filter((row) => Number.isInteger(row.final_target_cents) && Number.isInteger(row.joint_target_conservation?.counterpart_cents) && row.final_target_cents + row.joint_target_conservation.counterpart_cents > 99).map((row) => `${row.leg_identity}@${row.receipt}:${row.final_target_cents}+${row.joint_target_conservation.counterpart_cents}`),
  };
}

function mergeV54AssertionFailures(target, addition) {
  for (const [key, rows] of Object.entries(addition)) {
    if (!target[key]) target[key] = [];
    target[key].push(...rows);
  }
  return target;
}

function fullBookPnl(events, closeByTicker) {
  const rows = [], categories = new Map();
  for (const event of events) {
    const legs = Object.values(event.legs), credited = legs.filter((leg) => leg.credited);
    let disposition, pnl = 0, priced = true, nakedLeg = null;
    if (credited.length === 2) {
      disposition = "COMPLETED";
      pnl = 100 - credited.reduce((sum, leg) => sum + leg.entry_cents, 0);
    } else if (credited.length === 1) {
      disposition = "NAKED";
      nakedLeg = credited[0];
      const close = closeByTicker.get(nakedLeg.ticker);
      priced = Number.isInteger(close);
      pnl = priced ? close - nakedLeg.entry_cents : null;
    } else {
      disposition = "SKIP";
      pnl = 0;
    }
    const row = { event_id: event.event_id, category: event.category, disposition, completed: disposition === "COMPLETED", naked: disposition === "NAKED", skip: disposition === "SKIP", pair_entry_cents: disposition === "COMPLETED" ? event.combined_entry_cents : null, completed_locked_cents: disposition === "COMPLETED" ? pnl : 0, naked_leg_identity: nakedLeg?.leg_identity ?? null, naked_entry_cents: nakedLeg?.entry_cents ?? null, naked_close_cents: nakedLeg ? (closeByTicker.get(nakedLeg.ticker) ?? null) : null, naked_priced: disposition === "NAKED" ? priced : null, naked_pnl_cents: disposition === "NAKED" && priced ? pnl : 0, net_cents: disposition === "NAKED" && !priced ? 0 : pnl };
    rows.push(row);
    if (!categories.has(event.category)) categories.set(event.category, []);
    categories.get(event.category).push(row);
  }
  const summarize = (x) => ({ events: x.length, completed_pairs: x.filter((row) => row.completed).length, completed_locked_cents: x.reduce((sum, row) => sum + row.completed_locked_cents, 0), naked_legs: x.filter((row) => row.naked).length, naked_priced: x.filter((row) => row.naked && row.naked_priced).length, naked_open: x.filter((row) => row.naked && !row.naked_priced).length, naked_pnl_cents: x.reduce((sum, row) => sum + row.naked_pnl_cents, 0), skips: x.filter((row) => row.skip).length, true_book_net_cents: x.reduce((sum, row) => sum + row.net_cents, 0) });
  return { aggregate: summarize(rows), by_category: Object.fromEntries([...categories].sort(([a], [b]) => a.localeCompare(b)).map(([key, value]) => [key, summarize(value)])), rows, conservation: { events: rows.length, disposition_sum: rows.filter((row) => row.completed).length + rows.filter((row) => row.naked).length + rows.filter((row) => row.skip).length, pass: rows.length === 804 && rows.every((row) => ["COMPLETED", "NAKED", "SKIP"].includes(row.disposition)) } };
}

function scorePartitions(events) {
  const groups = new Map();
  for (const event of events) {
    const key = `${event.category}|${event.bell_confidence}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(event);
  }
  return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, rows]) => ({
    cell,
    category: rows[0].category,
    bell_confidence: rows[0].bell_confidence,
    ...score(rows),
  }));
}

function tradedFloorCensus(baseByEvent, printLoad, reachByEvent) {
  const legRows = [], gameRows = [];
  for (const base of [...baseByEvent.values()].sort((a, b) => a.event_id.localeCompare(b.event_id))) {
    const reach = reachByEvent.get(base.event_id), legs = [];
    for (const [legId, leg] of Object.entries(base.legs).sort(([a], [b]) => a.localeCompare(b))) {
      const prints = printLoad.byTicker.get(leg.ticker) || [];
      const lawful = prints.filter((row) => row.ts >= base.left && row.ts <= base.right && Number.isInteger(row.price) && typeof row.trade_id === "string" && row.trade_id.length > 0);
      const minimum = lawful.length ? Math.min(...lawful.map((row) => row.price)) : null;
      const floorPrint = Number.isInteger(minimum) ? lawful.find((row) => row.price === minimum) : null;
      const oldUnion = reach?.legs?.[legId]?.union_reach_cents ?? null;
      const row = {
        event_id: base.event_id,
        category: base.category,
        bell_confidence: base.bell_confidence,
        starting_price_split: base.starting_price_split,
        leg_identity: leg.leg_identity,
        ticker: leg.ticker,
        price_region: leg.price_region,
        lawful_span: { left_epoch: base.left, right_epoch: base.right },
        lowest_traded_price_cents: minimum,
        floor_print: floorPrint ? { timestamp_epoch: floorPrint.ts, receipt: floorPrint.receipt, trade_id: floorPrint.trade_id, size: floorPrint.size, taker_side: floorPrint.taker_side, taker_book_side: floorPrint.taker_book_side } : null,
        lawful_true_prints: lawful.length,
        old_union_floor_cents: oldUnion,
        traded_minus_old_union_cents: Number.isInteger(minimum) && Number.isInteger(oldUnion) ? minimum - oldUnion : null,
      };
      legRows.push(row); legs.push(row);
    }
    const traded = legs.map((row) => row.lowest_traded_price_cents), old = legs.map((row) => row.old_union_floor_cents);
    const tradedComplete = traded.every(Number.isInteger), oldComplete = old.every(Number.isInteger);
    const tradedSum = tradedComplete ? traded.reduce((a, b) => a + b, 0) : null;
    const oldSum = oldComplete ? old.reduce((a, b) => a + b, 0) : null;
    const classify = (sum) => !Number.isInteger(sum) ? "UNAVAILABLE" : sum < 100 ? "UNDER_PAR" : "OVER_PAR";
    gameRows.push({
      event_id: base.event_id,
      category: base.category,
      bell_confidence: base.bell_confidence,
      starting_price_split: base.starting_price_split,
      lowest_traded_pair_sum_cents: tradedSum,
      old_union_pair_sum_cents: oldSum,
      traded_floor_class: classify(tradedSum),
      old_union_class: classify(oldSum),
      flip: `${classify(oldSum)}->${classify(tradedSum)}`,
      legs: legs.map((row) => ({ leg_identity: row.leg_identity, lowest_traded_price_cents: row.lowest_traded_price_cents, old_union_floor_cents: row.old_union_floor_cents })),
    });
  }
  const summarize = (rows) => ({ games: rows.length, traded_floor_classes: countBy(rows, (row) => row.traded_floor_class), old_union_classes: countBy(rows, (row) => row.old_union_class), flips: countBy(rows, (row) => row.flip) });
  const categories = new Map();
  for (const row of gameRows) { if (!categories.has(row.category)) categories.set(row.category, []); categories.get(row.category).push(row); }
  return {
    law: "PER_LEG_FLOOR_IS_LOWEST_LAWFUL_TRUE_TRADED_PRICE_IN_HARD_WINDOW1_SPAN; NO_ASK_AGGRESSOR_DWELL_SIZE_OR_ARRIVAL_FILTER",
    aggregate: summarize(gameRows),
    by_category: Object.fromEntries([...categories].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => [key, summarize(rows)])),
    leg_rows: legRows,
    game_rows: gameRows,
    conservation: { games: gameRows.length, legs: legRows.length, expected_games: 804, expected_legs: 1608, pass: gameRows.length === 804 && legRows.length === 1608 },
  };
}

function gradeAgainstTradedFloors(events, tradedFloorByLeg) {
  const rows = [], games = [];
  for (const event of events) {
    const legs = Object.values(event.legs).map((leg) => {
      const floor = tradedFloorByLeg.get(leg.leg_identity), value = floor?.lowest_traded_price_cents ?? null;
      const row = { event_id: event.event_id, category: event.category, bell_confidence: event.bell_confidence, starting_price_split: event.starting_price_split, leg_identity: leg.leg_identity, ticker: leg.ticker, price_region: leg.price_region, credited: leg.credited, entry_cents: leg.entry_cents, lowest_traded_price_cents: value, gap_to_lowest_trade_cents: leg.credited && Number.isInteger(value) ? leg.entry_cents - value : null, fill_class: leg.fill_class };
      rows.push(row); return row;
    });
    games.push({ event_id: event.event_id, category: event.category, bell_confidence: event.bell_confidence, completed: event.completed_pair, under_par: event.pair_under_par, combined_entry_cents: event.combined_entry_cents, both_traded_floors_available: legs.every((row) => Number.isInteger(row.lowest_traded_price_cents)), pair_traded_floor_cents: legs.every((row) => Number.isInteger(row.lowest_traded_price_cents)) ? legs.reduce((sum, row) => sum + row.lowest_traded_price_cents, 0) : null, gaps_cents: legs.map((row) => row.gap_to_lowest_trade_cents) });
  }
  const summarize = (eventRows, legSubset) => ({ score: score(eventRows), credited_leg_gap_to_lowest_trade_cents: distribution(legSubset.filter((row) => row.credited).map((row) => row.gap_to_lowest_trade_cents)), credited_at_or_better_than_lowest_trade: legSubset.filter((row) => row.credited && Number.isInteger(row.gap_to_lowest_trade_cents) && row.gap_to_lowest_trade_cents <= 0).length, traded_floor_missing_legs: legSubset.filter((row) => !Number.isInteger(row.lowest_traded_price_cents)).length });
  const cells = new Map();
  for (const event of events) { const key = `${event.category}|${event.bell_confidence}`; if (!cells.has(key)) cells.set(key, []); cells.get(key).push(event); }
  return {
    aggregate: summarize(events, rows),
    category_x_bell_confidence: [...cells].sort(([a], [b]) => a.localeCompare(b)).map(([cell, eventRows]) => { const ids = new Set(eventRows.map((row) => row.event_id)); return { cell, category: eventRows[0].category, bell_confidence: eventRows[0].bell_confidence, ...summarize(eventRows, rows.filter((row) => ids.has(row.event_id))) }; }),
    rows,
    games,
    conservation: { games: games.length, legs: rows.length, pass: games.length === 804 && rows.length === 1608 },
  };
}

function ladderDifferential(incumbentEvents, ladderEvents, closeByTicker, ladderName) {
  const prior = new Map(incumbentEvents.map((event) => [event.event_id, event])), rows = [];
  for (const event of ladderEvents) {
    const baseline = prior.get(event.event_id); ensure(baseline, `missing incumbent event ${event.event_id}`);
    for (const [legId, leg] of Object.entries(event.legs)) {
      const old = baseline.legs[legId];
      let disposition = "UNCHANGED";
      if (!old.credited && leg.credited) disposition = "FILL_GAINED";
      else if (old.credited && !leg.credited) disposition = "FILL_LOST";
      else if (old.credited && leg.credited && old.entry_cents !== leg.entry_cents) disposition = leg.entry_cents < old.entry_cents ? "FILL_REPRICED_FAVORABLE" : "FILL_REPRICED_ADVERSE";
      if (disposition === "UNCHANGED") continue;
      rows.push({ event_id: event.event_id, category: event.category, bell_confidence: event.bell_confidence, leg_identity: leg.leg_identity, ladder: ladderName, disposition, incumbent_credited: old.credited, incumbent_entry_cents: old.entry_cents, ladder_credited: leg.credited, ladder_entry_cents: leg.entry_cents, reprice_delta_cents: old.credited && leg.credited ? leg.entry_cents - old.entry_cents : null, incumbent_pair_completed: baseline.completed_pair, ladder_pair_completed: event.completed_pair, incumbent_combined_entry_cents: baseline.combined_entry_cents, ladder_combined_entry_cents: event.combined_entry_cents });
    }
  }
  const oldBook = fullBookPnl(incumbentEvents, closeByTicker).aggregate, newBook = fullBookPnl(ladderEvents, closeByTicker).aggregate;
  const summarize = (subset) => ({ changed_legs: subset.length, dispositions: countBy(subset, (row) => row.disposition), favorable_reprice_cents: -subset.filter((row) => row.disposition === "FILL_REPRICED_FAVORABLE").reduce((sum, row) => sum + row.reprice_delta_cents, 0), adverse_reprice_cents: subset.filter((row) => row.disposition === "FILL_REPRICED_ADVERSE").reduce((sum, row) => sum + row.reprice_delta_cents, 0) });
  const categories = new Map(); for (const row of rows) { if (!categories.has(row.category)) categories.set(row.category, []); categories.get(row.category).push(row); }
  return { ladder: ladderName, aggregate: summarize(rows), by_category: Object.fromEntries([...categories].sort(([a], [b]) => a.localeCompare(b)).map(([key, value]) => [key, summarize(value)])), score_delta: { completed_pairs: score(ladderEvents).completed_pairs - score(incumbentEvents).completed_pairs, under_par_pairs: score(ladderEvents).under_par_pairs - score(incumbentEvents).under_par_pairs, locked_cents: newBook.completed_locked_cents - oldBook.completed_locked_cents, naked_pnl_cents: newBook.naked_pnl_cents - oldBook.naked_pnl_cents, true_book_net_cents: newBook.true_book_net_cents - oldBook.true_book_net_cents }, rows };
}

function deepGapDifferential(v41Events, v42Events, closeByTicker) {
  const current = new Map(v42Events.map((event) => [event.event_id, event])), rows = [];
  for (const prior of v41Events) {
    const next = current.get(prior.event_id); ensure(next, `missing V42 event ${prior.event_id}`);
    const priorLegs = Object.values(prior.legs), nextLegs = Object.values(next.legs);
    const priorCredited = priorLegs.filter((leg) => leg.credited), nextCredited = nextLegs.filter((leg) => leg.credited);
    if (JSON.stringify(priorLegs.map((leg) => [leg.leg_identity, leg.credited, leg.entry_cents, leg.fill_class])) === JSON.stringify(nextLegs.map((leg) => [leg.leg_identity, leg.credited, leg.entry_cents, leg.fill_class]))) continue;
    let classification = "OTHER_CHANGED_STREAM", cents = 0;
    if (priorCredited.length === 1 && nextCredited.length === 0) {
      const leg = priorCredited[0], close = closeByTicker.get(leg.ticker), nakedPnl = Number.isInteger(close) ? close - leg.entry_cents : null;
      if (Number.isInteger(nakedPnl) && nakedPnl < 0) { classification = "LOSS_AVOIDED"; cents = -nakedPnl; }
      else if (Number.isInteger(nakedPnl) && nakedPnl > 0) { classification = "WINNING_NAKED_FORFEITED"; cents = -nakedPnl; }
      else classification = Number.isInteger(nakedPnl) ? "FLAT_NAKED_REMOVED" : "OPEN_NAKED_REMOVED";
    } else if (priorCredited.length === 2 && nextCredited.length < 2) {
      classification = "COMPLETED_PAIR_FORFEITED";
      cents = -(100 - priorCredited.reduce((sum, leg) => sum + leg.entry_cents, 0));
    } else if (nextCredited.length > priorCredited.length) classification = "CREDIT_RECOVERED";
    rows.push({ event_id: prior.event_id, category: prior.category, classification, cents, V41: { credited_legs: priorCredited.length, entries: priorCredited.map((leg) => ({ leg_identity: leg.leg_identity, entry_cents: leg.entry_cents })) }, V42: { credited_legs: nextCredited.length, entries: nextCredited.map((leg) => ({ leg_identity: leg.leg_identity, entry_cents: leg.entry_cents })) } });
  }
  return { rows, aggregate: { changed_events: rows.length, losses_avoided: { events: rows.filter((row) => row.classification === "LOSS_AVOIDED").length, cents: rows.filter((row) => row.classification === "LOSS_AVOIDED").reduce((sum, row) => sum + row.cents, 0) }, pairs_forfeited: { events: rows.filter((row) => row.classification === "COMPLETED_PAIR_FORFEITED").length, cents: -rows.filter((row) => row.classification === "COMPLETED_PAIR_FORFEITED").reduce((sum, row) => sum + row.cents, 0) }, winning_naked_forfeited: { events: rows.filter((row) => row.classification === "WINNING_NAKED_FORFEITED").length, cents: -rows.filter((row) => row.classification === "WINNING_NAKED_FORFEITED").reduce((sum, row) => sum + row.cents, 0) }, net_classified_cents: rows.reduce((sum, row) => sum + row.cents, 0), by_class: countBy(rows, (row) => row.classification) } };
}

function kalshiTakerFeePerContractCents(priceCents) {
  ensure(Number.isInteger(priceCents) && priceCents >= 1 && priceCents <= 99, `invalid taker price ${priceCents}`);
  const p = priceCents / 100;
  return Math.ceil(0.07 * p * (1 - p) * 100);
}

function frozenV36NetScore(events) {
  const summarize = (rows) => {
    const legs = rows.flatMap((event) => Object.values(event.legs));
    const takers = legs.filter((leg) => leg.credited && String(leg.fill_class).startsWith("PROVEN_TAKER"));
    const makers = legs.filter((leg) => leg.credited && String(leg.fill_class).startsWith("PROVEN_MAKER"));
    const completed = rows.filter((event) => Object.values(event.legs).every((leg) => leg.credited));
    const grossUnder = completed.filter((event) => Object.values(event.legs).reduce((sum, leg) => sum + leg.entry_cents, 0) < 100);
    const grossLocked = grossUnder.reduce((sum, event) => sum + 100 - Object.values(event.legs).reduce((s, leg) => s + leg.entry_cents, 0), 0);
    const completedNet = completed.map((event) => {
      const eventLegs = Object.values(event.legs), grossCost = eventLegs.reduce((sum, leg) => sum + leg.entry_cents, 0);
      const fees = eventLegs.reduce((sum, leg) => sum + (String(leg.fill_class).startsWith("PROVEN_TAKER") ? kalshiTakerFeePerContractCents(leg.entry_cents) : 0), 0);
      return { gross_cost: grossCost, fee: fees, net_locked: 100 - grossCost - fees };
    });
    const feeAll = takers.reduce((sum, leg) => sum + kalshiTakerFeePerContractCents(leg.entry_cents), 0);
    const feeCompleted = completedNet.reduce((sum, row) => sum + row.fee, 0);
    return {
      events: rows.length,
      credited_legs: takers.length + makers.length,
      maker_legs_fee_exempt: makers.length,
      taker_legs_charged: takers.length,
      completed_pairs: completed.length,
      gross_under_par_pairs: grossUnder.length,
      net_positive_completed_pairs: completedNet.filter((row) => row.net_locked > 0).length,
      games_flipped_negative_by_fees: completedNet.filter((row) => row.gross_cost < 100 && row.net_locked < 0).length,
      games_flipped_to_zero_by_fees: completedNet.filter((row) => row.gross_cost < 100 && row.net_locked === 0).length,
      gross_locked_cents_per_contract: grossLocked,
      gross_locked_cents_five_lot: grossLocked * 5,
      taker_fees_all_credited_legs_cents_per_contract: feeAll,
      taker_fees_all_credited_legs_five_lot: feeAll * 5,
      taker_fees_completed_pairs_cents_per_contract: feeCompleted,
      taker_fees_completed_pairs_five_lot: feeCompleted * 5,
      net_locked_after_all_entry_taker_fees_cents_per_contract: grossLocked - feeAll,
      net_locked_after_all_entry_taker_fees_five_lot: (grossLocked - feeAll) * 5,
      completed_pair_net_locked_cents_per_contract: completedNet.reduce((sum, row) => sum + row.net_locked, 0),
      completed_pair_net_locked_cents_five_lot: completedNet.reduce((sum, row) => sum + row.net_locked, 0) * 5,
    };
  };
  const groups = new Map();
  for (const event of events) { if (!groups.has(event.category)) groups.set(event.category, []); groups.get(event.category).push(event); }
  return { fee_law: "TAKER=CEIL(0.07*P*(1-P)*100)_CENTS_PER_CONTRACT; MAKER=0; FIVE_CONTRACTS_PER_LEG", aggregate: summarize(events), per_category: [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([category, rows]) => ({ category, ...summarize(rows) })) };
}

function frozenV36Score(reachRows) {
  const byEvent = new Map();
  for (const row of reachRows) { if (!byEvent.has(row.event_id)) byEvent.set(row.event_id, []); byEvent.get(row.event_id).push(row); }
  const events = [...byEvent].map(([event_id, legs]) => {
    const completed = legs.length === 2 && legs.every((leg) => leg.v36_credited && Number.isInteger(leg.v36_entry_cents));
    const cost = completed ? legs.reduce((sum, leg) => sum + leg.v36_entry_cents, 0) : null;
    return {
      event_id,
      completed_pair: completed,
      combined_entry_cents: cost,
      pair_under_par: completed && cost < 100,
      legs: Object.fromEntries(legs.map((leg) => [leg.leg_id, {
        first_action_timestamp_epoch: leg.v36_decision_count > 0 ? leg.v36_left_epoch : null,
        credited: Boolean(leg.v36_credited),
        fill_class: leg.v36_fill_class,
      }])),
    };
  });
  return score(events);
}

function classifierTelemetry(events) {
  const legs = events.flatMap((event) => Object.values(event.legs).map((leg) => ({ ...leg, event_category: event.category, event_bell_confidence: event.bell_confidence })));
  const sealedDirection = (leg) => leg.leg_direction === "CLIMBING" ? "RISING" : leg.leg_direction === "FALLING" ? "FALLING" : leg.leg_direction === "FLAT" ? "SETTLED" : null;
  const summarize = (rows) => {
    const atReach = rows.filter((leg) => sealedDirection(leg) && leg.reach_snapshot?.combined_state);
    const atReachCorrect = atReach.filter((leg) => leg.reach_snapshot.combined_state === sealedDirection(leg));
    return {
      legs: rows.length,
      decision_receipts: rows.reduce((sum, leg) => sum + leg.classifier_rows, 0),
      eligible_receipts: rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_rows : 0), 0),
      correct_receipts: rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_state_counts[sealedDirection(leg)] : 0), 0),
      receipt_accuracy: rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_rows : 0), 0) ? rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_state_counts[sealedDirection(leg)] : 0), 0) / rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_rows : 0), 0) : null,
      reach_moment_eligible_legs: atReach.length,
      reach_moment_correct_legs: atReachCorrect.length,
      reach_moment_accuracy: atReach.length ? atReachCorrect.length / atReach.length : null,
      reach_moment_confusion: countBy(atReach, (leg) => `${sealedDirection(leg)}->${leg.reach_snapshot.combined_state}`),
      agreement_receipts: rows.reduce((sum, leg) => sum + leg.classifier_agreement_rows, 0),
      opposed_receipts_settled: rows.reduce((sum, leg) => sum + leg.classifier_opposed_rows, 0),
    };
  };
  const groups = new Map(); for (const leg of legs) { const key = `${leg.event_category}|${leg.event_bell_confidence}`; if (!groups.has(key)) groups.set(key, []); groups.get(key).push(leg); }
  return { aggregate: summarize(legs), category_x_bell_confidence: [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, rows]) => ({ cell, ...summarize(rows) })), telemetry_only_ex_post_direction_not_consumed_by_policy: true };
}

function residualOwner(leg, reach, base) {
  if (leg.credited && leg.entry_cents <= reach) return null;
  if (leg.credited && String(leg.fill_class).includes("TAKER")) return { owner: "TAKE_FIRED_ABOVE_REACH", detail: `take ${leg.entry_cents} > union reach ${reach}`, measurable_cents: leg.entry_cents - reach };
  if (leg.credited) return { owner: `${leg.fill_source_state || "UNKNOWN"}_REST_FILLED_SHALLOW`, detail: `entry ${leg.entry_cents} > union reach ${reach}`, measurable_cents: leg.entry_cents - reach };
  if (!leg.reach_inside_v36_edge) return { owner: "HARD_PREBELL_EDGE_EXCLUDES_REACH_EVIDENCE", detail: `reach evidence ${leg.union_first_evidence_timestamp_epoch} outside ${base.left}..${base.right}`, measurable_cents: null };
  const snapshot = leg.reach_snapshot || leg.last_decision, rest = snapshot?.order_after_cents ?? leg.resting_target_at_edge_cents, cap = snapshot?.pair_cap_cents ?? leg.pair_cap_cents;
  if (Number.isInteger(cap) && reach > cap) return { owner: "PAIR_CAP_ARITHMETIC", detail: `reach ${reach} > cap ${cap}`, measurable_cents: reach - cap };
  if (leg.decision_count === 0) return { owner: "ADMISSION_NO_TWO_SIDED_BOOK", detail: "no decision receipt inside hard edge", measurable_cents: null };
  if (Number.isInteger(rest) && rest >= reach) return { owner: "UNION_REACH_PRECEDED_RESIDENCY_OR_CHANNEL_NOT_REPEATED", detail: `rest ${rest} at/above reach ${reach} but no later union channel`, measurable_cents: 0 };
  const state = snapshot?.combined_state || leg.last_decision?.combined_state || "UNKNOWN";
  const gap = Number.isInteger(rest) ? reach - rest : null;
  if (state === "RISING" && !leg.pulse_floor_ever) return { owner: "RISER_NO_TWO_VISIT_TRAILING_PULSE_FLOOR", detail: `no signable revisited pulse floor; reach ${reach}`, measurable_cents: gap };
  if (state === "RISING") return { owner: "RISER_PULSE_REST_OFF_REACH", detail: `pulse rest ${rest} below reach ${reach}`, measurable_cents: gap };
  if (state === "FALLING") return { owner: "FALLER_V36_NO_CHASE_REST_OFF_REACH", detail: `falling rest ${rest} below reach ${reach}`, measurable_cents: gap };
  return { owner: "SETTLED_BID_MINUS_ONE_REST_OFF_REACH", detail: `settled rest ${rest} below reach ${reach}`, measurable_cents: gap };
}

function gradeAgainstReach(events, reachByEvent, baseByEvent) {
  const rows = [], residuals = [], classRows = [];
  for (const event of events) {
    const reach = reachByEvent.get(event.event_id);
    if (!reach) continue;
    const levels = Object.values(reach.legs).map((leg) => leg.union_reach_cents);
    const reachComplete = levels.every(Number.isInteger), reachCost = reachComplete ? levels.reduce((a, b) => a + b, 0) : null;
    if (!(reachComplete && reachCost < 100)) continue;
    const legRows = [];
    for (const id of Object.keys(event.legs).sort()) {
      const leg = event.legs[id], level = reach.legs[id].union_reach_cents, gap = leg.credited ? leg.entry_cents - level : null;
      const bind = residualOwner(leg, level, baseByEvent.get(event.event_id));
      const row = { event_id: event.event_id, leg_identity: leg.leg_identity, ticker: leg.ticker, category: event.category, starting_price_split: event.starting_price_split, price_region: leg.price_region, bell_confidence: event.bell_confidence, reach_cents: level, reach_sources: reach.legs[id].union_sources, reach_first_evidence_timestamp_epoch: reach.legs[id].union_first_evidence_timestamp_epoch, credited: leg.credited, entry_cents: leg.entry_cents, gap_to_reach_cents: gap, fill_class: leg.fill_class, terminal_state: leg.final_state, terminal_rest_cents: leg.resting_target_at_edge_cents, pair_cap_cents: leg.pair_cap_cents, pulse_floor_ever: leg.pulse_floor_ever, terminal_pulse_floor_cents: leg.pulse_floor_cents, reach_snapshot: leg.reach_snapshot, layer_bind: bind };
      legRows.push(row); rows.push(row); if (bind) residuals.push(row);
    }
    const completed = legRows.every((row) => row.credited), shallowCents = legRows.filter((row) => Number.isInteger(row.gap_to_reach_cents) && row.gap_to_reach_cents > 0).reduce((sum, row) => sum + row.gap_to_reach_cents, 0);
    const grade = completed ? (shallowCents === 0 ? "MATCHED" : "SHALLOW") : "MISSING";
    classRows.push({ event_id: event.event_id, category: event.category, starting_price_split: event.starting_price_split, bell_confidence: event.bell_confidence, reach_cost_cents: reachCost, reach_locked_cents: 100 - reachCost, grade, completed, combined_entry_cents: event.combined_entry_cents, under_par: event.pair_under_par, shallow_cents: shallowCents, measurable_residual_cents: legRows.reduce((sum, row) => sum + (row.layer_bind?.measurable_cents || 0), 0), legs: legRows.map((row) => ({ leg_identity: row.leg_identity, reach_cents: row.reach_cents, credited: row.credited, entry_cents: row.entry_cents, gap_to_reach_cents: row.gap_to_reach_cents, owner: row.layer_bind?.owner || null })) });
  }
  const aggregate = { answer_key_games: classRows.length, answer_key_locked_cents: classRows.reduce((sum, row) => sum + row.reach_locked_cents, 0), grades: countBy(classRows, (row) => row.grade), shallow_gap_cents: distribution(rows.map((row) => row.gap_to_reach_cents).filter((gap) => Number.isInteger(gap) && gap > 0)), measurable_residual_cents: distribution(residuals.map((row) => row.layer_bind?.measurable_cents).filter(Number.isFinite)), completed_pairs: classRows.filter((row) => row.completed).length, under_par_pairs: classRows.filter((row) => row.under_par).length };
  ensure(aggregate.answer_key_games === EXPECTED_REACH.under_par_games && aggregate.answer_key_locked_cents === EXPECTED_REACH.locked_cents, "reach answer-key conservation failed");
  return { rows, residuals, classRows, aggregate };
}

function cellSummary(grades) {
  const groups = new Map();
  for (const row of grades.classRows) { const key = `${row.category}|${row.bell_confidence}`; if (!groups.has(key)) groups.set(key, []); groups.get(key).push(row); }
  return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, rows]) => ({ cell, category: rows[0].category, bell_confidence: rows[0].bell_confidence, answer_key_games: rows.length, reach_locked_cents: rows.reduce((sum, row) => sum + row.reach_locked_cents, 0), grades: countBy(rows, (row) => row.grade), completed_pairs: rows.filter((row) => row.completed).length, under_par_pairs: rows.filter((row) => row.under_par).length, shallow_cents: distribution(rows.map((row) => row.shallow_cents).filter((x) => x > 0)), measurable_residual_cents: distribution(rows.map((row) => row.measurable_residual_cents).filter((x) => x > 0)) }));
}

function v52ShortEvent(eventId) {
  return [...V52_FLOW_EVENTS].find((code) => String(eventId).includes(code)) ?? null;
}

function buildV52bCohort(baseByEvent, censusBytes) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  ensure(Array.isArray(source.rows) && source.rows.length === 1143, `reflex census row count ${source.rows?.length}`);
  const seedMaterial = `V52B_ITERATION1_COHORT25|${V52_COMMIT}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) {
    if (!byCode.has(row.code)) byCode.set(row.code, []);
    byCode.get(row.code).push(row);
  }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (V52_FLOW_EVENTS.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const orderedStrata = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of orderedStrata) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of orderedStrata) {
      if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT" }); added += 1; }
    }
    ensure(added > 0, `cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52b cohort conservation failed");
  return {
    controlling_parent_commit: V52_COMMIT,
    seed_derivation_law: "SHA256('V52B_ITERATION1_COHORT25|' + controlling_parent_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pins,
    fresh_25: selected,
    combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52cCohort(baseByEvent, censusBytes, priorCohortBytes) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const prior = JSON.parse(priorCohortBytes.toString("utf8"));
  ensure(Array.isArray(source.rows) && source.rows.length === 1143, `reflex census row count ${source.rows?.length}`);
  ensure(Array.isArray(prior.fresh_25) && prior.fresh_25.length === 25, "V52b prior cohort missing");
  const excludedPrior = new Set(prior.fresh_25.map((row) => row.code));
  const seedMaterial = `V52C_ITERATION2_COHORT25|${V52B_COMMIT}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) {
    if (!byCode.has(row.code)) byCode.set(row.code, []);
    byCode.get(row.code).push(row);
  }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (V52_FLOW_EVENTS.has(code) || excludedPrior.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const orderedStrata = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of orderedStrata) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of orderedStrata) {
      if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B" }); added += 1; }
    }
    ensure(added > 0, `V52c cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52c cohort conservation failed");
  ensure(selected.every((row) => !excludedPrior.has(row.code)), "V52c reused V52b fresh cohort event");
  return {
    controlling_parent_commit: V52B_COMMIT,
    seed_derivation_law: "SHA256('V52C_ITERATION2_COHORT25|' + controlling_parent_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohort: { commit: V52B_COMMIT, path: ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812/COHORT_SELECTION_RECEIPT.json", sha256: shaBytes(priorCohortBytes), events: prior.fresh_25.length },
    exclusions: { prior_V52b_fresh25_overlap_count: selected.filter((row) => excludedPrior.has(row.code)).length, frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pins,
    fresh_25: selected,
    combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52dCohort(baseByEvent, censusBytes, v52bCohortBytes, v52cCohortBytes) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priorB = JSON.parse(v52bCohortBytes.toString("utf8"));
  const priorC = JSON.parse(v52cCohortBytes.toString("utf8"));
  ensure(Array.isArray(source.rows) && source.rows.length === 1143, `reflex census row count ${source.rows?.length}`);
  ensure(priorB.fresh_25?.length === 25 && priorC.fresh_25?.length === 25, "prior cohort binding missing");
  const excludedB = new Set(priorB.fresh_25.map((row) => row.code)), excludedC = new Set(priorC.fresh_25.map((row) => row.code));
  const excluded = new Set([...excludedB, ...excludedC]);
  const seedMaterial = `V52D_ITERATION3_COHORT25|${V52D_PARENT_COMMIT}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) {
    if (!byCode.has(row.code)) byCode.set(row.code, []);
    byCode.get(row.code).push(row);
  }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (V52_FLOW_EVENTS.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const orderedStrata = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of orderedStrata) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of orderedStrata) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_OR_V52C" }); added += 1; }
    ensure(added > 0, `V52d cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52d cohort conservation failed");
  ensure(selected.every((row) => !excluded.has(row.code)), "V52d reused prior fresh cohort event");
  return {
    controlling_parent_commit: V52D_PARENT_COMMIT,
    seed_derivation_law: "SHA256('V52D_ITERATION3_COHORT25|' + controlling_parent_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: [
      { iteration: "V52B", commit: V52B_COMMIT, path: ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812/COHORT_SELECTION_RECEIPT.json", sha256: shaBytes(v52bCohortBytes), events: priorB.fresh_25.length },
      { iteration: "V52C", commit: V52C_COMMIT, path: ".claude/window1_live_v4_replay/v52c_full_post_onset_read_20260812/COHORT_SELECTION_RECEIPT.json", sha256: shaBytes(v52cCohortBytes), events: priorC.fresh_25.length },
    ],
    exclusions: { prior_V52b_fresh25_overlap_count: selected.filter((row) => excludedB.has(row.code)).length, prior_V52c_fresh25_overlap_count: selected.filter((row) => excludedC.has(row.code)).length, frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pins,
    fresh_25: selected,
    combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52eCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path, bytes }) => ({ iteration, commit, path, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52e cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const seedMaterial = `V52E_ITERATION4_COHORT25|${V52D_COMMIT}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (V52_FLOW_EVENTS.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_V52C_V52D" }); added += 1; }
    ensure(added > 0, `V52e cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52e cohort conservation failed");
  ensure(selected.every((row) => !excluded.has(row.code)), "V52e reused prior fresh cohort event");
  return {
    controlling_parent_commit: V52D_COMMIT,
    seed_derivation_law: "SHA256('V52E_ITERATION4_COHORT25|' + controlling_parent_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, selected.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pins, fresh_25: selected, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52fCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path, bytes }) => ({ iteration, commit, path, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52f cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const seedMaterial = `V52F_ITERATION5_COHORT25|${V52F_PARENT_COMMIT}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const claims = ["26JUL15VANDRO", "26JUL13ZHEBOU", "26JUL18BERSAI", "26JUL20BARYUA"].map((code) => {
    ensure(byCode.has(code), `V52f pre-stated claim missing from census ${code}`);
    ensure(!excluded.has(code), `V52f pre-stated claim overlaps a prior fresh cohort ${code}`);
    const rows = byCode.get(code), category = rows[0].cat;
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    return { code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum: `${category}|${stamps.join("+")}`, role: "FRESH_PRE_STATED_CLAIM_CASE" };
  });
  const reserved = new Set([...V52_FLOW_EVENTS, ...claims.map((row) => row.code)]);
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (reserved.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 21; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 21) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_V52C_V52D_V52E" }); added += 1; }
    ensure(added > 0, `V52f cohort exhausted at ${selected.length}`);
  }
  const fresh25 = [...claims, ...selected];
  const combined = [...pins, ...fresh25];
  ensure(fresh25.length === 25 && combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52f cohort conservation failed");
  ensure(fresh25.every((row) => !excluded.has(row.code)), "V52f reused prior fresh cohort event");
  return {
    controlling_parent_commit: V52F_PARENT_COMMIT,
    seed_derivation_law: "SHA256('V52F_ITERATION5_COHORT25|' + controlling_parent_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, fresh25.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "FOUR_PRE_STATED_FRESH_CLAIM_CASES_PLUS_HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pre_stated_claim_cases: claims,
    pins, fresh_25: fresh25, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52gCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path: receiptPath, bytes }) => ({ iteration, commit, path: receiptPath, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.length === 5 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52g cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const seedMaterial = `V52G_ITERATION6_COHORT25|${V52F_COMMIT}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (V52_FLOW_EVENTS.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_V52C_V52D_V52E_V52F" }); added += 1; }
    ensure(added > 0, `V52g cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52g cohort conservation failed");
  ensure(selected.every((row) => !excluded.has(row.code)), "V52g reused a prior fresh cohort event");
  return {
    controlling_parent_commit: V52F_COMMIT,
    seed_derivation_law: "SHA256('V52G_ITERATION6_COHORT25|' + frozen_V52f_parent_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, selected.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pins, fresh_25: selected, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52hCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path: receiptPath, bytes }) => ({ iteration, commit, path: receiptPath, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.length === 6 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52h cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const seedMaterial = `V52H_ITERATION7_COHORT25|${V52G_COMMIT}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const claimCode = "26JUL14SMIILA";
  ensure(byCode.has(claimCode) && excludedByIteration.V52B?.has(claimCode), "V52h SMIILA named replay must bind to its frozen V52B fresh-cohort provenance");
  const claimRows = byCode.get(claimCode), claimCategory = claimRows[0].cat;
  const claimStamps = claimRows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
  const claim = { code: claimCode, event_id: eventIdForCode(claimCode), category: claimCategory, census_stamps: claimStamps, stratum: `${claimCategory}|${claimStamps.join("+")}`, role: "EXPLICITLY_REUSED_NAMED_OBSERVATION_OUTSIDE_FRESH_25", prior_iteration: "V52B", prior_commit: V52B_COMMIT };
  const reserved = new Set([...V52_FLOW_EVENTS, claimCode]);
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (reserved.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_V52C_V52D_V52E_V52F_V52G" }); added += 1; }
    ensure(added > 0, `V52h cohort exhausted at ${selected.length}`);
  }
  const fresh25 = selected, combined = [...pins, ...fresh25];
  ensure(fresh25.length === 25 && combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52h cohort conservation failed");
  ensure(fresh25.every((row) => !excluded.has(row.code)), "V52h reused a prior fresh cohort event");
  return {
    controlling_parent_commit: V52G_COMMIT,
    seed_derivation_law: "SHA256('V52H_ITERATION7_COHORT25|' + frozen_V52g_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, fresh25.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    named_reused_observation: claim,
    pins, fresh_25: fresh25, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52iCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path: receiptPath, bytes }) => ({ iteration, commit, path: receiptPath, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.length === 7 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52i cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const sourceImplementationCommit = V52I_SOURCE_IMPLEMENTATION_COMMIT;
  ensure(/^[0-9a-f]{40}$/.test(sourceImplementationCommit), "V52i source implementation commit unavailable");
  const seedMaterial = `V52I_ITERATION8_COHORT25|${sourceImplementationCommit}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const reserved = new Set(V52_FLOW_EVENTS);
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (reserved.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_V52C_V52D_V52E_V52F_V52G_V52H" }); added += 1; }
    ensure(added > 0, `V52i cohort exhausted at ${selected.length}`);
  }
  const fresh25 = selected, combined = [...pins, ...fresh25];
  ensure(fresh25.length === 25 && combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52i cohort conservation failed");
  ensure(fresh25.every((row) => !excluded.has(row.code)), "V52i reused a prior fresh cohort event");
  return {
    controlling_parent_commit: V52H_COMMIT,
    source_implementation_commit: sourceImplementationCommit,
    seed_derivation_law: "SHA256('V52I_ITERATION8_COHORT25|' + source_implementation_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, fresh25.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pins, fresh_25: fresh25, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52jCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path: receiptPath, bytes }) => ({ iteration, commit, path: receiptPath, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.length === 8 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52j cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const sourceImplementationCommit = gitHead(repo);
  ensure(/^[0-9a-f]{40}$/.test(sourceImplementationCommit), "V52j source implementation commit unavailable");
  const seedMaterial = `V52J_ITERATION9_COHORT25|${sourceImplementationCommit}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const namedCode = "26JUL12GUEGOM";
  ensure(excludedByIteration.V52I?.has(namedCode), "V52j GUEGOM must retain its V52i fresh-cohort provenance");
  const namedRows = byCode.get(namedCode), namedCategory = namedRows[0].cat;
  const namedStamps = namedRows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
  const namedObservation = { code: namedCode, event_id: eventIdForCode(namedCode), category: namedCategory, census_stamps: namedStamps, stratum: `${namedCategory}|${namedStamps.join("+")}`, role: "EXPLICITLY_REUSED_NAMED_OBSERVATION_OUTSIDE_FRESH_25", prior_iteration: "V52I", prior_commit: V52I_COMMIT };
  const reserved = new Set([...V52_FLOW_EVENTS, namedCode]);
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (reserved.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_THROUGH_V52I" }); added += 1; }
    ensure(added > 0, `V52j cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52j cohort conservation failed");
  ensure(selected.every((row) => !excluded.has(row.code)), "V52j reused a prior fresh cohort event");
  return {
    controlling_policy_base_commit: V52H_COMMIT,
    lineage_parent_commit: V52I_COMMIT,
    V52i_symmetric_depth_refinement_reverted: true,
    source_implementation_commit: sourceImplementationCommit,
    seed_derivation_law: "SHA256('V52J_ITERATION9_COHORT25|' + source_implementation_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, selected.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true, named_observation_excluded_from_fresh_25: selected.every((row) => row.code !== namedCode) },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    named_reused_observation: namedObservation,
    pins, fresh_25: selected, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52kCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path: receiptPath, bytes }) => ({ iteration, commit, path: receiptPath, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.length === 9 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52k cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const sourceImplementationCommit = gitHead(repo);
  ensure(/^[0-9a-f]{40}$/.test(sourceImplementationCommit), "V52k source implementation commit unavailable");
  const seedMaterial = `V52K_ITERATION10_COHORT25|${sourceImplementationCommit}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const namedCode = "26JUL12GUEGOM";
  ensure(excluded.has(namedCode), "V52k GUEGOM must retain prior-cohort provenance");
  const namedRows = byCode.get(namedCode), namedCategory = namedRows[0].cat;
  const namedStamps = namedRows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
  const namedObservation = { code: namedCode, event_id: eventIdForCode(namedCode), category: namedCategory, census_stamps: namedStamps, stratum: `${namedCategory}|${namedStamps.join("+")}`, role: "EXPLICITLY_REUSED_NAMED_OBSERVATION_OUTSIDE_FRESH_25", original_prior_iteration: "V52I", latest_observation_iteration: "V52J", latest_observation_commit: V52J_COMMIT };
  const reserved = new Set([...V52_FLOW_EVENTS, namedCode]);
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (reserved.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_THROUGH_V52J" }); added += 1; }
    ensure(added > 0, `V52k cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52k cohort conservation failed");
  ensure(selected.every((row) => !excluded.has(row.code)), "V52k reused a prior fresh cohort event");
  return {
    controlling_policy_base_commit: V52H_COMMIT,
    lineage_parent_commit: V52J_COMMIT,
    V52i_and_V52j_behavioral_selection_reverted: true,
    source_implementation_commit: sourceImplementationCommit,
    seed_derivation_law: "SHA256('V52K_ITERATION10_COHORT25|' + source_implementation_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, selected.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true, named_observation_excluded_from_fresh_25: selected.every((row) => row.code !== namedCode) },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    named_reused_observation: namedObservation,
    pins, fresh_25: selected, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52lCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path: receiptPath, bytes }) => ({ iteration, commit, path: receiptPath, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.length === 10 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52l cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const parentCommit = "fc17d0d3ec3db4795d2e25a986bb9bfa1806714b";
  const seedMaterial = `V52L_CAUSAL_ONSET_COHORT25|${parentCommit}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (V52_FLOW_EVENTS.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_THROUGH_V52K" }); added += 1; }
    ensure(added > 0, `V52l cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52l cohort conservation failed");
  ensure(selected.every((row) => !excluded.has(row.code)), "V52l reused a prior fresh cohort event");
  return {
    controlling_policy_commit: V52H_COMMIT,
    part_A_parent_commit: parentCommit,
    seed_derivation_law: "SHA256('V52L_CAUSAL_ONSET_COHORT25|' + Part_A_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, selected.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pins, fresh_25: selected, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52mCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path: receiptPath, bytes }) => ({ iteration, commit, path: receiptPath, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.length === 11 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52m cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const parentCommit = V52L_COMMIT;
  const seedMaterial = `V52M_MACRO_RECOGNITION_COHORT25|${parentCommit}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (V52_FLOW_EVENTS.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_THROUGH_V52L" }); added += 1; }
    ensure(added > 0, `V52m cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52m cohort conservation failed");
  ensure(selected.every((row) => !excluded.has(row.code)), "V52m reused a prior fresh cohort event");
  return {
    controlling_policy_commit: V52L_COMMIT,
    seed_derivation_law: "SHA256('V52M_MACRO_RECOGNITION_COHORT25|' + V52L_adopted_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, selected.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pins, fresh_25: selected, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52nCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path: receiptPath, bytes }) => ({ iteration, commit, path: receiptPath, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.length === 12 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52n cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const seedMaterial = `V52N_RECOGNITION_CONFIDENCE_GATES_COHORT25|${V52M_COMMIT}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (V52_FLOW_EVENTS.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_THROUGH_V52M" }); added += 1; }
    ensure(added > 0, `V52n cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52n cohort conservation failed");
  ensure(selected.every((row) => !excluded.has(row.code)), "V52n reused a prior fresh cohort event");
  return {
    controlling_policy_commit: V52M_COMMIT,
    behavioral_lineage_commit: V52L_COMMIT,
    seed_derivation_law: "SHA256('V52N_RECOGNITION_CONFIDENCE_GATES_COHORT25|' + V52M_parent_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, selected.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pins, fresh_25: selected, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52oCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path: receiptPath, bytes }) => ({ iteration, commit, path: receiptPath, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.length === 13 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52o cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const seedMaterial = `V52O_BENCHMARKED_ROLE_INSTRUMENT_COHORT25|${V52N_COMMIT}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (V52_FLOW_EVENTS.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_THROUGH_V52N" }); added += 1; }
    ensure(added > 0, `V52o cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52o cohort conservation failed");
  ensure(selected.every((row) => !excluded.has(row.code)), "V52o reused a prior fresh cohort event");
  return {
    controlling_parent_commit: V52N_COMMIT,
    behavioral_lineage_commit: V52L_COMMIT,
    superseded_observation_bindings_retained: ["V52M_MACRO_RECOGNITION", "V52N_RECOGNITION_CONFIDENCE_GATES"],
    seed_derivation_law: "SHA256('V52O_BENCHMARKED_ROLE_INSTRUMENT_COHORT25|' + V52N_parent_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, selected.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pins, fresh_25: selected, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52pCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path: receiptPath, bytes }) => ({ iteration, commit, path: receiptPath, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.length === 14 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52p cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const seedMaterial = `V52P_RIPENESS_GATED_ROLE_BINDING_COHORT25|${V52O_COMMIT}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (V52_FLOW_EVENTS.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_THROUGH_V52O" }); added += 1; }
    ensure(added > 0, `V52p cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52p cohort conservation failed");
  ensure(selected.every((row) => !excluded.has(row.code)), "V52p reused a prior fresh cohort event");
  return {
    controlling_parent_commit: V52O_COMMIT,
    behavioral_lineage_commit: V52L_COMMIT,
    superseded_observation_bindings_retained: ["V52M_MACRO_RECOGNITION", "V52N_RECOGNITION_CONFIDENCE_GATES", "V52O_BENCHMARKED_ROLE_INSTRUMENT"],
    seed_derivation_law: "SHA256('V52P_RIPENESS_GATED_ROLE_BINDING_COHORT25|' + V52O_parent_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, selected.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pins, fresh_25: selected, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52qCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path: receiptPath, bytes }) => ({ iteration, commit, path: receiptPath, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.length === 15 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52q cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const seedMaterial = `V52Q_ANCHOR_CORRECTION_COHORT25|${V52P_COMMIT}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (V52_FLOW_EVENTS.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_THROUGH_V52P" }); added += 1; }
    ensure(added > 0, `V52q cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52q cohort conservation failed");
  ensure(selected.every((row) => !excluded.has(row.code)), "V52q reused a prior fresh cohort event");
  return {
    controlling_parent_commit: V52P_COMMIT,
    behavioral_lineage_commit: V52L_COMMIT,
    superseded_observation_bindings_retained: ["V52M_MACRO_RECOGNITION", "V52N_RECOGNITION_CONFIDENCE_GATES", "V52O_BENCHMARKED_ROLE_INSTRUMENT", "V52P_RIPENESS_GATED_ROLE_BINDING"],
    seed_derivation_law: "SHA256('V52Q_ANCHOR_CORRECTION_COHORT25|' + V52P_parent_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, selected.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pins, fresh_25: selected, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52rCohort(baseByEvent, censusBytes, priorReceipts) {
  const source = JSON.parse(censusBytes.toString("utf8"));
  const priors = priorReceipts.map(({ iteration, commit, path: receiptPath, bytes }) => ({ iteration, commit, path: receiptPath, bytes, receipt: JSON.parse(bytes.toString("utf8")) }));
  ensure(source.rows?.length === 1143 && priors.length === 16 && priors.every((item) => item.receipt.fresh_25?.length === 25), "V52r cohort inputs invalid");
  const excludedByIteration = Object.fromEntries(priors.map((item) => [item.iteration, new Set(item.receipt.fresh_25.map((row) => row.code))]));
  const excluded = new Set(Object.values(excludedByIteration).flatMap((set) => [...set]));
  const seedMaterial = `V52R_ASSEMBLED_POLICY_COHORT25|${V52Q_COMMIT}`;
  const seedSha256 = shaBytes(Buffer.from(seedMaterial));
  const baseIds = [...baseByEvent.keys()];
  const eventIdForCode = (code) => {
    const matches = baseIds.filter((eventId) => String(eventId).includes(code));
    ensure(matches.length === 1, `cohort code ${code} bound to ${matches.length} events`);
    return matches[0];
  };
  const byCode = new Map();
  for (const row of source.rows) { if (!byCode.has(row.code)) byCode.set(row.code, []); byCode.get(row.code).push(row); }
  const pins = [...V52_FLOW_EVENTS].sort().map((code) => ({ code, event_id: eventIdForCode(code), role: "FROZEN_PIN" }));
  const strata = new Map();
  for (const [code, rows] of byCode) {
    if (V52_FLOW_EVENTS.has(code) || excluded.has(code)) continue;
    const category = rows[0].cat;
    ensure(rows.every((row) => row.cat === category), `category disagreement ${code}`);
    const stamps = rows.sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
    const stratum = `${category}|${stamps.join("+")}`;
    if (!strata.has(stratum)) strata.set(stratum, []);
    strata.get(stratum).push({ code, event_id: eventIdForCode(code), category, census_stamps: stamps, stratum });
  }
  const hashRank = (value) => shaBytes(Buffer.from(`${seedSha256}|${value}`));
  const ordered = [...strata].sort(([a], [b]) => hashRank(a).localeCompare(hashRank(b)) || a.localeCompare(b));
  for (const [stratum, rows] of ordered) rows.sort((a, b) => hashRank(`${stratum}|${a.code}`).localeCompare(hashRank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
  const selected = [];
  for (let round = 0; selected.length < 25; round += 1) {
    let added = 0;
    for (const [, rows] of ordered) if (rows[round] && selected.length < 25) { selected.push({ ...rows[round], role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_THROUGH_V52Q" }); added += 1; }
    ensure(added > 0, `V52r cohort exhausted at ${selected.length}`);
  }
  const combined = [...pins, ...selected];
  ensure(combined.length === 30 && new Set(combined.map((row) => row.event_id)).size === 30, "V52r cohort conservation failed");
  ensure(selected.every((row) => !excluded.has(row.code)), "V52r reused a prior fresh cohort event");
  return {
    controlling_parent_commit: V52Q_COMMIT,
    behavioral_lineage_commit: V52L_COMMIT,
    superseded_observation_bindings_retained: ["V52M_MACRO_RECOGNITION", "V52N_RECOGNITION_CONFIDENCE_GATES", "V52P_RIPENESS_GATED_ROLE_BINDING", "V52Q_ANCHOR_CORRECTION"],
    seed_derivation_law: "SHA256('V52R_ASSEMBLED_POLICY_COHORT25|' + V52Q_parent_commit)",
    seed_material: seedMaterial,
    seed_sha256: seedSha256,
    source: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(censusBytes), rows: source.rows.length },
    excluded_prior_fresh_cohorts: priors.map((item) => ({ iteration: item.iteration, commit: item.commit, path: item.path, sha256: shaBytes(item.bytes), events: item.receipt.fresh_25.length })),
    exclusions: { ...Object.fromEntries(Object.entries(excludedByIteration).map(([iteration, set]) => [`prior_${iteration}_fresh25_overlap_count`, selected.filter((row) => set.has(row.code)).length])), frozen_pins_are_intentionally_reused: true },
    stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN_ONE_EVENT_PER_STRATUM", strata_available: strata.size },
    pins, fresh_25: selected, combined_30: combined,
    event_list_sha256: shaBytes(Buffer.from(combined.map((row) => row.event_id).sort().join("\n") + "\n")),
  };
}

function buildV52FlowPackage(run, baseByEvent, tapePackBytes, onsetReceiptBytes, expectedEvents = 5, stageLabel = "STAGE_1_FLOW_CHECK_FIVE_GAMES_ONLY") {
  const events = run.marketEvents.sort((a, b) => a.event_id.localeCompare(b.event_id));
  ensure(events.length === expectedEvents, `V52 flow event count ${events.length}`);
  const legs = events.flatMap((event) => Object.values(event.legs));
  ensure(legs.length === expectedEvents * 2, `V52 flow leg count ${legs.length}`);
  const postActions = run.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && ["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE", "GAP_CREDIT_REPRICE_DOWN"].includes(row.kind));
  const assertions = {
    zero_posts_pre_onset: { violations: postActions.filter((row) => !row.birth_license?.onset?.passed).map((row) => `${row.leg_identity}@${row.receipt}`) },
    zero_posts_on_no_tape: { violations: postActions.filter((row) => !row.birth_license?.read?.passed).map((row) => `${row.leg_identity}@${row.receipt}`) },
    zero_levels_from_displayed_bids: { violations: postActions.filter((row) => row.birth_license?.level?.displayed_bid_consumed !== false).map((row) => `${row.leg_identity}@${row.receipt}`) },
    every_post_has_four_license_fields: { violations: postActions.filter((row) => !(row.birth_license?.onset?.passed && row.birth_license?.read?.passed && ((isV52h || isV52DepthValidation || isV52CausalOnset) ? row.birth_license?.diary && row.birth_license?.coherence?.disagreement_clear : row.birth_license?.diary?.passed && row.birth_license?.coherence?.lows_under_par && row.birth_license?.coherence?.disagreement_clear))).map((row) => `${row.leg_identity}@${row.receipt}`) },
    scavenger_off: { violations: postActions.filter((row) => row.birth_license?.scavenger?.enabled !== false).map((row) => `${row.leg_identity}@${row.receipt}`) },
  };
  for (const value of Object.values(assertions)) value.pass = value.violations.length === 0;
  const pass = Object.values(assertions).every((value) => value.pass);
  const trace = legs.flatMap((leg) => leg.judgment_trace_rows).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.leg_identity.localeCompare(b.leg_identity) || a.receipt.localeCompare(b.receipt));
  const outcomes = events.map((event) => ({
    event_id: event.event_id,
    short_event: v52ShortEvent(event.event_id),
    completed_pair_observation: event.completed_pair,
    combined_entry_cents_observation: event.combined_entry_cents,
    under_par_observation: event.pair_under_par,
    legs: Object.values(event.legs).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)).map((leg) => ({
      leg_identity: leg.leg_identity,
      onset: leg.v52_onset,
      final_state: leg.final_state,
      entry_cents_observation: leg.entry_cents,
      fill_timestamp_epoch: leg.fill_timestamp_epoch,
      terminal_reason: leg.terminal_reason,
      gate_evaluations: leg.judgment_gate_evaluations,
      gate_posts: leg.judgment_gate_posts,
      gate_blocks: leg.judgment_gate_blocks,
      post_onset_true_trade_low_cents: leg.post_onset_true_trade_low_cents,
      post_onset_true_trade_low_receipt: leg.post_onset_true_trade_low_receipt,
    })),
  }));
  return {
    pass,
    assertions,
    post_actions: postActions.length,
    trace,
    outcomes,
    control: {
      stage: stageLabel,
      behavioral_tuning_permitted: false,
      mechanical_repair_only: true,
      outcome_grading: null,
      tape_pack_commit: FIVE_GAME_TAPE_PACK_COMMIT,
      tape_pack_manifest_sha256: shaBytes(tapePackBytes),
      stability_onset_commit: STABILITY_ONSET_COMMIT,
      stability_receipt_sha256: shaBytes(onsetReceiptBytes),
    },
  };
}

function buildV52NamedAutopsy(candidateRun, baselineRun, baseByEvent, printLoad, stage1Flow) {
  const exactEvent = (run, code) => {
    const matches = run.marketEvents.filter((event) => event.event_id.includes(code));
    ensure(matches.length === 1, `expected one ${code} event, found ${matches.length}`);
    return matches[0];
  };
  const relevantActions = (eventId) => candidateRun.actions
    .filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && row.event_id === eventId)
    .sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
  const lifecycle = (rows, legIdentity) => rows.filter((row) => row.leg_identity === legIdentity && [
    "PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE", "GAP_CREDIT_REPRICE_DOWN", "PAIR_ARM",
    "DEEP_GAP_WITHHOLD_START", "DEEP_GAP_WITHHOLD_RELEASE", "FILL",
  ].includes(row.kind));
  const legSnapshot = (event, legId) => {
    const leg = event.legs[legId];
    return { leg_identity: leg.leg_identity, onset: leg.v52_onset, credited: leg.credited, entry_cents: leg.entry_cents, action_timestamp_epoch: leg.action_timestamp_epoch, fill_timestamp_epoch: leg.fill_timestamp_epoch, fill_class: leg.fill_class, post_onset_true_trade_low_cents: leg.post_onset_true_trade_low_cents, post_onset_true_trade_low_receipt: leg.post_onset_true_trade_low_receipt, terminal_reason: leg.terminal_reason, gate_evaluations: leg.judgment_gate_evaluations, gate_posts: leg.judgment_gate_posts, gate_blocks: leg.judgment_gate_blocks };
  };
  const withType = (rowType, rows) => rows.map((row) => ({ row_type: rowType, ...row }));

  const arsEvent = exactEvent(candidateRun, "26JUL19ARSMAR");
  const arsBaseline = exactEvent(baselineRun, "26JUL19ARSMAR");
  const arsBase = baseByEvent.get(arsEvent.event_id);
  const arsLeg = arsEvent.legs.ARS;
  const arsActions = relevantActions(arsEvent.event_id);
  const arsLife = lifecycle(arsActions, arsLeg.leg_identity);
  const arsPrints35 = (printLoad.byTicker.get(arsLeg.ticker) || []).filter((row) => row.price === 35);
  ensure(arsPrints35.length > 0, "ARSMAR ARS 35-cent print missing");
  const arsCriticalTs = arsPrints35[0].ts;
  const arsCriticalPrints = arsPrints35.filter((row) => row.ts === arsCriticalTs);
  const arsGateTrace = stage1Flow.trace.filter((row) => row.event_id === arsEvent.event_id && row.leg_identity === arsLeg.leg_identity);
  const arsWindowTrace = arsGateTrace.filter((row) => Math.abs(row.timestamp_epoch - arsCriticalTs) <= 300);
  const arsWindowActions = arsActions.filter((row) => row.leg_identity === arsLeg.leg_identity && Math.abs(row.timestamp_epoch - arsCriticalTs) <= 300);
  const arsFirstPost = arsLife.find((row) => row.kind === "PLACE_REST") ?? null;
  const arsRestAtPrint = arsFirstPost && arsFirstPost.timestamp_epoch <= arsCriticalTs ? arsFirstPost.target_cents : null;
  const arsPrintRows = arsCriticalPrints.map((row) => ({
    row_type: "CERTIFIED_TRUE_PRINT",
    event_id: arsEvent.event_id,
    leg_identity: arsLeg.leg_identity,
    ticker: row.ticker,
    ...clockFields(row.ts, arsBase),
    receipt: row.receipt,
    trade_id: row.trade_id,
    price_cents: row.price,
    size: row.size,
    taker_side: row.taker_side,
    taker_book_side: row.taker_book_side,
    rest_price_cents_at_receipt: arsRestAtPrint,
    crediting_organ_evaluations: [
      { organ: "LAWFUL_STANDING_REST_PRESENCE", passed: Number.isInteger(arsRestAtPrint), result: Number.isInteger(arsRestAtPrint) ? "CONTINUE" : "WITHHOLD_NO_LAWFUL_STANDING_REST" },
      { organ: "TRADES_AS_TRUTH_AT_OR_BELOW_REST", reached: Number.isInteger(arsRestAtPrint), passed: Number.isInteger(arsRestAtPrint) ? row.price <= arsRestAtPrint : null, result: Number.isInteger(arsRestAtPrint) ? (row.price <= arsRestAtPrint ? "CREDIT" : "WITHHOLD_TRADE_ABOVE_REST") : "NOT_REACHED" },
      { organ: "S12_DEEP_GAP_GUARD", reached: false, result: "NOT_A_CREDITING_FILTER" },
    ],
  }));
  const arsCriticalTrace = [
    ...withType("GATE_PERMISSION_EVALUATION", arsWindowTrace),
    ...withType("ORDER_LIFECYCLE_ACTION", arsWindowActions),
    ...arsPrintRows,
  ].sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.row_type).localeCompare(String(b.row_type)) || String(a.receipt).localeCompare(String(b.receipt)));
  const arsBefore = [...arsGateTrace].filter((row) => row.timestamp_epoch <= arsCriticalTs).at(-1) ?? null;
  const arsAfter = arsGateTrace.find((row) => row.timestamp_epoch >= arsCriticalTs) ?? null;

  const polEvent = exactEvent(candidateRun, "26JUL12POLKUH");
  const polBaseline = exactEvent(baselineRun, "26JUL12POLKUH");
  const polActions = relevantActions(polEvent.event_id);
  const polGateTrace = stage1Flow.trace.filter((row) => row.event_id === polEvent.event_id);
  const polLegs = Object.fromEntries(Object.keys(polEvent.legs).sort().map((legId) => {
    const leg = polEvent.legs[legId], prior = polBaseline.legs[legId], life = lifecycle(polActions, leg.leg_identity), firstPost = life.find((row) => row.kind === "PLACE_REST") ?? null;
    return [legId, {
      baseline_V49b: { credited: prior.credited, entry_cents: prior.entry_cents, action_timestamp_epoch: prior.action_timestamp_epoch, fill_timestamp_epoch: prior.fill_timestamp_epoch, fill_class: prior.fill_class, terminal_reason: prior.terminal_reason },
      V52: legSnapshot(polEvent, legId),
      first_licensed_post: firstPost,
      post_onset_diary_levels: [...new Set(polGateTrace.filter((row) => row.leg_identity === leg.leg_identity).map((row) => row.birth_license?.diary?.own_post_onset_true_trade_low_cents).filter(Number.isInteger))],
      gate_verdict_counts: countBy(polGateTrace.filter((row) => row.leg_identity === leg.leg_identity), (row) => row.gate_verdict),
      lifecycle: life,
    }];
  }));

  const exactIdentityCorrection = {
    defect: "GENERIC_SUBSTRING_NAMED_LOOKUP_COULD_SELECT_AN_EARLIER_EVENT_WITH_THE_SAME_PAIR_CODE",
    prior_generic_ARSMAR_event_id: candidateRun.marketEvents.find((row) => row.event_id.includes("ARSMAR"))?.event_id ?? null,
    exact_tape_pack_ARSMAR_event_id: arsEvent.event_id,
    prior_generic_POLKUH_event_id: candidateRun.marketEvents.find((row) => row.event_id.includes("POLKUH"))?.event_id ?? null,
    exact_tape_pack_POLKUH_event_id: polEvent.event_id,
    replay_behavior_changed: false,
    score_artifacts_changed_by_correction: false,
  };
  const summary = {
    scope: "TRACE_ONLY_POST_RUN_AUTOPSY_NO_BEHAVIORAL_EDIT",
    exact_identity_binding: exactIdentityCorrection,
    onset_clause_1_binding: {
      law: "EARLIEST_CAUSALLY_VALID_OF_A_OR_B",
      A: "SPREAD_COLLAPSE_PLUS_CROSS_LEG_MIDSUM_SETTLE",
      B: "SUSTAINED_TRADE_CADENCE_ARRIVAL",
      ruling_authority: "OPERATOR_V52_JUDGMENT_GATE_ORDER_2026-08-12",
      method_receipt_commit: STABILITY_ONSET_COMMIT,
      ARS_selected_candidate: arsLeg.v52_onset.selected_candidate,
      POL_selected_candidate: polEvent.legs.POL.v52_onset.selected_candidate,
      KUH_selected_candidate: polEvent.legs.KUH.v52_onset.selected_candidate,
    },
    ARSMAR: {
      event_id: arsEvent.event_id,
      critical_leg: arsLeg.leg_identity,
      critical_print_timestamp_epoch: arsCriticalTs,
      minutes_after_window_open: (arsCriticalTs - arsBase.left) / 60,
      critical_print_receipts: arsPrintRows.map((row) => ({ receipt: row.receipt, trade_id: row.trade_id, price_cents: row.price_cents, size: row.size, taker_side: row.taker_side, taker_book_side: row.taker_book_side })),
      rest_licensed_and_standing_at_critical_print: Number.isInteger(arsRestAtPrint),
      rest_price_cents_at_critical_print: arsRestAtPrint,
      gate_evaluation_immediately_before: arsBefore,
      gate_evaluation_immediately_after: arsAfter,
      S12_withhold_rows_at_critical_window: arsWindowActions.filter((row) => row.kind === "DEEP_GAP_WITHHOLD_START").length,
      miss_owner_before_print: arsBefore?.gate_verdict ?? null,
      miss_owner_after_print: arsAfter?.gate_verdict ?? null,
      first_licensed_post: arsFirstPost,
      V49b: { completed: arsBaseline.completed_pair, combined_entry_cents: arsBaseline.combined_entry_cents, legs: Object.fromEntries(Object.keys(arsBaseline.legs).sort().map((legId) => [legId, legSnapshot(arsBaseline, legId)])) },
      V52: { completed: arsEvent.completed_pair, combined_entry_cents: arsEvent.combined_entry_cents, legs: Object.fromEntries(Object.keys(arsEvent.legs).sort().map((legId) => [legId, legSnapshot(arsEvent, legId)])) },
    },
    POLKUH: { event_id: polEvent.event_id, legs: polLegs },
  };
  return { summary, arsFullGateTrace: arsGateTrace, arsCriticalTrace, arsRestLifecycle: arsLife, polFullGateTrace: polGateTrace, polLegs };
}

async function main() {
  ensure(gitHead(v36Root) === V36_COMMIT, "V36 frozen worktree mismatch");
  ensure(gitHead(reachRoot) === REACH_COMMIT, "reach frozen worktree mismatch");
  ensure(gitHead(gapRoot) === GAP_COMMIT, "gap-grade frozen worktree mismatch");
  ensure(isPlacementStack || gitHead(repo) === GAP_COMMIT || compare, "V38 must build from b581cbb parent before commit");
  const examPolicyIdentity = isV52sExam ? v52sExamAdapter.attestFrozenV52lPolicy(repo) : isV52rExam ? v52rExamAdapter.attestFrozenPolicy(repo) : null;
  const examV52eLaneIdentity = (isV52rExam || isV52sExam) ? v52rExamAdapter.attestV52eLaneUnchanged(repo) : null;
  const examSanityFence = isV52rExam ? (() => {
    ensure(sanityReceiptPath && fs.existsSync(sanityReceiptPath), "V52r disposition804 requires a completed 30-game sanity receipt");
    const receipt = JSON.parse(fs.readFileSync(sanityReceiptPath, "utf8"));
    ensure(receipt.pass === true && receipt.outcomes_and_score_artifacts_byte_identical === true && receipt.frozen_commit === v52rExamAdapter.FROZEN_V52R_COMMIT, "V52r 30-game sanity receipt is invalid");
    return receipt;
  })() : null;
  safeOutput(output);
  const n9Binding = isV52e ? loadN9CleanStore() : null;
  if (isV52e) policy.configurePalantir(n9Binding.store);
  const v36Package = path.join(v36Root, V36_PACKAGE), gapPackage = path.join(gapRoot, GAP_PACKAGE);
  const v36StrictFrozenEvents = readRows(path.join(v36Package, "STRICT_EVENT_LEDGER.jsonl.gz"));
  ensure(v36StrictFrozenEvents.length === 804, "frozen V36 strict ledger must contain 804 events");
  const spans = JSON.parse(fs.readFileSync(path.join(v36Package, "WINDOW1_SPAN_804.json"), "utf8")).rows;
  const v36Trace = JSON.parse(fs.readFileSync(path.join(v36Package, "STRICT_DECISION_TRACE_1608.json"), "utf8")).rows;
  const reachRows = readRows(path.join(gapPackage, "V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz"));
  ensure(spans.length === 804 && v36Trace.length === 1608 && reachRows.length === 1608, "frozen population mismatch");
  const traceByLeg = new Map(v36Trace.map((row) => [row.leg_identity, row])), reachByLeg = new Map(reachRows.map((row) => [row.leg_identity, row]));
  const reachByEvent = new Map(), baseByEvent = new Map(), tickerBounds = new Map();
  const identity81Path = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/THE_81_IDENTITY_LEDGER.json";
  const identity81Bytes = isV49b ? gitShow(IDENTITY_81_COMMIT, identity81Path) : null;
  const identity81 = isV49b ? JSON.parse(identity81Bytes) : null;
  const v49bDoctrineByEventLeg = new Map();
  if (isV49b) {
    ensure(identity81.conservation.games === 81 && identity81.the_81.length === 81, "81-identity ledger game conservation failed");
    for (const game of identity81.the_81) for (const missing of game.missing) {
      const key = `${game.event}|${missing.leg}`;
      ensure(!v49bDoctrineByEventLeg.has(key), `duplicate V49b doctrine ${key}`);
      ensure(Number.isInteger(missing.P) && missing.P >= 1 && missing.P <= 99 && missing.standable === true, `unlawful V49b doctrine ${key}`);
      v49bDoctrineByEventLeg.set(key, { identity_key: key, source_event: game.event, leg_id: missing.leg, level_cents: missing.P, frozen_verdict: missing.verdict, frozen_evidence_type: missing.evidence_type, frozen_evidence_timestamp_epoch: missing.evidence_ts, completing_print_timestamp_epoch: missing.print_ts, completing_print_price_cents: missing.P, completing_print_size: missing.print_size, completing_print_side: missing.print_side, window_total_seconds: missing.window_total_s });
    }
    ensure(v49bDoctrineByEventLeg.size === 93, `V49b doctrine leg count ${v49bDoctrineByEventLeg.size}`);
  }
  for (const row of reachRows) {
    if (!reachByEvent.has(row.event_id)) reachByEvent.set(row.event_id, { event_id: row.event_id, legs: {} });
    reachByEvent.get(row.event_id).legs[row.leg_id] = row;
  }
  for (const span of spans) {
    const scheduled = Number.isFinite(span.formation_clock?.t_minus_scheduled_seconds) ? span.w1_left_epoch + span.formation_clock.t_minus_scheduled_seconds : null;
    const actualBell = Number.isFinite(span.formation_clock?.t_minus_actual_bell_seconds) ? span.w1_left_epoch + span.formation_clock.t_minus_actual_bell_seconds : null;
    const base = { event_id: span.event_id, category: span.category, starting_price_split: span.starting_price_split, bell_confidence: span.precision_class, edge_source_field: span.edge_source_field, discovery_epoch: span.w1_left_epoch, left: span.w1_left_epoch, right: span.w1_right_epoch, scheduled, actual_bell: actualBell, v52_flow_trace: isV52FullExam || (isV52 && Boolean(v52ShortEvent(span.event_id))), legs: {} };
    for (const leg of span.per_leg) {
      const prior = traceByLeg.get(leg.leg_identity), reach = reachByLeg.get(leg.leg_identity);
      ensure(prior && reach, `missing leg binding ${leg.leg_identity}`);
      const legId = leg.leg_identity.split("|").at(-1);
      base.legs[legId] = { leg_id: legId, leg_identity: leg.leg_identity, ticker: leg.ticker, category: span.category, price_region: prior.price_region, leg_direction: reach.leg_direction, reach, ...(isV49b ? { v49b_doctrine: v49bDoctrineByEventLeg.get(`${span.event_id}|${legId}`) ?? null } : {}) };
      tickerBounds.set(leg.ticker, { left: span.w1_left_epoch, right: span.w1_right_epoch });
    }
    ensure(Object.keys(base.legs).length === 2, `event not paired ${span.event_id}`);
    baseByEvent.set(span.event_id, base);
  }
  ensure(baseByEvent.size === 804 && tickerBounds.size === 1608, "base conservation failed");
  if (isV49b) ensure([...baseByEvent.values()].flatMap((base) => Object.values(base.legs)).filter((leg) => leg.v49b_doctrine).length === 93, "V49b doctrine identities did not bind to replay legs");
  const v52mTaxonomyBytes = isV52MacroRecognition ? gitShow(SHAPE_TAXONOMY_COMMIT, SHAPE_TAXONOMY_PATH) : null;
  const v52oTaxonomyCsvBytes = (isV52o || isV52Ripeness || isV52r) ? gitShow(SHAPE_TAXONOMY_COMMIT, SHAPE_TAXONOMY_CSV_PATH) : null;
  const v52pRipenessBytes = isV52Ripeness ? gitShow(RIPENESS_COMMIT, RIPENESS_PATH) : null;
  const v52qDiscrepancyBytes = (isV52q || isV52r) ? gitShow(ANCHOR_DISCREPANCY_COMMIT, ANCHOR_DISCREPANCY_PATH) : null;
  const v52mFloorDepthBytes = isV52MacroRecognition ? gitShow(SHAPE_FLOOR_DEPTH_COMMIT, SHAPE_FLOOR_DEPTH_PATH) : null;
  const v52mShapeBinding = isV52MacroRecognition ? {
    taxonomy: JSON.parse(v52mTaxonomyBytes),
    floor_tables: JSON.parse(v52mFloorDepthBytes),
    taxonomy_provenance: { label: "SHAPE_TAXONOMY_BUILD1", commit: SHAPE_TAXONOMY_COMMIT, path: SHAPE_TAXONOMY_PATH, sha256: shaBytes(v52mTaxonomyBytes) },
    floor_table_provenance: { label: "PER_SHAPE_FLOOR_DEPTH_TABLES", commit: SHAPE_FLOOR_DEPTH_COMMIT, path: SHAPE_FLOOR_DEPTH_PATH, sha256: shaBytes(v52mFloorDepthBytes) },
  } : null;
  if (isV52MacroRecognition) policy.configureShapeLibrary(v52mShapeBinding);
  const v52pRipenessBinding = isV52Ripeness ? {
    artifact: JSON.parse(v52pRipenessBytes),
    provenance: { label: "RECOGNITION_OPERATING_POINT_RECONCILIATION", commit: RIPENESS_COMMIT, path: RIPENESS_PATH, sha256: shaBytes(v52pRipenessBytes) },
  } : null;
  if (isV52Ripeness) policy.configureRipeness(v52pRipenessBinding);
  const v52qAnchorBinding = (isV52q || isV52r) ? {
    method: { name: "SPREAD_SETTLE_MID_AT_FORMATION_END", commit: SHAPE_TAXONOMY_COMMIT, path: SHAPE_TAXONOMY_PATH, sha256: shaBytes(v52mTaxonomyBytes), literal: "first mid with spread<=10c holding <=20c for 30min" },
    ground_truth: { ...groundTruthWindowBinding.binding, commit: groundTruthWindowBinding.binding.source_commit, path: groundTruthWindowBinding.binding.source_path },
    discrepancy: { commit: ANCHOR_DISCREPANCY_COMMIT, path: ANCHOR_DISCREPANCY_PATH, sha256: shaBytes(v52qDiscrepancyBytes) },
    series_floor: "FORMATION_END_INCLUSIVE",
  } : null;
  if (isV52q || isV52r) policy.configureAnchorCorrection(v52qAnchorBinding);
  const v52rTRD5Bytes = isV52r ? gitShow(TRD5_COMMIT, TRD5_PATH) : null;
  const v52rLOW1Bytes = isV52r ? gitShow(LOW1_COMMIT, LOW1_PATH) : null;
  const v52rTRD5Binding = isV52r ? { artifact: JSON.parse(v52rTRD5Bytes), provenance: { label: "GATE_POLICY_EVALUATION_LIVE_COORDINATES", commit: TRD5_COMMIT, path: TRD5_PATH, sha256: shaBytes(v52rTRD5Bytes), bytes: v52rTRD5Bytes.length } } : null;
  const v52rLOW1Binding = isV52r ? { artifact: JSON.parse(v52rLOW1Bytes), provenance: { label: "DOWN_TARGET_FRONTIER", commit: LOW1_COMMIT, path: LOW1_PATH, sha256: shaBytes(v52rLOW1Bytes), bytes: v52rLOW1Bytes.length } } : null;
  if (isV52r) { policy.configureTRD5(v52rTRD5Binding); policy.configureLOW1(v52rLOW1Binding); }
  const v52bCensusBytes = isV52b ? gitShow(REFLEX_CENSUS_COMMIT, ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json") : null;
  let v52bCohort = isV52b ? buildV52bCohort(baseByEvent, v52bCensusBytes) : null;
  const v52cCensusBytes = isV52c ? gitShow(REFLEX_CENSUS_COMMIT, ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json") : null;
  const v52cPriorCohortBytes = isV52c ? gitShow(V52B_COMMIT, ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812/COHORT_SELECTION_RECEIPT.json") : null;
  const v52cCohort = isV52c ? buildV52cCohort(baseByEvent, v52cCensusBytes, v52cPriorCohortBytes) : null;
  const v52dCensusBytes = isV52d ? gitShow(REFLEX_CENSUS_COMMIT, ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json") : null;
  const v52dPriorBCohortBytes = isV52d ? gitShow(V52B_COMMIT, ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812/COHORT_SELECTION_RECEIPT.json") : null;
  const v52dPriorCCohortBytes = isV52d ? gitShow(V52C_COMMIT, ".claude/window1_live_v4_replay/v52c_full_post_onset_read_20260812/COHORT_SELECTION_RECEIPT.json") : null;
  const v52dCohort = isV52d ? buildV52dCohort(baseByEvent, v52dCensusBytes, v52dPriorBCohortBytes, v52dPriorCCohortBytes) : null;
  const v52eCensusBytes = isV52e && !isV52FullExam ? gitShow(REFLEX_CENSUS_COMMIT, ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json") : null;
  const v52ePriorReceipts = isV52e && !isV52FullExam ? [
    { iteration: "V52B", commit: V52B_COMMIT, path: ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52B_COMMIT, ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812/COHORT_SELECTION_RECEIPT.json") },
    { iteration: "V52C", commit: V52C_COMMIT, path: ".claude/window1_live_v4_replay/v52c_full_post_onset_read_20260812/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52C_COMMIT, ".claude/window1_live_v4_replay/v52c_full_post_onset_read_20260812/COHORT_SELECTION_RECEIPT.json") },
    { iteration: "V52D", commit: V52D_COMMIT, path: ".claude/window1_live_v4_replay/v52d_disagreement_referee_20260812/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52D_COMMIT, ".claude/window1_live_v4_replay/v52d_disagreement_referee_20260812/COHORT_SELECTION_RECEIPT.json") },
    ...((isV52f || isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ? [{ iteration: "V52E", commit: V52E_COMMIT, path: ".claude/window1_live_v4_replay/v52e_palantir_wiring_20260812/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52E_COMMIT, ".claude/window1_live_v4_replay/v52e_palantir_wiring_20260812/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...((isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ? [{ iteration: "V52F", commit: V52F_COMMIT, path: ".claude/window1_live_v4_replay/v52f_pair_entry_conservation_20260813/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52F_COMMIT, ".claude/window1_live_v4_replay/v52f_pair_entry_conservation_20260813/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...((isV52h || isV52DepthValidation || isV52CausalOnset) ? [{ iteration: "V52G", commit: V52G_COMMIT, path: ".claude/window1_live_v4_replay/v52g_joint_target_conservation_20260813/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52G_COMMIT, ".claude/window1_live_v4_replay/v52g_joint_target_conservation_20260813/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...((isV52DepthValidation || isV52CausalOnset) ? [{ iteration: "V52H", commit: V52H_COMMIT, path: ".claude/window1_live_v4_replay/v52h_remove_pair_lows_precondition_20260813/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52H_COMMIT, ".claude/window1_live_v4_replay/v52h_remove_pair_lows_precondition_20260813/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...((isV52j || isV52k || isV52CausalOnset) ? [{ iteration: "V52I", commit: V52I_COMMIT, path: ".claude/window1_live_v4_replay/v52i_depth_informed_level_selection_20260813/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52I_COMMIT, ".claude/window1_live_v4_replay/v52i_depth_informed_level_selection_20260813/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...((isV52k || isV52CausalOnset) ? [{ iteration: "V52J", commit: V52J_COMMIT, path: ".claude/window1_live_v4_replay/v52j_role_conditioned_level_selection_20260813/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52J_COMMIT, ".claude/window1_live_v4_replay/v52j_role_conditioned_level_selection_20260813/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...(isV52CausalOnset ? [{ iteration: "V52K", commit: V52K_COMMIT, path: ".claude/window1_live_v4_replay/v52k_library_backed_evidence_20260814/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52K_COMMIT, ".claude/window1_live_v4_replay/v52k_library_backed_evidence_20260814/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...(isV52MacroRecognition ? [{ iteration: "V52L", commit: V52L_COMMIT, path: ".claude/window1_live_v4_replay/v52l_causal_stability_onset_20260814/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52L_COMMIT, ".claude/window1_live_v4_replay/v52l_causal_stability_onset_20260814/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...((isV52n || isV52o || isV52Ripeness || isV52r) ? [{ iteration: "V52M", commit: V52M_COMMIT, path: ".claude/window1_live_v4_replay/v52m_macro_recognition_20260817/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52M_COMMIT, ".claude/window1_live_v4_replay/v52m_macro_recognition_20260817/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...((isV52o || isV52Ripeness || isV52r) ? [{ iteration: "V52N", commit: V52N_COMMIT, path: ".claude/window1_live_v4_replay/v52n_recognition_confidence_gates_20260817/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52N_COMMIT, ".claude/window1_live_v4_replay/v52n_recognition_confidence_gates_20260817/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...((isV52Ripeness || isV52r) ? [{ iteration: "V52O", commit: V52O_COMMIT, path: ".claude/window1_live_v4_replay/v52o_benchmarked_role_instrument_20260817/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52O_COMMIT, ".claude/window1_live_v4_replay/v52o_benchmarked_role_instrument_20260817/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...((isV52q || isV52r) ? [{ iteration: "V52P", commit: V52P_COMMIT, path: ".claude/window1_live_v4_replay/v52p_ripeness_gated_role_binding_20260817/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52P_COMMIT, ".claude/window1_live_v4_replay/v52p_ripeness_gated_role_binding_20260817/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...(isV52r ? [{ iteration: "V52Q", commit: V52Q_COMMIT, path: ".claude/window1_live_v4_replay/v52q_anchor_correction_20260818/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52Q_COMMIT, ".claude/window1_live_v4_replay/v52q_anchor_correction_20260818/COHORT_SELECTION_RECEIPT.json") }] : []),
  ] : null;
  const v54PinsSource = isV54 && stage === "pins5" ? arg("--pins-source", null) : null;
  const v53PreRegistrationPath = v54PinsSource ? path.resolve(v54PinsSource) : path.join(repo, isV54
    ? ".claude/window1_v53_04_preregistration_20260820/PRE_REGISTRATION.json"
    : isV5304
    ? (stage === "pins5" ? ".claude/window1_v53_03_preregistration_20260820/PRE_REGISTRATION.json" : ".claude/window1_v53_04_preregistration_20260820/PRE_REGISTRATION.json")
    : isV5303
      ? (stage === "pins5" ? ".claude/window1_v53_02_preregistration_20260820/PRE_REGISTRATION.json" : ".claude/window1_v53_03_preregistration_20260820/PRE_REGISTRATION.json")
    : isV5302 ? ".claude/window1_v53_02_preregistration_20260820/PRE_REGISTRATION.json"
      : ".claude/window1_v53_preregistration_20260819/PRE_REGISTRATION.json");
  const v52eCohort = isV52e && !isV52FullExam ? (isV53 ? (() => {
    ensure(fs.existsSync(v53PreRegistrationPath), `V53 pre-registration missing ${v53PreRegistrationPath}`);
    const receipt = JSON.parse(fs.readFileSync(v53PreRegistrationPath, "utf8"));
    if ((isV5303 || isV5304 || isV54) && stage === "pins5") {
      ensure(receipt.population?.standing_pins?.length === 5, `${isV54 ? "V54" : isV5304 ? "V53-04" : "V53-03"} pins smoke source must contain exactly five standing pins`);
      const pins = receipt.population.standing_pins;
      return {
        standing_pins: pins,
        fresh_25: [],
        combined_30: pins,
        pre_registration: {
          label: `${isV54 ? "V54" : isV5304 ? "V53_04" : "V53_03"}_PINS_SMOKE_POPULATION`,
          fresh_cohort_drawn: false,
          source_path: path.relative(repo, v53PreRegistrationPath).replaceAll("\\", "/"),
          source_label: receipt.label,
          standing_pins: pins,
        },
      };
    }
    if (isV54) {
      const pins = receipt.population?.standing_pins;
      ensure(pins?.length === 5, "V54 standing pins source must contain exactly five games");
      if (isV54CheckSet) {
        const deadSiblingCodes = ["26JUL19ARSMAR", "26JUL14TANHAV", "26JUL19MARCOL", "26JUL12DIEMON", "26JUL18ROCBUE", "26JUL18ITOKNU", "26JUL15RODINC"];
        const championCompleteCodes = ["26JUL12KUMTUR", "26JUL12POLKUH", "26JUL13SANDAN", "26JUL14FERZAN", "26JUL14PUTJEA"];
        const bindCode = (code, role) => {
          const matches = [...baseByEvent.values()].filter((base) => base.event_id.endsWith(code));
          ensure(matches.length === 1, `V54 check-set code ${code} bound to ${matches.length} events`);
          const base = matches[0];
          return { event_id: base.event_id, code, category: base.category, role };
        };
        const deadSiblings = deadSiblingCodes.map((code) => bindCode(code, "V53_04_EXAM_DEAD_SIBLING"));
        const championCompletes = championCompleteCodes.map((code) => bindCode(code, "V53_04_CHAMPION_COMPLETE_CONTROL"));
        const checkSet = [...deadSiblings, ...championCompletes];
        ensure(checkSet.length === 12 && new Set(checkSet.map((row) => row.event_id)).size === 12, "V54 check-set conservation failed");
        return {
          standing_pins: championCompletes,
          fresh_25: [],
          combined_30: checkSet,
          check_set_12: checkSet,
          pre_registration: {
            label: "V54_CHECK_SET_12_READING_ORDER",
            law: "F-V53-040_SMALL_FIRST_ITERATION_LAW",
            source_index_commit: "c37e88ec40aea28d7785a364afe11a64643baec0",
            aggregate_804_read_before_check_set: false,
            dead_sibling_games: deadSiblings,
            champion_complete_controls: championCompletes,
          },
        };
      }
      ensure(stage === "tune804", `V54 requires pins5, checkset12, or tune804 stage, got ${stage}`);
      const fixed804 = [...baseByEvent.values()].sort((a, b) => a.event_id.localeCompare(b.event_id)).map((base) => ({ event_id: base.event_id, code: base.event_id.split("-").at(-1), category: base.category, role: "L19A_FIXED_804_TUNE" }));
      ensure(fixed804.length === 804, `V54 fixed dev population changed ${fixed804.length}`);
      return {
        standing_pins: pins,
        fresh_25: [],
        combined_30: fixed804,
        fixed_804: fixed804,
        pre_registration: {
          label: "V54_L19A_FIXED_804_TUNE_POPULATION",
          law: "L19a",
          fresh_cohort_drawn: false,
          source_path: path.relative(repo, v53PreRegistrationPath).replaceAll("\\", "/"),
          standing_pins: pins,
        },
      };
    }
    ensure(receipt.population?.combined_30?.length === 30, "V53 pre-registration must contain exactly 30 games");
    ensure(receipt.population.standing_pins?.length === 5 && receipt.population.fresh_25?.length === 25, "V53 pre-registration 5+25 law failed");
    ensure(receipt.zero_overlap_with_prior_iterations === true, "V53 pre-registration overlap assertion failed");
    if (isV5304) ensure(receipt.label === "V53_04_STAGE1_PRE_REGISTRATION", `V53-04 pre-registration label mismatch ${receipt.label}`);
    if (isV5303) ensure(receipt.label === "V53_03_STAGE1_PRE_REGISTRATION", `V53-03 pre-registration label mismatch ${receipt.label}`);
    if (isV5302) ensure(receipt.label === "V53_02_STAGE1_PRE_REGISTRATION", `V53-02 pre-registration label mismatch ${receipt.label}`);
    return { ...receipt.population, pre_registration: receipt };
  })() : isV52r ? buildV52rCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52q ? buildV52qCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52p ? buildV52pCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52o ? buildV52oCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52n ? buildV52nCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52m ? buildV52mCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52l ? buildV52lCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52k ? buildV52kCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52j ? buildV52jCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52i ? buildV52iCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52h ? buildV52hCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52g ? buildV52gCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52f ? buildV52fCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : buildV52eCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts)) : null;
  if (isV52c) v52bCohort = v52cCohort; // compatibility alias for the shared receipt block only
  if (isV52d) v52bCohort = v52dCohort; // compatibility alias for the shared receipt block only
  if (isV52e && !isV52FullExam) v52bCohort = v52eCohort; // compatibility alias for the shared receipt block only
  const activeReadCohort = isV52FullExam ? null : isV52e ? v52eCohort : isV52d ? v52dCohort : isV52c ? v52cCohort : v52bCohort;
  const emitV53Stage1 = async () => {
    const iterationLabel = isV54 ? "V54_01" : isV5304 ? "V53_04" : isV5303 ? "V53_03" : isV5302 ? "V53_02" : "V53_01";
    const candidateName = isV54 ? "V54_PAIR_MODEL" : isV5304 ? "V53_04_RISER_ARMING_LAW" : isV5303 ? "V53_03_READ_LICENSED_BOUND" : isV5302 ? "V53_02_UNDERSTANDING_BOUNDS" : "V53_UNDERSTANDING_ORGAN";
    const isPinsSmoke = (isV5303 || isV5304 || isV54) && stage === "pins5";
    const expectedGames = isPinsSmoke ? 5 : isV54CheckSet ? 12 : 30;
    ensure(isPinsSmoke || stage === "cohort30" || (isV54 && ["checkset12", "tune804"].includes(stage)), `${iterationLabel} requires pins5${isV54 ? ", checkset12, or tune804" : " or cohort30"} stage, got ${stage}`);
    const baselineRun = machineRuns.get("V52L_FROZEN_BASELINE");
    const candidateRun = machineRuns.get(candidateName);
    const baselineFlow = buildV52FlowPackage(baselineRun, baseByEvent, v52TapePackBytes, v52OnsetReceiptBytes, expectedGames, `${iterationLabel}_${isPinsSmoke ? "PINS_SMOKE" : "STAGE1"}_V52L_COMPARATOR`);
    const candidateFlow = buildV52FlowPackage(candidateRun, baseByEvent, v52TapePackBytes, v52OnsetReceiptBytes, expectedGames, `${iterationLabel}_${isPinsSmoke ? "PINS_SMOKE_5_ONLY" : "STAGE1_FRESH_30_ONLY"}`);
    const postActions = candidateRun.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && ["PLACE_REST", "REPRICE_REST"].includes(row.kind));
    const commonAssertions = {
      no_pre_onset_inputs: postActions.filter((row) => !row.birth_license?.onset?.passed).map((row) => `${row.leg_identity}@${row.receipt}`),
      no_span_fraction_inputs: postActions.filter((row) => row.birth_license?.game_view?.provenance?.no_span_fraction_consumed !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
      no_static_depth_targets: postActions.filter((row) => row.birth_license?.game_view?.provenance?.no_static_depth_target_consumed !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
      complete_license_on_every_bid: postActions.filter((row) => !(row.birth_license?.game_view && row.birth_license?.plan?.licensed && row.birth_license?.level && row.birth_license?.pair_entry_conservation && row.birth_license?.joint_target_conservation)).map((row) => `${row.leg_identity}@${row.receipt}`),
      N9_advisory_only: postActions.filter((row) => row.birth_license?.level?.N9_role !== "ADVISORY_ONLY_NOT_TARGET_AUTHORITY").map((row) => `${row.leg_identity}@${row.receipt}`),
      WTA_CHALL_role_disabled: postActions.filter((row) => row.category === "WTA_CHALL" && Object.values(row.birth_license?.game_view?.legs ?? {}).some((view) => view.role?.value !== "UNRIPE")).map((row) => `${row.leg_identity}@${row.receipt}`),
    };
    const v53Assertions = isV54 ? {
      ...commonAssertions,
      post_onset_view_only: candidateFlow.trace.filter((row) => row.game_view?.provenance?.post_onset_only !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
      pair_polarity_type_invariant: candidateFlow.trace.filter((row) => {
        const p = row.v54_pair_model?.polarity;
        return !(p?.tag === "UNDECIDED"
          ? p.strengthening_leg_id === null && p.fading_leg_id === null
          : p?.tag === "DECIDED" && p.strengthening_leg_id && p.fading_leg_id && p.strengthening_leg_id !== p.fading_leg_id);
      }).map((row) => `${row.leg_identity}@${row.receipt}`),
      no_same_label_pair_representable: candidateFlow.trace.filter((row) => row.v54_pair_model?.polarity?.tag === "DECIDED" && row.v54_pair_model.polarity.strengthening_leg_id === row.v54_pair_model.polarity.fading_leg_id).map((row) => `${row.leg_identity}@${row.receipt}`),
      joint_license_complete_coherent_and_readable_on_every_bid: postActions.filter((row) => {
        const license = row.birth_license?.joint_license, split = license?.budget_split;
        return !(license?.law === "L23_PAIR_UNIT_PROOF" && license.complete === true && typeof license.sentence === "string" && license.sentence.trim().length > 0 && license.sentence_action_assertion?.equal === true && split && Number.isInteger(split.sum_cents) && split.sum_cents <= 99);
      }).map((row) => `${row.leg_identity}@${row.receipt}`),
      sentence_action_equal_on_every_written_license: candidateFlow.trace.filter((row) => typeof row.joint_license?.sentence === "string" && row.joint_license.sentence_action_assertion?.equal !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
      fading_path_byte_equal_to_lineage: candidateFlow.trace.filter((row) => row.v54_pair_model?.reason !== "V54_FORMATION_NOT_SETTLED_NO_POST" && row.v54_pair_model?.window === "LATE" && row.v54_pair_model?.polarity?.tag === "DECIDED" && row.leg_identity.endsWith(`|${row.v54_pair_model.polarity.fading_leg_id}`) && (row.final_action !== row.lineage_decision?.action || row.final_target_cents !== row.lineage_target_cents)).map((row) => `${row.leg_identity}@${row.receipt}`),
      undecided_path_byte_equal_to_lineage: candidateFlow.trace.filter((row) => row.v54_pair_model?.reason !== "V54_FORMATION_NOT_SETTLED_NO_POST" && row.v54_pair_model?.polarity?.tag === "UNDECIDED" && (row.final_action !== row.lineage_decision?.action || row.final_target_cents !== row.lineage_target_cents)).map((row) => `${row.leg_identity}@${row.receipt}`),
      preformation_gate_only_nulls_lineage: candidateFlow.trace.filter((row) => row.v54_pair_model?.reason === "V54_FORMATION_NOT_SETTLED_NO_POST" && (!["HOLD_REST", "CANCEL_REST"].includes(row.final_action) || row.final_target_cents !== null)).map((row) => `${row.leg_identity}@${row.receipt}`),
      conservation_inputs_byte_equal: candidateFlow.trace.filter((row) => row.conservation_input_identity?.byte_equal !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
      no_pre_formation_anchor_consumption: postActions.filter((row) => {
        const own = row.birth_license?.game_view?.legs?.[row.leg_identity.split("|").at(-1)];
        return Number.isFinite(own?.l16_formation_anchor?.formation_end_epoch) && row.timestamp_epoch < own.l16_formation_anchor.formation_end_epoch;
      }).map((row) => `${row.leg_identity}@${row.receipt}`),
      l16_anchor_provenance_on_strengthening_bids: postActions.filter((row) => row.birth_license?.level?.v54_pair_model?.applied === true && row.birth_license?.game_view?.provenance?.formation_anchor?.law !== "L16").map((row) => `${row.leg_identity}@${row.receipt}`),
      joint_target_at_or_below_99_per_receipt: candidateFlow.trace.filter((row) => Number.isInteger(row.final_target_cents) && Number.isInteger(row.joint_target_conservation?.counterpart_cents) && row.final_target_cents + row.joint_target_conservation.counterpart_cents > 99).map((row) => `${row.leg_identity}@${row.receipt}:${row.final_target_cents}+${row.joint_target_conservation.counterpart_cents}`),
    } : isV5304 ? {
      ...commonAssertions,
      post_onset_view_only: candidateFlow.trace.filter((row) => row.game_view?.provenance?.post_onset_only !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
      joint_license_complete_on_every_bid: postActions.filter((row) => !(row.birth_license?.joint_license?.law === "L23_PAIR_UNIT_PROOF" && row.birth_license.joint_license.complete === true && row.birth_license.joint_license.both_states && row.birth_license.joint_license.both_stances && row.birth_license.joint_license.budget_split)).map((row) => `${row.leg_identity}@${row.receipt}`),
      arming_law_provenance_on_every_bid: postActions.filter((row) => !(row.birth_license?.joint_license?.arming_law?.id === v5304ArmingLaw.id && row.birth_license.joint_license.arming_law.source_commit === v5304ArmingLaw.source_commit && row.birth_license.joint_license.arming_law.shape_offset_aim_consumed === false && row.birth_license.joint_license.arming_law.latchcal_consumed === false)).map((row) => `${row.leg_identity}@${row.receipt}`),
      faller_path_byte_equal_to_lineage: candidateFlow.trace.filter((row) => row.v53_riser_arming?.stance?.value === "LATE_FLOOR_SIDE" && (row.final_action !== row.lineage_decision?.action || row.final_target_cents !== row.lineage_target_cents)).map((row) => `${row.leg_identity}@${row.receipt}`),
      absent_classification_silence_to_lineage: candidateFlow.trace.filter((row) => row.v53_riser_arming?.stance?.value === "CLASSIFICATION_ABSENT" && (row.final_action !== row.lineage_decision?.action || row.final_target_cents !== row.lineage_target_cents)).map((row) => `${row.leg_identity}@${row.receipt}`),
      early_floor_never_posts_before_selected_arming_law: v5304ArmingLaw.id === "A0_CONTROL_PROXY_SECOND_VISIT" ? [] : candidateFlow.trace.filter((row) => row.v53_riser_arming?.stance?.value === "EARLY_FLOOR_SIDE" && row.v53_riser_arming.stance.armed !== true && ["PLACE_REST", "REPRICE_REST"].includes(row.final_action)).map((row) => `${row.leg_identity}@${row.receipt}`),
      A0_control_decisions_byte_equal_to_lineage: v5304ArmingLaw.id !== "A0_CONTROL_PROXY_SECOND_VISIT" ? [] : candidateFlow.trace.filter((row) => row.final_action !== row.lineage_decision?.action || row.final_target_cents !== row.lineage_target_cents).map((row) => `${row.leg_identity}@${row.receipt}`),
      conservation_inputs_byte_equal: candidateFlow.trace.filter((row) => row.conservation_input_identity?.byte_equal !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
      no_shape_offset_or_latchcal: candidateFlow.trace.filter((row) => row.v53_riser_arming?.stance?.arming_law && (row.v53_riser_arming.stance.arming_law.shape_offset_aim_consumed !== false || row.v53_riser_arming.stance.arming_law.latchcal_consumed !== false)).map((row) => `${row.leg_identity}@${row.receipt}`),
      joint_target_at_or_below_99_per_receipt: candidateFlow.trace.filter((row) => Number.isInteger(row.final_target_cents) && Number.isInteger(row.joint_target_conservation?.counterpart_cents) && row.final_target_cents + row.joint_target_conservation.counterpart_cents > 99).map((row) => `${row.leg_identity}@${row.receipt}:${row.final_target_cents}+${row.joint_target_conservation.counterpart_cents}`),
    } : isV5303 ? {
      ...commonAssertions,
      post_onset_view_only: candidateFlow.trace.filter((row) => row.game_view?.provenance?.post_onset_only !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
      read_bound_receipt_present: candidateFlow.trace.filter((row) => !row.v53_read_licensed_bound).map((row) => `${row.leg_identity}@${row.receipt}`),
      non_settled_or_unripe_target_byte_equal: candidateFlow.trace.filter((row) => row.v53_read_licensed_bound?.authorized !== true && Number.isInteger(row.final_target_cents) && Number.isInteger(row.lineage_target_cents) && row.final_target_cents !== row.lineage_target_cents).map((row) => `${row.leg_identity}@${row.receipt}:${row.lineage_target_cents}->${row.final_target_cents}`),
      lift_only_on_settled_ripe: candidateFlow.trace.filter((row) => Number.isInteger(row.final_target_cents) && Number.isInteger(row.lineage_target_cents) && row.final_target_cents > row.lineage_target_cents && !(row.v53_read_licensed_bound?.applied === true && row.v53_read_licensed_bound?.quote_path?.state === "SETTLED" && row.v53_read_licensed_bound?.quote_path?.ripe === true && row.v53_read_licensed_bound?.pressure?.state === "SETTLED" && row.v53_read_licensed_bound?.pressure?.ripe === true)).map((row) => `${row.leg_identity}@${row.receipt}:${row.lineage_target_cents}->${row.final_target_cents}`),
      never_below_lineage: candidateFlow.trace.filter((row) => Number.isInteger(row.final_target_cents) && Number.isInteger(row.lineage_target_cents) && row.final_target_cents < row.lineage_target_cents).map((row) => `${row.leg_identity}@${row.receipt}:${row.lineage_target_cents}->${row.final_target_cents}`),
      conservation_inputs_byte_equal: candidateFlow.trace.filter((row) => Number.isInteger(row.lineage_target_cents) && row.conservation_input_identity?.byte_equal !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
      applied_bound_license_complete: candidateFlow.trace.filter((row) => row.v53_read_licensed_bound?.applied === true && !(row.v53_read_licensed_bound?.license_complete === true && row.v53_read_licensed_bound?.running_session_low_receipt && row.v53_read_licensed_bound?.quote_path?.evidence && row.v53_read_licensed_bound?.evaluation_receipt)).map((row) => `${row.leg_identity}@${row.receipt}`),
      lineage_target_present_for_every_licensed_target: candidateFlow.trace.filter((row) => Number.isInteger(row.final_target_cents) && !Number.isInteger(row.lineage_target_cents)).map((row) => `${row.leg_identity}@${row.receipt}`),
      joint_target_at_or_below_99_per_receipt: candidateFlow.trace.filter((row) => Number.isInteger(row.final_target_cents) && Number.isInteger(row.joint_target_conservation?.counterpart_cents) && row.final_target_cents + row.joint_target_conservation.counterpart_cents > 99).map((row) => `${row.leg_identity}@${row.receipt}:${row.final_target_cents}+${row.joint_target_conservation.counterpart_cents}`),
      budget_owner_overlay_deleted: candidateFlow.trace.filter((row) => row.plan?.delta_goal_deleted !== true || row.plan?.pair_budget_derivation_deleted !== true || row.plan?.owner_allowance_deleted !== true || row.plan?.allocation_overlay_deleted !== true || Object.hasOwn(row.plan ?? {}, "delta_goal_cents") || Object.hasOwn(row.plan ?? {}, "pair_budget_cents") || Object.hasOwn(row.plan ?? {}, "owner_leg_id") || Object.hasOwn(row.plan ?? {}, "allocation")).map((row) => `${row.leg_identity}@${row.receipt}`),
    } : isV5302 ? {
      ...commonAssertions,
      post_onset_view_only: candidateFlow.trace.filter((row) => row.game_view?.provenance?.post_onset_only !== true).map((row) => `${row.leg_identity}@${row.receipt}`),
      monotone_receipt_present: candidateFlow.trace.filter((row) => !row.v53_monotone_lift).map((row) => `${row.leg_identity}@${row.receipt}`),
      monotone_lift_invariant: candidateFlow.trace.filter((row) => row.v53_monotone_lift?.applicable && (row.v53_monotone_lift.passed !== true || row.final_target_cents < row.lineage_target_cents)).map((row) => `${row.leg_identity}@${row.receipt}:${row.lineage_target_cents}->${row.final_target_cents}`),
      lineage_target_present_for_every_licensed_target: candidateFlow.trace.filter((row) => Number.isInteger(row.final_target_cents) && !Number.isInteger(row.lineage_target_cents)).map((row) => `${row.leg_identity}@${row.receipt}`),
      joint_target_at_or_below_99_per_receipt: candidateFlow.trace.filter((row) => Number.isInteger(row.final_target_cents) && Number.isInteger(row.joint_target_conservation?.counterpart_cents) && row.final_target_cents + row.joint_target_conservation.counterpart_cents > 99).map((row) => `${row.leg_identity}@${row.receipt}:${row.final_target_cents}+${row.joint_target_conservation.counterpart_cents}`),
      pair_running_session_low_incomplete_gate_absent: candidateFlow.trace.filter((row) => JSON.stringify(row.plan ?? {}).includes("PAIR_RUNNING_SESSION_LOW_INCOMPLETE") || row.blocked_clause === "PAIR_RUNNING_SESSION_LOW_INCOMPLETE").map((row) => `${row.leg_identity}@${row.receipt}`),
    } : {
      ...commonAssertions,
      joint_plan_within_par: postActions.filter((row) => !(Number.isInteger(row.birth_license?.plan?.target_sum_cents) && row.birth_license.plan.target_sum_cents <= 99)).map((row) => `${row.leg_identity}@${row.receipt}`),
    };
    const assertionPass = Object.values(v53Assertions).every((rows) => rows.length === 0) && candidateFlow.pass;
    ensure(assertionPass, `V53 build assertion failed ${JSON.stringify(v53Assertions)}`);
    const summarize = (run) => {
      const rows = run.marketEvents.slice().sort((a, b) => a.event_id.localeCompare(b.event_id));
      const completed = rows.filter((event) => event.completed_pair);
      const valid = completed.filter((event) => event.pair_under_par);
      const deltas = valid.map((event) => 100 - event.combined_entry_cents);
      return {
        games: rows.length,
        completed_pairs: completed.length,
        under_par_pairs: valid.length,
        locked_cents: deltas.reduce((sum, value) => sum + value, 0),
        average_locked_delta_cents: deltas.length ? deltas.reduce((sum, value) => sum + value, 0) / deltas.length : null,
        completed_event_ids: completed.map((event) => event.event_id),
        rows,
      };
    };
    const baselineScore = summarize(baselineRun), candidateScore = summarize(candidateRun);
    if (isV54CheckSet) {
      const actionsFor = (run, eventId) => run.actions
        .filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && row.event_id === eventId && ["PLACE_REST", "REPRICE_REST", "CANCEL_REST", "PAIR_CAP_REPRICE", "FILL"].includes(row.kind))
        .sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
      const honestLine = (event) => ({
        verdict: event.completed_pair && event.pair_under_par ? "COMPLETE_UNDER_PAR_VALID" : event.completed_pair ? "COMPLETE_AT_OR_ABOVE_PAR_DEFECT" : Object.values(event.legs).some((leg) => leg.credited) ? "PARTIAL_ONE_LEG_ONLY" : "NEITHER_NO_VALID_COMPLETION",
        completed_pair: event.completed_pair,
        combined_entry_cents: event.combined_entry_cents,
        delta_vs_100_cents: event.completed_pair ? 100 - event.combined_entry_cents : null,
        legs: Object.values(event.legs).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)).map((leg) => ({ leg_identity: leg.leg_identity, credited: leg.credited, entry_cents: leg.entry_cents, fill_timestamp_epoch: leg.fill_timestamp_epoch, fill_class: leg.fill_class, terminal_reason: leg.terminal_reason })),
      });
      const receiptLine = (row) => `${row.timestamp_epoch} | ${row.t_minus_scheduled_seconds ?? "NA"} | ${row.t_minus_actual_bell_seconds ?? "NA"} | ${row.leg_identity} | ${row.kind} | ${row.target_cents ?? row.entry_cents ?? "NA"} | ${row.reason ?? row.fill_class ?? ""}`;
      const sections = [];
      for (const selected of activeReadCohort.check_set_12) {
        const baselineEvent = baselineScore.rows.find((event) => event.event_id === selected.event_id);
        const candidateEvent = candidateScore.rows.find((event) => event.event_id === selected.event_id);
        ensure(baselineEvent && candidateEvent, `V54 check-set event absent ${selected.event_id}`);
        const traceRows = candidateFlow.trace.filter((row) => row.event_id === selected.event_id);
        const sentenceSpans = v54LicenseSpans(traceRows).filter((span) => typeof span.representative_sentence === "string" && span.representative_sentence.length > 0);
        const candidateActions = actionsFor(candidateRun, selected.event_id), baselineActions = actionsFor(baselineRun, selected.event_id);
        const candidateHonest = honestLine(candidateEvent), baselineHonest = honestLine(baselineEvent);
        sections.push(`## ${selected.code} — ${selected.role}\n\n### Pair-model written licenses\n\n${sentenceSpans.length ? sentenceSpans.map((span) => `- ${span.first_timestamp_epoch}..${span.last_timestamp_epoch} (${span.receipt_count} receipts; scheduled ${span.first_t_minus_scheduled_seconds}..${span.last_t_minus_scheduled_seconds}; bell ${span.first_t_minus_actual_bell_seconds}..${span.last_t_minus_actual_bell_seconds}): ${span.representative_sentence}`).join("\n") : "- No written pair-model sentence was licensed."}\n\n### V54 bids, cancels, and fills\n\n\`epoch | T−scheduled s | T−bell s | leg | event | level c | reason\`\n\n${candidateActions.length ? candidateActions.map(receiptLine).join("\n") : "NO_ACTION"}\n\n### Champion bids, cancels, and fills\n\n\`epoch | T−scheduled s | T−bell s | leg | event | level c | reason\`\n\n${baselineActions.length ? baselineActions.map(receiptLine).join("\n") : "NO_ACTION"}\n\n### Honest ruler side-by-side\n\n| ruler | verdict | completed | pair cents | delta vs 100 | leg details |\n|---|---:|---:|---:|---:|---|\n| V54 | ${candidateHonest.verdict} | ${candidateHonest.completed_pair} | ${candidateHonest.combined_entry_cents ?? "NA"} | ${candidateHonest.delta_vs_100_cents ?? "NA"} | ${JSON.stringify(candidateHonest.legs)} |\n| Champion | ${baselineHonest.verdict} | ${baselineHonest.completed_pair} | ${baselineHonest.combined_entry_cents ?? "NA"} | ${baselineHonest.delta_vs_100_cents ?? "NA"} | ${JSON.stringify(baselineHonest.legs)} |`);
      }
      write("CHECK_SET_12.md", `# V54 iteration-01 check set — read before aggregate\n\nReading-order law: this artifact precedes any V54 iteration-01 aggregate score. Source index: c37e88ec40aea28d7785a364afe11a64643baec0. Honest ruler (V54r rule 1): only credited legs count; a valid completed game requires two credited legs and combined entries strictly below 100. Seven dead-sibling games and five champion-complete controls are conserved below.\n\n${sections.join("\n\n")}\n`);
      write("CHECK_SET_BINDING.json", canonical({ law: "F-V53-040_SMALL_FIRST_ITERATION_LAW", index_commit: "c37e88ec40aea28d7785a364afe11a64643baec0", expected_games: 12, observed_games: candidateScore.games, dead_sibling_games: activeReadCohort.check_set_12.filter((row) => row.role === "V53_04_EXAM_DEAD_SIBLING"), champion_complete_controls: activeReadCohort.check_set_12.filter((row) => row.role === "V53_04_CHAMPION_COMPLETE_CONTROL"), aggregate_804_read_or_reported_before_receipt: false, pass: candidateScore.games === 12 }));
      await writeGzipRowsFile(path.join(output, "V54_CHECK_SET_TRACE_12.jsonl.gz"), candidateFlow.trace, 9);
      await writeGzipRowsFile(path.join(output, "CHAMPION_CHECK_SET_TRACE_12.jsonl.gz"), baselineFlow.trace, 9);
      write("FORBIDDEN_ACCESS_RECEIPT.json", canonical({ full_804_score_computed_in_this_lane: false, sealed: false, holdout: false, live: false, network_runtime: false, orders: false, positions: false, deployment: false }));
      let determinism;
      const names = fs.readdirSync(output).sort();
      if (compare) {
        const mismatches = names.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
        ensure(!mismatches.length, `V54 check-set determinism mismatch ${mismatches.join(",")}`);
        determinism = { clean_builds: 2, compared_files: names.length, byte_identical: true, mismatches: [] };
      } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
      write("DETERMINISM_RECEIPT.json", canonical(determinism));
      writeManifest(output);
      if (compare) { fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism)); writeManifest(compare); ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "V54 check-set final manifests differ"); }
      process.stdout.write(canonical({ output, check_set_games: 12, artifact: "CHECK_SET_12.md", determinism }));
      return;
    }
    const offerPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/POST_ONSET_OFFER_CENSUS.json";
    const closePath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/INDEPENDENT_CLOSE_AUDIT_1608.csv";
    const offerBytes = gitShow(OFFER_DENOMINATOR_COMMIT, offerPath), offerSource = JSON.parse(offerBytes);
    const closeBytes = gitShow(FULL_BOOK_PNL_COMMIT, closePath), closeParsed = parseCsv(closeBytes.toString("utf8"));
    const closeIx = Object.fromEntries(closeParsed.header.map((value, index) => [value, index]));
    const closeByTicker = new Map(closeParsed.rows.map((row) => [row[closeIx.ticker], Number.parseInt(row[closeIx.audited_close_cents], 10)]));
    const offerByCode = new Map(offerSource.rows.map((row) => [row.code, row]));
    const f24Scoreboard = (scoreRows) => {
      const gameRows = scoreRows.rows.map((event) => {
        const offer = offerByCode.get(v52ShortEvent(event.event_id)) ?? null;
        const legs = Object.values(event.legs).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)).map((leg) => {
          const ownClose = closeByTicker.get(leg.ticker);
          return { leg_identity: leg.leg_identity, credited: leg.credited, entry_cents: leg.entry_cents, own_w1_close_cents: Number.isInteger(ownClose) ? ownClose : null, signed_entry_minus_own_w1_close_cents: leg.credited && Number.isInteger(ownClose) ? leg.entry_cents - ownClose : null };
        });
        return { event_id: event.event_id, offer_class: offer?.cls ?? "NOT_BOUND", offer_margin_cents: offer?.margin ?? null, completed_pair: event.completed_pair, combined_entry_cents: event.combined_entry_cents, signed_game_delta_vs_100_cents: event.completed_pair ? event.combined_entry_cents - 100 : null, legs };
      });
      const offered = gameRows.filter((row) => row.offer_class === "OFFERED_POST_ONSET");
      const rungs = [["GE_10_CENTS", 10], ["GE_5_CENTS", 5], ["THIN_1_TO_2_CENTS", 1]];
      return {
        games: gameRows.length,
        offered_games: offered.length,
        percent_of_offered_completed_under_par: offered.length ? 100 * offered.filter((row) => row.completed_pair && row.combined_entry_cents < 100).length / offered.length : null,
        margin_ladder: Object.fromEntries(rungs.map(([label, threshold]) => {
          const denominator = label === "THIN_1_TO_2_CENTS" ? offered.filter((row) => row.offer_margin_cents >= 1 && row.offer_margin_cents <= 2) : offered.filter((row) => row.offer_margin_cents >= threshold);
          const captured = denominator.filter((row) => row.completed_pair && row.combined_entry_cents < 100);
          return [label, { offered_games: denominator.length, completed_under_par: captured.length, percent_of_offered: denominator.length ? 100 * captured.length / denominator.length : null }];
        })),
        game_rows: gameRows,
      };
    };
    const f24 = {
      law: "F_V53_024_SCOREBOARD_LAW",
      offer_source: { commit: OFFER_DENOMINATOR_COMMIT, path: offerPath, sha256: shaBytes(offerBytes) },
      own_w1_close_source: { commit: FULL_BOOK_PNL_COMMIT, path: closePath, sha256: shaBytes(closeBytes) },
      comparator: f24Scoreboard(baselineScore),
      candidate: f24Scoreboard(candidateScore),
    };
    const baselineCompleteSet = new Set(baselineScore.completed_event_ids);
    const heldLineage = baselineScore.completed_event_ids.filter((id) => candidateScore.completed_event_ids.includes(id));
    const bar = {
      candidate_completes_strictly_more: candidateScore.completed_pairs > baselineScore.completed_pairs,
      every_lineage_complete_held_by_identity: heldLineage.length === baselineCompleteSet.size,
      candidate_average_locked_delta_at_least_lineage: Number.isFinite(candidateScore.average_locked_delta_cents) && Number.isFinite(baselineScore.average_locked_delta_cents) && candidateScore.average_locked_delta_cents >= baselineScore.average_locked_delta_cents,
      zero_build_assertion_violations: assertionPass,
    };
    bar.pass = Object.values(bar).every((value) => value === true);
    const pinsSmokeGate = {
      candidate_locked_cents_at_least_lineage: candidateScore.locked_cents >= baselineScore.locked_cents,
      zero_build_assertion_violations: assertionPass,
    };
    pinsSmokeGate.pass = Object.values(pinsSmokeGate).every((value) => value === true);
    const eventRows = candidateScore.rows.map((event) => {
      const baseline = baselineScore.rows.find((row) => row.event_id === event.event_id);
      const trace = candidateFlow.trace.filter((row) => row.event_id === event.event_id);
      const firstPost = trace.find((row) => ["PLACE_REST", "REPRICE_REST"].includes(row.final_action)) ?? null;
      const last = trace.at(-1) ?? null;
      return {
        event_id: event.event_id,
        category: event.category,
        L1_ADMISSION: { result: last?.onset?.passed ? "PASS" : "FLAG", why: last?.onset ?? null },
        L2_GAME_VIEW: { result: last?.game_view ? "PASS" : "FLAG", why: last?.game_view ?? null },
        L3_ROLE: { result: last?.game_view ? "PASS" : "FLAG", why: Object.fromEntries(Object.entries(last?.game_view?.legs ?? {}).map(([id, view]) => [id, view.role])) },
        L4_POSITION: { result: last?.game_view ? "PASS" : "FLAG", why: Object.fromEntries(Object.entries(last?.game_view?.legs ?? {}).map(([id, view]) => [id, view.leg_state])) },
        L5_PLAN: { result: last?.plan?.licensed ? "PASS" : "FLAG", why: last?.plan ?? null },
        L6_TARGET: { result: firstPost ? "PASS" : "FLAG", why: firstPost ? { receipt: firstPost.receipt, target_cents: firstPost.final_target_cents, license: firstPost.level } : { reason: last?.blocked_clause ?? "NO_LICENSED_POST" } },
        L7_CREDIT: { result: event.completed_pair ? "PASS" : "FLAG", why: Object.fromEntries(Object.values(event.legs).map((leg) => [leg.leg_identity, { credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, fill_receipt: leg.fill_source_state?.receipt ?? null }])) },
        L8_OUTCOME: { result: event.completed_pair && event.pair_under_par ? "PASS" : "FLAG", candidate: { completed: event.completed_pair, combined_entry_cents: event.combined_entry_cents, under_par: event.pair_under_par }, comparator: { completed: baseline.completed_pair, combined_entry_cents: baseline.combined_entry_cents, under_par: baseline.pair_under_par } },
      };
    });
    const pinIds = new Set(activeReadCohort.standing_pins.map((row) => row.event_id));
    const exemplarRows = candidateFlow.trace.filter((row) => pinIds.has(row.event_id));
    const preRegistration = activeReadCohort.pre_registration;
    const scorecard = {
      scope: `${iterationLabel}_${isPinsSmoke ? "PINS_SMOKE_5_ONLY" : "STAGE1_FRESH_30_ONLY"}`,
      full_804_run: false,
      ...(isV5304 ? { arming_law: v5304ArmingLaw } : {}),
      comparator: { ...baselineScore, rows: undefined },
      candidate: { ...candidateScore, rows: undefined },
      ...(isPinsSmoke ? { pins_smoke_gate: pinsSmokeGate } : { acceptance_bar: bar }),
      disposition: isPinsSmoke
        ? (pinsSmokeGate.pass ? "PINS_SMOKE_PASS_PREREGISTRATION_PERMITTED" : "PINS_SMOKE_FAILED_STOP_NO_FRESH25_NO_804")
        : (bar.pass ? "STAGE1_PASS_ELIGIBLE_FOR_SEPARATE_OPERATOR_804_AUTHORIZATION" : "STAGE1_FAILED_STOP_NO_804"),
    };
    write(isPinsSmoke ? "PINS_POPULATION_RECEIPT.json" : "PRE_REGISTRATION.json", canonical(preRegistration));
    write("STAGE1_BUILD_ASSERTIONS.json", canonical({ pass: assertionPass, assertions: v53Assertions, inherited_flow_assertions: candidateFlow.assertions }));
    write(isPinsSmoke ? "PINS_SMOKE_RECEIPT.json" : "STAGE1_SCORECARD.json", canonical(scorecard));
    write("F24_SCOREBOARD.json", canonical(f24));
    write(isPinsSmoke ? "PINS_SMOKE_DISPOSITION_RECEIPT.json" : "STAGE1_DISPOSITION_RECEIPT.json", canonical({ iteration: iterationLabel, pass: isPinsSmoke ? pinsSmokeGate.pass : bar.pass, disposition: scorecard.disposition, ...(isPinsSmoke ? { pins_smoke_gate: pinsSmokeGate, fresh_25_drawn: false } : { acceptance_bar: bar }), full_804_run: false }));
    write("PER_GAME_L1_L8.json", canonical({ rows: eventRows }));
    write("REPORT.md", `# ${iterationLabel.replace("_", "-")} ${isPinsSmoke ? "pins smoke" : "Stage-1"}\n\nScope: ${isPinsSmoke ? "five standing pins only; no fresh cohort was drawn" : "fresh 30 only"}; full-804 did not run.${isV5304 ? ` Arming law: ${v5304ArmingLaw.id}.` : ""}\n\nV52l comparator: ${baselineScore.completed_pairs} completes, ${baselineScore.locked_cents}c locked, ${baselineScore.average_locked_delta_cents}c average locked delta.\n\n${iterationLabel.replace("_", "-")}: ${candidateScore.completed_pairs} completes, ${candidateScore.locked_cents}c locked, ${candidateScore.average_locked_delta_cents}c average locked delta.\n\nGate: ${(isPinsSmoke ? pinsSmokeGate.pass : bar.pass) ? "PASS" : "FAIL"}. Disposition: ${scorecard.disposition}.\n`);
    write("FORBIDDEN_ACCESS_RECEIPT.json", canonical({ full_804: false, sealed: false, holdout: false, live: false, network_runtime: false, orders: false, positions: false, deployment: false }));
    await writeGzipRowsFile(path.join(output, `FULL_DECISION_TRACE_${expectedGames}.jsonl.gz`), candidateFlow.trace);
    await writeGzipRowsFile(path.join(output, `V52L_COMPARATOR_TRACE_${expectedGames}.jsonl.gz`), baselineFlow.trace);
    await writeGzipRowsFile(path.join(output, "FIVE_EXEMPLAR_DECISION_TRACES.jsonl.gz"), exemplarRows);
    const compactMarketRows = candidateScore.rows.map((event) => ({
      event_id: event.event_id,
      category: event.category,
      starting_price_split: event.starting_price_split,
      bell_confidence: event.bell_confidence,
      completed_pair: event.completed_pair,
      combined_entry_cents: event.combined_entry_cents,
      pair_under_par: event.pair_under_par,
      legs: Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, {
        leg_identity: leg.leg_identity,
        credited: leg.credited,
        entry_cents: leg.entry_cents,
        fill_class: leg.fill_class,
        action_timestamp_epoch: leg.action_timestamp_epoch,
        fill_timestamp_epoch: leg.fill_timestamp_epoch,
        terminal_reason: leg.terminal_reason,
        resting_target_at_edge_cents: leg.resting_target_at_edge_cents,
      }])),
    }));
    await writeGzipRowsFile(path.join(output, `MARKET_EVENT_LEDGER_${expectedGames}.jsonl.gz`), compactMarketRows);
    const names = fs.readdirSync(output).sort();
    let determinism;
    if (compare) {
      const mismatches = names.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
      ensure(!mismatches.length, `${iterationLabel} determinism mismatch ${mismatches.join(",")}`);
      determinism = { clean_builds: 2, compared_files: names.length, byte_identical: true, mismatches: [] };
    } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
    write("DETERMINISM_RECEIPT.json", canonical(determinism));
    writeManifest(output);
    if (compare) { fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism)); writeManifest(compare); ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), `${iterationLabel} final manifests differ`); }
    process.stdout.write(canonical({ output, scorecard, determinism }));
  };
  if (isV52ReadAuthority && !isV52FullExam) {
    const selected = new Set((v52hNamedOnly || v52jNamedOnly || v52kNamedOnly) ? [activeReadCohort.named_reused_observation.event_id] : activeReadCohort.combined_30.map((row) => row.event_id));
    for (const base of baseByEvent.values()) base.v52_flow_trace = selected.has(base.event_id);
  }
  const machineSpecs = isV54Tune804 ? [
    { name: "V54_PAIR_MODEL", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, v54_pair_model: true } },
  ] : isV53 ? [
    { name: "V52L_FROZEN_BASELINE", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true } },
    { name: isV54 ? "V54_PAIR_MODEL" : isV5304 ? "V53_04_RISER_ARMING_LAW" : isV5303 ? "V53_03_READ_LICENSED_BOUND" : isV5302 ? "V53_02_UNDERSTANDING_BOUNDS" : "V53_UNDERSTANDING_ORGAN", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, ...(isV54 ? { v54_pair_model: true } : isV5304 ? { v53_riser_arming_law: true } : isV5303 ? { v53_read_licensed_bound: true } : isV5302 ? { v53_understanding_bounds: true } : { v53_understanding_organ: true }) } },
  ] : isV52eExam ? [
    { name: "V52E_DISPOSITION_804", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true } },
  ] : isV52sExam ? [
    { name: "V52S_JOINT_BUDGET_YIELD_PRIORITY_DEPTH", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, joint_budget_yield_priority_depth: true } },
  ] : isV52r ? [
    { name: "V52L_FROZEN_BASELINE", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true } },
    { name: "V52R_ASSEMBLED_POLICY", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, assembled_policy: true, benchmarked_role_instrument: true, anchor_correction: true } },
  ] : isV52q ? [
    { name: "V52L_FROZEN_BASELINE", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true } },
    { name: "V52P_FROZEN_BASELINE", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, benchmarked_role_instrument: true, ripeness_role_binding: true } },
    { name: "V52Q_ANCHOR_CORRECTION", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, benchmarked_role_instrument: true, ripeness_role_binding: true, anchor_correction: true } },
  ] : isV52p ? [
    { name: "V52L_FROZEN_BASELINE", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true } },
    { name: "V52P_RIPENESS_GATED_ROLE_BINDING", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, benchmarked_role_instrument: true, ripeness_role_binding: true } },
  ] : isV52o ? [
    { name: "V52L_FROZEN_BASELINE", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true } },
    { name: "V52M_OBSERVATION_CONTROL", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, macro_recognition: true } },
    { name: "V52N_OBSERVATION_CONTROL", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, macro_recognition: true, recognition_confidence_gate: true } },
    { name: "V52O_BENCHMARKED_ROLE_INSTRUMENT", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, benchmarked_role_instrument: true } },
  ] : isV52n ? [
    { name: "V52L_FROZEN_BASELINE", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true } },
    { name: "V52M_FROZEN_BASELINE", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, macro_recognition: true } },
    { name: "V52N_RECOGNITION_CONFIDENCE_GATES", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, macro_recognition: true, recognition_confidence_gate: true } },
  ] : isV52m ? [
    { name: "V52L_FROZEN_BASELINE", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true } },
    { name: "V52M_MACRO_RECOGNITION", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, macro_recognition: true } },
  ] : isV52l ? [
    { name: "V52H_FROZEN_BASELINE", onset_mode: "FROZEN_FULL_SPAN_INTERIM", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true } },
    { name: "V52L_CAUSAL_STABILITY_ONSET", onset_mode: "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true } },
  ] : isV52k ? [
    { name: "V52H_FROZEN_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true } },
    { name: "V52K_LIBRARY_BACKED_EVIDENCE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, library_backed_level_evidence: true } },
  ] : isV52j ? [
    { name: "V52H_FROZEN_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true } },
    { name: "V52J_ROLE_CONDITIONED_LEVEL_SELECTION", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, role_conditioned_level_selection: true } },
  ] : isV52i ? [
    { name: "V52H_FROZEN_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true } },
    { name: "V52I_DEPTH_INFORMED_LEVEL_SELECTION", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, depth_informed_level_selection: true } },
  ] : isV52h ? [
    { name: "V52G_FROZEN_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true } },
    { name: "V52H_REMOVE_PAIR_LOWS_PRECONDITION", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true } },
  ] : isV52g ? [
    { name: "V52F_FROZEN_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true } },
    { name: "V52G_JOINT_TARGET_CONSERVATION", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true } },
  ] : isV52f ? [
    { name: "V52E_FROZEN_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true } },
    { name: "V52F_PAIR_ENTRY_CONSERVATION", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true } },
  ] : isV52e ? [
    { name: "V52D_FROZEN_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true } },
    { name: "V52E_PALANTIR_WIRING", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true } },
  ] : isV52d ? [
    { name: "V52C_FROZEN_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true } },
    { name: "V52D_DISAGREEMENT_REFEREE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true } },
  ] : isV52c ? [
    { name: "V52B_FROZEN_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true } },
    { name: "V52C_FULL_POST_ONSET_READ", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true } },
  ] : isV52b ? [
    { name: "V52_FROZEN_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false } },
    { name: "V52B_READ_LEVEL_AUTHORITY", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true } },
  ] : isV52 ? [
    { name: "TRADE_TRUTH_V47_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: false, judgment_gate: false, scavenger: false } },
    { name: "V49B_FAITHFUL_STAND_AT_P", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: false, scavenger: false } },
    { name: "V52_JUDGMENT_GATE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false } },
  ] : isV49b ? [
    { name: "TRADE_TRUTH_V47_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: false } },
    { name: "V49B_FAITHFUL_STAND_AT_P", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true } },
  ] : isV49 ? [
    { name: "TRADE_TRUTH_V47_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, evidenced_level_standing: false } },
    { name: "V49_EVIDENCED_LEVEL_STANDING", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: false, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, evidenced_level_standing: true } },
  ] : isV48 ? [
    { name: "V47_BASELINE", market_mode: "MARKET_UNION_REACH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: false, placement_ladder: "V47_INCUMBENT" } },
    { name: "TRADE_TRUTH_V47_INCUMBENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, placement_ladder: "V47_INCUMBENT" } },
    { name: "TRADE_TRUTH_BID_MINUS_ONE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, placement_ladder: "BID_MINUS_ONE" } },
    { name: "TRADE_TRUTH_BID", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, placement_ladder: "BID" } },
    { name: "TRADE_TRUTH_RECENT_TRADE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, placement_ladder: "LOWEST_RECENT_TRADED_LEVEL" } },
  ] : isV47 ? [
    { name: "V45_BASELINE", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: false } },
    { name: "V47_SAME_TICK_ARM", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true } },
  ] : isV46 ? [
    { name: "V45_BASELINE", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true } },
    { name: "V46_PAIR_GATED_GAP_CREDIT", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, pair_gated_gap_credit: true } },
  ] : isV45 ? [
    { name: "V43_BASELINE", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true } },
    { name: "V45_GUARD_RELEASE_AT_SIBLING_CREDIT", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true } },
  ] : isV43 ? [
    { name: "V41_BASELINE", clauses: {} },
    { name: "C1_ARM_ONLY", clauses: { arm_at_first_evidence: true } },
    { name: "C2_GUARD_ONLY", clauses: { deep_gap_guard: true } },
    { name: "C3_LOOSEN_ONLY", clauses: { loosen_one_cent: true } },
    { name: "C1_C2_ARM_GUARD", clauses: { arm_at_first_evidence: true, deep_gap_guard: true } },
    { name: "C1_C3_ARM_LOOSEN", clauses: { arm_at_first_evidence: true, loosen_one_cent: true } },
    { name: "C2_C3_GUARD_LOOSEN", clauses: { deep_gap_guard: true, loosen_one_cent: true } },
    { name: "V43_ALL_THREE", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true } },
  ] : [{ name: "PRIMARY", clauses: isV42 ? { deep_gap_guard: true } : {} }];
  const machineRuns = new Map(machineSpecs.map((spec) => [spec.name, { spec, marketEvents: [], strictEvents: [], actions: [], joinQualifications: [] }]));
  const printLoad = await loadPrints(tickerBounds), tapeHashes = {};
  const v52TapePackPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/game_tape_packs/MANIFEST.json";
  const v52OnsetReceiptPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/MERDRO_CLOSEOUT.json";
  const v52TapePackBytes = isV52 ? gitShow(FIVE_GAME_TAPE_PACK_COMMIT, v52TapePackPath) : null;
  const v52OnsetReceiptBytes = isV52 ? gitShow(STABILITY_ONSET_COMMIT, v52OnsetReceiptPath) : null;
  const examRoleStats = { role_receipt_rows: 0, missing_both_clock_fields: [], terminal_by_leg: new Map() };
  const examTraceNormalizer = (isV52rExam || isV52sExam) ? v52rExamAdapter.makeExamTraceNormalizer(examRoleStats) : isV52eExam ? makeLosslessTraceNormalizer() : null;
  const examTraceWriter = isV52sExam ? makeTraceChunkWriter(output, 1, null, "V52S_FULL_DECISION_TRACE_804_CHUNK", 1) : isV52rExam ? makeTraceChunkWriter(output, 1, null, "V52R_FULL_DECISION_TRACE_804_CHUNK") : isV52eExam ? makeTraceChunkWriter(output, 8, null) : null;
  const isV54Full = isV54Tune804;
  const v54StorySelection = isV54Full ? selectV54DecisionStories(baseByEvent, activeReadCohort.standing_pins, 30) : null;
  const v54StoryIds = new Set(v54StorySelection?.event_ids ?? []);
  const v54StoryRows = [];
  const v54AssertionFailures = {};
  const v54PairModelStats = { decision_receipts: 0, decided_receipts: 0, undecided_receipts: 0, strengthening_early_receipts: 0, fading_late_receipts: 0, early_cancels_on_down_pressure: 0, machine_written_sentences: 0, sentence_hashes: new Set() };
  const v54TraceWriter = isV54Full ? makeTraceChunkWriter(output, 1, null, "V54_FULL_PAIR_LICENSE_TRACE_804_CHUNK", 1) : null;
  const examTraceStats = { rows: 0, palantir_consumption_rows: 0, continuous_rows: 0, priors_gate_true_rows: 0, N2_rows: 0, N4_rows: 0, N5_rows: 0, N4_grid_rows: 0, N4_rescue_rows: 0, N5_adjudication_rows: 0, by_block_reason: {}, by_category_x_block_reason: {}, provenance_asset_ids: new Set() };
  if (isV52FullExam) { activeExamTraceNormalizer = examTraceNormalizer; activeExamTraceStats = examTraceStats; }
  const examSpanCloseRows = [];
  const rightEdgeIndependenceRows = [];
  let index = 0;
  const v52ReadEventIds = isV52ReadAuthority && !isV52FullExam ? new Set(activeReadCohort.combined_30.map((row) => row.event_id)) : null;
  if (v52hNamedOnly || v52jNamedOnly || v52kNamedOnly) { v52ReadEventIds.clear(); v52ReadEventIds.add(activeReadCohort.named_reused_observation.event_id); }
  const replayBases = [...baseByEvent.values()].filter((base) => !isV52 || (isV52FullExam ? true : isV52ReadAuthority ? v52ReadEventIds.has(base.event_id) : stage === "full" || v52ShortEvent(base.event_id))).sort((a, b) => a.event_id.localeCompare(b.event_id));
  for (const base of replayBases) {
    index += 1; if (index % 50 === 0) process.stderr.write(`${isV52 ? "V52x2" : isV49b ? "V49bx2" : isV49 ? "V49x2" : isV48 ? "V48x5" : isV47 ? "V47x2" : isV46 ? "V46x2" : isV45 ? "V45x2" : isV43 ? "V43x8" : isV42 ? "V42" : isV41 ? "V41" : isV40 ? "V40" : isV39 ? "V39" : "V38"} replay ${index}/${replayBases.length}\n`);
    const tapes = new Map(), prints = new Map();
    for (const [id, leg] of Object.entries(base.legs)) {
      const loaded = loadTape(leg.ticker); tapeHashes[leg.ticker] = { sha256: loaded.sha256, bytes: loaded.bytes };
      tapes.set(id, loaded.rows); prints.set(id, printLoad.byTicker.get(leg.ticker));
    }
    let frozenOnsets = null, causalOnsets = null;
    if (isV52) {
      frozenOnsets = onsetPolicy.computeEventOnsets(base, tapes, prints);
      if (isV52CausalOnset) {
        causalOnsets = causalOnsetPolicy.computeEventOnsets(base, tapes, prints);
        const independence = causalOnsetPolicy.assertRightEdgeIndependence(base, tapes, prints);
        if (isV52rExam || isV52sExam) {
          ensure(independence.pass === true, `${isV52sExam ? "V52s" : "V52r"} right-edge independence failed ${base.event_id}`);
          rightEdgeIndependenceRows.push({ event_id: base.event_id, pass: true });
        } else rightEdgeIndependenceRows.push(independence);
      } else for (const id of Object.keys(base.legs)) base.legs[id].v52_onset = frozenOnsets[id];
    }
    for (const spec of machineSpecs) {
      const marketMode = spec.market_mode || "MARKET_UNION_REACH";
      const specOnsets = isV52CausalOnset && spec.onset_mode === "CAUSAL_PREFIX_RIGHT_EDGE_INDEPENDENT" ? causalOnsets : frozenOnsets;
      const specBase = isV52CausalOnset ? { ...base, v52s_enabled: spec.clauses.joint_budget_yield_priority_depth === true, v52_onset_mode: spec.onset_mode, legs: Object.fromEntries(Object.entries(base.legs).map(([id, leg]) => [id, { ...leg, v52_onset: specOnsets[id] }])) } : base;
      // Strict-ruler decisions are scored but never exported as a second receipt diary.
      // Suppressing that duplicate trace is serializer/memory hygiene only.
      const collectExamTrace = isV52eExam || (isV52rExam && spec.name === "V52R_ASSEMBLED_POLICY") || (isV52sExam && spec.name === "V52S_JOINT_BUDGET_YIELD_PRIORITY_DEPTH");
      const collectV54Trace = isV54Full && spec.name === "V54_PAIR_MODEL";
      const marketBase = isV54Full
        ? { ...specBase, v52_flow_trace: false, v54_compact_trace: collectV54Trace }
        : (((isV52rExam || isV52sExam) && !collectExamTrace) ? { ...specBase, v52_flow_trace: false } : specBase);
      const strictBase = (isV52FullExam || isV52ReadAuthority) ? { ...specBase, v52_flow_trace: false } : specBase;
      const run = machineRuns.get(spec.name), market = simulate(marketBase, tapes, prints, marketMode, spec.clauses), strict = isV54Full ? null : simulate(strictBase, tapes, prints, "STRICT_PRINT_CROSS", spec.clauses);
      run.marketEvents.push((isV52rExam || isV52sExam) ? compactV52rExamEvent(market.event) : market.event);
      if (strict) run.strictEvents.push((isV52rExam || isV52sExam) ? compactV52rExamEvent(strict.event) : strict.event);
      if (collectV54Trace) {
        const licenseSpans = Object.values(market.event.legs)
          .flatMap((leg) => leg.v54_license_spans ?? [])
          .sort((a, b) => a.first_timestamp_epoch - b.first_timestamp_epoch || a.leg_identity.localeCompare(b.leg_identity) || String(a.first_receipt).localeCompare(String(b.first_receipt)));
        for (const leg of Object.values(market.event.legs)) mergeV54AssertionFailures(v54AssertionFailures, leg.v54_assertion_failures ?? {});
        for (const span of licenseSpans) {
          const count = span.receipt_count;
          const pairModel = span.semantic?.pair_model;
          v54PairModelStats.decision_receipts += count;
          if (pairModel?.polarity?.tag === "DECIDED") v54PairModelStats.decided_receipts += count;
          if (pairModel?.polarity?.tag === "UNDECIDED") v54PairModelStats.undecided_receipts += count;
          if (pairModel?.window === "EARLY") v54PairModelStats.strengthening_early_receipts += count;
          if (pairModel?.window === "LATE" && pairModel?.polarity?.tag === "DECIDED") v54PairModelStats.fading_late_receipts += count;
          if (span.semantic?.reason === "V54_STRENGTHENING_EARLY_BID_CANCELLED_ON_OWN_DOWN_PRESSURE") v54PairModelStats.early_cancels_on_down_pressure += count;
          const licenseSentence = span.representative_sentence;
          if (typeof licenseSentence === "string" && licenseSentence.length > 0) {
            v54PairModelStats.machine_written_sentences += count;
            v54PairModelStats.sentence_hashes.add(shaBytes(Buffer.from(licenseSentence)));
          }
        }
        await v54TraceWriter.append(base.event_id, licenseSpans);
        if (v54StoryIds.has(base.event_id)) v54StoryRows.push(...licenseSpans);
        for (const leg of Object.values(market.event.legs)) {
          leg.v54_license_spans = [];
          leg.v54_assertion_failures = {};
        }
      }
      if (isV52rExam || isV52sExam) {
        const candidateSpec = isV52sExam ? "V52S_JOINT_BUDGET_YIELD_PRIORITY_DEPTH" : "V52R_ASSEMBLED_POLICY";
        if (spec.name === candidateSpec) for (const row of market.actions) {
          if (!["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE", "GAP_CREDIT_REPRICE_DOWN", "V52S_DEPTH_LIFT", "V52S_YIELD_TO_SENIOR_DEFAULT", "V52S_DEFAULT_RESTORE"].includes(row.kind)) continue;
          run.actions.push({ machine: spec.name, mode: marketMode, event_id: row.event_id, leg_identity: row.leg_identity, kind: row.kind, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds, target_before_cents: row.target_before_cents ?? null, target_after_cents: row.target_after_cents ?? row.target_cents ?? null, default_target_cents: row.default_target_cents ?? null, running_post_onset_session_low_cents: row.running_post_onset_session_low_cents ?? null, slack_before_lifts_cents: row.slack_before_lifts_cents ?? null, slack_after_lifts_cents: row.slack_after_lifts_cents ?? null, joint_target_sum_cents: row.joint_target_sum_cents ?? null, invariant_pass: row.invariant_pass ?? null, cause: row.cause ?? null, birth_license: row.birth_license ? { read: row.birth_license.read ? { passed: row.birth_license.read.passed, state: row.birth_license.read.state, evidence: row.birth_license.read.evidence } : null } : null });
        }
      } else if (isV54Full) {
        if (spec.name === "V54_PAIR_MODEL") for (const row of market.actions) {
          if (!["PLACE_REST", "REPRICE_REST", "CANCEL_REST", "FILL"].includes(row.kind)) continue;
          run.actions.push({ machine: spec.name, mode: marketMode, event_id: row.event_id, leg_identity: row.leg_identity, category: row.category, kind: row.kind, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, target_cents: row.target_cents ?? row.entry_cents ?? null, reason: row.reason ?? row.fill_class ?? null });
        }
      } else {
        for (const row of market.joinQualifications) run.joinQualifications.push({ machine: spec.name, ...row });
        if (strict) for (const row of strict.joinQualifications) run.joinQualifications.push({ machine: spec.name, ...row });
        for (const row of market.actions) run.actions.push({ machine: spec.name, mode: marketMode, ...row });
        if (strict) for (const row of strict.actions) run.actions.push({ machine: spec.name, mode: "STRICT_PRINT_CROSS", ...row });
      }
      if (collectExamTrace) {
        const traceRows = Object.values(market.event.legs).flatMap((leg) => leg.judgment_trace_rows).sort((a, b) => a[5] - b[5] || a[1].localeCompare(b[1]) || a[9].localeCompare(b[9]));
        await examTraceWriter.append(base.event_id, traceRows);
        for (const [id, leg] of Object.entries(market.event.legs)) {
          const materialized = [...tapes.get(id), ...prints.get(id)].filter((row) => row.ts <= base.right).sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
          const finalReceipt = materialized.at(-1) ?? null;
          const finalDecision = traceRows.filter((row) => row[1] === leg.leg_identity).at(-1) ?? null;
          examSpanCloseRows.push({ event_id: base.event_id, leg_identity: leg.leg_identity, category: base.category, price_region: leg.price_region, window_left_epoch: base.left, window_right_epoch: base.right, final_materialized_receipt_consumed_timestamp_epoch: finalReceipt?.ts ?? null, final_materialized_receipt_consumed: finalReceipt?.receipt ?? null, materialized_span_to_edge_seconds: finalReceipt ? base.right - finalReceipt.ts : null, materialized_span_status: finalReceipt ? "FULL_AVAILABLE_SPAN_CONSUMED" : "NO_MATERIALIZED_RECEIPT_INSIDE_EDGE", final_decision_timestamp_epoch: finalDecision?.[5] ?? null, final_decision_receipt: finalDecision?.[9] ?? null, decision_trace_to_edge_seconds: finalDecision ? base.right - finalDecision[5] : null, credited: leg.credited, fill_timestamp_epoch: leg.fill_timestamp_epoch, terminal_reason: leg.terminal_reason, full_materialized_span_consumed: finalReceipt !== null, export_convention: "DECISION_ROWS_END_WHEN_ENTRY_TERMINATES; SPAN_CLOSE_ROW_RECORDS_FULL_AVAILABLE_MATERIALIZED_INPUT_OR_EXPLICIT_ABSENCE" });
          leg.judgment_trace_rows = [];
        }
        for (const leg of Object.values(strict.event.legs)) leg.judgment_trace_rows = [];
      }
    }
  }
  const examTraceChunks = isV52FullExam ? await examTraceWriter.finish() : null;
  const v54TraceChunks = isV54Full ? await v54TraceWriter.finish() : null;
  if (isV54Full) {
    const frozenBaselinePath = ".claude/window1_live_v4_replay/v52r_disposition_804_20260818/V52L_MARKET_EVENT_LEDGER_804.jsonl.gz";
    const frozenBaselineBytes = gitShow(v52sExamAdapter.PARENT_COMMIT, frozenBaselinePath);
    const frozenBaselineEvents = readRowsBytes(frozenBaselineBytes);
    ensure(frozenBaselineEvents.length === 804, `V54 frozen champion ledger conservation changed ${frozenBaselineEvents.length}`);
    // The frozen V52l ledger intentionally stores per-leg terminal facts only.
    // Restore its event-level score fields mechanically before applying score().
    for (const event of frozenBaselineEvents) {
      const legs = Object.values(event.legs);
      event.completed_pair = legs.every((leg) => leg.credited);
      event.combined_entry_cents = event.completed_pair ? legs.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
      event.pair_under_par = event.completed_pair && event.combined_entry_cents < 100;
    }
    machineRuns.set("V52L_FROZEN_BASELINE", { spec: { name: "V52L_FROZEN_BASELINE", role: "HASH_BOUND_PARENT_LEDGER_NO_DUPLICATE_REPLAY" }, marketEvents: frozenBaselineEvents, strictEvents: [], actions: [], joinQualifications: [], source: { commit: v52sExamAdapter.PARENT_COMMIT, path: frozenBaselinePath, sha256: shaBytes(frozenBaselineBytes), bytes: frozenBaselineBytes.length } });
  }
  if (isV52sExam) {
    const frozenBaselinePath = ".claude/window1_live_v4_replay/v52r_disposition_804_20260818/V52L_MARKET_EVENT_LEDGER_804.jsonl.gz";
    const frozenBaselineBytes = gitShow(v52sExamAdapter.PARENT_COMMIT, frozenBaselinePath);
    const frozenBaselineEvents = readRowsBytes(frozenBaselineBytes);
    ensure(frozenBaselineEvents.length === 804, `frozen V52l parent-ledger conservation changed ${frozenBaselineEvents.length}`);
    machineRuns.set("V52L_FROZEN_BASELINE", { spec: { name: "V52L_FROZEN_BASELINE", role: "HASH_BOUND_PARENT_LEDGER_NO_DUPLICATE_REPLAY" }, marketEvents: frozenBaselineEvents, strictEvents: [], actions: [], joinQualifications: [], source: { commit: v52sExamAdapter.PARENT_COMMIT, path: frozenBaselinePath, sha256: shaBytes(frozenBaselineBytes), bytes: frozenBaselineBytes.length } });
  }
  if (v52jNamedOnly || v52kNamedOnly) {
    const namedIteration = isV52k ? "V52K" : "V52J";
    const baselineRun = machineRuns.get("V52H_FROZEN_BASELINE"), candidateRun = machineRuns.get(isV52k ? "V52K_LIBRARY_BACKED_EVIDENCE" : "V52J_ROLE_CONDITIONED_LEVEL_SELECTION");
    const before = buildV52FlowPackage(baselineRun, baseByEvent, v52TapePackBytes, v52OnsetReceiptBytes, 1, "V52H_GUEGOM_NAMED_REPLAY");
    const after = buildV52FlowPackage(candidateRun, baseByEvent, v52TapePackBytes, v52OnsetReceiptBytes, 1, `${namedIteration}_GUEGOM_NAMED_REPLAY`);
    const baselineEvent = baselineRun.marketEvents[0], candidateEvent = candidateRun.marketEvents[0];
    ensure(baselineEvent?.event_id.includes("GUEGOM") && candidateEvent?.event_id === baselineEvent.event_id, "GUEGOM named replay identity mismatch");
    const base = baseByEvent.get(candidateEvent.event_id);
    const offerCensus = JSON.parse(gitShow("22441e05", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/POST_ONSET_OFFER_CENSUS.json"));
    const offerGame = offerCensus.rows.find((row) => row.code === "26JUL12GUEGOM");
    ensure(offerGame, "GUEGOM offer-floor row unavailable");
    const legs = Object.values(candidateEvent.legs).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)).map((leg) => {
      const baselineLeg = Object.values(baselineEvent.legs).find((row) => row.leg_identity === leg.leg_identity);
      const legId = leg.leg_identity.split("|").at(-1);
      const offer = offerGame.legs?.[legId] ?? Object.values(offerGame.legs ?? {}).find((row) => row.ticker?.endsWith(`-${legId}`)) ?? null;
      const traceRows = after.trace.filter((row) => row.leg_identity === leg.leg_identity && (!Number.isFinite(leg.fill_timestamp_epoch) || row.timestamp_epoch <= leg.fill_timestamp_epoch));
      const roleRow = traceRows.filter((row) => row.role_conditioned_level_selection?.role_assignment).at(-1) ?? null;
      const libraryRow = traceRows.filter((row) => row.library_backed_level_evidence).at(-1) ?? null;
      return {
        leg_identity: leg.leg_identity,
        role_at_fill_or_terminal: roleRow?.role_conditioned_level_selection?.role_assignment?.own_role ?? null,
        role_receipt: roleRow?.receipt ?? null,
        library_evidence_authority_at_fill_or_terminal: libraryRow?.library_backed_level_evidence?.evidence_authority ?? null,
        library_supported_floor_cents: libraryRow?.library_backed_level_evidence?.library_supported_floor_cents ?? null,
        library_receipt: libraryRow?.receipt ?? null,
        baseline: { credited: baselineLeg.credited, entry_cents: baselineLeg.entry_cents, fill_timestamp_epoch: baselineLeg.fill_timestamp_epoch, fill_clock: Number.isFinite(baselineLeg.fill_timestamp_epoch) ? clockFields(baselineLeg.fill_timestamp_epoch, base) : null },
        candidate: { credited: leg.credited, entry_cents: leg.entry_cents, fill_timestamp_epoch: leg.fill_timestamp_epoch, fill_clock: Number.isFinite(leg.fill_timestamp_epoch) ? clockFields(leg.fill_timestamp_epoch, base) : null },
        post_onset_offer_floor_cents: offer?.floor_sel ?? null,
        candidate_entry_minus_floor_cents: leg.credited && Number.isInteger(offer?.floor_sel) ? leg.entry_cents - offer.floor_sel : null,
        fill_delay_seconds: leg.credited && Number.isFinite(baselineLeg.fill_timestamp_epoch) ? leg.fill_timestamp_epoch - baselineLeg.fill_timestamp_epoch : null,
      };
    });
    const fallerRows = legs.filter((row) => row.role_at_fill_or_terminal === "FALLING");
    const observation = {
      event_id: candidateEvent.event_id,
      provenance: activeReadCohort.named_reused_observation,
      baseline: { completed: baselineEvent.completed_pair, combined_entry_cents: baselineEvent.combined_entry_cents, pair_under_par: baselineEvent.pair_under_par },
      candidate: { completed: candidateEvent.completed_pair, combined_entry_cents: candidateEvent.combined_entry_cents, pair_under_par: candidateEvent.pair_under_par },
      legs,
      pre_stated_GUEGOM_class_claim: {
        faller_side_identified: fallerRows.length > 0,
        all_candidate_faller_fills_later_than_baseline: fallerRows.length > 0 && fallerRows.every((row) => Number.isFinite(row.fill_delay_seconds) && row.fill_delay_seconds >= 0),
        all_candidate_faller_fills_at_or_near_later_floor_0_to_1c: fallerRows.length > 0 && fallerRows.every((row) => Number.isInteger(row.candidate_entry_minus_floor_cents) && row.candidate_entry_minus_floor_cents >= 0 && row.candidate_entry_minus_floor_cents <= 1),
        converts: !baselineEvent.completed_pair && candidateEvent.completed_pair,
        adjudication: "OBSERVATION_ONLY; FAILURE DOES_NOT_AUTHORIZE_POLICY_EDIT",
      },
    };
    write("REPORT.md", `# ${namedIteration} GUEGOM named observation\n\nGUEGOM is explicitly reused outside ${namedIteration}'s fresh 25. Baseline ${JSON.stringify(observation.baseline)}; candidate ${JSON.stringify(observation.candidate)}. Named observation ${JSON.stringify(observation.pre_stated_GUEGOM_class_claim)}. No behavioral edit followed this observation.\n`);
    write("CONTROL_BINDING.json", canonical({ parent_commit: isV52k ? V52J_COMMIT : V52I_COMMIT, controlling_policy_base_commit: V52H_COMMIT, branch: isV52k ? "codex/window1-v52k-library-backed-evidence-20260814" : "codex/window1-v52j-role-conditioned-level-selection-20260813", scope: "GUEGOM_NAMED_OBSERVATION_OUTSIDE_COHORT30", score_or_disposition_804_run: false, policy_edits: false }));
    write("GUEGOM_NAMED_OBSERVATION.json", canonical(observation));
    write("FORBIDDEN_ACCESS_RECEIPT.json", canonical({ holdout: false, live: false, network_runtime: false, orders: false, positions: false, deployment: false, full_804_run: false, scavenger: false }));
    const namedTraceRows = before.trace.map((row) => ({ variant: "V52H", ...row })).concat(after.trace.map((row) => ({ variant: namedIteration, ...row })));
    const namedTraceChunks = [];
    for (let start = 0; start < namedTraceRows.length; start += 10000) {
      const rows = namedTraceRows.slice(start, start + 10000);
      const name = `GUEGOM_NAMED_BEFORE_AFTER_TRACE_CHUNK_${String(namedTraceChunks.length + 1).padStart(3, "0")}.jsonl.gz`;
      await writeGzipRowsFile(path.join(output, name), rows);
      namedTraceChunks.push({ name, rows: rows.length, sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size });
    }
    write("GUEGOM_NAMED_BEFORE_AFTER_TRACE_MANIFEST.json", canonical({ format: "FULL_RECEIPT_GRAIN_JSONL_GZIP_ROW_CHUNKS", chunk_row_limit: 10000, rows: namedTraceRows.length, chunks: namedTraceChunks, conservation_pass: namedTraceChunks.reduce((sum, row) => sum + row.rows, 0) === namedTraceRows.length }));
    const names = fs.readdirSync(output).sort();
    let determinism;
    if (compare) {
      const mismatches = names.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
      ensure(!mismatches.length, `GUEGOM determinism mismatch ${mismatches.join(",")}`);
      determinism = { clean_builds: 2, compared_files: names.length, byte_identical: true, mismatches: [] };
    } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
    write("DETERMINISM_RECEIPT.json", canonical(determinism)); writeManifest(output);
    if (compare) { fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism)); writeManifest(compare); ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "GUEGOM final manifests differ"); }
    process.stdout.write(canonical({ output, observation, determinism })); return;
  }
  if (v52hNamedOnly) {
    const baselineRun = machineRuns.get("V52G_FROZEN_BASELINE"), candidateRun = machineRuns.get("V52H_REMOVE_PAIR_LOWS_PRECONDITION");
    const before = buildV52FlowPackage(baselineRun, baseByEvent, v52TapePackBytes, v52OnsetReceiptBytes, 1, "V52G_SMIILA_NAMED_REPLAY");
    const after = buildV52FlowPackage(candidateRun, baseByEvent, v52TapePackBytes, v52OnsetReceiptBytes, 1, "V52H_SMIILA_NAMED_REPLAY");
    const baselineEvent = baselineRun.marketEvents[0], candidateEvent = candidateRun.marketEvents[0];
    ensure(baselineEvent?.event_id.includes("SMIILA") && candidateEvent?.event_id === baselineEvent.event_id, "SMIILA named replay identity mismatch");
    const observation = {
      event_id: candidateEvent.event_id,
      provenance: activeReadCohort.named_reused_observation,
      baseline_pair_lows_block_receipts: before.trace.filter((row) => row.blocked_clause === "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR").length,
      candidate_pair_lows_block_receipts: after.trace.filter((row) => row.blocked_clause === "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR").length,
      candidate_posts_authorized_with_market_proof_false: after.trace.filter((row) => ["POST", "LICENSED_HOLD"].includes(row.gate_verdict) && row.coherence?.lows_under_par === false).length,
      baseline_completed: baselineEvent.completed_pair, candidate_completed: candidateEvent.completed_pair,
      baseline_combined_entry_cents: baselineEvent.combined_entry_cents, candidate_combined_entry_cents: candidateEvent.combined_entry_cents,
      candidate_COMPLETE_AT_LOSS: candidateEvent.completed_pair && !candidateEvent.pair_under_par,
    };
    observation.pair_par_block_converted = observation.baseline_pair_lows_block_receipts > 0 && observation.candidate_pair_lows_block_receipts === 0 && observation.candidate_posts_authorized_with_market_proof_false > 0;
    ensure(observation.pair_par_block_converted && !observation.candidate_COMPLETE_AT_LOSS, `SMIILA named claim failed ${JSON.stringify(observation)}`);
    write("REPORT.md", `# V52h SMIILA named observation\n\nSMIILA is an explicitly reused V52B fresh-cohort identity, not a member of V52h's fresh 25. The isolated replay exists only to bind the pre-stated named observation without contaminating the V52h cohort. Pair-par block conversion: ${observation.pair_par_block_converted}. COMPLETE_AT_LOSS: ${observation.candidate_COMPLETE_AT_LOSS}.\n`);
    write("CONTROL_BINDING.json", canonical({ parent_commit: V52G_COMMIT, branch: "codex/window1-v52h-remove-pair-lows-precondition-20260813", scope: "SMIILA_NAMED_OBSERVATION_ONLY", score_or_disposition_804_run: false, policy_edits: false }));
    write("SMIILA_NAMED_OBSERVATION.json", canonical(observation));
    write("FORBIDDEN_ACCESS_RECEIPT.json", canonical({ holdout: false, live: false, network_runtime: false, orders: false, positions: false, deployment: false, full_804_run: false, scavenger: false }));
    await writeGzipRowsFile(path.join(output, "SMIILA_NAMED_BEFORE_AFTER_TRACE.jsonl.gz"), before.trace.map((row) => ({ variant: "V52G", ...row })).concat(after.trace.map((row) => ({ variant: "V52H", ...row }))));
    const names = fs.readdirSync(output).sort();
    let determinism;
    if (compare) {
      const mismatches = names.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
      ensure(!mismatches.length, `SMIILA determinism mismatch ${mismatches.join(",")}`);
      determinism = { clean_builds: 2, compared_files: names.length, byte_identical: true, mismatches: [] };
    } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
    write("DETERMINISM_RECEIPT.json", canonical(determinism)); writeManifest(output);
    if (compare) { fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism)); writeManifest(compare); ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "SMIILA final manifests differ"); }
    process.stdout.write(canonical({ output, observation, determinism })); return;
  }
  if (isV54Full) {
    const baselineRun = machineRuns.get("V52L_FROZEN_BASELINE"), candidateRun = machineRuns.get("V54_PAIR_MODEL");
    const baselineGrade = gradeV54Events(baselineRun.marketEvents, groundTruthWindowBinding), candidateGrade = gradeV54Events(candidateRun.marketEvents, groundTruthWindowBinding);
    const baseline = baselineGrade.score, candidate = candidateGrade.score;
    ensure(baseline.D === 804 && candidate.D === 804, `V54 fixed-population conservation changed ${baseline.D}/${candidate.D}`);
    ensure(baseline.completed_pairs === 311, `V54 champion floor binding changed ${baseline.completed_pairs}`);
    ensure(baseline.locked_cents_per_contract === 714, `V54 champion locked-cents binding changed ${baseline.locked_cents_per_contract}`);
    const assertionPass = Object.values(v54AssertionFailures).every((rows) => rows.length === 0);
    ensure(assertionPass, `V54 build assertions failed ${JSON.stringify(v54AssertionFailures)}`);
    const baselineIds = new Set(baselineGrade.rows.filter((row) => row.state === "COMPLETE_AT_DELTA").map((row) => row.event_id));
    const candidateIds = new Set(candidateGrade.rows.filter((row) => row.state === "COMPLETE_AT_DELTA").map((row) => row.event_id));
    const retained = [...baselineIds].filter((id) => candidateIds.has(id)).sort(), lost = [...baselineIds].filter((id) => !candidateIds.has(id)).sort(), gained = [...candidateIds].filter((id) => !baselineIds.has(id)).sort();
    const pinIds = new Set(activeReadCohort.standing_pins.map((row) => row.event_id));
    const pinBaselineEvents = baselineRun.marketEvents.filter((event) => pinIds.has(event.event_id));
    const pinCandidateEvents = candidateRun.marketEvents.filter((event) => pinIds.has(event.event_id));
    const pinBaseline = score(pinBaselineEvents), pinCandidate = score(pinCandidateEvents);
    const pinIdentityLost = pinBaselineEvents.filter((event) => event.completed_pair && !pinCandidateEvents.find((row) => row.event_id === event.event_id)?.completed_pair).map((event) => event.event_id);
    const pinsTripwire = {
      games: 5,
      champion: { completed_pairs: pinBaseline.completed_pairs, locked_cents: pinBaseline.locked_cents_per_contract },
      candidate: { completed_pairs: pinCandidate.completed_pairs, locked_cents: pinCandidate.locked_cents_per_contract },
      identity_lost: pinIdentityLost,
      pass: pinCandidate.completed_pairs >= pinBaseline.completed_pairs && pinCandidate.locked_cents_per_contract >= pinBaseline.locked_cents_per_contract && pinIdentityLost.length === 0,
    };
    ensure(pinsTripwire.pass, `V54 pins tripwire failed during 804 replay ${JSON.stringify(pinsTripwire)}`);
    const averageDelta = (rows) => {
      const completed = rows.filter((row) => row.state === "COMPLETE_AT_DELTA");
      const values = completed.map((row) => 100 - row.combined_entry_cents);
      return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
    };
    const categories = [...new Set(candidateRun.marketEvents.map((event) => event.category))].sort();
    const categoryRows = categories.map((category) => {
      const baseRows = baselineGrade.rows.filter((event) => event.category === category), candidateRows = candidateGrade.rows.filter((event) => event.category === category);
      const b = gradeV54Events(baselineRun.marketEvents.filter((event) => event.category === category), groundTruthWindowBinding).score, c = gradeV54Events(candidateRun.marketEvents.filter((event) => event.category === category), groundTruthWindowBinding).score;
      return { category, games: candidateRows.length, champion_completed_pairs: b.completed_pairs, candidate_completed_pairs: c.completed_pairs, champion_locked_cents: b.locked_cents_per_contract, candidate_locked_cents: c.locked_cents_per_contract, champion_average_game_delta_vs_100_cents: averageDelta(baseRows), candidate_average_game_delta_vs_100_cents: averageDelta(candidateRows) };
    });
    const tuneGate = {
      champion_floor_completed_pairs: 311,
      candidate_completed_pairs: candidate.completed_pairs,
      candidate_at_or_above_champion_floor: candidate.completed_pairs >= 311,
      pins_tripwire: pinsTripwire.pass,
      build_assertions: assertionPass,
    };
    tuneGate.pass = Object.values(tuneGate).filter((value) => typeof value === "boolean").every(Boolean);

    const custodyRelative = "stage1/v54_pair_model_iteration_01_804_20260821/full_pair_license_trace";
    const custodyDir = path.join(privateRoot, ...custodyRelative.split("/"));
    fs.mkdirSync(custodyDir, { recursive: true });
    const custodyRows = [];
    for (const chunk of v54TraceChunks) {
      const source = path.join(output, chunk.name), destination = path.join(custodyDir, chunk.name);
      fs.copyFileSync(source, destination);
      ensure(fileHash(source) === fileHash(destination), `V54 custody copy mismatch ${chunk.name}`);
      custodyRows.push({ logical_trace_path: `V54_PAIR_LICENSE_TRACE_804/${chunk.name}`, sha256: chunk.sha256, bytes: chunk.bytes, license_span_rows: chunk.row_count, event_count: chunk.event_count, event_ids: chunk.events, custody_location: `OMI-Window1-private/${custodyRelative}/${chunk.name}` });
      fs.unlinkSync(source);
    }
    const custodyManifest = {
      law: "L8_L22_EXTERNAL_CUSTODY",
      committed_file_cap_bytes: 50 * 1024 * 1024,
      format: "GZIP_JSONL_LOSSLESS_BID_LICENSE_STATE_SPANS_ONE_EVENT_PER_CHUNK; EVERY_POST_OR_REPRICE_LICENSE_RECEIPT_COUNTED_AND_HASH_CHAINED",
      total_chunks: custodyRows.length,
      total_events: custodyRows.reduce((sum, row) => sum + row.event_count, 0),
      total_rows: custodyRows.reduce((sum, row) => sum + row.license_span_rows, 0),
      total_bytes: custodyRows.reduce((sum, row) => sum + row.bytes, 0),
      rows: custodyRows,
      conservation: { expected_events: 804, observed_events: custodyRows.reduce((sum, row) => sum + row.event_count, 0), pass: custodyRows.reduce((sum, row) => sum + row.event_count, 0) === 804 },
    };
    ensure(custodyManifest.conservation.pass, "V54 custody trace event conservation failed");

    const compactEvent = (event) => ({
      event_id: event.event_id,
      category: event.category,
      starting_price_split: event.starting_price_split,
      bell_confidence: event.bell_confidence,
      completed_pair: event.completed_pair,
      combined_entry_cents: event.combined_entry_cents,
      pair_under_par: event.pair_under_par,
      game_delta_vs_100_cents: event.completed_pair ? 100 - event.combined_entry_cents : null,
      legs: Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, { leg_identity: leg.leg_identity, credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, fill_timestamp_epoch: leg.fill_timestamp_epoch, terminal_reason: leg.terminal_reason, resting_target_at_edge_cents: leg.resting_target_at_edge_cents }]))
    });
    const storyEvents = candidateRun.marketEvents.filter((event) => v54StoryIds.has(event.event_id)).sort((a, b) => a.event_id.localeCompare(b.event_id));
    ensure(storyEvents.length === 30, `V54 story selection conservation changed ${storyEvents.length}`);
    const storyIndex = storyEvents.map((event) => {
      const spans = v54StoryRows.filter((row) => row.event_id === event.event_id && typeof row.representative_sentence === "string");
      return { ...compactEvent(event), license_spans: v54StoryRows.filter((row) => row.event_id === event.event_id).length, covered_receipts: v54StoryRows.filter((row) => row.event_id === event.event_id).reduce((sum, row) => sum + row.receipt_count, 0), first_pair_sentence: spans.at(0)?.representative_sentence ?? null, last_pair_sentence: spans.at(-1)?.representative_sentence ?? null };
    });
    const scorecard = {
      label: "V54_PAIR_MODEL_ITERATION_01_FIXED_804",
      law: "L19a",
      population: { games: 804, truth_table_offered_denominator: 680, offered_percentage_embargoed: true, denominator_source_commit: "d449889e" },
      champion: { completes_over_804: { numerator: baseline.completed_pairs, denominator: 804 }, completes_over_truth_table_offered_680: { numerator: baseline.completed_pairs, denominator: 680, percentage: null }, under_par_pairs: baseline.under_par_pairs, completed_at_loss: baseline.completed_at_loss, locked_cents: baseline.locked_cents_per_contract, average_game_delta_vs_100_cents: averageDelta(baselineGrade.rows) },
      candidate: { completes_over_804: { numerator: candidate.completed_pairs, denominator: 804 }, completes_over_truth_table_offered_680: { numerator: candidate.completed_pairs, denominator: 680, percentage: null }, under_par_pairs: candidate.under_par_pairs, completed_at_loss: candidate.completed_at_loss, locked_cents: candidate.locked_cents_per_contract, average_game_delta_vs_100_cents: averageDelta(candidateGrade.rows) },
      identity_vs_champion: { retained_count: retained.length, lost_count: lost.length, gained_count: gained.length, retained_event_ids: retained, lost_event_ids: lost, gained_event_ids: gained },
      per_category: categoryRows,
      pins_tripwire: pinsTripwire,
      tune_gate: tuneGate,
      disposition: tuneGate.pass ? "ITERATION_01_SURVIVES_CHAMPION_FLOOR_OPERATOR_REVIEW_REQUIRED" : "STOP_BANK_CAUSE_BELOW_CHAMPION_FLOOR",
    };
    const pairStats = { ...v54PairModelStats, sentence_hashes: [...v54PairModelStats.sentence_hashes].sort(), distinct_machine_written_sentences: v54PairModelStats.sentence_hashes.size };
    write("SCORECARD.json", canonical(scorecard));
    write("BUILD_ASSERTIONS.json", canonical({ pass: assertionPass, failures: v54AssertionFailures }));
    write("PAIR_MODEL_LICENSE_SUMMARY.json", canonical({ model: "V54_PAIR_MODEL", provenance: v54PairModel.PROVENANCE, stats: pairStats, type_system: { legal_decided_state: "exactly one STRENGTHENING and exactly one FADING", legal_fallback_state: "UNDECIDED with null side identities", two_same_labels_representable: false }, every_license_archived: custodyManifest.conservation.pass }));
    write("EXTERNAL_CUSTODY_MANIFEST.json", canonical(custodyManifest));
    write("DECISION_STORY_INDEX_30.json", canonical({ selection: v54StorySelection, games: storyIndex, conservation: { expected: 30, observed: storyIndex.length, pass: storyIndex.length === 30 } }));
    await writeGzipRowsFile(path.join(output, "DECISION_STORIES_30.jsonl.gz"), v54StoryRows, 9);
    await writeGzipRowsFile(path.join(output, "MARKET_EVENT_LEDGER_804.jsonl.gz"), candidateRun.marketEvents.map(compactEvent), 9);
    write("SOURCE_HASH_MANIFEST.json", canonical({ policy: { path: "arb-executor/analysis/window1_v54_pair_model.js", sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v54_pair_model.js")) }, replay_shell: { path: "arb-executor/analysis/build_window1_v38_maker_only.js", sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v38_maker_only.js")) }, ground_truth: groundTruthWindowBinding.binding, baseline: { policy: "V52L_FROZEN_CHAMPION", expected_completed_pairs: 311, expected_locked_cents: 714 }, full_trace: custodyManifest }));
    write("FORBIDDEN_ACCESS_RECEIPT.json", canonical({ sealed: false, holdout: false, live: false, network_runtime: false, orders: false, positions: false, deployment: false, tuning_population: "FIXED_DEV_804_ONLY", truth_table_offered_percentages_reported: false }));
    write("REPORT.md", `# V54 Pair Model — iteration 01\n\nPins passed ${pinCandidate.completed_pairs}/${pinBaseline.completed_pairs} completes and ${pinCandidate.locked_cents_per_contract}/${pinBaseline.locked_cents_per_contract}c. On the W1-ground-truth-bound fixed D=804 ruler, champion completed ${baseline.completed_pairs} and V54 completed ${candidate.completed_pairs}; the hard floor ${tuneGate.candidate_at_or_above_champion_floor ? "held" : "failed"}. Raw truth-table offered display: ${candidate.completed_pairs}/680; percentages are embargoed under F-V53-039. Average completed-game delta was ${averageDelta(candidateGrade.rows)}c versus champion ${averageDelta(baselineGrade.rows)}c. Identity: ${retained.length} retained, ${lost.length} lost, ${gained.length} gained. All ${v54PairModelStats.decision_receipts} bid-license receipt computations are count- and hash-bound into ${custodyManifest.total_rows} lossless license-state spans in external custody; 30 deterministic decision stories are included for CC. No sealed, live, order, position, deployment, or network-runtime path was accessed.\n`);
    const committed = fs.readdirSync(output).sort();
    for (const name of committed) ensure(fs.statSync(path.join(output, name)).size <= 50 * 1024 * 1024, `L22 committed-file cap exceeded ${name}`);
    let determinism;
    if (compare) {
      const mismatches = committed.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
      ensure(!mismatches.length, `V54 determinism mismatch ${mismatches.join(",")}`);
      determinism = { clean_builds: 2, compared_files: committed.length, byte_identical: true, mismatches: [] };
    } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
    write("DETERMINISM_RECEIPT.json", canonical(determinism));
    writeManifest(output);
    if (compare) { fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism)); writeManifest(compare); ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "V54 final manifests differ"); }
    process.stdout.write(canonical({ output, scorecard, pair_model_stats: pairStats, decision_stories: v54StorySelection, custody: { events: custodyManifest.total_events, rows: custodyManifest.total_rows, bytes: custodyManifest.total_bytes }, determinism }));
    return;
  }
  if (isV53) { await emitV53Stage1(); return; }
  if (isV52ReadAuthority && !isV52FullExam) {
    const iterationLabel = isV52r ? "V52R_ITERATION_ASSEMBLED_POLICY" : isV52q ? "V52Q_ITERATION_ANCHOR_CORRECTION" : isV52p ? "V52P_ITERATION_RIPENESS_GATED_ROLE_BINDING" : isV52o ? "V52O_ITERATION_BENCHMARKED_ROLE_INSTRUMENT" : isV52n ? "V52N_ITERATION_RECOGNITION_CONFIDENCE_GATES" : isV52m ? "V52M_ITERATION_MACRO_RECOGNITION" : isV52l ? "V52L_CAUSAL_ONSET" : isV52k ? "V52K_ITERATION10" : isV52j ? "V52J_ITERATION9" : isV52i ? "V52I_ITERATION8" : isV52h ? "V52H_ITERATION7" : isV52g ? "V52G_ITERATION6" : isV52f ? "V52F_ITERATION5" : isV52e ? "V52E_ITERATION4" : isV52d ? "V52D_ITERATION3" : isV52c ? "V52C_ITERATION2" : "V52B_ITERATION1";
    const authorizedClause = isV52r ? "CLAUSE_3_TRD5_ROLE_AND_LOW_MINUS_ONE_ASSEMBLY_ONLY" : isV52q ? "CLAUSE_3_ROLE_ANCHOR_CORRECTION_ONLY" : isV52p ? "CLAUSE_3_RIPENESS_GATED_ROLE_BINDING_ONLY" : isV52o ? "CLAUSE_3_BENCHMARKED_EARLY_ROLE_INSTRUMENT_ONLY" : isV52n ? "CLAUSE_3_RECOGNITION_CONFIDENCE_GATE_ONLY" : isV52m ? "CLAUSE_3_CAUSAL_MACRO_RECOGNITION_FLOOR_DEPTH_ONLY" : isV52l ? "CLAUSE_1_CAUSAL_STABILITY_ONSET_ONLY" : isV52k ? "CLAUSE_3_LIBRARY_BACKED_LEVEL_EVIDENCE_ONLY" : isV52j ? "CLAUSE_3_N4_ROLE_CONDITIONED_LEVEL_SELECTION_ONLY" : isV52i ? "CLAUSE_3_N4_DEPTH_INFORMED_LEVEL_SELECTION_ONLY" : isV52h ? "CLAUSE_4_MARKET_PROOF_PRECONDITION_REMOVAL_ONLY" : isV52g ? "CLAUSE_6_ORDER_FREE_JOINT_TARGET_CONSERVATION_ONLY" : isV52f ? "CLAUSE_5_PAIR_ENTRY_CONSERVATION_ONLY" : isV52e ? "N9_CLEAN_PALANTIR_WIRING_ONLY" : isV52d ? "CLAUSE_4_DISAGREEMENT_REFEREE_ONLY" : isV52c ? "CLAUSE_2_EVIDENCE_HORIZON_ONLY" : "CLAUSE_3_LEVEL_AUTHORITY_ONLY";
    const baselineName = isV52r ? "V52L_FROZEN_BASELINE" : isV52q ? "V52P_FROZEN_BASELINE" : (isV52p || isV52o) ? "V52L_FROZEN_BASELINE" : isV52n ? "V52M_FROZEN_BASELINE" : isV52m ? "V52L_FROZEN_BASELINE" : (isV52l || isV52DepthValidation) ? "V52H_FROZEN_BASELINE" : isV52h ? "V52G_FROZEN_BASELINE" : isV52g ? "V52F_FROZEN_BASELINE" : isV52f ? "V52E_FROZEN_BASELINE" : isV52e ? "V52D_FROZEN_BASELINE" : isV52d ? "V52C_FROZEN_BASELINE" : isV52c ? "V52B_FROZEN_BASELINE" : "V52_FROZEN_BASELINE";
    const candidateName = isV52r ? "V52R_ASSEMBLED_POLICY" : isV52q ? "V52Q_ANCHOR_CORRECTION" : isV52p ? "V52P_RIPENESS_GATED_ROLE_BINDING" : isV52o ? "V52O_BENCHMARKED_ROLE_INSTRUMENT" : isV52n ? "V52N_RECOGNITION_CONFIDENCE_GATES" : isV52m ? "V52M_MACRO_RECOGNITION" : isV52l ? "V52L_CAUSAL_STABILITY_ONSET" : isV52k ? "V52K_LIBRARY_BACKED_EVIDENCE" : isV52j ? "V52J_ROLE_CONDITIONED_LEVEL_SELECTION" : isV52i ? "V52I_DEPTH_INFORMED_LEVEL_SELECTION" : isV52h ? "V52H_REMOVE_PAIR_LOWS_PRECONDITION" : isV52g ? "V52G_JOINT_TARGET_CONSERVATION" : isV52f ? "V52F_PAIR_ENTRY_CONSERVATION" : isV52e ? "V52E_PALANTIR_WIRING" : isV52d ? "V52D_DISAGREEMENT_REFEREE" : isV52c ? "V52C_FULL_POST_ONSET_READ" : "V52B_READ_LEVEL_AUTHORITY";
    const baselineRun = machineRuns.get(baselineName);
    const candidateRun = machineRuns.get(candidateName);
    ensure(stage === "cohort30", `${iterationLabel} requires cohort30 stage, got ${stage}`);
    const baselineFlow = buildV52FlowPackage(baselineRun, baseByEvent, v52TapePackBytes, v52OnsetReceiptBytes, 30, `${baselineName}_30_GAME_TRACE`);
    const candidateFlow = buildV52FlowPackage(candidateRun, baseByEvent, v52TapePackBytes, v52OnsetReceiptBytes, 30, `${iterationLabel}_30_GAME_FLOW_CHECK`);
    const traceKey = (row) => `${row.event_id}|${row.leg_identity}|${row.timestamp_epoch}|${row.receipt}`;
    const baselineTrace = new Map(baselineFlow.trace.map((row) => [traceKey(row), row]));
    const candidateTrace = new Map(candidateFlow.trace.map((row) => [traceKey(row), row]));
    ensure(baselineTrace.size === baselineFlow.trace.length && candidateTrace.size === candidateFlow.trace.length, "duplicate decision trace key");
    const commonTraceKeys = [...baselineTrace.keys()].filter((key) => candidateTrace.has(key));
    ensure(commonTraceKeys.length > 0, `${baselineName}/${candidateName} traces have no common receipt universe`);
    const candidateTraceIndex = new Map(candidateFlow.trace.map((row, index) => [traceKey(row), index]));
    const firstAuthorizedIndexByEvent = new Map();
    const firstAuthorizedTimestampByEvent = new Map();
    if (isV52g) for (let index = 0; index < candidateFlow.trace.length; index += 1) {
      const row = candidateFlow.trace[index];
      if (row.joint_target_conservation?.target_changed === true && !firstAuthorizedIndexByEvent.has(row.event_id)) firstAuthorizedIndexByEvent.set(row.event_id, index);
    }
    if (isV52h) for (let index = 0; index < candidateFlow.trace.length; index += 1) {
      const after = candidateFlow.trace[index], before = baselineTrace.get(traceKey(after));
      if (before?.blocked_clause === "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR" && after.blocked_clause !== "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR" && !firstAuthorizedIndexByEvent.has(after.event_id)) firstAuthorizedIndexByEvent.set(after.event_id, index);
    }
    if (isV52i) for (let index = 0; index < candidateFlow.trace.length; index += 1) {
      const row = candidateFlow.trace[index];
      if (row.depth_informed_level_selection?.target_changed === true && !firstAuthorizedIndexByEvent.has(row.event_id)) firstAuthorizedIndexByEvent.set(row.event_id, index);
    }
    if (isV52j) for (let index = 0; index < candidateFlow.trace.length; index += 1) {
      const row = candidateFlow.trace[index];
      if (row.role_conditioned_level_selection?.target_changed === true && !firstAuthorizedIndexByEvent.has(row.event_id)) firstAuthorizedIndexByEvent.set(row.event_id, index);
    }
    if (isV52k) for (let index = 0; index < candidateFlow.trace.length; index += 1) {
      const row = candidateFlow.trace[index];
      if (row.library_backed_level_evidence?.target_changed === true && !firstAuthorizedIndexByEvent.has(row.event_id)) firstAuthorizedIndexByEvent.set(row.event_id, index);
    }
    if (isV52MacroRecognition) for (let index = 0; index < candidateFlow.trace.length; index += 1) {
      const row = candidateFlow.trace[index];
      if ((isV52r && row.macro_recognition?.trd5?.gate_passed === true && row.macro_recognition?.bound_role !== null) || (isV52q && row.macro_recognition?.candidate_role !== null) || (isV52p && row.macro_recognition?.ripeness?.verified_binding === true) || (isV52o && row.benchmarked_role_instrument?.benchmark_role?.signable === true) || (isV52n && row.recognition_confidence_gate) || (!isV52Ripeness && !isV52r && !isV52o && !isV52n && row.per_shape_floor_depth?.applicable === true)) {
        if (!firstAuthorizedIndexByEvent.has(row.event_id)) firstAuthorizedIndexByEvent.set(row.event_id, index);
        const priorTimestamp = firstAuthorizedTimestampByEvent.get(row.event_id);
        if (!Number.isFinite(priorTimestamp) || row.timestamp_epoch < priorTimestamp) firstAuthorizedTimestampByEvent.set(row.event_id, row.timestamp_epoch);
      }
    }
    const onsetLawFields = (value) => value ? ({ passed: value.passed, selected_candidate: value.selected_candidate, timestamp_epoch: value.timestamp_epoch, t_minus_scheduled_seconds: value.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: value.t_minus_actual_bell_seconds, candidates: value.candidates }) : null;
    if (isV52l) for (let index = 0; index < candidateFlow.trace.length; index += 1) {
      const after = candidateFlow.trace[index], before = baselineTrace.get(traceKey(after));
      if (before && canonical(onsetLawFields(before.onset)) !== canonical(onsetLawFields(after.onset)) && !firstAuthorizedIndexByEvent.has(after.event_id)) firstAuthorizedIndexByEvent.set(after.event_id, index);
    }
    const coherenceLawApplied = (value) => Boolean(value) && value.disagreement_clear === (!value.disagreement_firing || value.sibling_credited);
    const clause4SameInputProof = (coherence) => {
      const fixedLicense = { onset: { passed: true }, read: { passed: true }, diary: { passed: true }, coherence, level: { target_cents: 50 } };
      const frozenVerdict = ((isV52c || isV52d || isV52e) ? frozenV52bPolicy : frozenV52Policy).firstFailure(fixedLicense, { authorized: true, target_cents: 50 });
      const candidateVerdict = policy.firstFailure(fixedLicense, { authorized: true, target_cents: 50 });
      return coherenceLawApplied(coherence) && frozenVerdict === candidateVerdict;
    };
    const frozenClauseDiffs = [];
    const downstreamFrozenInputDivergences = [];
    const decisionDiffs = [];
    for (const key of commonTraceKeys) {
      const before = baselineTrace.get(key);
      const after = candidateTrace.get(key);
      const checks = {
        clause_1_onset: canonical(onsetLawFields(before.onset)) === canonical(onsetLawFields(after.onset)),
        ...((isV52c || isV52d || isV52e) ? {} : { clause_2_read: canonical(before.read) === canonical(after.read) }),
        ...(isV52MacroRecognition ? {
          clause_2_read: canonical(before.read) === canonical(after.read),
          clause_4_coherence: canonical(before.coherence) === canonical(after.coherence),
          N9_palantir: canonical(before.palantir) === canonical(after.palantir),
          frozen_clause_function_identity: policy.fullPostOnsetRead === frozenV52ePolicy.fullPostOnsetRead
            && policy.fullPostOnsetAuthority === frozenV52ePolicy.fullPostOnsetAuthority
            && policy.observePostOnsetEvidence === frozenV52ePolicy.observePostOnsetEvidence
            && policy.firstFailure === frozenV52ePolicy.firstFailure
            && policy.tradeTruthCredit === frozenV52ePolicy.tradeTruthCredit
            && policy.continuousConsultation === frozenV52ePolicy.continuousConsultation
            && policy.machineReadLevel === frozenV52ePolicy.machineReadLevel
            && policy.settlementIdentity === frozenV52hPolicy.settlementIdentity
            && policy.jointTargetConservation === frozenV52hPolicy.jointTargetConservation
            && policy.marketProofReceipt === frozenV52hPolicy.marketProofReceipt,
          clause_3_authorized_wrapper_present: typeof policy.floorDepthSelection === "function" && typeof policy.incumbentWithSelectedTarget === "function",
        } : isV52DepthValidation ? {
          clause_2_read: canonical(before.read) === canonical(after.read),
          clause_4_coherence: canonical(before.coherence) === canonical(after.coherence),
          clause_5_function_identity: policy.settlementIdentity === frozenV52hPolicy.settlementIdentity,
          clause_6_function_identity: policy.jointTargetConservation === frozenV52hPolicy.jointTargetConservation,
          clause_4_market_proof_function_identity: policy.marketProofReceipt === frozenV52hPolicy.marketProofReceipt,
          frozen_upstream_function_identity: policy.fullPostOnsetRead === frozenV52hPolicy.fullPostOnsetRead
            && policy.fullPostOnsetAuthority === frozenV52hPolicy.fullPostOnsetAuthority
            && policy.observePostOnsetEvidence === frozenV52hPolicy.observePostOnsetEvidence
            && policy.firstFailure === frozenV52hPolicy.firstFailure
            && policy.tradeTruthCredit === frozenV52hPolicy.tradeTruthCredit,
        } : (isV52f || isV52g || isV52h || isV52CausalOnset) ? {
          clause_2_read: canonical(before.read) === canonical(after.read),
          clause_3_machine_read_input: canonical(before.level?.machine_read) === canonical(after.level?.machine_read),
          clause_4_coherence: canonical(before.coherence) === canonical(after.coherence),
          N9_palantir: canonical(before.palantir) === canonical(after.palantir),
          frozen_clause_function_identity: policy.fullPostOnsetRead === frozenV52ePolicy.fullPostOnsetRead
            && policy.fullPostOnsetAuthority === frozenV52ePolicy.fullPostOnsetAuthority
            && policy.observePostOnsetEvidence === frozenV52ePolicy.observePostOnsetEvidence
            && policy.firstFailure === frozenV52ePolicy.firstFailure
            && policy.tradeTruthCredit === frozenV52ePolicy.tradeTruthCredit
            && policy.continuousConsultation === frozenV52ePolicy.continuousConsultation
            && policy.machineReadLevel === frozenV52ePolicy.machineReadLevel,
        } : isV52e ? {
          clause_2_read: canonical(before.read) === canonical(after.read),
          frozen_clause_function_identity: policy.fullPostOnsetRead === frozenV52dPolicy.fullPostOnsetRead
            && policy.fullPostOnsetAuthority === frozenV52dPolicy.fullPostOnsetAuthority
            && policy.observePostOnsetEvidence === frozenV52dPolicy.observePostOnsetEvidence
            && policy.firstFailure === frozenV52dPolicy.firstFailure
            && policy.tradeTruthCredit === frozenV52dPolicy.tradeTruthCredit,
        } : isV52d ? {
          clause_2_read: canonical(before.read) === canonical(after.read),
          clause_3_policy_function_identity: policy.machineReadLevel === frozenV52cPolicy.machineReadLevel && policy.gateDecision === frozenV52cPolicy.gateDecision && policy.firstFailure === frozenV52cPolicy.firstFailure,
        } : { clause_4_coherence: clause4SameInputProof(before.coherence) && clause4SameInputProof(after.coherence) }),
        scavenger: canonical(before.scavenger) === canonical(after.scavenger),
      };
      if (!Object.values(checks).every(Boolean)) {
        const firstAuthorizedIndex = firstAuthorizedIndexByEvent.get(after.event_id);
        const candidateIndex = candidateTraceIndex.get(key);
        const receipt = { key, checks, before: { onset: before.onset, read: before.read, coherence: before.coherence, scavenger: before.scavenger }, after: { onset: after.onset, read: after.read, coherence: after.coherence, scavenger: after.scavenger } };
        const authorizationReached = isV52MacroRecognition
          ? Number.isFinite(firstAuthorizedTimestampByEvent.get(after.event_id)) && after.timestamp_epoch >= firstAuthorizedTimestampByEvent.get(after.event_id)
          : Number.isInteger(firstAuthorizedIndex) && candidateIndex >= firstAuthorizedIndex;
        if ((isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) && authorizationReached) downstreamFrozenInputDivergences.push({ ...receipt, classification: isV52r ? "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_TRD5_LOW1_ASSEMBLY" : isV52q ? "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_ROLE_ANCHOR_CORRECTION" : isV52p ? "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_RIPENESS_GATED_ROLE_DEPTH_TARGET" : isV52o ? "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_BENCHMARKED_ROLE_DEPTH_TARGET" : isV52n ? "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_RECOGNITION_CONFIDENCE_ABSTENTION" : isV52m ? "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CAUSAL_MACRO_DEPTH_TARGET" : isV52l ? "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CAUSAL_ONSET" : isV52k ? "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_3_LIBRARY_EVIDENCE" : isV52j ? "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_3_ROLE_SELECTION" : isV52i ? "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_3_DEPTH_SELECTION" : isV52h ? "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_4_PRECONDITION_REMOVAL" : "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_6" });
        else frozenClauseDiffs.push(receipt);
      }
      const decisionView = (row, includeDepth) => ({
        gate_verdict: row.gate_verdict,
        blocked_clause: row.blocked_clause,
        final_action: row.final_action,
        final_target_cents: row.final_target_cents,
        reason: row.reason,
        ...(isV52DepthValidation ? {
          frozen_machine_read_authorized: row.level?.machine_read?.authorized ?? null,
          frozen_machine_read_target_cents: row.level?.machine_read?.target_cents ?? null,
          ...(includeDepth && row.depth_informed_level_selection?.target_changed ? { depth_informed_level_selection: row.depth_informed_level_selection } : {}),
          ...(includeDepth && row.role_conditioned_level_selection ? { role_conditioned_level_selection: row.role_conditioned_level_selection } : {}),
          ...(includeDepth && row.library_backed_level_evidence ? { library_backed_level_evidence: row.library_backed_level_evidence } : {}),
        } : { level: row.level }),
      });
      const beforeDecision = decisionView(before, false);
      const afterDecision = decisionView(after, true);
      if (canonical(beforeDecision) !== canonical(afterDecision)) decisionDiffs.push({ key, event_id: after.event_id, leg_identity: after.leg_identity, timestamp_epoch: after.timestamp_epoch, receipt: after.receipt, before: beforeDecision, after: afterDecision, authorized_clause: authorizedClause });
    }
    for (const key of [...baselineTrace.keys()].filter((value) => !candidateTrace.has(value))) {
      const before = baselineTrace.get(key);
      decisionDiffs.push({ key, event_id: before.event_id, leg_identity: before.leg_identity, timestamp_epoch: before.timestamp_epoch, receipt: before.receipt, before: { gate_verdict: before.gate_verdict, blocked_clause: before.blocked_clause, final_action: before.final_action, final_target_cents: before.final_target_cents, reason: before.reason, level: before.level }, after: null, branch_disposition: `${candidateName}_STREAM_ENDED_EARLIER_AFTER_AUTHORIZED_ACTION_OR_CREDIT`, authorized_clause: authorizedClause });
    }
    for (const key of [...candidateTrace.keys()].filter((value) => !baselineTrace.has(value))) {
      const after = candidateTrace.get(key);
      decisionDiffs.push({ key, event_id: after.event_id, leg_identity: after.leg_identity, timestamp_epoch: after.timestamp_epoch, receipt: after.receipt, before: null, after: { gate_verdict: after.gate_verdict, blocked_clause: after.blocked_clause, final_action: after.final_action, final_target_cents: after.final_target_cents, reason: after.reason, level: after.level }, branch_disposition: `${baselineName}_STREAM_ENDED_EARLIER_AFTER_AUTHORIZED_ACTION_OR_CREDIT`, authorized_clause: authorizedClause });
    }
    const checkedClauses = isV52MacroRecognition ? ["clause_1_onset", "clause_2_read", "clause_4_coherence", "N9_palantir", "frozen_clause_function_identity", "clause_3_authorized_wrapper_present", "scavenger"] : isV52DepthValidation ? ["clause_1_onset", "clause_2_read", "clause_4_coherence", "clause_5_function_identity", "clause_6_function_identity", "clause_4_market_proof_function_identity", "frozen_upstream_function_identity", "scavenger"] : (isV52f || isV52g || isV52h || isV52CausalOnset) ? ["clause_1_onset", "clause_2_read", "clause_3_machine_read_input", "clause_4_coherence", "N9_palantir", "frozen_clause_function_identity", "scavenger"] : isV52e ? ["clause_1_onset", "clause_2_read", "frozen_clause_function_identity", "scavenger"] : isV52d ? ["clause_1_onset", "clause_2_read", "clause_3_policy_function_identity", "scavenger"] : isV52c ? ["clause_1_onset", "clause_4_coherence", "scavenger"] : ["clause_1_onset", "clause_2_read", "clause_4_coherence", "scavenger"];
    const frozenClauseFailureCounts = Object.fromEntries(checkedClauses.map((name) => [name, frozenClauseDiffs.filter((row) => !row.checks[name]).length]));
    ensure(frozenClauseDiffs.length === 0, `${iterationLabel} frozen-clause receipt comparison failed ${JSON.stringify(frozenClauseFailureCounts)} first=${JSON.stringify(frozenClauseDiffs[0])}`);
    const candidateMutations = candidateRun.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && ["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE", "GAP_CREDIT_REPRICE_DOWN"].includes(row.kind));
    const baselineDisagreementBlocks = baselineFlow.trace.filter((row) => row.blocked_clause === "FIRING_DISAGREEMENT_ACTIVE");
    const candidateDisagreementBlocks = candidateFlow.trace.filter((row) => row.blocked_clause === "FIRING_DISAGREEMENT_ACTIVE");
    const candidateAdjudicationRows = candidateFlow.trace.filter((row) => row.coherence?.disagreement_adjudication?.firing === true);
    const candidateResolvedAdjudications = candidateAdjudicationRows.filter((row) => row.coherence.disagreement_adjudication.resolved === true);
    const candidateTieAdjudications = candidateAdjudicationRows.filter((row) => row.coherence.disagreement_adjudication.status === "HONEST_TIE_FREEZE_STANDS");
    const eligibleReadRows = candidateFlow.trace.filter((row) => row.onset?.passed && row.read?.passed && row.coherence?.lows_under_par);
    const arsBaselineDisagreementBlocks = baselineDisagreementBlocks.filter((row) => row.event_id.includes("ARSMAR"));
    const arsCandidateAdjudications = candidateAdjudicationRows.filter((row) => row.event_id.includes("ARSMAR"));
    const arsCandidateDisagreementBlocks = candidateDisagreementBlocks.filter((row) => row.event_id.includes("ARSMAR"));
    const refereeSummary = isV52d ? {
      pre_stated_operator_count: 127,
      frozen_V52c_actual_ARSMAR_block_rows: arsBaselineDisagreementBlocks.length,
      discrepancy: arsBaselineDisagreementBlocks.length === 127 ? null : "OPERATOR_PRE_STATED_127_DOES_NOT_EQUAL_FROZEN_V52C_ROW_GRAIN; ACTUAL_FROZEN_TRACE_CONTROLS",
      baseline_order_masked_disagreement_blocks: baselineDisagreementBlocks.length,
      candidate_order_masked_disagreement_blocks: candidateDisagreementBlocks.length,
      order_masked_burden_delta: candidateDisagreementBlocks.length - baselineDisagreementBlocks.length,
      candidate_eligible_read_rows: eligibleReadRows.length,
      candidate_flag_firing_rows: candidateAdjudicationRows.length,
      candidate_flag_firing_rate: eligibleReadRows.length ? candidateAdjudicationRows.length / eligibleReadRows.length : null,
      recorded_adjudications: candidateAdjudicationRows.length,
      resolved_strictly_stronger: candidateResolvedAdjudications.length,
      honest_ties: candidateTieAdjudications.length,
      ARSMAR: {
        baseline_order_masked_blocks: arsBaselineDisagreementBlocks.length,
        candidate_recorded_adjudications: arsCandidateAdjudications.length,
        candidate_order_masked_blocks: arsCandidateDisagreementBlocks.length,
        completed_observation: candidateRun.marketEvents.find((event) => event.event_id.includes("ARSMAR"))?.completed_pair ?? null,
      },
      pre_stated_falsifiable_claim: {
        adjudications_occur: candidateAdjudicationRows.length > 0,
        order_masked_disagreement_burden_falls: candidateDisagreementBlocks.length < baselineDisagreementBlocks.length,
        ARSMAR_blocks_resolve_to_recorded_adjudications_or_downstream_credit: arsCandidateAdjudications.length > 0 && arsCandidateDisagreementBlocks.length < arsBaselineDisagreementBlocks.length,
      },
    } : {
      recorded_adjudications: null,
      resolved_strictly_stronger: null,
      honest_ties: null,
      baseline_order_masked_disagreement_blocks: null,
      candidate_order_masked_disagreement_blocks: null,
      ARSMAR: { baseline_order_masked_blocks: null, candidate_recorded_adjudications: null, candidate_order_masked_blocks: null },
    };
    const palantirRows = isV52e ? candidateFlow.trace.filter((row) => row.palantir) : [];
    const baselineGridAbstentionKeys = isV52e ? new Set(baselineFlow.trace.filter((row) => row.blocked_clause === "MACHINE_READ_LEVEL_AUTHORITY_NOT_EARNED" && candidateTrace.get(traceKey(row))?.palantir?.N4?.grid).map(traceKey)) : new Set();
    const candidateGridAbstentionKeys = isV52e ? new Set(candidateFlow.trace.filter((row) => row.blocked_clause === "MACHINE_READ_LEVEL_AUTHORITY_NOT_EARNED" && row.palantir?.N4?.grid && baselineGridAbstentionKeys.has(traceKey(row))).map(traceKey)) : new Set();
    const n4RescueRows = isV52e ? candidateFlow.trace.filter((row) => row.level?.machine_read?.palantir_rescue === true) : [];
    const n5PriorResolvedRows = isV52e ? candidateFlow.trace.filter((row) => row.coherence?.disagreement_adjudication?.status === "ADJUDICATED_N5_STRICTLY_STRONGER_VALIDATED_BASE_RATE") : [];
    const fourStateRowsFor = (events) => events.map((event) => {
      const legs = Object.values(event.legs), credited = legs.filter((leg) => leg.credited), combined = event.combined_entry_cents;
      const state = credited.length === 2 ? (combined < 100 ? "COMPLETE_AT_DELTA" : "COMPLETE_AT_LOSS") : credited.length === 1 ? "PARTIAL_FOR_REASON" : "NEITHER_FOR_REASON";
      return { event_id: event.event_id, category: event.category, price_region: event.starting_price_split, state, combined_entry_cents: combined, credited_legs: credited.map((leg) => ({ leg_identity: leg.leg_identity, entry_cents: leg.entry_cents })).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)), missing_legs: legs.filter((leg) => !leg.credited).map((leg) => ({ leg_identity: leg.leg_identity, terminal_reason: leg.terminal_reason, judgment_gate_blocks: leg.judgment_gate_blocks })).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)) };
    });
    const baselineFourStateRows = fourStateRowsFor(baselineRun.marketEvents);
    const candidateFourStateRows = fourStateRowsFor(candidateRun.marketEvents);
    const groundBoundFourStateRowsFor = (events) => events.map((event) => {
      const window = groundTruthWindowBinding?.byEvent.get(event.event_id);
      ensure(window, `V52l ground-truth grading row absent ${event.event_id}`);
      if (!window.scoring_eligible) return {
        event_id: event.event_id,
        category: event.category,
        price_region: event.starting_price_split,
        state: "UNKNOWN_BELL_NON_GRADEABLE",
        combined_entry_cents: null,
        delta_vs_100_cents: null,
        credited_legs: [],
        missing_legs: [],
        offered_under_par: null,
        window_binding: window,
      };
      const legs = Object.entries(event.legs).map(([legId, leg]) => ({ legId, leg, floor: window.legs[legId] ?? null }));
      const credited = legs.filter(({ leg }) => leg.credited && Number.isFinite(leg.fill_timestamp_epoch) && leg.fill_timestamp_epoch >= window.span_start_epoch && leg.fill_timestamp_epoch <= window.span_end_epoch);
      const combined = credited.length === 2 ? credited.reduce((sum, { leg }) => sum + leg.entry_cents, 0) : null;
      const state = credited.length === 2 ? (combined < 100 ? "COMPLETE_AT_DELTA" : "COMPLETE_AT_LOSS") : credited.length === 1 ? "PARTIAL_FOR_REASON" : "NEITHER_FOR_REASON";
      const offeredFloors = legs.map(({ floor }) => floor?.floor_cents).filter(Number.isInteger);
      return {
        event_id: event.event_id,
        category: event.category,
        price_region: event.starting_price_split,
        state,
        combined_entry_cents: combined,
        delta_vs_100_cents: Number.isInteger(combined) ? combined - 100 : null,
        credited_legs: credited.map(({ legId, leg, floor }) => ({ leg_identity: leg.leg_identity, leg_id: legId, entry_cents: leg.entry_cents, fill_timestamp_epoch: leg.fill_timestamp_epoch, ground_truth_floor_cents: floor?.floor_cents ?? null, entry_minus_floor_cents: Number.isInteger(floor?.floor_cents) ? leg.entry_cents - floor.floor_cents : null })).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)),
        missing_legs: legs.filter(({ legId, leg }) => !credited.some((row) => row.legId === legId)).map(({ legId, leg, floor }) => ({ leg_identity: leg.leg_identity, leg_id: legId, terminal_reason: leg.credited ? "HISTORICAL_FILL_OUTSIDE_GROUND_TRUTH_WINDOW" : leg.terminal_reason, judgment_gate_blocks: leg.judgment_gate_blocks, ground_truth_floor_cents: floor?.floor_cents ?? null })).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)),
        offered_under_par: offeredFloors.length === 2 ? offeredFloors[0] + offeredFloors[1] < 100 : null,
        offered_floor_sum_cents: offeredFloors.length === 2 ? offeredFloors[0] + offeredFloors[1] : null,
        window_binding: window,
      };
    });
    const reportedBaselineFourStateRows = isV52CausalOnset ? groundBoundFourStateRowsFor(baselineRun.marketEvents) : baselineFourStateRows;
    const reportedCandidateFourStateRows = isV52CausalOnset ? groundBoundFourStateRowsFor(candidateRun.marketEvents) : candidateFourStateRows;
    const fourStateCensus = {
      grading_binding: isV52CausalOnset ? groundTruthWindowBinding.binding : null,
      baseline: { states: countBy(reportedBaselineFourStateRows, (row) => row.state), rows: reportedBaselineFourStateRows.length },
      candidate: { states: countBy(reportedCandidateFourStateRows, (row) => row.state), rows: reportedCandidateFourStateRows.length },
      conservation: { expected: 30, baseline_sum: reportedBaselineFourStateRows.length, candidate_sum: reportedCandidateFourStateRows.length, pass: reportedBaselineFourStateRows.length === 30 && reportedCandidateFourStateRows.length === 30 },
    };
    const onsetTimingRows = isV52l ? candidateRun.marketEvents.flatMap((candidateEvent) => {
      const baselineEvent = baselineRun.marketEvents.find((event) => event.event_id === candidateEvent.event_id);
      const base = baseByEvent.get(candidateEvent.event_id);
      return Object.entries(candidateEvent.legs).map(([legId, candidateLeg]) => {
        const baselineLeg = baselineEvent.legs[legId];
        const oldTimestamp = baselineLeg.v52_onset?.selected?.timestamp_epoch ?? null;
        const newTimestamp = candidateLeg.v52_onset?.selected?.timestamp_epoch ?? null;
        return {
          event_id: candidateEvent.event_id,
          leg_identity: candidateLeg.leg_identity,
          category: candidateEvent.category,
          price_region: candidateLeg.price_region,
          old_onset: oldTimestamp === null ? null : { timestamp_epoch: oldTimestamp, candidate: baselineLeg.v52_onset.selected.candidate, ...clockFields(oldTimestamp, base) },
          new_onset: newTimestamp === null ? null : { timestamp_epoch: newTimestamp, candidate: candidateLeg.v52_onset.selected.candidate, ...clockFields(newTimestamp, base) },
          new_minus_old_seconds: Number.isFinite(oldTimestamp) && Number.isFinite(newTimestamp) ? newTimestamp - oldTimestamp : null,
          old_present_new_absent: Number.isFinite(oldTimestamp) && !Number.isFinite(newTimestamp),
          old_absent_new_present: !Number.isFinite(oldTimestamp) && Number.isFinite(newTimestamp),
          causal_prefix_receipt_law: candidateLeg.v52_onset?.causal_prefix_receipt_law ?? null,
          maximum_consumed_timestamp_epoch: candidateLeg.v52_onset?.maximum_consumed_timestamp_epoch ?? null,
          right_edge_consumed: candidateLeg.v52_onset?.right_edge_consumed ?? null,
          full_span_fit: candidateLeg.v52_onset?.full_span_fit ?? null,
        };
      });
    }).sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_identity.localeCompare(b.leg_identity)) : [];
    const onsetTimingShiftReceipt = isV52l ? {
      rows: onsetTimingRows,
      distribution_new_minus_old_seconds: distribution(onsetTimingRows.map((row) => row.new_minus_old_seconds)),
      old_present_new_absent: onsetTimingRows.filter((row) => row.old_present_new_absent).length,
      old_absent_new_present: onsetTimingRows.filter((row) => row.old_absent_new_present).length,
      both_present: onsetTimingRows.filter((row) => Number.isFinite(row.old_onset?.timestamp_epoch) && Number.isFinite(row.new_onset?.timestamp_epoch)).length,
      conservation: { expected_legs: 60, rows: onsetTimingRows.length, pass: onsetTimingRows.length === 60 },
    } : null;
    const rightEdgeIndependenceReceipt = isV52CausalOnset ? {
      law: "CLAUSE_1_READS_NO_RIGHT_EDGE_AND_NO_FULL_SPAN_FIT; PERTURBING_RIGHT_EDGE_BY_PLUS_OR_MINUS_86400_SECONDS_MUST_NOT_CHANGE_ANY_ONSET",
      rows: rightEdgeIndependenceRows,
      pass: rightEdgeIndependenceRows.length === 30 && rightEdgeIndependenceRows.every((row) => row.pass && row.identical_onsets),
      conservation: { expected_games: 30, rows: rightEdgeIndependenceRows.length },
    } : null;
    const causalPerGameOutcomeTable = isV52CausalOnset ? reportedCandidateFourStateRows.map((row) => {
      const event = candidateRun.marketEvents.find((item) => item.event_id === row.event_id);
      return {
        event_id: row.event_id,
        category: row.category,
        price_region: row.price_region,
        state: row.state,
        combined_entry_cents: row.combined_entry_cents,
        delta_vs_100_cents: row.delta_vs_100_cents,
        credited_legs: row.credited_legs,
        missing_legs: row.missing_legs,
        offer_margin_cents: Number.isInteger(row.offered_floor_sum_cents) ? 100 - row.offered_floor_sum_cents : null,
        offered_floor_sum_cents: row.offered_floor_sum_cents ?? null,
        window_scoring_class: row.window_binding?.scoring_class ?? null,
        window_scoring_eligible: row.window_binding?.scoring_eligible ?? null,
        leg_onsets: Object.fromEntries(Object.entries(event.legs).sort(([a], [b]) => a.localeCompare(b)).map(([legId, leg]) => [legId, { leg_identity: leg.leg_identity, selected: leg.v52_onset?.selected ?? null, right_edge_consumed: leg.v52_onset?.right_edge_consumed ?? null, full_span_fit: leg.v52_onset?.full_span_fit ?? null }])),
        ...(isV52MacroRecognition ? { leg_macro_recognition: Object.fromEntries(Object.entries(event.legs).sort(([a], [b]) => a.localeCompare(b)).map(([legId, leg]) => {
          const recognitionRows = candidateFlow.trace.filter((traceRow) => traceRow.leg_identity === leg.leg_identity && traceRow.macro_recognition && (!Number.isFinite(leg.fill_timestamp_epoch) || traceRow.timestamp_epoch <= leg.fill_timestamp_epoch));
          const last = recognitionRows.at(-1) ?? null;
          return [legId, { leg_identity: leg.leg_identity, credited: leg.credited, entry_cents: leg.entry_cents, fill_timestamp_epoch: leg.fill_timestamp_epoch, ...((isV52o || isV52Ripeness) ? { role_at_entry_or_terminal: isV52Ripeness ? (last?.macro_recognition?.bound_role ?? "ABSTAIN") : (last?.macro_recognition?.role ?? "ABSTAIN"), candidate_role: last?.macro_recognition?.candidate_role ?? null, drift_cents: last?.macro_recognition?.drift_cents ?? null, anchor_correction: last?.macro_recognition?.anchor_correction ?? null, ripeness: last?.macro_recognition?.ripeness ?? null, benchmarked_role_instrument: last?.benchmarked_role_instrument ?? null } : { family_at_entry_or_terminal: last?.macro_recognition?.binding_family ?? last?.macro_recognition?.family ?? null, proposed_family: last?.macro_recognition?.proposed_family ?? last?.macro_recognition?.family ?? null, confidence: last?.macro_recognition?.confidence ?? null, confidence_gate: last?.recognition_confidence_gate ?? null, per_shape_floor_depth: last?.per_shape_floor_depth ?? null }), signable: last?.macro_recognition?.signable ?? false, receipt: last?.receipt ?? null }];
        })) } : {}),
      };
    }).sort((a, b) => a.event_id.localeCompare(b.event_id)) : null;
    const pairBudgetRecords = (isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ? candidateRun.marketEvents.map((event) => event.pair_budget_record) : [];
    const pairBudgetRecordSummary = (isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ? {
      records: pairBudgetRecords.length,
      born_records: pairBudgetRecords.filter((record) => record?.born_at).length,
      unborn_records: pairBudgetRecords.filter((record) => !record?.born_at).length,
      revision_rows: pairBudgetRecords.reduce((sum, record) => sum + (record?.revisions?.length ?? 0), 0),
      joint_sum_violations: pairBudgetRecords.flatMap((record) => (record?.revisions ?? []).filter((revision) => Number.isInteger(revision.joint_target_sum_cents) && revision.joint_target_sum_cents > 99).map((revision) => `${record.event_id}@${revision.receipt}`)),
      incomplete_revision_chains: pairBudgetRecords.filter((record) => !record || !Array.isArray(record.revisions) || record.revisions.some((revision, index) => revision.revision !== index + 1 || revision.current_joint_split?.length !== 2)).map((record) => record?.event_id ?? "MISSING_RECORD"),
      forbidden_plan_fields: pairBudgetRecords.filter((record) => ["goals", "predictions", "plan"].some((key) => Object.prototype.hasOwnProperty.call(record ?? {}, key))).map((record) => record.event_id),
      exactly_one_record_per_game: pairBudgetRecords.length === 30 && pairBudgetRecords.every(Boolean),
      pass: pairBudgetRecords.length === 30 && pairBudgetRecords.every(Boolean) && pairBudgetRecords.every((record) => Array.isArray(record.revisions)) && pairBudgetRecords.flatMap((record) => record.revisions).every((revision) => revision.joint_identity_pass),
      minimal_object_law: "ONE_RECORD_PER_GAME; BORN_AT_FIRST_LICENSED_POST; CURRENT_JOINT_SPLIT_AND_COMPLETE_LICENSED_REVISION_HISTORY_ONLY; NO_GOALS_OR_PREDICTIONS",
    } : null;
    const frozenV52fClaimReceipt = isV52g ? JSON.parse(gitShow(V52F_COMMIT, ".claude/window1_live_v4_replay/v52f_pair_entry_conservation_20260813/PRE_STATED_CLAIM_RECEIPT.json")) : null;
    const v52gPriorLossReattestation = isV52g ? {
      source: { commit: V52F_COMMIT, path: ".claude/window1_live_v4_replay/v52f_pair_entry_conservation_20260813/PRE_STATED_CLAIM_RECEIPT.json" },
      named_cases: frozenV52fClaimReceipt.named_cases.map((row) => ({ code: row.code, V52f_candidate_state: row.candidate.state, V52f_candidate_combined_entry_cents: row.candidate.combined_entry_cents, remains_lawful_under_V52g_identity: row.candidate.state !== "COMPLETE_AT_LOSS" && (!Number.isInteger(row.candidate.combined_entry_cents) || row.candidate.combined_entry_cents <= 99) })),
      replay_scope_note: "The fresh V52g cohort excludes every V52f fresh event. These four identities are therefore re-attested from the frozen V52f receipt plus V52g's universal <=99 invariant, not reinserted into the fresh cohort.",
      all_four_remain_lawful: frozenV52fClaimReceipt.named_cases.length === 4 && frozenV52fClaimReceipt.named_cases.every((row) => row.candidate.state !== "COMPLETE_AT_LOSS" && (!Number.isInteger(row.candidate.combined_entry_cents) || row.candidate.combined_entry_cents <= 99)),
      zero_new_COMPLETE_AT_LOSS_in_fresh_30: candidateFourStateRows.every((row) => row.state !== "COMPLETE_AT_LOSS"),
    } : null;
    if (v52gPriorLossReattestation) v52gPriorLossReattestation.pass = v52gPriorLossReattestation.all_four_remain_lawful && v52gPriorLossReattestation.zero_new_COMPLETE_AT_LOSS_in_fresh_30;
    const v52fClaimRows = isV52f ? activeReadCohort.pre_stated_claim_cases.map((claim) => {
      const before = baselineFourStateRows.find((row) => row.event_id === claim.event_id), after = candidateFourStateRows.find((row) => row.event_id === claim.event_id);
      ensure(before && after, `V52f claim outcome missing ${claim.event_id}`);
      return { code: claim.code, event_id: claim.event_id, baseline: before, candidate: after, converted_from_COMPLETE_AT_LOSS_to_lawful_outcome: before.state === "COMPLETE_AT_LOSS" && after.state !== "COMPLETE_AT_LOSS" };
    }) : [];
    const v52fPreStatedClaim = isV52f ? {
      named_cases: v52fClaimRows,
      all_four_convert_from_COMPLETE_AT_LOSS: v52fClaimRows.length === 4 && v52fClaimRows.every((row) => row.converted_from_COMPLETE_AT_LOSS_to_lawful_outcome),
      zero_new_COMPLETE_AT_LOSS: candidateFourStateRows.every((row) => row.state !== "COMPLETE_AT_LOSS"),
    } : null;
    if (v52fPreStatedClaim) v52fPreStatedClaim.pass = v52fPreStatedClaim.all_four_convert_from_COMPLETE_AT_LOSS && v52fPreStatedClaim.zero_new_COMPLETE_AT_LOSS;
    const pinComparisons = isV52e ? activeReadCohort.pins.map((pin) => {
      const before = baselineRun.marketEvents.find((event) => event.event_id === pin.event_id);
      const after = candidateRun.marketEvents.find((event) => event.event_id === pin.event_id);
      ensure(before && after, `pin missing ${pin.event_id}`);
      const legRows = Object.keys(before.legs).sort().map((legId) => ({
        leg_id: legId,
        baseline_credited: before.legs[legId].credited,
        candidate_credited: after.legs[legId].credited,
        baseline_entry_cents: before.legs[legId].entry_cents,
        candidate_entry_cents: after.legs[legId].entry_cents,
        unharmed: !before.legs[legId].credited || after.legs[legId].credited,
      }));
      return { code: pin.code, event_id: pin.event_id, baseline_completed: before.completed_pair, baseline_combined_entry_cents: before.combined_entry_cents, candidate_completed: after.completed_pair, candidate_combined_entry_cents: after.combined_entry_cents, at_or_better: before.completed_pair && after.completed_pair ? after.combined_entry_cents <= before.combined_entry_cents : !before.completed_pair || after.completed_pair, legs: legRows, unharmed: (!before.completed_pair || after.completed_pair) && legRows.every((row) => row.unharmed) };
    }) : [];
    const sandanPin = (isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ? pinComparisons.find((row) => row.code === "26JUL13SANDAN") : null;
    const smiilaNamedRoot = path.join(repo, ".claude/window1_live_v4_replay/v52h_smiila_named_observation_20260813");
    const smiilaObservation = isV52h ? JSON.parse(fs.readFileSync(path.join(smiilaNamedRoot, "SMIILA_NAMED_OBSERVATION.json"), "utf8")) : null;
    const guegomNamedRoot = path.join(repo, isV52k ? ".claude/window1_live_v4_replay/v52k_guegom_named_observation_20260814" : ".claude/window1_live_v4_replay/v52j_guegom_named_observation_20260813");
    const guegomObservation = (isV52j || isV52k) ? JSON.parse(fs.readFileSync(path.join(guegomNamedRoot, "GUEGOM_NAMED_OBSERVATION.json"), "utf8")) : null;
    const newOneSidedExposureRows = (isV52h || isV52DepthValidation || isV52CausalOnset) ? candidateFourStateRows.filter((row) => row.state === "PARTIAL_FOR_REASON").flatMap((row) => {
      const before = baselineFourStateRows.find((item) => item.event_id === row.event_id);
      const beforeIds = (before?.credited_legs ?? []).map((leg) => leg.leg_identity).sort().join("|");
      const afterIds = row.credited_legs.map((leg) => leg.leg_identity).sort().join("|");
      if (before?.state === "PARTIAL_FOR_REASON" && beforeIds === afterIds) return [];
      const event = candidateRun.marketEvents.find((item) => item.event_id === row.event_id);
      const credited = Object.values(event.legs).find((leg) => leg.credited), missing = Object.values(event.legs).find((leg) => !leg.credited);
      const edge = baseByEvent.get(row.event_id).right;
      return [{ event_id: row.event_id, category: row.category, price_region: row.price_region, baseline_state: before?.state ?? null, credited_leg: credited.leg_identity, credited_entry_cents: credited.entry_cents, credited_timestamp_epoch: credited.fill_timestamp_epoch, missing_leg: missing.leg_identity, missing_terminal_reason: missing.terminal_reason, exposure_to_window_edge_seconds: Number.isFinite(credited.fill_timestamp_epoch) ? edge - credited.fill_timestamp_epoch : null, second_side_never_kissed: true }];
    }) : [];
    const frozenV52hOneSided = isV52DepthValidation ? JSON.parse(gitShow(V52H_COMMIT, ".claude/window1_live_v4_replay/v52h_remove_pair_lows_precondition_20260813/NEW_ONE_SIDED_EXPOSURE_RECEIPT.json")) : null;
    const oneSidedExposureSummary = (isV52h || isV52DepthValidation || isV52CausalOnset) ? {
      newly_created_partials: newOneSidedExposureRows.length,
      duration_seconds: distribution(newOneSidedExposureRows.map((row) => row.exposure_to_window_edge_seconds)),
      rows: newOneSidedExposureRows,
      ...(isV52DepthValidation ? { V52h_baseline: { newly_created_partials: frozenV52hOneSided.newly_created_partials, duration_seconds: frozenV52hOneSided.duration_seconds }, requested_baseline_count_six: frozenV52hOneSided.newly_created_partials === 6 } : {}),
    } : null;
    const macroRecognitionSummary = isV52MacroRecognition ? (() => {
      const evaluationRows = candidateFlow.trace.filter((row) => row.macro_recognition);
      const recognizedRows = candidateFlow.trace.filter((row) => row.macro_recognition?.family);
      const consumedRows = candidateFlow.trace.filter((row) => row.per_shape_floor_depth?.applicable === true);
      const changedRows = consumedRows.filter((row) => row.per_shape_floor_depth.target_changed === true);
      const candidateLegByIdentity = new Map(candidateRun.marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
      const baselineLegByIdentity = new Map(baselineRun.marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
      const groundByLeg = new Map(reportedCandidateFourStateRows.flatMap((event) => event.credited_legs.concat(event.missing_legs).map((leg) => [leg.leg_identity, leg.ground_truth_floor_cents])));
      const traceByLeg = new Map();
      for (const row of recognizedRows) { if (!traceByLeg.has(row.leg_identity)) traceByLeg.set(row.leg_identity, []); traceByLeg.get(row.leg_identity).push(row); }
      const recognitionAt = (legIdentity, timestamp) => (traceByLeg.get(legIdentity) ?? []).filter((row) => !Number.isFinite(timestamp) || row.timestamp_epoch <= timestamp).at(-1) ?? null;
      const terminalClassifications = [...candidateLegByIdentity.entries()].map(([legIdentity, leg]) => {
        const row = recognitionAt(legIdentity, leg.fill_timestamp_epoch);
        return { leg_identity: legIdentity, family: row?.macro_recognition?.family ?? null, proposed_family: row?.macro_recognition?.proposed_family ?? row?.macro_recognition?.family ?? null, binding_family: row?.macro_recognition?.binding_family ?? (row?.macro_recognition?.signable ? row?.macro_recognition?.family : null), confidence: row?.macro_recognition?.confidence ?? null, signable: row?.macro_recognition?.signable ?? false, status: row?.macro_recognition?.status ?? "NO_CLASSIFICATION_RECEIPT", confidence_gate: row?.recognition_confidence_gate ?? row?.macro_recognition?.recognition_confidence_gate ?? null, receipt: row?.receipt ?? null, timestamp_epoch: row?.timestamp_epoch ?? null };
      });
      const taxonomyCounts = v52mShapeBinding.taxonomy.families;
      const taxonomyTotal = Object.values(taxonomyCounts).reduce((sum, value) => sum + value, 0);
      const observedCounts = countBy(terminalClassifications.filter((row) => (isV52n ? row.binding_family : row.family)), (row) => isV52n ? row.binding_family : row.family);
      const proposedCounts = countBy(terminalClassifications.filter((row) => row.proposed_family), (row) => row.proposed_family);
      const frequencyComparison = policy.FAMILY_ORDER.map((family) => ({
        family,
        taxonomy_legs: taxonomyCounts[family] ?? 0,
        taxonomy_share: taxonomyTotal ? (taxonomyCounts[family] ?? 0) / taxonomyTotal : null,
        cohort_terminal_legs: observedCounts[family] ?? 0,
        cohort_terminal_share: terminalClassifications.length ? (observedCounts[family] ?? 0) / terminalClassifications.length : null,
        absolute_share_difference: taxonomyTotal && terminalClassifications.length ? Math.abs((taxonomyCounts[family] ?? 0) / taxonomyTotal - (observedCounts[family] ?? 0) / terminalClassifications.length) : null,
      }));
      const familyForLeg = new Map(terminalClassifications.map((row) => [row.leg_identity, row.proposed_family]));
      const fillRows = [...candidateLegByIdentity.entries()].filter(([, leg]) => leg.credited).map(([legIdentity, candidateLeg]) => {
        const baselineLeg = baselineLegByIdentity.get(legIdentity);
        const fillRecognition = recognitionAt(legIdentity, candidateLeg.fill_timestamp_epoch)?.macro_recognition ?? null;
        const family = isV52n ? (fillRecognition?.binding_family ?? null) : (fillRecognition?.family ?? familyForLeg.get(legIdentity) ?? null);
        const floor = groundByLeg.get(legIdentity);
        return {
          leg_identity: legIdentity,
          family,
          baseline_credited: baselineLeg?.credited ?? false,
          baseline_entry_cents: baselineLeg?.entry_cents ?? null,
          baseline_fill_timestamp_epoch: baselineLeg?.fill_timestamp_epoch ?? null,
          candidate_entry_cents: candidateLeg.entry_cents,
          candidate_fill_timestamp_epoch: candidateLeg.fill_timestamp_epoch,
          candidate_minus_baseline_fill_seconds: Number.isFinite(baselineLeg?.fill_timestamp_epoch) ? candidateLeg.fill_timestamp_epoch - baselineLeg.fill_timestamp_epoch : null,
          ground_truth_floor_cents: floor ?? null,
          baseline_entry_minus_floor_cents: baselineLeg?.credited && Number.isInteger(floor) ? baselineLeg.entry_cents - floor : null,
          candidate_entry_minus_floor_cents: Number.isInteger(floor) ? candidateLeg.entry_cents - floor : null,
        };
      });
      const downFills = fillRows.filter((row) => row.family?.endsWith("_DOWN"));
      const comparableDown = downFills.filter((row) => row.baseline_credited && Number.isInteger(row.ground_truth_floor_cents));
      const upStillFamilies = new Set(policy.FAMILY_ORDER.filter((family) => family.endsWith("_UP") || ["SLEEPER", "ROUND_TRIP", "QUIET_WOBBLE"].includes(family)));
      const v52lRun = isV52n ? machineRuns.get("V52L_FROZEN_BASELINE") : baselineRun;
      const v52lLegByIdentity = new Map(v52lRun.marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
      const preservationRows = [...v52lLegByIdentity.entries()].filter(([legIdentity, leg]) => leg.credited && upStillFamilies.has(familyForLeg.get(legIdentity))).map(([legIdentity, v52lLeg]) => ({ leg_identity: legIdentity, family: familyForLeg.get(legIdentity), V52l_entry_cents: v52lLeg.entry_cents, V52m_credited: baselineLegByIdentity.get(legIdentity)?.credited ?? false, V52m_entry_cents: baselineLegByIdentity.get(legIdentity)?.entry_cents ?? null, candidate_credited: candidateLegByIdentity.get(legIdentity)?.credited ?? false, candidate_entry_cents: candidateLegByIdentity.get(legIdentity)?.entry_cents ?? null }));
      const eligibleLocked = (rows) => rows.filter((row) => row.window_binding?.scoring_eligible && row.state === "COMPLETE_AT_DELTA").map((row) => 100 - row.combined_entry_cents);
      const beforeLocked = eligibleLocked(reportedBaselineFourStateRows), afterLocked = eligibleLocked(reportedCandidateFourStateRows);
      const baselinePartial = new Map(baselineFourStateRows.filter((row) => row.state === "PARTIAL_FOR_REASON").map((row) => [row.event_id, row]));
      const candidatePartial = new Map(candidateFourStateRows.filter((row) => row.state === "PARTIAL_FOR_REASON").map((row) => [row.event_id, row]));
      const created = [...candidatePartial].filter(([eventId]) => !baselinePartial.has(eventId)).map(([eventId, row]) => ({ event_id: eventId, direction: `CREATED_BY_${isV52n ? "V52N" : "V52M"}`, credited_legs: row.credited_legs, exposure_to_window_edge_seconds: oneSidedExposureSummary.rows.find((item) => item.event_id === eventId)?.exposure_to_window_edge_seconds ?? null }));
      const resolved = [...baselinePartial].filter(([eventId]) => !candidatePartial.has(eventId)).map(([eventId, row]) => ({ event_id: eventId, direction: `RESOLVED_BY_${isV52n ? "V52N" : "V52M"}`, baseline_credited_legs: row.credited_legs, candidate_state: candidateFourStateRows.find((item) => item.event_id === eventId)?.state ?? null }));
      const downBeforeGap = distribution(comparableDown.map((row) => row.baseline_entry_minus_floor_cents));
      const downAfterGap = distribution(comparableDown.map((row) => row.candidate_entry_minus_floor_cents));
      const fillDelay = distribution(comparableDown.map((row) => row.candidate_minus_baseline_fill_seconds));
      return {
        provenance: { taxonomy: v52mShapeBinding.taxonomy_provenance, floor_depth_table: v52mShapeBinding.floor_table_provenance },
        causal_law: "EVERY_SIGNATURE_USES_ONLY_TRUE_PRINTS_AT_OR_BEFORE_THE_EVALUATION_RECEIPT; RIGHT_EDGE_AND_COMPLETED_PATH_ARE_NOT_INPUTS",
        classifications: { evaluation_receipt_rows: evaluationRows.length, classified_receipt_rows: recognizedRows.length, receipt_rows: recognizedRows.length, receipt_rows_legacy_alias: "classified_receipt_rows", terminal_leg_rows: terminalClassifications.length, signable_terminal_legs: terminalClassifications.filter((row) => row.signable).length, abstain_terminal_legs: terminalClassifications.filter((row) => !row.signable).length, receipt_frequency: countBy(recognizedRows, (row) => isV52n ? (row.macro_recognition.binding_family ?? "ABSTAIN") : row.macro_recognition.family), proposed_receipt_frequency: countBy(recognizedRows, (row) => row.macro_recognition.proposed_family ?? row.macro_recognition.family), terminal_frequency: observedCounts, proposed_terminal_frequency: proposedCounts, frequency_comparison: frequencyComparison, sleeper_bound_share: terminalClassifications.length ? (observedCounts.SLEEPER ?? 0) / terminalClassifications.length : null, broad_match_adjudication: "REPORTED_NOT_FORCED; NO NUMERIC DISTANCE BAR INVENTED" },
        consumption: { applicable_receipts: consumedRows.length, changed_target_receipts: changedRows.length, legs: new Set(consumedRows.map((row) => row.leg_identity)).size, games: new Set(consumedRows.map((row) => row.event_id)).size, abstain_class_behavior: "FROZEN_V52L_UNCHANGED" },
        down_family_fills: { rows: downFills, comparable_rows: comparableDown.length, [`fill_delay_seconds_vs_${isV52n ? "V52m" : "V52l"}`]: fillDelay, [`${isV52n ? "V52m" : "V52l"}_entry_minus_ground_truth_floor_cents`]: downBeforeGap, [`${isV52n ? "V52n" : "V52m"}_entry_minus_ground_truth_floor_cents`]: downAfterGap, retained_at_or_near_one_cent: downAfterGap.n > 0 && downAfterGap.median <= 1, moved_later: fillDelay.n > 0 && fillDelay.median > 0, landed_nearer_true_floor: downBeforeGap.n > 0 && downAfterGap.n > 0 && downAfterGap.median < downBeforeGap.median },
        up_and_still_preservation: { V52l_credited_legs: preservationRows.length, V52m_credited_legs: preservationRows.filter((row) => row.V52m_credited).length, candidate_credited_legs: preservationRows.filter((row) => row.candidate_credited).length, lost_vs_V52l: preservationRows.filter((row) => !row.candidate_credited), restored_from_V52m: preservationRows.filter((row) => row.candidate_credited && !row.V52m_credited), preserved: preservationRows.every((row) => row.candidate_credited) },
        banked_delta: { baseline: { n: beforeLocked.length, mean_cents: beforeLocked.length ? beforeLocked.reduce((sum, value) => sum + value, 0) / beforeLocked.length : null }, candidate: { n: afterLocked.length, mean_cents: afterLocked.length ? afterLocked.reduce((sum, value) => sum + value, 0) / afterLocked.length : null }, rises: beforeLocked.length > 0 && afterLocked.length > 0 && afterLocked.reduce((sum, value) => sum + value, 0) / afterLocked.length > beforeLocked.reduce((sum, value) => sum + value, 0) / beforeLocked.length, at_or_above: beforeLocked.length > 0 && afterLocked.length > 0 && afterLocked.reduce((sum, value) => sum + value, 0) / afterLocked.length >= beforeLocked.reduce((sum, value) => sum + value, 0) / beforeLocked.length },
        one_sided_exposure_both_ways: { created_count: created.length, resolved_count: resolved.length, created, resolved },
        pins: { lawful: null, comparisons: pinComparisons },
        REFLEX_POST_zero: null,
        terminal_classifications: terminalClassifications,
      };
    })() : null;
    const benchmarkRoleSummary = (isV52o || isV52Ripeness || isV52r) ? (() => {
      // The detailed V52r license remains in the streamed full trace and LOW-1
      // ledger.  Summary JSON carries only scalar receipt facts; embedding the
      // inherited V52l machine-read object at every receipt creates a
      // monolithic >V8-string-limit serialization without adding evidence.
      const compactAssembledPolicy = (value) => value ? {
        applicable: value.applicable,
        reason: value.reason,
        level_policy: value.level_policy,
        level_policy_consumed: value.level_policy_consumed,
        session_low_cents: value.session_low_cents ?? null,
        session_low_receipt: value.session_low_receipt ?? null,
        delta_cents: value.delta_cents ?? null,
        arithmetic: value.arithmetic ?? null,
        current_touch_ask_cents: value.current_touch_ask_cents ?? null,
        clause_6_cap_cents: value.clause_6_cap_cents ?? null,
        selected_target_cents: value.selected_target_cents ?? null,
        target_changed: value.target_changed,
        low1_identity: value.low1_identity ?? null,
        provenance: value.provenance ?? null,
      } : null;
      const parsed = parseCsv(v52oTaxonomyCsvBytes.toString("utf8"));
      const ix = Object.fromEntries(parsed.header.map((value, index) => [value, index]));
      const truthRows = parsed.rows.map((values) => Object.fromEntries(parsed.header.map((name, index) => [name, values[index]])));
      const truthByIdentity = new Map(truthRows.map((row) => [`${row.code}|${row.leg}`, row]));
      const candidateLegByIdentity = new Map(candidateRun.marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
      const baselineLegByIdentity = new Map(baselineRun.marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
      const v52lRoleRun = (isV52q || isV52r) ? machineRuns.get("V52L_FROZEN_BASELINE") : baselineRun;
      const v52lLegByIdentity = new Map(v52lRoleRun.marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
      const groundFloorByIdentity = new Map(reportedCandidateFourStateRows.flatMap((event) => event.credited_legs.concat(event.missing_legs).map((leg) => [leg.leg_identity, leg.ground_truth_floor_cents])));
      const traceByLeg = new Map();
      for (const row of candidateFlow.trace.filter((row) => row.macro_recognition)) {
        if (!traceByLeg.has(row.leg_identity)) traceByLeg.set(row.leg_identity, []);
        traceByLeg.get(row.leg_identity).push(row);
      }
      const recognitionAt = (legIdentity, timestamp) => (traceByLeg.get(legIdentity) ?? []).filter((row) => !Number.isFinite(timestamp) || row.timestamp_epoch <= timestamp).at(-1) ?? null;
      const terminalRows = [...candidateLegByIdentity.entries()].map(([legIdentity, leg]) => {
        const row = recognitionAt(legIdentity, leg.fill_timestamp_epoch);
        const code = legIdentity.split("|")[0].match(/26JUL\d{2}[A-Z]+/)?.[0] ?? null;
        const legId = legIdentity.split("|").at(-1);
        const truth = truthByIdentity.get(`${code}|${legId}`) ?? null;
        const expected = truth?.family_CANDIDATE?.endsWith("_UP")
          ? "ROLE_UP"
          : truth?.family_CANDIDATE?.endsWith("_DOWN")
            ? "ROLE_DOWN"
            : truth?.family_CANDIDATE
              ? "ROLE_STILL"
              : null;
        return {
          event_id: legIdentity.split("|")[0], leg_identity: legIdentity, category: truth?.cat ?? null, price_region: truth?.open_band ?? null,
          role: (isV52Ripeness || isV52r) ? (row?.macro_recognition?.bound_role ?? "ABSTAIN") : (row?.macro_recognition?.role ?? "ABSTAIN"), candidate_role: row?.macro_recognition?.candidate_role ?? null, ripeness: row?.macro_recognition?.ripeness ?? null, trd5: row?.macro_recognition?.trd5 ?? null, drift_cents: row?.macro_recognition?.drift_cents ?? null, anchor_correction: row?.macro_recognition?.anchor_correction ?? null,
          post_formation_open_cents: row?.macro_recognition?.post_formation_open_cents ?? null, last_causal_print_cents: row?.macro_recognition?.last_causal_print_cents ?? null,
          evaluation_timestamp_epoch: row?.timestamp_epoch ?? null, evaluation_receipt: row?.receipt ?? null,
          expected_verified_role: expected, verified_family: truth?.family_CANDIDATE ?? null,
          called: (isV52Ripeness || isV52r) ? row?.macro_recognition?.bound_role != null : ["ROLE_DOWN", "ROLE_UP"].includes(row?.macro_recognition?.role), correct: expected ? ((isV52Ripeness || isV52r) ? row?.macro_recognition?.bound_role : row?.macro_recognition?.role) === expected : null,
          credited: leg.credited, entry_cents: leg.entry_cents, fill_timestamp_epoch: leg.fill_timestamp_epoch,
          depth_consumption: isV52r ? compactAssembledPolicy(row?.assembled_policy) : row?.benchmarked_role_instrument ?? null,
        };
      }).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity));
      const truthEligible = terminalRows.filter((row) => row.expected_verified_role);
      const calledTruth = truthEligible.filter((row) => row.called);
      const calledAll = terminalRows.filter((row) => row.called);
      const downFillRows = terminalRows.filter((row) => row.role === "ROLE_DOWN" && row.credited).map((row) => {
        const baseline = v52lLegByIdentity.get(row.leg_identity);
        const floor = groundFloorByIdentity.get(row.leg_identity);
        return { ...row, ground_truth_floor_cents: floor ?? null, entry_minus_ground_truth_floor_cents: Number.isInteger(floor) ? row.entry_cents - floor : null, V52l_credited: baseline?.credited ?? false, V52l_entry_cents: baseline?.entry_cents ?? null, V52l_entry_minus_ground_truth_floor_cents: baseline?.credited && Number.isInteger(floor) ? baseline.entry_cents - floor : null, fill_delay_seconds_vs_V52l: Number.isFinite(baseline?.fill_timestamp_epoch) ? row.fill_timestamp_epoch - baseline.fill_timestamp_epoch : null };
      });
      const upStillTruth = terminalRows.filter((row) => row.verified_family && !row.verified_family.endsWith("_DOWN"));
      const preservedUniverse = upStillTruth.filter((row) => v52lLegByIdentity.get(row.leg_identity)?.credited);
      const locked = (rows) => rows.filter((row) => row.window_binding?.scoring_eligible && row.state === "COMPLETE_AT_DELTA").map((row) => 100 - row.combined_entry_cents);
      const v52lReportedRows = (isV52q || isV52r) ? groundBoundFourStateRowsFor(v52lRoleRun.marketEvents) : reportedBaselineFourStateRows;
      const baselineLocked = locked(v52lReportedRows), candidateLocked = locked(reportedCandidateFourStateRows);
      const baselinePartials = new Map(baselineFourStateRows.filter((row) => row.state === "PARTIAL_FOR_REASON").map((row) => [row.event_id, row]));
      const candidatePartials = new Map(candidateFourStateRows.filter((row) => row.state === "PARTIAL_FOR_REASON").map((row) => [row.event_id, row]));
      const created = [...candidatePartials].filter(([eventId]) => !baselinePartials.has(eventId)).map(([eventId, row]) => ({ event_id: eventId, credited_legs: row.credited_legs, exposure_to_window_edge_seconds: oneSidedExposureSummary?.rows?.find((item) => item.event_id === eventId)?.exposure_to_window_edge_seconds ?? null }));
      const resolved = [...baselinePartials].filter(([eventId]) => !candidatePartials.has(eventId)).map(([eventId, row]) => ({ event_id: eventId, baseline_credited_legs: row.credited_legs, candidate_state: candidateFourStateRows.find((item) => item.event_id === eventId)?.state ?? null }));
      const roleReceiptRows = candidateFlow.trace.filter((row) => row.macro_recognition).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, category: row.category, price_region: row.price_region, timestamp_epoch: row.timestamp_epoch, t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds, receipt: row.receipt, role: (isV52Ripeness || isV52r) ? (row.macro_recognition.bound_role ?? "ABSTAIN") : row.macro_recognition.role, candidate_role: row.macro_recognition.candidate_role ?? null, ripeness: row.macro_recognition.ripeness ?? null, trd5: row.macro_recognition.trd5 ?? null, drift_cents: row.macro_recognition.drift_cents, post_formation_open_cents: row.macro_recognition.post_formation_open_cents, last_causal_print_cents: row.macro_recognition.last_causal_print_cents, anchor_correction: row.macro_recognition.anchor_correction ?? null, rule: row.macro_recognition.rule, depth_row_consumed: row.benchmarked_role_instrument?.down_depth_row_consumed ?? null, assembled_policy: isV52r ? compactAssembledPolicy(row.assembled_policy) : null, level_policy: isV52r ? row.assembled_policy?.level_policy ?? null : row.benchmarked_role_instrument?.level_policy ?? null, level_policy_consumed: isV52r ? row.assembled_policy?.level_policy_consumed ?? false : row.benchmarked_role_instrument?.level_policy_consumed ?? false, final_target_cents: row.final_target_cents, final_action: row.final_action }));
      const ungatedParityRows = (isV52q || isV52r) ? roleReceiptRows.filter((row) => Number.isInteger(row.post_formation_open_cents) && Number.isInteger(row.last_causal_print_cents) && row.candidate_role).map((row) => {
        const offlineDrift = row.last_causal_print_cents - row.post_formation_open_cents;
        const offlineRole = offlineDrift >= 2 ? "ROLE_UP" : offlineDrift <= -2 ? "ROLE_DOWN" : "ROLE_STILL";
        return { event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, anchor_cents: row.post_formation_open_cents, last_causal_print_cents: row.last_causal_print_cents, runtime_drift_cents: row.drift_cents, offline_drift_cents: offlineDrift, runtime_candidate_role: row.candidate_role, offline_candidate_role: offlineRole, parity: row.drift_cents === offlineDrift && row.candidate_role === offlineRole };
      }) : [];
      return {
        rule_binding: isV52r ? { rule: policy.recognitionReceipt(), recognition: v52rTRD5Binding.provenance, down_target: v52rLOW1Binding.provenance, anchor_correction: v52qAnchorBinding, threshold_source: "TRD5_OPERATOR_PICK_FROM_SEALED_FRONTIER", delta_source: "LOW_1_OPERATOR_PICK_FROM_DOWN_TARGET_FRONTIER_AND_INTEGER_TRAIL1_IDENTITY", new_constants: 0 } : { rule: policy.benchmarkRuleReceipt(), source_commit: SHAPE_TAXONOMY_COMMIT, source_path: SHAPE_TAXONOMY_PATH, source_csv_path: SHAPE_TAXONOMY_CSV_PATH, source_csv_sha256: shaBytes(v52oTaxonomyCsvBytes), exact_literal_reinterpreted: false, new_constants: 0, ...(isV52Ripeness ? { ripeness: v52pRipenessBinding.provenance, class_gates: policy.CLASS_GATES, category_gates: policy.CATEGORY_GATES, effective_gate_law: "max(candidate_role_class_gate, category_gate)" } : {}), ...(isV52q ? { anchor_correction: v52qAnchorBinding } : {}) },
        down_depth_aggregate_derivation: isV52r ? [{ rule: "LOW-1", expression: "running_post_onset_session_low-1c", delta_cents: 1, provenance: v52rLOW1Binding.provenance, static_shape_aggregate_consumed: false }] : ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"].map((category) => policy.downDepthAggregate(category)),
        terminal_roles: terminalRows,
        role_receipt_count: roleReceiptRows.length,
        coverage: { terminal_grain: "LAST_DECISION_RECEIPT_BEFORE_ENTRY_OR_AVAILABLE_REPLAY_TERMINAL", terminal_legs: terminalRows.length, called_all_legs: calledAll.length, called_all_legs_share: terminalRows.length ? calledAll.length / terminalRows.length : null, benchmark_truth_role_legs: truthEligible.length, called_truth_role_legs: calledTruth.length, called_truth_role_legs_share: truthEligible.length ? calledTruth.length / truthEligible.length : null, benchmark_reference_called_coverage: isV52r ? 0.924 : 0.84, target_band: isV52r ? [0.85, 1.0] : isV52Ripeness ? [0.60, 1.0] : [0.70, 0.90], lands_in_target_band: truthEligible.length > 0 && calledTruth.length / truthEligible.length >= (isV52r ? 0.85 : isV52Ripeness ? 0.60 : 0.70) && calledTruth.length / truthEligible.length <= (isV52r || isV52Ripeness ? 1.0 : 0.90) },
        accuracy: { called_truth_role_legs: calledTruth.length, correct: calledTruth.filter((row) => row.correct).length, accuracy: calledTruth.length ? calledTruth.filter((row) => row.correct).length / calledTruth.length : null, benchmark_reference_accuracy: 0.951, target_near_benchmark_reported_not_forced: true },
        ...((isV52q || isV52r) ? { runtime_vs_offline_parity: { grain: "UNGATED_ROLE_EVALUATION_RECEIPTS_WITH_PUBLISHED_ANCHOR_AND_POST_FORMATION_PRINT", rows: ungatedParityRows.length, matching: ungatedParityRows.filter((row) => row.parity).length, parity: ungatedParityRows.length ? ungatedParityRows.filter((row) => row.parity).length / ungatedParityRows.length : null, claim_at_least_99pct: ungatedParityRows.length > 0 && ungatedParityRows.filter((row) => row.parity).length / ungatedParityRows.length >= 0.99, mismatches: ungatedParityRows.filter((row) => !row.parity) } } : {}),
        ROLE_DOWN_fills: { rows: downFillRows, floor_gap_cents: distribution(downFillRows.map((row) => row.entry_minus_ground_truth_floor_cents)), V52l_floor_gap_cents: distribution(downFillRows.map((row) => row.V52l_entry_minus_ground_truth_floor_cents)), fill_delay_seconds_vs_V52l: distribution(downFillRows.map((row) => row.fill_delay_seconds_vs_V52l)), claim_median_gap_at_or_below_1_5c: Number.isFinite(distribution(downFillRows.map((row) => row.entry_minus_ground_truth_floor_cents)).median) && distribution(downFillRows.map((row) => row.entry_minus_ground_truth_floor_cents)).median <= 1.5, claim_median_gap_at_or_below_2c: Number.isFinite(distribution(downFillRows.map((row) => row.entry_minus_ground_truth_floor_cents)).median) && distribution(downFillRows.map((row) => row.entry_minus_ground_truth_floor_cents)).median <= 2, kiss_count: downFillRows.filter((row) => Number.isInteger(row.entry_minus_ground_truth_floor_cents) && row.entry_minus_ground_truth_floor_cents <= 0).length, kiss_share: downFillRows.length ? downFillRows.filter((row) => Number.isInteger(row.entry_minus_ground_truth_floor_cents) && row.entry_minus_ground_truth_floor_cents <= 0).length / downFillRows.length : null },
        up_and_still_completion_preservation: { V52l_credited_legs: preservedUniverse.length, V52o_credited_legs: preservedUniverse.filter((row) => candidateLegByIdentity.get(row.leg_identity)?.credited).length, candidate_credited_legs: preservedUniverse.filter((row) => candidateLegByIdentity.get(row.leg_identity)?.credited).length, lost: preservedUniverse.filter((row) => !candidateLegByIdentity.get(row.leg_identity)?.credited), preserved: preservedUniverse.every((row) => candidateLegByIdentity.get(row.leg_identity)?.credited) },
        banked_delta: { V52l: { n: baselineLocked.length, mean_cents: baselineLocked.length ? baselineLocked.reduce((sum, value) => sum + value, 0) / baselineLocked.length : null }, V52o: { n: candidateLocked.length, mean_cents: candidateLocked.length ? candidateLocked.reduce((sum, value) => sum + value, 0) / candidateLocked.length : null }, candidate: { n: candidateLocked.length, mean_cents: candidateLocked.length ? candidateLocked.reduce((sum, value) => sum + value, 0) / candidateLocked.length : null }, exceeds_V52m_1_83c: candidateLocked.length > 0 && candidateLocked.reduce((sum, value) => sum + value, 0) / candidateLocked.length > 1.83, exceeds_claim_bar_cents: isV52r ? 2.4 : isV52q ? 2.14 : isV52p ? 1.94 : 1.83, exceeds_claim_bar: candidateLocked.length > 0 && candidateLocked.reduce((sum, value) => sum + value, 0) / candidateLocked.length > (isV52r ? 2.4 : isV52q ? 2.14 : isV52p ? 1.94 : 1.83) },
        role_receipts: isV52r ? roleReceiptRows.map((row) => ({ t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds })) : roleReceiptRows,
        ...(isV52r ? {
          role_receipt_ledger: "TRD5_ROLE_BINDING_LEDGER.jsonl.gz",
          role_receipts_streamed_not_embedded: true,
          both_clocks_present_on_role_receipts: roleReceiptRows.every((row) => Object.hasOwn(row, "t_minus_scheduled_seconds") && Object.hasOwn(row, "t_minus_actual_bell_seconds")),
        } : {}),
        one_sided_exposure_both_ways: { created_count: created.length, resolved_count: resolved.length, created_duration_seconds: distribution(created.map((row) => row.exposure_to_window_edge_seconds)), created, resolved },
        pins: { comparisons: pinComparisons, lawful: pinComparisons.every((row) => row.unharmed) },
        REFLEX_POST_zero: null,
      };
    })() : null;
    const ripenessRoleSummary = isV52Ripeness ? (() => {
      const rows = candidateFlow.trace.filter((row) => row.macro_recognition?.ripeness).map((row) => ({
        event_id: row.event_id,
        leg_identity: row.leg_identity,
        category: row.category,
        price_region: row.price_region,
        timestamp_epoch: row.timestamp_epoch,
        receipt: row.receipt,
        candidate_role: row.macro_recognition.candidate_role,
        bound_role: row.macro_recognition.bound_role,
        drift_cents: row.macro_recognition.drift_cents,
        anchor_cents: row.macro_recognition.post_formation_open_cents,
        anchor_method: row.macro_recognition.anchor_correction?.method ?? null,
        anchor_method_sha256: row.macro_recognition.anchor_correction?.method?.sha256 ?? null,
        series_floor: row.macro_recognition.anchor_correction?.series_floor ?? null,
        ...row.macro_recognition.ripeness,
        final_action: row.final_action,
        final_target_cents: row.final_target_cents,
      }));
      const terminal = [...new Set(rows.map((row) => row.leg_identity))].sort().map((legIdentity) => rows.filter((row) => row.leg_identity === legIdentity).at(-1));
      const divergences = rows.filter((row) => row.binding_decision_diverges);
      const verifiedBound = terminal.filter((row) => row.verified_binding);
      const scheduledBound = terminal.filter((row) => row.scheduled_proxy_binding);
      return {
        source: v52pRipenessBinding.provenance,
        arithmetic: { class_gates: policy.CLASS_GATES, category_gates: policy.CATEGORY_GATES, effective_gate: "max(class_gate,category_gate)", verified_f: "(receipt-formation_end)/(verified_bell-formation_end)", scheduled_proxy_f: "(receipt-formation_end)/(scheduled_start-formation_end)" },
        decision_basis: "VERIFIED_PRE_MATCH_SPAN_FOR_THIS_OBSERVATION_ONLY",
        live_proxy: "SCHEDULED_START_SPAN_TELEMETRY_ONLY",
        receipt_rows: rows.length,
        terminal_legs: terminal.length,
        verified_bound_terminal_legs: verifiedBound.length,
        verified_bound_terminal_share: terminal.length ? verifiedBound.length / terminal.length : null,
        scheduled_proxy_bound_terminal_legs: scheduledBound.length,
        scheduled_proxy_bound_terminal_share: terminal.length ? scheduledBound.length / terminal.length : null,
        binding_divergence_receipts: divergences.length,
        binding_divergence_legs: new Set(divergences.map((row) => row.leg_identity)).size,
        binding_divergence_games: new Set(divergences.map((row) => row.event_id)).size,
        divergence_by_category: countBy(divergences, (row) => row.category),
        materiality: divergences.length > 0 ? "MATERIAL_LIVE_FIDELITY_ITEM" : "NO_BINDING_DECISION_DIVERGENCE_OBSERVED",
        terminal_rows: terminal,
        divergence_rows: divergences,
      };
    })() : null;
    const offerCensus = isV52DepthValidation ? JSON.parse(gitShow("22441e05", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/POST_ONSET_OFFER_CENSUS.json")) : null;
    const offerByTicker = isV52DepthValidation ? new Map(offerCensus.rows.flatMap((game) => Object.values(game.legs ?? {}).map((leg) => [`${game.code}|${leg.ticker.split("-").at(-1)}`, { ...leg, game_code: game.code, offer_class: game.cls, offer_margin_cents: game.margin, pair_floor_cents: game.pair_floor_sel }]))) : new Map();
    const entryFloorRowsFor = (run, variantName) => isV52DepthValidation ? run.marketEvents.flatMap((event) => Object.values(event.legs).filter((leg) => leg.credited).map((leg) => {
      const offer = offerByTicker.get(`${event.event_id.split("-").at(-1)}|${leg.leg_identity.split("|").at(-1)}`) ?? null;
      return { variant: variantName, event_id: event.event_id, leg_identity: leg.leg_identity, category: event.category, price_region: leg.price_region, entry_cents: leg.entry_cents, post_onset_offer_floor_cents: offer?.floor_sel ?? null, entry_minus_later_floor_cents: Number.isInteger(offer?.floor_sel) ? leg.entry_cents - offer.floor_sel : null, offer_class: offer?.offer_class ?? null, offer_margin_cents: offer?.offer_margin_cents ?? null };
    })) : [];
    const baselineEntryFloorRows = entryFloorRowsFor(baselineRun, "V52H");
    const candidateEntryFloorRows = entryFloorRowsFor(candidateRun, isV52k ? "V52K" : isV52j ? "V52J" : "V52I");
    const gapSummary = (rows) => ({ credited_legs: rows.length, floor_available: rows.filter((row) => Number.isInteger(row.entry_minus_later_floor_cents)).length, signed_entry_minus_later_floor_cents: distribution(rows.map((row) => row.entry_minus_later_floor_cents)), bought_above_later_floor_only: distribution(rows.filter((row) => row.entry_minus_later_floor_cents > 0).map((row) => row.entry_minus_later_floor_cents)) });
    const entryLaterFloorComparison = isV52DepthValidation ? {
      floor_source: { commit: "22441e05", path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/POST_ONSET_OFFER_CENSUS.json", law: "PER_LEG_POST_ONSET_FLOOR_SEL" },
      baseline: gapSummary(baselineEntryFloorRows), candidate: gapSummary(candidateEntryFloorRows),
      pre_stated_claim: { bought_above_later_floor_depth_shifts_toward_zero: null, adjudication: "OBSERVATION_ONLY; NO_BEHAVIORAL_REPAIR_PERMITTED" },
    } : null;
    if (entryLaterFloorComparison) {
      const before = entryLaterFloorComparison.baseline.bought_above_later_floor_only;
      const after = entryLaterFloorComparison.candidate.bought_above_later_floor_only;
      entryLaterFloorComparison.pre_stated_claim.bought_above_later_floor_depth_shifts_toward_zero = before.n > 0 && after.n > 0 && after.median <= before.median && after.p75 <= before.p75 && (after.median < before.median || after.p75 < before.p75);
    }
    const perGameOutcomeTable = isV52DepthValidation ? candidateRun.marketEvents.map((event) => {
      const outcome = candidateFourStateRows.find((row) => row.event_id === event.event_id);
      const base = baseByEvent.get(event.event_id);
      const firstLeg = Object.values(event.legs)[0];
      const offer = offerByTicker.get(`${event.event_id.split("-").at(-1)}|${firstLeg.leg_identity.split("|").at(-1)}`) ?? null;
      const perLeg = Object.values(event.legs).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)).map((leg) => {
        const legId = leg.leg_identity.split("|").at(-1), meta = base.legs[legId];
        const legOffer = offerByTicker.get(`${event.event_id.split("-").at(-1)}|${legId}`) ?? null;
        const floorRows = Number.isInteger(legOffer?.floor_sel) && Number.isFinite(legOffer?.onset_sel)
          ? (printLoad.byTicker.get(meta.ticker) ?? []).filter((row) => row.ts >= legOffer.onset_sel && row.price === legOffer.floor_sel)
          : [];
        const floorRow = floorRows[0] ?? null;
        const legTrace = candidateFlow.trace.filter((row) => row.leg_identity === leg.leg_identity && (!Number.isFinite(leg.fill_timestamp_epoch) || row.timestamp_epoch <= leg.fill_timestamp_epoch));
        const roleRow = legTrace.filter((row) => row.role_conditioned_level_selection?.role_assignment).at(-1) ?? null;
        const libraryRow = legTrace.filter((row) => row.library_backed_level_evidence).at(-1) ?? null;
        return {
          leg_identity: leg.leg_identity,
          credited: leg.credited,
          entry_cents: leg.entry_cents,
          role_at_entry_or_terminal: roleRow?.role_conditioned_level_selection?.role_assignment?.own_role ?? null,
          role_receipt: roleRow?.receipt ?? null,
          role_read_evidence: roleRow?.role_conditioned_level_selection?.role_assignment?.own_read_evidence ?? null,
          read_state_at_entry_or_terminal: libraryRow?.read?.state ?? legTrace.at(-1)?.read?.state ?? null,
          level_evidence_authority_at_entry_or_terminal: libraryRow?.library_backed_level_evidence?.evidence_authority ?? null,
          library_supported_floor_cents: libraryRow?.library_backed_level_evidence?.library_supported_floor_cents ?? null,
          library_level_below_shown_range: libraryRow?.library_backed_level_evidence?.below_shown_range ?? null,
          library_prior_values: libraryRow?.library_backed_level_evidence?.prior_values ?? null,
          library_prior_provenance: libraryRow?.library_backed_level_evidence?.prior_provenance ?? null,
          library_license_receipt: libraryRow?.receipt ?? null,
          fill_timestamp_epoch: leg.fill_timestamp_epoch,
          fill_clock: Number.isFinite(leg.fill_timestamp_epoch) ? clockFields(leg.fill_timestamp_epoch, base) : null,
          fill_t_minus_scheduled_seconds: Number.isFinite(leg.fill_timestamp_epoch) ? clockFields(leg.fill_timestamp_epoch, base).t_minus_scheduled_seconds : null,
          fill_t_minus_actual_bell_seconds: Number.isFinite(leg.fill_timestamp_epoch) ? clockFields(leg.fill_timestamp_epoch, base).t_minus_actual_bell_seconds : null,
          post_onset_offer_floor_cents: legOffer?.floor_sel ?? null,
          floor_timestamp_epoch: floorRow?.ts ?? null,
          floor_clock: floorRow ? clockFields(floorRow.ts, base) : null,
          floor_t_minus_scheduled_seconds: floorRow ? clockFields(floorRow.ts, base).t_minus_scheduled_seconds : null,
          floor_t_minus_actual_bell_seconds: floorRow ? clockFields(floorRow.ts, base).t_minus_actual_bell_seconds : null,
          entry_minus_later_floor_cents: leg.credited && Number.isInteger(legOffer?.floor_sel) ? leg.entry_cents - legOffer.floor_sel : null,
        };
      });
      return { event_id: event.event_id, category: event.category, price_region: event.starting_price_split, state: outcome.state, combined_entry_cents: event.completed_pair ? event.combined_entry_cents : null, credited_legs: outcome.credited_legs, legs: perLeg, combined_entry_minus_100_cents: event.completed_pair ? event.combined_entry_cents - 100 : null, locked_delta_vs_100_cents: event.completed_pair ? 100 - event.combined_entry_cents : null, offer_class: offer?.offer_class ?? null, offer_margin_cents: offer?.offer_margin_cents ?? null, offer_census_source_commit: OFFER_DENOMINATOR_COMMIT };
    }).sort((a, b) => a.event_id.localeCompare(b.event_id)) : null;
    const roleConditionedSummary = isV52j ? (() => {
      const roleRows = candidateFlow.trace.filter((row) => row.role_conditioned_level_selection?.role_assignment);
      const byLeg = new Map();
      for (const row of roleRows) { if (!byLeg.has(row.leg_identity)) byLeg.set(row.leg_identity, []); byLeg.get(row.leg_identity).push(row); }
      const roleFlips = [];
      for (const [legIdentity, rows] of byLeg) {
        let prior = null;
        for (const row of rows) {
          const role = row.role_conditioned_level_selection.role_assignment.own_role;
          if (prior && role !== prior.role) roleFlips.push({ leg_identity: legIdentity, from: prior.role, to: role, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, target_before_cents: prior.target, target_after_cents: row.final_target_cents, reaimed: prior.target !== row.final_target_cents });
          prior = { role, target: row.final_target_cents };
        }
      }
      const baselineByLeg = new Map(baselineRun.marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
      const candidateByLeg = new Map(candidateRun.marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
      const fallerFills = perGameOutcomeTable.flatMap((game) => game.legs.filter((leg) => leg.credited && leg.role_at_entry_or_terminal === "FALLING").map((leg) => {
        const baseline = baselineByLeg.get(leg.leg_identity), candidate = candidateByLeg.get(leg.leg_identity);
        return { event_id: game.event_id, category: game.category, price_region: game.price_region, leg_identity: leg.leg_identity, baseline_credited: baseline.credited, baseline_entry_cents: baseline.entry_cents, baseline_fill_timestamp_epoch: baseline.fill_timestamp_epoch, candidate_entry_cents: candidate.entry_cents, candidate_fill_timestamp_epoch: candidate.fill_timestamp_epoch, fill_delay_seconds: Number.isFinite(baseline.fill_timestamp_epoch) ? candidate.fill_timestamp_epoch - baseline.fill_timestamp_epoch : null, later_floor_cents: leg.post_onset_offer_floor_cents, candidate_entry_minus_floor_cents: leg.entry_minus_later_floor_cents, fill_clock: leg.fill_clock, floor_clock: leg.floor_clock };
      }));
      const climberCandidateLegs = perGameOutcomeTable.flatMap((game) => game.legs.filter((leg) => leg.role_at_entry_or_terminal === "RISING").map((leg) => ({ game, leg })));
      const climberBaselineCredited = climberCandidateLegs.filter(({ leg }) => baselineByLeg.get(leg.leg_identity)?.credited).length;
      const climberLost = climberCandidateLegs.filter(({ leg }) => baselineByLeg.get(leg.leg_identity)?.credited && !candidateByLeg.get(leg.leg_identity)?.credited).map(({ game, leg }) => ({ event_id: game.event_id, leg_identity: leg.leg_identity }));
      const locked = (run) => run.marketEvents.filter((event) => event.completed_pair && event.pair_under_par).map((event) => 100 - event.combined_entry_cents);
      const baselineLocked = locked(baselineRun), candidateLocked = locked(candidateRun);
      const baselinePartial = new Map(baselineFourStateRows.filter((row) => row.state === "PARTIAL_FOR_REASON").map((row) => [row.event_id, row]));
      const candidatePartial = new Map(candidateFourStateRows.filter((row) => row.state === "PARTIAL_FOR_REASON").map((row) => [row.event_id, row]));
      const created = [...candidatePartial].filter(([eventId]) => !baselinePartial.has(eventId)).map(([eventId, row]) => ({ event_id: eventId, direction: "CREATED_BY_V52J", credited_legs: row.credited_legs }));
      const resolved = [...baselinePartial].filter(([eventId]) => !candidatePartial.has(eventId)).map(([eventId, row]) => ({ event_id: eventId, direction: "RESOLVED_BY_V52J", baseline_credited_legs: row.credited_legs, candidate_state: candidateFourStateRows.find((item) => item.event_id === eventId)?.state ?? null }));
      return {
        role_receipts: roleRows.length,
        roles: countBy(roleRows, (row) => row.role_conditioned_level_selection.role_assignment.own_role),
        pair_read_coherence: countBy(roleRows, (row) => row.role_conditioned_level_selection.role_assignment.pair_read_coherence),
        role_flips: { count: roleFlips.length, reaimed: roleFlips.filter((row) => row.reaimed).length, rows: roleFlips },
        faller_side_fills: { rows: fallerFills, fill_delay_seconds: distribution(fallerFills.map((row) => row.fill_delay_seconds)), entry_minus_later_floor_cents: distribution(fallerFills.map((row) => row.candidate_entry_minus_floor_cents)), at_or_near_floor_0_to_1c: fallerFills.filter((row) => Number.isInteger(row.candidate_entry_minus_floor_cents) && row.candidate_entry_minus_floor_cents >= 0 && row.candidate_entry_minus_floor_cents <= 1).length },
        climber_preservation: { baseline_credited_climber_legs: climberBaselineCredited, candidate_lost_climber_legs: climberLost.length, inverse_error_count: climberLost.length, rows: climberLost },
        banked_delta: { baseline: { n: baselineLocked.length, mean_cents: baselineLocked.length ? baselineLocked.reduce((a, b) => a + b, 0) / baselineLocked.length : null }, candidate: { n: candidateLocked.length, mean_cents: candidateLocked.length ? candidateLocked.reduce((a, b) => a + b, 0) / candidateLocked.length : null } },
        one_sided_exposure_changes: { created_count: created.length, resolved_count: resolved.length, created, resolved },
      };
    })() : null;
    const libraryBackedEvidenceSummary = isV52k ? (() => {
      const evaluationRows = candidateFlow.trace.filter((row) => row.library_backed_level_evidence);
      const applicableRows = evaluationRows.filter((row) => row.library_backed_level_evidence.applicable === true);
      const belowShownRows = applicableRows.filter((row) => row.library_backed_level_evidence.below_shown_range === true
        && Number.isInteger(row.final_target_cents)
        && Number.isInteger(row.library_backed_level_evidence.original_tape_bounds?.min_cents)
        && row.final_target_cents < row.library_backed_level_evidence.original_tape_bounds.min_cents);
      const mutationRows = candidateRun.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && ["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE", "GAP_CREDIT_REPRICE_DOWN"].includes(row.kind) && row.birth_license?.level?.library_backed_level_evidence?.applicable === true);
      const baselineByLeg = new Map(baselineRun.marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
      const candidateByLeg = new Map(candidateRun.marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
      const fallerFills = perGameOutcomeTable.flatMap((game) => game.legs.filter((leg) => leg.credited && leg.read_state_at_entry_or_terminal === "FALLING").map((leg) => {
        const baseline = baselineByLeg.get(leg.leg_identity), candidate = candidateByLeg.get(leg.leg_identity);
        return { event_id: game.event_id, category: game.category, price_region: game.price_region, leg_identity: leg.leg_identity, baseline_credited: baseline?.credited ?? false, baseline_entry_cents: baseline?.entry_cents ?? null, baseline_fill_timestamp_epoch: baseline?.fill_timestamp_epoch ?? null, candidate_entry_cents: candidate.entry_cents, candidate_fill_timestamp_epoch: candidate.fill_timestamp_epoch, fill_delay_seconds: Number.isFinite(baseline?.fill_timestamp_epoch) ? candidate.fill_timestamp_epoch - baseline.fill_timestamp_epoch : null, later_floor_cents: leg.post_onset_offer_floor_cents, candidate_entry_minus_floor_cents: leg.entry_minus_later_floor_cents, library_evidence_authority: leg.level_evidence_authority_at_entry_or_terminal };
      }));
      const climberRows = perGameOutcomeTable.flatMap((game) => game.legs.filter((leg) => leg.read_state_at_entry_or_terminal === "RISING").map((leg) => ({ event_id: game.event_id, leg_identity: leg.leg_identity, baseline_credited: baselineByLeg.get(leg.leg_identity)?.credited ?? false, candidate_credited: candidateByLeg.get(leg.leg_identity)?.credited ?? false })));
      const climberLost = climberRows.filter((row) => row.baseline_credited && !row.candidate_credited);
      const locked = (run) => run.marketEvents.filter((event) => event.completed_pair && event.pair_under_par).map((event) => 100 - event.combined_entry_cents);
      const baselineLocked = locked(baselineRun), candidateLocked = locked(candidateRun);
      const baselinePartial = new Map(baselineFourStateRows.filter((row) => row.state === "PARTIAL_FOR_REASON").map((row) => [row.event_id, row]));
      const candidatePartial = new Map(candidateFourStateRows.filter((row) => row.state === "PARTIAL_FOR_REASON").map((row) => [row.event_id, row]));
      const created = [...candidatePartial].filter(([eventId]) => !baselinePartial.has(eventId)).map(([eventId, row]) => ({ event_id: eventId, direction: "CREATED_BY_V52K", credited_legs: row.credited_legs, exposure_to_window_edge_seconds: oneSidedExposureSummary?.rows?.find((item) => item.event_id === eventId)?.exposure_to_window_edge_seconds ?? null }));
      const resolved = [...baselinePartial].filter(([eventId]) => !candidatePartial.has(eventId)).map(([eventId, row]) => ({ event_id: eventId, direction: "RESOLVED_BY_V52K", baseline_credited_legs: row.credited_legs, candidate_state: candidateFourStateRows.find((item) => item.event_id === eventId)?.state ?? null }));
      return {
        evaluation_receipts: evaluationRows.length,
        applicable_library_receipts: applicableRows.length,
        library_backed_stands_below_shown_range: { receipts: belowShownRows.length, legs: new Set(belowShownRows.map((row) => row.leg_identity)).size, games: new Set(belowShownRows.map((row) => row.event_id)).size, distance_below_tape_min_cents: distribution(belowShownRows.map((row) => row.library_backed_level_evidence.original_tape_bounds.min_cents - row.final_target_cents)), rows: belowShownRows.map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, target_cents: row.final_target_cents, tape_min_cents: row.library_backed_level_evidence.original_tape_bounds.min_cents, library_floor_cents: row.library_backed_level_evidence.library_supported_floor_cents, current_ask_cents: row.library_backed_level_evidence.current_touch_ask_cents })) },
        library_backed_rest_mutations: mutationRows.length,
        faller_side_fills: { rows: fallerFills, fill_delay_seconds_vs_V52h: distribution(fallerFills.map((row) => row.fill_delay_seconds)), entry_minus_later_floor_cents: distribution(fallerFills.map((row) => row.candidate_entry_minus_floor_cents)), at_or_near_floor_0_to_1c: fallerFills.filter((row) => Number.isInteger(row.candidate_entry_minus_floor_cents) && row.candidate_entry_minus_floor_cents >= 0 && row.candidate_entry_minus_floor_cents <= 1).length },
        climber_completion_preservation: { baseline_credited_climber_legs: climberRows.filter((row) => row.baseline_credited).length, candidate_lost_climber_legs: climberLost.length, rows: climberLost },
        banked_delta: { baseline: { n: baselineLocked.length, mean_cents: baselineLocked.length ? baselineLocked.reduce((a, b) => a + b, 0) / baselineLocked.length : null }, candidate: { n: candidateLocked.length, mean_cents: candidateLocked.length ? candidateLocked.reduce((a, b) => a + b, 0) / candidateLocked.length : null } },
        one_sided_exposure_changes: { created_count: created.length, resolved_count: resolved.length, created_duration_seconds: distribution(created.map((row) => row.exposure_to_window_edge_seconds)), created, resolved },
        pre_stated_claims: {
          library_backed_levels_actually_stand_below_shown_range: belowShownRows.length > 0,
          faller_side_fills_move_later_and_nearer_floor: fallerFills.length > 0 && distribution(fallerFills.map((row) => row.fill_delay_seconds)).median > 0 && distribution(fallerFills.map((row) => row.candidate_entry_minus_floor_cents)).median <= entryLaterFloorComparison.baseline.signed_entry_minus_later_floor_cents.median,
          climber_side_completions_preserved: climberLost.length === 0,
          mean_banked_delta_rises: baselineLocked.length > 0 && candidateLocked.length > 0 && (candidateLocked.reduce((a, b) => a + b, 0) / candidateLocked.length) > (baselineLocked.reduce((a, b) => a + b, 0) / baselineLocked.length),
          new_one_sided_exposure_counted_both_ways_per_game: true,
          pins_unharmed: pinComparisons.every((row) => row.unharmed),
          REFLEX_POST_zero: null,
          adjudication: "OBSERVATION_ONLY; CURRENT_PRE_RE-CUT_FLOOR_BASIS; NO_BEHAVIORAL_REPAIR_PERMITTED",
        },
      };
    })() : null;
    const palantirConsumptionSummary = isV52e ? {
      decision_trace_rows: candidateFlow.trace.length,
      consumption_receipts: palantirRows.length,
      N2_receipts: palantirRows.filter((row) => row.palantir?.N2?.node === "N2").length,
      N4_receipts: palantirRows.filter((row) => row.palantir?.N4?.node === "N4").length,
      N5_receipts: palantirRows.filter((row) => row.palantir?.N5?.node === "N5").length,
      N4_grid_covered_receipts: palantirRows.filter((row) => row.palantir?.N4?.grid).length,
      N4_prior_informed_live_evidence_rescues: n4RescueRows.length,
      N5_frozen_tie_resolutions: n5PriorResolvedRows.length,
      baseline_N4_abstentions_in_grid_covered_receipts: baselineGridAbstentionKeys.size,
      candidate_N4_abstentions_on_same_receipts: candidateGridAbstentionKeys.size,
      N4_abstention_delta: candidateGridAbstentionKeys.size - baselineGridAbstentionKeys.size,
      all_receipts_continuous: palantirRows.length === candidateFlow.trace.length && palantirRows.every((row) => row.palantir?.continuous_at_decision_time === true),
      priors_gate: false,
      behaviorally_consumed: n4RescueRows.length + n5PriorResolvedRows.length > 0,
      ...(isV52k ? {
        depth_under_validation_receipts: palantirRows.filter((row) => row.palantir?.N4?.library_level_evidence_under_validation).length,
        library_evidence_evaluation_receipts: candidateFlow.trace.filter((row) => row.library_backed_level_evidence).length,
        library_backed_target_changed_receipts: candidateFlow.trace.filter((row) => row.library_backed_level_evidence?.target_changed).length,
        library_backed_below_shown_range_receipts: candidateFlow.trace.filter((row) => row.library_backed_level_evidence?.applicable && row.library_backed_level_evidence?.below_shown_range).length,
        under_validation_candidate_ids: n9Binding.store.boot_assertion.under_validation_loaded_ids,
      } : isV52i ? {
        depth_under_validation_receipts: palantirRows.filter((row) => row.palantir?.N4?.depth_candidates_under_validation).length,
        depth_target_changed_receipts: candidateFlow.trace.filter((row) => row.depth_informed_level_selection?.target_changed).length,
        under_validation_candidate_ids: n9Binding.store.boot_assertion.under_validation_loaded_ids,
      } : isV52j ? {
        depth_under_validation_receipts: palantirRows.filter((row) => row.palantir?.N4?.depth_candidates_under_validation).length,
        role_conditioned_receipts: candidateFlow.trace.filter((row) => row.role_conditioned_level_selection).length,
        faller_depth_target_changed_receipts: candidateFlow.trace.filter((row) => row.role_conditioned_level_selection?.role_assignment?.own_role === "FALLING" && row.role_conditioned_level_selection?.target_changed).length,
        rising_or_neutral_target_changed_receipts: candidateFlow.trace.filter((row) => ["RISING", "SETTLED", "INSUFFICIENT"].includes(row.role_conditioned_level_selection?.role_assignment?.own_role) && row.role_conditioned_level_selection?.target_changed).length,
        under_validation_candidate_ids: n9Binding.store.boot_assertion.under_validation_loaded_ids,
      } : {}),
      pin_comparisons: pinComparisons,
      pins_unharmed: pinComparisons.every((row) => row.unharmed),
    } : null;
    const v52bAssertions = {
      flow_assertions: candidateFlow.assertions,
      [isV52CausalOnset ? "clause_1_V52L_CAUSAL_PREFIX" : "clause_1_CODEX_INTERIM"]: { violations: candidateFlow.trace.filter((row) => isV52CausalOnset
        ? row.onset?.binding_status !== "V52L_CAUSAL_PREFIX" || row.onset?.right_edge_consumed !== false || row.onset?.full_span_fit !== false || (Number.isFinite(row.onset?.maximum_consumed_timestamp_epoch) && row.onset.maximum_consumed_timestamp_epoch > row.timestamp_epoch)
        : row.onset?.binding_status !== "CODEX-INTERIM").map(traceKey) },
      machine_read_evidence_on_every_post: { violations: candidateMutations.filter((row) => row.birth_license?.level?.machine_read?.authorized !== true || !row.birth_license?.level?.machine_read?.evidence?.evaluation_receipt || !row.birth_license?.level?.machine_read?.evidence?.directional_evidence_receipt).map((row) => `${row.leg_identity}@${row.receipt}`) },
      diary_demoted_not_removed: { violations: candidateMutations.filter((row) => row.birth_license?.diary?.role !== "RECORDED_REFERENCE_INPUT_NOT_SOLE_LEVEL_AUTHORITY").map((row) => `${row.leg_identity}@${row.receipt}`) },
      REFLEX_POST_zero: { observed: candidateMutations.filter((row) => row.birth_license?.read?.passed !== true).length, expected: 0 },
      ...((isV52c || isV52d || isV52e) ? {
        every_post_binds_full_post_onset_read_span: { violations: candidateMutations.filter((row) => row.birth_license?.read?.full_post_onset_evidence?.fixed_horizon_seconds !== null || row.birth_license?.read?.full_post_onset_evidence?.replacement_tuning_constant !== null || !Number.isInteger(row.birth_license?.read?.full_post_onset_evidence?.consulted?.evidence_receipts)).map((row) => `${row.leg_identity}@${row.receipt}`) },
        ...(isV52e ? {
          clauses_1_through_4_and_scavenger_mechanics_frozen: { violations: frozenClauseDiffs.map((row) => row.key) },
          CLEAN_store_boot_assertion: { pass: n9Binding.store.boot_assertion.passed && n9Binding.store.boot_assertion.unvalidated_loaded === 0 && n9Binding.store.boot_assertion.quarantined_loaded === 0 && n9Binding.store.boot_assertion.superseded_loaded === 0 && n9Binding.store.boot_assertion.fallback_loads === 0 && (!isV52DepthValidation || (n9Binding.store.boot_assertion.canonical_clean_store_unchanged === true && n9Binding.store.boot_assertion.under_validation_loaded === 2)) },
          every_decision_receipt_consumes_N2_N4_N5_continuously: { violations: candidateFlow.trace.filter((row) => !(row.palantir?.continuous_at_decision_time && row.palantir?.N2?.node === "N2" && row.palantir?.N4?.node === "N4" && row.palantir?.N5?.node === "N5")).map(traceKey) },
          every_prior_has_CLEAN_provenance: { violations: palantirRows.filter((row) => [row.palantir.N2, row.palantir.N4, row.palantir.N5].some((node) => !Array.isArray(node.provenance) || node.provenance.some((asset) => !["VALIDATED", "VALID-NARROW"].includes(asset.status) || !(asset.source_sha256 ? /^[0-9a-f]{64}$/.test(asset.source_sha256) : Array.isArray(asset.source_sha256s) && asset.source_sha256s.length > 0 && asset.source_sha256s.every((sha) => /^[0-9a-f]{64}$/.test(sha)))))).map(traceKey) },
          priors_inform_never_gate: { violations: candidateFlow.trace.filter((row) => {
            const before = baselineTrace.get(traceKey(row));
            const candidateIndex = candidateTraceIndex.get(traceKey(row)), firstAuthorizedIndex = firstAuthorizedIndexByEvent.get(row.event_id);
            const firstAuthorizedTimestamp = firstAuthorizedTimestampByEvent.get(row.event_id);
            const frozen_same_input_scope = isV52MacroRecognition
              ? !Number.isFinite(firstAuthorizedTimestamp) || row.timestamp_epoch <= firstAuthorizedTimestamp
              : !(isV52h || isV52DepthValidation || isV52CausalOnset) || !Number.isInteger(firstAuthorizedIndex) || candidateIndex <= firstAuthorizedIndex;
            return row.palantir?.priors_gate !== false || (frozen_same_input_scope && before?.level?.machine_read?.authorized === true && row.level?.machine_read?.authorized !== true);
          }).map(traceKey) },
          ...(isV52CausalOnset ? {
            frozen_N9_continuous_consumption_preserved: { pass: palantirConsumptionSummary.all_receipts_continuous },
            causal_onset_right_edge_independence: { violations: rightEdgeIndependenceRows.filter((row) => row.pass !== true || row.identical_onsets !== true).map((row) => row.event_id), evaluated_games: rightEdgeIndependenceRows.length },
            no_full_span_or_right_edge_input_in_clause_1: { violations: candidateFlow.trace.filter((row) => row.onset?.right_edge_consumed !== false || row.onset?.full_span_fit !== false).map(traceKey) },
            clause_4_market_proof_removal_recorded_on_every_rest_mutation: { violations: candidateMutations.filter((row) => row.birth_license?.clause_4_market_proof_precondition?.removed_from_licensing !== true || row.birth_license?.clause_4_market_proof_precondition?.recorded_as_telemetry !== true).map((row) => `${row.leg_identity}@${row.receipt}`) },
            clause_4_disagreement_referee_intact: { violations: candidateFlow.trace.filter((row) => row.coherence?.disagreement_firing && !row.coherence?.disagreement_clear && row.blocked_clause !== "FIRING_DISAGREEMENT_ACTIVE").map(traceKey) },
            clauses_2_through_6_function_identity: { pass: policy.fullPostOnsetRead === frozenV52hPolicy.fullPostOnsetRead
              && policy.fullPostOnsetAuthority === frozenV52hPolicy.fullPostOnsetAuthority
              && policy.observePostOnsetEvidence === frozenV52hPolicy.observePostOnsetEvidence
              && policy.firstFailure === frozenV52hPolicy.firstFailure
              && policy.tradeTruthCredit === frozenV52hPolicy.tradeTruthCredit
              && policy.continuousConsultation === frozenV52hPolicy.continuousConsultation
              && policy.machineReadLevel === frozenV52hPolicy.machineReadLevel
              && policy.settlementIdentity === frozenV52hPolicy.settlementIdentity
              && policy.jointTargetConservation === frozenV52hPolicy.jointTargetConservation
              && policy.marketProofReceipt === frozenV52hPolicy.marketProofReceipt },
            clauses_5_and_6_recorded_on_every_rest_mutation: { violations: candidateMutations.filter((row) => row.birth_license?.pair_entry_conservation?.clause !== "CLAUSE_5_PAIR_ENTRY_CONSERVATION" || row.birth_license?.joint_target_conservation?.clause !== "CLAUSE_6_ORDER_FREE_JOINT_TARGET_CONSERVATION").map((row) => `${row.leg_identity}@${row.receipt}`) },
            clause_6_zero_joint_target_sum_above_99: { violations: pairBudgetRecordSummary.joint_sum_violations },
            pair_budget_record_one_per_game_complete_revision_chain: { pass: pairBudgetRecordSummary.pass && pairBudgetRecordSummary.incomplete_revision_chains.length === 0 && pairBudgetRecordSummary.forbidden_plan_fields.length === 0 },
            zero_COMPLETE_AT_LOSS: { violations: candidateFourStateRows.filter((row) => row.state === "COMPLETE_AT_LOSS").map((row) => row.event_id) },
            pins_lawful_not_outcome_bound: { violations: candidateMutations.filter((row) => V52_FLOW_EVENTS.has(row.event_id.match(/26JUL\d{2}[A-Z]+/)?.[0] ?? "") && !(row.birth_license?.onset?.passed && row.birth_license?.read?.passed && row.birth_license?.joint_target_conservation?.passed)).map((row) => `${row.leg_identity}@${row.receipt}`) },
            ...(isV52MacroRecognition ? {
              every_macro_signature_is_receipt_causal: { violations: candidateFlow.trace.filter((row) => row.macro_recognition && (row.macro_recognition.causal !== true || row.macro_recognition.right_edge_consumed !== false || row.macro_recognition.full_span_fit !== false || (Number.isFinite(row.macro_recognition.maximum_consumed_timestamp_epoch) && row.macro_recognition.maximum_consumed_timestamp_epoch > row.timestamp_epoch))).map(traceKey) },
              ...(isV52r ? {
                exact_TRD5_source_and_gate_on_every_evaluation: { violations: candidateFlow.trace.filter((row) => row.macro_recognition && !(row.macro_recognition.rule?.threshold_post_onset_trades === 5 && row.macro_recognition.rule?.provenance?.commit === TRD5_COMMIT && row.macro_recognition.trd5?.threshold === 5 && row.macro_recognition.trd5?.provenance?.commit === TRD5_COMMIT)).map(traceKey) },
                spread_settle_anchor_receipted_on_every_evaluation: { violations: candidateFlow.trace.filter((row) => row.macro_recognition && !(row.macro_recognition.anchor_correction?.method?.commit === SHAPE_TAXONOMY_COMMIT && row.macro_recognition.anchor_correction?.method?.sha256 === v52qAnchorBinding.method.sha256 && row.macro_recognition.anchor_correction?.series_floor === "FORMATION_END_INCLUSIVE")).map(traceKey) },
                coordinate_zero_is_max_onset_formation: { violations: candidateFlow.trace.filter((row) => row.macro_recognition && Number.isFinite(row.macro_recognition.post_onset_epoch) && Number.isFinite(row.macro_recognition.formation_end_epoch) && row.macro_recognition.coordinate_zero_epoch !== Math.max(row.macro_recognition.post_onset_epoch, row.macro_recognition.formation_end_epoch)).map(traceKey) },
                candidate_role_matches_literal_drift_arithmetic: { violations: candidateFlow.trace.filter((row) => row.macro_recognition?.drift_cents !== null && row.macro_recognition.candidate_role !== (row.macro_recognition.drift_cents >= 2 ? "ROLE_UP" : row.macro_recognition.drift_cents <= -2 ? "ROLE_DOWN" : "ROLE_STILL")).map(traceKey) },
                no_directional_bind_before_five_post_onset_trades: { violations: candidateFlow.trace.filter((row) => row.macro_recognition?.bound_role && row.macro_recognition.trd5?.post_onset_trade_count < 5).map(traceKey) },
                held_role_changes_only_on_instrument_flip: { violations: candidateFlow.trace.filter((row) => row.macro_recognition?.trd5?.transition === "INSTRUMENT_FLIP_REBIND" && row.macro_recognition?.trd5?.last_flip?.from === row.macro_recognition?.trd5?.last_flip?.to).map(traceKey) },
                UP_STILL_ABSTAIN_preserve_V52l_level: { violations: candidateFlow.trace.filter((row) => row.macro_recognition?.bound_role !== "ROLE_DOWN" && row.assembled_policy?.target_changed === true).map(traceKey) },
                every_ROLE_DOWN_consumption_is_LOW1_with_source: { violations: candidateFlow.trace.filter((row) => row.assembled_policy?.applicable && !(row.assembled_policy.recognition?.bound_role === "ROLE_DOWN" && row.assembled_policy.delta_cents === 1 && row.assembled_policy.low1_identity === "TRAIL1_IDENTICAL_TO_LOW_1_ON_INTEGER_TAPE" && row.assembled_policy.provenance?.commit === LOW1_COMMIT && row.assembled_policy.selected_target_cents === Math.min(row.assembled_policy.session_low_cents - 1, row.assembled_policy.current_touch_ask_cents - 1, Number.isInteger(row.assembled_policy.clause_6_cap_cents) ? row.assembled_policy.clause_6_cap_cents : 99))).map(traceKey) },
                every_consumed_ROLE_DOWN_target_reaches_final_license: { violations: candidateFlow.trace.filter((row) => row.assembled_policy?.level_policy_consumed === true && row.final_target_cents !== row.assembled_policy.selected_target_cents).map(traceKey) },
                LOW1_target_respects_touch_and_clause_6: { violations: candidateFlow.trace.filter((row) => row.assembled_policy?.level_policy_consumed === true && Number.isInteger(row.final_target_cents) && (row.final_target_cents >= row.assembled_policy.current_touch_ask_cents || (Number.isInteger(row.assembled_policy.clause_6_cap_cents) && row.final_target_cents > row.assembled_policy.clause_6_cap_cents))).map(traceKey) },
                LOW1_is_not_decorative: { pass: candidateFlow.trace.some((row) => row.assembled_policy?.target_changed === true) },
                both_clocks_present_side_by_side: { violations: candidateFlow.trace.filter((row) => row.macro_recognition && !(Object.hasOwn(row, "t_minus_scheduled_seconds") && Object.hasOwn(row, "t_minus_actual_bell_seconds"))).map(traceKey) },
              } : isV52Ripeness ? {
                exact_benchmark_role_rule_on_every_evaluation: { violations: candidateFlow.trace.filter((row) => row.macro_recognition && !(row.macro_recognition.rule?.threshold_cents === 2 && row.macro_recognition.rule?.new_constants === 0 && (isV52q ? row.macro_recognition.rule?.anchor_method?.commit === SHAPE_TAXONOMY_COMMIT && row.macro_recognition.rule?.series_floor === "FORMATION_END_INCLUSIVE" : row.macro_recognition.rule?.taxonomy_commit === SHAPE_TAXONOMY_COMMIT))).map(traceKey) },
                ...(isV52q ? {
                  spread_settle_anchor_receipted_on_every_evaluation: { violations: candidateFlow.trace.filter((row) => row.macro_recognition && !(row.macro_recognition.anchor_correction?.method?.commit === SHAPE_TAXONOMY_COMMIT && row.macro_recognition.anchor_correction?.method?.sha256 === v52qAnchorBinding.method.sha256 && row.macro_recognition.anchor_correction?.series_floor === "FORMATION_END_INCLUSIVE")).map(traceKey) },
                  anchor_value_matches_bound_ground_truth_leg: { violations: candidateFlow.trace.filter((row) => {
                    const leg = groundTruthWindowBinding.byEvent.get(row.event_id)?.legs?.[row.leg_identity.split("|").at(-1)];
                    return row.macro_recognition && Number.isInteger(leg?.open_postformation_cents) && row.macro_recognition.post_formation_open_cents !== leg.open_postformation_cents;
                  }).map(traceKey) },
                  causal_price_series_floored_at_formation_end: { violations: candidateFlow.trace.filter((row) => row.macro_recognition && Number.isFinite(row.macro_recognition.maximum_consumed_timestamp_epoch) && row.macro_recognition.maximum_consumed_timestamp_epoch < row.macro_recognition.formation_end_epoch).map(traceKey) },
                } : {}),
                exact_published_ripeness_source_on_every_evaluation: { violations: candidateFlow.trace.filter((row) => row.macro_recognition && !(row.macro_recognition.ripeness?.source?.commit === RIPENESS_COMMIT && row.macro_recognition.ripeness?.new_constants === 0)).map(traceKey) },
                candidate_role_matches_literal_drift_arithmetic: { violations: candidateFlow.trace.filter((row) => row.macro_recognition?.drift_cents !== null && row.macro_recognition.candidate_role !== (row.macro_recognition.drift_cents >= 2 ? "ROLE_UP" : row.macro_recognition.drift_cents <= -2 ? "ROLE_DOWN" : "ROLE_STILL")).map(traceKey) },
                effective_gate_is_exact_max_and_binding_uses_verified_f: { violations: candidateFlow.trace.filter((row) => row.macro_recognition?.candidate_role && !(row.macro_recognition.ripeness?.effective_gate_f === Math.max(policy.CLASS_GATES[row.macro_recognition.candidate_role], policy.CATEGORY_GATES[row.category]) && row.macro_recognition.ripeness?.verified_binding === (row.macro_recognition.ripeness.verified_span_f >= row.macro_recognition.ripeness.effective_gate_f))).map(traceKey) },
                below_gate_abstains_to_V52l: { violations: candidateFlow.trace.filter((row) => row.macro_recognition?.candidate_role && row.macro_recognition.ripeness?.verified_binding === false && (row.macro_recognition.bound_role !== null || row.benchmarked_role_instrument?.target_changed === true)).map(traceKey) },
                ROLE_UP_STILL_and_below_gate_preserve_V52l_level: { violations: candidateFlow.trace.filter((row) => (row.macro_recognition?.bound_role !== "ROLE_DOWN") && row.benchmarked_role_instrument?.target_changed === true).map(traceKey) },
                every_ROLE_DOWN_consumption_binds_aggregate_and_three_SHAs: { violations: candidateFlow.trace.filter((row) => row.benchmarked_role_instrument?.applicable && !(row.benchmarked_role_instrument.benchmark_role?.bound_role === "ROLE_DOWN" && row.benchmarked_role_instrument.down_depth_row_consumed?.row_identity === `ROLE_DOWN_AGGREGATE|${row.category}` && /^[0-9a-f]{64}$/.test(row.benchmarked_role_instrument.provenance?.taxonomy?.sha256 ?? "") && /^[0-9a-f]{64}$/.test(row.benchmarked_role_instrument.provenance?.floor_depth_table?.sha256 ?? "") && /^[0-9a-f]{64}$/.test(row.macro_recognition?.ripeness?.source?.sha256 ?? ""))).map(traceKey) },
                every_consumed_ROLE_DOWN_target_reaches_final_license: { violations: candidateFlow.trace.filter((row) => row.benchmarked_role_instrument?.level_policy_consumed === true && row.final_target_cents !== row.benchmarked_role_instrument.selected_target_cents).map(traceKey) },
                role_depth_target_respects_touch_and_clause_6: { violations: candidateFlow.trace.filter((row) => row.benchmarked_role_instrument?.level_policy_consumed === true && Number.isInteger(row.final_target_cents) && (row.final_target_cents >= row.benchmarked_role_instrument.current_touch_ask_cents || (Number.isInteger(row.benchmarked_role_instrument.clause_6_cap_cents) && row.final_target_cents > row.benchmarked_role_instrument.clause_6_cap_cents))).map(traceKey) },
                role_is_reevaluated_as_f_advances: { pass: candidateFlow.trace.some((row) => row.macro_recognition?.candidate_role && row.macro_recognition?.ripeness?.verified_binding === false) && candidateFlow.trace.some((row) => row.macro_recognition?.ripeness?.verified_binding === true) },
                scheduled_proxy_is_telemetry_not_decision_basis: { violations: candidateFlow.trace.filter((row) => row.macro_recognition?.ripeness && row.macro_recognition.ripeness.decision_basis !== "VERIFIED_PRE_MATCH_SPAN").map(traceKey) },
              } : isV52o ? {
                exact_benchmark_role_rule_on_every_evaluation: { violations: candidateFlow.trace.filter((row) => row.macro_recognition && !(row.macro_recognition.rule?.taxonomy_commit === SHAPE_TAXONOMY_COMMIT && row.macro_recognition.rule?.threshold_cents === 2 && row.macro_recognition.rule?.new_constants === 0)).map(traceKey) },
                role_matches_literal_drift_arithmetic: { violations: candidateFlow.trace.filter((row) => row.macro_recognition && row.macro_recognition.drift_cents !== null && row.macro_recognition.role !== (row.macro_recognition.drift_cents >= 2 ? "ROLE_UP" : row.macro_recognition.drift_cents <= -2 ? "ROLE_DOWN" : "ABSTAIN")).map(traceKey) },
                every_ROLE_DOWN_consumption_binds_aggregate_and_two_SHAs: { violations: candidateFlow.trace.filter((row) => row.benchmarked_role_instrument?.applicable && !(row.benchmarked_role_instrument.benchmark_role?.role === "ROLE_DOWN" && row.benchmarked_role_instrument.down_depth_row_consumed?.row_identity === `ROLE_DOWN_AGGREGATE|${row.category}` && /^[0-9a-f]{64}$/.test(row.benchmarked_role_instrument.provenance?.taxonomy?.sha256 ?? "") && /^[0-9a-f]{64}$/.test(row.benchmarked_role_instrument.provenance?.floor_depth_table?.sha256 ?? ""))).map(traceKey) },
                ROLE_UP_and_ABSTAIN_preserve_V52l_level: { violations: candidateFlow.trace.filter((row) => ["ROLE_UP", "ABSTAIN"].includes(row.macro_recognition?.role) && row.benchmarked_role_instrument?.target_changed === true).map(traceKey) },
                every_consumed_ROLE_DOWN_target_reaches_final_license: { violations: candidateFlow.trace.filter((row) => row.benchmarked_role_instrument?.level_policy_consumed === true && row.final_target_cents !== row.benchmarked_role_instrument.selected_target_cents).map(traceKey) },
                role_depth_target_is_not_decorative: { pass: candidateFlow.trace.some((row) => row.benchmarked_role_instrument?.target_changed === true) },
                role_depth_target_respects_touch_and_clause_6: { violations: candidateFlow.trace.filter((row) => row.benchmarked_role_instrument?.level_policy_consumed === true && Number.isInteger(row.final_target_cents) && (row.final_target_cents >= row.benchmarked_role_instrument.current_touch_ask_cents || (Number.isInteger(row.benchmarked_role_instrument.clause_6_cap_cents) && row.final_target_cents > row.benchmarked_role_instrument.clause_6_cap_cents))).map(traceKey) },
                role_re_evaluated_as_evidence_accrues: { pass: candidateFlow.trace.some((row) => row.macro_recognition?.role === "ABSTAIN") && candidateFlow.trace.some((row) => ["ROLE_DOWN", "ROLE_UP"].includes(row.macro_recognition?.role)) },
              } : {
                every_shape_depth_consumption_binds_family_confidence_row_and_two_SHAs: { violations: candidateFlow.trace.filter((row) => row.per_shape_floor_depth?.applicable && !(row.per_shape_floor_depth.macro_recognition?.family && Number.isFinite(row.per_shape_floor_depth.confidence) && row.per_shape_floor_depth.table_row && /^[0-9a-f]{64}$/.test(row.per_shape_floor_depth.provenance?.taxonomy?.sha256 ?? "") && /^[0-9a-f]{64}$/.test(row.per_shape_floor_depth.provenance?.floor_depth_table?.sha256 ?? ""))).map(traceKey) },
                abstain_class_retains_frozen_V52l_target: { violations: candidateFlow.trace.filter((row) => row.macro_recognition?.signable === false && row.per_shape_floor_depth?.target_changed === true).map(traceKey) },
                every_consumed_macro_target_reaches_final_license: { violations: candidateFlow.trace.filter((row) => row.per_shape_floor_depth?.level_policy_consumed === true && row.final_target_cents !== row.per_shape_floor_depth.selected_target_cents).map(traceKey) },
                macro_target_is_not_decorative: { pass: candidateFlow.trace.some((row) => row.per_shape_floor_depth?.target_changed === true) },
                macro_target_respects_current_touch_and_clause_6: { violations: candidateFlow.trace.filter((row) => row.per_shape_floor_depth?.level_policy_consumed === true && Number.isInteger(row.final_target_cents) && (row.final_target_cents >= row.per_shape_floor_depth.current_touch_ask_cents || (Number.isInteger(row.per_shape_floor_depth.clause_6_cap_cents) && row.final_target_cents > row.per_shape_floor_depth.clause_6_cap_cents))).map(traceKey) },
              }),
              ...(isV52n ? {
                every_classification_receipts_confidence_vs_pinned_gate: { violations: candidateFlow.trace.filter((row) => row.macro_recognition?.family && !(row.recognition_confidence_gate?.verdict && row.recognition_confidence_gate?.gate?.source === "PER_SHAPE_FLOOR_DEPTH_TABLES.early_call" && row.recognition_confidence_gate?.table_row_identity)).map(traceKey) },
                below_gate_abstains_to_V52l: { violations: candidateFlow.trace.filter((row) => row.recognition_confidence_gate?.passed === false && (row.macro_recognition?.signable !== false || row.per_shape_floor_depth?.target_changed === true)).map(traceKey) },
                bound_family_meets_pinned_f05_and_2c_declaration: { violations: candidateFlow.trace.filter((row) => row.recognition_confidence_gate?.passed === true && !(row.recognition_confidence_gate.gate.median_declaration_by_pinned_checkpoint && row.recognition_confidence_gate.gate.receipt_has_pinned_directional_declaration)).map(traceKey) },
                recognition_is_reattempted_as_evidence_accrues: { pass: candidateFlow.trace.some((row) => row.recognition_confidence_gate?.passed === false) && candidateFlow.trace.some((row) => row.recognition_confidence_gate?.passed === true) },
              } : {}),
            } : {}),
          } : isV52DepthValidation ? {
            frozen_N9_continuous_consumption_preserved: { pass: palantirConsumptionSummary.all_receipts_continuous },
            exact_two_depth_candidates_under_validation: { pass: n9Binding.store.boot_assertion.under_validation_loaded === 2 && canonical(n9Binding.store.boot_assertion.under_validation_loaded_ids) === canonical(["G_GRID_LEVEL_DISCOUNT", "G3_DIP_RECOVERY_GRADIENT"]) },
            ...(isV52k ? {
              every_library_consultation_records_candidate_provenance: { violations: candidateFlow.trace.filter((row) => row.palantir?.N4?.library_level_evidence_under_validation && (row.palantir.N4.library_level_evidence_under_validation.provenance?.length !== 2 || row.palantir.N4.library_level_evidence_under_validation.provenance.some((asset) => asset.status !== "UNDER-VALIDATION_V52I" || !asset.source_sha256))).map(traceKey) },
              library_authority_never_bypasses_clause_2_read: { violations: candidateFlow.trace.filter((row) => row.library_backed_level_evidence?.applicable && row.read?.passed !== true).map(traceKey) },
              every_library_backed_level_binds_identity_value_and_SHA: {
                violations: candidateFlow.trace.filter((row) => row.library_backed_level_evidence?.applicable && !(
                  row.library_backed_level_evidence.prior_provenance?.length === 2
                  && row.library_backed_level_evidence.prior_provenance.every((asset) => asset.asset_id && asset.source_sha256 && /^[0-9a-f]{64}$/.test(asset.source_sha256))
                  && Number.isInteger(row.library_backed_level_evidence.library_supported_floor_cents)
                )).map(traceKey),
              },
              no_library_backed_level_below_library_floor_or_at_above_touch: { violations: candidateFlow.trace.filter((row) => row.library_backed_level_evidence?.applicable && Number.isInteger(row.final_target_cents) && (row.final_target_cents < row.library_backed_level_evidence.library_supported_floor_cents || row.final_target_cents >= row.library_backed_level_evidence.current_touch_ask_cents)).map(traceKey) },
              V52i_and_V52j_behavior_reverted_direct_V52h_parent: { pass: policy.depthSelection === undefined && policy.roleConditionedSelection === undefined && policy.libraryEvidenceSelection !== undefined },
            } : {
              every_depth_consultation_records_candidate_provenance: { violations: candidateFlow.trace.filter((row) => row.palantir?.N4?.depth_candidates_under_validation && (row.palantir.N4.depth_candidates_under_validation.provenance?.length !== 2 || row.palantir.N4.depth_candidates_under_validation.provenance.some((asset) => asset.status !== "UNDER-VALIDATION_V52I" || !asset.source_sha256))).map(traceKey) },
              depth_priors_never_create_or_withdraw_live_authority: { violations: candidateFlow.trace.filter((row) => {
                const selection = isV52j ? row.role_conditioned_level_selection : row.depth_informed_level_selection;
                return selection && (selection.live_authority_retained !== true || selection.priors_gate !== false || (selection.applicable && selection.frozen_machine_read?.authorized !== true));
              }).map(traceKey) },
            }),
            ...(isV52j ? {
              V52i_symmetric_depth_refinement_reverted: { pass: policy.depthSelection === undefined && policy.roleConditionedSelection !== undefined },
              role_assignment_recorded_on_every_clause_3_evaluation: { violations: candidateFlow.trace.filter((row) => !row.role_conditioned_level_selection?.role_assignment?.own_read_evidence || !row.role_conditioned_level_selection?.role_assignment?.sibling_read_evidence).map(traceKey) },
              only_falling_role_can_apply_depth_prior: { violations: candidateFlow.trace.filter((row) => row.role_conditioned_level_selection?.applicable && row.role_conditioned_level_selection?.role_assignment?.own_role !== "FALLING").map(traceKey) },
              rising_settled_insufficient_targets_unchanged: { violations: candidateFlow.trace.filter((row) => ["RISING", "SETTLED", "INSUFFICIENT"].includes(row.role_conditioned_level_selection?.role_assignment?.own_role) && row.role_conditioned_level_selection?.target_changed).map(traceKey) },
              role_flips_re_evaluated: { pass: roleConditionedSummary.role_flips.count >= roleConditionedSummary.role_flips.reaimed },
            } : {}),
            clauses_4_5_6_and_referee_frozen: { violations: frozenClauseDiffs.map((row) => row.key) },
            clause_6_zero_joint_target_sum_above_99: { violations: pairBudgetRecordSummary.joint_sum_violations },
            pair_budget_record_one_per_game_complete_revision_chain: { pass: pairBudgetRecordSummary.pass && pairBudgetRecordSummary.incomplete_revision_chains.length === 0 && pairBudgetRecordSummary.forbidden_plan_fields.length === 0 },
            zero_COMPLETE_AT_LOSS: { violations: candidateFourStateRows.filter((row) => row.state === "COMPLETE_AT_LOSS").map((row) => row.event_id) },
            pins_unharmed: { violations: pinComparisons.filter((row) => !row.unharmed).map((row) => row.event_id) },
          } : isV52h ? {
            frozen_N9_continuous_consumption_preserved: { pass: palantirConsumptionSummary.all_receipts_continuous },
            clause_4_market_proof_removal_recorded_on_every_rest_mutation: { violations: candidateMutations.filter((row) => row.birth_license?.clause_4_market_proof_precondition?.removed_from_licensing !== true || row.birth_license?.clause_4_market_proof_precondition?.recorded_as_telemetry !== true).map((row) => `${row.leg_identity}@${row.receipt}`) },
            clause_4_disagreement_referee_intact: { violations: candidateFlow.trace.filter((row) => row.coherence?.disagreement_firing && !row.coherence?.disagreement_clear && row.blocked_clause !== "FIRING_DISAGREEMENT_ACTIVE").map(traceKey) },
            clauses_5_and_6_recorded_on_every_rest_mutation: { violations: candidateMutations.filter((row) => row.birth_license?.pair_entry_conservation?.clause !== "CLAUSE_5_PAIR_ENTRY_CONSERVATION" || row.birth_license?.joint_target_conservation?.clause !== "CLAUSE_6_ORDER_FREE_JOINT_TARGET_CONSERVATION").map((row) => `${row.leg_identity}@${row.receipt}`) },
            clause_6_zero_joint_target_sum_above_99: { violations: pairBudgetRecordSummary.joint_sum_violations },
            pair_budget_record_one_per_game_complete_revision_chain: { pass: pairBudgetRecordSummary.pass && pairBudgetRecordSummary.incomplete_revision_chains.length === 0 && pairBudgetRecordSummary.forbidden_plan_fields.length === 0 },
            zero_COMPLETE_AT_LOSS: { violations: candidateFourStateRows.filter((row) => row.state === "COMPLETE_AT_LOSS").map((row) => row.event_id) },
            SMIILA_pair_par_block_converts: { pass: smiilaObservation.pair_par_block_converted },
            pins_unharmed: { violations: pinComparisons.filter((row) => !row.unharmed).map((row) => row.event_id) },
          } : isV52g ? {
            frozen_N9_continuous_consumption_preserved: { pass: palantirConsumptionSummary.all_receipts_continuous },
            clause_6_recorded_on_every_rest_mutation: { violations: candidateMutations.filter((row) => row.birth_license?.joint_target_conservation?.clause !== "CLAUSE_6_ORDER_FREE_JOINT_TARGET_CONSERVATION").map((row) => `${row.leg_identity}@${row.receipt}`) },
            clause_6_zero_joint_target_sum_above_99: { violations: pairBudgetRecordSummary.joint_sum_violations },
            pair_budget_record_one_per_game_complete_revision_chain: { pass: pairBudgetRecordSummary.pass && pairBudgetRecordSummary.incomplete_revision_chains.length === 0 && pairBudgetRecordSummary.forbidden_plan_fields.length === 0 },
            four_prior_AT_LOSS_identities_remain_lawful: { pass: v52gPriorLossReattestation.pass },
            pins_unharmed_and_SANDAN_at_or_better: { violations: pinComparisons.filter((row) => !row.unharmed || (row.code === "26JUL13SANDAN" && !row.at_or_better)).map((row) => row.event_id) },
          } : isV52f ? {
            frozen_N9_continuous_consumption_preserved: { pass: palantirConsumptionSummary.all_receipts_continuous },
            clause_5_recorded_on_every_rest_mutation: { violations: candidateMutations.filter((row) => row.birth_license?.pair_entry_conservation?.clause !== "CLAUSE_5_PAIR_ENTRY_CONSERVATION").map((row) => `${row.leg_identity}@${row.receipt}`) },
            clause_5_strict_integer_identity_on_every_post_credit_rest: { violations: candidateMutations.filter((row) => row.birth_license?.pair_entry_conservation?.applicable && !(Number.isInteger(row.target_cents) && row.target_cents <= row.birth_license.pair_entry_conservation.max_lawful_target_cents && row.target_cents + row.birth_license.pair_entry_conservation.credited_sibling_entry_cents < 100)).map((row) => `${row.leg_identity}@${row.receipt}`) },
            pre_stated_claim_four_conversions_and_zero_new_AT_LOSS: { pass: v52fPreStatedClaim.pass },
          } : {
            consumption_receipts_are_behavioral_not_decorative: { pass: palantirConsumptionSummary.behaviorally_consumed },
            N4_grid_covered_abstentions_fall: { observed_before: baselineGridAbstentionKeys.size, observed_after: candidateGridAbstentionKeys.size, pass: baselineGridAbstentionKeys.size > 0 && candidateGridAbstentionKeys.size < baselineGridAbstentionKeys.size },
          }),
          ...(isV52MacroRecognition ? {} : { pins_unharmed: { violations: pinComparisons.filter((row) => !row.unharmed).map((row) => row.event_id) } }),
        } : isV52d ? {
          clauses_1_2_3_and_scavenger_frozen: { violations: frozenClauseDiffs.map((row) => row.key) },
          referee_records_every_firing_disagreement: { violations: candidateAdjudicationRows.filter((row) => !row.coherence?.disagreement_adjudication?.status || !row.coherence?.disagreement_adjudication?.comparison).map(traceKey) },
          referee_uses_no_palantir_N9_or_historical_inputs: { violations: candidateAdjudicationRows.filter((row) => row.coherence.disagreement_adjudication.palantir_priors_consumed !== false || row.coherence.disagreement_adjudication.N9_post_bell_consumed !== false || row.coherence.disagreement_adjudication.historical_inputs_consumed !== false).map(traceKey) },
          adjudications_occur_and_order_masked_burden_falls: { pass: refereeSummary.pre_stated_falsifiable_claim.adjudications_occur && refereeSummary.pre_stated_falsifiable_claim.order_masked_disagreement_burden_falls },
        } : { clauses_1_3_4_and_scavenger_frozen: { violations: frozenClauseDiffs.map((row) => row.key) } }),
      } : { clauses_1_2_4_and_scavenger_byte_equal_per_receipt: { violations: frozenClauseDiffs.map((row) => row.key) } }),
    };
    const blockReasonLegs = [...new Set([...baselineFlow.trace, ...candidateFlow.trace].map((row) => row.leg_identity))].sort().map((legIdentity) => {
      const before = baselineFlow.trace.filter((row) => row.leg_identity === legIdentity), after = candidateFlow.trace.filter((row) => row.leg_identity === legIdentity);
      const beforeAbsent = before.filter((row) => row.blocked_clause === "NO_TAPE_MACHINE_READ_ABSENT").length;
      const afterAbsent = after.filter((row) => row.blocked_clause === "NO_TAPE_MACHINE_READ_ABSENT").length;
      const fullReadRows = after.filter((row) => row.read?.full_post_onset_evidence);
      const lastRead = fullReadRows.at(-1)?.read?.full_post_onset_evidence ?? null;
      return {
        event_id: after[0]?.event_id ?? before[0]?.event_id,
        leg_identity: legIdentity,
        category: after[0]?.category ?? before[0]?.category,
        price_region: after[0]?.price_region ?? before[0]?.price_region,
        baseline_block_reasons: countBy(before.filter((row) => row.blocked_clause), (row) => row.blocked_clause),
        candidate_block_reasons: countBy(after.filter((row) => row.blocked_clause), (row) => row.blocked_clause),
        baseline_READ_ABSENT_receipts: beforeAbsent,
        candidate_READ_ABSENT_receipts: afterAbsent,
        READ_ABSENT_delta: afterAbsent - beforeAbsent,
        thin_tape_endogenous_class: beforeAbsent > 0,
        final_full_post_onset_read_span: lastRead ? { span_seconds: lastRead.span_seconds, consulted: lastRead.consulted, sufficient: lastRead.sufficient, first_evidence: lastRead.first_evidence, last_evidence: lastRead.last_evidence } : null,
      };
    });
    const thinTapeRows = blockReasonLegs.filter((row) => row.thin_tape_endogenous_class);
    const blockReasonHistogram = {
      definition: "THIN_TAPE_IS_ENDOGENOUS: LEG_WITH_ONE_OR_MORE_FROZEN_V52B_READ_ABSENT_RECEIPTS; NO_COUNT_OR_TIME_THRESHOLD_ADDED",
      per_leg: blockReasonLegs,
      aggregate: {
        legs: blockReasonLegs.length,
        baseline: countBy(baselineFlow.trace.filter((row) => row.blocked_clause), (row) => row.blocked_clause),
        candidate: countBy(candidateFlow.trace.filter((row) => row.blocked_clause), (row) => row.blocked_clause),
        thin_tape_legs: thinTapeRows.length,
        thin_tape_READ_ABSENT_before: thinTapeRows.reduce((sum, row) => sum + row.baseline_READ_ABSENT_receipts, 0),
        thin_tape_READ_ABSENT_after: thinTapeRows.reduce((sum, row) => sum + row.candidate_READ_ABSENT_receipts, 0),
      },
    };
    blockReasonHistogram.aggregate.READ_ABSENT_fell_on_thin_tapes = blockReasonHistogram.aggregate.thin_tape_READ_ABSENT_after < blockReasonHistogram.aggregate.thin_tape_READ_ABSENT_before;
    if (isV52c) v52bAssertions.READ_ABSENT_falls_on_endogenous_thin_tapes = { observed_before: blockReasonHistogram.aggregate.thin_tape_READ_ABSENT_before, observed_after: blockReasonHistogram.aggregate.thin_tape_READ_ABSENT_after, pass: blockReasonHistogram.aggregate.READ_ABSENT_fell_on_thin_tapes };
    for (const [name, value] of Object.entries(v52bAssertions)) {
      if (name === "flow_assertions") continue;
      if (typeof value.pass === "boolean") continue;
      value.pass = name === "REFLEX_POST_zero" ? value.observed === value.expected : value.violations.length === 0;
    }
    v52bAssertions.pass = candidateFlow.pass && Object.entries(v52bAssertions).filter(([name]) => name !== "flow_assertions" && name !== "pass").every(([, value]) => value.pass);
    if (libraryBackedEvidenceSummary) libraryBackedEvidenceSummary.pre_stated_claims.REFLEX_POST_zero = v52bAssertions.REFLEX_POST_zero.observed === 0;
    if (macroRecognitionSummary) {
      macroRecognitionSummary.pins.lawful = v52bAssertions.pins_lawful_not_outcome_bound.pass;
      macroRecognitionSummary.REFLEX_POST_zero = v52bAssertions.REFLEX_POST_zero.observed === 0;
    }
    if (benchmarkRoleSummary) {
      benchmarkRoleSummary.pins.lawful = v52bAssertions.pins_lawful_not_outcome_bound.pass;
      benchmarkRoleSummary.REFLEX_POST_zero = v52bAssertions.REFLEX_POST_zero.observed === 0;
    }
    const eventFor = (label) => {
      const pinned = activeReadCohort.pins.filter((row) => row.code.endsWith(label));
      ensure(pinned.length === 1, `named pin ${label} found ${pinned.length}`);
      const matches = candidateRun.marketEvents.filter((event) => event.event_id === pinned[0].event_id);
      ensure(matches.length === 1, `named ${label} found ${matches.length}`);
      return matches[0];
    };
    const namedRows = Object.fromEntries(["ARSMAR", "SANDAN", "PUTJEA", "POLKUH", "MERDRO"].map((label) => {
      const event = eventFor(label);
      const actions = candidateRun.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && row.event_id === event.event_id);
      return [label, { event_id: event.event_id, completed_observation: event.completed_pair, combined_entry_cents_observation: event.combined_entry_cents, legs: Object.fromEntries(Object.entries(event.legs).sort(([a], [b]) => a.localeCompare(b)).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, final_state: leg.final_state, terminal_reason: leg.terminal_reason, gate_posts: leg.judgment_gate_posts, gate_blocks: leg.judgment_gate_blocks }])), rest_mutations: actions.filter((row) => ["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE", "GAP_CREDIT_REPRICE_DOWN"].includes(row.kind)) }];
    }));
    if (isV52h) namedRows.SMIILA = smiilaObservation;
    const polKuh = namedRows.POLKUH.legs;
    const v52bNamedChecks = {
      ARSMAR_completes_at_lawful_levels: namedRows.ARSMAR.completed_observation,
      SANDAN_DAN_uncapped_by_displayed_premium: namedRows.SANDAN.rest_mutations.filter((row) => row.leg_identity.endsWith("|DAN")).every((row) => row.birth_license?.level?.authority === "V52B_EVIDENCE_BACKED_MACHINE_READ_LEVEL" && row.birth_license?.level?.displayed_bid_consumed === false),
      PUTJEA_real_levels_or_lawful_sit_out: namedRows.PUTJEA.rest_mutations.every((row) => row.birth_license?.level?.authority === "V52B_EVIDENCE_BACKED_MACHINE_READ_LEVEL" && row.birth_license?.level?.displayed_bid_consumed === false),
      POLKUH_KUH_licensed_credit: polKuh.KUH?.credited === true,
      POLKUH_POL_lawful_abstention: polKuh.POL?.credited === false && polKuh.POL?.final_state === "NEVER_PLACED_OR_CANCELLED",
      MERDRO_not_credited_as_judgment: Object.values(namedRows.MERDRO.legs).every((leg) => !leg.credited),
    };
    const merDroEvent = eventFor("MERDRO"), merDroBase = baseByEvent.get(merDroEvent.event_id);
    const merDroFormationPrints6 = Object.values(merDroEvent.legs).flatMap((leg) => {
      const onsetTimestamp = leg.v52_onset?.selected?.timestamp_epoch;
      return Number.isFinite(onsetTimestamp) ? (printLoad.byTicker.get(leg.ticker) || []).filter((row) => row.price === 6 && row.ts < onsetTimestamp).map((row) => ({ leg_identity: leg.leg_identity, timestamp_epoch: row.ts, receipt: row.receipt, trade_id: row.trade_id, price_cents: row.price, size: row.size, onset_timestamp_epoch: onsetTimestamp })) : [];
    });
    const merDroFillActions = candidateRun.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && row.event_id === merDroEvent.event_id && row.kind === "FILL");
    const merDroFormationReceipts = new Set(merDroFormationPrints6.map((row) => row.receipt));
    const merDroPostOnsetCredits = merDroFillActions.map((row) => {
      const leg = merDroEvent.legs[row.leg_identity.split("|").at(-1)];
      const priorLicensedPost = namedRows.MERDRO.rest_mutations.filter((action) => action.leg_identity === row.leg_identity && action.timestamp_epoch <= row.timestamp_epoch && action.birth_license?.onset?.passed && action.birth_license?.read?.passed && action.birth_license?.coherence?.lows_under_par && action.birth_license?.coherence?.disagreement_clear).at(-1) ?? null;
      return { leg_identity: row.leg_identity, fill_timestamp_epoch: row.timestamp_epoch, fill_receipt: row.receipt, fill_price_cents: row.entry_cents, onset_timestamp_epoch: leg?.v52_onset?.selected?.timestamp_epoch ?? null, after_onset: Boolean(leg?.v52_onset?.selected && row.timestamp_epoch >= leg.v52_onset.selected.timestamp_epoch), licensed_post_receipt: priorLicensedPost?.receipt ?? null, licensed_post_target_cents: priorLicensedPost?.target_cents ?? null, licensed_before_credit: Boolean(priorLicensedPost), formation_6c_receipt_consumed: merDroFormationReceipts.has(row.receipt) };
    });
    const v52cNamedChecks = {
      ARSMAR_observation_only: namedRows.ARSMAR.completed_observation,
      SANDAN_clause_3_frozen: namedRows.SANDAN.rest_mutations.every((row) => row.birth_license?.level?.authority === "V52B_EVIDENCE_BACKED_MACHINE_READ_LEVEL"),
      PUTJEA_clause_3_frozen_or_lawful_sit_out: namedRows.PUTJEA.rest_mutations.every((row) => row.birth_license?.level?.authority === "V52B_EVIDENCE_BACKED_MACHINE_READ_LEVEL"),
      POLKUH_observation_only_KUH_credit: polKuh.KUH?.credited === true,
      MERDRO_formation_era_6c_prints_not_credited: merDroFormationPrints6.length > 0 && merDroPostOnsetCredits.every((row) => !row.formation_6c_receipt_consumed),
      MERDRO_post_onset_judgment_credits_lawful: merDroPostOnsetCredits.length > 0 && merDroPostOnsetCredits.every((row) => row.after_onset && row.licensed_before_credit),
    };
    const namedChecks = (isV52c || isV52d || isV52e) ? {
      ...v52cNamedChecks,
      ...(isV52k ? {
        GUEGOM_named_observation_carried: Boolean(guegomObservation?.event_id?.includes("GUEGOM")),
        zero_COMPLETE_AT_LOSS: candidateFourStateRows.every((row) => row.state !== "COMPLETE_AT_LOSS"),
        pins_unharmed: pinComparisons.every((row) => row.unharmed),
        disagreement_referee_untouched: candidateFlow.trace.filter((row) => row.coherence?.disagreement_firing && !row.coherence?.disagreement_clear).every((row) => row.blocked_clause === "FIRING_DISAGREEMENT_ACTIVE"),
      } : isV52h ? {
        SMIILA_pair_par_block_converted: smiilaObservation.pair_par_block_converted,
        zero_COMPLETE_AT_LOSS: candidateFourStateRows.every((row) => row.state !== "COMPLETE_AT_LOSS"),
        pins_unharmed: pinComparisons.every((row) => row.unharmed),
        disagreement_referee_untouched: candidateFlow.trace.filter((row) => row.coherence?.disagreement_firing && !row.coherence?.disagreement_clear).every((row) => row.blocked_clause === "FIRING_DISAGREEMENT_ACTIVE"),
      } : isV52g ? {
        VANDRO_remains_lawful: v52gPriorLossReattestation.named_cases.find((row) => row.code.endsWith("VANDRO"))?.remains_lawful_under_V52g_identity ?? false,
        ZHEBOU_remains_lawful: v52gPriorLossReattestation.named_cases.find((row) => row.code.endsWith("ZHEBOU"))?.remains_lawful_under_V52g_identity ?? false,
        BERSAI_remains_lawful: v52gPriorLossReattestation.named_cases.find((row) => row.code.endsWith("BERSAI"))?.remains_lawful_under_V52g_identity ?? false,
        BARYUA_remains_lawful: v52gPriorLossReattestation.named_cases.find((row) => row.code.endsWith("BARYUA"))?.remains_lawful_under_V52g_identity ?? false,
        zero_new_COMPLETE_AT_LOSS: v52gPriorLossReattestation.zero_new_COMPLETE_AT_LOSS_in_fresh_30,
        pins_unharmed: pinComparisons.every((row) => row.unharmed),
        SANDAN_at_or_better: sandanPin?.at_or_better ?? false,
      } : isV52f ? {
        VANDRO_converted_from_COMPLETE_AT_LOSS: v52fClaimRows.find((row) => row.code.endsWith("VANDRO"))?.converted_from_COMPLETE_AT_LOSS_to_lawful_outcome ?? false,
        ZHEBOU_converted_from_COMPLETE_AT_LOSS: v52fClaimRows.find((row) => row.code.endsWith("ZHEBOU"))?.converted_from_COMPLETE_AT_LOSS_to_lawful_outcome ?? false,
        BERSAI_converted_from_COMPLETE_AT_LOSS: v52fClaimRows.find((row) => row.code.endsWith("BERSAI"))?.converted_from_COMPLETE_AT_LOSS_to_lawful_outcome ?? false,
        BARYUA_converted_from_COMPLETE_AT_LOSS: v52fClaimRows.find((row) => row.code.endsWith("BARYUA"))?.converted_from_COMPLETE_AT_LOSS_to_lawful_outcome ?? false,
        zero_new_COMPLETE_AT_LOSS: v52fPreStatedClaim.zero_new_COMPLETE_AT_LOSS,
      } : {}),
    } : v52bNamedChecks;
    namedRows.MERDRO.authoring_correction = { formation_era_6c_prints: merDroFormationPrints6, post_onset_judgment_credits: merDroPostOnsetCredits, law: "FORMATION_ERA_6C_PRINTS_NOT_CREDITED; POST_ONSET_LICENSED_JUDGMENT_CREDITS_LAWFUL" };
    const actionStream = (run, eventId, legIdentity) => run.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && row.event_id === eventId && row.leg_identity === legIdentity).map(({ machine, ...row }) => row);
    const streamDiffs = [];
    const behaviorStreamDiffs = [];
    const behaviorFields = (row) => ({ kind: row.kind, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, target_cents: row.target_cents ?? null, prior_target_cents: row.prior_target_cents ?? null, entry_cents: row.entry_cents ?? null, fill_class: row.fill_class ?? null, reason: row.reason ?? null });
    for (const event of candidateRun.marketEvents) for (const leg of Object.values(event.legs)) {
      const before = actionStream(baselineRun, event.event_id, leg.leg_identity), after = actionStream(candidateRun, event.event_id, leg.leg_identity);
      const beforeSha = shaCanonicalRows(before), afterSha = shaCanonicalRows(after);
      if (beforeSha !== afterSha) streamDiffs.push({ event_id: event.event_id, leg_identity: leg.leg_identity, before_sha256: beforeSha, after_sha256: afterSha, first_difference: decisionDiffs.find((row) => row.leg_identity === leg.leg_identity) ?? null });
      const beforeBehavior = before.map(behaviorFields), afterBehavior = after.map(behaviorFields);
      const beforeBehaviorSha = shaCanonicalRows(beforeBehavior), afterBehaviorSha = shaCanonicalRows(afterBehavior);
      if (beforeBehaviorSha !== afterBehaviorSha) {
        const count = Math.max(beforeBehavior.length, afterBehavior.length);
        let firstIndex = 0; while (firstIndex < count && canonical(beforeBehavior[firstIndex] ?? null) === canonical(afterBehavior[firstIndex] ?? null)) firstIndex += 1;
        const firstBoundCandidates = candidateFlow.trace.filter((row) => row.event_id === event.event_id && (isV52r ? row.macro_recognition?.trd5?.gate_passed === true && row.macro_recognition?.bound_role !== null : isV52q ? row.macro_recognition?.candidate_role !== null : isV52p ? row.macro_recognition?.ripeness?.verified_binding === true : isV52o ? row.benchmarked_role_instrument?.benchmark_role?.signable === true : isV52n ? Boolean(row.recognition_confidence_gate) : isV52m ? row.per_shape_floor_depth?.applicable === true : isV52l ? (() => {
          const before = baselineTrace.get(traceKey(row));
          return before && canonical(onsetLawFields(before.onset)) !== canonical(onsetLawFields(row.onset));
        })() : isV52k ? row.library_backed_level_evidence?.target_changed === true : isV52j ? row.role_conditioned_level_selection?.target_changed === true : isV52i ? row.depth_informed_level_selection?.target_changed === true : isV52h ? baselineTrace.get(traceKey(row))?.blocked_clause === "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR" && row.blocked_clause !== "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR" : isV52g ? row.joint_target_conservation?.target_changed === true : row.pair_entry_conservation?.target_changed === true));
        const firstBound = firstBoundCandidates.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.leg_identity.localeCompare(b.leg_identity) || a.receipt.localeCompare(b.receipt))[0] ?? null;
        const changedCandidates = [beforeBehavior[firstIndex], afterBehavior[firstIndex]].filter(Boolean);
        const firstChangedTimestamp = changedCandidates.length ? Math.min(...changedCandidates.map((row) => row.timestamp_epoch)) : null;
        behaviorStreamDiffs.push({ event_id: event.event_id, leg_identity: leg.leg_identity, attribution_grain: "PAIR_IS_ENTRY_UNIT", before_sha256: beforeBehaviorSha, after_sha256: afterBehaviorSha, first_difference_index: firstIndex, before: beforeBehavior[firstIndex] ?? null, after: afterBehavior[firstIndex] ?? null, first_authorized_bound_receipt_in_game: firstBound ? { leg_identity: firstBound.leg_identity, timestamp_epoch: firstBound.timestamp_epoch, receipt: firstBound.receipt, authorized_clause: isV52r ? { recognition: firstBound.macro_recognition, level: firstBound.assembled_policy } : isV52q ? { anchor_correction: firstBound.macro_recognition?.anchor_correction, ripeness: firstBound.macro_recognition?.ripeness } : isV52p ? firstBound.macro_recognition?.ripeness : isV52o ? firstBound.benchmarked_role_instrument : isV52n ? firstBound.recognition_confidence_gate : isV52m ? firstBound.per_shape_floor_depth : isV52l ? { clause: "CLAUSE_1_CAUSAL_STABILITY_ONSET", onset: firstBound.onset } : isV52k ? firstBound.library_backed_level_evidence : isV52j ? firstBound.role_conditioned_level_selection : isV52i ? firstBound.depth_informed_level_selection : isV52h ? firstBound.clause_4_market_proof_precondition : isV52g ? firstBound.joint_target_conservation : firstBound.pair_entry_conservation } : null, first_behavior_difference_timestamp_epoch: firstChangedTimestamp, first_behavior_difference_not_before_authorized_clause: Boolean(firstBound && Number.isFinite(firstChangedTimestamp) && firstChangedTimestamp >= firstBound.timestamp_epoch) });
      }
    }
    if (isV52f || isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ensure(behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause), `${iterationLabel} behavior changed before authorized clause ${behaviorStreamDiffs.find((row) => !row.first_behavior_difference_not_before_authorized_clause)?.leg_identity}`);
    const frozenV52PolicyPath = "arb-executor/analysis/window1_v52_judgment_gate.js";
    const frozenV52PolicyBytes = gitShow(V52_COMMIT, frozenV52PolicyPath);
    const currentV52PolicyBytes = fs.readFileSync(path.join(repo, frozenV52PolicyPath));
    ensure(shaBytes(frozenV52PolicyBytes) === shaBytes(currentV52PolicyBytes), "frozen V52 policy changed");
    const frozenV52bPolicyPath = "arb-executor/analysis/window1_v52b_read_level_authority.js";
    const frozenV52bPolicyBytes = (isV52c || isV52d || isV52e) ? gitShow(V52B_COMMIT, frozenV52bPolicyPath) : fs.readFileSync(path.join(repo, frozenV52bPolicyPath));
    const currentV52bPolicyBytes = fs.readFileSync(path.join(repo, frozenV52bPolicyPath));
    ensure(shaBytes(frozenV52bPolicyBytes) === shaBytes(currentV52bPolicyBytes), "frozen V52b clause-3 policy changed");
    if (isV52c || isV52d) {
      ensure(policy.machineReadLevel === frozenV52bPolicy.machineReadLevel, "V52c changed clause-3 machineReadLevel function");
      ensure(policy.gateDecision === frozenV52bPolicy.gateDecision, "V52c changed frozen gate decision function");
      ensure(policy.firstFailure === frozenV52bPolicy.firstFailure, "V52c changed frozen failure ordering");
    }
    if (isV52d || isV52e) {
      ensure(policy.fullPostOnsetRead === frozenV52cPolicy.fullPostOnsetRead, "V52d changed frozen clause-2 fullPostOnsetRead function");
      ensure(policy.fullPostOnsetAuthority === frozenV52cPolicy.fullPostOnsetAuthority, "V52d changed frozen clause-2 authority function");
    }
    if (isV52f || isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) {
      const frozenV52eBytes = gitShow(V52E_COMMIT, "arb-executor/analysis/window1_v52e_palantir_wiring.js");
      ensure(shaBytes(frozenV52eBytes) === fileHash(path.join(repo, "arb-executor/analysis/window1_v52e_palantir_wiring.js")), "frozen V52e policy bytes changed");
      ensure(policy.machineReadLevel === frozenV52ePolicy.machineReadLevel && policy.tradeTruthCredit === frozenV52ePolicy.tradeTruthCredit && (isV52DepthValidation || policy.continuousConsultation === frozenV52ePolicy.continuousConsultation), "later iteration changed a frozen V52e clause function");
    }
    if (isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) {
      const frozenV52fBytes = gitShow(V52F_COMMIT, "arb-executor/analysis/window1_v52f_pair_entry_conservation.js");
      ensure(shaBytes(frozenV52fBytes) === fileHash(path.join(repo, "arb-executor/analysis/window1_v52f_pair_entry_conservation.js")), "frozen V52f policy bytes changed");
      ensure(policy.fullPostOnsetRead === frozenV52fPolicy.fullPostOnsetRead && policy.tradeTruthCredit === frozenV52fPolicy.tradeTruthCredit, "V52g changed frozen V52f upstream functions");
    }
    if (isV52h || isV52DepthValidation || isV52CausalOnset) {
      const frozenV52gBytes = gitShow(V52G_COMMIT, "arb-executor/analysis/window1_v52g_joint_target_conservation.js");
      ensure(shaBytes(frozenV52gBytes) === fileHash(path.join(repo, "arb-executor/analysis/window1_v52g_joint_target_conservation.js")), "frozen V52g policy bytes changed");
      ensure(policy.jointTargetConservation === frozenV52gPolicy.jointTargetConservation, "V52h changed V52g joint target conservation");
    }
    if (isV52DepthValidation || isV52CausalOnset) {
      const frozenV52hBytes = gitShow(V52H_COMMIT, "arb-executor/analysis/window1_v52h_remove_pair_lows_precondition.js");
      ensure(shaBytes(frozenV52hBytes) === fileHash(path.join(repo, "arb-executor/analysis/window1_v52h_remove_pair_lows_precondition.js")), "frozen V52h policy bytes changed");
      ensure(policy.marketProofReceipt === frozenV52hPolicy.marketProofReceipt && policy.settlementIdentity === frozenV52hPolicy.settlementIdentity && policy.jointTargetConservation === frozenV52hPolicy.jointTargetConservation && policy.tradeTruthCredit === frozenV52hPolicy.tradeTruthCredit, `${iterationLabel} changed a frozen V52h clause function`);
    }
    const step0ReuseInventory = isV52e ? {
      law: "REUSE_EXISTING_CONSULTATION_MACHINERY; PARALLEL_DISCOVERY_OR_FALLBACK_LOADER_IS_A_DEFECT",
      components: [
        { component: "vault-wired entry ten-surface dossier assembly", symbol: "live_v4.py::_entry_dossier", source: { file: "arb-executor/live_v4.py", line: localLine("arb-executor/live_v4.py", "def _entry_dossier") }, disposition: "REUSED", exact_role: "DOSSIER_ASSEMBLY_AND_PER-SURFACE_PROVENANCE_CONTRACT", runtime_note: "REPLAY_EMITS_THE_SAME_ASSET_SHA_STATUS_FIELDS_IN_EVERY_LICENSE; LIVE_ENTRY_CODE_NOT_MODIFIED" },
        { component: "C-ONE-TRUTH surface registry", symbol: "live_v4.py boot truth/INDEX.json", source: { file: "arb-executor/live_v4.py", line: localLine("arb-executor/live_v4.py", "# [C-ONE-TRUTH v1") }, disposition: "RE-POINTED", exact_role: "SINGLE_REGISTRY_SEMANTICS_REPOINTED_TO_PINNED_MACHINE_PALANTIR.store_CLEAN", target: { commit: MACHINE_PALANTIR_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/MACHINE_PALANTIR.json", sha256: n9Binding.store.manifest_sha256 } },
        { component: "entry table loader", symbol: "live_v4.py::_load_entry_table", source: { file: "arb-executor/live_v4.py", line: localLine("arb-executor/live_v4.py", "def _load_entry_table") }, disposition: "RE-POINTED", exact_role: "P1_GRID_BYTES_READ_THROUGH_EXISTING_PINNED_GIT_OBJECT_PATH_AND_VALIDATED_BY_CLEAN_REGISTRY" },
        { component: "aim atlas loader", symbol: "live_v4.py::_aim_load", source: { file: "arb-executor/live_v4.py", line: localLine("arb-executor/live_v4.py", "def _aim_load") }, disposition: "RETIRED-WITH-REASON", reason: "HOT_MUTABLE_ATLAS_NOT_A_HASH-BOUND_CLEAN_N9_ASSET" },
        { component: "trend-path ATLAS loader", symbol: "live_v4.py::_trendpath_atlas", source: { file: "arb-executor/live_v4.py", line: localLine("arb-executor/live_v4.py", "def _trendpath_atlas") }, disposition: "RETIRED-WITH-REASON", reason: "MTIME-HOT-RELOAD_AND_PRE-MIGRATION_ATLAS_IS_SUPERSEDED_IN_MACHINE_PALANTIR" },
        { component: "cohort surface loader", symbol: "live_v4.py::_cohort_surface", source: { file: "arb-executor/live_v4.py", line: localLine("arb-executor/live_v4.py", "def _cohort_surface") }, disposition: "RETIRED-WITH-REASON", reason: "MUTABLE_COHORT_SURFACE_NOT_PRESENT_IN_CLEAN_STORE_AND_NO_FALLBACK_ALLOWED" },
        { component: "BCASC maps loader", symbol: "live_v4.py::_bcasc_maps", source: { file: "arb-executor/live_v4.py", line: localLine("arb-executor/live_v4.py", "def _bcasc_maps") }, disposition: "RETIRED-WITH-REASON", reason: "NOT_A_REQUIRED_CLEAN_N2_N4_N5_ASSET" },
        { component: "N8 frozen-chain organ loads", source: { commit: "2af60dfc", path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DECISION_WEB.json" }, disposition: "REUSED", exact_role: "FROZEN_V52D_INCUMBENT_UNGUARDED_DECISION_AND_TARGET_CHAIN; N9_CONSULTS_BESIDE_IT" },
        { component: "pinned Git object loader", symbol: "build_window1_v38_maker_only.js::gitShow", source: { file: "arb-executor/analysis/build_window1_v38_maker_only.js", line: localLine("arb-executor/analysis/build_window1_v38_maker_only.js", "function gitShow") }, disposition: "REUSED", exact_role: "ONLY_BYTE_READER_FOR_MACHINE_PALANTIR_AND_ALL_N9_ASSETS" },
        { component: "CLEAN-store adapter", symbol: "window1_n9_clean_store.js::makeCleanStore", source: { file: "arb-executor/analysis/window1_n9_clean_store.js", line: localLine("arb-executor/analysis/window1_n9_clean_store.js", "function makeCleanStore") }, disposition: "REUSED", exact_role: "NO_DISCOVERY_NO_FALLBACK_STATUS_AND_PROVENANCE_ASSERTION; VALIDATOR_NOT_LOADER" },
      ],
      parallel_loader_built: false,
      byte_read_path: "EXISTING_gitShow_ONLY",
      adapter_role: "VALIDATE_AND_COMPACT_ALREADY_READ_BYTES_ONLY",
    } : null;
    const clauseReceipt = isV52r ? {
      authorized_change: "CLAUSE_3_TRD5_ROLE_AND_LOW_MINUS_ONE_ASSEMBLY_ONLY",
      parent: { commit: V52Q_COMMIT, observations_retained: ["V52M", "V52N", "V52P", "V52Q"] },
      behavioral_lineage: { policy: "V52L", commit: V52L_COMMIT, adopted_by_operator: true },
      recognition: { name: "TRD5", threshold_post_onset_trades: policy.TRD5_MIN_POST_ONSET_TRADES, coordinate_zero: "max(causal_onset,formation_end)", bind: "FIRST_GATE_CROSSING_WITH_DIRECTIONAL_CALL", persistence: "HOLD_UNLESS_INSTRUMENT_FLIPS", corrected_anchor: v52qAnchorBinding, provenance: v52rTRD5Binding.provenance },
      level: { ROLE_DOWN: "RUNNING_POST_ONSET_SESSION_LOW_MINUS_ONE_REEVALUATED_ON_NEW_LOW", delta_cents: policy.LOW1_DELTA_CENTS, identity: "TRAIL1_IDENTICAL_TO_LOW_1_ON_INTEGER_TAPE", bounds: ["CURRENT_TOUCH_ABOVE", "CLAUSE_6_JOINT_LAW"], provenance: v52rLOW1Binding.provenance },
      defaults: { ROLE_UP: "V52L_AT_WAKE_EVIDENCE_BACKED_LEVEL", ROLE_STILL: "V52L_DEFAULT", ABSTAIN: "V52L_DEFAULT", static_shape_depth_consumed: false },
      frozen_clauses: { clause_1_causal_onset: true, clause_2: true, clause_4_and_referee: true, clause_5: true, clause_6: true, crediting: "TRADES_AS_TRUTH_UNCHANGED", scavenger: false, REFLEX_POST: v52bAssertions.REFLEX_POST_zero.observed },
      both_clocks: { trace_fields: ["t_minus_scheduled_seconds", "t_minus_actual_bell_seconds"], present_on_role_receipts: isV52r ? benchmarkRoleSummary.both_clocks_present_on_role_receipts : benchmarkRoleSummary.role_receipts.every((row) => Object.hasOwn(row, "t_minus_scheduled_seconds") && Object.hasOwn(row, "t_minus_actual_bell_seconds")) },
      ground_truth_grading_binding: groundTruthWindowBinding.binding,
      differential: { changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_TRD5_binding: behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause), frozen_pre_authorized_differences: frozenClauseDiffs.length, authorized_downstream_input_divergences: downstreamFrozenInputDivergences.length },
      pre_stated_claims: { runtime_offline_parity: benchmarkRoleSummary.runtime_vs_offline_parity, coverage: benchmarkRoleSummary.coverage, accuracy: benchmarkRoleSummary.accuracy, ROLE_DOWN_fills: benchmarkRoleSummary.ROLE_DOWN_fills, up_and_still_completion_preservation: benchmarkRoleSummary.up_and_still_completion_preservation, banked_delta: benchmarkRoleSummary.banked_delta, one_sided_exposure_both_ways: benchmarkRoleSummary.one_sided_exposure_both_ways, pins_lawful: benchmarkRoleSummary.pins.lawful, REFLEX_POST_zero: benchmarkRoleSummary.REFLEX_POST_zero },
      disposition: "OBSERVATION_ONLY; ADOPT_OR_HOLD_RESERVED_TO_OPERATOR_AT_DOCK",
    } : isV52q ? {
      authorized_change: "CLAUSE_3_ROLE_ANCHOR_CORRECTION_ONLY",
      parent: { commit: V52P_COMMIT, observations_retained: ["V52M", "V52N", "V52O", "V52P"] },
      behavioral_lineage: { policy: "V52L", commit: V52L_COMMIT, adopted_by_operator: true },
      defect: { old_anchor: "FIRST_TRUE_PRINT_AT_OR_AFTER_FORMATION_END", corrected_anchor: "SPREAD_SETTLE_MID_AT_FORMATION_END", old_price_series_floor: "UNBOUND_PRE_FORMATION_PRINT_HISTORY", corrected_price_series_floor: "FORMATION_END_INCLUSIVE", discrepancy: v52qAnchorBinding.discrepancy },
      anchor_binding: v52qAnchorBinding,
      candidate_role_rule: benchmarkRoleSummary.rule_binding.rule,
      ripeness_binding: { source: v52pRipenessBinding.provenance, class_gates: policy.CLASS_GATES, category_gates: policy.CATEGORY_GATES, effective_gate: "max(class,category)", below_gate: "ABSTAIN_TO_V52L_AND_REEVALUATE_EVERY_RECEIPT" },
      depth_derivation: benchmarkRoleSummary.down_depth_aggregate_derivation,
      role_laws: { ROLE_DOWN: "CATEGORY_FREQUENCY_WEIGHTED_DOWN_FAMILY_DEPTH_TARGET_BOUNDED_BY_CURRENT_TOUCH_AND_CLAUSE_6", ROLE_UP: "IMMEDIATE_V52L_EVIDENCE_BACKED_LEVEL", ROLE_STILL: "V52L_DEFAULT", ABSTAIN: "V52L_DEFAULT_REEVALUATED_EVERY_RECEIPT" },
      frozen_clauses: { clause_1_causal_onset: true, clause_2: true, clause_4_and_referee: true, clause_5: true, clause_6: true, crediting: "TRADES_AS_TRUTH_UNCHANGED", scavenger: false, REFLEX_POST: v52bAssertions.REFLEX_POST_zero.observed },
      ground_truth_grading_binding: groundTruthWindowBinding.binding,
      differential: { changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_corrected_anchor_role_binding: behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause), frozen_pre_authorized_differences: frozenClauseDiffs.length, authorized_downstream_input_divergences: downstreamFrozenInputDivergences.length },
      pre_stated_claims: { runtime_offline_parity: benchmarkRoleSummary.runtime_offline_anchor_parity, coverage: benchmarkRoleSummary.coverage, accuracy: benchmarkRoleSummary.accuracy, ROLE_DOWN_fills: benchmarkRoleSummary.ROLE_DOWN_fills, up_and_still_completion_preservation: benchmarkRoleSummary.up_and_still_completion_preservation, banked_delta: benchmarkRoleSummary.banked_delta, one_sided_exposure_both_ways: benchmarkRoleSummary.one_sided_exposure_both_ways, pins_lawful: benchmarkRoleSummary.pins.lawful, REFLEX_POST_zero: benchmarkRoleSummary.REFLEX_POST_zero },
      disposition: "OBSERVATION_ONLY; ADOPT_OR_HOLD_RESERVED_TO_OPERATOR_AT_DOCK",
    } : isV52p ? {
      authorized_change: "CLAUSE_3_RIPENESS_GATED_ROLE_BINDING_ONLY",
      parent: { commit: V52O_COMMIT, observations_retained: ["V52M", "V52N", "V52O"] },
      behavioral_lineage: { policy: "V52L", commit: V52L_COMMIT, adopted_by_operator: true },
      candidate_role_rule: benchmarkRoleSummary.rule_binding.rule,
      ripeness_binding: { source: v52pRipenessBinding.provenance, class_gates: policy.CLASS_GATES, category_gates: policy.CATEGORY_GATES, effective_gate: "max(class,category)", below_gate: "ABSTAIN_TO_V52L_AND_REEVALUATE_EVERY_RECEIPT" },
      depth_derivation: benchmarkRoleSummary.down_depth_aggregate_derivation,
      role_laws: { ROLE_DOWN: "CATEGORY_FREQUENCY_WEIGHTED_DOWN_FAMILY_DEPTH_TARGET_BOUNDED_BY_CURRENT_TOUCH_AND_CLAUSE_6", ROLE_UP: "IMMEDIATE_V52L_EVIDENCE_BACKED_LEVEL", ROLE_STILL: "V52L_DEFAULT", ABSTAIN: "V52L_DEFAULT_REEVALUATED_EVERY_RECEIPT" },
      live_realizability: ripenessRoleSummary,
      frozen_clauses: { clause_1_causal_onset: true, clause_2: true, clause_4_and_referee: true, clause_5: true, clause_6: true, crediting: "TRADES_AS_TRUTH_UNCHANGED", scavenger: false, REFLEX_POST: v52bAssertions.REFLEX_POST_zero.observed },
      ground_truth_grading_binding: groundTruthWindowBinding.binding,
      differential: { changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_ripeness_binding: behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause), frozen_pre_authorized_differences: frozenClauseDiffs.length, authorized_downstream_input_divergences: downstreamFrozenInputDivergences.length },
      pre_stated_claims: { coverage: benchmarkRoleSummary.coverage, accuracy: benchmarkRoleSummary.accuracy, ROLE_DOWN_fills: benchmarkRoleSummary.ROLE_DOWN_fills, up_and_still_completion_preservation: benchmarkRoleSummary.up_and_still_completion_preservation, banked_delta: benchmarkRoleSummary.banked_delta, one_sided_exposure_both_ways: benchmarkRoleSummary.one_sided_exposure_both_ways, pins_lawful: benchmarkRoleSummary.pins.lawful, REFLEX_POST_zero: benchmarkRoleSummary.REFLEX_POST_zero },
      disposition: "OBSERVATION_ONLY; ADOPT_OR_HOLD_RESERVED_TO_OPERATOR_AT_DOCK",
    } : isV52o ? {
      authorized_change: "CLAUSE_3_BENCHMARKED_EARLY_ROLE_INSTRUMENT_ONLY",
      parent: { commit: V52N_COMMIT, observations_retained: ["V52M", "V52N"] },
      behavioral_lineage: { policy: "V52L", commit: V52L_COMMIT, adopted_by_operator: true },
      role_rule: benchmarkRoleSummary.rule_binding,
      depth_derivation: benchmarkRoleSummary.down_depth_aggregate_derivation,
      role_laws: { ROLE_DOWN: "CATEGORY_FREQUENCY_WEIGHTED_DOWN_FAMILY_DEPTH_TARGET_BOUNDED_BY_CURRENT_TOUCH_AND_CLAUSE_6", ROLE_UP: "IMMEDIATE_V52L_EVIDENCE_BACKED_LEVEL_CATCH_EARLY", ABSTAIN: "V52L_DEFAULT_REEVALUATED_EVERY_RECEIPT" },
      frozen_clauses: { clause_1_causal_onset: true, clause_2: true, clause_4_and_referee: true, clause_5: true, clause_6: true, crediting: "TRADES_AS_TRUTH_UNCHANGED", scavenger: false, REFLEX_POST: v52bAssertions.REFLEX_POST_zero.observed },
      ground_truth_grading_binding: groundTruthWindowBinding.binding,
      differential: { changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_benchmarked_role_call: behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause), frozen_pre_authorized_differences: frozenClauseDiffs.length, authorized_downstream_input_divergences: downstreamFrozenInputDivergences.length },
      pre_stated_claims: { coverage: benchmarkRoleSummary.coverage, accuracy: benchmarkRoleSummary.accuracy, ROLE_DOWN_fills: benchmarkRoleSummary.ROLE_DOWN_fills, up_and_still_completion_preservation: benchmarkRoleSummary.up_and_still_completion_preservation, banked_delta: benchmarkRoleSummary.banked_delta, one_sided_exposure_both_ways: benchmarkRoleSummary.one_sided_exposure_both_ways, pins_lawful: benchmarkRoleSummary.pins.lawful, REFLEX_POST_zero: benchmarkRoleSummary.REFLEX_POST_zero },
      disposition: "OBSERVATION_ONLY; ADOPT_OR_HOLD_RESERVED_TO_OPERATOR_AT_DOCK",
    } : isV52n ? {
      authorized_change: "CLAUSE_3_RECOGNITION_CONFIDENCE_GATE_ONLY",
      behavioral_base: { policy: "V52M", commit: V52M_COMMIT, parent_commit: V52M_COMMIT, V52l_lineage: V52L_COMMIT, depth_targeting_on_bound_down_families_unchanged: true },
      taxonomy: { method_commit: SHAPE_TAXONOMY_COMMIT, path: SHAPE_TAXONOMY_PATH, sha256: v52mShapeBinding.taxonomy_provenance.sha256, families: policy.FAMILY_ORDER, method: v52mShapeBinding.taxonomy.signature_method },
      floor_depth_table: { commit: SHAPE_FLOOR_DEPTH_COMMIT, path: SHAPE_FLOOR_DEPTH_PATH, sha256: v52mShapeBinding.floor_table_provenance.sha256, label: v52mShapeBinding.floor_tables.LABEL, stamp: v52mShapeBinding.floor_tables.stamp, rows: v52mShapeBinding.floor_tables.rows.length, early_call_method: v52mShapeBinding.floor_tables.method.early_call },
      confidence_gate: { law: "BIND_ONLY_WHEN_PINNED_FAMILY_MEDIAN_DECLARATION_IS_AT_OR_BEFORE_THE_TABLES_F05_CHECKPOINT_AND_THIS_RECEIPT_HAS_THE_TABLES_2C_DIRECTIONAL_DECLARATION; OTHERWISE_ABSTAIN_TO_V52L_AND_REATTEMPT_EVERY_RECEIPT", pinned_early_checkpoint_f: policy.PINNED_EARLY_CHECKPOINT_F, pinned_directional_declaration_cents: policy.PINNED_DIRECTIONAL_DECLARATION_CENTS, new_constants: 0, right_edge_consumed: false, full_span_fit_consumed: false },
      mechanical_repairs: [
        { defect: "INHERITED_V52M_WRAPPER_DROPPED_V45_GUARD_AUTHORITY_TERMINATED_RECEIPT_BIT_WHILE_RETAINING_GUARD_NULL", scope: "RECEIPT_STAMP_ONLY", action_target_and_predicates_changed: false, applied_symmetrically_to_frozen_V52m_control_and_V52n_candidate: true },
        { defect: "NAMED_CHECK_EXPORT_USED_SUFFIX_SUBSTRING_AND_COLLIDED_WITH_A_FRESH_EVENT_SHARING_ARSMAR", scope: "EXPORT_IDENTITY_LOOKUP_ONLY", correction: "EXACT_PINNED_EVENT_ID_FROM_COHORT_RECEIPT", action_target_predicates_and_outcomes_changed: false },
      ],
      frozen_clauses: { clause_1_causal_onset: true, clause_2: true, clause_3_depth_target_on_bound_down_family: true, clause_4_and_referee: true, clause_5: true, clause_6: true, crediting: "TRADES_AS_TRUTH_UNCHANGED", scavenger: false, REFLEX_POST: v52bAssertions.REFLEX_POST_zero.observed },
      ground_truth_grading_binding: groundTruthWindowBinding.binding,
      differential: { changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_confidence_gate: behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause), frozen_pre_authorized_differences: frozenClauseDiffs.length, authorized_downstream_input_divergences: downstreamFrozenInputDivergences.length },
      pre_stated_claims: { classifications: macroRecognitionSummary.classifications, down_family_fills: macroRecognitionSummary.down_family_fills, up_and_still_preservation: macroRecognitionSummary.up_and_still_preservation, banked_delta: macroRecognitionSummary.banked_delta, one_sided_exposure_both_ways: macroRecognitionSummary.one_sided_exposure_both_ways, pins_lawful: macroRecognitionSummary.pins.lawful, SANDAN: macroRecognitionSummary.pins.comparisons.find((row) => row.code === "26JUL13SANDAN") ?? null, REFLEX_POST_zero: macroRecognitionSummary.REFLEX_POST_zero },
      disposition: "OBSERVATION_ONLY; ADOPT_OR_HOLD_RESERVED_TO_OPERATOR_AT_DOCK",
    } : isV52m ? {
      authorized_change: "CLAUSE_3_CAUSAL_MACRO_RECOGNITION_FLOOR_DEPTH_ONLY",
      behavioral_base: { policy: "V52L", commit: V52L_COMMIT, adopted_by_operator: true, causal_onset_byte_behavior_frozen: true },
      taxonomy: { method_commit: SHAPE_TAXONOMY_COMMIT, path: SHAPE_TAXONOMY_PATH, sha256: v52mShapeBinding.taxonomy_provenance.sha256, families: policy.FAMILY_ORDER, method: v52mShapeBinding.taxonomy.signature_method },
      floor_depth_table: { commit: SHAPE_FLOOR_DEPTH_COMMIT, path: SHAPE_FLOOR_DEPTH_PATH, sha256: v52mShapeBinding.floor_table_provenance.sha256, label: v52mShapeBinding.floor_tables.LABEL, stamp: v52mShapeBinding.floor_tables.stamp, rows: v52mShapeBinding.floor_tables.rows.length },
      causal_classifier: { input: "TRUE_PRINT_HISTORY_AT_OR_BEFORE_EVALUATION_RECEIPT_ONLY", sample_points: policy.SAMPLE_POINTS, completed_path_consumed: false, right_edge_consumed: false, abstain_families: [...policy.ABSTAIN_FAMILIES].sort(), abstain_behavior: "FROZEN_V52L" },
      consumption_law: "SIGNABLE_FAMILY_MEDIAN_DEPTH_BELOW_CAUSAL_OPEN_NAMES_THE_LEVEL_TARGET; CURRENT_ASK_MINUS_ONE_AND_CLAUSE_6_BOUND_IT; THE_TABLE_INFORMS_LEVEL_AND_NEVER_GATES_THE_LICENSE",
      frozen_clauses: { clause_1_causal_onset: true, clause_2: true, clause_4_and_referee: true, clause_5: true, clause_6: true, crediting: "TRADES_AS_TRUTH_UNCHANGED", scavenger: false, REFLEX_POST: v52bAssertions.REFLEX_POST_zero.observed },
      ground_truth_grading_binding: groundTruthWindowBinding.binding,
      differential: { changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_macro_target: behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause), frozen_pre_authorized_differences: frozenClauseDiffs.length, authorized_downstream_input_divergences: downstreamFrozenInputDivergences.length },
      pre_stated_claims: { classifications: macroRecognitionSummary.classifications, down_family_fills: macroRecognitionSummary.down_family_fills, up_and_still_preservation: macroRecognitionSummary.up_and_still_preservation, banked_delta: macroRecognitionSummary.banked_delta, one_sided_exposure_both_ways: macroRecognitionSummary.one_sided_exposure_both_ways, pins_lawful: macroRecognitionSummary.pins.lawful, REFLEX_POST_zero: macroRecognitionSummary.REFLEX_POST_zero },
      disposition: "OBSERVATION_ONLY; ADOPT_OR_HOLD_RESERVED_TO_OPERATOR_AT_DOCK",
    } : isV52l ? {
      authorized_change: "CLAUSE_1_CAUSAL_STABILITY_ONSET_ONLY",
      behavioral_base: { policy: "V52H", commit: V52H_COMMIT, policy_module_byte_identical: true },
      before: "FULL_SPAN_INTERIM_ONSET_FIT_COULD_CONSUME_RECEIPTS_AFTER_THE_EVALUATION_MOMENT_AND_DEPEND_ON_THE_WINDOW_RIGHT_EDGE",
      after: "EACH_ONSET_CANDIDATE_IS_EVALUATED_ON_SEQUENTIAL_PREFIXES_AND_CONSUMES_ONLY_RECEIPTS_AT_OR_BEFORE_THAT_EVALUATION; FIRST_SUPPORTED_PREFIX_FIXES_RECOGNITION",
      candidates_preserved: ["A_SPREAD_COLLAPSE_PLUS_CROSS_LEG_MIDSUM_SETTLE", "B_SUSTAINED_TRADE_CADENCE_ARRIVAL"],
      constants_preserved_not_refit: { grid_seconds: causalOnsetPolicy.GRID_SECONDS, trade_cadence_seconds: causalOnsetPolicy.TRADE_CADENCE_SECONDS },
      right_edge_independence: rightEdgeIndependenceReceipt,
      onset_timing_shifts: onsetTimingShiftReceipt,
      frozen_clauses: { clause_2: true, clause_3: true, clause_4_and_referee: true, clause_5: true, clause_6: true, crediting: "TRADES_AS_TRUTH_UNCHANGED", scavenger: false, REFLEX_POST: v52bAssertions.REFLEX_POST_zero.observed },
      ground_truth_grading_binding: groundTruthWindowBinding.binding,
      differential: { changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_causal_onset: behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause), frozen_pre_authorized_differences: frozenClauseDiffs.length, authorized_downstream_input_divergences: downstreamFrozenInputDivergences.length },
      pre_stated_claims: {
        zero_onset_values_change_under_right_edge_perturbation: rightEdgeIndependenceReceipt.pass,
        onset_timing_shifts_reported_per_leg: onsetTimingShiftReceipt.conservation.pass,
        pin_lawfulness_holds_outcomes_may_move: v52bAssertions.pins_lawful_not_outcome_bound,
        REFLEX_POST_zero: v52bAssertions.REFLEX_POST_zero.observed === 0,
      },
      lineage_disposition: "OBSERVATION_ONLY; ADOPT_OR_HOLD_RESERVED_TO_OPERATOR_AT_DOCK",
    } : isV52k ? {
      authorized_change: "CLAUSE_3_LIBRARY_BACKED_LEVEL_EVIDENCE_ONLY",
      behavioral_base: { policy: "V52H", commit: V52H_COMMIT, direct_import: true },
      reverted_non_validating_iterations: { V52i: V52I_COMMIT, V52j: V52J_COMMIT, inherited_behavior: false },
      law: "A_LEVEL_IS_EVIDENCE_BACKED_BY_THIS_GAME_POST_ONSET_TAPE_OR_BY_GRID_PLUS_G3_LIBRARY_EVIDENCE; LIBRARY_MAY_LICENSE_BELOW_SHOWN_RANGE_BUT_NEVER_BELOW_ITS_OWN_SUPPORTED_FLOOR_OR_AT_ABOVE_CURRENT_TOUCH; CLAUSE_6_REMAINS_BINDING",
      weighting_law_reused_not_refit: "ROUND(G_GRID_DISCOUNT*G3_RECOVERY + G3_MEDIAN_DIP_DEPTH*(1-G3_RECOVERY))",
      constants_added: 0,
      timing_rules_added: 0,
      assets: {
        G_GRID: { id: "G_GRID_LEVEL_DISCOUNT", source_asset: "P1_THE_GRID", canonical_asset_status_unchanged: "VALIDATED", behavioral_role: "UNDER-VALIDATION_CONTINUED_V52K" },
        G3: { id: "G3_DIP_RECOVERY_GRADIENT", source_asset: "G3", source_commit: GREEK_INSTRUMENTS_COMMIT, canonical_status: "UNVALIDATED-CANDIDATE", behavioral_role: "UNDER-VALIDATION_CONTINUED_V52K" },
      },
      authority_union: { post_onset_tape: true, validated_library: true, library_can_create_clause_3_authority: true, library_can_bypass_clause_2_read: false, current_touch_upper_bound: true, library_floor_lower_bound: true, clause_6_joint_sum: true },
      clean_store: { canonical_manifest_unchanged: true, exact_under_validation_aliases: n9Binding.store.boot_assertion.under_validation_loaded_ids, boot_assertion: n9Binding.store.boot_assertion },
      frozen_clauses: { clause_1: true, clause_2: true, clause_4_and_referee: true, clause_5: true, clause_6: true, crediting: "TRADES_AS_TRUTH_UNCHANGED", scavenger: false, REFLEX_POST: v52bAssertions.REFLEX_POST_zero.observed },
      differential: { changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_library_evidence: behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause), frozen_pre_authorized_differences: frozenClauseDiffs.length },
      pre_stated_claims: libraryBackedEvidenceSummary.pre_stated_claims,
      floor_basis: { status: "CURRENT_PRE_RE-CUT", source: entryLaterFloorComparison.floor_source, future_analysis_regrade_required: true },
    } : isV52j ? {
      authorized_change: "CLAUSE_3_N4_ROLE_CONDITIONED_LEVEL_SELECTION_ONLY",
      V52i_disposition: "REVERTED; V52J_CALLS_FROZEN_V52H_DIRECTLY_AND_DOES_NOT_INHERIT_SYMMETRIC_DEPTH_REFINEMENT",
      law: "FALLING_USES_CELL_PRIOR_EXPECTED_FLOOR_DEPTH; RISING_USES_OWN_NEAR_SUPPORT; SETTLED_OR_INSUFFICIENT_RETAINS_FROZEN_EVIDENCE_BACKED_LEVEL",
      role_inputs: ["OWN_CURRENT_READ", "SIBLING_CURRENT_READ", "ALREADY_LICENSED_COHERENCE"],
      reevaluation: "EVERY_RECEIPT; ROLE_FLIP_LAWFULLY_REAIMS",
      constants_added: 0,
      assets: {
        G_GRID: { id: "G_GRID_LEVEL_DISCOUNT", source_asset: "P1_THE_GRID", canonical_asset_status_unchanged: "VALIDATED", behavioral_weighting_role: "UNDER-VALIDATION_CONTINUED_FROM_V52I", note: "Only FALLING role may consume this depth prior." },
        G3: { id: "G3_DIP_RECOVERY_GRADIENT", source_asset: "G3", source_commit: GREEK_INSTRUMENTS_COMMIT, canonical_status: "UNVALIDATED-CANDIDATE", behavioral_weighting_role: "UNDER-VALIDATION_CONTINUED_FROM_V52I" },
      },
      clean_store: { canonical_manifest_unchanged: true, exact_under_validation_aliases: n9Binding.store.boot_assertion.under_validation_loaded_ids, boot_assertion: n9Binding.store.boot_assertion },
      live_evidence_authority: { retained: true, candidate_authority_without_frozen_machine_read: false, assertions: v52bAssertions.depth_priors_never_create_or_withdraw_live_authority },
      frozen_clauses: { clause_1: true, clause_2: true, clause_4_and_referee: true, clause_5: true, clause_6: true, crediting: "TRADES_AS_TRUTH_UNCHANGED", scavenger: false, REFLEX_POST: v52bAssertions.REFLEX_POST_zero.observed },
      differential: { changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_role_selection: behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause), frozen_pre_authorized_differences: frozenClauseDiffs.length },
      pre_stated_claims: { faller_fills: roleConditionedSummary.faller_side_fills, climber_preservation: roleConditionedSummary.climber_preservation, banked_delta: roleConditionedSummary.banked_delta, one_sided_exposure_changes: roleConditionedSummary.one_sided_exposure_changes, pins_unharmed: pinComparisons.every((row) => row.unharmed), REFLEX_POST_zero: v52bAssertions.REFLEX_POST_zero.observed === 0 },
    } : isV52i ? {
      authorized_change: "CLAUSE_3_N4_DEPTH_INFORMED_LEVEL_SELECTION_ONLY",
      law: "DEPTH_PRIORS_MAY_WEIGHT_AN_ALREADY_AUTHORIZED_LIVE_EVIDENCE_LEVEL; PRIORS_INFORM_NEVER_GATE; SELECTED_TARGET_CAN_ONLY_MOVE_DOWN_INSIDE_LIVE_POST_ONSET_BOUNDS",
      weighting_law: "ROUND(G_GRID_DISCOUNT*G3_RECOVERY + G3_MEDIAN_DIP_DEPTH*(1-G3_RECOVERY))",
      assets: {
        G_GRID: { id: "G_GRID_LEVEL_DISCOUNT", source_asset: "P1_THE_GRID", canonical_asset_status_unchanged: "VALIDATED", behavioral_weighting_role_before: "UNVALIDATED-CANDIDATE", behavioral_weighting_role_this_run: "UNDER-VALIDATION_V52I", note: "Operator label G-grid is bound as the candidate behavioral use of the existing P1 cell-conditional grid; no parallel asset was invented." },
        G3: { id: "G3_DIP_RECOVERY_GRADIENT", source_asset: "G3", source_commit: GREEK_INSTRUMENTS_COMMIT, status_before: "UNVALIDATED-CANDIDATE", status_this_run: "UNDER-VALIDATION_V52I" },
      },
      clean_store: { canonical_manifest_unchanged: true, exact_under_validation_aliases: n9Binding.store.boot_assertion.under_validation_loaded_ids, boot_assertion: n9Binding.store.boot_assertion },
      live_evidence_authority: { retained: true, candidate_authority_without_frozen_machine_read: false, assertions: v52bAssertions.depth_priors_never_create_or_withdraw_live_authority },
      frozen_clauses: { clause_1: true, clause_2: true, clause_4_and_referee: true, clause_5: true, clause_6: true, crediting: "TRADES_AS_TRUTH_UNCHANGED", scavenger: false, REFLEX_POST: v52bAssertions.REFLEX_POST_zero.observed },
      differential: { changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_depth_selection: behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause), frozen_pre_authorized_differences: frozenClauseDiffs.length },
      pre_stated_claims: { entry_minus_later_floor: entryLaterFloorComparison, completes_not_reduced: { baseline: fourStateCensus.baseline.states.COMPLETE_AT_DELTA ?? 0, candidate: fourStateCensus.candidate.states.COMPLETE_AT_DELTA ?? 0, pass: (fourStateCensus.candidate.states.COMPLETE_AT_DELTA ?? 0) >= (fourStateCensus.baseline.states.COMPLETE_AT_DELTA ?? 0) }, pins_unharmed: pinComparisons.every((row) => row.unharmed), one_sided_exposure: oneSidedExposureSummary },
    } : isV52h ? {
      authorized_change: "CLAUSE_4_MARKET_PROOF_PRECONDITION_REMOVAL_ONLY",
      before: "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR_BLOCKS_REST_LICENSE",
      after: "POST_ONSET_TRADED_LOW_SUM_RECORDED_AS_TELEMETRY_NOT_A_LICENSE_PRECONDITION",
      burden_transfer: { clause_3_evidence_backed_levels: "FROZEN", clause_6_joint_targets_at_or_below_99: "FROZEN_AND_BINDING", tuned_constant: false },
      disagreement_referee: { status: "FROZEN_FULLY_INTACT", firing_disagreement_still_blocks: true, receipt_violations: v52bAssertions.clause_4_disagreement_referee_intact.violations },
      clauses_1_2_3_5_6: { status: "FROZEN", receipt_differences_before_authorized_change: frozenClauseDiffs.length, V52g_policy_commit: V52G_COMMIT, pair_budget_summary: pairBudgetRecordSummary },
      N9: { status: "FROZEN_V52E", clean_store_boot: n9Binding.store.boot_assertion },
      crediting: { status: "FROZEN_TRADES_AS_TRUTH", source_file: frozenV52PolicyPath, source_sha256: shaBytes(currentV52PolicyBytes) },
      scavenger: { enabled: false, status: "FROZEN" },
      REFLEX_POST: { expected: 0, observed: v52bAssertions.REFLEX_POST_zero.observed },
      differential: { changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_market_proof_removal: behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause) },
      pre_stated_claims: { SMIILA: smiilaObservation, zero_COMPLETE_AT_LOSS: candidateFourStateRows.every((row) => row.state !== "COMPLETE_AT_LOSS"), pins_unharmed: pinComparisons.every((row) => row.unharmed), new_one_sided_exposure: oneSidedExposureSummary },
    } : isV52g ? {
      authorized_change: "CLAUSE_6_ORDER_FREE_JOINT_TARGET_CONSERVATION_ONLY",
      settlement_identity: { payout_cents: 100, joint_law: "target_A_cents + target_B_cents <= 99", tuned_constant: false },
      allocation: { law: "EXISTING_LEVEL_AUTHORITIES_EVALUATED_JOINTLY_AT_EACH_RECEIPT; NEWLY_EVALUATED_SIDE_BOUNDED_BY_99_MINUS_THE_DECISION_TIME_KNOWN_COUNTERPART", bought_side_immutable_at_entry: true, standing_side_re_evaluated_receipt_causally: true, sequence_role_language_used: false },
      pair_budget_record: { one_per_game: true, born_at: "PAIR_FIRST_LICENSED_POST", fields: ["current_joint_split", "full_revision_history_with_each_revision_license_fields"], goals: "ABSENT_BY_DESIGN", predictions: "ABSENT_BY_DESIGN", future_plan_organ_home: "INTENTIONALLY_EMPTY_PENDING_OPERATOR_DESIGN_RULING", summary: pairBudgetRecordSummary },
      frozen_upstream_proof: { pre_authorized_clause_differences: frozenClauseDiffs.length, downstream_state_input_divergences_after_clause_6: downstreamFrozenInputDivergences.length, law: "FROZEN_CLAUSE_MECHANICS_AND_RECEIPTS_MUST_MATCH THROUGH THE AUTHORIZED CLAUSE_6 DIVERGENCE; LATER CREDIT_AND_STANDING INPUTS MAY DIFFER ONLY AS A CAUSAL CONSEQUENCE AND ARE RECEIPTED_SEPARATELY" },
      clause_1: { status: "FROZEN_CODEX_INTERIM", behavior_changed: false, receipt_differences: frozenClauseFailureCounts.clause_1_onset },
      clause_2: { status: "FROZEN_V52C", behavior_changed: false, receipt_differences: frozenClauseFailureCounts.clause_2_read },
      clause_3: { status: "FROZEN_V52B_PLUS_V52E_N4", machine_read_input_changed: false, receipt_differences: frozenClauseFailureCounts.clause_3_machine_read_input },
      clause_4: { status: "FROZEN_V52D_PLUS_V52E_N5", behavior_changed: false, receipt_differences: frozenClauseFailureCounts.clause_4_coherence },
      clause_5: { status: "FROZEN_V52F_POST_CREDIT_DEGENERATE_IDENTITY", source_commit: V52F_COMMIT },
      N9: { status: "FROZEN_V52E", palantir_receipt_differences: frozenClauseFailureCounts.N9_palantir, clean_store_boot: n9Binding.store.boot_assertion },
      crediting: { status: "FROZEN_TRADES_AS_TRUTH", source_file: frozenV52PolicyPath, source_sha256: shaBytes(currentV52PolicyBytes) },
      scavenger: { enabled: false, status: "FROZEN" },
      differential: { changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_clause_6: behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause) },
      prior_AT_LOSS_re_attestation: v52gPriorLossReattestation,
      pins: { comparisons: pinComparisons, SANDAN_at_or_better: sandanPin?.at_or_better ?? false },
    } : isV52f ? {
      authorized_change: "CLAUSE_5_PAIR_ENTRY_CONSERVATION_ONLY",
      settlement_identity: { payout_cents: 100, strict_law: "target_cents + credited_sibling_entry_cents < 100", integer_form: "target_cents <= 99 - credited_sibling_entry_cents", tuned_constant: false },
      application: { only_after_sibling_credit: true, before_sibling_credit: "NOT_APPLICABLE_V52E_BYTE_BEHAVIOR", effect: "BOUND_LICENSED_TARGET_AT_FIXED_PAIR_CAP", timing_gate_added: false, crediting_changed: false },
      clause_1: { status: "FROZEN_CODEX_INTERIM", behavior_changed: false, receipt_differences: frozenClauseFailureCounts.clause_1_onset },
      clause_2: { status: "FROZEN_V52C", behavior_changed: false, receipt_differences: frozenClauseFailureCounts.clause_2_read },
      clause_3: { status: "FROZEN_V52B_PLUS_V52E_N4", machine_read_input_changed: false, receipt_differences: frozenClauseFailureCounts.clause_3_machine_read_input },
      clause_4: { status: "FROZEN_V52D_PLUS_V52E_N5", behavior_changed: false, receipt_differences: frozenClauseFailureCounts.clause_4_coherence },
      N9: { status: "FROZEN_V52E", palantir_receipt_differences: frozenClauseFailureCounts.N9_palantir, clean_store_boot: n9Binding.store.boot_assertion },
      crediting: { status: "FROZEN_TRADES_AS_TRUTH", source_file: frozenV52PolicyPath, source_sha256: shaBytes(currentV52PolicyBytes) },
      scavenger: { enabled: false, status: "FROZEN" },
      differential: { changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_clause_5: behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause) },
      pre_stated_claim: v52fPreStatedClaim,
    } : isV52e ? {
      authorized_change: "N9_CLEAN_PALANTIR_WIRING_ONLY",
      clause_1: { status: "FROZEN_CODEX_INTERIM", behavior_changed: false, common_receipts_compared: commonTraceKeys.length, exact_per_receipt_match: frozenClauseDiffs.length === 0 },
      clause_2: { status: "FROZEN_V52C", behavior_changed: false, exact_read_object_match: frozenClauseDiffs.length === 0, function_identity: { fullPostOnsetRead: true, fullPostOnsetAuthority: true, observePostOnsetEvidence: true } },
      clause_3: { status: "FROZEN_MECHANICS_WITH_AUTHORIZED_N4_INFORMANT", incumbent_authority_withdrawn: false, N4_power: "RESCUE_ONLY_WHERE_FROZEN_LEVEL_ABSTAINS_AND_LIVE_RECEIPT_EVIDENCE_ALREADY_SUPPORTS_AUTHORITY; REFERENCE_BOUND_NEVER_SOLE_AUTHORITY", grid_lookup: "CURRENT_QUALIFYING_BOOK_ASK_NOT_EX_POST_CLOSE", N4_rescue_receipts: n4RescueRows.length },
      clause_4: { status: "FROZEN_V52D_IN_GAME_REFEREE_FIRST_WITH_AUTHORIZED_N5_EXACT_TIE_INFORMANT", frozen_strict_winner_overridden: false, N5_power: "ONLY_FROZEN_EXACT_TIE; STRICT_VALIDATED_BASE_RATE_MARGIN_REQUIRED", N5_tie_resolutions: n5PriorResolvedRows.length },
      N2: { role: "RECORDED_CATEGORY_CELL_AND_VALIDATED_SIGNAL_PRIORS_FOR_THE_LIVE_TAPE_READ", behavior_gate: false },
      N4: { role: "GRID_DISCOUNT_AND_ZONE_REFERENCE_BOUND_BESIDE_LIVE_EVIDENCE", behavior_gate: false },
      N5: { role: "MIRROR_COHERENCE_AND_VINDICATION_TIE_AND_MARGIN_INFORMANT", behavior_gate: false },
      continuous_consumption: palantirConsumptionSummary,
      clean_store_boot: n9Binding.store.boot_assertion,
      crediting: { status: "FROZEN_TRADES_AS_TRUTH", source_file: frozenV52PolicyPath, source_sha256: shaBytes(currentV52PolicyBytes) },
      scavenger: { enabled: false, status: "FROZEN" },
    } : isV52d ? {
      authorized_change: "CLAUSE_4_DISAGREEMENT_REFEREE_ONLY",
      clause_1: { status: "FROZEN_CODEX_INTERIM", behavior_changed: false, common_receipts_compared: commonTraceKeys.length, exact_per_receipt_match: frozenClauseDiffs.length === 0 },
      clause_2: { status: "FROZEN_V52C", behavior_changed: false, common_receipts_compared: commonTraceKeys.length, exact_read_object_match: frozenClauseDiffs.length === 0, function_identity: { fullPostOnsetRead: true, fullPostOnsetAuthority: true } },
      clause_3: { status: "FROZEN_V52B", behavior_changed: false, source_file: frozenV52bPolicyPath, source_sha256: shaBytes(currentV52bPolicyBytes), function_identity: { machineReadLevel: true, gateDecision: true, firstFailure: true }, downstream_decisions_may_change_only_after_clause_4_adjudication: true },
      clause_4: { before: "FIRING_DISAGREEMENT_FREEZES_UNLESS_SIBLING_CREDITED", after: "STRICTLY_STRONGER_RECEIPT_LOCAL_BACKING_WINS; HONEST_TIE_FREEZES", evidence_class_order: ["PRINT_BACKED", "QUOTE_PATH", "DEPTH_PRESSURE"], comparison_order: ["EVIDENCE_CLASS", "BACKING_RECEIPT_RECENCY", "EVIDENCING_MOVE_MAGNITUDE"], pair_under_par_check_changed: false, palantir_priors_consumed: false, N9_post_bell_consumed: false, historical_inputs_consumed: false, changed_decision_receipts: decisionDiffs.length, changed_leg_streams: streamDiffs.length, referee_summary: refereeSummary },
      crediting: { status: "FROZEN_TRADES_AS_TRUTH", source_file: frozenV52PolicyPath, source_sha256: shaBytes(currentV52PolicyBytes) },
      scavenger: { enabled: false, status: "FROZEN" },
    } : isV52c ? {
      authorized_change: "CLAUSE_2_EVIDENCE_HORIZON_ONLY",
      clause_1: { status: "FROZEN_CODEX_INTERIM_RESTAMP_ONLY", behavior_changed: false, common_receipts_compared: commonTraceKeys.length, per_receipt_match: frozenClauseDiffs.length === 0 },
      clause_2: { before: "FIXED_300_SECOND_RECEIPT_TRAIL", after: "ALL_POST_ONSET_PRINT_AND_BOOK_HISTORY_AVAILABLE_AT_EVALUATION_RECEIPT_RECENCY_WEIGHTED_BY_CAUSAL_RECEIPT_RANK", READ_ABSENT_law: "ONLY_WHEN_POST_ONSET_EVIDENCE_CANNOT_SUPPORT_ANY_COMPARATIVE_READ", fixed_replacement_constant: null, changed_decision_receipts: decisionDiffs.length, changed_leg_streams: streamDiffs.length },
      clause_3: { status: "FROZEN_V52B", behavior_changed: false, source_file: frozenV52bPolicyPath, source_sha256: shaBytes(currentV52bPolicyBytes), function_identity: { machineReadLevel: true, gateDecision: true, firstFailure: true }, downstream_inputs_may_change_only_from_clause_2: true },
      clause_4: { status: "FROZEN", behavior_changed: false, common_receipts_compared: commonTraceKeys.length, proof: "FROZEN_V52B_AND_V52C_FIRST_FAILURE_EVALUATED_ON_IDENTICAL_COHERENCE_INPUT_AT_EVERY_SHARED_RECEIPT", downstream_state_may_differ_after_clause_2_action: true, per_receipt_same_input_law_match: frozenClauseDiffs.length === 0 },
      crediting: { status: "FROZEN_TRADES_AS_TRUTH", source_file: frozenV52PolicyPath, source_sha256: shaBytes(currentV52PolicyBytes) },
      scavenger: { enabled: false, status: "FROZEN" },
    } : {
      authorized_change: "CLAUSE_3_LEVEL_AUTHORITY_ONLY",
      clause_1: { status: "FROZEN_CODEX_INTERIM_RESTAMP_ONLY", behavior_changed: false, common_receipts_compared: commonTraceKeys.length, per_receipt_match: frozenClauseDiffs.length === 0 },
      clause_2: { status: "FROZEN", behavior_changed: false, common_receipts_compared: commonTraceKeys.length, per_receipt_match: frozenClauseDiffs.length === 0 },
      clause_3: { before: "POST_ONSET_TRUE_TRADE_DIARY_SOLE_LEVEL_AUTHORITY", after: "EVIDENCE_BACKED_RECEIPT_LOCAL_MACHINE_READ_LEVEL_AUTHORITY_BOUNDED_BY_POST_ONSET_OBSERVATIONS", diary_role_after: "RECORDED_REFERENCE_INPUT_NOT_SOLE_LEVEL_AUTHORITY", changed_decision_receipts: decisionDiffs.length, changed_leg_streams: streamDiffs.length },
      clause_4: { status: "FROZEN", behavior_changed: false, common_receipts_compared: commonTraceKeys.length, proof: "FROZEN_V52_AND_V52B_FIRST_FAILURE_EVALUATED_ON_IDENTICAL_COHERENCE_INPUT_AT_EVERY_SHARED_RECEIPT", downstream_state_may_differ_after_clause_3_action: true, per_receipt_same_input_law_match: frozenClauseDiffs.length === 0 },
      crediting: { status: "FROZEN_TRADES_AS_TRUTH", source_file: frozenV52PolicyPath, source_sha256: shaBytes(currentV52PolicyBytes) },
      scavenger: { enabled: false, status: "FROZEN" },
    };
    const sourceFiles = {
      "arb-executor/analysis/window1_v52_judgment_gate.js": { sha256: shaBytes(currentV52PolicyBytes), role: "FROZEN_POLICY_BASE" },
      "arb-executor/analysis/window1_v52b_read_level_authority.js": { sha256: shaBytes(currentV52bPolicyBytes), role: (isV52c || isV52d || isV52e) ? "FROZEN_CLAUSE_3_POLICY" : "CLAUSE_3_ONLY_POLICY" },
      "arb-executor/analysis/build_window1_v38_maker_only.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v38_maker_only.js")), role: "REPLAY_AND_RECEIPT_BUILDER" },
    };
    if (isV52e) Object.assign(sourceFiles, {
      "arb-executor/analysis/window1_v52c_full_post_onset_read.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52c_full_post_onset_read.js")), role: "FROZEN_CLAUSE_2_POLICY" },
      "arb-executor/analysis/window1_v52d_disagreement_referee.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52d_disagreement_referee.js")), role: "FROZEN_CLAUSE_4_POLICY" },
      "arb-executor/analysis/window1_n9_clean_store.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_n9_clean_store.js")), role: "CLEAN_REGISTRY_VALIDATOR_NOT_A_LOADER" },
      "arb-executor/analysis/window1_v52e_palantir_wiring.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52e_palantir_wiring.js")), role: "N9_CONTINUOUS_PRIOR_WIRING" },
      "arb-executor/analysis/build_window1_v52e_palantir_wiring.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52e_palantir_wiring.js")), role: "DETERMINISTIC_ENTRYPOINT" },
      "arb-executor/tests/test_window1_v52e_palantir_wiring.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52e_palantir_wiring.js")), role: "N9_UNIT_TEST" },
      "arb-executor/tests/test_window1_v52e_palantir_wiring_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52e_palantir_wiring_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
      ...((isV52f || isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ? {
        "arb-executor/analysis/window1_v52f_pair_entry_conservation.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52f_pair_entry_conservation.js")), role: "CLAUSE_5_ONLY_POLICY" },
        "arb-executor/analysis/build_window1_v52f_pair_entry_conservation.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52f_pair_entry_conservation.js")), role: "DETERMINISTIC_ENTRYPOINT" },
        "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js")), role: "CLAUSE_5_UNIT_TEST" },
        "arb-executor/tests/test_window1_v52f_pair_entry_conservation_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52f_pair_entry_conservation_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
      } : {}),
      ...((isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ? {
        "arb-executor/analysis/window1_v52g_joint_target_conservation.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52g_joint_target_conservation.js")), role: "CLAUSE_6_ONLY_POLICY" },
        "arb-executor/analysis/build_window1_v52g_joint_target_conservation.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52g_joint_target_conservation.js")), role: "DETERMINISTIC_ENTRYPOINT" },
        "arb-executor/analysis/build_window1_v52g_provenance_repairs.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52g_provenance_repairs.js")), role: "RECEIPTS_ONLY_PROVENANCE_REPAIR_BUILDER" },
        "arb-executor/tests/test_window1_v52g_joint_target_conservation.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52g_joint_target_conservation.js")), role: "CLAUSE_6_UNIT_TEST" },
        "arb-executor/tests/test_window1_v52g_joint_target_conservation_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52g_joint_target_conservation_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
        "arb-executor/tests/test_window1_v52g_provenance_repairs.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52g_provenance_repairs.js")), role: "RECEIPTS_ONLY_PROVENANCE_REPAIR_TEST" },
      } : {}),
      ...((isV52h || isV52DepthValidation || isV52CausalOnset) ? {
        "arb-executor/analysis/window1_v52h_remove_pair_lows_precondition.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52h_remove_pair_lows_precondition.js")), role: "CLAUSE_4_MARKET_PROOF_PRECONDITION_REMOVAL_ONLY_POLICY" },
        "arb-executor/analysis/build_window1_v52h_remove_pair_lows_precondition.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52h_remove_pair_lows_precondition.js")), role: "DETERMINISTIC_ENTRYPOINT" },
        "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js")), role: "CLAUSE_UNIT_TEST" },
        "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
      } : {}),
      ...(isV52MacroRecognition ? {
        "arb-executor/analysis/window1_ground_truth_window_adapter.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_ground_truth_window_adapter.js")), role: "SOLE_GRADING_WINDOW_ADAPTER" },
        "arb-executor/analysis/window1_v52l_causal_stability_onset.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52l_causal_stability_onset.js")), role: "FROZEN_ADOPTED_CLAUSE_1_CAUSAL_PREFIX_POLICY" },
        "arb-executor/analysis/window1_v52m_macro_recognition.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52m_macro_recognition.js")), role: "CLAUSE_3_CAUSAL_MACRO_RECOGNITION_POLICY" },
        "arb-executor/analysis/build_window1_v52m_macro_recognition.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52m_macro_recognition.js")), role: "DETERMINISTIC_ENTRYPOINT" },
        "arb-executor/tests/test_window1_v52m_macro_recognition.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52m_macro_recognition.js")), role: "CLAUSE_UNIT_TEST" },
        "arb-executor/tests/test_window1_v52m_macro_recognition_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52m_macro_recognition_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
        ...((isV52n || isV52o || isV52Ripeness || isV52r) ? {
          "arb-executor/analysis/window1_v52n_recognition_confidence_gates.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52n_recognition_confidence_gates.js")), role: "CLAUSE_3_RECOGNITION_CONFIDENCE_GATE_ONLY_POLICY" },
          "arb-executor/analysis/build_window1_v52n_recognition_confidence_gates.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52n_recognition_confidence_gates.js")), role: "DETERMINISTIC_ENTRYPOINT" },
          "arb-executor/tests/test_window1_v52n_recognition_confidence_gates.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52n_recognition_confidence_gates.js")), role: "CLAUSE_UNIT_TEST" },
          "arb-executor/tests/test_window1_v52n_recognition_confidence_gates_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52n_recognition_confidence_gates_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
        } : {}),
        ...((isV52o || isV52Ripeness || isV52r) ? {
          "arb-executor/analysis/window1_v52o_benchmarked_role_instrument.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52o_benchmarked_role_instrument.js")), role: "CLAUSE_3_EXACT_BENCHMARKED_ROLE_INSTRUMENT_POLICY" },
          "arb-executor/analysis/build_window1_v52o_benchmarked_role_instrument.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52o_benchmarked_role_instrument.js")), role: "DETERMINISTIC_ENTRYPOINT" },
          "arb-executor/tests/test_window1_v52o_benchmarked_role_instrument.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52o_benchmarked_role_instrument.js")), role: "CLAUSE_UNIT_TEST" },
          "arb-executor/tests/test_window1_v52o_benchmarked_role_instrument_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52o_benchmarked_role_instrument_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
        } : {}),
        [`${SHAPE_TAXONOMY_COMMIT}:${SHAPE_TAXONOMY_PATH}`]: { sha256: v52mShapeBinding.taxonomy_provenance.sha256, role: "PINNED_13_FAMILY_TAXONOMY_METHOD_AND_COUNTS" },
        ...((isV52o || isV52Ripeness || isV52r) ? { [`${SHAPE_TAXONOMY_COMMIT}:${SHAPE_TAXONOMY_CSV_PATH}`]: { sha256: shaBytes(v52oTaxonomyCsvBytes), role: "PINNED_VERIFIED_ROLE_TRUTH_AND_BENCHMARK_ROWS" } } : {}),
        ...(isV52Ripeness ? {
          "arb-executor/analysis/window1_v52p_ripeness_gated_role_binding.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52p_ripeness_gated_role_binding.js")), role: "CLAUSE_3_RIPENESS_GATED_ROLE_BINDING_ONLY_POLICY" },
          "arb-executor/analysis/build_window1_v52p_ripeness_gated_role_binding.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52p_ripeness_gated_role_binding.js")), role: "DETERMINISTIC_ENTRYPOINT" },
          "arb-executor/tests/test_window1_v52p_ripeness_gated_role_binding.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52p_ripeness_gated_role_binding.js")), role: "CLAUSE_UNIT_TEST" },
          "arb-executor/tests/test_window1_v52p_ripeness_gated_role_binding_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52p_ripeness_gated_role_binding_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
          [`${RIPENESS_COMMIT}:${RIPENESS_PATH}`]: { sha256: shaBytes(v52pRipenessBytes), role: "PINNED_PUBLISHED_CLASS_AND_CATEGORY_RIPENESS_FRACTIONS" },
        } : {}),
        ...((isV52q || isV52r) ? {
          "arb-executor/analysis/window1_v52q_anchor_correction.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52q_anchor_correction.js")), role: "CLAUSE_3_ROLE_ANCHOR_CORRECTION_ONLY_POLICY" },
          "arb-executor/analysis/build_window1_v52q_anchor_correction.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52q_anchor_correction.js")), role: "DETERMINISTIC_ENTRYPOINT" },
          "arb-executor/tests/test_window1_v52q_anchor_correction.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52q_anchor_correction.js")), role: "CLAUSE_UNIT_TEST" },
          "arb-executor/tests/test_window1_v52q_anchor_correction_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52q_anchor_correction_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
          [`${ANCHOR_DISCREPANCY_COMMIT}:${ANCHOR_DISCREPANCY_PATH}`]: { sha256: shaBytes(v52qDiscrepancyBytes), role: "PINNED_RUNTIME_VS_PUBLISHED_ANCHOR_DISCREPANCY" },
        } : {}),
        ...(isV52r ? {
          "arb-executor/analysis/window1_v52r_assembled_policy.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52r_assembled_policy.js")), role: "CLAUSE_3_TRD5_AND_LOW_MINUS_ONE_ASSEMBLED_POLICY" },
          "arb-executor/analysis/build_window1_v52r_assembled_policy.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52r_assembled_policy.js")), role: "DETERMINISTIC_ENTRYPOINT" },
          "arb-executor/tests/test_window1_v52r_assembled_policy.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52r_assembled_policy.js")), role: "CLAUSE_UNIT_TEST" },
          "arb-executor/tests/test_window1_v52r_assembled_policy_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52r_assembled_policy_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
          [`${TRD5_COMMIT}:${TRD5_PATH}`]: { sha256: shaBytes(v52rTRD5Bytes), role: "PINNED_OPERATOR_SELECTED_TRD5_RECOGNITION_FRONTIER" },
          [`${LOW1_COMMIT}:${LOW1_PATH}`]: { sha256: shaBytes(v52rLOW1Bytes), role: "PINNED_OPERATOR_SELECTED_LOW_MINUS_ONE_TARGET_FRONTIER" },
        } : {}),
        [`${SHAPE_FLOOR_DEPTH_COMMIT}:${SHAPE_FLOOR_DEPTH_PATH}`]: { sha256: v52mShapeBinding.floor_table_provenance.sha256, role: "PINNED_PER_SHAPE_FLOOR_DEPTH_TABLE" },
      } : isV52l ? {
        "arb-executor/analysis/window1_ground_truth_window_adapter.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_ground_truth_window_adapter.js")), role: "SOLE_GRADING_WINDOW_ADAPTER" },
        "arb-executor/analysis/window1_v52l_causal_stability_onset.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52l_causal_stability_onset.js")), role: "CLAUSE_1_CAUSAL_PREFIX_ONLY_POLICY" },
        "arb-executor/analysis/build_window1_v52l_causal_stability_onset.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52l_causal_stability_onset.js")), role: "DETERMINISTIC_ENTRYPOINT" },
        "arb-executor/tests/test_window1_v52l_causal_stability_onset.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52l_causal_stability_onset.js")), role: "CLAUSE_1_CAUSALITY_UNIT_TEST" },
        "arb-executor/tests/test_window1_v52l_causal_stability_onset_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52l_causal_stability_onset_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
      } : isV52k ? {
        "arb-executor/analysis/window1_v52i_under_validation_store.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52i_under_validation_store.js")), role: "EXACT_TWO_CANDIDATE_VALIDATION_ADAPTER_REUSED" },
        "arb-executor/analysis/window1_v52k_library_backed_evidence.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52k_library_backed_evidence.js")), role: "CLAUSE_3_LIBRARY_BACKED_EVIDENCE_ONLY_POLICY" },
        "arb-executor/analysis/build_window1_v52k_library_backed_evidence.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52k_library_backed_evidence.js")), role: "DETERMINISTIC_ENTRYPOINT" },
        "arb-executor/analysis/build_window1_v52k_guegom_named_observation.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52k_guegom_named_observation.js")), role: "NAMED_OBSERVATION_ENTRYPOINT_OUTSIDE_COHORT30" },
        "arb-executor/tests/test_window1_v52k_library_backed_evidence.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52k_library_backed_evidence.js")), role: "CLAUSE_UNIT_TEST" },
        "arb-executor/tests/test_window1_v52k_library_backed_evidence_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52k_library_backed_evidence_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
      } : isV52i ? {
        "arb-executor/analysis/window1_v52i_under_validation_store.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52i_under_validation_store.js")), role: "EXACT_TWO_CANDIDATE_VALIDATION_ADAPTER" },
        "arb-executor/analysis/window1_v52i_depth_informed_level_selection.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52i_depth_informed_level_selection.js")), role: "CLAUSE_3_N4_DEPTH_SELECTION_ONLY_POLICY" },
        "arb-executor/analysis/build_window1_v52i_depth_informed_level_selection.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52i_depth_informed_level_selection.js")), role: "DETERMINISTIC_ENTRYPOINT" },
        "arb-executor/tests/test_window1_v52i_depth_informed_level_selection.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52i_depth_informed_level_selection.js")), role: "CLAUSE_UNIT_TEST" },
        "arb-executor/tests/test_window1_v52i_depth_informed_level_selection_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52i_depth_informed_level_selection_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
      } : isV52j ? {
        "arb-executor/analysis/window1_v52i_under_validation_store.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52i_under_validation_store.js")), role: "EXACT_TWO_CANDIDATE_VALIDATION_ADAPTER_REUSED" },
        "arb-executor/analysis/window1_v52j_role_conditioned_level_selection.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52j_role_conditioned_level_selection.js")), role: "CLAUSE_3_N4_ROLE_CONDITIONED_LEVEL_SELECTION_ONLY_POLICY" },
        "arb-executor/analysis/build_window1_v52j_role_conditioned_level_selection.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52j_role_conditioned_level_selection.js")), role: "DETERMINISTIC_ENTRYPOINT" },
        "arb-executor/analysis/build_window1_v52j_guegom_named_observation.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52j_guegom_named_observation.js")), role: "NAMED_OBSERVATION_ENTRYPOINT_OUTSIDE_COHORT30" },
        "arb-executor/tests/test_window1_v52j_role_conditioned_level_selection.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52j_role_conditioned_level_selection.js")), role: "CLAUSE_UNIT_TEST" },
        "arb-executor/tests/test_window1_v52j_role_conditioned_level_selection_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52j_role_conditioned_level_selection_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
      } : {}),
    }); else if (isV52d) Object.assign(sourceFiles, {
      "arb-executor/analysis/window1_v52c_full_post_onset_read.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52c_full_post_onset_read.js")), role: "FROZEN_CLAUSE_2_POLICY" },
      "arb-executor/analysis/window1_v52d_disagreement_referee.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52d_disagreement_referee.js")), role: "CLAUSE_4_ONLY_POLICY" },
      "arb-executor/analysis/build_window1_v52d_disagreement_referee.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52d_disagreement_referee.js")), role: "DETERMINISTIC_ENTRYPOINT" },
      "arb-executor/tests/test_window1_v52d_disagreement_referee.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52d_disagreement_referee.js")), role: "CLAUSE_UNIT_TEST" },
      "arb-executor/tests/test_window1_v52d_disagreement_referee_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52d_disagreement_referee_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
    }); else if (isV52c) Object.assign(sourceFiles, {
      "arb-executor/analysis/window1_v52c_full_post_onset_read.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52c_full_post_onset_read.js")), role: "CLAUSE_2_ONLY_POLICY" },
      "arb-executor/analysis/build_window1_v52c_full_post_onset_read.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52c_full_post_onset_read.js")), role: "DETERMINISTIC_ENTRYPOINT" },
      "arb-executor/tests/test_window1_v52c_full_post_onset_read.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52c_full_post_onset_read.js")), role: "CLAUSE_UNIT_TEST" },
      "arb-executor/tests/test_window1_v52c_full_post_onset_read_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52c_full_post_onset_read_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
    }); else Object.assign(sourceFiles, {
      "arb-executor/analysis/build_window1_v52b_read_level_authority.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52b_read_level_authority.js")), role: "DETERMINISTIC_ENTRYPOINT" },
      "arb-executor/tests/test_window1_v52b_read_level_authority.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52b_read_level_authority.js")), role: "CLAUSE_UNIT_TEST" },
      "arb-executor/tests/test_window1_v52b_read_level_authority_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52b_read_level_authority_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
    });
    const sourceManifest = {
      files: {
        ...sourceFiles,
      },
    };
    const observationSummary = (events) => {
      const value = score(events);
      return { ...value, conservation: { D: value.D, legs: value.legs, expected_D: 30, expected_legs: 60, pass: value.D === 30 && value.legs === 60 } };
    };
    const groundObservationSummary = (rows) => {
      const eligible = rows.filter((row) => row.state !== "UNKNOWN_BELL_NON_GRADEABLE");
      return {
        D: eligible.length,
        unknown_bell: rows.length - eligible.length,
        completed_pairs: eligible.filter((row) => ["COMPLETE_AT_DELTA", "COMPLETE_AT_LOSS"].includes(row.state)).length,
        under_par_pairs: eligible.filter((row) => row.state === "COMPLETE_AT_DELTA").length,
        states: countBy(rows, (row) => row.state),
        offer_denominator_under_par: eligible.filter((row) => row.offered_under_par === true).length,
        binding: groundTruthWindowBinding.binding,
        conservation: { rows: rows.length, eligible: eligible.length, unknown_bell: rows.length - eligible.length, pass: rows.length === 30 && eligible.length + (rows.length - eligible.length) === 30 },
      };
    };
    const observationScore = isV52CausalOnset
      ? { baseline: groundObservationSummary(reportedBaselineFourStateRows), candidate: groundObservationSummary(reportedCandidateFourStateRows), adjudication: null, role: "OBSERVATION_ONLY_30_GAME_GROUND_TRUTH_BOUND_GRADING" }
      : { baseline: observationSummary(baselineRun.marketEvents), candidate: observationSummary(candidateRun.marketEvents), adjudication: null, role: "OBSERVATION_ONLY_30_GAME_FLOW_COHORT" };
    const v52pFrozenObservationControls = (isV52Ripeness || isV52r) ? Object.fromEntries([
      ["V52M_OBSERVATION_CONTROL", V52M_COMMIT, ".claude/window1_live_v4_replay/v52m_macro_recognition_20260817/OUTCOME_OBSERVATIONS_30.json"],
      ["V52N_OBSERVATION_CONTROL", V52N_COMMIT, ".claude/window1_live_v4_replay/v52n_recognition_confidence_gates_20260817/OUTCOME_OBSERVATIONS_30.json"],
      ["V52O_OBSERVATION_CONTROL", V52O_COMMIT, ".claude/window1_live_v4_replay/v52o_benchmarked_role_instrument_20260817/OUTCOME_OBSERVATIONS_30.json"],
      ...((isV52q || isV52r) ? [["V52P_OBSERVATION_CONTROL", V52P_COMMIT, ".claude/window1_live_v4_replay/v52p_ripeness_gated_role_binding_20260817/OUTCOME_OBSERVATIONS_30.json"]] : []),
      ...(isV52r ? [["V52Q_OBSERVATION_CONTROL", V52Q_COMMIT, ".claude/window1_live_v4_replay/v52q_anchor_correction_20260818/OUTCOME_OBSERVATIONS_30.json"]] : []),
    ].map(([name, commit, artifactPath]) => {
      const bytes = gitShow(commit, artifactPath);
      return [name, { retained_not_replayed: true, commit, path: artifactPath, sha256: shaBytes(bytes), observation: JSON.parse(bytes.toString("utf8")) }];
    })) : null;
    const v52oObservationControls = (isV52Ripeness || isV52r) ? v52pFrozenObservationControls : isV52o ? Object.fromEntries(["V52M_OBSERVATION_CONTROL", "V52N_OBSERVATION_CONTROL"].map((name) => {
      const run = machineRuns.get(name);
      const rows = groundBoundFourStateRowsFor(run.marketEvents);
      return [name, { score: groundObservationSummary(rows), states: countBy(rows, (row) => row.state), rows }];
    })) : null;
    const onsetRows = isV52CausalOnset
      ? candidateRun.marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => ({ event_id: event.event_id, leg_identity: leg.leg_identity, onset: leg.v52_onset })))
      : replayBases.flatMap((base) => Object.values(base.legs).map((leg) => ({ event_id: base.event_id, leg_identity: leg.leg_identity, onset: leg.v52_onset })));
    const compactTrace = (rows) => rows.map((row) => ({
      ...row,
      onset: row.onset ? { ...row.onset, candidates: undefined, candidates_receipt: `STABILITY_ONSET_LEDGER.jsonl.gz#${row.leg_identity}` } : null,
    }));
    const baselineCompactTrace = compactTrace(baselineFlow.trace);
    const candidateCompactTrace = compactTrace(candidateFlow.trace);
    const report = `# V52b Iteration 1 — 30-game observation build\n\nV52b changes clause ③ only. The frozen V52 onset, read, pair-coherence, disagreement, crediting, and scavenger laws are unchanged. The true-trade diary remains recorded but is no longer the sole level authority. An incumbent receipt-local machine target may sign only when its evidence receipts are post-onset and its target lies inside post-onset observed prices.\n\n- Cohort: 5 frozen pins + 25 deterministic category × paired census-stamp events; seed ${v52bCohort.seed_sha256}.\n- Decision receipts traced: before ${baselineFlow.trace.length}; after ${candidateFlow.trace.length}; clause-③ decision differences ${decisionDiffs.length}; changed leg streams ${streamDiffs.length}.\n- Assertions: ${v52bAssertions.pass ? "PASS" : "BLOCKED"}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; scavenger OFF.\n- Named observations (not acceptance bars): ${JSON.stringify(namedChecks)}.\n- 30-game outcome observations: before completed ${observationScore.baseline.completed_pairs}; after completed ${observationScore.candidate.completed_pairs}. No disposition-804 adjudication was run.\n- No deployment, authorization, live access, holdout access, order action, or position action.\n`;
    const v52cReport = `# V52c Iteration 2 - 30-game observation build\n\nV52c changes clause 2 only. A receipt's machine read may consume all post-onset prints and book history available at that receipt, with causal receipt-rank recency weighting and no fixed time horizon. READ_ABSENT means the available post-onset evidence supports no comparative read. Clauses 1, 3, and 4, trades-as-truth crediting, and scavenger OFF remain frozen from V52b.\n\n- Cohort: 5 frozen pins + 25 fresh deterministic category x paired census-stamp events; seed ${activeReadCohort.seed_sha256}; overlap with V52b fresh cohort ${activeReadCohort.exclusions?.prior_V52b_fresh25_overlap_count ?? null}.\n- Decision receipts traced: before ${baselineFlow.trace.length}; after ${candidateFlow.trace.length}; clause-2 decision differences ${decisionDiffs.length}; changed leg streams ${streamDiffs.length}.\n- Thin-tape READ_ABSENT receipts: before ${blockReasonHistogram.aggregate.thin_tape_READ_ABSENT_before}; after ${blockReasonHistogram.aggregate.thin_tape_READ_ABSENT_after}.\n- Assertions: ${v52bAssertions.pass ? "PASS" : "BLOCKED"}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; scavenger OFF.\n- MERDRO authoring correction: formation-era 6c prints are excluded from credit; post-onset licensed judgment credits are lawful.\n- Named observations (not acceptance bars): ${JSON.stringify(namedChecks)}.\n- 30-game outcome observations: before completed ${observationScore.baseline.completed_pairs}; after completed ${observationScore.candidate.completed_pairs}. No disposition-804 adjudication was run.\n- No deployment, authorization, live access, holdout access, order action, or position action.\n`;
    const v52dReport = `# V52d Iteration 3 - disagreement referee, 30-game observation build\n\nV52d changes clause 4 only. When the full post-onset read and Jul 6 depth-pressure reading disagree, the receipt-local referee compares in-game backing in strict order: print-backed over quote-path over depth-pressure, then backing-receipt recency, then evidencing-move magnitude. A strictly stronger reading is licensed; an exact tie remains frozen. Pair-under-par, clauses 1/2/3, trades-as-truth crediting, and scavenger OFF are unchanged. Palantir, N9, post-bell, and historical inputs are absent.\n\n- Cohort: 5 frozen pins + 25 fresh deterministic category x paired census-stamp events; seed ${activeReadCohort.seed_sha256}; overlap V52b/V52c fresh cohorts ${activeReadCohort.exclusions?.prior_V52b_fresh25_overlap_count ?? null}/${activeReadCohort.exclusions?.prior_V52c_fresh25_overlap_count ?? null}.\n- Decision receipts traced: before ${baselineFlow.trace.length}; after ${candidateFlow.trace.length}; clause-4 decision differences ${decisionDiffs.length}; changed leg streams ${streamDiffs.length}.\n- Referee: ${refereeSummary.recorded_adjudications} firing rows, ${refereeSummary.resolved_strictly_stronger} strictly resolved, ${refereeSummary.honest_ties} honest ties; order-masked blocks ${refereeSummary.baseline_order_masked_disagreement_blocks} -> ${refereeSummary.candidate_order_masked_disagreement_blocks}.\n- ARSMAR: frozen V52c has ${refereeSummary.ARSMAR.baseline_order_masked_blocks} row-grain disagreement blocks, not the pre-stated 127; candidate records ${refereeSummary.ARSMAR.candidate_recorded_adjudications} adjudications and leaves ${refereeSummary.ARSMAR.candidate_order_masked_blocks} order-masked blocks. Completion remains an observation, not a falsifiable claim.\n- Assertions: ${v52bAssertions.pass ? "PASS" : "BLOCKED"}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; scavenger OFF.\n- Named observations (not acceptance bars): ${JSON.stringify(namedChecks)}.\n- 30-game outcome observations: before completed ${observationScore.baseline.completed_pairs}; after completed ${observationScore.candidate.completed_pairs}. The disposition-804 bell did not run.\n- No deployment, authorization, live access, holdout access, order action, position action, Palantir, or N9 input.\n`;
    const v52eReport = `# V52e Iteration 4 - N9 Palantir wiring, 30-game observation build\n\nV52e reuses the existing dossier, C-ONE-TRUTH, pinned Git-object, and frozen N8-chain machinery. It repoints the single registry to the hash-bound MACHINE_PALANTIR CLEAN store and refuses every UNVALIDATED, QUARANTINED, SUPERSEDED, or fallback input at boot. N2, N4, and N5 are consulted continuously at decision receipt grain with asset/SHA/status provenance. Priors inform; they never gate. Clauses 1-4 mechanics, trades-as-truth crediting, scavenger OFF, and REFLEX_POST=0 are frozen.\n\n- Step 0: ${step0ReuseInventory.components.filter((row) => row.disposition === "REUSED" || row.disposition === "RE-POINTED" || row.disposition === "REUSED_AS_VALIDATOR_NOT_LOADER").length} components reused/re-pointed; ${step0ReuseInventory.components.filter((row) => row.disposition === "RETIRED-WITH-REASON").length} retired with reason; parallel loader built: NO.\n- CLEAN boot: ${n9Binding.store.boot_assertion.passed ? "PASS" : "FAIL"}; loaded ${n9Binding.store.boot_assertion.loaded_ids.join(", ")}; unvalidated/quarantined/superseded/fallback ${n9Binding.store.boot_assertion.unvalidated_loaded}/${n9Binding.store.boot_assertion.quarantined_loaded}/${n9Binding.store.boot_assertion.superseded_loaded}/${n9Binding.store.boot_assertion.fallback_loads}.\n- Cohort: 5 frozen pins + 25 fresh deterministic category x paired census-stamp events; seed ${activeReadCohort.seed_sha256}; prior fresh-cohort overlap B/C/D ${activeReadCohort.exclusions.prior_V52B_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52C_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52D_fresh25_overlap_count}.\n- Continuous consumption: ${palantirConsumptionSummary.consumption_receipts}/${palantirConsumptionSummary.decision_trace_rows} decision receipts; N4 rescues ${palantirConsumptionSummary.N4_prior_informed_live_evidence_rescues}; N5 frozen-tie resolutions ${palantirConsumptionSummary.N5_frozen_tie_resolutions}.\n- Grid-covered N4 abstentions: ${palantirConsumptionSummary.baseline_N4_abstentions_in_grid_covered_receipts} -> ${palantirConsumptionSummary.candidate_N4_abstentions_on_same_receipts}; pins unharmed ${palantirConsumptionSummary.pins_unharmed}.\n- Assertions: ${v52bAssertions.pass ? "PASS" : "BLOCKED"}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; scavenger OFF.\n- 30-game observations: before completed ${observationScore.baseline.completed_pairs}; after ${observationScore.candidate.completed_pairs}. These are observations only; the full-804 exam did not run.\n- No deployment, authorization, live access, holdout access, order action, position action, or disposition-804 run.\n`;
    const v52fReport = isV52f ? `# V52f Iteration 5 - pair-entry conservation, 30-game observation build\n\nV52f adds exactly clause 5 to frozen V52e: once a sibling is credited, each licensed target is bounded by target <= 99 - credited sibling entry. This is the integer settlement identity, not a fitted margin. Clauses 1-4, N9 continuous priors, trades-as-truth crediting, scavenger OFF, and REFLEX_POST=0 remain frozen.\n\n- Cohort: 5 frozen pins + 25 fresh events (4 pre-stated AT_LOSS identities plus 21 deterministic category x census-stamp events); seed ${activeReadCohort.seed_sha256}; prior B/C/D/E fresh overlap ${activeReadCohort.exclusions.prior_V52B_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52C_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52D_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52E_fresh25_overlap_count}.\n- Clause-5 differential: ${decisionDiffs.length} decision receipts, ${behaviorStreamDiffs.length} behavior streams, and ${streamDiffs.length} license-or-metadata streams changed; every behavior delta begins at/after a clause-5 bind; clauses 1-4/N9 receipt differences ${frozenClauseDiffs.length}.\n- Four-state observation: baseline ${JSON.stringify(fourStateCensus.baseline.states)}; V52f ${JSON.stringify(fourStateCensus.candidate.states)}.\n- Pre-stated claim: four conversions ${v52fPreStatedClaim.all_four_convert_from_COMPLETE_AT_LOSS}; zero new COMPLETE_AT_LOSS ${v52fPreStatedClaim.zero_new_COMPLETE_AT_LOSS}.\n- Assertions: ${v52bAssertions.pass ? "PASS" : "BLOCKED"}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; scavenger OFF.\n- These 30 outcomes are observations only. No full-804 disposition, sealed, deployment, authorization, live, order, or position action occurred.\n` : null;
    const v52gReport = isV52g ? `# V52g Iteration 6 - joint target conservation and pair budget record\n\nV52g adds one receipt-causal joint identity to frozen V52f: whenever both decision-time-known sides have a bought or standing value, their sum is at most 99. Existing per-leg level authorities are evaluated first; the newly evaluated standing side is bounded only when the identity binds. Post-credit this degenerates exactly to V52f. Clauses 1-4, N9, crediting, scavenger OFF, and REFLEX_POST=0 are frozen.\n\n- Cohort: 5 frozen pins + 25 fresh deterministic category x census-stamp events; seed ${activeReadCohort.seed_sha256}; fresh overlap B/C/D/E/F ${activeReadCohort.exclusions.prior_V52B_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52C_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52D_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52E_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52F_fresh25_overlap_count}.\n- Joint identity: ${pairBudgetRecordSummary.joint_sum_violations.length} violations across ${pairBudgetRecordSummary.revision_rows} revisions; ${pairBudgetRecordSummary.records} records for 30 games.\n- Pair budget record: born at first licensed post; current joint split plus complete licensed revision chain only. Goals and predictions are absent pending operator design.\n- Four-state observation: V52f baseline ${JSON.stringify(fourStateCensus.baseline.states)}; V52g ${JSON.stringify(fourStateCensus.candidate.states)}.\n- Prior four loss identities remain lawful: ${v52gPriorLossReattestation.pass}; fresh cohort has zero new COMPLETE_AT_LOSS: ${v52gPriorLossReattestation.zero_new_COMPLETE_AT_LOSS_in_fresh_30}.\n- Pins unharmed ${pinComparisons.every((row) => row.unharmed)}; SANDAN at-or-better ${sandanPin?.at_or_better ?? false}.\n- Assertions: ${v52bAssertions.pass ? "PASS" : "BLOCKED"}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; scavenger OFF.\n- These 30 outcomes are observations only. No full-804 disposition, sealed, deployment, authorization, live, order, or position action occurred.\n` : null;
    const v52hReport = isV52h ? `# V52h Iteration 7 - remove clause 4 market-proof precondition\n\nV52h removes exactly the requirement that post-onset traded lows already sum below 100 before a rest may be licensed. The traded-low sum remains recorded telemetry. The disagreement referee is intact; clauses 1, 2, 3, 5, and 6, N9, trades-as-truth crediting, scavenger OFF, and REFLEX_POST=0 are frozen.\n\n- Cohort: 5 frozen pins + 25 fresh deterministic category x census-stamp events; seed ${activeReadCohort.seed_sha256}; fresh overlap B/C/D/E/F/G ${activeReadCohort.exclusions.prior_V52B_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52C_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52D_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52E_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52F_fresh25_overlap_count}/${activeReadCohort.exclusions.prior_V52G_fresh25_overlap_count}. SMIILA is an explicitly reused named observation from frozen V52B and is excluded from the fresh-25 score observation.\n- Differential: ${decisionDiffs.length} decision receipts, ${behaviorStreamDiffs.length} behavior streams; every behavior change begins at or after the removed market-proof check.\n- Four-state observation: V52g ${JSON.stringify(fourStateCensus.baseline.states)}; V52h ${JSON.stringify(fourStateCensus.candidate.states)}; COMPLETE_AT_LOSS ${(fourStateCensus.candidate.states.COMPLETE_AT_LOSS || 0)}.\n- SMIILA named replay: ${JSON.stringify(smiilaObservation)}.\n- New one-sided exposure: ${oneSidedExposureSummary.newly_created_partials}; duration seconds ${JSON.stringify(oneSidedExposureSummary.duration_seconds)}.\n- Pins unharmed ${pinComparisons.every((row) => row.unharmed)}; disagreement referee violations ${v52bAssertions.clause_4_disagreement_referee_intact.violations.length}.\n- Assertions: ${v52bAssertions.pass ? "PASS" : "BLOCKED"}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; scavenger OFF.\n- These 30 outcomes plus the separately named SMIILA replay are observations only. No full-804 disposition, sealed, deployment, authorization, live, order, or position action occurred.\n` : null;
    const v52iReport = isV52i ? `# V52i Iteration 8 - depth-informed level selection\n\nV52i changes only clause 3/N4 level selection over frozen V52h. An already-authorized live-evidence level may be refined downward using the G-grid cell discount and G3 dip-recovery gradient as recorded prior inputs. Priors never create, withdraw, or gate authority. Canonical CLEAN assets are unchanged; exactly two operator-bound behavioral roles are UNDER-VALIDATION_V52I for this run.\n\n- Cohort: 5 pins + 25 fresh deterministic category x census-stamp games; seed ${activeReadCohort.seed_sha256}; prior-cohort overlaps are all zero.\n- Differential: ${decisionDiffs.length} decision receipts, ${behaviorStreamDiffs.length} behavior streams; frozen pre-authorized differences ${frozenClauseDiffs.length}.\n- Four-state: V52h ${JSON.stringify(fourStateCensus.baseline.states)}; V52i ${JSON.stringify(fourStateCensus.candidate.states)}.\n- Entry minus post-onset later floor: V52h ${JSON.stringify(entryLaterFloorComparison.baseline)}; V52i ${JSON.stringify(entryLaterFloorComparison.candidate)}; toward-zero claim ${entryLaterFloorComparison.pre_stated_claim.bought_above_later_floor_depth_shifts_toward_zero}.\n- One-sided exposure: V52i ${oneSidedExposureSummary.newly_created_partials}, durations ${JSON.stringify(oneSidedExposureSummary.duration_seconds)}; V52h frozen baseline ${frozenV52hOneSided.newly_created_partials}.\n- Pins unharmed ${pinComparisons.every((row) => row.unharmed)}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; assertions ${v52bAssertions.pass ? "PASS" : "BLOCKED"}.\n- Outcomes are observations only. No disposition-804, sealed, deployment, authorization, live, order, or position action occurred.\n` : null;
    const v52jReport = isV52j ? `# V52j Iteration 9 - pair-role-conditioned level selection

V52j changes clause 3/N4 only over frozen V52h. V52i's symmetric depth refinement is reverted. The existing own read, sibling read, and licensed coherence assign a receipt-local role. FALLING may lower the already-authorized target using the under-validation GRID and G3 depth priors inside live evidence bounds. RISING uses frozen evidence-backed near support. SETTLED and insufficient reads remain frozen V52h. Priors never create, withdraw, or gate authority.

- Cohort: 5 pins + 25 fresh deterministic category x census-stamp games; seed ${activeReadCohort.seed_sha256}; V52b-i fresh overlaps all zero. GUEGOM is a separately bound prior-cohort named observation and is not folded into the 30-game census.
- Differential: ${decisionDiffs.length} decision receipts, ${behaviorStreamDiffs.length} behavior streams; frozen pre-authorized differences ${frozenClauseDiffs.length}.
- Four-state: V52h ${JSON.stringify(fourStateCensus.baseline.states)}; V52j ${JSON.stringify(fourStateCensus.candidate.states)}.
- Faller fill delay/floor: ${JSON.stringify(roleConditionedSummary.faller_side_fills)}.
- Climber preservation: ${JSON.stringify(roleConditionedSummary.climber_preservation)}.
- Mean banked delta: ${JSON.stringify(roleConditionedSummary.banked_delta)}.
- One-sided exposure changes: ${JSON.stringify(roleConditionedSummary.one_sided_exposure_changes)}.
- Role flips: ${roleConditionedSummary.role_flips.count}; lawful re-aims ${roleConditionedSummary.role_flips.reaimed}.
- Pins unharmed ${pinComparisons.every((row) => row.unharmed)}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; assertions ${v52bAssertions.pass ? "PASS" : "BLOCKED"}.
- Outcomes are observations only. No disposition-804, sealed, deployment, authorization, live, order, or position action occurred.
` : null;
    const v52kReport = isV52k ? `# V52k Iteration 10 - library-backed level evidence

V52k changes clause 3 only over frozen V52h. A licensed level may be supported by the game's own post-onset tape or by the two hash-bound library candidates. The library may name a level below the shown range; it cannot license below its own supported floor, cannot cross the current touch, cannot bypass clause 2's live read, and remains subject to clause 6. V52i and V52j behavioral selection are not inherited.

- Cohort: 5 pins + 25 fresh deterministic category x census-stamp games; seed ${activeReadCohort.seed_sha256}; V52b-j fresh overlaps all zero. GUEGOM is a separately bound named observation outside the 30-game census.
- Differential: ${decisionDiffs.length} decision receipts and ${behaviorStreamDiffs.length} behavior streams; frozen pre-authorized differences ${frozenClauseDiffs.length}.
- Four-state: V52h ${JSON.stringify(fourStateCensus.baseline.states)}; V52k ${JSON.stringify(fourStateCensus.candidate.states)}.
- Library-backed stands below shown range: ${libraryBackedEvidenceSummary.library_backed_stands_below_shown_range.receipts} receipts / ${libraryBackedEvidenceSummary.library_backed_stands_below_shown_range.legs} legs / ${libraryBackedEvidenceSummary.library_backed_stands_below_shown_range.games} games.
- Faller fill delay versus V52h: ${JSON.stringify(libraryBackedEvidenceSummary.faller_side_fills.fill_delay_seconds_vs_V52h)}; entry-minus-later-floor ${JSON.stringify(libraryBackedEvidenceSummary.faller_side_fills.entry_minus_later_floor_cents)}.
- Climber preservation: ${JSON.stringify(libraryBackedEvidenceSummary.climber_completion_preservation)}.
- Mean banked delta: ${JSON.stringify(libraryBackedEvidenceSummary.banked_delta)}.
- One-sided exposure: created ${libraryBackedEvidenceSummary.one_sided_exposure_changes.created_count}, resolved ${libraryBackedEvidenceSummary.one_sided_exposure_changes.resolved_count}, created duration ${JSON.stringify(libraryBackedEvidenceSummary.one_sided_exposure_changes.created_duration_seconds)}.
- Pre-stated claims: ${JSON.stringify(libraryBackedEvidenceSummary.pre_stated_claims)}.
- REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; assertions ${v52bAssertions.pass ? "PASS" : "BLOCKED"}; scavenger OFF.
- Floor comparisons in this package use the current pre-re-cut 22441e05 receipt basis and await analysis-seat regrading. Outcomes are observations only. No 804, sealed, deployment, authorization, live, order, or position action occurred.
` : null;
    const v52lReport = isV52l ? `# V52l Iteration - causal stability onset

V52l replaces clause 1 only. The A/B onset candidates are preserved, but each is evaluated on sequential receipt prefixes and the first supported prefix fixes recognition. The onset code consumes no right edge and performs no full-span fit. Clauses 2-6, N9, trades-as-truth crediting, scavenger OFF, and REFLEX_POST=0 are frozen V52h behavior.

- Cohort: 5 pins + 25 fresh deterministic category x census-stamp games; seed ${activeReadCohort.seed_sha256}; overlap with every V52b-k fresh cohort is zero.
- Right-edge independence: ${rightEdgeIndependenceReceipt.pass ? "PASS" : "FAIL"}; ${rightEdgeIndependenceReceipt.rows.length}/30 games identical under -86400/0/+86400 second perturbations.
- Onset shifts, new minus old seconds: ${JSON.stringify(onsetTimingShiftReceipt.distribution_new_minus_old_seconds)}; old-present/new-absent ${onsetTimingShiftReceipt.old_present_new_absent}; old-absent/new-present ${onsetTimingShiftReceipt.old_absent_new_present}.
- Decision differential: ${decisionDiffs.length} decision receipts; ${behaviorStreamDiffs.length} behavior streams; frozen pre-onset differences ${frozenClauseDiffs.length}.
- Ground-truth grading binding: ${groundTruthWindowBinding.binding.source_commit}; SHA-256 ${groundTruthWindowBinding.binding.sha256}; UNKNOWN_BELL ${fourStateCensus.candidate.states.UNKNOWN_BELL_NON_GRADEABLE ?? 0} reported separately.
- Four-state observation: V52h ${JSON.stringify(fourStateCensus.baseline.states)}; V52l ${JSON.stringify(fourStateCensus.candidate.states)}.
- Pin outcomes are observations, not fixed bars: ${JSON.stringify(namedChecks)}. Pin license lawfulness: ${v52bAssertions.pins_lawful_not_outcome_bound.pass}.
- REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; assertions ${v52bAssertions.pass ? "PASS" : "BLOCKED"}; full-804, sealed, deployment, authorization, live, order, and position actions did not run.
- Lineage disposition: observation only. Adoption or hold is reserved to the operator at dock.
` : null;
    const v52mReport = isV52m ? `# V52m Iteration - causal macro recognition wired

V52m changes one capability over operator-adopted V52l: at each read/level receipt, the leg's true-print prefix is sampled with the pinned 17-point taxonomy method and classified into one of 13 families. A signable family consumes the pinned category/family median floor depth as clause 3's target; the current ask and clause 6 remain hard bounds. SLEEPER and the two GRIND_WOBBLE families abstain because the pinned taxonomy exposes no family confidence for them, so V52l runs unchanged. Clauses 1-2 and 4-6, the referee, trades-as-truth crediting, scavenger OFF, and REFLEX_POST=0 are frozen.

- Cohort: 5 pins + 25 fresh deterministic category x census-stamp games; seed ${activeReadCohort.seed_sha256}; overlap with every V52b-l fresh cohort is zero.
- Bound surfaces: taxonomy ${v52mShapeBinding.taxonomy_provenance.commit}/${v52mShapeBinding.taxonomy_provenance.sha256}; floor table ${v52mShapeBinding.floor_table_provenance.commit}/${v52mShapeBinding.floor_table_provenance.sha256}.
- Macro evaluations/classifications: ${macroRecognitionSummary.classifications.evaluation_receipt_rows}/${macroRecognitionSummary.classifications.classified_receipt_rows} receipt rows, ${macroRecognitionSummary.classifications.signable_terminal_legs} signable terminal legs, ${macroRecognitionSummary.classifications.abstain_terminal_legs} abstain terminal legs. Frequency comparison is emitted without inventing a numeric broad-match threshold.
- Consumption: ${macroRecognitionSummary.consumption.applicable_receipts} applicable receipts, ${macroRecognitionSummary.consumption.changed_target_receipts} target changes, ${macroRecognitionSummary.consumption.legs} legs, ${macroRecognitionSummary.consumption.games} games.
- Down-family fill timing/floor: ${JSON.stringify(macroRecognitionSummary.down_family_fills)}.
- Up/still preservation: ${JSON.stringify(macroRecognitionSummary.up_and_still_preservation)}.
- Mean banked delta: ${JSON.stringify(macroRecognitionSummary.banked_delta)}.
- One-sided exposure: created ${macroRecognitionSummary.one_sided_exposure_both_ways.created_count}, resolved ${macroRecognitionSummary.one_sided_exposure_both_ways.resolved_count}.
- Ground-truth grading: ${groundTruthWindowBinding.binding.source_commit}; SHA-256 ${groundTruthWindowBinding.binding.sha256}; UNKNOWN_BELL ${fourStateCensus.candidate.states.UNKNOWN_BELL_NON_GRADEABLE ?? 0} separate.
- Four-state observation: V52l ${JSON.stringify(fourStateCensus.baseline.states)}; V52m ${JSON.stringify(fourStateCensus.candidate.states)}.
- Pins lawful ${macroRecognitionSummary.pins.lawful}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; assertions ${v52bAssertions.pass ? "PASS" : "BLOCKED"}.
- Outcomes are observations only. No full-804, sealed, deployment, authorization, live, order, position, or holdout action occurred.
` : null;
    const v52nReport = isV52n ? `# V52n Iteration - recognition confidence gates

V52n changes one clause over frozen V52m. A causal family may bind clause 3 only when its pinned median declaration is at or before the floor table's own f=0.5 early checkpoint and the current receipt has crossed the table's 2c directional declaration. Below-gate proposals abstain to byte-frozen V52l behavior and are re-evaluated on every receipt. Bound down-family depth targeting is unchanged. Clauses 1-2 and 4-6, the referee, trades-as-truth crediting, scavenger OFF, and REFLEX_POST=0 are frozen.

- Cohort: 5 pins + 25 fresh deterministic category x census-stamp games; seed ${activeReadCohort.seed_sha256}; overlap with every V52b-m fresh cohort is zero.
- Bound surfaces: taxonomy ${v52mShapeBinding.taxonomy_provenance.commit}/${v52mShapeBinding.taxonomy_provenance.sha256}; floor table ${v52mShapeBinding.floor_table_provenance.commit}/${v52mShapeBinding.floor_table_provenance.sha256}.
- Gate: f<=${policy.PINNED_EARLY_CHECKPOINT_F}, signed drift>=${policy.PINNED_DIRECTIONAL_DECLARATION_CENTS}c; both values are pinned table schema facts; constants fitted in V52n: 0.
- Bound terminal frequencies: ${JSON.stringify(macroRecognitionSummary.classifications.terminal_frequency)}; proposed frequencies: ${JSON.stringify(macroRecognitionSummary.classifications.proposed_terminal_frequency)}; SLEEPER bound share ${macroRecognitionSummary.classifications.sleeper_bound_share}.
- Consumption: ${macroRecognitionSummary.consumption.applicable_receipts} applicable receipts, ${macroRecognitionSummary.consumption.changed_target_receipts} target changes, ${macroRecognitionSummary.consumption.legs} legs, ${macroRecognitionSummary.consumption.games} games.
- Down-family floor retention vs V52m: ${JSON.stringify(macroRecognitionSummary.down_family_fills)}.
- Up/still preservation vs V52l: ${JSON.stringify(macroRecognitionSummary.up_and_still_preservation)}.
- Mean banked delta vs V52m: ${JSON.stringify(macroRecognitionSummary.banked_delta)}.
- One-sided exposure vs V52m: created ${macroRecognitionSummary.one_sided_exposure_both_ways.created_count}, resolved ${macroRecognitionSummary.one_sided_exposure_both_ways.resolved_count}.
- SANDAN: ${JSON.stringify(macroRecognitionSummary.pins.comparisons.find((row) => row.code === "26JUL13SANDAN") ?? null)}.
- Pre-stated claims: family-frequency/SLEEPER NOT MET (bound 0% versus taxonomy ${macroRecognitionSummary.classifications.frequency_comparison.find((row) => row.family === "SLEEPER").taxonomy_share * 100}%); up/still NOT MET (${macroRecognitionSummary.up_and_still_preservation.candidate_credited_legs}/${macroRecognitionSummary.up_and_still_preservation.V52l_credited_legs}, although ${macroRecognitionSummary.up_and_still_preservation.restored_from_V52m.length} V52m losses returned); down-family ~1c NOT MET (median ${macroRecognitionSummary.down_family_fills.V52n_entry_minus_ground_truth_floor_cents.median}c); banked delta >= V52m NOT MET (${macroRecognitionSummary.banked_delta.candidate.mean_cents}c versus ${macroRecognitionSummary.banked_delta.baseline.mean_cents}c); pins lawful PASS; SANDAN restored PASS; REFLEX_POST=0 PASS. Exposure created/resolved is reported in both directions above.
- Four-state observation: V52m ${JSON.stringify(fourStateCensus.baseline.states)}; V52n ${JSON.stringify(fourStateCensus.candidate.states)}.
- Pins lawful ${macroRecognitionSummary.pins.lawful}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; assertions ${v52bAssertions.pass ? "PASS" : "BLOCKED"}.
- Outcomes are observations only. No full-804, sealed, deployment, authorization, live, order, position, or holdout action occurred.
` : null;
    const v52oReport = isV52o ? `# V52o Iteration - benchmarked early-role instrument

V52o binds the taxonomy benchmark's published rule literally: last causal true print at the evaluation receipt minus post-formation open; drift >= +2c is ROLE_UP, drift <= -2c is ROLE_DOWN, otherwise ABSTAIN. V52m/n remain replayed as observation controls and do not govern V52o. ROLE_DOWN consumes the stated per-category frequency-weighted aggregate of existing down-family median depths; ROLE_UP and ABSTAIN retain V52l behavior. Clauses 1-2 and 4-6, the referee, trades-as-truth crediting, scavenger OFF, and REFLEX_POST=0 are frozen.

- Cohort: 5 pins + 25 fresh deterministic category x census-stamp games; seed ${activeReadCohort.seed_sha256}; every V52b-n fresh overlap is zero.
- Bound rule: ${SHAPE_TAXONOMY_COMMIT}/${v52mShapeBinding.taxonomy_provenance.sha256}; floor table ${SHAPE_FLOOR_DEPTH_COMMIT}/${v52mShapeBinding.floor_table_provenance.sha256}; new constants 0.
- Called coverage: all terminal legs ${benchmarkRoleSummary.coverage.called_all_legs}/${benchmarkRoleSummary.coverage.terminal_legs} (${benchmarkRoleSummary.coverage.called_all_legs_share}); benchmark truth-role legs ${benchmarkRoleSummary.coverage.called_truth_role_legs}/${benchmarkRoleSummary.coverage.benchmark_truth_role_legs} (${benchmarkRoleSummary.coverage.called_truth_role_legs_share}); target band ${benchmarkRoleSummary.coverage.lands_in_target_band}.
- Called verified-role accuracy: ${benchmarkRoleSummary.accuracy.correct}/${benchmarkRoleSummary.accuracy.called_truth_role_legs} (${benchmarkRoleSummary.accuracy.accuracy}); benchmark reference 0.951.
- ROLE_DOWN floor gap: ${JSON.stringify(benchmarkRoleSummary.ROLE_DOWN_fills.floor_gap_cents)}; <=1.5c median claim ${benchmarkRoleSummary.ROLE_DOWN_fills.claim_median_gap_at_or_below_1_5c}.
- Up/still preservation: ${benchmarkRoleSummary.up_and_still_completion_preservation.V52o_credited_legs}/${benchmarkRoleSummary.up_and_still_completion_preservation.V52l_credited_legs}; preserved ${benchmarkRoleSummary.up_and_still_completion_preservation.preserved}.
- Mean banked delta: V52l ${benchmarkRoleSummary.banked_delta.V52l.mean_cents}c; V52o ${benchmarkRoleSummary.banked_delta.V52o.mean_cents}c; exceeds 1.83c ${benchmarkRoleSummary.banked_delta.exceeds_V52m_1_83c}.
- One-sided exposure: created ${benchmarkRoleSummary.one_sided_exposure_both_ways.created_count}, resolved ${benchmarkRoleSummary.one_sided_exposure_both_ways.resolved_count}; pins lawful ${benchmarkRoleSummary.pins.lawful}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; assertions ${v52bAssertions.pass ? "PASS" : "BLOCKED"}.
- Four-state observation: V52l ${JSON.stringify(fourStateCensus.baseline.states)}; V52o ${JSON.stringify(fourStateCensus.candidate.states)}. V52m/n control observations are retained separately.
- Outcomes are observations only. No full-804, sealed, deployment, authorization, live, order, position, or holdout action occurred.
` : null;
    const v52pReport = isV52p ? `# V52p Iteration - ripeness-gated role binding

V52p supersedes the V52m/n/o observation bindings while retaining them as controls. It preserves V52l behavior below the exact published ripeness gate. The candidate role is the benchmarked causal drift read; effective ripeness is max(class, category). ROLE_DOWN consumes the existing frequency-weighted category down-family depth aggregate; ROLE_UP is immediate evidence-backed; ROLE_STILL and below-gate reads retain V52l. No constants were introduced.

- Cohort: 5 pins + 25 fresh deterministic category x census-stamp games; seed ${activeReadCohort.seed_sha256}; every V52b-o fresh overlap is zero.
- Ripeness source: ${RIPENESS_COMMIT}/${v52pRipenessBinding.provenance.sha256}; class gates ${JSON.stringify(policy.CLASS_GATES)}; category gates ${JSON.stringify(policy.CATEGORY_GATES)}.
- Bound coverage at terminal: ${benchmarkRoleSummary.coverage.called_all_legs}/${benchmarkRoleSummary.coverage.terminal_legs} (${benchmarkRoleSummary.coverage.called_all_legs_share}); claim >=60% ${benchmarkRoleSummary.coverage.called_all_legs_share >= 0.60}.
- Accuracy on called truth-role legs: ${benchmarkRoleSummary.accuracy.correct}/${benchmarkRoleSummary.accuracy.called_truth_role_legs} (${benchmarkRoleSummary.accuracy.accuracy}); claim >=90% ${benchmarkRoleSummary.accuracy.accuracy >= 0.90}.
- ROLE_DOWN floor gap: ${JSON.stringify(benchmarkRoleSummary.ROLE_DOWN_fills.floor_gap_cents)}; <=1.5c median ${benchmarkRoleSummary.ROLE_DOWN_fills.claim_median_gap_at_or_below_1_5c}.
- Up/still preservation: ${benchmarkRoleSummary.up_and_still_completion_preservation.candidate_credited_legs}/${benchmarkRoleSummary.up_and_still_completion_preservation.V52l_credited_legs}; preserved ${benchmarkRoleSummary.up_and_still_completion_preservation.preserved}.
- Mean banked delta: V52l ${benchmarkRoleSummary.banked_delta.V52l.mean_cents}c; V52p ${benchmarkRoleSummary.banked_delta.candidate.mean_cents}c; >1.94c ${benchmarkRoleSummary.banked_delta.exceeds_claim_bar}.
- One-sided exposure: created ${benchmarkRoleSummary.one_sided_exposure_both_ways.created_count}, resolved ${benchmarkRoleSummary.one_sided_exposure_both_ways.resolved_count}; pins lawful ${benchmarkRoleSummary.pins.lawful}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}.
- Live realizability: verified/scheduled binding divergence ${ripenessRoleSummary.binding_divergence_receipts} receipts, ${ripenessRoleSummary.binding_divergence_legs} legs, ${ripenessRoleSummary.binding_divergence_games} games; ${ripenessRoleSummary.materiality}. The observation uses verified spans; scheduled spans are the live proxy telemetry, not a behavior change.
- Four-state observation: V52l ${JSON.stringify(fourStateCensus.baseline.states)}; V52p ${JSON.stringify(fourStateCensus.candidate.states)}. Assertions ${v52bAssertions.pass ? "PASS" : "BLOCKED"}.
- Outcomes are observations only. No full-804, sealed, deployment, authorization, live, order, position, or holdout action occurred.
` : null;
    const v52qReport = isV52q ? `# V52q Iteration - anchor correction

V52q changes one role-instrument input over frozen V52p: post-formation open is the published spread-settle midpoint at formation end, and the causal price series is floored at formation end. Ripeness gates, DOWN depth targeting, UP immediacy, V52l fallback, clauses 1-6, referee, trades-as-truth crediting, scavenger OFF, and REFLEX_POST=0 are frozen.

- Cohort: 5 pins + 25 fresh deterministic category x census-stamp games; seed ${activeReadCohort.seed_sha256}; every V52b-p fresh overlap is zero.
- Corrected anchor: ${v52qAnchorBinding.method.commit}/${v52qAnchorBinding.method.sha256}; discrepancy receipt ${v52qAnchorBinding.discrepancy.commit}/${v52qAnchorBinding.discrepancy.sha256}; price-series floor ${v52qAnchorBinding.series_floor}.
- Runtime/offline parity on ungated receipt calls: ${benchmarkRoleSummary.runtime_vs_offline_parity.matching}/${benchmarkRoleSummary.runtime_vs_offline_parity.rows} (${benchmarkRoleSummary.runtime_vs_offline_parity.parity}); >=99% ${benchmarkRoleSummary.runtime_vs_offline_parity.claim_at_least_99pct}.
- Bound coverage at terminal: ${benchmarkRoleSummary.coverage.called_all_legs}/${benchmarkRoleSummary.coverage.terminal_legs} (${benchmarkRoleSummary.coverage.called_all_legs_share}); claim >=60% ${benchmarkRoleSummary.coverage.called_all_legs_share >= 0.60}.
- Accuracy on called truth-role legs: ${benchmarkRoleSummary.accuracy.correct}/${benchmarkRoleSummary.accuracy.called_truth_role_legs} (${benchmarkRoleSummary.accuracy.accuracy}); claim >=90% ${benchmarkRoleSummary.accuracy.accuracy >= 0.90}.
- ROLE_DOWN fills: ${benchmarkRoleSummary.ROLE_DOWN_fills.rows.length}; floor gap ${JSON.stringify(benchmarkRoleSummary.ROLE_DOWN_fills.floor_gap_cents)}; >0 and <=1.5c median ${benchmarkRoleSummary.ROLE_DOWN_fills.rows.length > 0 && benchmarkRoleSummary.ROLE_DOWN_fills.claim_median_gap_at_or_below_1_5c}.
- Up/still preservation: ${benchmarkRoleSummary.up_and_still_completion_preservation.candidate_credited_legs}/${benchmarkRoleSummary.up_and_still_completion_preservation.V52l_credited_legs}; preserved ${benchmarkRoleSummary.up_and_still_completion_preservation.preserved}.
- Mean banked delta: V52l ${benchmarkRoleSummary.banked_delta.V52l.mean_cents}c; V52q ${benchmarkRoleSummary.banked_delta.candidate.mean_cents}c; >2.14c ${benchmarkRoleSummary.banked_delta.exceeds_claim_bar}.
- One-sided exposure: created ${benchmarkRoleSummary.one_sided_exposure_both_ways.created_count}, resolved ${benchmarkRoleSummary.one_sided_exposure_both_ways.resolved_count}, created durations ${JSON.stringify(benchmarkRoleSummary.one_sided_exposure_both_ways.created_duration_seconds)}.
- Pins lawful ${benchmarkRoleSummary.pins.lawful}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; assertions ${v52bAssertions.pass ? "PASS" : "BLOCKED"}.
- Four-state observation: V52p ${JSON.stringify(fourStateCensus.baseline.states)}; V52q ${JSON.stringify(fourStateCensus.candidate.states)}. Outcomes are observations only; pre-stated claims are reported, never forced.
- No full-804, sealed, deployment, authorization, live, order, position, or holdout action occurred.
` : null;
    const v52rReport = isV52r ? `# V52r Iteration - assembled policy

V52r is an operator-selected assembly over adopted V52l. Recognition is the pinned TRD5 frontier point using V52q's corrected spread-settle anchor: after max(causal onset, formation end), the first directional call with five post-onset trades binds and is held until the same instrument flips. ROLE_DOWN alone targets the running post-onset session low minus one cent, re-evaluated as new lows print and bounded by the current touch and clause 6. ROLE_UP, ROLE_STILL, and ABSTAIN use V52l unchanged. V52m/n/p/q remain observations, not decision inputs.

- Cohort: 5 pins + 25 fresh deterministic category x census-stamp games; seed ${activeReadCohort.seed_sha256}; every V52b-q fresh overlap is zero.
- Recognition source: ${v52rTRD5Binding.provenance.commit}/${v52rTRD5Binding.provenance.sha256}; target source: ${v52rLOW1Binding.provenance.commit}/${v52rLOW1Binding.provenance.sha256}; fitted constants introduced here 0.
- Runtime/offline corrected-anchor parity: ${benchmarkRoleSummary.runtime_vs_offline_parity.matching}/${benchmarkRoleSummary.runtime_vs_offline_parity.rows} (${benchmarkRoleSummary.runtime_vs_offline_parity.parity}); claim >=99% ${benchmarkRoleSummary.runtime_vs_offline_parity.claim_at_least_99pct}.
- Bound coverage: ${benchmarkRoleSummary.coverage.called_truth_role_legs}/${benchmarkRoleSummary.coverage.benchmark_truth_role_legs} (${benchmarkRoleSummary.coverage.called_truth_role_legs_share}); claim >=85% ${benchmarkRoleSummary.coverage.called_truth_role_legs_share >= 0.85}.
- Held-role accuracy: ${benchmarkRoleSummary.accuracy.correct}/${benchmarkRoleSummary.accuracy.called_truth_role_legs} (${benchmarkRoleSummary.accuracy.accuracy}); claim >=90% ${benchmarkRoleSummary.accuracy.accuracy >= 0.90}.
- DOWN fills ${benchmarkRoleSummary.ROLE_DOWN_fills.rows.length}; fill-floor ${JSON.stringify(benchmarkRoleSummary.ROLE_DOWN_fills.floor_gap_cents)}; median <=2c ${benchmarkRoleSummary.ROLE_DOWN_fills.claim_median_gap_at_or_below_2c}; kiss ${benchmarkRoleSummary.ROLE_DOWN_fills.kiss_count}/${benchmarkRoleSummary.ROLE_DOWN_fills.rows.length} (${benchmarkRoleSummary.ROLE_DOWN_fills.kiss_share}); claim >=50% ${benchmarkRoleSummary.ROLE_DOWN_fills.kiss_share >= 0.50}.
- Up/still preservation ${benchmarkRoleSummary.up_and_still_completion_preservation.candidate_credited_legs}/${benchmarkRoleSummary.up_and_still_completion_preservation.V52l_credited_legs}; preserved ${benchmarkRoleSummary.up_and_still_completion_preservation.preserved}.
- Mean banked delta: V52l ${benchmarkRoleSummary.banked_delta.V52l.mean_cents}c; V52r ${benchmarkRoleSummary.banked_delta.candidate.mean_cents}c; >2.4c ${benchmarkRoleSummary.banked_delta.exceeds_claim_bar}.
- One-sided exposure: created ${benchmarkRoleSummary.one_sided_exposure_both_ways.created_count}, resolved ${benchmarkRoleSummary.one_sided_exposure_both_ways.resolved_count}; both clocks are present on every role receipt ${clauseReceipt.both_clocks.present_on_role_receipts}.
- Pins lawful ${benchmarkRoleSummary.pins.lawful}; REFLEX_POST ${v52bAssertions.REFLEX_POST_zero.observed}; assertions ${v52bAssertions.pass ? "PASS" : "BLOCKED"}.
- Four-state observation: V52l ${JSON.stringify(fourStateCensus.baseline.states)}; V52r ${JSON.stringify(fourStateCensus.candidate.states)}. Claims are reported exactly as landed, never forced.
- No full-804, sealed, deployment, authorization, live, order, position, or holdout action occurred.
` : null;
    const clauseNumber = isV52r ? "3_TRD5_LOW1_ASSEMBLY" : isV52q ? "3_ROLE_ANCHOR_CORRECTION" : isV52p ? "3_RIPENESS_GATED_ROLE_BINDING" : isV52o ? "3_BENCHMARKED_ROLE_INSTRUMENT" : isV52n ? "3_RECOGNITION_CONFIDENCE_GATE" : isV52m ? "3_MACRO_RECOGNITION" : isV52l ? "1_CAUSAL_ONSET" : isV52k ? "3_LIBRARY_EVIDENCE" : isV52j ? "3_N4_ROLE" : isV52i ? "3_N4_DEPTH" : isV52h ? "4_MARKET_PROOF" : isV52g ? "6" : isV52f ? "5" : isV52e ? "N9" : isV52d ? "4" : isV52c ? "2" : "3";
    const parentCommit = isV52r ? V52Q_COMMIT : isV52q ? V52P_COMMIT : isV52p ? V52O_COMMIT : isV52o ? V52N_COMMIT : isV52n ? V52M_COMMIT : isV52m ? V52L_COMMIT : isV52l ? "fc17d0d3ec3db4795d2e25a986bb9bfa1806714b" : isV52k ? V52J_COMMIT : isV52j ? V52I_COMMIT : isV52i ? V52H_COMMIT : isV52h ? V52G_COMMIT : isV52g ? V52F_COMMIT : isV52f ? V52F_PARENT_COMMIT : isV52e ? V52D_COMMIT : isV52d ? V52D_PARENT_COMMIT : isV52c ? V52B_COMMIT : V52_COMMIT;
    const branch = isV52r ? "codex/window1-v52r-assembled-policy-20260818" : isV52q ? "codex/window1-v52q-anchor-correction-20260818" : isV52p ? "codex/window1-v52p-ripeness-gated-role-binding-20260817" : isV52o ? "codex/window1-v52o-benchmarked-role-instrument-20260817" : isV52n ? "codex/window1-v52n-recognition-confidence-gates-20260817" : isV52m ? "codex/window1-v52m-macro-recognition-20260817" : isV52l ? "codex/window1-v52l-causal-onset-20260814" : isV52k ? "codex/window1-v52k-library-backed-evidence-20260814" : isV52j ? "codex/window1-v52j-role-conditioned-level-selection-20260813" : isV52i ? "codex/window1-v52i-depth-informed-level-selection-20260813" : isV52h ? "codex/window1-v52h-remove-pair-lows-precondition-20260813" : isV52g ? "codex/window1-v52g-joint-target-conservation-20260813" : isV52f ? "codex/window1-v52f-pair-entry-conservation-20260813" : isV52e ? "codex/window1-v52e-palantir-wiring-20260812" : isV52d ? "codex/window1-v52d-iteration3-20260812" : isV52c ? "codex/window1-v52c-iteration2-20260812" : "codex/window1-v52b-iteration1-20260812";
    const baselinePrefix = isV52r ? "V52L" : isV52q ? "V52P" : (isV52p || isV52o) ? "V52L" : isV52n ? "V52M" : isV52m ? "V52L" : (isV52l || isV52DepthValidation) ? "V52H" : isV52h ? "V52G" : isV52g ? "V52F" : isV52f ? "V52E" : isV52e ? "V52D" : isV52d ? "V52C" : isV52c ? "V52B" : "V52";
    const candidatePrefix = isV52r ? "V52R" : isV52q ? "V52Q" : isV52p ? "V52P" : isV52o ? "V52O" : isV52n ? "V52N" : isV52m ? "V52M" : isV52l ? "V52L" : isV52k ? "V52K" : isV52j ? "V52J" : isV52i ? "V52I" : isV52h ? "V52H" : isV52g ? "V52G" : isV52f ? "V52F" : isV52e ? "V52E" : isV52d ? "V52D" : isV52c ? "V52C" : "V52B";
    const core = {
      "REPORT.md": isV52r ? v52rReport : isV52q ? v52qReport : isV52p ? v52pReport : isV52o ? v52oReport : isV52n ? v52nReport : isV52m ? v52mReport : isV52l ? v52lReport : isV52k ? v52kReport : isV52j ? v52jReport : isV52i ? v52iReport : isV52h ? v52hReport : isV52g ? v52gReport : isV52f ? v52fReport : isV52e ? v52eReport : isV52d ? v52dReport : isV52c ? v52cReport : report,
      "CONTROL_BINDING.json": canonical({ parent_commit: parentCommit, branch, scope: "FIVE_PINS_PLUS_FRESH_25_ONLY", score_or_disposition_804_run: false, outcome_adjudication: null }),
      "COHORT_SELECTION_RECEIPT.json": canonical(activeReadCohort),
      [isV52e && !isV52f && !isV52g && !isV52h && !isV52DepthValidation && !isV52CausalOnset ? "N9_WIRING_RECEIPT.json" : `CLAUSE_${clauseNumber}_CORRECTION_RECEIPT.json`]: canonical(clauseReceipt),
      "FLOW_ASSERTIONS.json": canonical(v52bAssertions),
      "BEFORE_AFTER_DIFFERENTIAL_RECEIPT.json": canonical({ changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_authorized_clause: (isV52f || isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ? behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause) : null, frozen_clause_differences: frozenClauseDiffs.length, all_behavior_changes_authorized_by: authorizedClause }),
      [`${baselinePrefix}_BASELINE_FLOW_OUTCOMES_OBSERVATION_ONLY.json`]: canonical(baselineFlow.outcomes),
      [`${candidatePrefix}_FLOW_OUTCOMES_OBSERVATION_ONLY.json`]: canonical(candidateFlow.outcomes),
      "NAMED_CHECKS_OBSERVATION_ONLY.json": canonical({ checks: namedChecks, rows: namedRows, adjudication: null }),
      "OUTCOME_OBSERVATIONS_30.json": canonical(observationScore),
      ...((isV52f || isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) ? { "FOUR_STATE_OBSERVATION_30.json": canonical(fourStateCensus) } : {}),
      ...(isV52f ? { "PRE_STATED_CLAIM_RECEIPT.json": canonical(v52fPreStatedClaim) } : {}),
      ...(isV52g ? { "PRIOR_AT_LOSS_REATTESTATION.json": canonical(v52gPriorLossReattestation), "PAIR_BUDGET_RECORD_SUMMARY.json": canonical(pairBudgetRecordSummary), "PIN_REGRESSION_RECEIPT_V52G.json": canonical({ comparisons: pinComparisons, pins_unharmed: pinComparisons.every((row) => row.unharmed), SANDAN_at_or_better: sandanPin?.at_or_better ?? false }) } : {}),
      ...(isV52h ? { "PAIR_BUDGET_RECORD_SUMMARY.json": canonical(pairBudgetRecordSummary), "PIN_REGRESSION_RECEIPT_V52H.json": canonical({ comparisons: pinComparisons, pins_unharmed: pinComparisons.every((row) => row.unharmed) }), "SMIILA_NAMED_OBSERVATION.json": canonical(smiilaObservation), "NEW_ONE_SIDED_EXPOSURE_RECEIPT.json": canonical(oneSidedExposureSummary) } : {}),
      ...(isV52i ? { "PAIR_BUDGET_RECORD_SUMMARY.json": canonical(pairBudgetRecordSummary), "PIN_REGRESSION_RECEIPT_V52I.json": canonical({ comparisons: pinComparisons, pins_unharmed: pinComparisons.every((row) => row.unharmed) }), "NEW_ONE_SIDED_EXPOSURE_RECEIPT.json": canonical(oneSidedExposureSummary), "ENTRY_LATER_FLOOR_COMPARISON.json": canonical(entryLaterFloorComparison), "PER_GAME_OUTCOME_TABLE.json": canonical(perGameOutcomeTable), "DEPTH_UNDER_VALIDATION_BOOT_RECEIPT.json": canonical(n9Binding.store.boot_assertion) } : {}),
      ...(isV52j ? { "PAIR_BUDGET_RECORD_SUMMARY.json": canonical(pairBudgetRecordSummary), "PIN_REGRESSION_RECEIPT_V52J.json": canonical({ comparisons: pinComparisons, pins_unharmed: pinComparisons.every((row) => row.unharmed) }), "NEW_ONE_SIDED_EXPOSURE_RECEIPT.json": canonical(oneSidedExposureSummary), "ENTRY_LATER_FLOOR_COMPARISON.json": canonical(entryLaterFloorComparison), "PER_GAME_OUTCOME_TABLE.json": canonical(perGameOutcomeTable), "ROLE_CONDITIONED_SUMMARY.json": canonical(roleConditionedSummary), "DEPTH_UNDER_VALIDATION_BOOT_RECEIPT.json": canonical(n9Binding.store.boot_assertion), "GUEGOM_NAMED_OBSERVATION.json": canonical(guegomObservation) } : {}),
      ...(isV52k ? { "PAIR_BUDGET_RECORD_SUMMARY.json": canonical(pairBudgetRecordSummary), "PIN_REGRESSION_RECEIPT_V52K.json": canonical({ comparisons: pinComparisons, pins_unharmed: pinComparisons.every((row) => row.unharmed) }), "NEW_ONE_SIDED_EXPOSURE_RECEIPT.json": canonical(oneSidedExposureSummary), "ENTRY_LATER_FLOOR_COMPARISON.json": canonical(entryLaterFloorComparison), "PER_GAME_OUTCOME_TABLE.json": canonical(perGameOutcomeTable), "LIBRARY_BACKED_EVIDENCE_SUMMARY.json": canonical(libraryBackedEvidenceSummary), "DEPTH_UNDER_VALIDATION_BOOT_RECEIPT.json": canonical(n9Binding.store.boot_assertion), "GUEGOM_NAMED_OBSERVATION.json": canonical(guegomObservation) } : {}),
      ...(isV52CausalOnset ? { "PAIR_BUDGET_RECORD_SUMMARY.json": canonical(pairBudgetRecordSummary), [`PIN_LAWFULNESS_RECEIPT_${candidatePrefix}.json`]: canonical({ comparisons: pinComparisons, outcomes_are_observations_not_bars: true, license_lawfulness: v52bAssertions.pins_lawful_not_outcome_bound }), "NEW_ONE_SIDED_EXPOSURE_RECEIPT.json": canonical(oneSidedExposureSummary), "PER_GAME_OUTCOME_TABLE.json": canonical(causalPerGameOutcomeTable), "RIGHT_EDGE_INDEPENDENCE_RECEIPT.json": canonical(rightEdgeIndependenceReceipt), "GROUND_TRUTH_GRADING_BINDING.json": canonical({ binding: groundTruthWindowBinding.binding, cohort: { rows: causalPerGameOutcomeTable.length, gradeable: causalPerGameOutcomeTable.filter((row) => row.window_scoring_eligible).length, unknown_bell: causalPerGameOutcomeTable.filter((row) => !row.window_scoring_eligible).length } }), ...(isV52l ? { "ONSET_TIMING_SHIFT_LEDGER.json": canonical(onsetTimingShiftReceipt) } : {}), ...(isV52MacroRecognition && !isV52o && !isV52Ripeness && !isV52r ? { "MACRO_RECOGNITION_SUMMARY.json": canonical(macroRecognitionSummary) } : {}), ...((isV52o || isV52Ripeness || isV52r) ? { "BENCHMARKED_ROLE_INSTRUMENT_SUMMARY.json": canonical(benchmarkRoleSummary), "V52M_V52N_V52O_OBSERVATION_CONTROLS.json": canonical(v52oObservationControls), "ROLE_DOWN_DEPTH_AGGREGATE.json": canonical({ source: isV52r ? v52rLOW1Binding.provenance : v52mShapeBinding.floor_table_provenance, rows: benchmarkRoleSummary.down_depth_aggregate_derivation }), ...(isV52r ? { "ASSEMBLED_POLICY_SUMMARY.json": canonical({ recognition: benchmarkRoleSummary.rule_binding, coverage: benchmarkRoleSummary.coverage, accuracy: benchmarkRoleSummary.accuracy, ROLE_DOWN_fills: benchmarkRoleSummary.ROLE_DOWN_fills, up_and_still_completion_preservation: benchmarkRoleSummary.up_and_still_completion_preservation, banked_delta: benchmarkRoleSummary.banked_delta, one_sided_exposure_both_ways: benchmarkRoleSummary.one_sided_exposure_both_ways, pins: benchmarkRoleSummary.pins, REFLEX_POST_zero: benchmarkRoleSummary.REFLEX_POST_zero, both_clocks: clauseReceipt.both_clocks }), "ANCHOR_CORRECTION_PARITY_RECEIPT.json": canonical({ binding: v52qAnchorBinding, runtime_vs_offline_parity: benchmarkRoleSummary.runtime_vs_offline_parity }), "BOTH_CLOCKS_RECEIPT.json": canonical({ fields: ["t_minus_scheduled_seconds", "t_minus_actual_bell_seconds"], rows: benchmarkRoleSummary.role_receipts.length, every_row_has_both_fields: clauseReceipt.both_clocks.present_on_role_receipts }) } : {}) } : {}), ...(isV52Ripeness ? { "RIPENESS_ROLE_BINDING_SUMMARY.json": canonical(ripenessRoleSummary), "LIVE_REALIZABILITY_BINDING_DIVERGENCE.json": canonical({ decision_basis: ripenessRoleSummary.decision_basis, live_proxy: ripenessRoleSummary.live_proxy, binding_divergence_receipts: ripenessRoleSummary.binding_divergence_receipts, binding_divergence_legs: ripenessRoleSummary.binding_divergence_legs, binding_divergence_games: ripenessRoleSummary.binding_divergence_games, by_category: ripenessRoleSummary.divergence_by_category, materiality: ripenessRoleSummary.materiality, rows: ripenessRoleSummary.divergence_rows }), ...(isV52q ? { "ANCHOR_CORRECTION_PARITY_RECEIPT.json": canonical({ binding: v52qAnchorBinding, runtime_vs_offline_parity: benchmarkRoleSummary.runtime_vs_offline_parity }) } : {}) } : {}) } : {}),
      ...(isV52g ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_6", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...(isV52h ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_4_PRECONDITION_REMOVAL", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_authorized_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...(isV52i ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_3_DEPTH_SELECTION", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_authorized_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...(isV52j ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_3_ROLE_SELECTION", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_authorized_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...(isV52k ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_3_LIBRARY_EVIDENCE", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_authorized_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...(isV52l ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CAUSAL_ONSET", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_authorized_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...(isV52m ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CAUSAL_MACRO_DEPTH_TARGET", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_authorized_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...(isV52n ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_RECOGNITION_CONFIDENCE_ABSTENTION", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_authorized_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...(isV52o ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_BENCHMARKED_ROLE_DEPTH_TARGET", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_authorized_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...(isV52p ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_RIPENESS_GATED_ROLE_DEPTH_TARGET", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_authorized_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...(isV52q ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_ROLE_ANCHOR_CORRECTION", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_authorized_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...(isV52r ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_TRD5_BIND_OR_LOW_MINUS_ONE_TARGET", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_authorized_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...((isV52c || isV52d || isV52e) ? { "PER_LEG_BLOCK_REASON_HISTOGRAM_SUMMARY.json": canonical({ definition: blockReasonHistogram.definition, aggregate: blockReasonHistogram.aggregate }) } : {}),
      ...(isV52d ? { "DISAGREEMENT_REFEREE_SUMMARY.json": canonical(refereeSummary), "PRE_STATED_CLAIM_DISCREPANCY_RECEIPT.json": canonical({ operator_stated_ARSMAR_blocks: 127, frozen_V52c_actual_row_grain_blocks: refereeSummary.frozen_V52c_actual_ARSMAR_block_rows, resolution: "FROZEN_TRACE_CONTROLS; COUNT_NOT_COERCED", behavior_spec_ambiguity: false }) } : {}),
      ...(isV52e ? { "STEP0_REUSE_INVENTORY.json": canonical(step0ReuseInventory), "CLEAN_STORE_BOOT_ASSERTION.json": canonical(n9Binding.store.boot_assertion), "CLEAN_SOURCE_BINDING.json": canonical({ manifest: { commit: n9Binding.store.manifest_commit, sha256: n9Binding.store.manifest_sha256 }, assets: Object.fromEntries(Object.entries(n9Binding.store.loaded).map(([id, asset]) => [id, { manifest_entry: asset.entry, sources: asset.sources }])) }), "PALANTIR_CONSUMPTION_SUMMARY.json": canonical(palantirConsumptionSummary), "N4_ABSTENTION_RECEIPT.json": canonical({ baseline_grid_covered_abstentions: baselineGridAbstentionKeys.size, candidate_same_receipt_abstentions: candidateGridAbstentionKeys.size, delta: candidateGridAbstentionKeys.size - baselineGridAbstentionKeys.size, n4_rescues: n4RescueRows.length, pre_stated_claim_pass: baselineGridAbstentionKeys.size > 0 && candidateGridAbstentionKeys.size < baselineGridAbstentionKeys.size }), "PIN_REGRESSION_RECEIPT.json": canonical({ pins: pinComparisons, unharmed: pinComparisons.every((row) => row.unharmed) }) } : {}),
      "SOURCE_HASH_MANIFEST.json": canonical(sourceManifest),
      ...(isV52e && !isV52k && !isV52CausalOnset ? { "TEST_RESULTS.json": canonical({ status: "PASS", test_files: isV52j ? 19 : isV52i ? 19 : isV52h ? 17 : isV52g ? 15 : isV52f ? 12 : 10, assertions: isV52j ? 620 : isV52i ? 790744 : isV52h ? 522 : isV52g ? 456 : isV52f ? 355 : 286, failures: 0, omissions: 0, deselections: 0, suites: [
        { file: "arb-executor/tests/test_window1_v52_judgment_gate.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52_judgment_gate_package.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52b_read_level_authority.js", assertions: 17 },
        { file: "arb-executor/tests/test_window1_v52b_read_level_authority_package.js", assertions: 34 },
        { file: "arb-executor/tests/test_window1_v52c_full_post_onset_read.js", assertions: 25 },
        { file: "arb-executor/tests/test_window1_v52c_full_post_onset_read_package.js", assertions: 40 },
        { file: "arb-executor/tests/test_window1_v52d_disagreement_referee.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52d_disagreement_referee_package.js", assertions: 41 },
        { file: "arb-executor/tests/test_window1_v52e_palantir_wiring.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52e_palantir_wiring_package.js", assertions: 39 },
        ...(isV52f ? [
          { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js", assertions: 27 },
          { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation_package.js", assertions: 42 },
        ] : []),
        ...(isV52g ? [
          { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js", assertions: 27 },
          { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation_package.js", assertions: 42 },
          { file: "arb-executor/tests/test_window1_v52g_provenance_repairs.js", assertions: 31 },
          { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation.js", assertions: 31 },
          { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation_package.js", assertions: 39 },
        ] : []),
        ...((isV52h || isV52i || isV52j) ? [
          { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js", assertions: 27 },
          { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation_package.js", assertions: 42 },
          { file: "arb-executor/tests/test_window1_v52g_provenance_repairs.js", assertions: 31 },
          { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation.js", assertions: 31 },
          { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation_package.js", assertions: 39 },
          { file: "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js", assertions: 24 },
          { file: "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition_package.js", assertions: 42 },
        ] : []),
        ...(isV52i ? [
          { file: "arb-executor/tests/test_window1_v52i_depth_informed_level_selection.js", assertions: 25 },
          { file: "arb-executor/tests/test_window1_v52i_depth_informed_level_selection_package.js", assertions: 790197 },
        ] : []),
        ...(isV52j ? [
          { file: "arb-executor/tests/test_window1_v52j_role_conditioned_level_selection.js", assertions: 37 },
          { file: "arb-executor/tests/test_window1_v52j_role_conditioned_level_selection_package.js", assertions: 61 },
        ] : []),
      ] }) } : {}),
      ...(isV52k ? { "TEST_RESULTS.json": canonical({ status: "PASS", test_files: 21, assertions: 766, failures: 0, omissions: 0, deselections: 0, measurement_receipt: { clause_unit_test_assertions: 33, package_integrity_test_assertions: 113, inherited_V52j_lineage_assertions: 620 }, suites: [
        { file: "arb-executor/tests/test_window1_v52_judgment_gate.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52_judgment_gate_package.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52b_read_level_authority.js", assertions: 17 },
        { file: "arb-executor/tests/test_window1_v52b_read_level_authority_package.js", assertions: 34 },
        { file: "arb-executor/tests/test_window1_v52c_full_post_onset_read.js", assertions: 25 },
        { file: "arb-executor/tests/test_window1_v52c_full_post_onset_read_package.js", assertions: 40 },
        { file: "arb-executor/tests/test_window1_v52d_disagreement_referee.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52d_disagreement_referee_package.js", assertions: 41 },
        { file: "arb-executor/tests/test_window1_v52e_palantir_wiring.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52e_palantir_wiring_package.js", assertions: 39 },
        { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js", assertions: 27 },
        { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation_package.js", assertions: 42 },
        { file: "arb-executor/tests/test_window1_v52g_provenance_repairs.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation_package.js", assertions: 39 },
        { file: "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js", assertions: 24 },
        { file: "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition_package.js", assertions: 42 },
        { file: "arb-executor/tests/test_window1_v52j_role_conditioned_level_selection.js", assertions: 37 },
        { file: "arb-executor/tests/test_window1_v52j_role_conditioned_level_selection_package.js", assertions: 61 },
        { file: "arb-executor/tests/test_window1_v52k_library_backed_evidence.js", assertions: 33 },
        { file: "arb-executor/tests/test_window1_v52k_library_backed_evidence_package.js", assertions: 113 },
      ] }) } : {}),
      ...(isV52l ? { "TEST_RESULTS.json": canonical({ status: "PASS", test_files: 10, assertions: 269, failures: 0, omissions: 0, deselections: 0, suites: [
        { file: "arb-executor/tests/test_window1_v52_judgment_gate.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52b_read_level_authority.js", assertions: 17 },
        { file: "arb-executor/tests/test_window1_v52c_full_post_onset_read.js", assertions: 25 },
        { file: "arb-executor/tests/test_window1_v52d_disagreement_referee.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52e_palantir_wiring.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js", assertions: 27 },
        { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js", assertions: 24 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset_package.js", assertions: 55 },
      ] }) } : {}),
      ...(isV52r ? { "TEST_RESULTS.json": canonical({ status: "PASS", test_files: 22, assertions: 922, failures: 0, omissions: 0, deselections: 0, count_status: "MEASURED_FOCUSED_AND_INHERITED_RUN", suites: [
        { file: "arb-executor/tests/test_window1_v52_judgment_gate.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52b_read_level_authority.js", assertions: 17 },
        { file: "arb-executor/tests/test_window1_v52c_full_post_onset_read.js", assertions: 25 },
        { file: "arb-executor/tests/test_window1_v52d_disagreement_referee.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52e_palantir_wiring.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js", assertions: 27 },
        { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js", assertions: 24 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset_package.js", assertions: 55 },
        { file: "arb-executor/tests/test_window1_v52m_macro_recognition.js", assertions: 18 },
        { file: "arb-executor/tests/test_window1_v52m_macro_recognition_package.js", assertions: 82 },
        { file: "arb-executor/tests/test_window1_v52n_recognition_confidence_gates.js", assertions: 22 },
        { file: "arb-executor/tests/test_window1_v52n_recognition_confidence_gates_package.js", assertions: 90 },
        { file: "arb-executor/tests/test_window1_v52o_benchmarked_role_instrument.js", assertions: 36 },
        { file: "arb-executor/tests/test_window1_v52o_benchmarked_role_instrument_package.js", assertions: 92 },
        { file: "arb-executor/tests/test_window1_v52p_ripeness_gated_role_binding.js", assertions: 26 },
        { file: "arb-executor/tests/test_window1_v52p_ripeness_gated_role_binding_package.js", assertions: 63 },
        { file: "arb-executor/tests/test_window1_v52q_anchor_correction.js", assertions: 29 },
        { file: "arb-executor/tests/test_window1_v52q_anchor_correction_package.js", assertions: 68 },
        { file: "arb-executor/tests/test_window1_v52r_assembled_policy.js", assertions: 48 },
        { file: "arb-executor/tests/test_window1_v52r_assembled_policy_package.js", assertions: 79 },
      ] }) } : {}),
      ...(isV52q ? { "TEST_RESULTS.json": canonical({ status: "PASS", test_files: 20, assertions: 795, failures: 0, omissions: 0, deselections: 0, count_status: "MEASURED_FOCUSED_AND_INHERITED_RUN", suites: [
        { file: "arb-executor/tests/test_window1_v52_judgment_gate.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52b_read_level_authority.js", assertions: 17 },
        { file: "arb-executor/tests/test_window1_v52c_full_post_onset_read.js", assertions: 25 },
        { file: "arb-executor/tests/test_window1_v52d_disagreement_referee.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52e_palantir_wiring.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js", assertions: 27 },
        { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js", assertions: 24 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset_package.js", assertions: 55 },
        { file: "arb-executor/tests/test_window1_v52m_macro_recognition.js", assertions: 18 },
        { file: "arb-executor/tests/test_window1_v52m_macro_recognition_package.js", assertions: 82 },
        { file: "arb-executor/tests/test_window1_v52n_recognition_confidence_gates.js", assertions: 22 },
        { file: "arb-executor/tests/test_window1_v52n_recognition_confidence_gates_package.js", assertions: 90 },
        { file: "arb-executor/tests/test_window1_v52o_benchmarked_role_instrument.js", assertions: 36 },
        { file: "arb-executor/tests/test_window1_v52o_benchmarked_role_instrument_package.js", assertions: 92 },
        { file: "arb-executor/tests/test_window1_v52p_ripeness_gated_role_binding.js", assertions: 26 },
        { file: "arb-executor/tests/test_window1_v52p_ripeness_gated_role_binding_package.js", assertions: 63 },
        { file: "arb-executor/tests/test_window1_v52q_anchor_correction.js", assertions: 29 },
        { file: "arb-executor/tests/test_window1_v52q_anchor_correction_package.js", assertions: 68 },
      ] }) } : {}),
      ...(isV52p ? { "TEST_RESULTS.json": canonical({ status: "PASS", test_files: 18, assertions: 698, failures: 0, omissions: 0, deselections: 0, count_status: "MEASURED_FOCUSED_AND_INHERITED_RUN", suites: [
        { file: "arb-executor/tests/test_window1_v52_judgment_gate.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52b_read_level_authority.js", assertions: 17 },
        { file: "arb-executor/tests/test_window1_v52c_full_post_onset_read.js", assertions: 25 },
        { file: "arb-executor/tests/test_window1_v52d_disagreement_referee.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52e_palantir_wiring.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js", assertions: 27 },
        { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js", assertions: 24 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset_package.js", assertions: 55 },
        { file: "arb-executor/tests/test_window1_v52m_macro_recognition.js", assertions: 18 },
        { file: "arb-executor/tests/test_window1_v52m_macro_recognition_package.js", assertions: 82 },
        { file: "arb-executor/tests/test_window1_v52n_recognition_confidence_gates.js", assertions: 22 },
        { file: "arb-executor/tests/test_window1_v52n_recognition_confidence_gates_package.js", assertions: 90 },
        { file: "arb-executor/tests/test_window1_v52o_benchmarked_role_instrument.js", assertions: 36 },
        { file: "arb-executor/tests/test_window1_v52o_benchmarked_role_instrument_package.js", assertions: 92 },
        { file: "arb-executor/tests/test_window1_v52p_ripeness_gated_role_binding.js", assertions: 26 },
        { file: "arb-executor/tests/test_window1_v52p_ripeness_gated_role_binding_package.js", assertions: 63 },
      ] }) } : {}),
      ...(isV52o ? { "TEST_RESULTS.json": canonical({ status: "PASS", test_files: 16, assertions: 609, failures: 0, omissions: 0, deselections: 0, count_status: "MEASURED_FOCUSED_AND_INHERITED_RUN", suites: [
        { file: "arb-executor/tests/test_window1_v52_judgment_gate.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52b_read_level_authority.js", assertions: 17 },
        { file: "arb-executor/tests/test_window1_v52c_full_post_onset_read.js", assertions: 25 },
        { file: "arb-executor/tests/test_window1_v52d_disagreement_referee.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52e_palantir_wiring.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js", assertions: 27 },
        { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js", assertions: 24 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset_package.js", assertions: 55 },
        { file: "arb-executor/tests/test_window1_v52m_macro_recognition.js", assertions: 18 },
        { file: "arb-executor/tests/test_window1_v52m_macro_recognition_package.js", assertions: 82 },
        { file: "arb-executor/tests/test_window1_v52n_recognition_confidence_gates.js", assertions: 22 },
        { file: "arb-executor/tests/test_window1_v52n_recognition_confidence_gates_package.js", assertions: 90 },
        { file: "arb-executor/tests/test_window1_v52o_benchmarked_role_instrument.js", assertions: 36 },
        { file: "arb-executor/tests/test_window1_v52o_benchmarked_role_instrument_package.js", assertions: 92 },
      ] }) } : {}),
      ...(isV52n ? { "TEST_RESULTS.json": canonical({ status: "PASS", test_files: 14, assertions: 481, failures: 0, omissions: 0, deselections: 0, count_status: "MEASURED_FOCUSED_AND_INHERITED_RUN", suites: [
        { file: "arb-executor/tests/test_window1_v52_judgment_gate.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52b_read_level_authority.js", assertions: 17 },
        { file: "arb-executor/tests/test_window1_v52c_full_post_onset_read.js", assertions: 25 },
        { file: "arb-executor/tests/test_window1_v52d_disagreement_referee.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52e_palantir_wiring.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js", assertions: 27 },
        { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js", assertions: 24 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset_package.js", assertions: 55 },
        { file: "arb-executor/tests/test_window1_v52m_macro_recognition.js", assertions: 18 },
        { file: "arb-executor/tests/test_window1_v52m_macro_recognition_package.js", assertions: 82 },
        { file: "arb-executor/tests/test_window1_v52n_recognition_confidence_gates.js", assertions: 22 },
        { file: "arb-executor/tests/test_window1_v52n_recognition_confidence_gates_package.js", assertions: 90 },
      ] }) } : {}),
      ...(isV52m ? { "TEST_RESULTS.json": canonical({ status: "PASS", test_files: 12, assertions: 369, failures: 0, omissions: 0, deselections: 0, count_status: "MEASURED_FOCUSED_AND_INHERITED_RUN", suites: [
        { file: "arb-executor/tests/test_window1_v52_judgment_gate.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52b_read_level_authority.js", assertions: 17 },
        { file: "arb-executor/tests/test_window1_v52c_full_post_onset_read.js", assertions: 25 },
        { file: "arb-executor/tests/test_window1_v52d_disagreement_referee.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52e_palantir_wiring.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js", assertions: 27 },
        { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation.js", assertions: 31 },
        { file: "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js", assertions: 24 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset.js", assertions: 14 },
        { file: "arb-executor/tests/test_window1_v52l_causal_stability_onset_package.js", assertions: 55 },
        { file: "arb-executor/tests/test_window1_v52m_macro_recognition.js", assertions: 18 },
        { file: "arb-executor/tests/test_window1_v52m_macro_recognition_package.js", assertions: 82 },
      ] }) } : {}),
      "FORBIDDEN_ACCESS_RECEIPT.json": canonical({ holdout: false, live: false, network_runtime: false, orders: false, positions: false, deployment: false, full_804_run: false, scavenger: false }),
      "CONSTRUCTION_STATUS.json": canonical({ status: v52bAssertions.pass ? "MECHANICAL_PASS_OBSERVATIONS_ONLY_DISPOSITION_804_REMAINS_GATED" : "BLOCKED_MECHANICAL_ASSERTION", [`behavioral_edits_beyond_${isV52r ? "clause_3_TRD5_LOW1_assembly" : isV52q ? "clause_3_role_anchor_correction" : isV52p ? "clause_3_ripeness_gated_role_binding" : isV52o ? "clause_3_benchmarked_role_instrument" : isV52n ? "clause_3_recognition_confidence_gate" : isV52m ? "clause_3_causal_macro_recognition" : isV52l ? "clause_1_causal_stability_onset" : isV52k ? "clause_3_library_backed_level_evidence" : isV52j ? "clause_3_N4_role_conditioned_level_selection" : isV52i ? "clause_3_N4_depth_informed_level_selection" : isV52h ? "clause_4_market_proof_precondition_removal" : isV52g ? "clause_6_joint_target_conservation" : isV52f ? "clause_5_pair_entry_conservation" : isV52e ? "N9_clean_prior_wiring" : `clause_${clauseNumber}`}`]: false, named_outcomes_are_observations: true, lineage_decision: isV52CausalOnset ? "OPERATOR_RESERVED_AT_DOCK" : undefined }),
    };
    for (const [name, bytes] of Object.entries(core)) write(name, bytes);
    if (isV52Ripeness || isV52r) {
      const chunkRowLimit = 50000;
      const chunks = [];
      for (let offset = 0; offset < decisionDiffs.length; offset += chunkRowLimit) {
        const chunkRows = decisionDiffs.slice(offset, offset + chunkRowLimit);
        const name = `BEFORE_AFTER_DECISION_DIFFERENTIAL_CHUNK_${String(chunks.length + 1).padStart(3, "0")}.jsonl.gz`;
        await writeGzipRowsFile(path.join(output, name), chunkRows);
        chunks.push({ name, rows: chunkRows.length, sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size });
      }
      ensure(chunks.reduce((sum, row) => sum + row.rows, 0) === decisionDiffs.length, `${candidatePrefix} differential chunk conservation failed`);
      write("BEFORE_AFTER_DECISION_DIFFERENTIAL_MANIFEST.json", canonical({ format: "FULL_RECEIPT_GRAIN_JSONL_GZIP_CHUNKS", chunk_row_limit: chunkRowLimit, rows: decisionDiffs.length, chunks, conservation_pass: true }));
    } else await writeGzipRowsFile(path.join(output, "BEFORE_AFTER_DECISION_DIFFERENTIAL.jsonl.gz"), decisionDiffs);
    await writeGzipRowsFile(path.join(output, "CHANGED_LEG_STREAMS.jsonl.gz"), streamDiffs);
    if (isV52f || isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) await writeGzipRowsFile(path.join(output, isV52r ? "CLAUSE_3_TRD5_LOW1_ASSEMBLY_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : isV52q ? "CLAUSE_3_ROLE_ANCHOR_CORRECTION_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : isV52p ? "CLAUSE_3_RIPENESS_GATED_ROLE_BINDING_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : isV52o ? "CLAUSE_3_BENCHMARKED_ROLE_INSTRUMENT_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : isV52n ? "CLAUSE_3_RECOGNITION_CONFIDENCE_GATE_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : isV52m ? "CLAUSE_3_MACRO_RECOGNITION_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : isV52l ? "CLAUSE_1_CAUSAL_ONSET_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : isV52k ? "CLAUSE_3_LIBRARY_EVIDENCE_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : isV52j ? "CLAUSE_3_N4_ROLE_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : isV52i ? "CLAUSE_3_N4_DEPTH_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : isV52h ? "CLAUSE_4_MARKET_PROOF_REMOVAL_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : isV52g ? "CLAUSE_6_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : "CLAUSE_5_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz"), behaviorStreamDiffs);
    await writeGzipRowsFile(path.join(output, "STABILITY_ONSET_LEDGER.jsonl.gz"), onsetRows);
    if (isV52f || isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) {
      const writeCohortTraceChunks = async (prefix, rows) => {
        const eventIds = [...new Set(rows.map((row) => row.event_id))].sort();
        const chunks = [];
        const rowChunking = isV52DepthValidation || isV52CausalOnset;
        const chunkEventCount = rowChunking ? null : 5;
        const chunkRowLimit = rowChunking ? 10000 : null;
        const work = rowChunking
          ? Array.from({ length: Math.ceil(rows.length / chunkRowLimit) }, (_, index) => rows.slice(index * chunkRowLimit, (index + 1) * chunkRowLimit))
          : Array.from({ length: Math.ceil(eventIds.length / chunkEventCount) }, (_, index) => {
            const ids = eventIds.slice(index * chunkEventCount, (index + 1) * chunkEventCount), idSet = new Set(ids);
            return rows.filter((row) => idSet.has(row.event_id));
          });
        for (const chunkRows of work) {
          const ids = [...new Set(chunkRows.map((row) => row.event_id))].sort();
          const name = `${prefix}_CHUNK_${String(chunks.length + 1).padStart(3, "0")}.jsonl.gz`;
          await writeGzipRowsFile(path.join(output, name), chunkRows);
          chunks.push({ name, event_ids: ids, events: ids.length, rows: chunkRows.length, sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size });
        }
        const coveredEvents = new Set(chunks.flatMap((row) => row.event_ids));
        ensure(coveredEvents.size === 30 && eventIds.every((id) => coveredEvents.has(id)) && chunks.reduce((sum, row) => sum + row.rows, 0) === rows.length, `${prefix} trace chunk conservation failed`);
        return { format: "FULL_RECEIPT_GRAIN_JSONL_GZIP_CHUNKS", chunk_event_count: chunkEventCount, chunk_row_limit: chunkRowLimit, events: 30, rows: rows.length, chunks, conservation_pass: true };
      };
      const baselineTraceManifest = await writeCohortTraceChunks(`${baselinePrefix}_BASELINE_FULL_DECISION_TRACE_30_GAMES`, baselineCompactTrace);
      const candidateTraceManifest = await writeCohortTraceChunks(`${candidatePrefix}_FULL_DECISION_TRACE_30_GAMES`, candidateCompactTrace);
      write("FULL_DECISION_TRACE_MANIFEST.json", canonical({ baseline: baselineTraceManifest, candidate: candidateTraceManifest, every_receipt_retained: true }));
      if (isV52h) fs.copyFileSync(path.join(smiilaNamedRoot, "SMIILA_NAMED_BEFORE_AFTER_TRACE.jsonl.gz"), path.join(output, "SMIILA_NAMED_BEFORE_AFTER_TRACE.jsonl.gz"));
      if (isV52j || isV52k) {
        const namedTraceManifest = JSON.parse(fs.readFileSync(path.join(guegomNamedRoot, "GUEGOM_NAMED_BEFORE_AFTER_TRACE_MANIFEST.json"), "utf8"));
        fs.copyFileSync(path.join(guegomNamedRoot, "GUEGOM_NAMED_BEFORE_AFTER_TRACE_MANIFEST.json"), path.join(output, "GUEGOM_NAMED_BEFORE_AFTER_TRACE_MANIFEST.json"));
        for (const chunk of namedTraceManifest.chunks) fs.copyFileSync(path.join(guegomNamedRoot, chunk.name), path.join(output, chunk.name));
      }
    } else {
      await writeGzipRowsFile(path.join(output, `${baselinePrefix}_BASELINE_FULL_DECISION_TRACE_30_GAMES.jsonl.gz`), baselineCompactTrace);
      await writeGzipRowsFile(path.join(output, `${candidatePrefix}_FULL_DECISION_TRACE_30_GAMES.jsonl.gz`), candidateCompactTrace);
    }
    if (isV52c || isV52d || isV52e) {
      await writeGzipRowsFile(path.join(output, "PER_LEG_BLOCK_REASON_HISTOGRAM.jsonl.gz"), blockReasonHistogram.per_leg);
      const marTrace = candidateCompactTrace.filter((row) => row.event_id.includes("ARSMAR") && row.leg_identity.endsWith("|MAR"));
      ensure(marTrace.length > 0, "ARSMAR MAR-side trace is empty");
      await writeGzipRowsFile(path.join(output, "ARSMAR_MAR_GATE_TRACE.jsonl.gz"), marTrace);
    }
    if (isV52d) {
      await writeGzipRowsFile(path.join(output, "DISAGREEMENT_ADJUDICATION_LEDGER.jsonl.gz"), candidateAdjudicationRows);
      await writeGzipRowsFile(path.join(output, "ARSMAR_DISAGREEMENT_ADJUDICATION_TRACE.jsonl.gz"), candidateCompactTrace.filter((row) => row.event_id.includes("ARSMAR") && (row.coherence?.disagreement_adjudication?.firing || row.blocked_clause === "FIRING_DISAGREEMENT_ACTIVE")));
    }
    if (isV52e) {
      await writeGzipRowsFile(path.join(output, "PALANTIR_CONSUMPTION_LEDGER.jsonl.gz"), candidateCompactTrace.map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, palantir: row.palantir, gate_verdict: row.gate_verdict, blocked_clause: row.blocked_clause, final_action: row.final_action, final_target_cents: row.final_target_cents })));
      await writeGzipRowsFile(path.join(output, "N4_PRIOR_INFORMED_RESCUE_LEDGER.jsonl.gz"), n4RescueRows);
      await writeGzipRowsFile(path.join(output, "N5_PRIOR_TIE_ADJUDICATION_LEDGER.jsonl.gz"), n5PriorResolvedRows);
    }
    if (isV52f || isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) {
      await writeGzipRowsFile(path.join(output, `${baselinePrefix}_${candidatePrefix}_FOUR_STATE_EVENT_LEDGER_30.jsonl.gz`), reportedBaselineFourStateRows.map((row) => ({ variant: baselinePrefix, ...row })).concat(reportedCandidateFourStateRows.map((row) => ({ variant: candidatePrefix, ...row }))));
      if (isV52f) await writeGzipRowsFile(path.join(output, "PAIR_ENTRY_CONSERVATION_LICENSE_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.pair_entry_conservation?.reached || row.final_target_cents !== null).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, final_action: row.final_action, final_target_cents: row.final_target_cents, pair_entry_conservation: row.pair_entry_conservation, level: row.level })));
      if (isV52g || isV52h || isV52DepthValidation || isV52CausalOnset) {
        await writeGzipRowsFile(path.join(output, "JOINT_TARGET_CONSERVATION_LICENSE_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.joint_target_conservation?.reached || row.final_target_cents !== null).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, final_action: row.final_action, final_target_cents: row.final_target_cents, joint_target_conservation: row.joint_target_conservation, level: row.level })));
        await writeGzipRowsFile(path.join(output, "PAIR_BUDGET_RECORDS.jsonl.gz"), pairBudgetRecords);
        await writeGzipRowsFile(path.join(output, "PAIR_JOINT_TARGET_TIME_SERIES.jsonl.gz"), pairBudgetRecords.flatMap((record) => record.revisions.map((revision) => ({ event_id: record.event_id, born_at: record.born_at, ...revision }))));
      }
      if (isV52h) await writeGzipRowsFile(path.join(output, "MARKET_PROOF_PRECONDITION_REMOVAL_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.clause_4_market_proof_precondition).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, gate_verdict: row.gate_verdict, blocked_clause: row.blocked_clause, coherence: row.coherence, clause_4_market_proof_precondition: row.clause_4_market_proof_precondition, final_action: row.final_action, final_target_cents: row.final_target_cents })));
      if (isV52i) {
        await writeGzipRowsFile(path.join(output, "DEPTH_PRIOR_CONSUMPTION_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.palantir?.N4?.depth_candidates_under_validation).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, depth_candidates_under_validation: row.palantir.N4.depth_candidates_under_validation, depth_informed_level_selection: row.depth_informed_level_selection, final_action: row.final_action, final_target_cents: row.final_target_cents })));
        await writeGzipRowsFile(path.join(output, "ENTRY_LATER_FLOOR_LEDGER.jsonl.gz"), baselineEntryFloorRows.concat(candidateEntryFloorRows));
      }
      if (isV52j) {
        await writeGzipRowsFile(path.join(output, "ROLE_CONDITIONED_LEVEL_SELECTION_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.role_conditioned_level_selection).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, role_conditioned_level_selection: row.role_conditioned_level_selection, final_action: row.final_action, final_target_cents: row.final_target_cents })));
        await writeGzipRowsFile(path.join(output, "DEPTH_PRIOR_CONSUMPTION_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.palantir?.N4?.depth_candidates_under_validation).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, depth_candidates_under_validation: row.palantir.N4.depth_candidates_under_validation, role_conditioned_level_selection: row.role_conditioned_level_selection, final_action: row.final_action, final_target_cents: row.final_target_cents })));
        await writeGzipRowsFile(path.join(output, "ENTRY_LATER_FLOOR_LEDGER.jsonl.gz"), baselineEntryFloorRows.concat(candidateEntryFloorRows));
      }
      if (isV52k) {
        await writeGzipRowsFile(path.join(output, "LIBRARY_BACKED_LEVEL_EVIDENCE_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.library_backed_level_evidence).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, library_backed_level_evidence: row.library_backed_level_evidence, final_action: row.final_action, final_target_cents: row.final_target_cents })));
        await writeGzipRowsFile(path.join(output, "LIBRARY_PRIOR_CONSUMPTION_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.palantir?.N4?.library_level_evidence_under_validation).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, library_level_evidence_under_validation: row.palantir.N4.library_level_evidence_under_validation, library_backed_level_evidence: row.library_backed_level_evidence, final_action: row.final_action, final_target_cents: row.final_target_cents })));
        await writeGzipRowsFile(path.join(output, "ENTRY_LATER_FLOOR_LEDGER.jsonl.gz"), baselineEntryFloorRows.concat(candidateEntryFloorRows));
      }
      if (isV52MacroRecognition && !isV52o && !isV52Ripeness && !isV52r) {
        await writeGzipRowsFile(path.join(output, "MACRO_RECOGNITION_CONSUMPTION_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.macro_recognition).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, category: row.category, price_region: row.price_region, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, macro_recognition: row.macro_recognition, per_shape_floor_depth: row.per_shape_floor_depth, final_action: row.final_action, final_target_cents: row.final_target_cents })));
        await writeGzipRowsFile(path.join(output, "DOWN_FAMILY_FILL_FLOOR_LEDGER.jsonl.gz"), macroRecognitionSummary.down_family_fills.rows);
      }
      if (isV52o || isV52Ripeness || isV52r) {
        await writeGzipRowsFile(path.join(output, isV52r ? "TRD5_ROLE_BINDING_LEDGER.jsonl.gz" : "BENCHMARKED_ROLE_CONSUMPTION_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.macro_recognition).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, category: row.category, price_region: row.price_region, timestamp_epoch: row.timestamp_epoch, t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds, receipt: row.receipt, ...row.macro_recognition, benchmarked_role_instrument: row.benchmarked_role_instrument, assembled_policy: row.assembled_policy, final_action: row.final_action, final_target_cents: row.final_target_cents })));
        await writeGzipRowsFile(path.join(output, "ROLE_DOWN_FILL_FLOOR_LEDGER.jsonl.gz"), benchmarkRoleSummary.ROLE_DOWN_fills.rows);
        if (isV52Ripeness) await writeGzipRowsFile(path.join(output, "RIPENESS_ROLE_BINDING_LEDGER.jsonl.gz"), ripenessRoleSummary.terminal_rows.concat(ripenessRoleSummary.divergence_rows.map((row) => ({ ...row, row_class: "VERIFIED_VS_SCHEDULED_BINDING_DIVERGENCE" }))));
        if (isV52q) await writeGzipRowsFile(path.join(output, "ANCHOR_CORRECTION_CONSUMPTION_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.macro_recognition?.anchor_correction).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, category: row.category, price_region: row.price_region, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, anchor_correction: row.macro_recognition.anchor_correction, drift_cents: row.macro_recognition.drift_cents, candidate_role: row.macro_recognition.candidate_role, bound_role: row.macro_recognition.bound_role, ripeness: row.macro_recognition.ripeness, final_action: row.final_action, final_target_cents: row.final_target_cents })));
        if (isV52r) {
          await writeGzipRowsFile(path.join(output, "DOWN_LOW1_TARGET_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.assembled_policy).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, category: row.category, price_region: row.price_region, timestamp_epoch: row.timestamp_epoch, t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds, receipt: row.receipt, assembled_policy: row.assembled_policy, final_action: row.final_action, final_target_cents: row.final_target_cents })));
          await writeGzipRowsFile(path.join(output, "ANCHOR_CORRECTION_CONSUMPTION_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.macro_recognition?.anchor_correction).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, category: row.category, price_region: row.price_region, timestamp_epoch: row.timestamp_epoch, t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds, receipt: row.receipt, anchor_correction: row.macro_recognition.anchor_correction, drift_cents: row.macro_recognition.drift_cents, candidate_role: row.macro_recognition.candidate_role, bound_role: row.macro_recognition.bound_role, trd5: row.macro_recognition.trd5, final_action: row.final_action, final_target_cents: row.final_target_cents })));
        }
      }
    }
    const namesBeforeDeterminism = fs.readdirSync(output).sort();
    let determinism;
    if (compare) {
      const mismatches = namesBeforeDeterminism.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
      const extra = fs.readdirSync(compare).filter((name) => ![...namesBeforeDeterminism, "DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name));
      ensure(!mismatches.length && !extra.length, `${candidatePrefix} determinism mismatch: ${[...mismatches, ...extra].join(",")}`);
      determinism = { clean_builds: 2, compared_files: namesBeforeDeterminism.length, byte_identical: true, mismatches: [] };
    } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
    write("DETERMINISM_RECEIPT.json", canonical(determinism));
    writeManifest(output);
    if (compare) {
      fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism));
      writeManifest(compare);
      ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), `${candidatePrefix} final manifests differ`);
    }
    process.stdout.write(canonical({ output, cohort: { events: 30, seed_sha256: activeReadCohort.seed_sha256 }, assertions: v52bAssertions, named_observations: namedChecks, outcome_observations: observationScore, differential: { changed_decision_receipts: decisionDiffs.length, changed_leg_streams: streamDiffs.length }, block_reason_histogram: blockReasonHistogram.aggregate, determinism }));
    return;
  }
  if (isV52eExam) {
    const run = machineRuns.get("V52E_DISPOSITION_804");
    ensure(run.marketEvents.length === 804 && run.strictEvents.length === 804, "V52e disposition population is not 804");
    ensure(examSpanCloseRows.length === 1608 && examSpanCloseRows.every((row) => ["FULL_AVAILABLE_SPAN_CONSUMED", "NO_MATERIALIZED_RECEIPT_INSIDE_EDGE"].includes(row.materialized_span_status)), "corrected full-span export failed");
    const market = score(run.marketEvents), strict = score(run.strictEvents);
    ensure(market.D === 804 && market.legs === 1608 && strict.D === 804 && strict.legs === 1608, "V52e score conservation failed");
    const overParCompleted = run.marketEvents.filter((event) => event.completed_pair && !event.pair_under_par);
    ensure(overParCompleted.length === 0, `three-state law has ${overParCompleted.length} completed non-delta games`);

    const dominantBlock = (leg) => Object.entries(leg.judgment_gate_blocks ?? {}).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0]?.[0] ?? "NO_GATE_BLOCK_RECORDED";
    const missingReason = (leg) => `${leg.terminal_reason ?? "NO_TERMINAL_REASON"}|${dominantBlock(leg)}`;
    const stateRows = run.marketEvents.map((event) => {
      const legs = Object.values(event.legs), credited = legs.filter((leg) => leg.credited), missing = legs.filter((leg) => !leg.credited);
      const state = credited.length === 2 ? "COMPLETE_AT_DELTA" : credited.length === 1 ? "PARTIAL_FOR_REASON" : "NEITHER_FOR_REASON";
      return { event_id: event.event_id, category: event.category, price_region: event.starting_price_split, bell_confidence: event.bell_confidence, state, combined_entry_cents: event.combined_entry_cents, credited_legs: credited.map((leg) => leg.leg_identity).sort(), missing: missing.map((leg) => ({ leg_identity: leg.leg_identity, terminal_reason: leg.terminal_reason, dominant_block_reason: dominantBlock(leg), reason: missingReason(leg) })).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)) };
    });
    const stateCensus = {
      D: 804,
      states: countBy(stateRows, (row) => row.state),
      named_reasons: countBy(stateRows.flatMap((row) => row.missing.map((leg) => `${row.state}|${leg.reason}`)), (row) => row),
      by_category_x_price_region: countBy(stateRows, (row) => `${row.category}|${row.price_region}|${row.state}`),
      conservation: { rows: stateRows.length, state_sum: Object.values(countBy(stateRows, (row) => row.state)).reduce((a, b) => a + b, 0), only_three_states: stateRows.every((row) => ["COMPLETE_AT_DELTA", "PARTIAL_FOR_REASON", "NEITHER_FOR_REASON"].includes(row.state)), pass: stateRows.length === 804 },
    };

    const partitionScores = (events, dimensions) => {
      const groups = new Map();
      for (const event of events) {
        const key = dimensions.map((name) => event[name]).join("|");
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(event);
      }
      return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, rows]) => {
        const value = score(rows);
        return { cell, denominator: rows.length, acted_legs: value.acted_legs, credited_legs: value.credited_legs, completed_pairs: value.completed_pairs, under_par_pairs: value.under_par_pairs, locked_cents_per_contract: value.locked_cents_per_contract, frontier: value.frontier };
      });
    };
    const twoRulers = {
      CANON_MARKET_GRADE: { ...market, role: "PRIMARY_MARKET_RULER_TRADES_AS_TRUTH", category_x_price_region: partitionScores(run.marketEvents, ["category", "starting_price_split"]) },
      STRICT_PRINT_CROSS: { ...strict, role: "BUILD_VERIFICATION_ONLY", category_x_price_region: partitionScores(run.strictEvents, ["category", "starting_price_split"]) },
    };

    const offerPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/POST_ONSET_OFFER_CENSUS.json";
    const offerBytes = gitShow(OFFER_DENOMINATOR_COMMIT, offerPath), offer = JSON.parse(offerBytes);
    ensure(offer.conservation.games === 804 && offer.rows.length === 804, "offer denominator D changed");
    ensure(offer.conservation.counts.OFFERED_POST_ONSET === 612 && offer.margin_distribution.ge10 === 90 && offer.margin_distribution.ge5 === 236 && offer.margin_distribution.ge3 === 384 && offer.margin_distribution.n - offer.margin_distribution.ge3 === 228, "offer margin ladder changed");
    const eventForCode = (code) => {
      const rows = run.marketEvents.filter((event) => event.event_id.includes(code));
      ensure(rows.length === 1, `offer code ${code} bound to ${rows.length} events`);
      return rows[0];
    };
    const strictByEvent = new Map(run.strictEvents.map((event) => [event.event_id, event]));
    const offerRows = offer.rows.map((row) => {
      const event = eventForCode(row.code), strictEvent = strictByEvent.get(event.event_id);
      return { code: row.code, event_id: event.event_id, category: row.cat, price_region: event.starting_price_split, offer_class: row.cls, offer_margin_cents: row.margin, pair_post_onset_floor_cents: row.pair_floor_sel, market_complete_at_delta: event.completed_pair && event.pair_under_par, market_combined_entry_cents: event.combined_entry_cents, strict_complete_at_delta: strictEvent.completed_pair && strictEvent.pair_under_par, strict_combined_entry_cents: strictEvent.combined_entry_cents, legs: row.legs };
    });
    const captureSummary = (rows, field) => ({ denominator: rows.length, captured: rows.filter((row) => row[field]).length, rate: rows.length ? rows.filter((row) => row[field]).length / rows.length : null });
    const offeredRows = offerRows.filter((row) => row.offer_class === "OFFERED_POST_ONSET");
    const ladder = [
      ["GE_10_CENTS", (row) => row.offer_margin_cents >= 10],
      ["GE_5_CENTS", (row) => row.offer_margin_cents >= 5],
      ["GE_3_CENTS", (row) => row.offer_margin_cents >= 3],
      ["THIN_1_TO_2_CENTS", (row) => row.offer_margin_cents >= 1 && row.offer_margin_cents <= 2],
      ["ALL_OFFERED_POST_ONSET", () => true],
    ];
    const offerCapture = {
      source: { commit: OFFER_DENOMINATOR_COMMIT, path: offerPath, sha256: shaBytes(offerBytes) },
      fixed_denominator: { D: 804, OFFERED_POST_ONSET: 612, margin_ladder: { GE_10_CENTS: 90, GE_5_CENTS: 236, GE_3_CENTS: 384, THIN_1_TO_2_CENTS: 228 }, other_classes: offer.conservation.counts },
      market_ladder: Object.fromEntries(ladder.map(([name, predicate]) => [name, captureSummary(offeredRows.filter(predicate), "market_complete_at_delta")])),
      strict_ladder: Object.fromEntries(ladder.map(([name, predicate]) => [name, captureSummary(offeredRows.filter(predicate), "strict_complete_at_delta")])),
      classes_market: Object.fromEntries([...new Set(offerRows.map((row) => row.offer_class))].sort().map((cls) => [cls, captureSummary(offerRows.filter((row) => row.offer_class === cls), "market_complete_at_delta")])) ,
      classes_strict: Object.fromEntries([...new Set(offerRows.map((row) => row.offer_class))].sort().map((cls) => [cls, captureSummary(offerRows.filter((row) => row.offer_class === cls), "strict_complete_at_delta")])) ,
      by_category_x_price_region: [...new Set(offerRows.map((row) => `${row.category}|${row.price_region}`))].sort().map((cell) => { const rows = offerRows.filter((row) => `${row.category}|${row.price_region}` === cell); return { cell, denominator: rows.length, offer_classes: countBy(rows, (row) => row.offer_class), market: captureSummary(rows, "market_complete_at_delta"), strict: captureSummary(rows, "strict_complete_at_delta") }; }),
      formation_only_and_not_offered_never_folded: true,
    };

    const offerLegByTicker = new Map(offer.rows.flatMap((row) => Object.values(row.legs).map((leg) => [leg.ticker, { code: row.code, category: row.cat, offer_class: row.cls, pair_margin_cents: row.margin, floor_cents: leg.floor_sel, onset_timestamp_epoch: leg.onset_sel }])));
    ensure(offerLegByTicker.size === 1608, "offer leg floor conservation failed");
    const regretRows = run.marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => {
      const source = offerLegByTicker.get(leg.ticker); ensure(source, `missing offer floor ${leg.ticker}`);
      return { event_id: event.event_id, leg_identity: leg.leg_identity, ticker: leg.ticker, category: event.category, price_region: leg.price_region, offer_class: source.offer_class, post_onset_floor_cents: source.floor_cents, onset_timestamp_epoch: source.onset_timestamp_epoch, credited: leg.credited, entry_cents: leg.entry_cents, regret_cents: leg.credited && Number.isInteger(source.floor_cents) ? leg.entry_cents - source.floor_cents : null, uncredited_opportunity: !leg.credited && Number.isInteger(source.floor_cents), terminal_reason: leg.terminal_reason, dominant_block_reason: dominantBlock(leg) };
    }));
    const regretSummary = (rows) => { const credited = rows.filter((row) => Number.isInteger(row.regret_cents)); return { legs: rows.length, floor_available: rows.filter((row) => Number.isInteger(row.post_onset_floor_cents)).length, credited_with_floor: credited.length, uncredited_with_floor: rows.filter((row) => row.uncredited_opportunity).length, regret_cents: distribution(credited.map((row) => row.regret_cents)), no_fabricated_incomplete_penalty: true }; };
    const regretGauge = {
      ruler: "ENTRY_MINUS_OFFER_CENSUS_PER_LEG_POST_ONSET_FLOOR",
      aggregate: regretSummary(regretRows),
      by_category_x_price_region: [...new Set(regretRows.map((row) => `${row.category}|${row.price_region}`))].sort().map((cell) => ({ cell, ...regretSummary(regretRows.filter((row) => `${row.category}|${row.price_region}` === cell)) })),
      by_offer_class: Object.fromEntries([...new Set(regretRows.map((row) => row.offer_class))].sort().map((cls) => [cls, regretSummary(regretRows.filter((row) => row.offer_class === cls))])),
    };

    const restKinds = new Set(["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE", "GAP_CREDIT_REPRICE_DOWN"]);
    const restMutations = run.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && restKinds.has(row.kind));
    const firstPostByLeg = new Map();
    for (const row of restMutations.filter((row) => row.kind === "PLACE_REST")) {
      const prior = firstPostByLeg.get(row.leg_identity);
      if (!prior || row.timestamp_epoch < prior.timestamp_epoch || (row.timestamp_epoch === prior.timestamp_epoch && row.receipt.localeCompare(prior.receipt) < 0)) firstPostByLeg.set(row.leg_identity, row);
    }
    const firstPosts = [...firstPostByLeg.values()];
    const reflexRows = restMutations.filter((row) => !row.birth_license?.read?.passed);
    ensure(reflexRows.length === 0, `REFLEX_POST=${reflexRows.length}`);
    const posting = {
      first_placements: firstPosts.length,
      rest_mutations: restMutations.length,
      REFLEX_POST: reflexRows.length,
      first_post_seconds_after_window_open: distribution(firstPosts.map((row) => row.timestamp_epoch - baseByEvent.get(row.event_id).left)),
      first_post_t_minus_scheduled_seconds: distribution(firstPosts.map((row) => row.t_minus_scheduled_seconds)),
      first_post_t_minus_actual_bell_seconds: distribution(firstPosts.map((row) => row.t_minus_actual_bell_seconds)),
      read_at_first_post: countBy(firstPosts, (row) => `${row.birth_license?.read?.state ?? "READ_ABSENT"}|${row.birth_license?.read?.evidence ?? "NO_EVIDENCE_CLASS"}`),
      onset_candidate_at_first_post: countBy(firstPosts, (row) => row.birth_license?.onset?.selected_candidate ?? "NO_ONSET"),
      by_category: Object.fromEntries([...new Set(firstPosts.map((row) => baseByEvent.get(row.event_id).category))].sort().map((cat) => [cat, { first_placements: firstPosts.filter((row) => baseByEvent.get(row.event_id).category === cat).length, seconds_after_open: distribution(firstPosts.filter((row) => baseByEvent.get(row.event_id).category === cat).map((row) => row.timestamp_epoch - baseByEvent.get(row.event_id).left)) }])),
    };

    const palantirSummary = { ...examTraceStats, provenance_asset_ids: [...examTraceStats.provenance_asset_ids].sort(), trace_dictionary_entries: examTraceNormalizer.entries().length, clean_store_boot_assertion: n9Binding.store.boot_assertion, all_decision_rows_consumed_N2_N4_N5: examTraceStats.rows > 0 && [examTraceStats.N2_rows, examTraceStats.N4_rows, examTraceStats.N5_rows, examTraceStats.palantir_consumption_rows, examTraceStats.continuous_rows].every((value) => value === examTraceStats.rows), priors_never_gate: examTraceStats.priors_gate_true_rows === 0 };
    ensure(palantirSummary.clean_store_boot_assertion.passed && palantirSummary.all_decision_rows_consumed_N2_N4_N5 && palantirSummary.priors_never_gate, "Palantir scale assertion failed");

    const namedRows = {};
    for (const label of ["ARSMAR", "SANDAN", "PUTJEA", "POLKUH", "MERDRO"]) {
      const event = run.marketEvents.find((row) => row.event_id.includes(label)); ensure(event, `named event missing ${label}`);
      namedRows[label] = { event_id: event.event_id, completed: event.completed_pair, combined_entry_cents: event.combined_entry_cents, under_par: event.pair_under_par, legs: Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, final_state: leg.final_state, terminal_reason: leg.terminal_reason, gate_blocks: leg.judgment_gate_blocks }])) };
    }
    const namedChecks = { role: "CURRENT_BINDINGS_REPORTED_NOT_TUNED", ARSMAR: namedRows.ARSMAR, SANDAN: namedRows.SANDAN, PUTJEA: namedRows.PUTJEA, POLKUH: namedRows.POLKUH, MERDRO: namedRows.MERDRO };

    const lineageArtifact = (commit, packagePath) => JSON.parse(gitShow(commit, packagePath));
    const v52Score = lineageArtifact(V52_COMMIT, ".claude/window1_live_v4_replay/v52_judgment_gate_20260812/MARKET_GRADE_SCORECARD.json");
    const v52bObs = lineageArtifact(V52B_COMMIT, ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812/OUTCOME_OBSERVATIONS_30.json");
    const v52cObs = lineageArtifact(V52C_COMMIT, ".claude/window1_live_v4_replay/v52c_full_post_onset_read_20260812/OUTCOME_OBSERVATIONS_30.json");
    const v52dObs = lineageArtifact(V52D_COMMIT, ".claude/window1_live_v4_replay/v52d_disagreement_referee_20260812/OUTCOME_OBSERVATIONS_30.json");
    const v52eObs = lineageArtifact(V52E_COMMIT, ".claude/window1_live_v4_replay/v52e_palantir_wiring_20260812/OUTCOME_OBSERVATIONS_30.json");
    ensure(v52Score.score.completed_pairs === 176, "honest V52 lineage start changed");
    const lineage = { warning: "V52_IS_FULL_804; V52B_TO_V52E_PRIOR_ROWS_ARE_DISTINCT_30_GAME_OBSERVATION_COHORTS_AND_NOT_A_SINGLE_SCORE_SERIES", rows: [
      { version: "V52", commit: V52_COMMIT, scope: "DEV_804_DISPOSITION", completed_pairs: v52Score.score.completed_pairs },
      { version: "V52B", commit: V52B_COMMIT, scope: "PINS_PLUS_FRESH25_OBSERVATION", completed_pairs: v52bObs.candidate.completed_pairs },
      { version: "V52C", commit: V52C_COMMIT, scope: "PINS_PLUS_FRESH25_OBSERVATION", completed_pairs: v52cObs.candidate.completed_pairs },
      { version: "V52D", commit: V52D_COMMIT, scope: "PINS_PLUS_FRESH25_OBSERVATION", completed_pairs: v52dObs.candidate.completed_pairs },
      { version: "V52E", commit: V52E_COMMIT, scope: "PINS_PLUS_FRESH25_OBSERVATION", completed_pairs: v52eObs.candidate.completed_pairs },
      { version: "V52E", commit: "THIS_PACKAGE", scope: "DEV_804_DISPOSITION_EXAM", completed_pairs: market.completed_pairs },
    ] };

    const policyReceiptPath = ".claude/window1_live_v4_replay/v52e_trace_span_provenance_audit_20260813/POLICY_BYTE_IDENTITY.json";
    const priorPolicyReceiptBytes = gitShow(V52E_SPAN_AUDIT_COMMIT, policyReceiptPath), priorPolicyReceipt = JSON.parse(priorPolicyReceiptBytes);
    const policyIdentity = { frozen_policy_commit: V52E_COMMIT, reattestation_commit: V52E_SPAN_AUDIT_COMMIT, reattestation_path: policyReceiptPath, reattestation_sha256: shaBytes(priorPolicyReceiptBytes), files: {} };
    for (const [relativePath, prior] of Object.entries(priorPolicyReceipt.files)) {
      const current = fileHash(path.join(repo, relativePath)), frozen = shaBytes(gitShow(V52E_COMMIT, relativePath));
      policyIdentity.files[relativePath] = { frozen_sha256: frozen, prior_reattest_sha256: prior.after_sha256, current_sha256: current, byte_identical: frozen === current && current === prior.after_sha256 };
    }
    policyIdentity.all_byte_identical = Object.values(policyIdentity.files).every((row) => row.byte_identical);
    ensure(policyIdentity.all_byte_identical, "V52e policy byte identity failed");

    const traceDictionary = examTraceNormalizer.entries();
    await writeGzipRowsFile(path.join(output, "V52E_TRACE_DICTIONARY.jsonl.gz"), traceDictionary);
    await writeGzipRowsFile(path.join(output, "V52E_CORRECTED_DECISION_SPAN_CLOSE_1608.jsonl.gz"), examSpanCloseRows.sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)));
    await writeGzipRowsFile(path.join(output, "THREE_STATE_EVENT_LEDGER_804.jsonl.gz"), stateRows.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "POST_ONSET_OFFER_CAPTURE_LEDGER_804.jsonl.gz"), offerRows.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "REGRET_LEDGER_1608.jsonl.gz"), regretRows.sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)));
    await writeGzipRowsFile(path.join(output, "FIRST_POST_LEDGER.jsonl.gz"), firstPosts.sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)));
    await writeGzipRowsFile(path.join(output, "MARKET_EVENT_LEDGER_804.jsonl.gz"), run.marketEvents.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "STRICT_EVENT_LEDGER_804.jsonl.gz"), run.strictEvents.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    write("TRACE_CHUNK_MANIFEST.json", canonical({ format: "RECEIPT_GRAIN_DECISION_DIARY_V1_JSONL_GZIP", reconstruction: "Map each row array through V52E_TRACE_DICTIONARY.fields; source receipts plus frozen policy reconstruct deliberately de-duplicated nested evidence objects", chunks: examTraceChunks, rows: examTraceChunks.reduce((sum, row) => sum + row.row_count, 0), events: examTraceChunks.reduce((sum, row) => sum + row.event_count, 0), schema_rows: traceDictionary.length, every_decision_receipt_retained: true, duplicated_nested_evidence_objects_not_repeated: true }));
    write("POLICY_BYTE_IDENTITY.json", canonical(policyIdentity));
    write("TWO_RULER_SCORECARD.json", canonical(twoRulers));
    write("THREE_STATE_CENSUS.json", canonical(stateCensus));
    write("FRONTIER.json", canonical({ market: twoRulers.CANON_MARKET_GRADE.frontier, strict: twoRulers.STRICT_PRINT_CROSS.frontier, denominator: 804, per_category_x_price_region: { market: twoRulers.CANON_MARKET_GRADE.category_x_price_region, strict: twoRulers.STRICT_PRINT_CROSS.category_x_price_region } }));
    write("REGRET_GAUGE.json", canonical(regretGauge));
    write("POSTING_TIME_AND_READ_AT_POST.json", canonical(posting));
    write("PALANTIR_CONSUMPTION_SCALE_RECEIPT.json", canonical(palantirSummary));
    write("CLEAN_STORE_BOOT_ASSERTION.json", canonical(n9Binding.store.boot_assertion));
    write("NAMED_CHECKS.json", canonical(namedChecks));
    write("PER_BLOCK_REASON_ROLLUP.json", canonical({ decision_receipts: { aggregate: examTraceStats.by_block_reason, by_category: examTraceStats.by_category_x_block_reason }, terminal_missing_legs: countBy(stateRows.flatMap((row) => row.missing), (row) => row.reason) }));
    write("OFFER_DENOMINATOR_CAPTURE.json", canonical(offerCapture));
    write("LINEAGE_RECEIPT.json", canonical(lineage));
    write("CONTROL_BINDING.json", canonical({ variant: "V52E_DISPOSITION_804", frozen_policy_commit: V52E_COMMIT, exact_parent: V52E_SPAN_AUDIT_COMMIT, scope: "DEV_804_ONLY", stage: "ONE_FULL_804_EXAM", policy_edits: false, mechanical_adapter_only: true, sealed_access: false, deployment: false, live: false }));
    write("SOURCE_HASH_MANIFEST.json", canonical({ sources: { policy_files: policyIdentity.files, offer_denominator: offerCapture.source, prints: printLoad.receipt, stability_spans: { path: `${V36_PACKAGE}/WINDOW1_SPAN_804.json`, sha256: fileHash(path.join(v36Package, "WINDOW1_SPAN_804.json")) }, clean_store_manifest: { commit: n9Binding.store.manifest_commit, sha256: n9Binding.store.manifest_sha256 }, tape_files: tapeHashes } }));
    write("FORBIDDEN_ACCESS_RECEIPT.json", canonical({ sealed: false, holdout: false, deployment: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, policy_edits: false }));
    const report = `# V52e disposition - full dev-804 exam\n\nFrozen V52e policy ${V52E_COMMIT} ran once over the complete development population with the corrected ${V52E_SPAN_AUDIT_COMMIT} span-close export convention. Policy byte identity: PASS.\n\n- CANON market ruler: completed/under-par ${market.completed_pairs}/${market.under_par_pairs}; frontier <=93/<=95/<=97/<100/any ${market.frontier.LE_93}/${market.frontier.LE_95}/${market.frontier.LE_97}/${market.frontier.LT_100}/${market.frontier.ANY_PRICE}.\n- Strict build-verification ruler: completed/under-par ${strict.completed_pairs}/${strict.under_par_pairs}; frontier ${strict.frontier.LE_93}/${strict.frontier.LE_95}/${strict.frontier.LE_97}/${strict.frontier.LT_100}/${strict.frontier.ANY_PRICE}.\n- Three-state census: ${JSON.stringify(stateCensus.states)}.\n- Offered-post-onset capture: ${offerCapture.market_ladder.ALL_OFFERED_POST_ONSET.captured}/612; margin ladder >=10 ${offerCapture.market_ladder.GE_10_CENTS.captured}/90, >=5 ${offerCapture.market_ladder.GE_5_CENTS.captured}/236, >=3 ${offerCapture.market_ladder.GE_3_CENTS.captured}/384, thin1-2 ${offerCapture.market_ladder.THIN_1_TO_2_CENTS.captured}/228. Formation-only and not-offered classes remain separate.\n- REFLEX_POST: ${posting.REFLEX_POST}. Palantir CLEAN boot: ${n9Binding.store.boot_assertion.passed ? "PASS" : "FAIL"}; continuous N2/N4/N5 receipts ${examTraceStats.palantir_consumption_rows}/${examTraceStats.rows}; priors gated ${examTraceStats.priors_gate_true_rows}.\n- Full decision stream: ${examTraceChunks.length} receipt-grain diary chunks, ${examTraceStats.rows} decision rows, 804 games; corrected span-close rows ${examSpanCloseRows.length}. Every receipt retains clocks, observation, read, coherence, target, verdict, action, and Palantir-use fields; source receipts and the frozen policy reconstruct nested evidence trees without serializing the same tree repeatedly.\n- No sealed, holdout, deployment, live, network, order, position, exit, or settlement access.\n`;
    write("REPORT.md", report);

    const namesBeforeDeterminism = fs.readdirSync(output).sort();
    let determinism;
    if (compare) {
      const mismatches = namesBeforeDeterminism.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
      const extra = fs.readdirSync(compare).filter((name) => ![...namesBeforeDeterminism, "DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name));
      ensure(!mismatches.length && !extra.length, `V52e disposition determinism mismatch: ${[...mismatches, ...extra].join(",")}`);
      determinism = { clean_builds: 2, compared_files: namesBeforeDeterminism.length, byte_identical: true, mismatches: [] };
    } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
    write("DETERMINISM_RECEIPT.json", canonical(determinism));
    writeManifest(output);
    if (compare) {
      fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism));
      writeManifest(compare);
      ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "V52e disposition final manifests differ");
    }
    process.stdout.write(canonical({ output, market, strict, states: stateCensus.states, offer_capture: offerCapture.market_ladder, REFLEX_POST: posting.REFLEX_POST, trace_rows: examTraceStats.rows, trace_chunks: examTraceChunks.length, determinism }));
    return;
  }
  if (isV52sExam) {
    const candidateRun = machineRuns.get("V52S_JOINT_BUDGET_YIELD_PRIORITY_DEPTH");
    const baselineRun = machineRuns.get("V52L_FROZEN_BASELINE");
    ensure(candidateRun?.marketEvents.length === 804 && candidateRun?.strictEvents.length === 804, "V52s candidate event conservation failed");
    ensure(baselineRun?.marketEvents.length === 804, "V52s V52l baseline event conservation failed");
    const built = v52sExamAdapter.buildArtifacts({
      repo,
      candidateRun,
      baselineRun,
      groundTruth: groundTruthWindowBinding,
      terminalRoles: examRoleStats.terminal_by_leg,
      roleStats: examRoleStats,
      traceStats: examTraceStats,
      traceNormalizer: examTraceNormalizer,
      traceChunks: examTraceChunks,
      spanCloseRows: examSpanCloseRows,
      n9Binding,
      policyIdentity: examPolicyIdentity,
      v52eLaneIdentity: examV52eLaneIdentity,
      sanityFence: { role: "DIRECT_CORPUS_SCALE_MECHANISM_EXAM", reason: "OPEN_LOOP_FAILURE_MODE_REQUIRES_FULL_804", pass: true },
    });
    const traceDictionary = examTraceNormalizer.entries();
    await writeGzipRowsFile(path.join(output, "V52S_TRACE_DICTIONARY.jsonl.gz"), traceDictionary);
    await writeGzipRowsFile(path.join(output, "V52S_CORRECTED_DECISION_SPAN_CLOSE_1608.jsonl.gz"), examSpanCloseRows.sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)));
    await writeGzipRowsFile(path.join(output, "MARKET_EVENT_LEDGER_804.jsonl.gz"), candidateRun.marketEvents.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "STRICT_EVENT_LEDGER_804.jsonl.gz"), candidateRun.strictEvents.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "V52L_MARKET_EVENT_LEDGER_804.jsonl.gz"), baselineRun.marketEvents.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "FOUR_STATE_MARKET_EVENT_LEDGER_804.jsonl.gz"), built.rows.marketRows.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "FOUR_STATE_STRICT_EVENT_LEDGER_804.jsonl.gz"), built.rows.strictRows.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "PER_GAME_OUTCOME_TABLE.jsonl.gz"), built.rows.perGame.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "REGRET_LEDGER_1608.jsonl.gz"), built.rows.regretRows.sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)));
    await writeGzipRowsFile(path.join(output, "OFFER_DENOMINATOR_EVENT_LEDGER_804.jsonl.gz"), built.rows.offerRows.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "FIRST_POST_LEDGER.jsonl.gz"), built.rows.firstPosts.sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)));
    await writeGzipRowsFile(path.join(output, "V52S_DEPTH_LIFT_AND_YIELD_LEDGER.jsonl.gz"), built.depthActions);
    for (const [name, value] of Object.entries(built.artifacts)) write(name, canonical(value));
    write("TRACE_CHUNK_MANIFEST.json", canonical({ format: "V52S_RECEIPT_GRAIN_DECISION_DIARY_V1_JSONL_GZIP", reconstruction: "Map each row array through V52S_TRACE_DICTIONARY.fields; candidate V52s V52l-policy decision receipts retain both clocks; depth-lift/yield actions are in V52S_DEPTH_LIFT_AND_YIELD_LEDGER.json", chunks: examTraceChunks, rows: examTraceChunks.reduce((sum, row) => sum + row.row_count, 0), events: examTraceChunks.reduce((sum, row) => sum + row.event_count, 0), schema_rows: traceDictionary.length, every_candidate_decision_receipt_retained: true }));
    write("SOURCE_HASH_MANIFEST.json", canonical({ sources: { frozen_V52l_policy: examPolicyIdentity, frozen_V52l_baseline_ledger: baselineRun.source, law_index: built.bindings.law_index, rejected_open_loop_simulation: built.bindings.simulation, ground_truth: groundTruthWindowBinding.binding, prints: printLoad.receipt, stability_spans: { path: `${V36_PACKAGE}/WINDOW1_SPAN_804.json`, sha256: fileHash(path.join(v36Package, "WINDOW1_SPAN_804.json")) }, clean_store_manifest: { commit: n9Binding.store.manifest_commit, sha256: n9Binding.store.manifest_sha256 }, tape_files: tapeHashes } }));
    write("ADDITIONS_ONLY_LANE_DIFF_RECEIPT.json", canonical({ exact_parent: v52sExamAdapter.PARENT_COMMIT, existing_policy_files_modified: 0, existing_lane_policy_semantics_modified: false, shared_builder_role: "MINIMAL_V52S804_REGISTRATION_PLUS_RECEIPT_LOCAL_MECHANISM_SEAM_AND_OUTPUT_DISPATCH", modified_registration_files: ["arb-executor/analysis/build_window1_v38_maker_only.js", "arb-executor/analysis/window1_v52r_exam_adapter.js"], additions: ["arb-executor/analysis/window1_v52s_joint_budget_yield_priority.js", "arb-executor/analysis/window1_v52s_exam_adapter.js", "arb-executor/analysis/build_window1_v52s_joint_budget_yield_priority.js", "arb-executor/analysis/finalize_window1_v52s_streaming_package.js", "arb-executor/tests/test_window1_v52s_joint_budget_yield_priority.js", "arb-executor/docs/research/window1/V52S_JOINT_BUDGET_YIELD_PRIORITY_20260819_ADDENDUM.md", ".claude/window1_live_v4_replay/v52s_joint_budget_yield_priority_804_20260819/*"], v52e804_attestation: examV52eLaneIdentity }));
    write("REPORT.md", built.report);

    const namesBeforeDeterminism = fs.readdirSync(output).sort();
    let determinism;
    if (compare) {
      const mismatches = namesBeforeDeterminism.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
      const extra = fs.readdirSync(compare).filter((name) => ![...namesBeforeDeterminism, "DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name));
      ensure(!mismatches.length && !extra.length, `V52s disposition determinism mismatch: ${[...mismatches, ...extra].join(",")}`);
      determinism = { clean_builds: 2, compared_files: namesBeforeDeterminism.length, byte_identical: true, mismatches: [] };
    } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
    write("DETERMINISM_RECEIPT.json", canonical(determinism));
    writeManifest(output);
    if (compare) {
      fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism));
      writeManifest(compare);
      ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "V52s final manifests differ");
    }
    const score = built.artifacts["TWO_RULER_SCORECARD.json"].CANON_MARKET_GRADE;
    process.stdout.write(canonical({ output, states: score.states, completed_pairs: score.completed_pairs, under_par_pairs: score.under_par_pairs, locked_cents: score.locked_cents, knife_edges_preserved: built.artifacts["V52S_KNIFE_EDGE_68_PRESERVATION.json"].preserved, invariant: built.artifacts["V52S_JOINT_BUDGET_INVARIANT_RECEIPT.json"], REFLEX_POST: built.artifacts["POSTING_TIME_AND_READ_AT_POST.json"].REFLEX_POST, mechanism_bar: built.bar, trace_rows: examTraceStats.rows, trace_chunks: examTraceChunks.length, determinism }));
    return;
  }
  if (isV52rExam) {
    const candidateRun = machineRuns.get("V52R_ASSEMBLED_POLICY");
    const baselineRun = machineRuns.get("V52L_FROZEN_BASELINE");
    ensure(candidateRun?.marketEvents.length === 804 && candidateRun?.strictEvents.length === 804, "V52r candidate event conservation failed");
    ensure(baselineRun?.marketEvents.length === 804, "V52l baseline event conservation failed");
    const built = v52rExamAdapter.buildExamArtifacts({
      candidateRun,
      baselineRun,
      groundTruth: groundTruthWindowBinding,
      terminalRoles: examRoleStats.terminal_by_leg,
      roleStats: examRoleStats,
      traceStats: examTraceStats,
      traceNormalizer: examTraceNormalizer,
      traceChunks: examTraceChunks,
      spanCloseRows: examSpanCloseRows,
      n9Binding,
      policyIdentity: examPolicyIdentity,
      v52eLaneIdentity: examV52eLaneIdentity,
      sanityFence: examSanityFence,
    });
    const traceDictionary = examTraceNormalizer.entries();
    await writeGzipRowsFile(path.join(output, "V52R_TRACE_DICTIONARY.jsonl.gz"), traceDictionary);
    await writeGzipRowsFile(path.join(output, "V52R_CORRECTED_DECISION_SPAN_CLOSE_1608.jsonl.gz"), examSpanCloseRows.sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)));
    await writeGzipRowsFile(path.join(output, "MARKET_EVENT_LEDGER_804.jsonl.gz"), candidateRun.marketEvents.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "STRICT_EVENT_LEDGER_804.jsonl.gz"), candidateRun.strictEvents.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "V52L_MARKET_EVENT_LEDGER_804.jsonl.gz"), baselineRun.marketEvents.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "FOUR_STATE_MARKET_EVENT_LEDGER_804.jsonl.gz"), built.rows.marketRows.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "FOUR_STATE_STRICT_EVENT_LEDGER_804.jsonl.gz"), built.rows.strictRows.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "PER_GAME_OUTCOME_TABLE.jsonl.gz"), built.rows.perGame.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "REGRET_LEDGER_1608.jsonl.gz"), built.rows.regretRows.sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)));
    await writeGzipRowsFile(path.join(output, "OFFER_DENOMINATOR_EVENT_LEDGER_804.jsonl.gz"), built.rows.offerRows.sort((a, b) => a.event_id.localeCompare(b.event_id)));
    await writeGzipRowsFile(path.join(output, "FIRST_POST_LEDGER.jsonl.gz"), built.rows.firstPosts.sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)));
    await writeGzipRowsFile(path.join(output, "TERMINAL_ROLE_LEDGER_1608.jsonl.gz"), built.rows.terminalRoles);
    for (const [name, value] of Object.entries(built.artifacts)) write(name, canonical(value));
    write("TRACE_CHUNK_MANIFEST.json", canonical({ format: "V52R_RECEIPT_GRAIN_DECISION_DIARY_V1_JSONL_GZIP", reconstruction: "Map each row array through V52R_TRACE_DICTIONARY.fields; every V52r candidate policy decision receipt is retained with TRD5/LOW-1 evidence and both clocks", chunks: examTraceChunks, rows: examTraceChunks.reduce((sum, row) => sum + row.row_count, 0), events: examTraceChunks.reduce((sum, row) => sum + row.event_count, 0), schema_rows: traceDictionary.length, every_candidate_decision_receipt_retained: true }));
    write("SOURCE_HASH_MANIFEST.json", canonical({ sources: { frozen_policy: examPolicyIdentity, ground_truth: groundTruthWindowBinding.binding, prints: printLoad.receipt, stability_spans: { path: `${V36_PACKAGE}/WINDOW1_SPAN_804.json`, sha256: fileHash(path.join(v36Package, "WINDOW1_SPAN_804.json")) }, clean_store_manifest: { commit: n9Binding.store.manifest_commit, sha256: n9Binding.store.manifest_sha256 }, tape_files: tapeHashes } }));
    write("ADDITIONS_ONLY_ADAPTER_DIFF_RECEIPT.json", canonical({ exact_parent: v52rExamAdapter.FROZEN_V52R_COMMIT, existing_lane_modifications: [{ path: "arb-executor/analysis/build_window1_v38_maker_only.js", role: "MINIMAL_V52R804_REGISTRATION_AND_OUTPUT_DISPATCH_ONLY" }], additions: ["arb-executor/analysis/window1_v52r_exam_adapter.js", "arb-executor/analysis/build_window1_v52r_disposition_804.js", "arb-executor/analysis/check_window1_v52r_exam_sanity.js", "arb-executor/tests/test_window1_v52r_exam_adapter.js", ".claude/window1_live_v4_replay/v52r_disposition_804_20260818/*"], policy_files_modified: 0, v52e804_protected_block_modified: false, v52e804_attestation: examV52eLaneIdentity }));
    write("REPORT.md", built.report);

    const namesBeforeDeterminism = fs.readdirSync(output).sort();
    let determinism;
    if (compare) {
      const mismatches = namesBeforeDeterminism.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
      const extra = fs.readdirSync(compare).filter((name) => ![...namesBeforeDeterminism, "DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name));
      ensure(!mismatches.length && !extra.length, `V52r disposition determinism mismatch: ${[...mismatches, ...extra].join(",")}`);
      determinism = { clean_builds: 2, compared_files: namesBeforeDeterminism.length, byte_identical: true, mismatches: [] };
    } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
    write("DETERMINISM_RECEIPT.json", canonical(determinism));
    writeManifest(output);
    if (compare) {
      fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism));
      writeManifest(compare);
      ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "V52r disposition final manifests differ");
    }
    const score = built.artifacts["TWO_RULER_SCORECARD.json"].CANON_MARKET_GRADE;
    process.stdout.write(canonical({ output, states: score.states, completed_pairs: score.completed_pairs, under_par_pairs: score.under_par_pairs, locked_cents: score.locked_cents, offer_capture: built.artifacts["OFFER_DENOMINATOR_CAPTURE.json"].market, REFLEX_POST: built.artifacts["POSTING_TIME_AND_READ_AT_POST.json"].REFLEX_POST, trace_rows: examTraceStats.rows, trace_chunks: examTraceChunks.length, determinism }));
    return;
  }
  if (isV52 && stage === "stage1") {
    const flow = buildV52FlowPackage(machineRuns.get("V52_JUDGMENT_GATE"), baseByEvent, v52TapePackBytes, v52OnsetReceiptBytes);
    write("STAGE1_FLOW_ASSERTIONS.json", canonical(flow.assertions));
    write("STAGE1_FLOW_OUTCOMES_OBSERVATION_ONLY.json", canonical(flow.outcomes));
    write("STAGE1_DECISION_TRACE.jsonl.gz", gzipRows(flow.trace));
    write("CONTROL_BINDING.json", canonical(flow.control));
    write("FORBIDDEN_ACCESS_RECEIPT.json", canonical({ live: false, holdout: false, network: false, orders: false, positions: false, deployment: false, scoring: false }));
    write("REPORT.md", `# V52 Stage 1 flow check - ${flow.pass ? "PASS" : "BLOCKED"}\n\nFive games only. Assertions: zero pre-onset posts; zero NO_TAPE posts; zero displayed-bid levels; every post carries all four license fields; scavenger OFF. Outcomes are observations and grade nothing.\n`);
    write("CONSTRUCTION_STATUS.json", canonical({ status: flow.pass ? "STAGE1_MECHANICAL_PASS_STAGE2_PERMITTED" : "BLOCKED_BEFORE_STAGE2", behavioral_edits_from_outcomes_permitted: false }));
    writeManifest(output);
    process.stdout.write(canonical({ output, status: flow.pass ? "PASS" : "BLOCKED", post_actions: flow.post_actions, assertions: flow.assertions, outcomes: flow.outcomes }));
    return;
  }
  const primaryRun = machineRuns.get(isV52c ? "V52C_FULL_POST_ONSET_READ" : isV52b ? "V52B_READ_LEVEL_AUTHORITY" : isV52 ? "V52_JUDGMENT_GATE" : isV49b ? "V49B_FAITHFUL_STAND_AT_P" : isV49 ? "V49_EVIDENCED_LEVEL_STANDING" : isV48 ? "TRADE_TRUTH_V47_INCUMBENT" : isV47 ? "V47_SAME_TICK_ARM" : isV46 ? "V46_PAIR_GATED_GAP_CREDIT" : isV45 ? "V45_GUARD_RELEASE_AT_SIBLING_CREDIT" : isV43 ? "V43_ALL_THREE" : "PRIMARY"), marketEvents = primaryRun.marketEvents, strictEvents = primaryRun.strictEvents, allActions = primaryRun.actions;
  const marketScore = score(marketEvents), strictScore = score(strictEvents), marketGrades = gradeAgainstReach(marketEvents, reachByEvent, baseByEvent), strictGrades = gradeAgainstReach(strictEvents, reachByEvent, baseByEvent), v36Score = frozenV36Score(reachRows), v36NetScore = frozenV36NetScore(v36StrictFrozenEvents);
  ensure(v36NetScore.aggregate.taker_legs_charged === 882, "V36 taker-leg fee population changed");
  const v41LedgerPath = ".claude/window1_live_v4_replay/v41_maker_machine_20260808/MARKET_EVENT_LEDGER.jsonl.gz";
  const closeAuditPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/INDEPENDENT_CLOSE_AUDIT_1608.csv";
  const fullBookReceiptPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V41_FULL_BOOK_PNL.json";
  const deepGapCensusPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/CAP_UNFEASIBLE_CENSUS.json";
  const v41FrozenEvents = hasDeepGap ? readRows(path.join(repo, v41LedgerPath)) : null;
  const closeAuditBytes = hasDeepGap ? gitShow(FULL_BOOK_PNL_COMMIT, closeAuditPath) : null;
  const fullBookReceiptBytes = hasDeepGap ? gitShow(FULL_BOOK_PNL_COMMIT, fullBookReceiptPath) : null;
  const deepGapCensusBytes = hasDeepGap ? gitShow(DEEP_GAP_CENSUS_COMMIT, deepGapCensusPath) : null;
  const closeByTicker = new Map();
  if (hasDeepGap) {
    const parsed = parseCsv(closeAuditBytes.toString("utf8")), ix = Object.fromEntries(parsed.header.map((value, index) => [value, index]));
    // a30f5ccd's full-book method intentionally prices only the frozen replay
    // close column.  The independently audited close column repairs 250
    // gradeability holes but is not the ruler used by the +782c receipt.
    for (const values of parsed.rows) {
      const raw = values[ix.replay_close_cents];
      closeByTicker.set(values[ix.ticker], /^\d+$/.test(raw) ? Number(raw) : null);
    }
    ensure(closeByTicker.size === 1608, `close audit count ${closeByTicker.size}`);
    ensure(v41FrozenEvents.length === 804, "frozen V41 event count changed");
  }
  const v41FullBook = hasDeepGap ? fullBookPnl(v41FrozenEvents, closeByTicker) : null;
  const v42FullBook = hasDeepGap ? fullBookPnl(marketEvents, closeByTicker) : null;
  const deepGapDiff = hasDeepGap ? deepGapDifferential(v41FrozenEvents, marketEvents, closeByTicker) : null;
  const fullBookFrozenReceipt = hasDeepGap ? JSON.parse(fullBookReceiptBytes) : null;
  const deepGapFrozenReceipt = hasDeepGap ? JSON.parse(deepGapCensusBytes) : null;
  const deepGapT10 = hasDeepGap ? deepGapFrozenReceipt.GUARD.sweep["T=10"] : null;
  if (hasDeepGap) {
    ensure(v41FullBook.aggregate.completed_pairs === 243 && v41FullBook.aggregate.completed_locked_cents === 732, "V41 completed-book reconstruction changed");
    ensure(v41FullBook.aggregate.naked_pnl_cents === 50 && v41FullBook.aggregate.naked_open === 63 && v41FullBook.aggregate.true_book_net_cents === 782, `V41 true-book reconstruction changed: ${JSON.stringify(v41FullBook.aggregate)}`);
    ensure(fullBookFrozenReceipt.TRUE_BOOK.NET_CENTS === 782 && fullBookFrozenReceipt.COMPLETED.pairs === 243, "a30f5ccd binding changed");
    ensure((-deepGapT10.withheld_naked_loss_cents) - deepGapT10.completed_locked_forfeited_cents - deepGapT10.winning_naked_forfeited_cents === 73, "645e035b T=10 binding changed");
  }
  const v42Acceptance = isV42 ? { completed_pairs: { value: marketScore.completed_pairs, minimum: 240, pass: marketScore.completed_pairs >= 240 }, true_book_net_cents: { value: v42FullBook.aggregate.true_book_net_cents, strict_minimum: 782, pass: v42FullBook.aggregate.true_book_net_cents > 782 } } : null;
  if (v42Acceptance) v42Acceptance.pass = v42Acceptance.completed_pairs.pass && v42Acceptance.true_book_net_cents.pass;
  const summarizeCategoryScores = (events) => Object.fromEntries([...new Set(events.map((event) => event.category))].sort().map((category) => {
    const cell = score(events.filter((event) => event.category === category));
    return [category, { D: cell.D, completed_pairs: cell.completed_pairs, under_par_pairs: cell.under_par_pairs, locked_cents_per_contract: cell.locked_cents_per_contract, frontier: cell.frontier }];
  }));
  const v48TradedFloors = isTradeTruthVariant ? tradedFloorCensus(baseByEvent, printLoad, reachByEvent) : null;
  const v48TradedFloorByLeg = isTradeTruthVariant ? new Map(v48TradedFloors.leg_rows.map((row) => [row.leg_identity, row])) : null;
  const attributionRows = isAttribution ? machineSpecs.map((spec) => {
    const run = machineRuns.get(spec.name), market = score(run.marketEvents), strict = score(run.strictEvents), fullBook = fullBookPnl(run.marketEvents, closeByTicker), tradeFloorGrade = isTradeTruthVariant ? gradeAgainstTradedFloors(run.marketEvents, v48TradedFloorByLeg) : null;
    return { machine: spec.name, market_mode: spec.market_mode || "MARKET_UNION_REACH", clauses: policy.normalizedClauses(spec.clauses), MARKET: market, MARKET_UNION_REACH: market, STRICT_PRINT_CROSS: strict, FULL_BOOK: fullBook.aggregate, TRADED_FLOOR_GRADE: tradeFloorGrade?.aggregate ?? null, category_x_bell_confidence: isTradeTruthVariant ? { MARKET: scorePartitions(run.marketEvents), STRICT_PRINT_CROSS: scorePartitions(run.strictEvents), TRADED_FLOOR_GRADE: tradeFloorGrade.category_x_bell_confidence } : null, by_category: { MARKET: summarizeCategoryScores(run.marketEvents), MARKET_UNION_REACH: summarizeCategoryScores(run.marketEvents), STRICT_PRINT_CROSS: summarizeCategoryScores(run.strictEvents), FULL_BOOK: fullBook.by_category }, full_book_rows: fullBook.rows, traded_floor_rows: tradeFloorGrade?.rows ?? null, traded_floor_games: tradeFloorGrade?.games ?? null };
  }) : null;
  const attributionByName = isAttribution ? new Map(attributionRows.map((row) => [row.machine, row])) : null;
  const v48BaselineReproduction = isV48 ? (() => {
    const row = attributionByName.get("V47_BASELINE");
    const expected = { completed_pairs: 396, under_par_pairs: 396, completed_locked_cents: 1936, naked_pnl_cents: -162, true_book_net_cents: 1774, strict_completed_pairs: 331, frontier: { LE_93: 52, LE_95: 71, LE_97: 142, LT_100: 396 } };
    const observed = { completed_pairs: row.MARKET.completed_pairs, under_par_pairs: row.MARKET.under_par_pairs, completed_locked_cents: row.FULL_BOOK.completed_locked_cents, naked_pnl_cents: row.FULL_BOOK.naked_pnl_cents, true_book_net_cents: row.FULL_BOOK.true_book_net_cents, strict_completed_pairs: row.STRICT_PRINT_CROSS.completed_pairs, frontier: row.MARKET.frontier };
    const pass = Object.entries(expected).every(([key, value]) => key === "frontier" ? Object.entries(value).every(([tier, n]) => observed.frontier[tier] === n) : observed[key] === value);
    return { frozen_V47_commit: V47_COMMIT, expected, observed, pass };
  })() : null;
  const v49BaselineReproduction = (isV49 || isV49b) ? (() => {
    const row = attributionByName.get("TRADE_TRUTH_V47_BASELINE");
    const expected = { completed_pairs: 396, under_par_pairs: 396, completed_locked_cents: 1936, naked_pnl_cents: -162, true_book_net_cents: 1774, strict_completed_pairs: 331, frontier: { LE_93: 52, LE_95: 71, LE_97: 142, LT_100: 396 } };
    const observed = { completed_pairs: row.MARKET.completed_pairs, under_par_pairs: row.MARKET.under_par_pairs, completed_locked_cents: row.FULL_BOOK.completed_locked_cents, naked_pnl_cents: row.FULL_BOOK.naked_pnl_cents, true_book_net_cents: row.FULL_BOOK.true_book_net_cents, strict_completed_pairs: row.STRICT_PRINT_CROSS.completed_pairs, frontier: row.MARKET.frontier };
    const pass = Object.entries(expected).every(([key, value]) => key === "frontier" ? Object.entries(value).every(([tier, n]) => observed.frontier[tier] === n) : observed[key] === value);
    return { frozen_V47_commit: V47_COMMIT, scoring_ruler: "TRADES_AS_TRUTH", expected, observed, pass };
  })() : null;
  const v49Differential = (isV49 || isV49b) ? ladderDifferential(machineRuns.get("TRADE_TRUTH_V47_BASELINE").marketEvents, machineRuns.get(isV49b ? "V49B_FAITHFUL_STAND_AT_P" : "V49_EVIDENCED_LEVEL_STANDING").marketEvents, closeByTicker, isV49b ? "V49B_FAITHFUL_STAND_AT_P" : "V49_EVIDENCED_LEVEL_STANDING") : null;
  const v48LadderNames = isV48 ? ["TRADE_TRUTH_BID_MINUS_ONE", "TRADE_TRUTH_BID", "TRADE_TRUTH_RECENT_TRADE"] : [];
  const v48SelectedRung = isV48 ? [...v48LadderNames].sort((a, b) => {
    const x = attributionByName.get(a), y = attributionByName.get(b);
    return y.FULL_BOOK.true_book_net_cents - x.FULL_BOOK.true_book_net_cents || y.MARKET.completed_pairs - x.MARKET.completed_pairs || y.FULL_BOOK.completed_locked_cents - x.FULL_BOOK.completed_locked_cents || a.localeCompare(b);
  })[0] : null;
  const v48LadderDiffs = isV48 ? Object.fromEntries(v48LadderNames.map((name) => [name, ladderDifferential(machineRuns.get("TRADE_TRUTH_V47_INCUMBENT").marketEvents, machineRuns.get(name).marketEvents, closeByTicker, name)])) : null;
  const receiptReproduction = isV43 ? {
    V41_BASELINE: { expected: { completed_pairs: 243, locked_cents: 732, naked_pnl_cents: 50, true_book_net_cents: 782 }, observed: attributionByName.get("V41_BASELINE").FULL_BOOK },
    C1_ARM_ONLY: { expected: { completed_pairs: 313, locked_cents: 925, naked_pnl_cents: 76, true_book_net_cents: 1001, frontier: { LE_93: 17, LE_95: 39, LE_97: 95, LT_100: 313 } }, observed: { ...attributionByName.get("C1_ARM_ONLY").FULL_BOOK, frontier: attributionByName.get("C1_ARM_ONLY").MARKET_UNION_REACH.frontier } },
    C3_LOOSEN_ONLY: { expected: { completed_pairs: 281, locked_cents: 799, naked_pnl_cents: 34, true_book_net_cents: 833 }, observed: attributionByName.get("C3_LOOSEN_ONLY").FULL_BOOK },
    C2_GUARD_ONLY: { controlling_receipt_expected_net_improvement_cents: 73, observed: attributionByName.get("C2_GUARD_ONLY").FULL_BOOK, observed_net_improvement_cents: attributionByName.get("C2_GUARD_ONLY").FULL_BOOK.true_book_net_cents - 782 },
  } : null;
  if (receiptReproduction) {
    for (const row of Object.values(receiptReproduction)) {
      if (!row.expected) continue;
      row.pass = Object.entries(row.expected).every(([key, value]) => key === "frontier" ? Object.entries(value).every(([tier, expected]) => row.observed.frontier[tier] === expected) : row.observed[key === "locked_cents" ? "completed_locked_cents" : key] === value);
    }
    receiptReproduction.C2_GUARD_ONLY.pass = receiptReproduction.C2_GUARD_ONLY.observed_net_improvement_cents === 73;
  }
  const v43Acceptance = isV43 ? {
    completed_pairs: { value: attributionByName.get("V43_ALL_THREE").MARKET_UNION_REACH.completed_pairs, minimum: 313, pass: attributionByName.get("V43_ALL_THREE").MARKET_UNION_REACH.completed_pairs >= 313 },
    true_book_net_cents: { value: attributionByName.get("V43_ALL_THREE").FULL_BOOK.true_book_net_cents, strict_minimum: 1001, pass: attributionByName.get("V43_ALL_THREE").FULL_BOOK.true_book_net_cents > 1001 },
  } : null;
  const v45BaselineReproduction = isV45 ? (() => {
    const row = attributionByName.get("V43_BASELINE");
    const expected = { completed_pairs: 395, completed_locked_cents: 1910, naked_pnl_cents: -162, true_book_net_cents: 1748, strict_completed_pairs: 331, frontier: { LE_93: 51, LE_95: 70, LE_97: 141, LT_100: 395 } };
    const observed = { completed_pairs: row.MARKET_UNION_REACH.completed_pairs, completed_locked_cents: row.FULL_BOOK.completed_locked_cents, naked_pnl_cents: row.FULL_BOOK.naked_pnl_cents, true_book_net_cents: row.FULL_BOOK.true_book_net_cents, strict_completed_pairs: row.STRICT_PRINT_CROSS.completed_pairs, frontier: row.MARKET_UNION_REACH.frontier };
    const pass = Object.entries(expected).every(([key, value]) => key === "frontier" ? Object.entries(value).every(([tier, n]) => observed.frontier[tier] === n) : observed[key] === value);
    return { frozen_V43_commit: V43_COMMIT, expected, observed, pass };
  })() : null;
  const v45Acceptance = isV45 ? (() => {
    const row = attributionByName.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT");
    return {
      baseline_reproduction: v45BaselineReproduction,
      completed_pairs: { value: row.MARKET_UNION_REACH.completed_pairs, minimum: 395, pass: row.MARKET_UNION_REACH.completed_pairs >= 395 },
      true_book_net_cents: { value: row.FULL_BOOK.true_book_net_cents, strict_minimum: 1748, pass: row.FULL_BOOK.true_book_net_cents > 1748 },
      naked_pnl_cents: { value: row.FULL_BOOK.naked_pnl_cents, strict_minimum: -162, pass: row.FULL_BOOK.naked_pnl_cents > -162 },
    };
  })() : null;
  const v46BaselineReproduction = isV46 ? (() => {
    const row = attributionByName.get("V45_BASELINE");
    const expected = { completed_pairs: 396, under_par_pairs: 396, completed_locked_cents: 1936, naked_pnl_cents: -162, true_book_net_cents: 1774, strict_completed_pairs: 331, frontier: { LE_93: 52, LE_95: 71, LE_97: 142, LT_100: 396 } };
    const observed = { completed_pairs: row.MARKET_UNION_REACH.completed_pairs, under_par_pairs: row.MARKET_UNION_REACH.under_par_pairs, completed_locked_cents: row.FULL_BOOK.completed_locked_cents, naked_pnl_cents: row.FULL_BOOK.naked_pnl_cents, true_book_net_cents: row.FULL_BOOK.true_book_net_cents, strict_completed_pairs: row.STRICT_PRINT_CROSS.completed_pairs, frontier: row.MARKET_UNION_REACH.frontier };
    const pass = Object.entries(expected).every(([key, value]) => key === "frontier" ? Object.entries(value).every(([tier, n]) => observed.frontier[tier] === n) : observed[key] === value);
    return { frozen_V45_commit: V45_COMMIT, expected, observed, pass };
  })() : null;
  const v47BaselineReproduction = isV47 ? (() => {
    const row = attributionByName.get("V45_BASELINE");
    const expected = { completed_pairs: 396, under_par_pairs: 396, completed_locked_cents: 1936, naked_pnl_cents: -162, true_book_net_cents: 1774, strict_completed_pairs: 331, frontier: { LE_93: 52, LE_95: 71, LE_97: 142, LT_100: 396 } };
    const observed = { completed_pairs: row.MARKET_UNION_REACH.completed_pairs, under_par_pairs: row.MARKET_UNION_REACH.under_par_pairs, completed_locked_cents: row.FULL_BOOK.completed_locked_cents, naked_pnl_cents: row.FULL_BOOK.naked_pnl_cents, true_book_net_cents: row.FULL_BOOK.true_book_net_cents, strict_completed_pairs: row.STRICT_PRINT_CROSS.completed_pairs, frontier: row.MARKET_UNION_REACH.frontier };
    const pass = Object.entries(expected).every(([key, value]) => key === "frontier" ? Object.entries(value).every(([tier, n]) => observed.frontier[tier] === n) : observed[key] === value);
    return { frozen_V45_commit: V45_COMMIT, expected, observed, pass };
  })() : null;
  const layerGroups = new Map();
  for (const row of marketGrades.residuals) { const key = row.layer_bind.owner; if (!layerGroups.has(key)) layerGroups.set(key, []); layerGroups.get(key).push(row); }
  const layerRanking = [...layerGroups].map(([owner, rows]) => ({ owner, games: new Set(rows.map((row) => row.event_id)).size, sides: rows.length, measurable_cents: rows.reduce((sum, row) => sum + (row.layer_bind.measurable_cents || 0), 0), category_x_bell_confidence: countBy(rows, (row) => `${row.category}|${row.bell_confidence}`) })).sort((a, b) => b.measurable_cents - a.measurable_cents || b.games - a.games || a.owner.localeCompare(b.owner));
  const namedLabels = isV52 ? ["ARSMAR", "SANDAN", "PUTJEA", "POLKUH", "MERDRO"] : (isV49 || isV49b) ? ["HERKAZ", "ARNROM", "KIRSEK", "KRUFER", "BOSCOP", "PANFAL"] : isV48 ? ["LUZTSE", "SALIBR", "ARNROM", "KIRSEK", "KRUFER", "BOSCOP", "PANFAL"] : isV47 ? ["SURECH", "ARNROM", "KIRSEK", "KRUFER", "BOSCOP", "PANFAL"] : isV46 ? ["PANFAL", "ARNROM", "KIRSEK", "KRUFER", "BOSCOP"] : isV45 ? ["LUZTSE", "COLCER", "SMIYUN", "VANLEE", "SAINUG", "PENTHA", "SHEOLI", "ARNROM", "KRUFER", "KIRSEK"] : isV43 ? ["KIRSEK", "ARNROM", "KRUFER", "BOSCOP", "PUTJEA", "BORDIM", "ROCBUE", "KREZHE"] : isV42 ? ["PUTJEA", "ROCBUE", "KREZHE", "BORDIM", "ARNROM"] : isV41 ? ["ARNROM", "BOSCOP", "NIKVRB", "WESPAA", "KRUFER"] : ["ARNROM", "BOSCOP", "WESPAA", "NIKVRB", "GANJAN"];
  const named = {};
  for (const label of namedLabels) {
    const market = marketEvents.find((event) => event.event_id.includes(label)), strict = strictEvents.find((event) => event.event_id.includes(label));
    ensure(market && strict, `named game absent ${label}`);
    const reach = reachByEvent.get(market.event_id), reachLevels = Object.values(reach.legs).map((leg) => leg.union_reach_cents);
    const legView = (event) => Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, terminal_rest_cents: leg.resting_target_at_edge_cents, final_causal_state: leg.last_combined_state, persistent_join_level_cents: leg.persistent_join_level, persistent_join_timestamp_epoch: leg.persistent_join_timestamp_epoch, persistent_join_book_last_trade_receipts: leg.persistent_join_book_last_trade_receipts, persistent_join_certified_seller_aggressed_prints: leg.persistent_join_certified_seller_aggressed_prints, persistent_join_evidence_receipt: leg.persistent_join_evidence_receipt, post_join_book_last_trade_receipts: leg.post_join_book_last_trade_receipts, post_join_certified_seller_hits_at_level: leg.post_join_certified_seller_hits_at_level, sanity_bound_receipts: leg.sanity_bound_rows, sanity_violations: leg.sanity_violation_rows }]));
    named[label] = { event_id: market.event_id, reach_levels: Object.fromEntries(Object.entries(reach.legs).map(([id, leg]) => [id, leg.union_reach_cents])), reach_combined_cents: reachLevels.every(Number.isInteger) ? reachLevels.reduce((a, b) => a + b, 0) : null, MARKET_UNION_REACH: { completed: market.completed_pair, combined_entry_cents: market.combined_entry_cents, under_par: market.pair_under_par, legs: legView(market) }, STRICT_PRINT_CROSS: { completed: strict.completed_pair, combined_entry_cents: strict.combined_entry_cents, under_par: strict.pair_under_par, legs: legView(strict) } };
  }
  if (!isV42 && !isAttribution) ensure(named.ARNROM.reach_combined_cents === 88 && named.BOSCOP.reach_combined_cents === 75 && named.NIKVRB.reach_combined_cents === 86, "named reach identities changed");
  const namedAttribution = isAttribution ? Object.fromEntries(machineSpecs.map((spec) => {
    const run = machineRuns.get(spec.name), gameRows = {};
    for (const label of namedLabels) {
      const market = run.marketEvents.find((event) => event.event_id.includes(label)), strict = run.strictEvents.find((event) => event.event_id.includes(label));
      gameRows[label] = { event_id: market.event_id, MARKET_UNION_REACH: { completed: market.completed_pair, combined_entry_cents: market.combined_entry_cents, under_par: market.pair_under_par, legs: Object.fromEntries(Object.entries(market.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, terminal_reason: leg.terminal_reason }])) }, STRICT_PRINT_CROSS: { completed: strict.completed_pair, combined_entry_cents: strict.combined_entry_cents, under_par: strict.pair_under_par } };
    }
    return [spec.name, gameRows];
  })) : null;
  const policyFile = path.join(repo, isV52 ? "arb-executor/analysis/window1_v52_judgment_gate.js" : isV49b ? "arb-executor/analysis/window1_v49b_faithful_stand_at_p.js" : isV49 ? "arb-executor/analysis/window1_v49_evidenced_level_standing.js" : isV48 ? "arb-executor/analysis/window1_v48_trades_as_truth.js" : isV47 ? "arb-executor/analysis/window1_v47_same_tick_arm.js" : isV46 ? "arb-executor/analysis/window1_v46_pair_gated_gap_credit.js" : isV45 ? "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js" : isV43 ? "arb-executor/analysis/window1_v43_composed_machine.js" : isV42 ? "arb-executor/analysis/window1_v42_deep_gap_feasibility_guard.js" : isV41 ? "arb-executor/analysis/window1_v41_maker_machine.js" : isV40 ? "arb-executor/analysis/window1_v40_incumbent_direction_placement_stack.js" : isV39 ? "arb-executor/analysis/window1_v39_corrected_placement_stack.js" : "arb-executor/analysis/window1_v38_maker_only_machine.js"), builderFile = __filename;
  const wrapperFile = path.join(repo, isV52 ? "arb-executor/analysis/build_window1_v52_judgment_gate.js" : isV49b ? "arb-executor/analysis/build_window1_v49b_faithful_stand_at_p.js" : isV49 ? "arb-executor/analysis/build_window1_v49_evidenced_level_standing.js" : isV48 ? "arb-executor/analysis/build_window1_v48_trades_as_truth.js" : isV47 ? "arb-executor/analysis/build_window1_v47_same_tick_arm.js" : isV46 ? "arb-executor/analysis/build_window1_v46_pair_gated_gap_credit.js" : isV45 ? "arb-executor/analysis/build_window1_v45_guard_release_sibling_credit.js" : isV43 ? "arb-executor/analysis/build_window1_v43_composed_machine.js" : isV42 ? "arb-executor/analysis/build_window1_v42_deep_gap_feasibility_guard.js" : isV41 ? "arb-executor/analysis/build_window1_v41_maker_machine.js" : isV40 ? "arb-executor/analysis/build_window1_v40_incumbent_direction_placement_stack.js" : "arb-executor/analysis/build_window1_v39_corrected_placement_stack.js");
  const policyText = fs.readFileSync(policyFile, "utf8");
  const makerPolicyLineageText = hasDeepGap ? `${fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v41_maker_machine.js"), "utf8")}\n${isAttribution ? fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v42_deep_gap_feasibility_guard.js"), "utf8") : ""}\n${policyText}` : policyText;
  if (!isPlacementStack || isMaker41) ensure(!/action:\s*["']TAKE["']/.test(policyText) && !/function\s+.*take/i.test(policyText) && !/matureFloorTakePermission/.test(policyText), `take path survived in ${variant.toUpperCase()} policy`);
  if (isV39) ensure(/V36_MATURE_EVIDENCE_FLOOR_TAKE_UNCHANGED/.test(policyText), "V36 take path missing from V39");
  if (isV40) {
    ensure(!/window1_v39|agreementWeightedDirection/.test(policyText), "V39 classifier survived in V40 policy");
    ensure(/MATURE_EVIDENCE_FLOOR_TAKE/.test(policyText), "V36 take path missing from V40");
  }
  if (isMaker41) {
    ensure(!/window1_v39|window1_v40|action:\s*["']TAKE["']|matureFloorTakePermission/.test(makerPolicyLineageText), "V41/V42 imported a forbidden classifier or take path");
    ensure(/PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1/.test(makerPolicyLineageText), "V41 persistence-only join authority absent");
    ensure(policy.combineState === require("./window1_v36_state_directional_rest_mature_floor.js").combineState, "V41 state machine is not V36 incumbent");
  }
  if (hasDeepGap) {
    ensure(policy.DEEP_GAP_TOLERANCE_CENTS === 10, "V42 tolerance changed");
    if (isV42) ensure(policy.placementTarget === require("./window1_v41_maker_machine.js").placementTarget, "V42 changed V41 placement target law");
  }
  if (isAttribution) {
    ensure(!/walk[_ -]?lag/i.test(policyText), "V43 imported excluded walk-lag removal");
    ensure(policy.normalizedClauses({}).arm_at_first_evidence === false, "V43 clause defaults are not all off");
    ensure(policy.combineState === require("./window1_v36_state_directional_rest_mature_floor.js").combineState, "V43 changed V41/V36 state machine");
  }
  const causalReachPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/CAUSAL_REACH.json";
  const riserFrontierPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RISER_TRIGGER_FRONTIER.json";
  const levelPolicyPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LEVEL_POLICY_REALIZATION.json";
  const armFirstEvidencePath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/CONVICTION_LAG_REMOVAL.json";
  const loosenOneCentPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/FLOW_ABOVE_REST_LOOSENING_SWEEP.json";
  const causalReachBytes = isMaker41 ? gitShow(CAUSAL_REACH_COMMIT, causalReachPath) : null;
  const riserFrontierBytes = isMaker41 ? gitShow(RISER_FRONTIER_COMMIT, riserFrontierPath) : null;
  const levelPolicyBytes = isMaker41 ? gitShow(LEVEL_POLICY_COMMIT, levelPolicyPath) : null;
  const causalReachReceipt = isMaker41 ? JSON.parse(causalReachBytes) : null;
  const riserFrontierReceipt = isMaker41 ? JSON.parse(riserFrontierBytes) : null;
  const levelPolicyReceipt = isMaker41 ? JSON.parse(levelPolicyBytes) : null;
  const armFirstEvidenceBytes = isAttribution ? gitShow(ARM_FIRST_EVIDENCE_COMMIT, armFirstEvidencePath) : null;
  const loosenOneCentBytes = isAttribution ? gitShow(LOOSEN_ONE_CENT_COMMIT, loosenOneCentPath) : null;
  const armFirstEvidenceReceipt = isAttribution ? JSON.parse(armFirstEvidenceBytes) : null;
  const loosenOneCentReceipt = isAttribution ? JSON.parse(loosenOneCentBytes) : null;
  const v43RecalibrationPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V43_COMPOSITION_RECALIBRATION.json";
  const v43DocketPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V43_RESIDUAL_DOCKET.json";
  const luztseMarksPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/v43_docket/26JUL18LUZTSE_DECISION_MARKS.json";
  const luztseTimelinePath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/v43_docket/26JUL18LUZTSE_DUAL_TIMELINE_V2.csv";
  const v43RecalibrationBytes = isV45 ? gitShow(V43_RECALIBRATION_COMMIT, v43RecalibrationPath) : null;
  const v43DocketBytes = isV45 ? gitShow(V43_RESIDUAL_DOCKET_COMMIT, v43DocketPath) : null;
  const luztseMarksBytes = isV45 ? gitShow(V43_RESIDUAL_DOCKET_COMMIT, luztseMarksPath) : null;
  const luztseTimelineBytes = isV45 ? gitShow(V43_RESIDUAL_DOCKET_COMMIT, luztseTimelinePath) : null;
  const strictAskFootprintPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/STRICT_ASK_CREDIT_FOOTPRINT.json";
  const strictAskFootprintMdPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/STRICT_ASK_CREDIT_FOOTPRINT.md";
  const panfalMarksPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/v45_docket/26JUL13PANFAL_DECISION_MARKS.json";
  const panfalTimelinePath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/v45_docket/26JUL13PANFAL_DUAL_TIMELINE_V2.csv";
  const strictAskFootprintBytes = isV46 ? gitShow(STRICT_ASK_FOOTPRINT_COMMIT, strictAskFootprintPath) : null;
  const strictAskFootprintMdBytes = isV46 ? gitShow(STRICT_ASK_FOOTPRINT_COMMIT, strictAskFootprintMdPath) : null;
  const panfalMarksBytes = isV46 ? gitShow(STRICT_ASK_FOOTPRINT_COMMIT, panfalMarksPath) : null;
  const panfalTimelineBytes = isV46 ? gitShow(STRICT_ASK_FOOTPRINT_COMMIT, panfalTimelinePath) : null;
  const strictAskFootprint = isV46 ? JSON.parse(strictAskFootprintBytes) : null;
  const frozenV45ControlPath = ".claude/window1_live_v4_replay/v45_guard_release_sibling_credit_20260809/CONTROL_BINDING.json";
  const frozenV45ScorePath = ".claude/window1_live_v4_replay/v45_guard_release_sibling_credit_20260809/ATTRIBUTION_SCORECARD.json";
  const frozenV45PolicyPath = "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js";
  const frozenV45ControlBytes = (isV46 || isV47) ? gitShow(V45_COMMIT, frozenV45ControlPath) : null;
  const frozenV45ScoreBytes = (isV46 || isV47) ? gitShow(V45_COMMIT, frozenV45ScorePath) : null;
  const frozenV45PolicyBytes = (isV46 || isV47) ? gitShow(V45_COMMIT, frozenV45PolicyPath) : null;
  const surechMarksPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/l4_archetype/SURECH_DECISION_MARKS.json";
  const surechTimelinePath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/l4_archetype/SURECH_DUAL_TIMELINE_V2.csv";
  const surechMarksBytes = isV47 ? gitShow(SURECH_RENDER_COMMIT, surechMarksPath) : null;
  const surechTimelineBytes = isV47 ? gitShow(SURECH_RENDER_COMMIT, surechTimelinePath) : null;
  const tradesTruthRecutPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/THE_316_RECUT.json";
  const tradesTruthRecutMdPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/THE_316_RECUT.md";
  const tradesTruthRecutBytes = isV48 ? gitShow(TRADES_TRUTH_RECUT_COMMIT, tradesTruthRecutPath) : null;
  const tradesTruthRecutMdBytes = isV48 ? gitShow(TRADES_TRUTH_RECUT_COMMIT, tradesTruthRecutMdPath) : null;
  const tradesTruthRecut = isV48 ? JSON.parse(tradesTruthRecutBytes) : null;
  const standabilityPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/STANDABILITY_V2_PLACEMENT_WINDOW.json";
  const standabilityMdPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/STANDABILITY_V2_PLACEMENT_WINDOW.md";
  const herkazPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/WLE_TOP_EXEMPLAR.json";
  const herkazMarksPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/wle_top/26JUL12HERKAZ_DECISION_MARKS.json";
  const herkazTimelinePath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/wle_top/26JUL12HERKAZ_DUAL_TIMELINE_V2.csv";
  const standabilityBytes = (isV49 || isV49b) ? gitShow(STANDABILITY_V2_COMMIT, standabilityPath) : null;
  const standabilityMdBytes = (isV49 || isV49b) ? gitShow(STANDABILITY_V2_COMMIT, standabilityMdPath) : null;
  const herkazBytes = isV49 ? gitShow(HERKAZ_EXEMPLAR_COMMIT, herkazPath) : null;
  const herkazMarksBytes = isV49 ? gitShow(HERKAZ_EXEMPLAR_COMMIT, herkazMarksPath) : null;
  const herkazTimelineBytes = isV49 ? gitShow(HERKAZ_EXEMPLAR_COMMIT, herkazTimelinePath) : null;
  const standabilityReceipt = (isV49 || isV49b) ? JSON.parse(standabilityBytes) : null;
  const herkazReceipt = isV49 ? JSON.parse(herkazBytes) : null;
  if (isMaker41) {
    ensure(causalReachReceipt.CAUSAL_REACH.under_par === 504 && causalReachReceipt.CAUSAL_REACH.locked === 3319, "causal reach binding changed");
    ensure(riserFrontierReceipt.per_trigger.T4_persist300.under_par === 631, "persistence-only trigger frontier changed");
    ensure(levelPolicyReceipt.per_policy.P2_join.under_par === 480, "P2 realization binding changed");
  }
  if (isAttribution) {
    ensure(armFirstEvidenceReceipt.rows.ARM.completed === 313 && armFirstEvidenceReceipt.rows.ARM.true_book === 1001, "9ddfe8c6 ARM binding changed");
    ensure(loosenOneCentReceipt.per_k["k=1"].completed === 281 && loosenOneCentReceipt.per_k["k=1"].true_book === 833, "52275c9d +1c binding changed");
  }
  if (isV46) {
    ensure(strictAskFootprint.FOOTPRINT?.total === 50, "aa884cc5 footprint leg count changed");
    ensure(strictAskFootprint.FOOTPRINT?.by_chain_link?.CHAIN_L6_PRESENT_BUT_NO_COUNTERPARTY === 42, "aa884cc5 L6 footprint changed");
    ensure(strictAskFootprint.THE_FIX?.ADVERSE?.naked_unfrozen_legs === 11 && strictAskFootprint.THE_FIX?.ADVERSE?.naked_only_distribution?.median === 44, "aa884cc5 naked-knife binding changed");
    ensure(shaBytes(frozenV45PolicyBytes) === shaBytes(Buffer.from(fs.readFileSync(path.join(repo, frozenV45PolicyPath), "utf8").replace(/\r\n/g, "\n"))), "V45 inherited Git-normalized policy bytes differ from 3bda0a54");
    ensure(JSON.parse(frozenV45ControlBytes).schema_version === "window1-v45-guard-release-sibling-credit-control-v1", "V45 frozen control binding changed");
  }
  if (isV47) {
    ensure(shaBytes(frozenV45PolicyBytes) === shaBytes(Buffer.from(fs.readFileSync(path.join(repo, frozenV45PolicyPath), "utf8").replace(/\r\n/g, "\n"))), "V45 inherited Git-normalized policy bytes differ from 3bda0a54");
    ensure(JSON.parse(frozenV45ControlBytes).schema_version === "window1-v45-guard-release-sibling-credit-control-v1", "V45 frozen control binding changed");
    ensure(JSON.parse(surechMarksBytes).event === "KXATPCHALLENGERMATCH-26JUL14SURECH", "SURECH render identity changed");
  }
  if (isV48) {
    ensure(tradesTruthRecut.population?.L6_legs_recut === 342, "e995c81b re-cut leg population changed");
    ensure(tradesTruthRecut.verdicts?.REST_AT_AVAILABLE + tradesTruthRecut.verdicts?.REST_BELOW_AVAILABLE === 330, "e995c81b real-offer population changed");
    ensure(!Object.hasOwn(tradesTruthRecut.channel_that_set_lowest || {}, "SELLER_CROSS"), "e995c81b unexpectedly contains seller-cross as a lowest channel");
  }
  if (isV49 || isV49b) {
    ensure(standabilityReceipt.recoverable_under_window_law.games === 81 && standabilityReceipt.recoverable_under_window_law.locked_cents === 1162, "fe4747cd window-law target changed");
    ensure(standabilityReceipt.conservation.the_46_analyzed === 46 && standabilityReceipt.conservation.WINDOW_LAWFUL_EVIDENCE === 20, "fe4747cd placement-window recut changed");
  }
  if (isV49) {
    ensure(herkazReceipt.game === "26JUL12HERKAZ" && herkazReceipt.P_evidenced_level === 46 && herkazReceipt.completing_print.price === 46, "b9673399 HERKAZ fingerprint changed");
  }
  const control = isV49b
    ? { schema_version: "window1-v49b-faithful-stand-at-p-control-v1", base: V47_COMMIT, frozen_V47: V47_COMMIT, controlling_receipts: [SUBSTITUTION_AUDIT_COMMIT, STANDABILITY_V2_COMMIT, DECISION_CHAIN_81_COMMIT, IDENTITY_81_COMMIT], architecture: { change: "ON_HASH_BOUND_DOCTRINE_LEGS_STAND_AT_EXACT_P_AFTER_CAUSAL_OWN_TAPE_EVIDENCE", no_offset: true, prohibited_mechanism: "BID_MINUS_ONE_OFFSET_AT_P", evidence_sources: ["PRIOR_TRUE_TRADE_AT_OR_BELOW_P", "OWN_BEST_BID_REACHED_EXACT_P", "HASH_BOUND_PRE_WINDOW_CAUSAL_EVIDENCE"], incumbent_elsewhere: "V47_BYTE_IDENTICAL", untouched: ["PERSISTENT_JOIN", "WTA_OTHER_EXPRESSION_HOLD", "PAIR_CAP", "POST_ONLY_SANITY", "DEEP_GAP_GUARD", "SIBLING_CREDIT_RELEASE", "SAME_TICK_ARM", "HARD_PREBELL_EDGE"], causal_floor_table_d3db740f: "PROHIBITED_FROM_DECISION_CONSUMPTION" }, fill_rulers: { market_scoring: "ANY_TRUE_TRADE_AT_OR_BELOW_PRIOR_LAWFUL_REST", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST", never_swapped: true }, gauge_stamp: "OPTIMISTIC_EX_POST_TRUE_TRADE_FLOOR" }
    : isV49
    ? { schema_version: "window1-v49-evidenced-level-standing-control-v1", base: V47_COMMIT, frozen_V47: V47_COMMIT, controlling_receipts: [STANDABILITY_V2_COMMIT, HERKAZ_EXEMPLAR_COMMIT, LOOSEN_ONE_CENT_COMMIT], architecture: { change: "UNIVERSAL_PLUS_ONE_REPLACED_BY_CAUSAL_EVIDENCE_CONDITIONAL_STAND_AT_P", lawful_level_evidence: ["STRICTLY_EARLIER_TRUE_TRADE_AT_OR_BELOW_P", `OWN_BEST_BID_CONTINUOUSLY_STANDING_AT_P_FOR_INHERITED_${policy.PERSISTENT_LEVEL_SECONDS}_SECONDS`], inherited_standing_constant: { seconds: policy.PERSISTENT_LEVEL_SECONDS, provenance: "V47_PERSISTENCE_ONLY_JOIN_LAW" }, historical_bid_sighting_alone: "NO_AUTHORITY", effect: "TRACKING_REST_STANDS_AT_P_INSTEAD_OF_P_MINUS_ONE", no_evidence: "V41_BID_MINUS_ONE_OR_JOIN_INCUMBENT_PATH", untouched: ["PERSISTENT_JOIN", "WTA_OTHER_EXPRESSION_HOLD", "PAIR_CAP", "POST_ONLY_SANITY", "DEEP_GAP_GUARD", "SIBLING_CREDIT_RELEASE", "SAME_TICK_ARM", "HARD_PREBELL_EDGE"], clocks_as_decision_inputs: [] }, acceptance_bar: { zero_bound_named_regressions: true, HERKAZ_completes_HER_at_or_better_46: true, aggregate_target: null }, fill_rulers: { market_scoring: "ANY_TRUE_TRADE_AT_OR_BELOW_PRIOR_LAWFUL_REST", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST", never_swapped: true } }
    : isV48
    ? { schema_version: "window1-v48-trades-as-truth-control-v1", base: V47_COMMIT, frozen_V47: V47_COMMIT, controlling_receipts: [TRADES_TRUTH_RECUT_COMMIT], architecture: { law_change: "A_STANDING_REST_CREDITS_ON_ANY_TRUE_TRADE_PRINT_AT_OR_BELOW_ITS_LEVEL_AFTER_THE_REST_STOOD", excluded_credit_filters: ["ASK", "QUOTE_TOUCH", "AGGRESSOR_SIDE", "DWELL", "SIZE", "ARRIVAL_DIRECTION", "CHANNEL_TAXONOMY"], asks_role: "PLACEMENT_ONLY_NEVER_CREDIT_OR_FLOOR", lawful_span: "V47_HARD_PREBELL_EDGE_UNCHANGED", strict_ruler: "V47_STRICT_PRINT_CROSS_BUILD_VERIFICATION_ONLY", placement_attribution: ["V47_INCUMBENT", "BID_MINUS_ONE", "BID", "LOWEST_TRUE_TRADE_TRAILING_300S"], placement_honesty: "V47_INCUMBENT_IS_A_MIXED_OPERATIVE_STACK_AND_IS_NOT_RELABELLED_BID_MINUS_ONE", clocks_as_decision_inputs: [] }, acceptance_bar: { zero_bound_named_regressions: true, aggregate_target: null, gains_reported_as_observed: true }, fill_rulers: { market_scoring: "ANY_TRUE_TRADE_AT_OR_BELOW_PRIOR_LAWFUL_REST", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST", never_swapped: true } }
    : isV46
    ? { schema_version: "window1-v46-pair-gated-gap-credit-control-v1", base: V45_COMMIT, frozen_V45: V45_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [STRICT_ASK_FOOTPRINT_COMMIT], architecture: { incumbent: "V45_BYTE_IDENTICAL_EXCEPT_ONE_PAIR_GATED_GAP_CREDIT_CLAUSE", incumbent_clause: "FALLING_NO_CHASE_STRICT_ASK_CREDIT", additional_credit_event: "SINGLE_RECEIPT_ASK_GAP_GE_3_CENTS", authorization: "OTHER_EXPRESSION_ALREADY_CREDITED", authorized_effect: "REPRICE_EXISTING_FALLING_REST_DOWN_TO_MIN_CURRENT_ASK_MINUS_1_PAIR_CAP", sibling_not_credited: "V45_ACTION_STREAM_UNCHANGED", fill_credit: "INHERITED_MARKET_UNION_OR_STRICT_LATER_RECEIPT_ONLY_NO_SAME_RECEIPT_FABRICATION", pair_cap: "V45_UNCHANGED", sanity_bound: "REST_STRICTLY_BELOW_CURRENT_BEST_ASK", clocks_as_decision_inputs: [], hard_prebell_edge: "V45_UNCHANGED", take_path: "DELETED_IN_V41" }, acceptance_bar: { completed_pairs_min: 396, true_book_net_cents_strictly_greater_than: 1774, zero_bound_regressions: true, PANFAL_at_or_better_92_and_locked_min_8: true }, fill_rulers: { market_scoring: "CANON_UNION_CHANNELS", build_verification: "STRICT_PRINT_CROSS", never_swapped: true } }
    : isV47
    ? { schema_version: "window1-v47-same-tick-arm-control-v1", base: V45_COMMIT, frozen_V45: V45_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [SURECH_RENDER_COMMIT], architecture: { incumbent: "V45_BYTE_IDENTICAL_EXCEPT_EXPLICIT_ATOMIC_RECEIPT_PIPELINE", fix: "JOIN_QUALIFICATION_AND_PLACEMENT_DECISION_EXECUTE_IN_ONE_RECEIPT_LOCAL_CALL", qualification_law: "V45_UNCHANGED", persistence_level_definition: "V45_UNCHANGED", target_guard_cap_sanity_fill_and_edge_laws: "V45_UNCHANGED", scheduler_latency_after_qualification: 0, clocks_as_decision_inputs: [], hard_prebell_edge: "V45_UNCHANGED", take_path: "DELETED_IN_V41" }, evidence_scope: { SURECH_render_role: "OLDER_L4_ARCHETYPE_EVIDENCE_NOT_A_FROZEN_V45_DECISION_TRACE", executable_SEG_C_footprint: "V45_VS_V47_WHOLE_804" }, acceptance_bar: { V45_reproduced: true, zero_named_regressions: true, aggregate_gain_required: false }, fill_rulers: { market_scoring: "CANON_UNION_CHANNELS", build_verification: "STRICT_PRINT_CROSS", never_swapped: true } }
    : isV45
    ? { schema_version: "window1-v45-guard-release-sibling-credit-control-v1", base: V43_COMMIT, frozen_V43: V43_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [V43_RESIDUAL_DOCKET_COMMIT, V43_RECALIBRATION_COMMIT, DEEP_GAP_CENSUS_COMMIT, FULL_BOOK_PNL_COMMIT], architecture: { incumbent: "V43_BYTE_IDENTICAL_EXCEPT_ONE_POST_CREDIT_GUARD_AUTHORITY_TERMINATION", pre_fill_deep_gap_guard: "V43_T10_REMAINS_ACTIVE_UNCHANGED", release_trigger: "OTHER_EXPRESSION_CREDITED", release_effect: "ACTIVE_DEEP_GAP_WITHHOLD_TERMINATES_AND_REST_POSTS_IMMEDIATELY_AT_V43_LAWFUL_LEVEL", fixed_pair_cap: "99_MINUS_CREDITED_SIBLING_ENTRY", sanity_bound: "V43_REST_STRICTLY_BELOW_CURRENT_BEST_ASK_UNCHANGED", clocks_as_decision_inputs: [], hard_prebell_edge: "V43_UNCHANGED", take_path: "DELETED_IN_V41" }, acceptance_bar: { completed_pairs_min: 395, true_book_net_cents_strictly_greater_than: 1748, naked_pnl_cents_strictly_greater_than: -162, named_at_or_better_and_scope_checks: true }, fill_rulers: { market_scoring: "CANON_UNION_CHANNELS", build_verification: "STRICT_PRINT_CROSS", never_swapped: true } }
    : isV43
    ? { schema_version: "window1-v43-composed-machine-control-v1", parent: V41_COMMIT, frozen_V41: V41_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [ARM_FIRST_EVIDENCE_COMMIT, DEEP_GAP_CENSUS_COMMIT, FULL_BOOK_PNL_COMMIT, LOOSEN_ONE_CENT_COMMIT], architecture: { incumbent: "V41_BYTE_IDENTICAL_EXCEPT_EXPLICIT_RECEIPT_PRICED_CLAUSE_COMBINATIONS", clause_1: "RISING_PERSISTED_LEVEL_JOINABLE_FROM_FIRST_OBSERVATION_NO_300S_NO_SELLER_HIT_NO_SECOND_VISIT", excluded_from_clause_1: "WALK_LAG_REMOVAL_HELD_NOT_INCLUDED", clause_2: "REST_AT_L_UNLAWFUL_IFF_99_MINUS_L_IS_STRICTLY_LESS_THAN_SIBLING_CONTEMPORANEOUS_BEST_ASK_MINUS_10", clause_3: "TRACKING_REST_MIN_BEST_BID_PAIR_CAP_BEST_ASK_MINUS_1", pairwise_and_combined_attribution: true, take_path: "DELETED_IN_V41", pair_cap: "V41_UNCHANGED", clocks_as_decision_inputs: [], hard_prebell_edge: "V41_UNCHANGED" }, acceptance_bar: { true_book_net_cents_strictly_greater_than: 1001, completed_pairs_min: 313, zero_named_regressions: true }, fill_rulers: { market_scoring: "CANON_UNION_CHANNELS", build_verification: "STRICT_PRINT_CROSS", never_swapped: true } }
    : isV42
    ? { schema_version: "window1-v42-deep-gap-feasibility-guard-control-v1", parent: V41_COMMIT, frozen_V41: V41_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [DEEP_GAP_CENSUS_COMMIT, FULL_BOOK_PNL_COMMIT, CAUSAL_REACH_COMMIT, RISER_FRONTIER_COMMIT, LEVEL_POLICY_COMMIT], architecture: { incumbent: "V41_BYTE_IDENTICAL_EXCEPT_ONE_RECEIPT_CAUSAL_FEASIBILITY_CLAUSE", clause: "REST_AT_L_UNLAWFUL_IFF_99_MINUS_L_IS_STRICTLY_LESS_THAN_SIBLING_CONTEMPORANEOUS_BEST_ASK_MINUS_10", tolerance_cents: policy.DEEP_GAP_TOLERANCE_CENTS, reevaluation: "EVERY_OWN_BOOK_RECEIPT_AND_EVERY_SIBLING_BOOK_RECEIPT_WHILE_WITHHELD", lift: "THE_MOMENT_SIBLING_ASK_MINUS_IMPLIED_CAP_IS_LE_10", missing_sibling_book: "NO_GUARD_AUTHORITY_V41_UNCHANGED", clocks_as_decision_inputs: [], take_path: "DELETED_IN_V41", hard_prebell_edge: "V41_UNCHANGED" }, acceptance_bar: { true_book_net_cents_strictly_greater_than: 782, completed_pairs_min: 240 }, fill_rulers: { market_scoring: "CANON_UNION_CHANNELS", build_verification: "STRICT_PRINT_CROSS", never_swapped: true } }
    : isV41
    ? { schema_version: "window1-v41-maker-machine-control-v1", base: V36_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [CAUSAL_REACH_COMMIT, RISER_FRONTIER_COMMIT, LEVEL_POLICY_COMMIT, COUNTERFACTUAL_COMMIT], architecture: { entry_unit: "ONE_GAME_STATE_TWO_SINGLE_REST_OUTPUTS", T5_arming: "EVERY_LEG_PLACES_FROM_FIRST_TWO_SIDED_BOOK_WITH_NO_PRE_PLACEMENT_EVIDENCE_GATE", direction: "V36_INCUMBENT_QUOTE_PATH_PLUS_JUL6_PRESSURE_STATE_MACHINE", FALLING: "V36_CAUSAL_NO_CHASE_WALKING_REST", SETTLED: "V36_BID_MINUS_ONE_TRACKING", RISING: `BID_MINUS_ONE_TRACKER_UNTIL_CURRENT_BID_LEVEL_PERSISTS_${policy.PERSISTENT_LEVEL_SECONDS}S_THEN_SINGLE_REST_JOINS_DEEPEST_PERSISTENT_LEVEL; SELLER_HIT_NOT_REQUIRED; P2_OVERRIDES_P1`, WTA_inverse_falling_hold: "WTA_RISING_SIDE_WITH_OTHER_EXPRESSION_FALLING_HOLDS_DEEPER_CAUSAL_OWN_LEVEL", sanity_bound: "REST_STRICTLY_BELOW_CURRENT_BEST_ASK", take_path: "DELETED_NOT_GATED", pair_cap: "99_MINUS_FIRST_FILL_LAZY_LEG_1", clocks_as_decision_inputs: [], hard_prebell_edge: "V36_WINDOW1_SPAN_804_UNCHANGED" }, fill_rulers: { market_scoring: "CANON_UNION_CHANNELS_QUOTE_TOUCH_10S_SIZE5_PLUS_TRADED_AT_LEVEL_PLUS_STRICT_PRINT_CROSS", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST", never_swapped: true }, comparison: { V36_gross: "FROZEN_STRICT_EVENT_LEDGER", V36_net: "TAKER_PER_CONTRACT_CEIL_0_07_P_1_MINUS_P; MAKER_ZERO", causal_reach: { under_par: 504, locked_cents: 3319 } } }
    : isV40
    ? { schema_version: "window1-v40-incumbent-direction-placement-stack-control-v1", base: V36_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [COUNTERFACTUAL_COMMIT, "2c54d724186d2f8b152205379aef88499c457a7a", FALLER_ANATOMY_COMMIT, "ff5880d11a88b0d12415f5371d7cbb61331957e4"], architecture: { direction: "V36_INCUMBENT_QUOTE_PATH_PLUS_JUL6_PRESSURE_STATE_MACHINE_BYTE_FOR_FUNCTION_INHERITED", classifier_research_status: "V39_CAUSAL_CLASSIFIER_SEVERED_CLASSIFIER_RESEARCH_OPEN", persistent_level_join: `V36_INCUMBENT_RISING_CURRENT_BID_RESIDENCY_GE_${policy.PERSISTENT_LEVEL_SECONDS}S_AND_LAST_TRADED_AT_LEVEL_THEN_REST_AT_LEVEL`, WTA_inverse_falling_hold: "WTA_V36_INCUMBENT_RISING_SIDE_ONLY_DEEPER_OF_TRAILING_PULSE_FLOOR_AND_CAUSAL_RUNNING_OWN_REACH_LOW", sanity_bound: "EVERY_REST_STRICTLY_BELOW_CURRENT_BEST_ASK", take_path: "V36_MATURE_FLOOR_TAKE_INTACT", pair_cap: "99_MINUS_FIRST_FILL", clocks_as_decision_inputs: [], hard_prebell_edge: "V36_WINDOW1_SPAN_804_UNCHANGED" }, acceptance_bar: { completed_pairs_min: 270, LE_93_min: 12, LE_95_min: 24 }, fill_rulers: { market_scoring: "UNION_REACH_CHANNELS_QUOTE_TOUCH_10S_SIZE5_PLUS_TRADED_AT_LEVEL_PLUS_STRICT_PRINT_CROSS", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST_PLUS_PROVEN_TAKER", never_swapped: true } }
    : isV39
    ? { schema_version: "window1-v39-corrected-placement-stack-control-v1", base: V36_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [COUNTERFACTUAL_COMMIT, "2c54d724186d2f8b152205379aef88499c457a7a", FALLER_ANATOMY_COMMIT], architecture: { causal_direction: "DECISION_TIME_QUOTE_PATH_PLUS_JUL6_PRESSURE_AGREEMENT_WEIGHTED; OPPOSED_DIRECTIONAL_VOTES_SETTLE; NO_EX_POST_LABEL_INPUT", persistent_level_join: `RISING_CURRENT_BID_RESIDENCY_GE_${policy.PERSISTENT_LEVEL_SECONDS}S_AND_SELLER_HIT_AT_LEVEL_THEN_REST_AT_LEVEL`, WTA_inverse_falling_hold: "WTA_RISING_SIDE_ONLY_DEEPER_OF_TRAILING_PULSE_FLOOR_AND_CAUSAL_RUNNING_OWN_REACH_LOW", sanity_bound: "EVERY_REST_STRICTLY_BELOW_CURRENT_BEST_ASK", take_path: "V36_MATURE_FLOOR_TAKE_INTACT", pair_cap: "99_MINUS_FIRST_FILL", clocks_as_decision_inputs: [], hard_prebell_edge: "V36_WINDOW1_SPAN_804_UNCHANGED" }, fill_rulers: { market_scoring: "UNION_REACH_CHANNELS_QUOTE_TOUCH_10S_SIZE5_PLUS_TRADED_AT_LEVEL_PLUS_STRICT_PRINT_CROSS", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST_PLUS_PROVEN_TAKER", never_swapped: true } }
    : { schema_version: "window1-v38-maker-only-control-v1", parent: GAP_COMMIT, frozen_V36: V36_COMMIT, frozen_union_reach: REACH_COMMIT, sealed_divot_census: DIVOT_COMMIT, architecture: { entry_actions: ["PLACE_REST", "REPRICE_REST"], take_path: "REMOVED_FROM_POLICY_SOURCE_NOT_GATED", FALLING: "V36_NO_CHASE_WALKING_REST_UNCHANGED", RISING: `REST_AT_LOWEST_ASK_LEVEL_WITH_AT_LEAST_${policy.PULSE_REVISIT_MIN}_DISTINCT_VISITS_INSIDE_EXISTING_${policy.LOOKBACK_SECONDS}S_RECEIPT_HORIZON; POST_ONLY_REQUIRES_STANDING_ASK_ABOVE_NEW_REST`, SETTLED: "BID_MINUS_ONE_TRACKING", pair_cap: "99_MINUS_FIRST_FILL", clocks_as_decision_inputs: [], hard_prebell_edge: "V36_WINDOW1_SPAN_804_UNCHANGED" }, fill_rulers: { market_scoring: "UNION_REACH_CHANNELS_QUOTE_TOUCH_10S_SIZE5_PLUS_TRADED_AT_LEVEL_PLUS_STRICT_PRINT_CROSS", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST", never_swapped: true } };
  const pulseBinding = { commit: DIVOT_COMMIT, path: ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_DIVOT_CENSUS.json", source_sha256: fileHash(path.join(reachRoot, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_DIVOT_CENSUS.json")), adopted: { ask_side_dwell_10s_depth_median_cents: 1, ask_side_dwell_10s_depth_p90_cents: 2, trailing_horizon_seconds: policy.LOOKBACK_SECONDS, minimum_distinct_level_visits: policy.PULSE_REVISIT_MIN }, causal_revisit_definition: "ASK_LEVEL_ENTRY_AFTER_A_DIFFERENT_PRIOR_ASK; UNCHANGED RECORDER SNAPSHOTS DO_NOT INCREMENT VISITS" };
  const directionTelemetry = isV39 ? classifierTelemetry(marketEvents) : null;
  const counterPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/PLACEMENT_LAW_COUNTERFACTUAL_V2.json";
  const counterBytes = isPlacementStack ? gitShow(COUNTERFACTUAL_COMMIT, counterPath) : null;
  const counterReceipt = isPlacementStack ? JSON.parse(counterBytes) : null;
  const anatomyPath = ".claude/window1_live_v4_replay/v36_faller_side_mirror_anatomy_20260807/FALLER_ISSUE_ANATOMY_399.jsonl.gz";
  const anatomyBytes = isV39 ? gitShow(FALLER_ANATOMY_COMMIT, anatomyPath) : null;
  const anatomyMislabels = isV39 ? readRowsBytes(anatomyBytes).filter((row) => row.miss_taxonomy?.class === "STATE_MISLABELED") : [];
  const marketLegByIdentity = new Map(marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
  const reconstructedRecovery = anatomyMislabels.map((row) => {
    const identity = `${row.event_id}|${row.leg_id}`, leg = marketLegByIdentity.get(identity);
    return { event_id: row.event_id, leg_identity: identity, frozen_ex_post_direction: String(row.miss_taxonomy.reason).split(" was ").at(-1), v36_credited: row.v36_credited, v36_entry_cents: row.v36_entry_cents, union_reach_cents: row.reach_bottom_cents, v39_credited: Boolean(leg?.credited), v39_entry_cents: leg?.entry_cents ?? null, recovered_at_or_better_than_reach: Boolean(leg?.credited && Number.isInteger(row.reach_bottom_cents) && leg.entry_cents <= row.reach_bottom_cents) };
  });
  const mislabelRecovery = isV39 ? { controlling_counterfactual_denominator: counterReceipt.faller_mislabel.measured_ran_faller_on_nonfaller, controlling_counterfactual_forfeited: counterReceipt.faller_mislabel.forfeited, controlling_counterfactual_credited: counterReceipt.faller_mislabel.credited, identity_binding_status: "NOT_BOUND_IN_2B45D146_AGGREGATE_RECEIPT_SO_NO_FALSE_115_SIDE_NUMERATOR_IS_EMITTED", independently_reconstructable_c396_cohort: { sides: reconstructedRecovery.length, recovered_credited: reconstructedRecovery.filter((row) => row.v39_credited && !row.v36_credited).length, recovered_at_or_better_than_reach: reconstructedRecovery.filter((row) => row.recovered_at_or_better_than_reach && !row.v36_credited).length }, telemetry_law: "FROZEN_EX_POST_DIRECTION_USED_ONLY_AFTER_REPLAY; NEVER_PASSED_TO_POLICY" } : null;
  const marketLegs = marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => ({ ...leg, category: event.category, bell_confidence: event.bell_confidence })));
  const sanity = isPlacementStack ? { legs: marketLegs.length, bound_application_receipts: marketLegs.reduce((sum, leg) => sum + leg.sanity_bound_rows, 0), post_decision_rest_at_or_above_ask_violations: marketLegs.reduce((sum, leg) => sum + leg.sanity_violation_rows, 0), legs_with_violation: marketLegs.filter((leg) => leg.sanity_violation_rows > 0).length, violations_by_category_x_bell_confidence: countBy(marketLegs.filter((leg) => leg.sanity_violation_rows > 0), (leg) => `${leg.category}|${leg.bell_confidence}`) } : null;
  const v36Comparison = isPlacementStack ? { frozen_commit: V36_COMMIT, frozen_gross_score: v36Score, frozen_net_of_taker_fee_score: v36NetScore, V41_maker_fee: isMaker41 ? { maker_fills_fee_exempt: true, taker_fills: 0, total_entry_fees_cents: 0, net_equals_gross: true } : null, causal_reach_reference: isMaker41 ? { commit: CAUSAL_REACH_COMMIT, under_par: causalReachReceipt.CAUSAL_REACH.under_par, locked_cents: causalReachReceipt.CAUSAL_REACH.locked } : null, reach_answer_key_grade_from_b581cbb: { matched: 52, shallow: 212, one_missing: 486, both_missing: 35, no_reach: 19, completed_on_637_answer_key: 264 }, [`${variant.toUpperCase()}_market_union_reach`]: marketScore, [`${variant.toUpperCase()}_strict_build_verification`]: strictScore } : null;
  const strictLegByIdentity = new Map(strictEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
  const joinRows = (isV40 || isMaker41) ? marketLegs.filter((leg) => Number.isInteger(leg.persistent_join_level)).map((leg) => {
    const strictLeg = strictLegByIdentity.get(leg.leg_identity);
    return {
      event_id: leg.event_id,
      leg_identity: leg.leg_identity,
      category: leg.category,
      bell_confidence: leg.bell_confidence,
      incumbent_state_at_terminal_decision: leg.last_combined_state,
      join_level_cents: leg.persistent_join_level,
      join_timestamp_epoch: leg.persistent_join_timestamp_epoch,
      join_receipt: leg.persistent_join_receipt,
      trigger_evidence_receipt: leg.persistent_join_evidence_receipt,
      all_book_last_trade_at_level_receipts: leg.persistent_join_book_last_trade_receipts,
      all_certified_seller_aggressed_prints_at_level: leg.persistent_join_certified_seller_aggressed_prints,
      post_join_book_last_trade_at_level_receipts: leg.post_join_book_last_trade_receipts,
      post_join_certified_seller_aggressed_prints_at_level: leg.post_join_certified_seller_hits_at_level,
      market_credited: leg.credited,
      market_entry_cents: leg.entry_cents,
      market_fill_timestamp_epoch: leg.fill_timestamp_epoch,
      market_fill_class: leg.fill_class,
      strict_credited: Boolean(strictLeg?.credited),
      strict_entry_cents: strictLeg?.entry_cents ?? null,
      strict_fill_timestamp_epoch: strictLeg?.fill_timestamp_epoch ?? null,
      strict_fill_class: strictLeg?.fill_class ?? null,
    };
  }).sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_identity.localeCompare(b.leg_identity)) : [];
  const joinReceipt = (isV40 || isMaker41) ? {
    join_legs: joinRows.length,
    market_credited_after_join: joinRows.filter((row) => row.market_credited && row.market_fill_timestamp_epoch > row.join_timestamp_epoch).length,
    strict_credited_after_join: joinRows.filter((row) => row.strict_credited && row.strict_fill_timestamp_epoch > row.join_timestamp_epoch).length,
    post_join_certified_seller_hit_distribution: distribution(joinRows.map((row) => row.post_join_certified_seller_aggressed_prints_at_level)),
    post_join_book_last_trade_receipt_distribution: distribution(joinRows.map((row) => row.post_join_book_last_trade_at_level_receipts)),
    zero_post_join_certified_seller_hits: joinRows.filter((row) => row.post_join_certified_seller_aggressed_prints_at_level === 0).length,
    by_category_x_bell_confidence: countBy(joinRows, (row) => `${row.category}|${row.bell_confidence}`),
    BOSCOP_COP: joinRows.find((row) => row.leg_identity.endsWith("BOSCOP|COP")) || null,
  } : null;
  const acceptance = isV40 ? { completed_pairs: { value: marketScore.completed_pairs, minimum: 270, pass: marketScore.completed_pairs >= 270 }, LE_93: { value: marketScore.frontier.LE_93, minimum: 12, pass: marketScore.frontier.LE_93 >= 12 }, LE_95: { value: marketScore.frontier.LE_95, minimum: 24, pass: marketScore.frontier.LE_95 >= 24 } } : null;
  if (acceptance) acceptance.pass = Object.values(acceptance).filter((row) => row && typeof row === "object" && "pass" in row).every((row) => row.pass);
  const v39TelemetryPath = ".claude/window1_live_v4_replay/v39_corrected_placement_stack_20260807/CAUSAL_DIRECTION_CLASSIFIER_TELEMETRY.json";
  const classifierResearchOpen = isV40 ? {
    status: "CLASSIFIER_RESEARCH_OPEN",
    V39_package_commit: "ff5880d11a88b0d12415f5371d7cbb61331957e4",
    V39_telemetry_path: v39TelemetryPath,
    V39_telemetry_sha256: fileHash(path.join(repo, v39TelemetryPath)),
    V39_reach_moment_accuracy: JSON.parse(fs.readFileSync(path.join(repo, v39TelemetryPath), "utf8")).aggregate.reach_moment_accuracy,
    ruling: "NO_BUILD_MAY_GATE_ON_A_NEW_DIRECTION_READ_UNTIL_IT_VALIDATES_ABOVE_THE_INCUMBENT_ON_HELD_OUT_LEGS",
    V40_policy_imports_V39: false,
    V40_state_combiner_identity: policy.combineState === require("./window1_v36_state_directional_rest_mature_floor.js").combineState,
  } : null;
  if (classifierResearchOpen) ensure(classifierResearchOpen.V40_state_combiner_identity, "V40 does not inherit V36 state combiner");
  const namedCausality = isV39 ? {
    controlling_counterfactual: {
      commit: COUNTERFACTUAL_COMMIT,
      ruler: counterReceipt.ruler,
      warning: "THE COUNTERFACTUAL CREDITS UNION REACH AT THE REST LEVEL WITHOUT REQUIRING A STRICTLY LATER CAUSAL RECEIPT; V39 DOES NOT RETRO-CREDIT THAT HINDSIGHT CONVENTION",
    },
    ARNROM: {
      ordered_target: "ARN joins 50; pair 89",
      result: named.ARNROM.MARKET_UNION_REACH,
      adjudication: named.ARNROM.MARKET_UNION_REACH.completed && named.ARNROM.MARKET_UNION_REACH.combined_entry_cents === 89 ? "PASS" : "FAIL",
    },
    BOSCOP: {
      ordered_target: "COP joins 47; pair 77",
      result: named.BOSCOP.MARKET_UNION_REACH,
      adjudication: named.BOSCOP.MARKET_UNION_REACH.completed && named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents === 77 ? "PASS" : "FAIL_CLOSED_NO_STRICTLY_LATER_UNION_REACH_AFTER_CAUSAL_JOIN",
      explanation: "COP causally joined 47 only after the persistent-level seller-hit receipt. No later quote-touch, traded-at-level, or print-cross receipt reached that resting order before the hard edge, so pair 77 is not credited.",
    },
    WESPAA: { role: "CAUSAL_CLASSIFIER_TEST_CASE", result: named.WESPAA.MARKET_UNION_REACH },
    NIKVRB: { role: "NEGATIVE_CONTROL_PERSISTENT_JOIN_DOES_NOT_OVERRIDE_PULSE_OR_INCUMBENT_PATH", result: named.NIKVRB.MARKET_UNION_REACH },
    GANJAN: { role: "NAMED_DAMAGE_REGRESSION", result: named.GANJAN.MARKET_UNION_REACH },
  } : null;
  const namedV40 = isV40 ? {
    ARNROM: { ordered: "ARN joins 50; pair 89", result: named.ARNROM.MARKET_UNION_REACH, pass: named.ARNROM.MARKET_UNION_REACH.completed && named.ARNROM.MARKET_UNION_REACH.combined_entry_cents === 89 },
    BOSCOP: { ordered: "REPORT_TRIGGER_LATENESS_BOUNDARY", result: named.BOSCOP.MARKET_UNION_REACH, COP_join_evidence: joinReceipt.BOSCOP_COP, boundary: joinReceipt.BOSCOP_COP?.post_join_certified_seller_aggressed_prints_at_level > 0 ? "LATER_CERTIFIED_HIT_EXISTS" : "NO_LATER_CERTIFIED_SELLER_HIT_AFTER_JOIN" },
    WESPAA: { ordered: "EXPECT_V36_BEHAVIOR_CLASSIFIER_SEVERED", result: named.WESPAA.MARKET_UNION_REACH },
    NIKVRB: { ordered: "NEGATIVE_CONTROL", result: named.NIKVRB.MARKET_UNION_REACH },
  } : null;
  const namedV41 = isV41 ? {
    ordered: { ARNROM: "maker rests should approach ARN~50 plus ROM38=88; report causal truth without retro-credit", BOSCOP: "named maker machine regression", NIKVRB: "named pulse/tracker regression", WESPAA: "named empty/forfeit regression", KRUFER: "named placement-stack regression" },
    ARNROM: {
      result: named.ARNROM.MARKET_UNION_REACH,
      exact_rest_and_fill_sequence: allActions.filter((row) => row.mode === "MARKET_UNION_REACH" && row.event_id.includes("ARNROM") && ["PLACE_REST", "REPRICE_REST", "PAIR_ARM", "PAIR_CAP_REPRICE", "FILL"].includes(row.kind)),
      observed_combined_entry_cents: named.ARNROM.MARKET_UNION_REACH.combined_entry_cents,
      near_88: Number.isInteger(named.ARNROM.MARKET_UNION_REACH.combined_entry_cents) && named.ARNROM.MARKET_UNION_REACH.combined_entry_cents <= 90,
      no_fabricated_target_credit: true,
    },
    BOSCOP: named.BOSCOP,
    NIKVRB: named.NIKVRB,
    WESPAA: named.WESPAA,
    KRUFER: named.KRUFER,
  } : null;
  const v42GuardLegs = hasDeepGap ? marketLegs.filter((leg) => leg.deep_gap_withhold_episodes > 0).map((leg) => ({ event_id: leg.event_id, leg_identity: leg.leg_identity, category: leg.category, bell_confidence: leg.bell_confidence, guard_evaluations: leg.deep_gap_guard_evaluations, withheld_evaluations: leg.deep_gap_withheld_evaluations, withhold_episodes: leg.deep_gap_withhold_episodes, lifts: leg.deep_gap_lifts, first_withhold: leg.deep_gap_first_withhold, last_withhold: leg.deep_gap_last_withhold, last_lift: leg.deep_gap_last_lift, credited: leg.credited, entry_cents: leg.entry_cents, terminal_reason: leg.terminal_reason })).sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_identity.localeCompare(b.leg_identity)) : [];
  const v42GuardActions = hasDeepGap ? allActions.filter((row) => row.mode === "MARKET_UNION_REACH" && String(row.kind).startsWith("DEEP_GAP_")) : [];
  const v45ReleasedRestLedger = isV45 ? (() => {
    const baselineByEvent = new Map(machineRuns.get("V43_BASELINE").marketEvents.map((event) => [event.event_id, event]));
    const rows = marketEvents.flatMap((event) => Object.values(event.legs).filter((leg) => leg.post_credit_guard_releases > 0).map((leg) => {
      const release = leg.post_credit_guard_release, baselineEvent = baselineByEvent.get(event.event_id), baselineLeg = baselineEvent.legs[leg.leg_id];
      const sibling = Object.values(event.legs).find((candidate) => candidate.leg_identity === release.credited_sibling_leg_identity);
      return { event_id: event.event_id, category: event.category, bell_confidence: event.bell_confidence, released_leg_identity: leg.leg_identity, credited_sibling_leg_identity: release.credited_sibling_leg_identity, sibling_entry_cents: release.sibling_entry_cents, fixed_pair_cap_cents: release.fixed_pair_cap_cents, release_timestamp_epoch: release.timestamp_epoch, t_minus_scheduled_seconds: release.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: release.t_minus_actual_bell_seconds, release_receipt: release.receipt, mechanism: release.mechanism || "ACTIVE_WITHHOLD_TERMINATED_AT_SIBLING_CREDIT", own_book_receipt: release.own_book_receipt, own_book: release.own_book, released_rest_cents: release.order_after_cents, reapplication_prevented_receipts: leg.post_credit_guard_reapplication_prevented_receipts, filled_after_release: leg.credited && leg.fill_timestamp_epoch >= release.timestamp_epoch, fill_cents: leg.entry_cents, fill_timestamp_epoch: leg.fill_timestamp_epoch, fill_class: leg.fill_class, pair_completed: event.completed_pair, combined_entry_cents: event.combined_entry_cents, pair_under_par: event.pair_under_par, sibling_stayed_credited: Boolean(sibling?.credited), V43_baseline: { released_leg_credited: baselineLeg.credited, released_leg_entry_cents: baselineLeg.entry_cents, pair_completed: baselineEvent.completed_pair, combined_entry_cents: baselineEvent.combined_entry_cents }, completion_gained_vs_V43: event.completed_pair && !baselineEvent.completed_pair, new_exposure_vs_V43: !event.completed_pair && Object.values(event.legs).filter((candidate) => candidate.credited).length > Object.values(baselineEvent.legs).filter((candidate) => candidate.credited).length, terminal_reason: leg.terminal_reason };
    })).sort((a, b) => a.event_id.localeCompare(b.event_id) || a.released_leg_identity.localeCompare(b.released_leg_identity));
    return { rows, summary: { released_rests: rows.length, active_withholds_terminated_at_credit: rows.filter((row) => row.mechanism === "ACTIVE_WITHHOLD_TERMINATED_AT_SIBLING_CREDIT").length, future_reapplications_prevented: rows.filter((row) => row.mechanism === "POST_CREDIT_GUARD_REAPPLICATION_PREVENTED").length, released_and_filled: rows.filter((row) => row.filled_after_release).length, released_unfilled: rows.filter((row) => !row.filled_after_release).length, two_columns: { pairs_completed: { events: rows.filter((row) => row.completion_gained_vs_V43).length, identities: rows.filter((row) => row.completion_gained_vs_V43).map((row) => row.event_id) }, new_exposure: { events: rows.filter((row) => row.new_exposure_vs_V43).length, identities: rows.filter((row) => row.new_exposure_vs_V43).map((row) => row.event_id) } }, by_category: countBy(rows, (row) => row.category), conservation: { rows: rows.length, filled_plus_unfilled: rows.filter((row) => row.filled_after_release).length + rows.filter((row) => !row.filled_after_release).length, pass: rows.length === rows.filter((row) => row.filled_after_release).length + rows.filter((row) => !row.filled_after_release).length } } };
  })() : null;
  const v41ActionRows = hasDeepGap ? readRows(path.join(repo, ".claude/window1_live_v4_replay/v41_maker_machine_20260808/ACTION_TRACE.jsonl.gz")).filter((row) => row.mode === "MARKET_UNION_REACH") : [];
  const normalizedAction = (row) => ({ kind: row.kind, event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, target_cents: row.target_cents ?? null, entry_cents: row.entry_cents ?? null, pair_cap_cents: row.pair_cap_cents ?? null, reason: row.reason ?? null, fill_class: row.fill_class ?? null });
  const actionStreams = (rows) => {
    const map = new Map();
    for (const row of rows.filter((item) => !String(item.kind).startsWith("DEEP_GAP_") && !["GAP_CREDIT_AUTHORIZED", "GAP_CREDIT_REFUSED"].includes(item.kind))) { if (!map.has(row.leg_identity)) map.set(row.leg_identity, []); map.get(row.leg_identity).push(normalizedAction(row)); }
    return map;
  };
  const v42Differential = hasDeepGap ? (() => {
    const prior = actionStreams(v41ActionRows), next = actionStreams(allActions.filter((row) => row.mode === "MARKET_UNION_REACH")), changed = [], unchanged = [];
    for (const identity of marketLegs.map((leg) => leg.leg_identity).sort()) {
      const priorBytes = canonical(prior.get(identity) || []), nextBytes = canonical(next.get(identity) || []);
      const row = { leg_identity: identity, V41_action_stream_sha256: shaBytes(priorBytes), V42_action_stream_sha256: shaBytes(nextBytes), byte_identical: priorBytes === nextBytes };
      (row.byte_identical ? unchanged : changed).push(row);
    }
    return { frozen_V41_commit: V41_COMMIT, compared_leg_streams: 1608, changed_leg_streams: changed.length, unchanged_leg_streams: unchanged.length, changed, unchanged_aggregate_sha256: shaBytes(canonical(unchanged)), conservation: { sum: changed.length + unchanged.length, expected: 1608, pass: changed.length + unchanged.length === 1608 } };
  })() : null;
  const v45Differential = isV45 ? (() => {
    const priorRows = machineRuns.get("V43_BASELINE").actions.filter((row) => row.mode === "MARKET_UNION_REACH"), nextRows = machineRuns.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT").actions.filter((row) => row.mode === "MARKET_UNION_REACH");
    const prior = actionStreams(priorRows), next = actionStreams(nextRows), changed = [], unchanged = [];
    for (const identity of marketLegs.map((leg) => leg.leg_identity).sort()) {
      const priorBytes = canonical(prior.get(identity) || []), nextBytes = canonical(next.get(identity) || []);
      const row = { leg_identity: identity, V43_action_stream_sha256: shaBytes(priorBytes), V45_action_stream_sha256: shaBytes(nextBytes), byte_identical: priorBytes === nextBytes };
      (row.byte_identical ? unchanged : changed).push(row);
    }
    return { frozen_V43_commit: V43_COMMIT, compared_leg_streams: 1608, changed_leg_streams: changed.length, unchanged_leg_streams: unchanged.length, changed, unchanged_aggregate_sha256: shaBytes(canonical(unchanged)), conservation: { sum: changed.length + unchanged.length, expected: 1608, pass: changed.length + unchanged.length === 1608 } };
  })() : null;
  const v46Differential = isV46 ? (() => {
    const priorRows = machineRuns.get("V45_BASELINE").actions.filter((row) => row.mode === "MARKET_UNION_REACH"), nextRows = machineRuns.get("V46_PAIR_GATED_GAP_CREDIT").actions.filter((row) => row.mode === "MARKET_UNION_REACH");
    const prior = actionStreams(priorRows), next = actionStreams(nextRows), changed = [], unchanged = [];
    for (const identity of marketLegs.map((leg) => leg.leg_identity).sort()) {
      const priorBytes = canonical(prior.get(identity) || []), nextBytes = canonical(next.get(identity) || []);
      const row = { leg_identity: identity, V45_action_stream_sha256: shaBytes(priorBytes), V46_action_stream_sha256: shaBytes(nextBytes), byte_identical: priorBytes === nextBytes };
      (row.byte_identical ? unchanged : changed).push(row);
    }
    return { frozen_V45_commit: V45_COMMIT, compared_leg_streams: 1608, changed_leg_streams: changed.length, unchanged_leg_streams: unchanged.length, changed, unchanged_aggregate_sha256: shaBytes(canonical(unchanged)), conservation: { sum: changed.length + unchanged.length, expected: 1608, pass: changed.length + unchanged.length === 1608 } };
  })() : null;
  const v47Differential = isV47 ? (() => {
    const priorRows = machineRuns.get("V45_BASELINE").actions.filter((row) => row.mode === "MARKET_UNION_REACH"), nextRows = machineRuns.get("V47_SAME_TICK_ARM").actions.filter((row) => row.mode === "MARKET_UNION_REACH");
    const prior = actionStreams(priorRows), next = actionStreams(nextRows), changed = [], unchanged = [];
    for (const identity of marketLegs.map((leg) => leg.leg_identity).sort()) {
      const priorBytes = canonical(prior.get(identity) || []), nextBytes = canonical(next.get(identity) || []);
      const row = { leg_identity: identity, V45_action_stream_sha256: shaBytes(priorBytes), V47_action_stream_sha256: shaBytes(nextBytes), byte_identical: priorBytes === nextBytes };
      (row.byte_identical ? unchanged : changed).push(row);
    }
    return { frozen_V45_commit: V45_COMMIT, compared_leg_streams: 1608, changed_leg_streams: changed.length, unchanged_leg_streams: unchanged.length, changed, unchanged_aggregate_sha256: shaBytes(canonical(unchanged)), conservation: { sum: changed.length + unchanged.length, expected: 1608, pass: changed.length + unchanged.length === 1608 } };
  })() : null;
  const v47SegCFootprint = isV47 ? (() => {
    const priorRun = machineRuns.get("V45_BASELINE"), nextRun = machineRuns.get("V47_SAME_TICK_ARM");
    const keyOf = (row) => `${row.mode}|${row.event_id}|${row.leg_identity}|${row.qualification_receipt}|${row.qualification_level_cents}`;
    const actionIndex = (actions) => {
      const index = new Map();
      for (const row of actions) {
        if (!["PLACE_REST", "REPRICE_REST"].includes(row.kind)) continue;
        const key = `${row.mode}|${row.leg_identity}|${row.target_cents}`;
        if (!index.has(key)) index.set(key, []);
        index.get(key).push(row);
      }
      for (const values of index.values()) values.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
      return index;
    };
    const priorActions = actionIndex(priorRun.actions), nextActions = actionIndex(nextRun.actions);
    const postFor = (qualification, index) => {
      if (qualification.disposition === "ALREADY_RESTING_AT_QUALIFIED_LEVEL") return { timestamp_epoch: qualification.qualification_timestamp_epoch, receipt: qualification.qualification_receipt, latency_seconds: 0, disposition: qualification.disposition };
      const candidates = index.get(`${qualification.mode}|${qualification.leg_identity}|${qualification.qualification_level_cents}`) || [];
      let low = 0, high = candidates.length;
      while (low < high) {
        const middle = (low + high) >>> 1;
        if (candidates[middle].timestamp_epoch < qualification.qualification_timestamp_epoch) low = middle + 1;
        else high = middle;
      }
      const hit = candidates[low];
      return hit ? { timestamp_epoch: hit.timestamp_epoch, receipt: hit.receipt, latency_seconds: hit.timestamp_epoch - qualification.qualification_timestamp_epoch, disposition: hit.timestamp_epoch === qualification.qualification_timestamp_epoch && hit.receipt === qualification.qualification_receipt ? "POSTED_ON_QUALIFYING_RECEIPT" : "POSTED_LATER_AFTER_UNCHANGED_LAW" } : { timestamp_epoch: null, receipt: null, latency_seconds: null, disposition: qualification.disposition };
    };
    const priorByKey = new Map(priorRun.joinQualifications.map((row) => [keyOf(row), row]));
    const nextByKey = new Map(nextRun.joinQualifications.map((row) => [keyOf(row), row]));
    ensure(priorByKey.size === priorRun.joinQualifications.length && nextByKey.size === nextRun.joinQualifications.length, "duplicate SEG_C qualification key");
    ensure(priorByKey.size === nextByKey.size && [...priorByKey.keys()].every((key) => nextByKey.has(key)), "V45/V47 deep-join qualification set changed");
    const priorMarket = new Map(priorRun.marketEvents.map((event) => [event.event_id, event])), nextMarket = new Map(nextRun.marketEvents.map((event) => [event.event_id, event]));
    const aggregates = new Map();
    const totals = { V45_zero_qualification_to_post_rows: 0, V47_zero_qualification_to_post_rows: 0, V45_positive_qualification_to_post_rows: 0, V47_positive_qualification_to_post_rows: 0, V45_positive_scheduler_latency_rows: 0, V47_positive_scheduler_latency_rows: 0, unchanged_law_no_post_rows: 0 };
    for (const [key, prior] of priorByKey) {
      const next = nextByKey.get(key), V45 = postFor(prior, priorActions), V47 = postFor(next, nextActions), groupKey = `${prior.mode}|${prior.leg_identity}`;
      if (!aggregates.has(groupKey)) {
        const priorEvent = priorMarket.get(prior.event_id), nextEvent = nextMarket.get(prior.event_id), legId = prior.leg_identity.split("|").at(-1), priorLeg = priorEvent.legs[legId], nextLeg = nextEvent.legs[legId];
        aggregates.set(groupKey, { key: groupKey, event_id: prior.event_id, leg_identity: prior.leg_identity, category: prior.category, price_region: prior.price_region, bell_confidence: prior.bell_confidence, mode: prior.mode, qualification_rows: 0, first_qualification: null, last_qualification: null, levels_cents: new Set(), V45_latencies: [], V47_latencies: [], V45_dispositions: {}, V47_dispositions: {}, V45_positive_scheduler_latency_rows: 0, V47_positive_scheduler_latency_rows: 0, V45_outcome: prior.mode === "MARKET_UNION_REACH" ? { leg_credited: priorLeg.credited, leg_entry_cents: priorLeg.entry_cents, pair_completed: priorEvent.completed_pair, combined_entry_cents: priorEvent.combined_entry_cents } : null, V47_outcome: prior.mode === "MARKET_UNION_REACH" ? { leg_credited: nextLeg.credited, leg_entry_cents: nextLeg.entry_cents, pair_completed: nextEvent.completed_pair, combined_entry_cents: nextEvent.combined_entry_cents } : null, outcome_changed: prior.mode === "MARKET_UNION_REACH" && (priorLeg.credited !== nextLeg.credited || priorLeg.entry_cents !== nextLeg.entry_cents || priorEvent.completed_pair !== nextEvent.completed_pair || priorEvent.combined_entry_cents !== nextEvent.combined_entry_cents) });
      }
      const aggregate = aggregates.get(groupKey), qualification = { timestamp_epoch: prior.qualification_timestamp_epoch, receipt: prior.qualification_receipt, level_cents: prior.qualification_level_cents, residency_seconds: prior.residency_seconds };
      aggregate.qualification_rows += 1;
      aggregate.first_qualification ||= qualification;
      aggregate.last_qualification = qualification;
      aggregate.levels_cents.add(prior.qualification_level_cents);
      if (Number.isFinite(V45.latency_seconds)) aggregate.V45_latencies.push(V45.latency_seconds);
      if (Number.isFinite(V47.latency_seconds)) aggregate.V47_latencies.push(V47.latency_seconds);
      aggregate.V45_dispositions[V45.disposition] = (aggregate.V45_dispositions[V45.disposition] || 0) + 1;
      aggregate.V47_dispositions[V47.disposition] = (aggregate.V47_dispositions[V47.disposition] || 0) + 1;
      if (V45.latency_seconds === 0) totals.V45_zero_qualification_to_post_rows += 1;
      if (V47.latency_seconds === 0) totals.V47_zero_qualification_to_post_rows += 1;
      if (Number.isFinite(V45.latency_seconds) && V45.latency_seconds > 0) totals.V45_positive_qualification_to_post_rows += 1;
      if (Number.isFinite(V47.latency_seconds) && V47.latency_seconds > 0) totals.V47_positive_qualification_to_post_rows += 1;
      if (Number.isFinite(prior.scheduler_latency_seconds) && prior.scheduler_latency_seconds > 0) { totals.V45_positive_scheduler_latency_rows += 1; aggregate.V45_positive_scheduler_latency_rows += 1; }
      if (Number.isFinite(next.scheduler_latency_seconds) && next.scheduler_latency_seconds > 0) { totals.V47_positive_scheduler_latency_rows += 1; aggregate.V47_positive_scheduler_latency_rows += 1; }
      if (V47.timestamp_epoch === null) totals.unchanged_law_no_post_rows += 1;
    }
    const rows = [...aggregates.values()].map((row) => ({ ...row, levels_cents: [...row.levels_cents].sort((a, b) => a - b), V45: { qualification_to_post_latency_seconds: distribution(row.V45_latencies), disposition_counts: row.V45_dispositions, positive_scheduler_latency_rows: row.V45_positive_scheduler_latency_rows }, V47: { qualification_to_post_latency_seconds: distribution(row.V47_latencies), disposition_counts: row.V47_dispositions, positive_scheduler_latency_rows: row.V47_positive_scheduler_latency_rows }, V45_latencies: undefined, V47_latencies: undefined, V45_dispositions: undefined, V47_dispositions: undefined, V45_positive_scheduler_latency_rows: undefined, V47_positive_scheduler_latency_rows: undefined })).sort((a, b) => a.mode.localeCompare(b.mode) || a.event_id.localeCompare(b.event_id) || a.leg_identity.localeCompare(b.leg_identity));
    const outcomeChanged = rows.filter((row) => row.outcome_changed);
    const summary = { qualification_rows: priorRun.joinQualifications.length, deep_join_legs: rows.length, by_mode: countBy(priorRun.joinQualifications, (row) => row.mode), ...totals, outcome_changed_rows: outcomeChanged.length, outcome_changed_events: [...new Set(outcomeChanged.map((row) => row.event_id))].sort(), SURECH: rows.filter((row) => row.event_id.includes("SURECH")), evidence_ruling: "8877c2d5_IS_AN_OLDER_L4_ARCHETYPE_RENDER_NOT_A_V45_TRACE; EXECUTABLE_V45_ALREADY_POSTS_JOIN_CHANGES_ON_THE_QUALIFYING_RECEIPT", latency_ruling: "QUALIFICATION_TO_POST_DELAY_FROM_UNCHANGED_GUARDS_IS_NOT_SCHEDULER_LATENCY", footprint_grain: "ONE_ROW_PER_MODE_AND_DEEP_JOIN_LEG", conservation: { V45_qualifications: priorRun.joinQualifications.length, V47_qualifications: nextRun.joinQualifications.length, qualification_assignment_sum: rows.reduce((sum, row) => sum + row.qualification_rows, 0), ledger_rows: rows.length, expected_ledger_rows: aggregates.size, pass: priorRun.joinQualifications.length === nextRun.joinQualifications.length && rows.reduce((sum, row) => sum + row.qualification_rows, 0) === priorRun.joinQualifications.length && rows.length === aggregates.size } };
    return { rows, summary };
  })() : null;
  const v46GapLedger = isV46 ? (() => {
    const baselineByEvent = new Map(machineRuns.get("V45_BASELINE").marketEvents.map((event) => [event.event_id, event]));
    const gapActions = allActions.filter((row) => row.mode === "MARKET_UNION_REACH" && row.kind === "GAP_CREDIT_REPRICE_DOWN");
    const rows = gapActions.map((action) => {
      const event = marketEvents.find((candidate) => candidate.event_id === action.event_id), baselineEvent = baselineByEvent.get(action.event_id), leg = Object.values(event.legs).find((candidate) => candidate.leg_identity === action.leg_identity), baselineLeg = Object.values(baselineEvent.legs).find((candidate) => candidate.leg_identity === action.leg_identity);
      const sibling = Object.values(event.legs).find((candidate) => candidate.leg_identity !== action.leg_identity);
      return { event_id: action.event_id, category: event.category, price_region: leg.price_region, leg_identity: action.leg_identity, timestamp_epoch: action.timestamp_epoch, t_minus_scheduled_seconds: action.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: action.t_minus_actual_bell_seconds, receipt: action.receipt, prior_ask_cents: action.gap_credit?.prior_ask_cents ?? null, current_ask_cents: action.gap_credit?.current_ask_cents ?? null, ask_gap_cents: action.gap_credit?.ask_gap_cents ?? null, order_after_cents: action.target_cents, sibling_credited_at_walk: true, sibling_entry_cents: action.gap_credit?.sibling_entry_cents ?? null, pair_cap_cents: action.gap_credit?.pair_cap_cents ?? null, leg_filled: leg.credited, leg_entry_cents: leg.entry_cents, fill_class: leg.fill_class, gap_credit_fill: leg.gap_credit_fill, pair_completed: event.completed_pair, combined_entry_cents: event.combined_entry_cents, pair_under_par: event.pair_under_par, falling_tail_depth_cents: leg.credited && Number.isInteger(leg.union_reach_cents) ? leg.entry_cents - leg.union_reach_cents : null, V45: { leg_credited: baselineLeg.credited, leg_entry_cents: baselineLeg.entry_cents, pair_completed: baselineEvent.completed_pair, combined_entry_cents: baselineEvent.combined_entry_cents }, completion_gained_vs_V45: event.completed_pair && !baselineEvent.completed_pair, new_exposure_vs_V45: !event.completed_pair && Object.values(event.legs).filter((candidate) => candidate.credited).length > Object.values(baselineEvent.legs).filter((candidate) => candidate.credited).length, sibling_stayed_credited: sibling.credited };
    }).sort((a, b) => a.event_id.localeCompare(b.event_id) || a.timestamp_epoch - b.timestamp_epoch || a.leg_identity.localeCompare(b.leg_identity));
    const changedEvents = new Set(rows.filter((row) => row.completion_gained_vs_V45).map((row) => row.event_id));
    const exposureEvents = new Set(rows.filter((row) => row.new_exposure_vs_V45).map((row) => row.event_id));
    const legRows = marketLegs.filter((leg) => leg.gap_credit_eligible_receipts > 0);
    return { rows, summary: { authorized_walks: rows.length, authorized_legs: new Set(rows.map((row) => row.leg_identity)).size, authorized_events: new Set(rows.map((row) => row.event_id)).size, authorized_walks_that_filled: rows.filter((row) => row.gap_credit_fill).length, eligible_legs: legRows.length, sibling_uncredited_refusal_receipts: legRows.reduce((sum, leg) => sum + leg.gap_credit_sibling_uncredited_refusals, 0), sibling_uncredited_refusal_legs: legRows.filter((leg) => leg.gap_credit_sibling_uncredited_refusals > 0).length, no_lawful_reprice_receipts: legRows.reduce((sum, leg) => sum + leg.gap_credit_no_lawful_reprice, 0), two_columns: { pairs_completed: { events: changedEvents.size, identities: [...changedEvents].sort() }, new_exposure: { events: exposureEvents.size, identities: [...exposureEvents].sort() } }, falling_tail_depth_cents: distribution(rows.filter((row) => row.gap_credit_fill).map((row) => row.falling_tail_depth_cents)), by_category: countBy(rows, (row) => row.category), conservation: { authorized_walk_rows: rows.length, leg_authorized_walk_sum: legRows.reduce((sum, leg) => sum + leg.gap_credit_authorized_walks, 0), pass: rows.length === legRows.reduce((sum, leg) => sum + leg.gap_credit_authorized_walks, 0) } } };
  })() : null;
  const namedV42 = isV42 ? (() => {
    const rowsFor = (label) => v42GuardActions.filter((row) => row.event_id.includes(label));
    const put = rowsFor("PUTJEA"), roc = rowsFor("ROCBUE"), kre = rowsFor("KREZHE"), bor = rowsFor("BORDIM");
    const putFingerprint = put.find((row) => row.leg_identity.endsWith("|JEA") && row.kind === "DEEP_GAP_WITHHOLD_START" && row.v41_target_cents === 64 && row.guard?.sibling_best_ask_cents === 93 && row.guard?.implied_sibling_cap_cents === 35) || null;
    const bordimDimWithholds = bor.filter((row) => row.leg_identity.endsWith("|DIM") && row.kind === "DEEP_GAP_WITHHOLD_START");
    return {
      PUTJEA: { ordered: "JEA_REST_64_WITHHELD_WHILE_PUT_ASK_93_AND_IMPLIED_CAP_35", fingerprint: putFingerprint, actions: put, result: named.PUTJEA },
      ROCBUE: { ordered: "DEEP_TAIL_LOSS_CASE", actions: roc, result: named.ROCBUE },
      KREZHE: { ordered: "DEEP_TAIL_LOSS_CASE", actions: kre, result: named.KREZHE },
      BORDIM: { ordered: "MARGINAL_GAP_ONE_CENT_MUST_NOT_BE_WITHHELD", DIM_withhold_starts: bordimDimWithholds.length, actions: bor, result: named.BORDIM },
      ARNROM: { role: "V41_REGRESSION", result: named.ARNROM },
      assertions: { PUTJEA_fingerprint_pass: Boolean(putFingerprint), ROCBUE_touched: roc.some((row) => row.kind === "DEEP_GAP_WITHHOLD_START"), KREZHE_touched: kre.some((row) => row.kind === "DEEP_GAP_WITHHOLD_START"), BORDIM_DIM_not_withheld: bordimDimWithholds.length === 0 },
    };
  })() : null;
  if (namedV42) {
    ensure(namedV42.assertions.PUTJEA_fingerprint_pass, "PUTJEA JEA 64/93/cap35 fingerprint did not fire");
    ensure(namedV42.assertions.ROCBUE_touched && namedV42.assertions.KREZHE_touched, "named deep-tail cases did not fire");
    ensure(namedV42.assertions.BORDIM_DIM_not_withheld, "BORDIM marginal DIM leg was withheld");
  }
  const namedV43 = isV43 ? (() => {
    const rowsFor = (label) => v42GuardActions.filter((row) => row.event_id.includes(label));
    const put = rowsFor("PUTJEA"), bor = rowsFor("BORDIM");
    const putFingerprint = put.find((row) => row.leg_identity.endsWith("|JEA") && row.kind === "DEEP_GAP_WITHHOLD_START" && row.v41_target_cents === 64 && row.guard?.sibling_best_ask_cents === 93 && row.guard?.implied_sibling_cap_cents === 35) || null;
    const bordimWithholds = bor.filter((row) => row.leg_identity.endsWith("|DIM") && row.kind === "DEEP_GAP_WITHHOLD_START");
    const observed = { KIRSEK: named.KIRSEK.MARKET_UNION_REACH.combined_entry_cents, ARNROM: named.ARNROM.MARKET_UNION_REACH.combined_entry_cents, KRUFER: named.KRUFER.MARKET_UNION_REACH.combined_entry_cents, BOSCOP: named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents };
    const assertions = { KIRSEK_47: observed.KIRSEK === 47, ARNROM_90: observed.ARNROM === 90, KRUFER_96: observed.KRUFER === 96, BOSCOP_94: observed.BOSCOP === 94, PUTJEA_fingerprint_pass: Boolean(putFingerprint), BORDIM_DIM_not_withheld: bordimWithholds.length === 0 };
    return { ordered: { KIRSEK: "COMPLETES_AT_47_KIR_APPROX_30_VIA_FIRST_EVIDENCE_PLUS_SEK_17", ARNROM: "ZERO_REGRESSION_90", KRUFER: "ZERO_REGRESSION_96", BOSCOP: "ZERO_REGRESSION_94", PUTJEA: "JEA_REST_64_WITHHELD_AT_SIBLING_ASK_93_IMPLIED_CAP_35", BORDIM: "MARGINAL_ONE_CENT_GAP_MUST_NOT_BE_WITHHELD" }, observed, assertions, PUTJEA: { fingerprint: putFingerprint, actions: put }, BORDIM: { DIM_withhold_starts: bordimWithholds.length, actions: bor }, by_machine: namedAttribution };
  })() : null;
  if (v43Acceptance) {
    v43Acceptance.named_regressions = { pass: Object.values(namedV43.assertions).every(Boolean), assertions: namedV43.assertions };
    v43Acceptance.receipt_single_clause_reproduction = { pass: Object.values(receiptReproduction).every((row) => row.pass), rows: Object.fromEntries(Object.entries(receiptReproduction).map(([name, row]) => [name, row.pass])) };
    v43Acceptance.pass = v43Acceptance.completed_pairs.pass && v43Acceptance.true_book_net_cents.pass && v43Acceptance.named_regressions.pass && v43Acceptance.receipt_single_clause_reproduction.pass;
  }
  const namedV45 = isV45 ? (() => {
    const baseline = namedAttribution.V43_BASELINE, releaseRows = v45ReleasedRestLedger.rows;
    const view = (label) => {
      const current = named[label].MARKET_UNION_REACH, prior = baseline[label].MARKET_UNION_REACH;
      const fullEvent = marketEvents.find((event) => event.event_id.includes(label));
      const rows = releaseRows.filter((row) => row.event_id.includes(label));
      let disposition = "NO_POST_CREDIT_RELEASE";
      if (rows.some((row) => row.completion_gained_vs_V43)) disposition = "RELEASED_AND_COMPLETED_PAIR";
      else if (rows.some((row) => row.filled_after_release)) disposition = "RELEASED_AND_FILLED_NO_NEW_COMPLETION";
      else if (rows.length) disposition = "RELEASED_UNFILLED";
      else if (!Object.values(current.legs).some((leg) => leg.credited)) disposition = "NO_SIBLING_CREDIT_PRE_FILL_GUARD_UNCHANGED";
      else disposition = "SIBLING_CREDIT_BUT_NO_ACTIVE_GUARD_WITHHOLD";
      return { event_id: named[label].event_id, V43: prior, V45: current, released_rest_rows: rows, disposition, causal_forensics: Object.fromEntries(Object.entries(fullEvent.legs).map(([id, leg]) => [id, { pair_cap_cents: leg.pair_cap_cents, terminal_rest_cents: leg.resting_target_at_edge_cents, union_reach_cents: leg.union_reach_cents, union_first_evidence_timestamp_epoch: leg.union_first_evidence_timestamp_epoch, reach_inside_hard_edge: leg.reach_inside_v36_edge, persistent_join_level_cents: leg.persistent_join_level, persistent_join_timestamp_epoch: leg.persistent_join_timestamp_epoch, post_join_certified_seller_hits_at_level: leg.post_join_certified_seller_hits_at_level, post_credit_guard_releases: leg.post_credit_guard_releases, post_credit_guard_reapplication_prevented_receipts: leg.post_credit_guard_reapplication_prevented_receipts, terminal_reason: leg.terminal_reason }])) };
    };
    const rows = Object.fromEntries(namedLabels.map((label) => [label, view(label)]));
    const exactOutcome = (label, ceiling) => rows[label].V45.completed && rows[label].V45.combined_entry_cents <= ceiling;
    const normalizedOutcome = (value) => ({ completed: value.completed, combined_entry_cents: value.combined_entry_cents, under_par: value.under_par, legs: Object.fromEntries(Object.entries(value.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class }])) });
    const unchanged = (label) => canonical(normalizedOutcome(rows[label].V45)) === canonical(normalizedOutcome(rows[label].V43));
    const assertions = { LUZTSE_completes_at_or_better_90: exactOutcome("LUZTSE", 90), PENTHA_unchanged_without_sibling_credit: unchanged("PENTHA"), SHEOLI_unchanged_without_sibling_credit: unchanged("SHEOLI"), ARNROM_at_or_better_89: exactOutcome("ARNROM", 89), KRUFER_at_or_better_96: exactOutcome("KRUFER", 96), KIRSEK_at_or_better_24: exactOutcome("KIRSEK", 24), no_new_exposure_from_post_credit_release: v45ReleasedRestLedger.summary.two_columns.new_exposure.events === 0 };
    return { ordered_law: "NAMED_COMPLETION_PASSES_AT_REQUIRED_COMBINED_PRICE_OR_BETTER; MECHANISM_FINGERPRINTS_BIND_TO_MECHANISM_NOT_TICK_VALUES", rows, assertions, pass: Object.values(assertions).every(Boolean) };
  })() : null;
  if (v45Acceptance) {
    v45Acceptance.named_checks = { pass: namedV45.pass, assertions: namedV45.assertions };
    v45Acceptance.pass = v45Acceptance.baseline_reproduction.pass && v45Acceptance.completed_pairs.pass && v45Acceptance.true_book_net_cents.pass && v45Acceptance.naked_pnl_cents.pass && v45Acceptance.named_checks.pass;
  }
  const namedV46 = isV46 ? (() => {
    const baseline = namedAttribution.V45_BASELINE, rows = {};
    for (const label of namedLabels) {
      const current = named[label].MARKET_UNION_REACH, prior = baseline[label].MARKET_UNION_REACH;
      const event = marketEvents.find((candidate) => candidate.event_id.includes(label));
      rows[label] = { event_id: event.event_id, V45: prior, V46: current, gap_credit_legs: Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, { eligible_receipts: leg.gap_credit_eligible_receipts, authorized_walks: leg.gap_credit_authorized_walks, sibling_uncredited_refusals: leg.gap_credit_sibling_uncredited_refusals, first: leg.gap_credit_first, last: leg.gap_credit_last, fill: leg.gap_credit_fill, terminal_rest_cents: leg.resting_target_at_edge_cents, terminal_reason: leg.terminal_reason }])) };
    }
    const atOrBetter = (label, ceiling) => rows[label].V46.completed && rows[label].V46.combined_entry_cents <= ceiling;
    const lockedAtLeast = (label, minimum) => rows[label].V46.completed && 100 - rows[label].V46.combined_entry_cents >= minimum;
    const assertions = { PANFAL_completes_at_or_better_92: atOrBetter("PANFAL", 92), PANFAL_locked_at_least_8: lockedAtLeast("PANFAL", 8), ARNROM_at_or_better_89: atOrBetter("ARNROM", 89), KIRSEK_at_or_better_24: atOrBetter("KIRSEK", 24), KRUFER_at_or_better_96: atOrBetter("KRUFER", 96), BOSCOP_at_or_better_80: atOrBetter("BOSCOP", 80), no_new_exposure_from_pair_gated_gap_credit: v46GapLedger.summary.two_columns.new_exposure.events === 0 };
    return { ordered_law: "NAMED_COMPLETION_PASSES_AT_REQUIRED_COMBINED_PRICE_OR_BETTER; GAP_CREDIT_REPRICE_REQUIRES_SIBLING_ALREADY_CREDITED", rows, assertions, pass: Object.values(assertions).every(Boolean), PANFAL_mechanism_diagnosis: { both_V45_legs_uncredited: Object.values(rows.PANFAL.V45.legs).every((leg) => !leg.credited), sibling_credit_authority_ever_available: Object.values(rows.PANFAL.gap_credit_legs).some((leg) => leg.authorized_walks > 0), conclusion: Object.values(rows.PANFAL.V45.legs).every((leg) => !leg.credited) ? "ORDERED_NAMED_OUTCOME_IS_UNREACHABLE_UNDER_THE_ORDERED_PAIR_GATE_BECAUSE_NEITHER_EXPRESSION_IS_CREDITED_BEFORE_THE_PAN_GAP" : "PAIR_GATE_AUTHORITY_EXISTED" } };
  })() : null;
  const v46Acceptance = isV46 ? (() => {
    const row = attributionByName.get("V46_PAIR_GATED_GAP_CREDIT"), baseline = attributionByName.get("V45_BASELINE");
    const frontierPass = ["LE_93", "LE_95", "LE_97", "LT_100"].every((tier) => row.MARKET_UNION_REACH.frontier[tier] >= baseline.MARKET_UNION_REACH.frontier[tier]);
    const boundRegressions = { under_par_non_regression: row.MARKET_UNION_REACH.under_par_pairs >= baseline.MARKET_UNION_REACH.under_par_pairs, locked_cents_non_regression: row.FULL_BOOK.completed_locked_cents >= baseline.FULL_BOOK.completed_locked_cents, frontier_non_regression: frontierPass, strict_build_verification_non_regression: row.STRICT_PRINT_CROSS.completed_pairs >= baseline.STRICT_PRINT_CROSS.completed_pairs, no_new_exposure: v46GapLedger.summary.two_columns.new_exposure.events === 0, named: namedV46.assertions };
    const out = { baseline_reproduction: v46BaselineReproduction, completed_pairs: { value: row.MARKET_UNION_REACH.completed_pairs, minimum: 396, pass: row.MARKET_UNION_REACH.completed_pairs >= 396 }, true_book_net_cents: { value: row.FULL_BOOK.true_book_net_cents, strict_minimum: 1774, pass: row.FULL_BOOK.true_book_net_cents > 1774 }, zero_bound_regressions: { checks: boundRegressions, pass: Object.values(boundRegressions).every((value) => typeof value === "boolean" ? value : Object.values(value).every(Boolean)) }, named_checks: { pass: namedV46.pass, assertions: namedV46.assertions } };
    out.pass = out.baseline_reproduction.pass && out.completed_pairs.pass && out.true_book_net_cents.pass && out.zero_bound_regressions.pass && out.named_checks.pass;
    return out;
  })() : null;
  const namedV47 = isV47 ? (() => {
    const baseline = namedAttribution.V45_BASELINE, rows = {};
    const view = (value) => ({ completed: value.completed, combined_entry_cents: value.combined_entry_cents, under_par: value.under_par, legs: Object.fromEntries(Object.entries(value.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class }])) });
    for (const label of namedLabels) rows[label] = { event_id: named[label].event_id, V45: view(baseline[label].MARKET_UNION_REACH), V47: view(named[label].MARKET_UNION_REACH), byte_identical_outcome: canonical(view(baseline[label].MARKET_UNION_REACH)) === canonical(view(named[label].MARKET_UNION_REACH)) };
    const assertions = { SURECH_causal_reach_null_remains_unfilled: !rows.SURECH.V45.completed && !rows.SURECH.V47.completed && Object.values(rows.SURECH.V47.legs).every((leg) => !leg.credited), ARNROM_no_regression: rows.ARNROM.byte_identical_outcome, KIRSEK_no_regression: rows.KIRSEK.byte_identical_outcome, KRUFER_no_regression: rows.KRUFER.byte_identical_outcome, BOSCOP_no_regression: rows.BOSCOP.byte_identical_outcome, PANFAL_no_regression: rows.PANFAL.byte_identical_outcome };
    return { rows, assertions, pass: Object.values(assertions).every(Boolean) };
  })() : null;
  const v47Acceptance = isV47 ? (() => {
    const row = attributionByName.get("V47_SAME_TICK_ARM"), baseline = attributionByName.get("V45_BASELINE");
    const regressionChecks = { market_completed: row.MARKET_UNION_REACH.completed_pairs >= baseline.MARKET_UNION_REACH.completed_pairs, market_under_par: row.MARKET_UNION_REACH.under_par_pairs >= baseline.MARKET_UNION_REACH.under_par_pairs, locked_cents: row.FULL_BOOK.completed_locked_cents >= baseline.FULL_BOOK.completed_locked_cents, true_book: row.FULL_BOOK.true_book_net_cents >= baseline.FULL_BOOK.true_book_net_cents, strict_completed: row.STRICT_PRINT_CROSS.completed_pairs >= baseline.STRICT_PRINT_CROSS.completed_pairs, frontier: ["LE_93", "LE_95", "LE_97", "LT_100"].every((tier) => row.MARKET_UNION_REACH.frontier[tier] >= baseline.MARKET_UNION_REACH.frontier[tier]), named: namedV47.pass };
    const out = { baseline_reproduction: v47BaselineReproduction, correctness: { V47_qualification_rows: v47SegCFootprint.summary.qualification_rows, V47_zero_qualification_to_post_rows: v47SegCFootprint.summary.V47_zero_qualification_to_post_rows, V47_positive_qualification_to_post_rows: v47SegCFootprint.summary.V47_positive_qualification_to_post_rows, V47_positive_scheduler_latency_rows: v47SegCFootprint.summary.V47_positive_scheduler_latency_rows, pass: v47SegCFootprint.summary.V47_positive_scheduler_latency_rows === 0 }, zero_regressions: { checks: regressionChecks, pass: Object.values(regressionChecks).every(Boolean) }, gain_required: false, observed_gain: { completed_pairs: row.MARKET_UNION_REACH.completed_pairs - baseline.MARKET_UNION_REACH.completed_pairs, locked_cents: row.FULL_BOOK.completed_locked_cents - baseline.FULL_BOOK.completed_locked_cents, true_book_net_cents: row.FULL_BOOK.true_book_net_cents - baseline.FULL_BOOK.true_book_net_cents } };
    out.pass = out.baseline_reproduction.pass && out.correctness.pass && out.zero_regressions.pass;
    return out;
  })() : null;
  const namedV48 = isV48 ? (() => {
    const selected = namedAttribution[v48SelectedRung], baseline = namedAttribution.V47_BASELINE, lawOnly = namedAttribution.TRADE_TRUTH_V47_INCUMBENT;
    const view = (row) => ({ completed: row.completed, combined_entry_cents: row.combined_entry_cents, under_par: row.under_par, legs: Object.fromEntries(Object.entries(row.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, terminal_reason: leg.terminal_reason }])) });
    const machineRows = {};
    for (const machine of machineSpecs.map((spec) => spec.name)) {
      machineRows[machine] = {};
      for (const label of namedLabels) machineRows[machine][label] = view(namedAttribution[machine][label].MARKET_UNION_REACH);
    }
    const selectedRun = machineRuns.get(v48SelectedRung), truthRun = machineRuns.get("TRADE_TRUTH_V47_INCUMBENT");
    const luzEvent = truthRun.marketEvents.find((event) => event.event_id.includes("LUZTSE"));
    const tseIdentity = Object.values(luzEvent.legs).find((leg) => leg.leg_identity.endsWith("|TSE")).leg_identity;
    const tseActions = truthRun.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && row.leg_identity === tseIdentity).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
    const tseFills = tseActions.filter((row) => row.kind === "FILL");
    const tseFill = tseFills[0] || null;
    const restPeriods = [];
    for (let i = 0; i < tseActions.length; i += 1) {
      const row = tseActions[i];
      if (!["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE"].includes(row.kind) || row.target_cents !== 79) continue;
      const next = tseActions.slice(i + 1).find((candidate) => ["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE", "PAIR_CAP_CANCEL", "CANCEL_REST", "FILL"].includes(candidate.kind));
      restPeriods.push({ start_epoch: row.timestamp_epoch, start_receipt: row.receipt, end_epoch: next?.timestamp_epoch ?? luzEvent.w1_right_epoch, end_receipt: next?.receipt ?? null });
    }
    const tseMeta = Object.values(baseByEvent.get(luzEvent.event_id).legs).find((leg) => leg.leg_identity === tseIdentity);
    const tsePrints = printLoad.byTicker.get(tseMeta.ticker) || [];
    const qualifyingPrints = restPeriods.flatMap((period) => tsePrints.filter((print) => print.ts > period.start_epoch && print.ts <= period.end_epoch && print.price <= 79).map((print) => ({ period, timestamp_epoch: print.ts, receipt: print.receipt, trade_id: print.trade_id, price_cents: print.price, size: print.size, taker_side: print.taker_side, taker_book_side: print.taker_book_side })));
    const floorRow = v48TradedFloorByLeg.get(tseIdentity);
    const creditedAt79 = Boolean(luzEvent.legs.TSE.credited && luzEvent.legs.TSE.entry_cents === 79);
    const selectedRows = machineRows[v48SelectedRung];
    const atOrBetter = (label, ceiling) => selectedRows[label].completed && selectedRows[label].combined_entry_cents <= ceiling;
    const normalized = (value) => canonical({ completed: value.completed, combined_entry_cents: value.combined_entry_cents, under_par: value.under_par, legs: value.legs });
    const noWorse = (label) => {
      const before = machineRows.V47_BASELINE[label], after = selectedRows[label];
      if (!before.completed) return !after.completed || after.under_par;
      return after.completed && after.combined_entry_cents <= before.combined_entry_cents;
    };
    const assertions = {
      LUZTSE_TSE_trade_truth_iff: creditedAt79 === (qualifyingPrints.length > 0),
      ARNROM_at_or_better_89: atOrBetter("ARNROM", 89),
      KIRSEK_at_or_better_24: atOrBetter("KIRSEK", 24),
      KRUFER_at_or_better_96: atOrBetter("KRUFER", 96),
      BOSCOP_at_or_better_80: atOrBetter("BOSCOP", 80),
      PANFAL_no_regression: noWorse("PANFAL"),
    };
    return {
      selected_ladder: v48SelectedRung,
      selection_law: "MAX_TRUE_BOOK_NET_CENTS_THEN_COMPLETED_PAIRS_THEN_COMPLETED_LOCKED_CENTS_THEN_MACHINE_NAME; NO_NAMED_RESULT_USED_FOR_SELECTION",
      by_machine: machineRows,
      LUZTSE_TSE: { leg_identity: tseIdentity, rest_periods_at_79: restPeriods, qualifying_post_stand_prints_at_or_below_79: qualifyingPrints, credited_at_79: creditedAt79, fills: tseFills, absolute_window_floor_print: floorRow.floor_print, absolute_floor_precedes_first_79_rest_by_seconds: restPeriods.length && floorRow.floor_print ? restPeriods[0].start_epoch - floorRow.floor_print.timestamp_epoch : null, condition: "CREDIT_IFF_TRUE_TRADE_PRINT_AT_OR_BELOW_79_WHILE_THE_79_REST_STOOD", pass: assertions.LUZTSE_TSE_trade_truth_iff },
      SALIBR_IBR_by_rung: Object.fromEntries(machineSpecs.map((spec) => [spec.name, machineRows[spec.name].SALIBR])),
      V47_baseline_vs_law_only_byte_equal_placements_not_claimed: normalized(machineRows.V47_BASELINE.ARNROM) === normalized(machineRows.TRADE_TRUTH_V47_INCUMBENT.ARNROM),
      assertions,
      pass: Object.values(assertions).every(Boolean),
    };
  })() : null;
  const v48Acceptance = isV48 ? (() => {
    const selected = attributionByName.get(v48SelectedRung), lawOnly = attributionByName.get("TRADE_TRUTH_V47_INCUMBENT");
    const out = {
      baseline_reproduction: v48BaselineReproduction,
      selected_ladder: v48SelectedRung,
      aggregate_targets: null,
      law_only_observed: { completed_pairs: lawOnly.MARKET.completed_pairs, true_book_net_cents: lawOnly.FULL_BOOK.true_book_net_cents },
      selected_observed: { completed_pairs: selected.MARKET.completed_pairs, true_book_net_cents: selected.FULL_BOOK.true_book_net_cents },
      zero_bound_named_regressions: { pass: namedV48.pass, assertions: namedV48.assertions },
    };
    out.pass = out.baseline_reproduction.pass && out.zero_bound_named_regressions.pass;
    return out;
  })() : null;
  const v49EvidenceLedger = isV49 ? (() => {
    const run = machineRuns.get("V49_EVIDENCED_LEVEL_STANDING");
    const actionRows = run.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && row.evidenced_standing?.raised).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, category: baseByEvent.get(row.event_id).category, price_region: baseByEvent.get(row.event_id).legs[row.leg_identity.split("|").at(-1)].price_region, timestamp_epoch: row.timestamp_epoch, t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds, receipt: row.receipt, action: row.kind, target_cents: row.target_cents, state: row.state, evidence: row.evidenced_standing.evidence }));
    const eventById = new Map(run.marketEvents.map((event) => [event.event_id, event]));
    const legIds = [...new Set(actionRows.map((row) => row.leg_identity))].sort();
    const legs = legIds.map((identity) => {
      const eventId = identity.split("|").slice(0, -1).join("|"), event = eventById.get(eventId), leg = Object.values(event.legs).find((value) => value.leg_identity === identity);
      return { event_id: eventId, leg_identity: identity, category: event.category, price_region: leg.price_region, evidenced_action_count: actionRows.filter((row) => row.leg_identity === identity).length, credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, first: actionRows.find((row) => row.leg_identity === identity), last: actionRows.filter((row) => row.leg_identity === identity).at(-1) };
    });
    return { rows: actionRows, legs, summary: { evidenced_actions: actionRows.length, evidenced_legs: legs.length, evidenced_games: new Set(legs.map((row) => row.event_id)).size, credited_legs: legs.filter((row) => row.credited).length, evidence_sources: countBy(actionRows.flatMap((row) => row.evidence.sources), (row) => row.source), fills_gained: v49Differential.rows.filter((row) => row.disposition === "FILL_GAINED").length, fills_repriced_favorable: v49Differential.rows.filter((row) => row.disposition === "FILL_REPRICED_FAVORABLE").length, fills_repriced_adverse: v49Differential.rows.filter((row) => row.disposition === "FILL_REPRICED_ADVERSE").length, fills_lost: v49Differential.rows.filter((row) => row.disposition === "FILL_LOST").length } };
  })() : null;
  const v49WindowTarget = isV49 ? (() => {
    const baseline = machineRuns.get("TRADE_TRUTH_V47_BASELINE").marketEvents, current = machineRuns.get("V49_EVIDENCED_LEVEL_STANDING").marketEvents;
    const baselineById = new Map(baseline.map((event) => [event.event_id, event]));
    const detailed = standabilityReceipt.detail.filter((row) => row.verdict === "WINDOW_LAWFUL_EVIDENCE").map((row) => {
      const event = current.find((candidate) => candidate.event_id.includes(row.code)), prior = baselineById.get(event.event_id), leg = Object.values(event.legs).find((value) => value.leg_id === row.leg), priorLeg = Object.values(prior.legs).find((value) => value.leg_id === row.leg);
      return { receipt_code: row.code, event_id: event.event_id, leg_id: row.leg, target_print_price_cents: row.print_price, V47_credited: priorLeg.credited, V47_entry_cents: priorLeg.entry_cents, V49_credited: leg.credited, V49_entry_cents: leg.entry_cents, V49_at_or_better_target: leg.credited && leg.entry_cents <= row.print_price, V47_pair_completed: prior.completed_pair, V49_pair_completed: event.completed_pair, pair_conversion: !prior.completed_pair && event.completed_pair };
    });
    const overallConversions = current.filter((event) => !baselineById.get(event.event_id).completed_pair && event.completed_pair);
    return { frozen_receipt_target: { games: standabilityReceipt.recoverable_under_window_law.games, locked_cents: standabilityReceipt.recoverable_under_window_law.locked_cents, by_category: standabilityReceipt.recoverable_under_window_law.by_category }, identity_binding: "THE_FE4747CD_RECEIPT_FREEZES_THE_81_GAME_TARGET_AS_AGGREGATES_BUT_DOES_NOT_EMIT_ALL_81_IDENTITIES; V49_DOES_NOT_FABRICATE_AN_INTERSECTION", frozen_detailed_lawful_evidence_rows: detailed, detailed_rows: detailed.length, detailed_at_or_better: detailed.filter((row) => row.V49_at_or_better_target).length, detailed_pair_conversions: detailed.filter((row) => row.pair_conversion).length, executable_all_population_pair_conversions_vs_V47: overallConversions.length, executable_conversion_event_ids: overallConversions.map((event) => event.event_id).sort() };
  })() : null;
  const namedV49 = isV49 ? (() => {
    const baseline = namedAttribution.TRADE_TRUTH_V47_BASELINE, current = namedAttribution.V49_EVIDENCED_LEVEL_STANDING, rows = {};
    const view = (value) => ({ completed: value.completed, combined_entry_cents: value.combined_entry_cents, under_par: value.under_par, legs: value.legs });
    for (const label of namedLabels) rows[label] = { event_id: named[label].event_id, V47: view(baseline[label].MARKET_UNION_REACH), V49: view(current[label].MARKET_UNION_REACH), evidenced_actions: v49EvidenceLedger.rows.filter((row) => row.event_id.includes(label)) };
    const noWorse = (label) => !rows[label].V47.completed ? true : rows[label].V49.completed && rows[label].V49.combined_entry_cents <= rows[label].V47.combined_entry_cents;
    const herLeg = rows.HERKAZ.V49.legs.HER;
    const assertions = { HERKAZ_completes: rows.HERKAZ.V49.completed, HERKAZ_HER_at_or_better_46: herLeg.credited && herLeg.entry_cents <= 46, HERKAZ_HER_trade_truth_fill: herLeg.fill_class === "MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST", ARNROM_no_regression: noWorse("ARNROM"), KIRSEK_no_regression: noWorse("KIRSEK"), KRUFER_no_regression: noWorse("KRUFER"), BOSCOP_no_regression: noWorse("BOSCOP"), PANFAL_no_regression: noWorse("PANFAL") };
    return { ordered_law: "NAMED_COMPLETION_PASSES_AT_REQUIRED_COMBINED_PRICE_OR_BETTER; HERKAZ_MECHANISM_BINDS_HER_AT_EVIDENCED_46_AND_LATER_TRUE_TRADE_CREDIT", rows, assertions, pass: Object.values(assertions).every(Boolean) };
  })() : null;
  const v49Acceptance = isV49 ? (() => {
    const current = attributionByName.get("V49_EVIDENCED_LEVEL_STANDING"), baseline = attributionByName.get("TRADE_TRUTH_V47_BASELINE");
    const checks = { named: namedV49.pass, completed_non_regression: current.MARKET.completed_pairs >= baseline.MARKET.completed_pairs, frontier_non_regression: ["LE_93", "LE_95", "LE_97", "LT_100"].every((tier) => current.MARKET.frontier[tier] >= baseline.MARKET.frontier[tier]), strict_completed_non_regression: current.STRICT_PRINT_CROSS.completed_pairs >= baseline.STRICT_PRINT_CROSS.completed_pairs };
    return { baseline_reproduction: v49BaselineReproduction, zero_bound_regressions: { checks, pass: Object.values(checks).every(Boolean) }, aggregate_target: null, observed: { completed_pairs: current.MARKET.completed_pairs, under_par_pairs: current.MARKET.under_par_pairs, full_book: current.FULL_BOOK, frontier: current.MARKET.frontier, strict_completed_pairs: current.STRICT_PRINT_CROSS.completed_pairs }, pass: v49BaselineReproduction.pass && Object.values(checks).every(Boolean) };
  })() : null;
  const v49bPackage = isV49b ? (() => {
    const baselineRun = machineRuns.get("TRADE_TRUTH_V47_BASELINE"), candidateRun = machineRuns.get("V49B_FAITHFUL_STAND_AT_P");
    const baseline = attributionByName.get("TRADE_TRUTH_V47_BASELINE"), candidate = attributionByName.get("V49B_FAITHFUL_STAND_AT_P");
    const baselineByEvent = new Map(baselineRun.marketEvents.map((event) => [event.event_id, event]));
    const candidateByEvent = new Map(candidateRun.marketEvents.map((event) => [event.event_id, event]));
    const doctrineActions = candidateRun.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && row.doctrine_standing?.authorized).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds, receipt: row.receipt, action: row.kind, target_cents: row.target_cents, reason: row.reason, mechanism_code: row.doctrine_standing.mechanism_code, doctrine: row.doctrine_standing.doctrine }));
    const exactActions = doctrineActions.filter((row) => row.mechanism_code === "AT_P");
    const offsetRows = doctrineActions.filter((row) => /BID_MINUS_ONE|OFFSET_AT_P/.test(`${row.mechanism_code}|${row.reason}`));
    const doctrineRows = [...v49bDoctrineByEventLeg.values()].sort((a, b) => a.identity_key.localeCompare(b.identity_key)).map((doctrine) => {
      const event = candidateByEvent.get(doctrine.source_event), prior = baselineByEvent.get(doctrine.source_event), leg = event.legs[doctrine.leg_id], priorLeg = prior.legs[doctrine.leg_id], actions = doctrineActions.filter((row) => row.leg_identity === leg.leg_identity);
      return { ...doctrine, category: event.category, price_region: leg.price_region, authorized_action_rows: actions.length, exact_AT_P_action_rows: actions.filter((row) => row.mechanism_code === "AT_P").length, V47: { credited: priorLeg.credited, entry_cents: priorLeg.entry_cents, pair_completed: prior.completed_pair, combined_entry_cents: prior.combined_entry_cents }, V49b: { credited: leg.credited, entry_cents: leg.entry_cents, at_or_better_than_P: leg.credited && leg.entry_cents <= doctrine.level_cents, pair_completed: event.completed_pair, combined_entry_cents: event.combined_entry_cents, fill_class: leg.fill_class, terminal_reason: leg.terminal_reason }, actions };
    });
    const games = identity81.the_81.map((frozen) => {
      const event = candidateByEvent.get(frozen.event), prior = baselineByEvent.get(frozen.event), rows = doctrineRows.filter((row) => row.source_event === frozen.event);
      return { event_id: frozen.event, code: frozen.code, category: frozen.cat, frozen_locked_value_cents: frozen.value, frozen_locked_value_role: "ANALYTICAL_LOCKED_VALUE_NOT_A_PAIR_PRICE", V47: { completed: prior.completed_pair, combined_entry_cents: prior.combined_entry_cents }, V49b: { completed: event.completed_pair, combined_entry_cents: event.combined_entry_cents, every_doctrine_leg_at_or_better_than_its_P: event.completed_pair && rows.every((row) => row.V49b.at_or_better_than_P) }, doctrine_legs: rows };
    });
    const regretRows = candidate.traded_floor_rows.filter((row) => row.credited && Number.isInteger(row.gap_to_lowest_trade_cents));
    const regretGroups = new Map();
    for (const row of regretRows) { const key = `${row.category}|${row.price_region}`; if (!regretGroups.has(key)) regretGroups.set(key, []); regretGroups.get(key).push(row); }
    const regretGauge = { stamp: "OPTIMISTIC_EX_POST_TRUE_TRADE_FLOOR", floor_source: "DIRECT_CANONICAL_PRINT_CENSUS_INSIDE_FROZEN_W1_SPAN", d3db740f_consumed_by_decision: false, aggregate: { credited_legs: regretRows.length, gap_cents: distribution(regretRows.map((row) => row.gap_to_lowest_trade_cents)) }, category_x_price_region: [...regretGroups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, rows]) => ({ cell, category: rows[0].category, price_region: rows[0].price_region, credited_legs: rows.length, gap_cents: distribution(rows.map((row) => row.gap_to_lowest_trade_cents)) })) };
    const frontierCells = (events) => {
      const groups = new Map(); for (const event of events) { const key = `${event.category}|${event.starting_price_split}`; if (!groups.has(key)) groups.set(key, []); groups.get(key).push(event); }
      return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, rows]) => ({ cell, category: rows[0].category, starting_price_split: rows[0].starting_price_split, denominator: rows.length, ...score(rows).frontier }));
    };
    const sealedFrontierPath = ".claude/window1_live_v4_replay/v47_sealed_exam_20260811/STAGE3_ONE_RUN_FINAL_RETRY2/SCORES/V47/FRONTIER.json";
    const sealedFrontierBytes = gitShow(SEALED_V47_EXAM_COMMIT, sealedFrontierPath), sealedFrontier = JSON.parse(sealedFrontierBytes);
    const added = candidateRun.marketEvents.filter((event) => event.completed_pair && !baselineByEvent.get(event.event_id).completed_pair);
    const addedDeep = added.filter((event) => event.combined_entry_cents <= 97);
    const sealedMarketFrontier = sealedFrontier.MARKET_TRADES_TRUTH;
    const depthShares = { sealed_V47: { commit: SEALED_V47_EXAM_COMMIT, path: sealedFrontierPath, completed_any: sealedMarketFrontier.ANY_PRICE, LE_97: sealedMarketFrontier.LE_97, share: sealedMarketFrontier.LE_97 / sealedMarketFrontier.ANY_PRICE }, dev_V47: { completed_any: baseline.MARKET.frontier.ANY_PRICE, LE_97: baseline.MARKET.frontier.LE_97, share: baseline.MARKET.frontier.LE_97 / baseline.MARKET.frontier.ANY_PRICE }, dev_V49b: { completed_any: candidate.MARKET.frontier.ANY_PRICE, LE_97: candidate.MARKET.frontier.LE_97, share: candidate.MARKET.frontier.LE_97 / candidate.MARKET.frontier.ANY_PRICE }, V49b_added_completions: { n: added.length, LE_97: addedDeep.length, share: added.length ? addedDeep.length / added.length : null, costs: distribution(added.map((event) => event.combined_entry_cents)), skew_shallow: added.length ? addedDeep.length / added.length < baseline.MARKET.frontier.LE_97 / baseline.MARKET.frontier.ANY_PRICE : null } };
    const boundRegressions = doctrineRows.filter((row) => row.V47.credited && row.V47.entry_cents <= row.level_cents && !row.V49b.at_or_better_than_P);
    const improvement = doctrineRows.filter((row) => row.V49b.at_or_better_than_P && !(row.V47.credited && row.V47.entry_cents <= row.level_cents));
    const mechanism = { doctrine_games: 81, doctrine_legs: doctrineRows.length, authorized_action_rows: doctrineActions.length, exact_AT_P_action_rows: exactActions.length, mechanism_codes: countBy(doctrineActions, (row) => row.mechanism_code), dominant_code: Object.entries(countBy(doctrineActions, (row) => row.mechanism_code)).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0]?.[0] ?? null, BID_MINUS_ONE_rows_on_doctrine_legs: offsetRows.length, exact_target_invariant_violations: exactActions.filter((row) => row.target_cents !== row.doctrine.level_cents).length, causal_authority_sources: countBy(exactActions.flatMap((row) => row.doctrine.causal_evidence || []), (row) => row.source), pass: exactActions.length > 0 && offsetRows.length === 0 && exactActions.every((row) => row.target_cents === row.doctrine.level_cents) };
    const acceptance = { baseline_reproduction: v49BaselineReproduction, mechanism, strict_improvements_on_bound_instrument: improvement.length, bound_regressions: boundRegressions.length, named_81_games_at_or_better: games.filter((row) => row.V49b.every_doctrine_leg_at_or_better_than_its_P).length, named_81_failures: games.filter((row) => !row.V49b.every_doctrine_leg_at_or_better_than_its_P).map((row) => row.event_id), ratified: v49BaselineReproduction.pass && mechanism.pass && improvement.length > 0 && boundRegressions.length === 0 };
    return { baseline, candidate, differential: v49Differential, doctrineActions, doctrineRows, games, regretGauge, depthShares, frontier: { market: { denominator: 804, ...candidate.MARKET.frontier, category_x_price_region: frontierCells(candidateRun.marketEvents) }, strict: { denominator: 804, ...candidate.STRICT_PRINT_CROSS.frontier, category_x_price_region: frontierCells(candidateRun.strictEvents) } }, acceptance, sealed_frontier_binding: { commit: SEALED_V47_EXAM_COMMIT, path: sealedFrontierPath, sha256: shaBytes(sealedFrontierBytes), bytes: sealedFrontierBytes.length } };
  })() : null;
  const v49bReceiptBindings = isV49b ? (() => {
    const paths = {
      substitution_audit: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/THE_SUBSTITUTION_AUDIT.json",
      standability_v2: standabilityPath,
      decision_chain_81: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DECISION_CHAIN_LEDGER_81.json",
      identity_81: identity81Path,
      causal_floor_conviction: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/ARNROM_RECONCILIATIONS.md",
    };
    const commits = { substitution_audit: SUBSTITUTION_AUDIT_COMMIT, standability_v2: STANDABILITY_V2_COMMIT, decision_chain_81: DECISION_CHAIN_81_COMMIT, identity_81: IDENTITY_81_COMMIT, causal_floor_conviction: CAUSAL_FLOOR_CONVICTION_COMMIT };
    return Object.fromEntries(Object.entries(paths).map(([name, artifactPath]) => { const bytes = name === "identity_81" ? identity81Bytes : name === "standability_v2" ? standabilityBytes : gitShow(commits[name], artifactPath); return [name, { commit: commits[name], path: artifactPath, sha256: shaBytes(bytes), bytes: bytes.length }]; }));
  })() : null;
  const v52Package = isV52 ? (() => {
    const baselineRun = machineRuns.get("V49B_FAITHFUL_STAND_AT_P"), candidateRun = machineRuns.get("V52_JUDGMENT_GATE");
    const baseline = attributionByName.get("V49B_FAITHFUL_STAND_AT_P"), candidate = attributionByName.get("V52_JUDGMENT_GATE");
    const frozenMarketPath = ".claude/window1_live_v4_replay/v49b_faithful_stand_at_p_20260811/MARKET_GRADE_SCORECARD.json";
    const frozenStrictPath = ".claude/window1_live_v4_replay/v49b_faithful_stand_at_p_20260811/STRICT_BUILD_VERIFICATION_SCORECARD.json";
    const frozenMarketBytes = gitShow(V49B_COMMIT, frozenMarketPath), frozenStrictBytes = gitShow(V49B_COMMIT, frozenStrictPath);
    const frozenMarket = JSON.parse(frozenMarketBytes).score, frozenStrict = JSON.parse(frozenStrictBytes).score;
    const baselineReproduction = {
      commit: V49B_COMMIT,
      market_path: frozenMarketPath,
      market_sha256: shaBytes(frozenMarketBytes),
      strict_path: frozenStrictPath,
      strict_sha256: shaBytes(frozenStrictBytes),
      market_byte_identical: canonical(baseline.MARKET) === canonical(frozenMarket),
      strict_byte_identical: canonical(baseline.STRICT_PRINT_CROSS) === canonical(frozenStrict),
    };
    baselineReproduction.pass = baselineReproduction.market_byte_identical && baselineReproduction.strict_byte_identical;
    const candidateByEvent = new Map(candidateRun.marketEvents.map((event) => [event.event_id, event]));
    const stateRows = candidateRun.marketEvents.map((event) => {
      const credited = Object.values(event.legs).filter((leg) => leg.credited);
      const state = credited.length === 2 && event.pair_under_par ? "COMPLETE_AT_DELTA" : credited.length === 1 ? "PARTIAL_FOR_REASON" : credited.length === 0 ? "NEITHER_FOR_REASON" : "COMPLETE_NOT_AT_DELTA";
      return { event_id: event.event_id, category: event.category, price_region: event.starting_price_split, state, combined_entry_cents: event.combined_entry_cents, reason: state === "COMPLETE_AT_DELTA" ? "BOTH_LICENSED_AND_CREDITED_UNDER_PAR" : Object.values(event.legs).filter((leg) => !leg.credited).map((leg) => `${leg.leg_id}:${leg.terminal_reason}:${Object.entries(leg.judgment_gate_blocks).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0]?.[0] ?? "NO_GATE_BLOCK"}`).join("|") };
    });
    const stateCensus = {
      states: countBy(stateRows, (row) => row.state),
      reasons: countBy(stateRows.filter((row) => row.state !== "COMPLETE_AT_DELTA"), (row) => `${row.state}|${row.reason}`),
      by_category_x_price_region: countBy(stateRows, (row) => `${row.category}|${row.price_region}|${row.state}`),
      rows: stateRows,
      conservation: { rows: stateRows.length, assigned_once: stateRows.length === 804, complete_not_at_delta: stateRows.filter((row) => row.state === "COMPLETE_NOT_AT_DELTA").length },
    };
    const restMutations = candidateRun.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && ["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE", "GAP_CREDIT_REPRICE_DOWN"].includes(row.kind));
    const firstPostByLeg = new Map();
    for (const row of candidateRun.actions.filter((action) => action.mode === "MARKET_TRADES_AS_TRUTH" && action.kind === "PLACE_REST")) {
      const prior = firstPostByLeg.get(row.leg_identity);
      if (!prior || row.timestamp_epoch < prior.timestamp_epoch || (row.timestamp_epoch === prior.timestamp_epoch && row.receipt.localeCompare(prior.receipt) < 0)) firstPostByLeg.set(row.leg_identity, row);
    }
    const firstPosts = [...firstPostByLeg.values()].sort((a, b) => a.leg_identity.localeCompare(b.leg_identity));
    const assertionRows = {
      zero_posts_pre_onset: restMutations.filter((row) => !row.birth_license?.onset?.passed),
      zero_posts_on_no_tape: restMutations.filter((row) => !row.birth_license?.read?.passed),
      zero_levels_from_displayed_bids: restMutations.filter((row) => row.birth_license?.level?.displayed_bid_consumed !== false),
      every_post_has_four_license_fields: restMutations.filter((row) => !(row.birth_license?.onset?.passed && row.birth_license?.read?.passed && row.birth_license?.diary?.passed && row.birth_license?.coherence?.lows_under_par && row.birth_license?.coherence?.disagreement_clear)),
      scavenger_off: restMutations.filter((row) => row.birth_license?.scavenger?.enabled !== false),
    };
    const flowAssertions = Object.fromEntries(Object.entries(assertionRows).map(([name, rows]) => [name, { violations: rows.map((row) => `${row.leg_identity}@${row.receipt}`), pass: rows.length === 0 }]));
    flowAssertions.pass = Object.values(flowAssertions).filter((value) => typeof value === "object").every((value) => value.pass);
    const postTiming = firstPosts.map((row) => ({ ...row, seconds_after_window_open: row.timestamp_epoch - baseByEvent.get(row.event_id).left }));
    const postingReceipt = {
      first_posts: firstPosts.length,
      rest_mutations: restMutations.length,
      REFLEX_POST: restMutations.filter((row) => !row.birth_license || row.birth_license.read.passed !== true).length,
      READ_LICENSED_POST: restMutations.filter((row) => row.birth_license?.read?.passed).length,
      first_post_seconds_after_window_open: distribution(postTiming.map((row) => row.seconds_after_window_open)),
      first_post_t_minus_scheduled_seconds: distribution(firstPosts.map((row) => row.t_minus_scheduled_seconds)),
      first_post_t_minus_actual_bell_seconds: distribution(firstPosts.map((row) => row.t_minus_actual_bell_seconds)),
      read_states_at_first_post: countBy(firstPosts, (row) => row.birth_license.read.state),
      onset_candidates_at_first_post: countBy(firstPosts, (row) => row.birth_license.onset.selected_candidate),
      within_300s_of_open_observation_only: postTiming.filter((row) => row.seconds_after_window_open <= 300).length,
    };
    const differential = ladderDifferential(baselineRun.marketEvents, candidateRun.marketEvents, closeByTicker, "V52_JUDGMENT_GATE");
    const regretRows = candidate.traded_floor_rows;
    const creditedRegret = regretRows.filter((row) => row.credited && Number.isInteger(row.gap_to_lowest_trade_cents));
    const missedWithFloor = regretRows.filter((row) => !row.credited && Number.isInteger(row.lowest_traded_price_cents));
    const regretGauge = {
      stamp: "OPTIMISTIC_EX_POST_TRUE_TRADE_FLOOR",
      credited: { legs: creditedRegret.length, gap_cents: distribution(creditedRegret.map((row) => row.gap_to_lowest_trade_cents)) },
      uncredited: { legs_with_lawful_traded_floor: missedWithFloor.length, no_fabricated_fill_price_or_penalty: true, by_terminal_reason: countBy(missedWithFloor, (row) => candidateByEvent.get(row.event_id).legs[row.leg_identity.split("|").at(-1)].terminal_reason) },
      category_x_price_region: [...new Set(regretRows.map((row) => `${row.category}|${row.price_region}`))].sort().map((cell) => {
        const rows = regretRows.filter((row) => `${row.category}|${row.price_region}` === cell), credited = rows.filter((row) => row.credited && Number.isInteger(row.gap_to_lowest_trade_cents));
        return { cell, legs: rows.length, credited_legs: credited.length, uncredited_with_floor: rows.filter((row) => !row.credited && Number.isInteger(row.lowest_traded_price_cents)).length, credited_gap_cents: distribution(credited.map((row) => row.gap_to_lowest_trade_cents)) };
      }),
    };
    const namedRows = {};
    for (const label of ["ARSMAR", "SANDAN", "PUTJEA", "POLKUH", "MERDRO"]) {
      const event = candidateRun.marketEvents.find((row) => row.event_id.includes(label));
      const actions = candidateRun.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && row.event_id === event.event_id);
      namedRows[label] = { event_id: event.event_id, completed: event.completed_pair, combined_entry_cents: event.combined_entry_cents, under_par: event.pair_under_par, legs: Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, post_onset_true_trade_low_cents: leg.post_onset_true_trade_low_cents, terminal_reason: leg.terminal_reason, gate_blocks: leg.judgment_gate_blocks, onset: leg.v52_onset }])), rest_mutations: actions.filter((row) => ["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE", "GAP_CREDIT_REPRICE_DOWN"].includes(row.kind)) };
    }
    const danMutations = namedRows.SANDAN.rest_mutations.filter((row) => row.leg_identity.endsWith("|DAN"));
    const putMutations = namedRows.PUTJEA.rest_mutations;
    const namedChecks = {
      ARSMAR_completes: namedRows.ARSMAR.completed,
      POLKUH_completes: namedRows.POLKUH.completed,
      SANDAN_DAN_uses_diary_not_displayed_premium: danMutations.length > 0 && danMutations.every((row) => row.birth_license?.level?.displayed_bid_consumed === false && row.target_cents === row.birth_license.level.target_cents),
      PUTJEA_real_diary_levels_or_lawful_sit_out: putMutations.every((row) => row.birth_license?.level?.displayed_bid_consumed === false && row.target_cents === row.birth_license.level.target_cents),
      MERDRO_not_credited_as_judgment: Object.values(namedRows.MERDRO.legs).every((leg) => !leg.credited),
    };
    const onsetRows = [...baseByEvent.values()].flatMap((base) => Object.values(base.legs).map((leg) => ({ event_id: base.event_id, leg_identity: leg.leg_identity, category: base.category, price_region: leg.price_region, ...leg.v52_onset })));
    const merDRO = onsetRows.find((row) => row.leg_identity.endsWith("26JUL16MERDRO|DRO")), merMER = onsetRows.find((row) => row.leg_identity.endsWith("26JUL16MERDRO|MER"));
    const onsetMethodCheck = {
      DRO_spread_shift_matches_9eff493b: merDRO?.candidates.A?.components.spread.shift_timestamp_epoch === 1784153734,
      DRO_midsum_shift_matches_9eff493b: merDRO?.candidates.A?.components.midsum.shift_timestamp_epoch === 1784156734,
      DRO_trade_cadence_shift_matches_9eff493b: merDRO?.candidates.B?.components.trade_cadence.shift_timestamp_epoch === 1784207794,
      MER_spread_shift_matches_9eff493b: merMER?.candidates.A?.components.spread.shift_timestamp_epoch === 1784153734,
      MER_midsum_shift_matches_9eff493b: merMER?.candidates.A?.components.midsum.shift_timestamp_epoch === 1784156734,
      MER_declining_trade_cadence_rejected: merMER?.candidates.B === null,
    };
    const flowRun = {
      marketEvents: candidateRun.marketEvents.filter((event) => v52ShortEvent(event.event_id)),
      actions: candidateRun.actions.filter((row) => v52ShortEvent(row.event_id)),
    };
    const stage1Flow = buildV52FlowPackage(flowRun, baseByEvent, v52TapePackBytes, v52OnsetReceiptBytes);
    const namedAutopsy = buildV52NamedAutopsy(candidateRun, baselineRun, baseByEvent, printLoad, stage1Flow);
    const frontierCells = (events) => {
      const groups = new Map();
      for (const event of events) {
        const key = `${event.category}|${event.starting_price_split}`;
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(event);
      }
      return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, rows]) => ({ cell, category: rows[0].category, price_region: rows[0].starting_price_split, denominator: rows.length, ...score(rows).frontier }));
    };
    const frontier = {
      market: { denominator: 804, ...candidate.MARKET.frontier, category_x_price_region: frontierCells(candidateRun.marketEvents) },
      strict: { denominator: 804, ...candidate.STRICT_PRINT_CROSS.frontier, category_x_price_region: frontierCells(candidateRun.strictEvents) },
    };
    const acceptance = { mechanism_bound: true, aggregate_target: null, baseline_reproduction: baselineReproduction, flow_assertions: flowAssertions, onset_method_check: { checks: onsetMethodCheck, pass: Object.values(onsetMethodCheck).every(Boolean) }, named_checks: { checks: namedChecks, pass: Object.values(namedChecks).every(Boolean) } };
    acceptance.pass = acceptance.baseline_reproduction.pass && acceptance.flow_assertions.pass && acceptance.onset_method_check.pass && acceptance.named_checks.pass;
    return { baseline, candidate, baselineReproduction, differential, stateCensus, flowAssertions, postingReceipt, regretGauge, namedRows, namedChecks, onsetRows, onsetMethodCheck, stage1Flow, frontier, restMutations, firstPosts, acceptance, namedAutopsy };
  })() : null;
  const v43GuardOnlyDiff = isV43 ? deepGapDifferential(machineRuns.get("V41_BASELINE").marketEvents, machineRuns.get("C2_GUARD_ONLY").marketEvents, closeByTicker) : null;
  const v43AttributionScorecard = isV43 ? {
    order: machineSpecs.map((spec) => spec.name),
    rows: attributionRows.map(({ full_book_rows, ...row }) => row),
    receipt_reproduction: receiptReproduction,
    composition_bar: v43Acceptance,
    interaction_deltas_vs_V41: attributionRows.map((row) => ({ machine: row.machine, completed_pairs_delta: row.MARKET_UNION_REACH.completed_pairs - 243, locked_cents_delta: row.FULL_BOOK.completed_locked_cents - 732, naked_pnl_cents_delta: row.FULL_BOOK.naked_pnl_cents - 50, true_book_net_cents_delta: row.FULL_BOOK.true_book_net_cents - 782 })),
  } : null;
  const v45AttributionScorecard = isV45 ? {
    order: machineSpecs.map((spec) => spec.name),
    rows: attributionRows.map(({ full_book_rows, ...row }) => row),
    frozen_V43_reproduction: v45BaselineReproduction,
    acceptance: v45Acceptance,
    delta_V45_minus_V43: { completed_pairs: attributionByName.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT").MARKET_UNION_REACH.completed_pairs - attributionByName.get("V43_BASELINE").MARKET_UNION_REACH.completed_pairs, under_par_pairs: attributionByName.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT").MARKET_UNION_REACH.under_par_pairs - attributionByName.get("V43_BASELINE").MARKET_UNION_REACH.under_par_pairs, locked_cents: attributionByName.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT").FULL_BOOK.completed_locked_cents - attributionByName.get("V43_BASELINE").FULL_BOOK.completed_locked_cents, naked_pnl_cents: attributionByName.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT").FULL_BOOK.naked_pnl_cents - attributionByName.get("V43_BASELINE").FULL_BOOK.naked_pnl_cents, true_book_net_cents: attributionByName.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT").FULL_BOOK.true_book_net_cents - attributionByName.get("V43_BASELINE").FULL_BOOK.true_book_net_cents },
  } : null;
  const v46AttributionScorecard = isV46 ? {
    order: machineSpecs.map((spec) => spec.name),
    rows: attributionRows.map(({ full_book_rows, ...row }) => row),
    frozen_V45_reproduction: v46BaselineReproduction,
    acceptance: v46Acceptance,
    delta_V46_minus_V45: { completed_pairs: attributionByName.get("V46_PAIR_GATED_GAP_CREDIT").MARKET_UNION_REACH.completed_pairs - attributionByName.get("V45_BASELINE").MARKET_UNION_REACH.completed_pairs, under_par_pairs: attributionByName.get("V46_PAIR_GATED_GAP_CREDIT").MARKET_UNION_REACH.under_par_pairs - attributionByName.get("V45_BASELINE").MARKET_UNION_REACH.under_par_pairs, locked_cents: attributionByName.get("V46_PAIR_GATED_GAP_CREDIT").FULL_BOOK.completed_locked_cents - attributionByName.get("V45_BASELINE").FULL_BOOK.completed_locked_cents, naked_pnl_cents: attributionByName.get("V46_PAIR_GATED_GAP_CREDIT").FULL_BOOK.naked_pnl_cents - attributionByName.get("V45_BASELINE").FULL_BOOK.naked_pnl_cents, true_book_net_cents: attributionByName.get("V46_PAIR_GATED_GAP_CREDIT").FULL_BOOK.true_book_net_cents - attributionByName.get("V45_BASELINE").FULL_BOOK.true_book_net_cents },
  } : null;
  const v47AttributionScorecard = isV47 ? {
    order: machineSpecs.map((spec) => spec.name),
    rows: attributionRows.map(({ full_book_rows, ...row }) => row),
    frozen_V45_reproduction: v47BaselineReproduction,
    acceptance: v47Acceptance,
    delta_V47_minus_V45: v47Acceptance.observed_gain,
  } : null;
  const v48AttributionScorecard = isV48 ? {
    order: machineSpecs.map((spec) => spec.name),
    market_law: "ANY_TRUE_TRADE_AT_OR_BELOW_A_PRIOR_LAWFUL_STANDING_REST; ASKS_NEVER_CREDIT_AND_NEVER_DEFINE_THE_FLOOR",
    rows: attributionRows.map(({ full_book_rows, traded_floor_rows, traded_floor_games, ...row }) => row),
    frozen_V47_reproduction: v48BaselineReproduction,
    selected_ladder: v48SelectedRung,
    selection_law: namedV48.selection_law,
    acceptance: v48Acceptance,
  } : null;
  const v49AttributionScorecard = isV49 ? {
    order: machineSpecs.map((spec) => spec.name),
    market_law: "ANY_TRUE_TRADE_AT_OR_BELOW_A_PRIOR_LAWFUL_STANDING_REST; ASKS_INFORM_PLACEMENT_ONLY",
    rows: attributionRows.map(({ full_book_rows, traded_floor_rows, traded_floor_games, ...row }) => row),
    frozen_V47_reproduction: v49BaselineReproduction,
    differential: { aggregate: v49Differential.aggregate, by_category: v49Differential.by_category, score_delta: v49Differential.score_delta },
    acceptance: v49Acceptance,
  } : null;
  const core = {
    "CONTROL_BINDING.json": canonical(control),
    ...((isPlacementStack && !isMaker41) ? { "TAKE_PATH_INTACT_RECEIPT.json": canonical({ frozen_V36_commit: V36_COMMIT, V36_policy_path: "arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js", V36_policy_sha256: fileHash(path.join(v36Root, "arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js")), variant_policy_path: path.relative(repo, policyFile).replaceAll("\\", "/"), variant_policy_sha256: fileHash(policyFile), decision_reason: isV40 ? "MATURE_EVIDENCE_FLOOR_TAKE" : "V36_MATURE_EVIDENCE_FLOOR_TAKE_UNCHANGED", market_taker_fills: marketLegs.filter((leg) => String(leg.fill_class).includes("TAKER")).length, strict_taker_fills: strictEvents.flatMap((event) => Object.values(event.legs)).filter((leg) => String(leg.fill_class).includes("TAKER")).length, V38_tombstone_role: "REJECTED_MAKER_ONLY_NEGATIVE_CONTROL_NOT_INHERITED" }) } : { "TAKE_PATH_DELETION_RECEIPT.json": canonical({ policy_path: path.relative(repo, policyFile).replaceAll("\\", "/"), policy_sha256: fileHash(policyFile), forbidden_action_literal_TAKE_count: (policyText.match(/action:\s*["']TAKE["']/g) || []).length, take_named_function_count: (policyText.match(/function\s+\w*take\w*/gi) || []).length, market_taker_fills: marketLegs.filter((leg) => String(leg.fill_class).includes("TAKER")).length, strict_taker_fills: strictEvents.flatMap((event) => Object.values(event.legs)).filter((leg) => String(leg.fill_class).includes("TAKER")).length, entry_actions_exported: ["PLACE_REST", "REPRICE_REST"], maker_fees_cents: 0, pass: true }) }),
    "PULSE_FLOOR_BINDING.json": canonical(pulseBinding),
    "MARKET_GRADE_SCORECARD.json": canonical(isV52 ? { score: marketScore, traded_floor_grade: attributionByName.get("V52_JUDGMENT_GATE").TRADED_FLOOR_GRADE, ruler: "CANON_TRADES_AS_TRUTH" } : isV49b ? { score: marketScore, traded_floor_grade: attributionByName.get("V49B_FAITHFUL_STAND_AT_P").TRADED_FLOOR_GRADE, ruler: "CANON_TRADES_AS_TRUTH" } : isV49 ? { score: marketScore, traded_floor_grade: attributionByName.get("V49_EVIDENCED_LEVEL_STANDING").TRADED_FLOOR_GRADE, ruler: "TRADES_AS_TRUTH" } : isV48 ? { score: marketScore, traded_floor_grade: attributionByName.get("TRADE_TRUTH_V47_INCUMBENT").TRADED_FLOOR_GRADE, ruler: "TRADES_AS_TRUTH" } : { score: marketScore, reach_grade: marketGrades.aggregate, comparison_answer_key: EXPECTED_REACH }),
    "STRICT_BUILD_VERIFICATION_SCORECARD.json": canonical(isTradeTruthVariant ? { score: strictScore, traded_floor_grade: gradeAgainstTradedFloors(strictEvents, v48TradedFloorByLeg).aggregate, role: "BUILD_VERIFICATION_ONLY_NOT_MARKET_VALUE" } : { score: strictScore, reach_grade: strictGrades.aggregate, role: "BUILD_VERIFICATION_ONLY_NOT_MARKET_VALUE" }),
    "CATEGORY_X_BELL_CONFIDENCE.json": canonical(isV52 ? { V49B_BASELINE: attributionByName.get("V49B_FAITHFUL_STAND_AT_P").category_x_bell_confidence, V52: attributionByName.get("V52_JUDGMENT_GATE").category_x_bell_confidence } : isV49b ? { BASELINE: attributionByName.get("TRADE_TRUTH_V47_BASELINE").category_x_bell_confidence, V49B: attributionByName.get("V49B_FAITHFUL_STAND_AT_P").category_x_bell_confidence } : isV49 ? { BASELINE: attributionByName.get("TRADE_TRUTH_V47_BASELINE").category_x_bell_confidence, V49: attributionByName.get("V49_EVIDENCED_LEVEL_STANDING").category_x_bell_confidence } : isV48 ? { MARKET_TRADES_AS_TRUTH: attributionByName.get("TRADE_TRUTH_V47_INCUMBENT").category_x_bell_confidence, selected_ladder: v48SelectedRung, SELECTED: attributionByName.get(v48SelectedRung).category_x_bell_confidence } : { MARKET_UNION_REACH: cellSummary(marketGrades), STRICT_PRINT_CROSS: cellSummary(strictGrades), conservation: { market_answer_key_D: marketGrades.classRows.length, strict_answer_key_D: strictGrades.classRows.length, expected: 637, pass: marketGrades.classRows.length === 637 && strictGrades.classRows.length === 637 } }),
    ...(!isTradeTruthVariant ? {
      "REACH_GRADE_EVENT_LEDGER.jsonl.gz": gzipRows(marketGrades.classRows),
      "REACH_GRADE_LEG_LEDGER.jsonl.gz": gzipRows(marketGrades.rows),
      "RESIDUAL_LAYER_BIND_LEDGER.jsonl.gz": gzipRows(marketGrades.residuals),
      "LAYER_BIND_RANKING.json": canonical({ rows: layerRanking, conservation: { residual_sides: marketGrades.residuals.length, ranked_sides: layerRanking.reduce((sum, row) => sum + row.sides, 0), pass: marketGrades.residuals.length === layerRanking.reduce((sum, row) => sum + row.sides, 0) } }),
    } : {}),
    ...(isV39 ? { "CAUSAL_DIRECTION_CLASSIFIER_TELEMETRY.json": canonical(directionTelemetry), "MISLABEL_RECOVERY_RECEIPT.json": canonical(mislabelRecovery), "MISLABEL_RECOVERY_LEDGER.jsonl.gz": gzipRows(reconstructedRecovery) } : {}),
    ...(isPlacementStack ? { "REST_SANITY.json": canonical(sanity), "V36_COMPARISON.json": canonical(v36Comparison) } : {}),
    ...(isV40 ? { "CLASSIFIER_RESEARCH_OPEN_RECEIPT.json": canonical(classifierResearchOpen), "ACCEPTANCE_BAR.json": canonical(acceptance), "PERSISTENT_JOIN_POST_EVIDENCE_RECEIPT.json": canonical(joinReceipt), "PERSISTENT_JOIN_POST_EVIDENCE_LEDGER.jsonl.gz": gzipRows(joinRows) } : {}),
    ...(isMaker41 ? { "PERSISTENCE_ONLY_JOIN_RECEIPT.json": canonical({ controlling_frontier: { commit: RISER_FRONTIER_COMMIT, sha256: shaBytes(riserFrontierBytes), T4_persist300: riserFrontierReceipt.per_trigger.T4_persist300 }, controlling_level_policy: { commit: LEVEL_POLICY_COMMIT, sha256: shaBytes(levelPolicyBytes), P2_join: levelPolicyReceipt.per_policy.P2_join, P3_join_track: levelPolicyReceipt.per_policy.P3_join_track }, seller_hit_gate_removed: true, first_two_sided_tracker_until_join: true, join_overrides_tracker: true, join_census: joinReceipt }), "PERSISTENT_JOIN_LEDGER.jsonl.gz": gzipRows(joinRows), "CAUSAL_REACH_BINDING.json": canonical({ commit: CAUSAL_REACH_COMMIT, path: causalReachPath, sha256: shaBytes(causalReachBytes), CAUSAL_REACH: causalReachReceipt.CAUSAL_REACH, conservation: causalReachReceipt.conservation }), ...(isV41 ? { "NAMED_V41_RECEIPT.json": canonical(namedV41) } : {}) } : {}),
    ...(isV49 ? {
      "V49_RECEIPT_BINDINGS.json": canonical({
        frozen_V47: { commit: V47_COMMIT, baseline_reproduction: v49BaselineReproduction },
        standability_v2: { commit: STANDABILITY_V2_COMMIT, json_path: standabilityPath, json_sha256: shaBytes(standabilityBytes), markdown_path: standabilityMdPath, markdown_sha256: shaBytes(standabilityMdBytes), target_games: standabilityReceipt.recoverable_under_window_law.games, target_locked_cents: standabilityReceipt.recoverable_under_window_law.locked_cents },
        HERKAZ: { commit: HERKAZ_EXEMPLAR_COMMIT, receipt_path: herkazPath, receipt_sha256: shaBytes(herkazBytes), marks_path: herkazMarksPath, marks_sha256: shaBytes(herkazMarksBytes), timeline_path: herkazTimelinePath, timeline_sha256: shaBytes(herkazTimelineBytes), evidenced_level_cents: herkazReceipt.P_evidenced_level },
        universal_plus_one_receipt: { commit: LOOSEN_ONE_CENT_COMMIT, path: loosenOneCentPath, sha256: shaBytes(loosenOneCentBytes), controlling_row: loosenOneCentReceipt.per_k["k=1"] },
      }),
      "ATTRIBUTION_SCORECARD.json": canonical(v49AttributionScorecard),
      "EVIDENCED_STANDING_RECEIPT.json": canonical(v49EvidenceLedger.summary),
      "EVIDENCED_STANDING_ACTION_LEDGER.jsonl.gz": gzipRows(v49EvidenceLedger.rows),
      "EVIDENCED_STANDING_LEG_LEDGER.jsonl.gz": gzipRows(v49EvidenceLedger.legs),
      "V47_V49_DIFFERENTIAL_RECEIPT.json": canonical({ aggregate: v49Differential.aggregate, by_category: v49Differential.by_category, score_delta: v49Differential.score_delta }),
      "V47_V49_DIFFERENTIAL_LEDGER.jsonl.gz": gzipRows(v49Differential.rows),
      "STANDABILITY_V2_EXECUTABLE_CONVERSION.json": canonical(v49WindowTarget),
      "NAMED_V49_RECEIPT.json": canonical(namedV49),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v49Acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v49Acceptance.pass ? "PASS" : "BLOCKED_V47_REMAINS_OPERATIVE", operative_candidate: v49Acceptance.pass ? "V49_EVIDENCED_LEVEL_STANDING" : "V47_FB74C8B8", aggregate_targets: null, reasons: [...(!v49Acceptance.baseline_reproduction.pass ? ["V47_BASELINE_REPRODUCTION_FAILED"] : []), ...(!v49Acceptance.zero_bound_regressions.pass ? ["BOUND_REGRESSION"] : [])], no_forced_values: true }),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, close_column: "replay_close_cents", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })) }),
      "TRADES_AS_TRUTH_CREDIT_LAW.json": canonical({ order_must_preexist_print: true, price_relation: "TRUE_TRADE_PRICE_LE_REST_LEVEL", required_fields: ["trade_id", "exchange_timestamp", "price"], asks_role: "PLACEMENT_ONLY", strict_build_verification_separate: true }),
    } : {}),
    ...(isV49b ? {
      "V49B_RECEIPT_BINDINGS.json": canonical({ frozen_V47: { commit: V47_COMMIT, baseline_reproduction: v49BaselineReproduction }, receipts: v49bReceiptBindings, sealed_depth_comparator: v49bPackage.sealed_frontier_binding }),
      "ATTRIBUTION_SCORECARD.json": canonical({ order: machineSpecs.map((spec) => spec.name), rows: attributionRows.map(({ full_book_rows, traded_floor_rows, traded_floor_games, ...row }) => row), differential: { aggregate: v49bPackage.differential.aggregate, by_category: v49bPackage.differential.by_category, score_delta: v49bPackage.differential.score_delta }, acceptance: v49bPackage.acceptance }),
      "FRONTIER.json": canonical(v49bPackage.frontier),
      "REGRET_GAUGE.json": canonical(v49bPackage.regretGauge),
      "DEPTH_SHARE_DEV_VS_SEALED.json": canonical(v49bPackage.depthShares),
      "FAITHFUL_STAND_AT_P_MECHANISM_RECEIPT.json": canonical(v49bPackage.acceptance.mechanism),
      "FAITHFUL_STAND_AT_P_ACTION_LEDGER.jsonl.gz": gzipRows(v49bPackage.doctrineActions),
      "DOCTRINE_81_OUTCOME_RECEIPT.json": canonical({ games: 81, doctrine_legs: v49bPackage.doctrineRows.length, games_at_or_better: v49bPackage.acceptance.named_81_games_at_or_better, failures: v49bPackage.acceptance.named_81_failures, conservation: { games: v49bPackage.games.length, doctrine_legs: v49bPackage.doctrineRows.length, pass: v49bPackage.games.length === 81 && v49bPackage.doctrineRows.length === 93 } }),
      "DOCTRINE_81_GAME_LEDGER.jsonl.gz": gzipRows(v49bPackage.games),
      "DOCTRINE_81_LEG_LEDGER.jsonl.gz": gzipRows(v49bPackage.doctrineRows),
      "V47_V49B_DIFFERENTIAL_RECEIPT.json": canonical({ aggregate: v49bPackage.differential.aggregate, by_category: v49bPackage.differential.by_category, score_delta: v49bPackage.differential.score_delta }),
      "V47_V49B_DIFFERENTIAL_LEDGER.jsonl.gz": gzipRows(v49bPackage.differential.rows),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v49bPackage.acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v49bPackage.acceptance.ratified ? "PASS_RATIFIED" : "BLOCKED_V47_REMAINS_OPERATIVE", operative_candidate: v49bPackage.acceptance.ratified ? "V49B_FAITHFUL_STAND_AT_P" : "V47_FB74C8B8", mechanism_bound_only: true }),
      "FLOOR_AUTHORITY_RECEIPT.json": canonical({ prohibited_decision_surface: { commit: CAUSAL_REACH_COMMIT, ruling_commit: CAUSAL_FLOOR_CONVICTION_COMMIT, consumed_by_V49b_decisions: false }, gauge: v49bPackage.regretGauge.stamp, direct_print_census_only: true }),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, close_column: "replay_close_cents", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })) }),
      "TRADES_AS_TRUTH_CREDIT_LAW.json": canonical({ order_must_preexist_print: true, price_relation: "TRUE_TRADE_PRICE_LE_REST_LEVEL", asks_role: "PLACEMENT_ONLY", strict_build_verification_separate: true }),
    } : {}),
    ...(isV52 ? {
      "V52_RECEIPT_BINDINGS.json": canonical({
        frozen_V49b: { commit: V49B_COMMIT, baseline_reproduction: v52Package.baselineReproduction },
        reflex_census: { commit: REFLEX_CENSUS_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json", sha256: shaBytes(gitShow(REFLEX_CENSUS_COMMIT, ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json")) },
        stability_onset: { commit: STABILITY_ONSET_COMMIT, path: v52OnsetReceiptPath, sha256: shaBytes(v52OnsetReceiptBytes), method: "NEUTRAL_TWO_SEGMENT_SSE_A_SPREAD_COLLAPSE_PLUS_CROSS_LEG_MIDSUM_SETTLE_OR_B_SUSTAINED_TRADE_CADENCE_ARRIVAL" },
        five_game_tape_packs: { commit: FIVE_GAME_TAPE_PACK_COMMIT, path: v52TapePackPath, sha256: shaBytes(v52TapePackBytes) },
        scoped_law: "REST_BIRTH_REQUIRES_STABILITY_ONSET_AND_MACHINE_READ_AND_POST_ONSET_TRUE_TRADE_DIARY_AND_PAIR_COHERENCE; SCAVENGER_OFF",
      }),
      "STAGE1_FLOW_ASSERTIONS.json": canonical({ ...v52Package.stage1Flow.assertions, pass: v52Package.stage1Flow.pass }),
      "STAGE1_FLOW_OUTCOMES_OBSERVATION_ONLY.json": canonical(v52Package.stage1Flow.outcomes),
      "STAGE1_DECISION_TRACE.jsonl.gz": gzipRows(v52Package.stage1Flow.trace),
      "STABILITY_ONSET_LEDGER.jsonl.gz": gzipRows(v52Package.onsetRows),
      "BIRTH_LICENSE_ACTION_LEDGER.jsonl.gz": gzipRows(v52Package.restMutations),
      "POSTING_AND_READ_DISTRIBUTIONS.json": canonical(v52Package.postingReceipt),
      "THREE_STATE_CENSUS.json": canonical({ states: v52Package.stateCensus.states, reasons: v52Package.stateCensus.reasons, by_category_x_price_region: v52Package.stateCensus.by_category_x_price_region, conservation: v52Package.stateCensus.conservation }),
      "THREE_STATE_EVENT_LEDGER.jsonl.gz": gzipRows(v52Package.stateCensus.rows),
      "FRONTIER.json": canonical(v52Package.frontier),
      "REGRET_GAUGE.json": canonical(v52Package.regretGauge),
      "V49B_V52_DIFFERENTIAL_RECEIPT.json": canonical({ aggregate: v52Package.differential.aggregate, by_category: v52Package.differential.by_category, score_delta: v52Package.differential.score_delta }),
      "V49B_V52_DIFFERENTIAL_LEDGER.jsonl.gz": gzipRows(v52Package.differential.rows),
      "NAMED_V52_RECEIPT.json": canonical({ rows: v52Package.namedRows, checks: v52Package.namedChecks }),
      "ONSET_CLAUSE_BINDING.json": canonical(v52Package.namedAutopsy.summary.onset_clause_1_binding),
      "NAMED_CHECK_AUTOPSY.json": canonical(v52Package.namedAutopsy.summary),
      "ARSMAR_FULL_GATE_TRACE.jsonl.gz": gzipRows(v52Package.namedAutopsy.arsFullGateTrace),
      "ARSMAR_35C_CRITICAL_TRACE.jsonl.gz": gzipRows(v52Package.namedAutopsy.arsCriticalTrace),
      "ARSMAR_REST_LIFECYCLE.jsonl.gz": gzipRows(v52Package.namedAutopsy.arsRestLifecycle),
      "POLKUH_FULL_GATE_TRACE.jsonl.gz": gzipRows(v52Package.namedAutopsy.polFullGateTrace),
      "POLKUH_TRANSITION_RECEIPT.json": canonical({ event_id: v52Package.namedAutopsy.summary.POLKUH.event_id, legs: v52Package.namedAutopsy.polLegs }),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v52Package.acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v52Package.acceptance.pass ? "PASS" : "BLOCKED_V49B_REMAINS_FROZEN_BASELINE", stage1_assertions_pass: v52Package.stage1Flow.pass, stage2_one_shot_completed: true, aggregate_target: null, behavioral_tuning_after_stage1: false, no_deployment: true }),
      "ATTRIBUTION_SCORECARD.json": canonical({ order: machineSpecs.map((spec) => spec.name), rows: attributionRows.map(({ full_book_rows, traded_floor_rows, traded_floor_games, ...row }) => row), differential: { aggregate: v52Package.differential.aggregate, by_category: v52Package.differential.by_category, score_delta: v52Package.differential.score_delta }, acceptance: v52Package.acceptance }),
      "FLOOR_AUTHORITY_RECEIPT.json": canonical({ decision_floor: "OWN_POST_ONSET_RUNNING_TRUE_TRADE_LOW", displayed_bid_consumed: false, ex_post_floor_consumed_by_decision: false, regret_gauge_stamp: v52Package.regretGauge.stamp }),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, close_column: "replay_close_cents", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })) }),
      "TRADES_AS_TRUTH_CREDIT_LAW.json": canonical({ order_must_preexist_print: true, timestamp_relation: "PRINT_TIMESTAMP_STRICTLY_GREATER_THAN_REST_ACTION_TIMESTAMP", price_relation: "TRUE_TRADE_PRICE_LE_REST_LEVEL", asks_role: "PLACEMENT_ONLY", strict_build_verification_separate: true, V52_crediting_changed_from_V49b: false }),
    } : {}),
    ...(isV48 ? {
      "V48_RECEIPT_BINDINGS.json": canonical({
        frozen_V47: { commit: V47_COMMIT, baseline_reproduction: v48BaselineReproduction },
        controlling_recut: { commit: TRADES_TRUTH_RECUT_COMMIT, json_path: tradesTruthRecutPath, json_sha256: shaBytes(tradesTruthRecutBytes), markdown_path: tradesTruthRecutMdPath, markdown_sha256: shaBytes(tradesTruthRecutMdBytes), re_cut_legs: tradesTruthRecut.population.L6_legs_recut, true_offer_existed: tradesTruthRecut.corrected_totals.true_offer_existed, seller_cross_set_lowest_legs: 0 },
        scoped_law: "ANY_TRUE_TRADE_PRINT_AT_OR_BELOW_A_LAWFUL_REST_AFTER_THE_REST_STOOD_CREDITS; NO_CHANNEL_AGGRESSOR_DWELL_SIZE_OR_ARRIVAL_FILTER",
        placement_honesty: "V47_INCUMBENT_IS_MIXED; BID_MINUS_ONE_BID_AND_RECENT_TRADE_ARE_EXPLICIT_EXECUTABLE_RUNGS",
      }),
      "ATTRIBUTION_SCORECARD.json": canonical(v48AttributionScorecard),
      "TRADED_FLOOR_RE_SUM.json": canonical({ law: v48TradedFloors.law, aggregate: v48TradedFloors.aggregate, by_category: v48TradedFloors.by_category, conservation: v48TradedFloors.conservation }),
      "TRADED_FLOOR_GAME_LEDGER.jsonl.gz": gzipRows(v48TradedFloors.game_rows),
      "TRADED_FLOOR_LEG_LEDGER.jsonl.gz": gzipRows(v48TradedFloors.leg_rows),
      "PLACEMENT_LADDER_ATTRIBUTION.json": canonical({ baseline: "TRADE_TRUTH_V47_INCUMBENT", rungs: Object.fromEntries(Object.entries(v48LadderDiffs).map(([name, value]) => [name, { aggregate: value.aggregate, by_category: value.by_category, score_delta: value.score_delta }])), selected: v48SelectedRung, selection_law: namedV48.selection_law }),
      "PLACEMENT_LADDER_DIFFERENTIAL_LEDGER.jsonl.gz": gzipRows(Object.values(v48LadderDiffs).flatMap((value) => value.rows)),
      "NAMED_V48_RECEIPT.json": canonical(namedV48),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v48Acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v48Acceptance.pass ? "PASS" : "BLOCKED", operative_candidate: v48Acceptance.pass ? v48SelectedRung : "V47_FB74C8B8_REMAINS_OPERATIVE", aggregate_targets: null, reasons: [ ...(!v48Acceptance.baseline_reproduction.pass ? ["V47_BASELINE_REPRODUCTION_FAILED"] : []), ...(!v48Acceptance.zero_bound_named_regressions.pass ? ["BOUND_NAMED_REGRESSION"] : []) ], no_forced_values: true }),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, receipt_path: fullBookReceiptPath, receipt_sha256: shaBytes(fullBookReceiptBytes), close_audit_path: closeAuditPath, close_audit_sha256: shaBytes(closeAuditBytes), close_column: "replay_close_cents", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, market_mode: row.market_mode, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })), acceptance: v48Acceptance }),
      "TRADES_AS_TRUTH_CREDIT_LAW.json": canonical({ order_must_preexist_print: true, timestamp_relation: "PRINT_TIMESTAMP_STRICTLY_GREATER_THAN_REST_ACTION_TIMESTAMP", price_relation: "TRUE_TRADE_PRICE_LE_REST_LEVEL", required_fields: ["trade_id", "exchange_timestamp", "price"], forbidden_filters: ["ask", "aggressor", "dwell", "displayed_size", "arrival_direction", "channel"], asks_role: "PLACEMENT_ONLY", strict_build_verification_separate: true }),
    } : {}),
    ...(isV47 ? {
      "V47_RECEIPT_BINDINGS.json": canonical({
        frozen_V45: { commit: V45_COMMIT, baseline_reproduction: v47BaselineReproduction, control_path: frozenV45ControlPath, control_sha256: shaBytes(frozenV45ControlBytes), attribution_path: frozenV45ScorePath, attribution_sha256: shaBytes(frozenV45ScoreBytes), inherited_policy_path: frozenV45PolicyPath, inherited_policy_git_sha256: shaBytes(frozenV45PolicyBytes), working_git_normalized_sha256: shaBytes(Buffer.from(fs.readFileSync(path.join(repo, frozenV45PolicyPath), "utf8").replace(/\r\n/g, "\n"))), git_normalized_policy_byte_identical: shaBytes(frozenV45PolicyBytes) === shaBytes(Buffer.from(fs.readFileSync(path.join(repo, frozenV45PolicyPath), "utf8").replace(/\r\n/g, "\n"))) },
        SURECH_forensic: { commit: SURECH_RENDER_COMMIT, marks_path: surechMarksPath, marks_sha256: shaBytes(surechMarksBytes), timeline_path: surechTimelinePath, timeline_sha256: shaBytes(surechTimelineBytes), role: "OLDER_L4_ARCHETYPE_EVIDENCE_NOT_A_FROZEN_V45_DECISION_TRACE" },
        scoped_law: "JOIN_QUALIFICATION_AND_PLACEMENT_DECISION_ARE_ONE_ATOMIC_RECEIPT_LOCAL_OPERATION; ALL_DECISION_LAWS_UNCHANGED",
      }),
      "ATTRIBUTION_SCORECARD.json": canonical(v47AttributionScorecard),
      "SEG_C_SAME_TICK_RECEIPT.json": canonical(v47SegCFootprint.summary),
      "SEG_C_SAME_TICK_FOOTPRINT.jsonl.gz": gzipRows(v47SegCFootprint.rows),
      "V45_V47_DIFFERENTIAL_RECEIPT.json": canonical(v47Differential),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v47Acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v47Acceptance.pass ? "PASS_OPERATIVE" : "BLOCKED_V45_REMAINS_OPERATIVE", operative_baseline: v47Acceptance.pass ? "V47_SAME_TICK_ARM" : "V45_3bda0a54", gains_required: false, reasons: [ ...(!v47Acceptance.baseline_reproduction.pass ? ["V45_BASELINE_REPRODUCTION_FAILED"] : []), ...(!v47Acceptance.correctness.pass ? ["POSITIVE_SCHEDULER_LATENCY_SURVIVED"] : []), ...(!v47Acceptance.zero_regressions.pass ? ["BOUND_REGRESSION"] : []) ], no_forced_values: true }),
      "NAMED_V47_RECEIPT.json": canonical(namedV47),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, receipt_path: fullBookReceiptPath, receipt_sha256: shaBytes(fullBookReceiptBytes), close_audit_path: closeAuditPath, close_audit_sha256: shaBytes(closeAuditBytes), close_column: "replay_close_cents", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })), acceptance: v47Acceptance }),
    } : {}),
    ...(isV46 ? {
      "V46_RECEIPT_BINDINGS.json": canonical({
        frozen_V45: { commit: V45_COMMIT, baseline_reproduction: v46BaselineReproduction, control_path: frozenV45ControlPath, control_sha256: shaBytes(frozenV45ControlBytes), attribution_path: frozenV45ScorePath, attribution_sha256: shaBytes(frozenV45ScoreBytes), inherited_policy_path: frozenV45PolicyPath, inherited_policy_git_sha256: shaBytes(frozenV45PolicyBytes), working_filesystem_sha256: fileHash(path.join(repo, frozenV45PolicyPath)), working_git_normalized_sha256: shaBytes(Buffer.from(fs.readFileSync(path.join(repo, frozenV45PolicyPath), "utf8").replace(/\r\n/g, "\n"))), git_normalized_policy_byte_identical: shaBytes(frozenV45PolicyBytes) === shaBytes(Buffer.from(fs.readFileSync(path.join(repo, frozenV45PolicyPath), "utf8").replace(/\r\n/g, "\n")))} ,
        footprint: { commit: STRICT_ASK_FOOTPRINT_COMMIT, path: strictAskFootprintPath, sha256: shaBytes(strictAskFootprintBytes), markdown_path: strictAskFootprintMdPath, markdown_sha256: shaBytes(strictAskFootprintMdBytes), frozen_legs: strictAskFootprint.FOOTPRINT.total, L6_misstamped_legs: strictAskFootprint.FOOTPRINT.by_chain_link.CHAIN_L6_PRESENT_BUT_NO_COUNTERPARTY, naked_knife_legs: strictAskFootprint.THE_FIX.ADVERSE.naked_unfrozen_legs, naked_knife_median_adverse_cents: strictAskFootprint.THE_FIX.ADVERSE.naked_only_distribution.median, role: "ANALYTICAL_FOOTPRINT_BINDING_NOT_EXECUTABLE_AGGREGATE" },
        PANFAL_forensic: { marks_path: panfalMarksPath, marks_sha256: shaBytes(panfalMarksBytes), timeline_path: panfalTimelinePath, timeline_sha256: shaBytes(panfalTimelineBytes), role: "ORDERED_NAMED_EXEMPLAR" },
        scoped_law: "ASK_GAP_GE_3_CREDITS_A_FALLING_REPRICE_DOWN_ONLY_WHEN_OTHER_EXPRESSION_ALREADY_CREDITED; OTHERWISE_V45_ACTION_UNCHANGED",
      }),
      "ATTRIBUTION_SCORECARD.json": canonical(v46AttributionScorecard),
      "GAP_CREDIT_RECEIPT.json": canonical(v46GapLedger.summary),
      "GAP_CREDIT_LEDGER.jsonl.gz": gzipRows(v46GapLedger.rows),
      "V45_V46_DIFFERENTIAL_RECEIPT.json": canonical(v46Differential),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v46Acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v46Acceptance.pass ? "PASS_OPERATIVE" : "BLOCKED_V45_REMAINS_OPERATIVE", operative_baseline: v46Acceptance.pass ? "V46_PAIR_GATED_GAP_CREDIT" : "V45_3bda0a54", reasons: [ ...(!v46Acceptance.baseline_reproduction.pass ? ["V45_BASELINE_REPRODUCTION_FAILED"] : []), ...(!v46Acceptance.completed_pairs.pass ? ["COMPLETION_BAR_FAILED"] : []), ...(!v46Acceptance.true_book_net_cents.pass ? ["TRUE_BOOK_BAR_FAILED"] : []), ...(!v46Acceptance.zero_bound_regressions.pass ? ["BOUND_REGRESSION"] : []), ...(!v46Acceptance.named_checks.pass ? ["NAMED_CHECK_FAILED"] : []) ], no_forced_values: true }),
      "NAMED_V46_RECEIPT.json": canonical(namedV46),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, receipt_path: fullBookReceiptPath, receipt_sha256: shaBytes(fullBookReceiptBytes), close_audit_path: closeAuditPath, close_audit_sha256: shaBytes(closeAuditBytes), close_column: "replay_close_cents", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })), acceptance: v46Acceptance }),
    } : {}),
    ...(isV45 ? {
      "V45_RECEIPT_BINDINGS.json": canonical({
        frozen_V43: { commit: V43_COMMIT, baseline_reproduction: v45BaselineReproduction },
        recalibration: { commit: V43_RECALIBRATION_COMMIT, path: v43RecalibrationPath, sha256: shaBytes(v43RecalibrationBytes), role: "WHOLE_GUARD_REMOVAL_COMPARISON_ONLY_NOT_IMPORTED" },
        residual_docket: { commit: V43_RESIDUAL_DOCKET_COMMIT, path: v43DocketPath, sha256: shaBytes(v43DocketBytes) },
        LUZTSE_forensic: { marks_path: luztseMarksPath, marks_sha256: shaBytes(luztseMarksBytes), timeline_path: luztseTimelinePath, timeline_sha256: shaBytes(luztseTimelineBytes), role: "POST_CREDIT_GUARD_WITHHOLD_EXEMPLAR" },
        scoped_law: "PRE_FILL_DEEP_GAP_GUARD_STAYS; ONLY_ACTIVE_WITHHOLD_ON_OTHER_LEG_TERMINATES_AT_SIBLING_CREDIT",
      }),
      "ATTRIBUTION_SCORECARD.json": canonical(v45AttributionScorecard),
      "RELEASED_REST_RECEIPT.json": canonical(v45ReleasedRestLedger.summary),
      "RELEASED_REST_LEDGER.jsonl.gz": gzipRows(v45ReleasedRestLedger.rows),
      "V43_V45_DIFFERENTIAL_RECEIPT.json": canonical(v45Differential),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v45Acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v45Acceptance.pass ? "PASS_OPERATIVE" : "BLOCKED_V43_REMAINS_OPERATIVE", operative_baseline: v45Acceptance.pass ? "V45_GUARD_RELEASE_AT_SIBLING_CREDIT" : "V43_01a58334", reasons: [ ...(!v45Acceptance.baseline_reproduction.pass ? ["V43_BASELINE_REPRODUCTION_FAILED"] : []), ...(!v45Acceptance.completed_pairs.pass ? ["COMPLETION_BAR_FAILED"] : []), ...(!v45Acceptance.true_book_net_cents.pass ? ["TRUE_BOOK_BAR_FAILED"] : []), ...(!v45Acceptance.naked_pnl_cents.pass ? ["NAKED_BOOK_DID_NOT_IMPROVE"] : []), ...(!v45Acceptance.named_checks.pass ? ["NAMED_CHECK_FAILED"] : []) ], no_forced_values: true }),
      "NAMED_V45_RECEIPT.json": canonical(namedV45),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, receipt_path: fullBookReceiptPath, receipt_sha256: shaBytes(fullBookReceiptBytes), close_audit_path: closeAuditPath, close_audit_sha256: shaBytes(closeAuditBytes), close_column: "replay_close_cents", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })), acceptance: v45Acceptance }),
    } : {}),
    ...(isV43 ? {
      "CLAUSE_BINDINGS.json": canonical({
        clause_1: { commit: ARM_FIRST_EVIDENCE_COMMIT, path: armFirstEvidencePath, sha256: shaBytes(armFirstEvidenceBytes), controlling_row: armFirstEvidenceReceipt.rows.ARM, included: "ARM_AT_FIRST_EVIDENCE_ONLY", explicitly_excluded: "WALK_LAG_REMOVAL" },
        clause_2: { commit: DEEP_GAP_CENSUS_COMMIT, path: deepGapCensusPath, sha256: shaBytes(deepGapCensusBytes), T10: { ...deepGapT10, derived_net_cents: (-deepGapT10.withheld_naked_loss_cents) - deepGapT10.completed_locked_forfeited_cents - deepGapT10.winning_naked_forfeited_cents }, full_book_method_commit: FULL_BOOK_PNL_COMMIT, full_book_method_path: fullBookReceiptPath, full_book_method_sha256: shaBytes(fullBookReceiptBytes) },
        clause_3: { commit: LOOSEN_ONE_CENT_COMMIT, path: loosenOneCentPath, sha256: shaBytes(loosenOneCentBytes), controlling_row: loosenOneCentReceipt.per_k["k=1"], law: loosenOneCentReceipt.law },
      }),
      "ATTRIBUTION_SCORECARD.json": canonical(v43AttributionScorecard),
      "DEEP_GAP_GUARD_ALONE_RECEIPT.json": canonical({ controlling_census: { commit: DEEP_GAP_CENSUS_COMMIT, T10: deepGapT10 }, score: attributionByName.get("C2_GUARD_ONLY"), differential_vs_V41: v43GuardOnlyDiff.aggregate }),
      "DEEP_GAP_GUARD_ALONE_DIFFERENTIAL_LEDGER.jsonl.gz": gzipRows(v43GuardOnlyDiff.rows),
      "COMBINED_DIFFERENTIAL_RECEIPT.json": canonical(v42Differential),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v43Acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v43Acceptance.pass ? "PASS" : "BLOCKED_NOT_OPERATIVE", operative_baseline: v43Acceptance.pass ? "V43_ALL_THREE" : "V41_96d33316", reasons: [
        ...(!v43Acceptance.receipt_single_clause_reproduction.pass ? ["ANALYSIS_ONLY_RECEIPT_PRICING_DOES_NOT_REPRODUCE_AS_EXECUTABLE_RECEIPT_CAUSAL_POLICY"] : []),
        ...(!v43Acceptance.named_regressions.pass ? ["MANDATORY_NAMED_IDENTITIES_CHANGED"] : []),
        ...(!v43Acceptance.completed_pairs.pass ? ["COMPLETION_BAR_FAILED"] : []),
        ...(!v43Acceptance.true_book_net_cents.pass ? ["TRUE_BOOK_BAR_FAILED"] : []),
      ], no_forced_values: true, no_operative_supersession_on_block: true }),
      "NAMED_V43_RECEIPT.json": canonical(namedV43),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, receipt_path: fullBookReceiptPath, receipt_sha256: shaBytes(fullBookReceiptBytes), close_audit_path: closeAuditPath, close_audit_sha256: shaBytes(closeAuditBytes), close_column: "replay_close_cents", audited_close_column_role: "NOT_CONSUMED_BY_A30F5CCD_FULL_BOOK_METHOD", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })), composition_bar: v43Acceptance }),
    } : {}),
    ...(isV42 ? {
      "DEEP_GAP_GUARD_RECEIPT.json": canonical({ law: control.architecture.clause, tolerance_cents: policy.DEEP_GAP_TOLERANCE_CENTS, controlling_census: { commit: DEEP_GAP_CENSUS_COMMIT, path: deepGapCensusPath, sha256: shaBytes(deepGapCensusBytes), T10: { ...deepGapT10, derived_net_cents: (-deepGapT10.withheld_naked_loss_cents) - deepGapT10.completed_locked_forfeited_cents - deepGapT10.winning_naked_forfeited_cents } }, market: { affected_legs: v42GuardLegs.length, withhold_episodes: v42GuardLegs.reduce((sum, row) => sum + row.withhold_episodes, 0), withheld_evaluations: v42GuardLegs.reduce((sum, row) => sum + row.withheld_evaluations, 0), lifts: v42GuardLegs.reduce((sum, row) => sum + row.lifts, 0), by_category_x_bell_confidence: countBy(v42GuardLegs, (row) => `${row.category}|${row.bell_confidence}`) }, two_columns: { losses_avoided: deepGapDiff.aggregate.losses_avoided, pairs_and_winners_forfeited: { completed_pairs: deepGapDiff.aggregate.pairs_forfeited, winning_naked: deepGapDiff.aggregate.winning_naked_forfeited } }, actual_full_book_delta_cents: v42FullBook.aggregate.true_book_net_cents - v41FullBook.aggregate.true_book_net_cents }),
      "DEEP_GAP_GUARD_LEG_LEDGER.jsonl.gz": gzipRows(v42GuardLegs),
      "DEEP_GAP_DIFFERENTIAL_RECEIPT.json": canonical(v42Differential),
      "DEEP_GAP_OUTCOME_DIFFERENTIAL.json": canonical(deepGapDiff.aggregate),
      "DEEP_GAP_OUTCOME_DIFFERENTIAL_LEDGER.jsonl.gz": gzipRows(deepGapDiff.rows),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, receipt_path: fullBookReceiptPath, receipt_sha256: shaBytes(fullBookReceiptBytes), close_audit_path: closeAuditPath, close_audit_sha256: shaBytes(closeAuditBytes), close_column: "replay_close_cents", audited_close_column_role: "NOT_CONSUMED_BY_A30F5CCD_FULL_BOOK_METHOD", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, V41_reconstructed: v41FullBook.aggregate, V42: v42FullBook.aggregate, by_category: v42FullBook.by_category, delta_cents: v42FullBook.aggregate.true_book_net_cents - v41FullBook.aggregate.true_book_net_cents, acceptance: v42Acceptance }),
      "FULL_BOOK_EVENT_LEDGER.jsonl.gz": gzipRows(v42FullBook.rows),
      "ACCEPTANCE_BAR.json": canonical(v42Acceptance),
      "NAMED_V42_RECEIPT.json": canonical(namedV42),
    } : {}),
    "MARKET_EVENT_LEDGER.jsonl.gz": gzipRows(marketEvents),
    "STRICT_EVENT_LEDGER.jsonl.gz": gzipRows(strictEvents),
    "DECISION_TRACE_1608.jsonl.gz": gzipRows((isTradeTruthVariant ? attributionByName.get(isV52 ? "V52_JUDGMENT_GATE" : isV49b ? "V49B_FAITHFUL_STAND_AT_P" : isV49 ? "V49_EVIDENCED_LEVEL_STANDING" : "TRADE_TRUTH_V47_INCUMBENT").traded_floor_rows : marketGrades.rows).map((row) => ({ ...row, ...(isTradeTruthVariant ? {} : { reach_snapshot: row.reach_snapshot }), first_decision: marketEvents.find((event) => event.event_id === row.event_id).legs[row.leg_identity.split("|").at(-1)].first_decision, last_decision: marketEvents.find((event) => event.event_id === row.event_id).legs[row.leg_identity.split("|").at(-1)].last_decision }))),
    "NAMED_GAMES.json": canonical({ games: named, action_rows: allActions.filter((row) => namedLabels.some((name) => row.event_id.includes(name)) && (row.kind === "FILL" || String(row.kind).includes("DEEP_GAP") || String(row.kind).includes("POST_CREDIT") || String(row.kind).includes("GAP_CREDIT") || String(row.reason).includes("PERSISTENT") || String(row.reason).includes("FIRST_OBSERVATION") || String(row.reason).includes("ONE_CENT_LESS_GREEDY") || String(row.reason).includes("WTA_OTHER_EXPRESSION_FALLING"))) }),
    ...(isV39 ? { "NAMED_CAUSALITY_RECEIPT.json": canonical(namedCausality) } : {}),
    ...(isV40 ? { "NAMED_V40_RECEIPT.json": canonical(namedV40) } : {}),
    "FORBIDDEN_ACCESS_RECEIPT.json": canonical({ holdout_accesses: 0, live_accesses: 0, network_runtime_accesses: 0, order_accesses: 0, position_accesses: 0, exit_accesses: 0, settlement_accesses: 0, DCA_accesses: 0, deployment_accesses: 0, private_scope: "FIT_DEVELOPMENT_804_TAPE_AND_CERTIFIED_PRINT_CACHE_ONLY", mutations: 0 }),
    "SOURCE_HASH_MANIFEST.json": canonical({
      commits: { V36: V36_COMMIT, UNION_REACH: REACH_COMMIT, GAP_GRADE_PARENT: GAP_COMMIT, DIVOT_CENSUS: DIVOT_COMMIT, ...(isPlacementStack ? { COUNTERFACTUAL: COUNTERFACTUAL_COMMIT } : {}), ...(isV39 ? { FALLER_ANATOMY: FALLER_ANATOMY_COMMIT } : {}), ...(isV40 ? { V39_EVIDENCE_PACKAGE: "ff5880d11a88b0d12415f5371d7cbb61331957e4" } : {}), ...(isMaker41 ? { CAUSAL_REACH: CAUSAL_REACH_COMMIT, RISER_TRIGGER_FRONTIER: RISER_FRONTIER_COMMIT, LEVEL_POLICY_REALIZATION: LEVEL_POLICY_COMMIT } : {}), ...(hasDeepGap ? { V41_PACKAGE: V41_COMMIT, DEEP_GAP_CENSUS: DEEP_GAP_CENSUS_COMMIT, FULL_BOOK_PNL_METHOD: FULL_BOOK_PNL_COMMIT } : {}), ...(isAttribution ? { ARM_FIRST_EVIDENCE: ARM_FIRST_EVIDENCE_COMMIT, LOOSEN_ONE_CENT: LOOSEN_ONE_CENT_COMMIT } : {}), ...(isV45 ? { V43_OPERATIVE: V43_COMMIT, V43_RECALIBRATION: V43_RECALIBRATION_COMMIT, V43_RESIDUAL_DOCKET: V43_RESIDUAL_DOCKET_COMMIT } : {}), ...(isV46 ? { V45_OPERATIVE: V45_COMMIT, STRICT_ASK_CREDIT_FOOTPRINT: STRICT_ASK_FOOTPRINT_COMMIT } : {}), ...(isV47 ? { V45_OPERATIVE: V45_COMMIT, SURECH_RENDER: SURECH_RENDER_COMMIT } : {}), ...(isV48 ? { V47_OPERATIVE: V47_COMMIT, TRADES_TRUTH_RECUT: TRADES_TRUTH_RECUT_COMMIT } : {}), ...(isV49 ? { V47_OPERATIVE: V47_COMMIT, STANDABILITY_V2: STANDABILITY_V2_COMMIT, HERKAZ_EXEMPLAR: HERKAZ_EXEMPLAR_COMMIT } : {}), ...(isV49b ? { V47_OPERATIVE: V47_COMMIT, SUBSTITUTION_AUDIT: SUBSTITUTION_AUDIT_COMMIT, STANDABILITY_V2: STANDABILITY_V2_COMMIT, DECISION_CHAIN_81: DECISION_CHAIN_81_COMMIT, IDENTITY_81: IDENTITY_81_COMMIT, CAUSAL_FLOOR_CONVICTION: CAUSAL_FLOOR_CONVICTION_COMMIT, SEALED_V47_EXAM: SEALED_V47_EXAM_COMMIT } : {}) },
      ...(isV52 ? { V52_CONTROLLING_COMMITS: { V49B_FROZEN_BASE: V49B_COMMIT, REFLEX_POST_CENSUS: REFLEX_CENSUS_COMMIT, STABILITY_ONSET_METHOD: STABILITY_ONSET_COMMIT, FIVE_GAME_TAPE_PACKS: FIVE_GAME_TAPE_PACK_COMMIT } } : {}),
      public: {
        [path.relative(repo, policyFile).replaceAll("\\", "/")]: { sha256: fileHash(policyFile), bytes: fs.statSync(policyFile).size },
        [path.relative(repo, builderFile).replaceAll("\\", "/")]: { sha256: fileHash(builderFile), bytes: fs.statSync(builderFile).size },
        ...(isPlacementStack ? { [path.relative(repo, wrapperFile).replaceAll("\\", "/")]: { sha256: fileHash(wrapperFile), bytes: fs.statSync(wrapperFile).size } } : {}),
        ...(isV41 ? {
          "arb-executor/tests/test_window1_v41_maker_machine.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v41_maker_machine.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v41_maker_machine.js")).size },
          "arb-executor/tests/test_window1_v41_maker_machine_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v41_maker_machine_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v41_maker_machine_package.js")).size },
        } : {}),
        ...(hasDeepGap ? {
          "arb-executor/analysis/window1_v41_maker_machine.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v41_maker_machine.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v41_maker_machine.js")).size },
          "arb-executor/analysis/window1_v42_deep_gap_feasibility_guard.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v42_deep_gap_feasibility_guard.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v42_deep_gap_feasibility_guard.js")).size },
          "arb-executor/tests/test_window1_v42_deep_gap_feasibility_guard.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v42_deep_gap_feasibility_guard.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v42_deep_gap_feasibility_guard.js")).size },
          "arb-executor/tests/test_window1_v42_deep_gap_feasibility_guard_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v42_deep_gap_feasibility_guard_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v42_deep_gap_feasibility_guard_package.js")).size },
          [v41LedgerPath]: { sha256: fileHash(path.join(repo, v41LedgerPath)), bytes: fs.statSync(path.join(repo, v41LedgerPath)).size },
        } : {}),
        ...(isV43 ? {
          "arb-executor/tests/test_window1_v43_composed_machine.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v43_composed_machine.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v43_composed_machine.js")).size },
          "arb-executor/tests/test_window1_v43_composed_machine_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v43_composed_machine_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v43_composed_machine_package.js")).size },
        } : {}),
        ...(isV45 ? {
          "arb-executor/analysis/window1_v43_composed_machine.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v43_composed_machine.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v43_composed_machine.js")).size },
          "arb-executor/tests/test_window1_v45_guard_release_sibling_credit.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v45_guard_release_sibling_credit.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v45_guard_release_sibling_credit.js")).size },
          "arb-executor/tests/test_window1_v45_guard_release_sibling_credit_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v45_guard_release_sibling_credit_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v45_guard_release_sibling_credit_package.js")).size },
        } : {}),
        ...(isV46 ? {
          "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js")).size },
          "arb-executor/tests/test_window1_v46_pair_gated_gap_credit.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v46_pair_gated_gap_credit.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v46_pair_gated_gap_credit.js")).size },
          "arb-executor/tests/test_window1_v46_pair_gated_gap_credit_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v46_pair_gated_gap_credit_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v46_pair_gated_gap_credit_package.js")).size },
        } : {}),
        ...(isV47 ? {
          "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js")).size },
          "arb-executor/tests/test_window1_v47_same_tick_arm.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v47_same_tick_arm.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v47_same_tick_arm.js")).size },
          "arb-executor/tests/test_window1_v47_same_tick_arm_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v47_same_tick_arm_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v47_same_tick_arm_package.js")).size },
        } : {}),
        ...(isV48 ? {
          "arb-executor/analysis/window1_v47_same_tick_arm.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v47_same_tick_arm.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v47_same_tick_arm.js")).size },
          "arb-executor/tests/test_window1_v48_trades_as_truth.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v48_trades_as_truth.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v48_trades_as_truth.js")).size },
          "arb-executor/tests/test_window1_v48_trades_as_truth_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v48_trades_as_truth_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v48_trades_as_truth_package.js")).size },
        } : {}),
        ...(isV49 ? {
          "arb-executor/analysis/window1_v47_same_tick_arm.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v47_same_tick_arm.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v47_same_tick_arm.js")).size },
          "arb-executor/tests/test_window1_v49_evidenced_level_standing.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v49_evidenced_level_standing.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v49_evidenced_level_standing.js")).size },
          "arb-executor/tests/test_window1_v49_evidenced_level_standing_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v49_evidenced_level_standing_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v49_evidenced_level_standing_package.js")).size },
        } : {}),
        ...(isV49b ? {
          "arb-executor/analysis/window1_v47_same_tick_arm.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v47_same_tick_arm.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v47_same_tick_arm.js")).size },
          "arb-executor/tests/test_window1_v49b_faithful_stand_at_p.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v49b_faithful_stand_at_p.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v49b_faithful_stand_at_p.js")).size },
        } : {}),
        ...(isV52 ? {
          "arb-executor/analysis/window1_v52_stability_onset.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52_stability_onset.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v52_stability_onset.js")).size },
          "arb-executor/tests/test_window1_v52_judgment_gate.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52_judgment_gate.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v52_judgment_gate.js")).size },
          "arb-executor/tests/test_window1_v52_judgment_gate_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52_judgment_gate_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v52_judgment_gate_package.js")).size },
        } : {}),
        ...(isV40 ? { [v39TelemetryPath]: { sha256: fileHash(path.join(repo, v39TelemetryPath)), bytes: fs.statSync(path.join(repo, v39TelemetryPath)).size } } : {}),
        [`${GAP_PACKAGE}/UNION_REACH_LEG_LEDGER.jsonl.gz`]: { sha256: fileHash(path.join(gapPackage, "UNION_REACH_LEG_LEDGER.jsonl.gz")), bytes: fs.statSync(path.join(gapPackage, "UNION_REACH_LEG_LEDGER.jsonl.gz")).size },
        [`${GAP_PACKAGE}/V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz`]: { sha256: fileHash(path.join(gapPackage, "V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz")), bytes: fs.statSync(path.join(gapPackage, "V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz")).size },
      },
      frozen_V36: { WINDOW1_SPAN_804: { sha256: fileHash(path.join(v36Package, "WINDOW1_SPAN_804.json")), bytes: fs.statSync(path.join(v36Package, "WINDOW1_SPAN_804.json")).size }, STRICT_DECISION_TRACE_1608: { sha256: fileHash(path.join(v36Package, "STRICT_DECISION_TRACE_1608.json")), bytes: fs.statSync(path.join(v36Package, "STRICT_DECISION_TRACE_1608.json")).size } },
      git_bound_receipts: isPlacementStack ? { [counterPath]: { commit: COUNTERFACTUAL_COMMIT, sha256: shaBytes(counterBytes), bytes: counterBytes.length }, ...(isV39 ? { [anatomyPath]: { commit: FALLER_ANATOMY_COMMIT, sha256: shaBytes(anatomyBytes), bytes: anatomyBytes.length } } : {}), ...(isMaker41 ? { [causalReachPath]: { commit: CAUSAL_REACH_COMMIT, sha256: shaBytes(causalReachBytes), bytes: causalReachBytes.length }, [riserFrontierPath]: { commit: RISER_FRONTIER_COMMIT, sha256: shaBytes(riserFrontierBytes), bytes: riserFrontierBytes.length }, [levelPolicyPath]: { commit: LEVEL_POLICY_COMMIT, sha256: shaBytes(levelPolicyBytes), bytes: levelPolicyBytes.length } } : {}), ...(hasDeepGap ? { [deepGapCensusPath]: { commit: DEEP_GAP_CENSUS_COMMIT, sha256: shaBytes(deepGapCensusBytes), bytes: deepGapCensusBytes.length }, [fullBookReceiptPath]: { commit: FULL_BOOK_PNL_COMMIT, sha256: shaBytes(fullBookReceiptBytes), bytes: fullBookReceiptBytes.length }, [closeAuditPath]: { commit: FULL_BOOK_PNL_COMMIT, sha256: shaBytes(closeAuditBytes), bytes: closeAuditBytes.length } } : {}), ...(isAttribution ? { [armFirstEvidencePath]: { commit: ARM_FIRST_EVIDENCE_COMMIT, sha256: shaBytes(armFirstEvidenceBytes), bytes: armFirstEvidenceBytes.length }, [loosenOneCentPath]: { commit: LOOSEN_ONE_CENT_COMMIT, sha256: shaBytes(loosenOneCentBytes), bytes: loosenOneCentBytes.length } } : {}), ...(isV45 ? { [v43RecalibrationPath]: { commit: V43_RECALIBRATION_COMMIT, sha256: shaBytes(v43RecalibrationBytes), bytes: v43RecalibrationBytes.length }, [v43DocketPath]: { commit: V43_RESIDUAL_DOCKET_COMMIT, sha256: shaBytes(v43DocketBytes), bytes: v43DocketBytes.length }, [luztseMarksPath]: { commit: V43_RESIDUAL_DOCKET_COMMIT, sha256: shaBytes(luztseMarksBytes), bytes: luztseMarksBytes.length }, [luztseTimelinePath]: { commit: V43_RESIDUAL_DOCKET_COMMIT, sha256: shaBytes(luztseTimelineBytes), bytes: luztseTimelineBytes.length } } : {}), ...(isV46 ? { [frozenV45ControlPath]: { commit: V45_COMMIT, sha256: shaBytes(frozenV45ControlBytes), bytes: frozenV45ControlBytes.length }, [frozenV45ScorePath]: { commit: V45_COMMIT, sha256: shaBytes(frozenV45ScoreBytes), bytes: frozenV45ScoreBytes.length }, [frozenV45PolicyPath]: { commit: V45_COMMIT, sha256: shaBytes(frozenV45PolicyBytes), bytes: frozenV45PolicyBytes.length }, [strictAskFootprintPath]: { commit: STRICT_ASK_FOOTPRINT_COMMIT, sha256: shaBytes(strictAskFootprintBytes), bytes: strictAskFootprintBytes.length }, [strictAskFootprintMdPath]: { commit: STRICT_ASK_FOOTPRINT_COMMIT, sha256: shaBytes(strictAskFootprintMdBytes), bytes: strictAskFootprintMdBytes.length }, [panfalMarksPath]: { commit: STRICT_ASK_FOOTPRINT_COMMIT, sha256: shaBytes(panfalMarksBytes), bytes: panfalMarksBytes.length }, [panfalTimelinePath]: { commit: STRICT_ASK_FOOTPRINT_COMMIT, sha256: shaBytes(panfalTimelineBytes), bytes: panfalTimelineBytes.length } } : {}), ...(isV48 ? { [tradesTruthRecutPath]: { commit: TRADES_TRUTH_RECUT_COMMIT, sha256: shaBytes(tradesTruthRecutBytes), bytes: tradesTruthRecutBytes.length }, [tradesTruthRecutMdPath]: { commit: TRADES_TRUTH_RECUT_COMMIT, sha256: shaBytes(tradesTruthRecutMdBytes), bytes: tradesTruthRecutMdBytes.length } } : {}), ...(isV49 ? { [standabilityPath]: { commit: STANDABILITY_V2_COMMIT, sha256: shaBytes(standabilityBytes), bytes: standabilityBytes.length }, [standabilityMdPath]: { commit: STANDABILITY_V2_COMMIT, sha256: shaBytes(standabilityMdBytes), bytes: standabilityMdBytes.length }, [herkazPath]: { commit: HERKAZ_EXEMPLAR_COMMIT, sha256: shaBytes(herkazBytes), bytes: herkazBytes.length }, [herkazMarksPath]: { commit: HERKAZ_EXEMPLAR_COMMIT, sha256: shaBytes(herkazMarksBytes), bytes: herkazMarksBytes.length }, [herkazTimelinePath]: { commit: HERKAZ_EXEMPLAR_COMMIT, sha256: shaBytes(herkazTimelineBytes), bytes: herkazTimelineBytes.length } } : {}) } : {},
      ...(isV52 ? { V52_BOUND_INPUTS: {
        [v52TapePackPath]: { commit: FIVE_GAME_TAPE_PACK_COMMIT, sha256: shaBytes(v52TapePackBytes), bytes: v52TapePackBytes.length },
        [v52OnsetReceiptPath]: { commit: STABILITY_ONSET_COMMIT, sha256: shaBytes(v52OnsetReceiptBytes), bytes: v52OnsetReceiptBytes.length },
        ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json": { commit: REFLEX_CENSUS_COMMIT, sha256: shaBytes(gitShow(REFLEX_CENSUS_COMMIT, ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json")) },
      } } : {}),
      private_prints: printLoad.receipt,
      private_tapes: tapeHashes,
    }),
  };
  for (const [name, bytes] of Object.entries(core)) write(name, bytes);
  if (isAttribution) {
    async function* attributionEvents(kind) {
      for (const spec of machineSpecs) for (const event of machineRuns.get(spec.name)[kind]) yield { machine: spec.name, clauses: policy.normalizedClauses(spec.clauses), ...event };
    }
    async function* attributionFullBookRows() {
      for (const row of attributionRows) for (const event of row.full_book_rows) yield { machine: row.machine, clauses: row.clauses, ...event };
    }
    await writeGzipRowsFile(path.join(output, "ATTRIBUTION_MARKET_EVENT_LEDGER.jsonl.gz"), attributionEvents("marketEvents"));
    await writeGzipRowsFile(path.join(output, "ATTRIBUTION_STRICT_EVENT_LEDGER.jsonl.gz"), attributionEvents("strictEvents"));
    await writeGzipRowsFile(path.join(output, "ATTRIBUTION_FULL_BOOK_LEDGER.jsonl.gz"), attributionFullBookRows());
  }
  await writeGzipRowsFile(path.join(output, "ACTION_TRACE.jsonl.gz"), allActions);
  write("REPORT.md", isV52
    ? `# V52 judgment gate — ${v52Package.acceptance.pass ? "PASS" : "BLOCKED / V49b REMAINS FROZEN BASELINE"}\n\nV52 changes rest birth only. A rest is licensed after stability onset, a causal machine read, an own post-onset true-trade diary value, and pair-coherent post-onset lows. Displayed bids name no V52 level. A disagreement blocks until it clears or the sibling credits. Scavenger is specified OFF. Crediting remains frozen trades-as-truth.\n\n- Stage 1: ${v52Package.stage1Flow.pass ? "PASS" : "BLOCKED"}; five games, ${v52Package.stage1Flow.post_actions} rest mutations, zero pre-onset/NO_TAPE/displayed-bid/unlicensed/scavenger violations. Outcomes were observation-only and caused no policy edits.\n- One-shot dev 804: market completed ${marketScore.completed_pairs}, under par ${marketScore.under_par_pairs}, frontier <=93/<=95/<=97/<100/any ${marketScore.frontier.LE_93}/${marketScore.frontier.LE_95}/${marketScore.frontier.LE_97}/${marketScore.frontier.LT_100}/${marketScore.frontier.ANY_PRICE}.\n- Strict build verification: completed ${strictScore.completed_pairs}, under par ${strictScore.under_par_pairs}, frontier ${strictScore.frontier.LE_93}/${strictScore.frontier.LE_95}/${strictScore.frontier.LE_97}/${strictScore.frontier.LT_100}/${strictScore.frontier.ANY_PRICE}.\n- Three states: ${JSON.stringify(v52Package.stateCensus.states)}; conservation ${v52Package.stateCensus.conservation.rows}/804.\n- Posting: first posts ${v52Package.postingReceipt.first_posts}; rest mutations ${v52Package.postingReceipt.rest_mutations}; REFLEX_POST ${v52Package.postingReceipt.REFLEX_POST}; read states ${JSON.stringify(v52Package.postingReceipt.read_states_at_first_post)}.\n- V49b frozen scorecards reproduced byte-identically: ${v52Package.baselineReproduction.pass ? "PASS" : "FAIL"}. V49b→V52 changed leg streams ${v52Package.differential.aggregate.changed_leg_streams}.\n- Named observations: ARSMAR ${v52Package.namedRows.ARSMAR.completed ? `complete ${v52Package.namedRows.ARSMAR.combined_entry_cents}` : "incomplete"}; POLKUH ${v52Package.namedRows.POLKUH.completed ? `complete ${v52Package.namedRows.POLKUH.combined_entry_cents}` : "incomplete"}; SANDAN ${v52Package.namedRows.SANDAN.completed ? `complete ${v52Package.namedRows.SANDAN.combined_entry_cents}` : "incomplete"}; PUTJEA ${v52Package.namedRows.PUTJEA.completed ? `complete ${v52Package.namedRows.PUTJEA.combined_entry_cents}` : "lawful sit-out/incomplete"}; MERDRO credited-as-judgment ${v52Package.namedChecks.MERDRO_not_credited_as_judgment ? "NO" : "YES"}.\n- Mechanism-bound checks: ${JSON.stringify(v52Package.namedChecks)}. Overall ${v52Package.acceptance.pass ? "PASS" : "BLOCKED"}. Aggregate completions were not tuned or forced. No deployment.\n`
    : isV49b
    ? `# V49b faithful stand-at-P — ${v49bPackage.acceptance.ratified ? "PASS / RATIFIED" : "BLOCKED / V47 REMAINS OPERATIVE"}\n\nV49b is one narrow replay variant on frozen V47. On the 93 hash-bound doctrine legs, after causal own-tape evidence names P, it posts the rest at exactly P. It performs no bid-minus-one or synthetic-book substitution. V47 remains byte-identical where doctrine authority is absent; after authority exists, an exact-P cap/sanity conflict abstains rather than substituting another price.\n\n- CANON trades-truth: completed ${marketScore.completed_pairs}; under par ${marketScore.under_par_pairs}; frontier <=93/<=95/<=97/<100/any ${marketScore.frontier.LE_93}/${marketScore.frontier.LE_95}/${marketScore.frontier.LE_97}/${marketScore.frontier.LT_100}/${marketScore.frontier.ANY_PRICE}.\n- Strict print-cross build verification: completed ${strictScore.completed_pairs}; under par ${strictScore.under_par_pairs}; frontier ${strictScore.frontier.LE_93}/${strictScore.frontier.LE_95}/${strictScore.frontier.LE_97}/${strictScore.frontier.LT_100}/${strictScore.frontier.ANY_PRICE}.\n- Frozen V47 baseline reproduction: ${v49BaselineReproduction.pass ? "PASS" : "FAIL"}.\n- Mechanism: dominant code ${v49bPackage.acceptance.mechanism.dominant_code}; exact AT_P action rows ${v49bPackage.acceptance.mechanism.exact_AT_P_action_rows}; BID_MINUS_ONE rows on doctrine legs ${v49bPackage.acceptance.mechanism.BID_MINUS_ONE_rows_on_doctrine_legs}; invariant violations ${v49bPackage.acceptance.mechanism.exact_target_invariant_violations}.\n- Bound-instrument improvements ${v49bPackage.acceptance.strict_improvements_on_bound_instrument}; regressions ${v49bPackage.acceptance.bound_regressions}. The 81-game ledger completes with every doctrine leg at its own P or better in ${v49bPackage.acceptance.named_81_games_at_or_better}/81 games; failures remain explicitly enumerated.\n- Depth shares at <=97: sealed V47 ${(100 * v49bPackage.depthShares.sealed_V47.share).toFixed(1)}%; dev V47 ${(100 * v49bPackage.depthShares.dev_V47.share).toFixed(1)}%; dev V49b ${(100 * v49bPackage.depthShares.dev_V49b.share).toFixed(1)}%. Added completions ${v49bPackage.depthShares.V49b_added_completions.n}, <=97 ${v49bPackage.depthShares.V49b_added_completions.LE_97}; shallow skew ${v49bPackage.depthShares.V49b_added_completions.skew_shallow ? "YES" : "NO"}.\n- REGRET GAUGE is stamped OPTIMISTIC_EX_POST_TRUE_TRADE_FLOOR. The convicted d3db740f causal-floor table is consumed by zero V49b decisions.\n- Acceptance uses mechanism-bound instruments only: ${v49bPackage.acceptance.ratified ? "RATIFIED" : "BLOCKED"}.\n`
    : isV49
    ? `# V49 evidenced-level standing - ${v49Acceptance.pass ? "PASS" : "BLOCKED / V47 REMAINS OPERATIVE"}\n\nV49 replaces V47's universal tracking-rest +1-cent loosen with one causal rule: stand at current best bid P only after an earlier true trade printed at-or-below P or the own best bid continuously stood at P for V47's inherited ${policy.PERSISTENT_LEVEL_SECONDS}-second persistence interval. A historical bid sighting alone has no authority. Without either receipt the bid-minus-one tracker runs; persistent joins and WTA holds are never overwritten. Pair cap, post-only sanity, deep-gap guard, sibling-credit release, same-tick arming, and the hard edge remain unchanged.\n\n${attributionRows.map((row) => `- ${row.machine}: completed ${row.MARKET.completed_pairs}, under par ${row.MARKET.under_par_pairs}, locked ${row.FULL_BOOK.completed_locked_cents}c, naked ${row.FULL_BOOK.naked_pnl_cents}c, true book ${row.FULL_BOOK.true_book_net_cents}c, frontier ${row.MARKET.frontier.LE_93}/${row.MARKET.frontier.LE_95}/${row.MARKET.frontier.LE_97}/${row.MARKET.frontier.LT_100}; strict ${row.STRICT_PRINT_CROSS.completed_pairs}.`).join("\n")}\n\n- Frozen V47 trades-as-truth baseline reproduction: ${v49BaselineReproduction.pass ? "PASS" : "FAIL"}.\n- Evidenced-standing actions / legs / games: ${v49EvidenceLedger.summary.evidenced_actions}/${v49EvidenceLedger.summary.evidenced_legs}/${v49EvidenceLedger.summary.evidenced_games}.\n- Outcome columns: gained ${v49EvidenceLedger.summary.fills_gained}; favorable reprices ${v49EvidenceLedger.summary.fills_repriced_favorable}; adverse reprices ${v49EvidenceLedger.summary.fills_repriced_adverse}; lost ${v49EvidenceLedger.summary.fills_lost}.\n- HERKAZ: ${namedV49.rows.HERKAZ.V49.combined_entry_cents ?? "INCOMPLETE"}; HER ${namedV49.rows.HERKAZ.V49.legs.HER.entry_cents ?? "UNFILLED"}; named mechanism ${namedV49.assertions.HERKAZ_HER_trade_truth_fill ? "PASS" : "FAIL"}.\n- fe4747cd freezes 81 games / 1,162c only as aggregate. It exposes 20 detailed WINDOW_LAWFUL_EVIDENCE identities; ${v49WindowTarget.detailed_at_or_better}/${v49WindowTarget.detailed_rows} are credited at-or-better and ${v49WindowTarget.detailed_pair_conversions} convert. Whole-population executable pair conversions versus V47: ${v49WindowTarget.executable_all_population_pair_conversions_vs_V47}. No unstated 81-row intersection was fabricated.\n- Bound named regressions: ${namedV49.pass ? "ZERO" : "PRESENT"}. Aggregate targets are null; observed values were not forced.\n- Overall: ${v49Acceptance.pass ? "PASS" : "BLOCKED"}.\n`
    : isV48
    ? `# V48 trades-as-truth crediting - ${v48Acceptance.pass ? "PASS" : "BLOCKED / V47 REMAINS OPERATIVE"}\n\nV48 changes one credit law on frozen V47: a lawful standing rest credits when any identified true trade prints at-or-below its level strictly after the rest stood. Ask observations remain placement inputs only. Aggressor side, dwell, displayed size, arrival direction, and the prior channel taxonomy are not credit filters or floor inputs. Strict seller-aggressed print crossing remains a separate build-verification ruler.\n\n${attributionRows.map((row) => `- ${row.machine} [${row.market_mode}]: completed ${row.MARKET.completed_pairs}, under par ${row.MARKET.under_par_pairs}, locked ${row.FULL_BOOK.completed_locked_cents}c, naked ${row.FULL_BOOK.naked_pnl_cents}c, true book ${row.FULL_BOOK.true_book_net_cents}c, frontier ${row.MARKET.frontier.LE_93}/${row.MARKET.frontier.LE_95}/${row.MARKET.frontier.LE_97}/${row.MARKET.frontier.LT_100}; strict ${row.STRICT_PRINT_CROSS.completed_pairs}.`).join("\n")}\n\n- Frozen V47 reproduction: ${v48BaselineReproduction.pass ? "PASS" : "FAIL"}.\n- The operative V47 placement stack is mixed; it is not mislabeled bid-1. The three requested executable rungs are scored independently.\n- Selected ladder by frozen full-book-first rule: ${v48SelectedRung}.\n- Traded-floor re-sum: ${JSON.stringify(v48TradedFloors.aggregate.traded_floor_classes)}; flips ${JSON.stringify(v48TradedFloors.aggregate.flips)}.\n- LUZTSE|TSE credit receipt: ${namedV48.LUZTSE_TSE.pass ? "PASS" : "FAIL"}; ${namedV48.LUZTSE_TSE.fills.length ? JSON.stringify(namedV48.LUZTSE_TSE.fills[0].evidence) : "NO QUALIFYING PRINT"}.\n- SALIBR|IBR outcomes are frozen rung-by-rung in NAMED_V48_RECEIPT.json.\n- Bound named regressions: ${namedV48.pass ? "ZERO" : "PRESENT"}. Aggregate targets were intentionally null; observed numbers were not forced.\n- Overall: ${v48Acceptance.pass ? "PASS" : "BLOCKED"}.\n`
    : isV47
    ? `# V47 same-tick arm - ${v47Acceptance.pass ? "PASS / OPERATIVE" : "BLOCKED / V45 REMAINS OPERATIVE"}\n\nV47 freezes one pipeline-correctness invariant on operative V45: a changed deep-join qualification and the placement decision are one receipt-local operation. Persistence, first-evidence arming, targets, guards, caps, sanity, fill rulers, and the hard edge are unchanged.\n\n${attributionRows.map((row) => `- ${row.machine}: completed ${row.MARKET_UNION_REACH.completed_pairs}, under par ${row.MARKET_UNION_REACH.under_par_pairs}, locked ${row.FULL_BOOK.completed_locked_cents}c, naked ${row.FULL_BOOK.naked_pnl_cents}c, true book ${row.FULL_BOOK.true_book_net_cents}c, frontier ${row.MARKET_UNION_REACH.frontier.LE_93}/${row.MARKET_UNION_REACH.frontier.LE_95}/${row.MARKET_UNION_REACH.frontier.LE_97}/${row.MARKET_UNION_REACH.frontier.LT_100}; strict ${row.STRICT_PRINT_CROSS.completed_pairs}.`).join("\n")}\n\n- Frozen V45 reproduction: ${v47BaselineReproduction.pass ? "PASS" : "FAIL"}.\n- SEG_C qualification rows: ${v47SegCFootprint.summary.qualification_rows}; V45/V47 positive qualification-to-post rows ${v47SegCFootprint.summary.V45_positive_qualification_to_post_rows}/${v47SegCFootprint.summary.V47_positive_qualification_to_post_rows}; V47 positive scheduler-latency rows ${v47SegCFootprint.summary.V47_positive_scheduler_latency_rows}. Qualification-to-post delay caused by an unchanged guard is reported separately and is not scheduler latency.\n- Changed outcomes: ${v47SegCFootprint.summary.outcome_changed_rows}; changed action streams: ${v47Differential.changed_leg_streams}.\n- SURECH remains unfilled as ordered; the 8877c2d5 render is older L4 archetype evidence, not a frozen V45 trace. The executable V45 baseline already posted each unguarded changed join on its qualifying receipt, so V47's correctness invariant yields zero score delta rather than a manufactured gain.\n- Named zero-regression checks: ${namedV47.pass ? "PASS" : "FAIL"}.\n- Acceptance: zero scheduler latency ${v47Acceptance.correctness.pass ? "PASS" : "FAIL"}; zero regressions ${v47Acceptance.zero_regressions.pass ? "PASS" : "FAIL"}; gain required NO; overall ${v47Acceptance.pass ? "PASS" : "BLOCKED"}.\n- Market value uses CANON union channels; strict print crossing remains build verification only.\n`
    : isV46
    ? `# V46 pair-gated gap credit - ${v46Acceptance.pass ? "PASS / OPERATIVE" : "BLOCKED / V45 REMAINS OPERATIVE"}\n\nV46 adds one clause to frozen operative V45: on a FALLING leg with an existing rest, a single-receipt ask gap of at least ${policy.ASK_GAP_CREDIT_MIN_CENTS} cents licenses a reprice down only after the game's other expression is already credited. Without sibling credit the V45 action stream is unchanged. The reprice posts at min(current ask minus one, pair cap); fills still require an inherited later market-union or strict-print receipt.\n\n${attributionRows.map((row) => `- ${row.machine}: completed ${row.MARKET_UNION_REACH.completed_pairs}, under par ${row.MARKET_UNION_REACH.under_par_pairs}, locked ${row.FULL_BOOK.completed_locked_cents}c, naked ${row.FULL_BOOK.naked_pnl_cents}c, true book ${row.FULL_BOOK.true_book_net_cents}c, frontier ${row.MARKET_UNION_REACH.frontier.LE_93}/${row.MARKET_UNION_REACH.frontier.LE_95}/${row.MARKET_UNION_REACH.frontier.LE_97}/${row.MARKET_UNION_REACH.frontier.LT_100}; strict ${row.STRICT_PRINT_CROSS.completed_pairs}.`).join("\n")}\n\n- Frozen V45 reproduction: ${v46BaselineReproduction.pass ? "PASS" : "FAIL"}.\n- Gap-credit walks: ${v46GapLedger.summary.authorized_walks} across ${v46GapLedger.summary.authorized_legs} legs; filled ${v46GapLedger.summary.authorized_walks_that_filled}.\n- Two columns: completion gains ${v46GapLedger.summary.two_columns.pairs_completed.events}; new exposure ${v46GapLedger.summary.two_columns.new_exposure.events}.\n- Sibling-uncredited refusal receipts: ${v46GapLedger.summary.sibling_uncredited_refusal_receipts} across ${v46GapLedger.summary.sibling_uncredited_refusal_legs} legs. The frozen aa884cc5 footprint's 11 naked-knife legs / median +44c remain an analytical binding, not a coerced replay count.\n- PANFAL ${named.PANFAL.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}: ${namedV46.PANFAL_mechanism_diagnosis.conclusion}.\n- ARNROM ${named.ARNROM.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; KIRSEK ${named.KIRSEK.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; KRUFER ${named.KRUFER.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; BOSCOP ${named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}.\n- Bar: completed >=396 ${v46Acceptance.completed_pairs.pass ? "PASS" : "FAIL"}; true book >1774c ${v46Acceptance.true_book_net_cents.pass ? "PASS" : "FAIL"}; zero bound regressions ${v46Acceptance.zero_bound_regressions.pass ? "PASS" : "FAIL"}; named ${v46Acceptance.named_checks.pass ? "PASS" : "FAIL"}; overall ${v46Acceptance.pass ? "PASS" : "BLOCKED"}.\n- Market value uses CANON union channels; strict print crossing remains build verification only.\n`
    : isV45
    ? `# V45 guard release at sibling credit — ${v45Acceptance.pass ? "PASS / OPERATIVE" : "BLOCKED / V43 REMAINS OPERATIVE"}\n\nV45 adds exactly one clause to operative V43: the pre-fill T=10 deep-gap guard remains unchanged, but its authority over the other leg terminates immediately when the sibling is credited. The released rest is posted from the last lawful own-book state, bounded by the fixed 99-minus-sibling-entry pair cap and the inherited sanity bound.\n\n${attributionRows.map((row) => `- ${row.machine}: completed ${row.MARKET_UNION_REACH.completed_pairs}, under par ${row.MARKET_UNION_REACH.under_par_pairs}, locked ${row.FULL_BOOK.completed_locked_cents}c, naked ${row.FULL_BOOK.naked_pnl_cents}c, true book ${row.FULL_BOOK.true_book_net_cents}c, frontier ${row.MARKET_UNION_REACH.frontier.LE_93}/${row.MARKET_UNION_REACH.frontier.LE_95}/${row.MARKET_UNION_REACH.frontier.LE_97}/${row.MARKET_UNION_REACH.frontier.LT_100}; strict ${row.STRICT_PRINT_CROSS.completed_pairs}.`).join("\n")}\n\n- Frozen V43 reproduction: ${v45BaselineReproduction.pass ? "PASS" : "FAIL"}.\n- Post-credit releases: ${v45ReleasedRestLedger.summary.released_rests}; filled ${v45ReleasedRestLedger.summary.released_and_filled}; unfilled ${v45ReleasedRestLedger.summary.released_unfilled}.\n- Two columns: completion gains ${v45ReleasedRestLedger.summary.two_columns.pairs_completed.events}; new exposure ${v45ReleasedRestLedger.summary.two_columns.new_exposure.events}.\n- Named LUZTSE ${named.LUZTSE.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; COLCER ${named.COLCER.MARKET_UNION_REACH.combined_entry_cents ?? namedV45.rows.COLCER.disposition}; SMIYUN ${named.SMIYUN.MARKET_UNION_REACH.combined_entry_cents ?? namedV45.rows.SMIYUN.disposition}; VANLEE ${named.VANLEE.MARKET_UNION_REACH.combined_entry_cents ?? namedV45.rows.VANLEE.disposition}; SAINUG ${named.SAINUG.MARKET_UNION_REACH.combined_entry_cents ?? namedV45.rows.SAINUG.disposition}.\n- PENTHA and SHEOLI remain unchanged because neither receives a sibling credit. ARNROM ${named.ARNROM.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; KRUFER ${named.KRUFER.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; KIRSEK ${named.KIRSEK.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}.\n- Bar: completed >=395 ${v45Acceptance.completed_pairs.pass ? "PASS" : "FAIL"}; true book >1748c ${v45Acceptance.true_book_net_cents.pass ? "PASS" : "FAIL"}; naked book >-162c ${v45Acceptance.naked_pnl_cents.pass ? "PASS" : "FAIL"}; named ${v45Acceptance.named_checks.pass ? "PASS" : "FAIL"}; overall ${v45Acceptance.pass ? "PASS" : "BLOCKED"}.\n- Market value uses CANON union channels; strict print crossing remains build verification only.\n`
    : isV43
    ? `# V43 composed machine — ${v43Acceptance.pass ? "PASS" : "BLOCKED / NOT OPERATIVE"}\n\nV43 evaluates all eight combinations of exactly three receipt-priced clauses on frozen V41 from one shared 804-event input load: first-evidence arming only (the adverse walk-lag removal is excluded), the T=10 deep-gap feasibility guard, and the +1c tracking-rest loosening. V41's maker-only, no-clock, pair-cap, sanity-bound, and hard pre-bell laws remain in force.\n\n${attributionRows.map((row) => `- ${row.machine}: completed ${row.MARKET_UNION_REACH.completed_pairs}, under par ${row.MARKET_UNION_REACH.under_par_pairs}, locked ${row.FULL_BOOK.completed_locked_cents}c, naked ${row.FULL_BOOK.naked_pnl_cents}c, true book ${row.FULL_BOOK.true_book_net_cents}c, frontier ${row.MARKET_UNION_REACH.frontier.LE_93}/${row.MARKET_UNION_REACH.frontier.LE_95}/${row.MARKET_UNION_REACH.frontier.LE_97}/${row.MARKET_UNION_REACH.frontier.LT_100}; strict ${row.STRICT_PRINT_CROSS.completed_pairs}.`).join("\n")}\n\n- Receipt single-clause reproduction: ${v43Acceptance.receipt_single_clause_reproduction.pass ? "PASS" : "FAIL"}. The controlling ARM and +1 receipts are static analysis-seat re-scores, not executable decision traces; V43 does not coerce their aggregate values into replay output.\n- Composition bar: completed >=313 ${v43Acceptance.completed_pairs.pass ? "PASS" : "FAIL"}; true book >1001c ${v43Acceptance.true_book_net_cents.pass ? "PASS" : "FAIL"}; named regressions ${v43Acceptance.named_regressions.pass ? "ZERO" : "PRESENT"}; overall ${v43Acceptance.pass ? "PASS" : "BLOCKED"}.\n- Named V43: KIRSEK ${named.KIRSEK.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; ARNROM ${named.ARNROM.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; KRUFER ${named.KRUFER.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; BOSCOP ${named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; PUTJEA exact 64/93/cap35 fingerprint ${namedV43.assertions.PUTJEA_fingerprint_pass ? "PASS" : "FAIL"}; BORDIM DIM not withheld ${namedV43.assertions.BORDIM_DIM_not_withheld ? "PASS" : "FAIL"}.\n- Because the receipt and named laws do not reproduce, V43 does not supersede V41 even though its observed aggregate numeric bars clear. No forced or post-hoc aggregate is emitted as an executable score.\n- Market value uses CANON union channels; strict print crossing remains build verification only.\n`
    : isV42
    ? `# V42 deep-gap feasibility guard\n\nV42 changes one V41 clause: a V41 rest target L is temporarily unlawful only while (99-L) is strictly more than 10 cents below the sibling's contemporaneous best ask. The clause is re-evaluated on every own-book receipt and every sibling-book receipt while withheld. It lifts without a clock the moment the live gap is at most 10 cents. Missing sibling-book evidence never gates V41. All placement, state, persistence-join, pair-cap, fill, and edge laws remain V41.\n\n- Market completed / under par: ${marketScore.completed_pairs} / ${marketScore.under_par_pairs}; locked ${marketScore.locked_cents_per_contract}c. Strict build verification completed / under par: ${strictScore.completed_pairs} / ${strictScore.under_par_pairs}.\n- V41 full book reconstructed: completed ${v41FullBook.aggregate.completed_pairs}, locked ${v41FullBook.aggregate.completed_locked_cents}c, naked ${v41FullBook.aggregate.naked_pnl_cents}c, true book ${v41FullBook.aggregate.true_book_net_cents}c.\n- V42 full book: completed ${v42FullBook.aggregate.completed_pairs}, locked ${v42FullBook.aggregate.completed_locked_cents}c, naked ${v42FullBook.aggregate.naked_pnl_cents}c, true book ${v42FullBook.aggregate.true_book_net_cents}c; delta ${v42FullBook.aggregate.true_book_net_cents - v41FullBook.aggregate.true_book_net_cents}c.\n- Acceptance: completed >=240 ${v42Acceptance.completed_pairs.pass ? "PASS" : "FAIL"}; true book >+782c ${v42Acceptance.true_book_net_cents.pass ? "PASS" : "FAIL"}; overall ${v42Acceptance.pass ? "PASS" : "FAIL"}.\n- Guard affected ${v42GuardLegs.length} legs across ${v42GuardLegs.reduce((sum, row) => sum + row.withhold_episodes, 0)} withholding episodes; ${v42GuardLegs.reduce((sum, row) => sum + row.lifts, 0)} receipt-causal lifts.\n- Guard columns: losses avoided ${deepGapDiff.aggregate.losses_avoided.events}/${deepGapDiff.aggregate.losses_avoided.cents}c; completed pairs forfeited ${deepGapDiff.aggregate.pairs_forfeited.events}/${deepGapDiff.aggregate.pairs_forfeited.cents}c; winning naked legs forfeited ${deepGapDiff.aggregate.winning_naked_forfeited.events}/${deepGapDiff.aggregate.winning_naked_forfeited.cents}c.\n- PUTJEA fingerprint ${namedV42.assertions.PUTJEA_fingerprint_pass ? "PASS" : "FAIL"}; ROCBUE ${namedV42.assertions.ROCBUE_touched ? "WITHHELD" : "NOT_WITHHELD"}; KREZHE ${namedV42.assertions.KREZHE_touched ? "WITHHELD" : "NOT_WITHHELD"}; BORDIM DIM not withheld ${namedV42.assertions.BORDIM_DIM_not_withheld ? "PASS" : "FAIL"}.\n`
    : isV41
    ? `# V41 maker machine\n\nV41 deletes the take path. Every leg carries one post-only rest from its first two-sided book. FALLING and SETTLED use the V36 incumbent walking laws. RISING tracks bid minus one until a bid level has persisted for ${policy.PERSISTENT_LEVEL_SECONDS} seconds, then the same single rest joins the deepest armed persistent level; the seller-hit trigger is absent. The WTA other-expression-FALLING hold, rest-below-ask sanity bound, lazy first-fill pair cap, no-clock law, and hard pre-bell edge remain in force.\n\nMarket scoring uses CANON union channels; strict seller-aggressed print crossing is build verification only. Maker fees are zero.\n\n- V41 market completed / under par: ${marketScore.completed_pairs} / ${marketScore.under_par_pairs}; locked ${marketScore.locked_cents_per_contract}c per-contract aggregate (${marketScore.locked_cents_five_lot}c at five lots); frontier ${marketScore.frontier.LE_93}/${marketScore.frontier.LE_95}/${marketScore.frontier.LE_97}/${marketScore.frontier.LT_100}.\n- V41 strict verification completed / under par: ${strictScore.completed_pairs} / ${strictScore.under_par_pairs}.\n- V36 gross completed / under par: ${v36Score.completed_pairs} / ${v36Score.under_par_pairs}. V36 taker legs charged: ${v36NetScore.aggregate.taker_legs_charged}; gross locked ${v36NetScore.aggregate.gross_locked_cents_five_lot}c; fees on all credited taker legs ${v36NetScore.aggregate.taker_fees_all_credited_legs_five_lot}c; portfolio net ${v36NetScore.aggregate.net_locked_after_all_entry_taker_fees_five_lot}c.\n- Causal-reach reference: ${causalReachReceipt.CAUSAL_REACH.under_par} under-par / ${causalReachReceipt.CAUSAL_REACH.locked}c locked.\n- Market reach grades across 637 games / 5,253c: ${JSON.stringify(marketGrades.aggregate.grades)}.\n- Persistent JOIN legs: ${joinReceipt.join_legs}; market fills after join: ${joinReceipt.market_credited_after_join}; strict fills after join: ${joinReceipt.strict_credited_after_join}.\n- Rest sanity violations: ${sanity.post_decision_rest_at_or_above_ask_violations}. Market taker fills: ${marketLegs.filter((leg) => String(leg.fill_class).includes("TAKER")).length}.\n- ARNROM observed: ${named.ARNROM.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; exact rest/fill sequence is frozen in NAMED_V41_RECEIPT.json. BOSCOP ${named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; NIKVRB ${named.NIKVRB.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; WESPAA ${named.WESPAA.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; KRUFER ${named.KRUFER.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}.\n`
    : isV40
    ? `# V40 placement stack on incumbent direction\n\nV40 inherits V36's state machine and mature-floor take path. The V39 causal classifier is severed and vaulted CLASSIFIER_RESEARCH_OPEN after 437/1,279 reach-moment calls (34.17%). V40 adds only the persistent-level join gated by V36's own RISING state, the WTA other-expression-FALLING deeper hold, and the universal rest-below-ask sanity bound.\n\nMarket grade uses the CANON union-reach channels; strict seller-print crossing plus proven takes is build verification.\n\n- V36 frozen completed / under par: ${v36Score.completed_pairs} / ${v36Score.under_par_pairs}; frontier ${v36Score.frontier.LE_93}/${v36Score.frontier.LE_95}/${v36Score.frontier.LE_97}.\n- V40 market completed / under par: ${marketScore.completed_pairs} / ${marketScore.under_par_pairs}; frontier ${marketScore.frontier.LE_93}/${marketScore.frontier.LE_95}/${marketScore.frontier.LE_97}.\n- Acceptance bar completed>=270 and <=93/<=95>=12/24: ${acceptance.pass ? "PASS" : "FAIL"}.\n- Market reach grades across 637 games / 5,253c: ${JSON.stringify(marketGrades.aggregate.grades)}; shallow ${marketGrades.aggregate.shallow_gap_cents.sum}c; measurable residual ${marketGrades.aggregate.measurable_residual_cents.sum}c.\n- Strict verification completed / under par: ${strictScore.completed_pairs} / ${strictScore.under_par_pairs}.\n- Persistent JOIN legs: ${joinReceipt.join_legs}; zero later certified seller hits at the joined level: ${joinReceipt.zero_post_join_certified_seller_hits}.\n- Rest sanity: ${sanity.post_decision_rest_at_or_above_ask_violations} violations after ${sanity.bound_application_receipts} bound applications.\n- Named market outcomes: ARNROM ${named.ARNROM.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; BOSCOP ${named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; WESPAA ${named.WESPAA.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; NIKVRB ${named.NIKVRB.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}. BOSCOP post-join certified seller hits at COP 47: ${joinReceipt.BOSCOP_COP?.post_join_certified_seller_aggressed_prints_at_level ?? "NOT_JOINED"}.\n`
    : isV39
    ? `# V39 corrected placement stack\n\nV39 runs on frozen V36 with its mature-floor take path intact. The receipt-causal direction classifier combines trailing quote-path and July-6 pressure without reading an ex-post path label; opposing directional votes settle. RISING sides may join a bid only after 300 seconds of continuous residency and a last-traded-at-level book receipt. WTA RISING sides whose other expression reads FALLING hold to the deeper causal pulse/reach level. Every rest is strictly below the current ask.\n\nMarket grade uses the CANON union-reach channels; strict seller-print crossing plus proven takes is build verification.\n\n- V36 frozen completed / under par: ${v36Score.completed_pairs} / ${v36Score.under_par_pairs}.\n- V39 market completed / under par: ${marketScore.completed_pairs} / ${marketScore.under_par_pairs}. This regresses the frozen V36 count and therefore does not supersede V36.\n- Market reach grades across 637 games / 5,253c: ${JSON.stringify(marketGrades.aggregate.grades)}; shallow ${marketGrades.aggregate.shallow_gap_cents.sum}c; measurable residual ${marketGrades.aggregate.measurable_residual_cents.sum}c.\n- Strict verification completed / under par: ${strictScore.completed_pairs} / ${strictScore.under_par_pairs}.\n- Direction telemetry: ${directionTelemetry.aggregate.correct_receipts}/${directionTelemetry.aggregate.eligible_receipts} eligible receipt calls correct and ${directionTelemetry.aggregate.reach_moment_correct_legs}/${directionTelemetry.aggregate.reach_moment_eligible_legs} reach-moment legs correct; ex-post labels consumed by policy: 0.\n- The 2b45d146 115-side cohort has no frozen identity list, so recovery is not fabricated; the independently reproducible c3961e2c cohort has ${mislabelRecovery.independently_reconstructable_c396_cohort.sides} sides and ${mislabelRecovery.independently_reconstructable_c396_cohort.recovered_at_or_better_than_reach} previously uncredited sides recovered at/better than reach.\n- Rest sanity: ${sanity.post_decision_rest_at_or_above_ask_violations} violations after ${sanity.bound_application_receipts} bound applications.\n- Named market outcomes: ARNROM ${named.ARNROM.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; BOSCOP ${named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; WESPAA ${named.WESPAA.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; NIKVRB ${named.NIKVRB.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}. BOSCOP causally joined COP at 47 but had no strictly later union-reach receipt; the 2b45d146 counterfactual's pair-77 credit is not replay-causal and is not imported.\n`
    : `# V38 maker-only machine\n\nV38 removes the take path from the executable policy source. FALLING preserves V36 no-chase rest behavior; SETTLED tracks bid minus one; RISING rests at the lowest ask level revisited at least twice inside the inherited 300-second receipt horizon, only after the standing ask has moved above that floor so the new order remains post-only. Pair cap, lazy first-fill coupling, no-clock law, and the V36 hard pre-bell edge remain intact.\n\nMarket grade uses the CANON union reach ruler; strict seller-print crossing is printed only as build verification.\n\n- Market completed / under par: ${marketScore.completed_pairs} / ${marketScore.under_par_pairs}.\n- Market reach grades across the 637-game answer key: ${JSON.stringify(marketGrades.aggregate.grades)}.\n- Market shallow gap cents: ${marketGrades.aggregate.shallow_gap_cents.sum}; measurable residual cents: ${marketGrades.aggregate.measurable_residual_cents.sum}.\n- Strict verification completed / under par: ${strictScore.completed_pairs} / ${strictScore.under_par_pairs}.\n- Named reach: ARNROM ${named.ARNROM.reach_combined_cents}; BOSCOP ${named.BOSCOP.reach_combined_cents}; NIKVRB ${named.NIKVRB.reach_combined_cents}; GANJAN ${named.GANJAN.reach_combined_cents}.\n`);
  if (isV52) {
    const scoreTraceByteDiff = Object.fromEntries(Object.entries(V52_PRE_REPAIR_SCORE_TRACE_HASHES).map(([name, before]) => {
      const after = fileHash(path.join(output, name));
      return [name, { before_sha256: before, after_sha256: after, byte_identical: before === after }];
    }));
    const scoreTraceBytesUnchanged = Object.values(scoreTraceByteDiff).every((row) => row.byte_identical);
    ensure(scoreTraceBytesUnchanged, `V52 receipt repair changed frozen score/trace bytes: ${Object.entries(scoreTraceByteDiff).filter(([, row]) => !row.byte_identical).map(([name]) => name).join(",")}`);
    const placeRows = machineRuns.get("V52_JUDGMENT_GATE").actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && row.kind === "PLACE_REST");
    const firstPostIdentityCount = new Set(v52Package.firstPosts.map((row) => row.leg_identity)).size;
    ensure(firstPostIdentityCount === v52Package.firstPosts.length, "V52 first-placement receipt contains duplicate legs");
    write("POST_RUN_RECEIPT_REPAIR.json", canonical({
      scope: "AUTHORIZED_RECEIPT_ONLY_REPAIR_NO_BEHAVIORAL_EDIT",
      authority: "OPERATOR_V52_POST_RUN_ORDER_2026-08-12",
      policy: { path: "arb-executor/analysis/window1_v52_judgment_gate.js", pre_repair_sha256: "9a4cba7936cabf17b7edc6fbccfffbafee36b36a3ce8765c731dca9e8ba8cc10", post_repair_sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52_judgment_gate.js")), byte_identical: fileHash(path.join(repo, "arb-executor/analysis/window1_v52_judgment_gate.js")) === "9a4cba7936cabf17b7edc6fbccfffbafee36b36a3ce8765c731dca9e8ba8cc10" },
      stage1_flow_assertions: { pre_repair_top_level_pass: "ABSENT", post_repair_top_level_pass: v52Package.stage1Flow.pass, nested_assertions_changed: false },
      first_post_distribution: { pre_repair_rows_incorrectly_counted_as_first_posts: 7236, post_repair_first_placements_only: v52Package.firstPosts.length, unique_leg_identities: firstPostIdentityCount, all_PLACE_REST_rows: placeRows.length, replacement_PLACE_REST_rows_excluded: placeRows.length - v52Package.firstPosts.length, law: "EARLIEST_PLACE_REST_PER_LEG_IDENTITY_ONLY" },
      named_identity_receipt_correction: v52Package.namedAutopsy.summary.exact_identity_binding,
      score_trace_artifacts: scoreTraceByteDiff,
      all_frozen_score_trace_bytes_unchanged: scoreTraceBytesUnchanged,
      score_artifacts_recomputed_by_clean_build: true,
      score_values_touched: false,
    }));
  }
  const namesBeforeDeterminism = fs.readdirSync(output).sort();
  let determinism;
  if (compare) {
    const mismatches = namesBeforeDeterminism.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
    const extra = fs.readdirSync(compare).filter((name) => ![...namesBeforeDeterminism, "DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name));
    ensure(!mismatches.length && !extra.length, `determinism mismatch: ${[...mismatches, ...extra].join(",")}`);
    determinism = { clean_builds: 2, compared_files: namesBeforeDeterminism.length, byte_identical: true, mismatches: [] };
  } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
  write("DETERMINISM_RECEIPT.json", canonical(determinism));
  writeManifest(output);
  if (compare) {
    fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism));
    writeManifest(compare);
    ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "finalized artifact manifests differ");
  }
  process.stdout.write(canonical({ output, MARKET: marketScore, STRICT_PRINT_CROSS: strictScore, ...(isV52 ? { ATTRIBUTION: attributionRows.map(({ full_book_rows, traded_floor_rows, traded_floor_games, ...row }) => row), ACCEPTANCE: v52Package.acceptance, THREE_STATE: v52Package.stateCensus.states, POSTING: v52Package.postingReceipt, NAMED: v52Package.namedRows } : isV49b ? { ATTRIBUTION: attributionRows.map(({ full_book_rows, traded_floor_rows, traded_floor_games, ...row }) => row), ACCEPTANCE: v49bPackage.acceptance, MECHANISM: v49bPackage.acceptance.mechanism, DEPTH_SHARES: v49bPackage.depthShares } : isV49 ? { ATTRIBUTION: attributionRows.map(({ full_book_rows, traded_floor_rows, traded_floor_games, ...row }) => row), ACCEPTANCE: v49Acceptance, EVIDENCED_STANDING: v49EvidenceLedger.summary, WINDOW_TARGET: v49WindowTarget, named: namedV49 } : isV48 ? { ATTRIBUTION: attributionRows.map(({ full_book_rows, traded_floor_rows, traded_floor_games, ...row }) => row), ACCEPTANCE: v48Acceptance, TRADED_FLOOR_RE_SUM: v48TradedFloors.aggregate, SELECTED_LADDER: v48SelectedRung, named: namedV48 } : isV47 ? { reach_grade: marketGrades.aggregate, ATTRIBUTION: attributionRows.map(({ full_book_rows, ...row }) => row), ACCEPTANCE: v47Acceptance, SEG_C: v47SegCFootprint.summary, named } : isV46 ? { reach_grade: marketGrades.aggregate, ATTRIBUTION: attributionRows.map(({ full_book_rows, ...row }) => row), ACCEPTANCE: v46Acceptance, GAP_CREDIT: v46GapLedger.summary, named } : isV45 ? { reach_grade: marketGrades.aggregate, ATTRIBUTION: attributionRows.map(({ full_book_rows, ...row }) => row), ACCEPTANCE: v45Acceptance, RELEASES: v45ReleasedRestLedger.summary, named } : isV43 ? { reach_grade: marketGrades.aggregate, ATTRIBUTION: attributionRows.map(({ full_book_rows, ...row }) => row), ACCEPTANCE: v43Acceptance, named } : isV42 ? { reach_grade: marketGrades.aggregate, FULL_BOOK: v42FullBook.aggregate, ACCEPTANCE: v42Acceptance, GUARD: { affected_legs: v42GuardLegs.length, differential: deepGapDiff.aggregate }, named } : { reach_grade: marketGrades.aggregate, named }) }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
