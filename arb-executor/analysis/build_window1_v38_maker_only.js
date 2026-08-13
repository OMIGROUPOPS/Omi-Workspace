#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const stream = require("stream/promises");
const zlib = require("zlib");
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
const isV52f = variant === "v52f";
const isV52g = variant === "v52g";
const isV52h = variant === "v52h";
const isV52i = variant === "v52i";
const isV52e = variant === "v52e" || isV52eExam || isV52f || isV52g || isV52h || isV52i;
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
if (!["v38", "v39", "v40", "v41", "v42", "v43", "v45", "v46", "v47", "v48", "v49", "v49b", "v52", "v52b", "v52c", "v52d", "v52e", "v52e804", "v52f", "v52g", "v52h", "v52i"].includes(variant)) throw new Error(`unknown variant ${variant}`);
const policy = require(isV52i ? "./window1_v52i_depth_informed_level_selection.js" : isV52h ? "./window1_v52h_remove_pair_lows_precondition.js" : isV52g ? "./window1_v52g_joint_target_conservation.js" : isV52f ? "./window1_v52f_pair_entry_conservation.js" : isV52e ? "./window1_v52e_palantir_wiring.js" : isV52d ? "./window1_v52d_disagreement_referee.js" : isV52c ? "./window1_v52c_full_post_onset_read.js" : isV52b ? "./window1_v52b_read_level_authority.js" : isV52 ? "./window1_v52_judgment_gate.js" : isV49b ? "./window1_v49b_faithful_stand_at_p.js" : isV49 ? "./window1_v49_evidenced_level_standing.js" : isV48 ? "./window1_v48_trades_as_truth.js" : isV47 ? "./window1_v47_same_tick_arm.js" : isV46 ? "./window1_v46_pair_gated_gap_credit.js" : isV45 ? "./window1_v45_guard_release_sibling_credit.js" : isV43 ? "./window1_v43_composed_machine.js" : isV42 ? "./window1_v42_deep_gap_feasibility_guard.js" : isV41 ? "./window1_v41_maker_machine.js" : isV40 ? "./window1_v40_incumbent_direction_placement_stack.js" : isV39 ? "./window1_v39_corrected_placement_stack.js" : "./window1_v38_maker_only_machine.js");
const frozenV52Policy = isV52b ? require("./window1_v52_judgment_gate.js") : null;
const frozenV52bPolicy = isV52FullRead ? require("./window1_v52b_read_level_authority.js") : null;
const frozenV52cPolicy = (isV52d || isV52e) ? require("./window1_v52c_full_post_onset_read.js") : null;
const frozenV52dPolicy = isV52e ? require("./window1_v52d_disagreement_referee.js") : null;
const frozenV52ePolicy = (isV52f || isV52g || isV52h || isV52i) ? require("./window1_v52e_palantir_wiring.js") : null;
const frozenV52fPolicy = (isV52g || isV52h || isV52i) ? require("./window1_v52f_pair_entry_conservation.js") : null;
const frozenV52gPolicy = (isV52h || isV52i) ? require("./window1_v52g_joint_target_conservation.js") : null;
const frozenV52hPolicy = isV52i ? require("./window1_v52h_remove_pair_lows_precondition.js") : null;
const onsetPolicy = isV52 ? require("./window1_v52_stability_onset.js") : null;
const v43Policy = isV45Family ? require("./window1_v43_composed_machine.js") : null;
const repo = path.resolve(arg("--repo", "."));
const v36Root = path.resolve(arg("--v36-root", "C:/tmp/omi-v36-frozen-bfde"));
const reachRoot = path.resolve(arg("--reach-root", "C:/tmp/omi-reach-57daf3"));
const gapRoot = path.resolve(arg("--gap-root", isPlacementStack ? "C:/tmp/omi-v36-gap-reach-20260807" : repo));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const v52hNamedOnly = isV52h && arg("--named-only", "false") === "true";
const output = path.resolve(arg("--output", path.join(repo, isV52eExam ? ".claude/window1_live_v4_replay/v52e_disposition_804_20260813" : isV52i ? ".claude/window1_live_v4_replay/v52i_depth_informed_level_selection_20260813" : v52hNamedOnly ? ".claude/window1_live_v4_replay/v52h_smiila_named_observation_20260813" : isV52h ? ".claude/window1_live_v4_replay/v52h_remove_pair_lows_precondition_20260813" : isV52g ? ".claude/window1_live_v4_replay/v52g_joint_target_conservation_20260813" : isV52f ? ".claude/window1_live_v4_replay/v52f_pair_entry_conservation_20260813" : isV52e ? ".claude/window1_live_v4_replay/v52e_palantir_wiring_20260812" : isV52d ? ".claude/window1_live_v4_replay/v52d_disagreement_referee_20260812" : isV52c ? ".claude/window1_live_v4_replay/v52c_full_post_onset_read_20260812" : isV52b ? ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812" : isV52 ? ".claude/window1_live_v4_replay/v52_judgment_gate_20260812" : isV49b ? ".claude/window1_live_v4_replay/v49b_faithful_stand_at_p_20260811" : isV49 ? ".claude/window1_live_v4_replay/v49_evidenced_level_standing_20260810" : isV48 ? ".claude/window1_live_v4_replay/v48_trades_as_truth_20260810" : isV47 ? ".claude/window1_live_v4_replay/v47_same_tick_arm_20260810" : isV46 ? ".claude/window1_live_v4_replay/v46_pair_gated_gap_credit_20260810" : isV45 ? ".claude/window1_live_v4_replay/v45_guard_release_sibling_credit_20260809" : isV43 ? ".claude/window1_live_v4_replay/v43_composed_machine_20260809" : isV42 ? ".claude/window1_live_v4_replay/v42_deep_gap_feasibility_guard_20260809" : isV41 ? ".claude/window1_live_v4_replay/v41_maker_machine_20260808" : isV40 ? ".claude/window1_live_v4_replay/v40_incumbent_direction_placement_stack_20260808" : isV39 ? ".claude/window1_live_v4_replay/v39_corrected_placement_stack_20260807" : OUT_REL)));
const compare = arg("--compare", null) ? path.resolve(arg("--compare", null)) : null;
const stage = arg("--stage", "full");
if (isV52 && !["stage1", "full", "cohort30", "disposition804"].includes(stage)) throw new Error(`invalid V52 stage ${stage}`);
if (isV52eExam && stage !== "disposition804") throw new Error(`V52e full exam requires disposition804 stage, got ${stage}`);
const V52_FLOW_EVENTS = new Set(["26JUL16MERDRO", "26JUL12POLKUH", "26JUL19ARSMAR", "26JUL13SANDAN", "26JUL14PUTJEA"]);

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function shaBytes(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
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
async function writeGzipRowsFile(file, rows) {
  async function* encode() { for await (const row of rows) yield `${JSON.stringify(row)}\n`; }
  await stream.pipeline(encode(), zlib.createGzip({ level: 9, mtime: 0 }), fs.createWriteStream(file));
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
    "event_id", "leg_identity", "category", "price_region", "sequence", "timestamp_epoch", "t_minus_scheduled_seconds", "t_minus_actual_bell_seconds", "t_minus_pre_match_boundary_seconds", "receipt",
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
        row.event_id, row.leg_identity, row.category, row.price_region, sequence, row.timestamp_epoch, row.t_minus_scheduled_seconds, row.t_minus_actual_bell_seconds, row.t_minus_pre_match_boundary_seconds, row.receipt,
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
function makeTraceChunkWriter(dir, eventsPerChunk = 8, normalizer = null) {
  let rows = [], eventIds = [], ordinal = 0;
  const chunks = [];
  const flush = async () => {
    if (!rows.length) return;
    ordinal += 1;
    const name = `V52E_FULL_DECISION_TRACE_804_CHUNK_${String(ordinal).padStart(3, "0")}.jsonl.gz`;
    await writeGzipRowsFile(path.join(dir, name), rows);
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
  if (!isV52i) return { store: cleanStore, manifest, manifestBytes, assets };
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
  ensure(path.basename(resolved).includes(isV52 ? "v52" : isV49b ? "v49b" : isV49 ? "v49" : isV48 ? "v48" : isV47 ? "v47" : isV46 ? "v46" : isV45 ? "v45" : isV43 ? "v43" : isV42 ? "v42" : isV41 ? "v41" : isV40 ? "v40" : isV39 ? "v39" : "v38"), `unsafe output ${resolved}`);
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
      sibling.active_order = { ...priorOrder, target_cents: sibling.pair_cap_cents, action_ts: row.ts, action_receipt: row.receipt, source_state: "PAIR_CAP" };
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
    leg.active_order = { target_cents: decision.target_cents, action_ts: row.ts, action_receipt: row.receipt, source_state: combinedState, ...(decision.gap_credit?.authorized ? { gap_credit: { ...decision.gap_credit, event_id: base.event_id, leg_identity: leg.leg_identity, authorization_timestamp_epoch: row.ts, authorization_receipt: row.receipt } } : {}), ...(decision.evidenced_standing ? { evidenced_standing: decision.evidenced_standing } : {}), ...(decision.doctrine_standing ? { doctrine_standing: decision.doctrine_standing } : {}), ...(decision.birth_license ? { birth_license: decision.birth_license } : {}) };
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
  const decision = policy.decide(inputs);
  ensure(decision.guard_authority_terminated === true && decision.guard === null, `V45 guard authority survived sibling credit ${withheldLeg.leg_identity}`);
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
  const inputs = { ...withheldLeg.last_placement_inputs, activeTarget: before, pairCap: withheldLeg.pair_cap_cents, siblingBestAsk: row.ask, ...(withheldLeg.last_placement_inputs.clauses?.joint_target_conservation ? { siblingStandingTarget: triggeringLeg.active_order?.target_cents ?? null, siblingEntryCents: triggeringLeg.entry_cents, siblingCredited: triggeringLeg.credited } : {}) };
  const decision = policy.decide(inputs);
  noteV42Guard(withheldLeg, decision, row, base, actions, triggeringLeg.leg_identity);
  if (decision.guard?.withheld) return;
  const ownBook = withheldLeg.last_placement_inputs.book;
  const detail = { ...clockFields(row.ts, base), receipt: row.receipt, ordinal: row.ordinal, observation: receiptObservation(ownBook), sibling_observation: receiptObservation(row), combined_state: withheldLeg.last_placement_inputs.state, pulse_floor: { floor_cents: withheldLeg.last_placement_inputs.pulseFloor }, pair_cap_cents: withheldLeg.pair_cap_cents, order_before_cents: before, decision, re_evaluated_on_sibling_receipt: true, order_after_cents: null };
  applyRestDecision(withheldLeg, triggeringLeg, row, decision, withheldLeg.last_placement_inputs.state, detail, actions, base, triggeringLeg.leg_identity);
  detail.order_after_cents = withheldLeg.active_order?.target_cents ?? null;
  withheldLeg.last_decision = detail;
}

function simulate(base, tapes, prints, mode, clauses = {}) {
  const ids = Object.keys(base.legs).sort(), actions = [], joinQualifications = [];
  const normalizedClauses = policy.normalizedClauses ? policy.normalizedClauses(clauses) : (isV42 ? { arm_at_first_evidence: false, deep_gap_guard: true, loosen_one_cent: false } : {});
  const event = { event_id: base.event_id, category: base.category, starting_price_split: base.starting_price_split, bell_confidence: base.bell_confidence, edge_source_field: base.edge_source_field, w1_left_epoch: base.left, w1_right_epoch: base.right, mode, clauses: normalizedClauses, legs: {} };
  if (normalizedClauses.joint_target_conservation) event.pair_budget_record = { event_id: base.event_id, born_at: null, current_joint_split: null, revisions: [] };
  for (const id of ids) {
    const meta = base.legs[id], reach = meta.reach;
    event.legs[id] = { ...meta, reach: undefined, event_id: base.event_id, credited: false, entry_cents: null, fill_class: null, fill_source_state: null, action_timestamp_epoch: null, fill_timestamp_epoch: null, pair_cap_cents: null, active_order: null, prior_book: null, directional: [], pulse_visits: [], recent_trade_rows: [], prior_true_trade_low_cents: null, prior_true_trade_low_receipt: null, post_onset_true_trade_low_cents: null, post_onset_true_trade_low_receipt: null, judgment_gate_evaluations: 0, judgment_gate_posts: 0, judgment_gate_blocks: {}, judgment_first_post: null, judgment_first_block: null, judgment_trace_rows: [], exact_bid_first_receipt: new Map(), evidenced_standing_level_cents: null, evidenced_standing_authority: null, evidenced_standing_decisions: 0, evidenced_standing_first: null, evidenced_standing_last: null, pulse_floor_cents: null, pulse_floor_ever: false, current_bid_level: null, current_bid_since: null, current_bid_last_trade_hit: false, current_bid_last_trade_hit_receipt: null, book_last_trade_hits_by_level: new Map(), seller_hits_by_level: new Map(), persistent_join_level: null, persistent_join_receipt: null, persistent_join_evidence_receipt: null, persistent_join_timestamp_epoch: null, post_join_book_last_trade_receipts: 0, post_join_certified_seller_hits_at_level: 0, running_seller_hit_low: null, running_qualified_ask_low: null, running_qualified_ask_low_unabsorbed: false, running_qualified_ask_low_reformed_nonfalling: false, latest_new_low_evidence_ts: null, downward_evidence_rows: [], last_combined_state: "SETTLED", last_disagreement: false, classifier_rows: 0, classifier_state_counts: { FALLING: 0, RISING: 0, SETTLED: 0 }, classifier_opposed_rows: 0, classifier_agreement_rows: 0, decision_count: 0, state_counts: { FALLING: 0, RISING: 0, SETTLED: 0 }, action_counts: {}, disagreement_count: 0, first_decision: null, last_decision: null, first_action: null, terminal_reason: null, last_placement_inputs: null, deep_gap_guard_evaluations: 0, deep_gap_withheld_evaluations: 0, deep_gap_withhold_episodes: 0, deep_gap_lifts: 0, deep_gap_withhold_active: false, deep_gap_first_withhold: null, deep_gap_last_withhold: null, deep_gap_last_lift: null, post_credit_guard_release_attempts: 0, post_credit_guard_releases: 0, post_credit_guard_release_no_book: 0, post_credit_guard_reapplication_prevented_receipts: 0, post_credit_guard_release: null, gap_credit_eligible_receipts: 0, gap_credit_authorized_walks: 0, gap_credit_sibling_uncredited_refusals: 0, gap_credit_no_lawful_reprice: 0, gap_credit_first: null, gap_credit_last: null, gap_credit_fill: null, union_reach_cents: reach.union_reach_cents, union_first_evidence_timestamp_epoch: reach.union_first_evidence_timestamp_epoch, reach_sources: reach.union_sources, reach_inside_v36_edge: reach.union_first_evidence_timestamp_epoch >= base.left && reach.union_first_evidence_timestamp_epoch <= base.right, reach_snapshot: null };
    if (isV52ReadAuthority) Object.assign(event.legs[id], {
      post_onset_observed_min_cents: null,
      post_onset_observed_max_cents: null,
      post_onset_first_observation: null,
      post_onset_last_observation: null,
      ...(isV52FullRead ? { post_onset_read_state: policy.emptyReadState(meta.v52_onset?.selected?.timestamp_epoch ?? null) } : {}),
    });
    if (event.pair_budget_record) event.legs[id].pair_budget_record = event.pair_budget_record;
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
    if ((isV40 || isMaker41) && Number.isFinite(leg.persistent_join_timestamp_epoch) && row.ts > leg.persistent_join_timestamp_epoch) {
      if (row.kind === "PRINT" && row.taker_side === "no" && row.price === leg.persistent_join_level) leg.post_join_certified_seller_hits_at_level += 1;
      if (row.kind === "BOOK" && row.bid === leg.persistent_join_level && row.last_trade === leg.persistent_join_level) leg.post_join_book_last_trade_receipts += 1;
    }
    if (leg.credited) {
      if (normalizedClauses.deep_gap_guard && row.kind === "BOOK") {
        leg.prior_book = row;
        reevaluateV42WithSiblingBook(sibling, leg, row, actions, base);
      }
      continue;
    }
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
    }
    if (row.kind === "PRINT") {
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
    const palantir = normalizedClauses.palantir_priors ? policy.continuousConsultation({ category: base.category, priceRegion: leg.price_region, startingPriceSplit: base.starting_price_split, combinedState: combinedRaw.state, quoteState: quote.state, pressureState: pressure, siblingState: sibling.last_combined_state, row, clauses: normalizedClauses }) : null;
    const referee = normalizedClauses.disagreement_referee ? policy.adjudicateDisagreement({ quote, pressure, row, readState: leg.post_onset_read_state, siblingState: sibling.last_combined_state, palantir }) : null;
    const combinedBase = normalizedClauses.full_post_onset_evidence_horizon ? { ...combinedRaw, authority: policy.fullPostOnsetAuthority(combinedRaw) } : combinedRaw;
    const combined = referee?.resolved ? { ...combinedBase, state: referee.winner.reading, authority: referee.winner.evidence_class === "VALIDATED_N5_PRIOR" ? "V52E_N5_PRIOR_INFORMED_TIE_ADJUDICATION" : "V52D_DISAGREEMENT_REFEREE_STRICTLY_STRONGER_BACKING", disagreement_adjudication: referee } : referee ? { ...combinedBase, disagreement_adjudication: referee } : combinedBase;
    const fullReadEvidence = quote.full_post_onset_evidence?.last_directional_evidence ?? quote.full_post_onset_evidence?.last_evidence ?? null;
    const directionalEvidence = normalizedClauses.full_post_onset_evidence_horizon ? (fullReadEvidence ? { ts: fullReadEvidence.timestamp_epoch, receipt: fullReadEvidence.receipt, kind: fullReadEvidence.kind } : null) : leg.directional.find((evidence) => evidence.receipt === quote.receipt) ?? null;
    leg.last_combined_state = combined.state;
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
    const ownDiary = leg.post_onset_true_trade_low_cents;
    const siblingDiary = sibling.post_onset_true_trade_low_cents;
    const lowsSum = Number.isInteger(ownDiary) && Number.isInteger(siblingDiary) ? ownDiary + siblingDiary : null;
    let diaryTarget = Number.isInteger(ownDiary) ? ownDiary : null;
    if (Number.isInteger(diaryTarget) && Number.isInteger(leg.pair_cap_cents)) diaryTarget = Math.min(diaryTarget, leg.pair_cap_cents);
    if (Number.isInteger(diaryTarget) && Number.isInteger(row.ask)) diaryTarget = Math.min(diaryTarget, row.ask - 1);
    if (!policy.lawfulCent(diaryTarget)) diaryTarget = null;
    const birthLicense = isV52 ? {
      onset: {
        passed: Boolean(onset && row.ts >= onset.timestamp_epoch),
        selected_candidate: onset?.candidate ?? null,
        timestamp_epoch: onset?.timestamp_epoch ?? null,
        t_minus_scheduled_seconds: onset ? (Number.isFinite(base.scheduled) ? base.scheduled - onset.timestamp_epoch : null) : null,
        t_minus_actual_bell_seconds: onset ? (Number.isFinite(base.actual_bell) ? base.actual_bell - onset.timestamp_epoch : null) : null,
        candidates: leg.v52_onset?.candidates ?? null,
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
    const placementInputs = { state: combined.state, book: row, priorAsk: prior?.ask ?? null, askGapCents, activeTarget: before, pairCap: leg.pair_cap_cents, pulseFloor: pulse.floor_cents, persistentJoinLevel: isPlacementStack ? leg.persistent_join_level : null, wtaInverseFalling, causalOwnReachLow, activeEvidenceFloor, floorFirstFlickerLive: activeEvidenceFloor === leg.running_qualified_ask_low && leg.running_qualified_ask_low_unabsorbed, floorMature, recentTradeLow, priorTrueTradeLow: leg.prior_true_trade_low_cents, priorTrueTradeLowReceipt: leg.prior_true_trade_low_receipt, priorExactBidEvidence, evidencedStandingLevel: leg.evidenced_standing_level_cents, evidencedStandingAuthority: leg.evidenced_standing_authority, doctrineStanding, birthLicense, siblingBestAsk: normalizedClauses.deep_gap_guard ? (sibling.prior_book?.ask ?? null) : undefined, siblingEntryCents: sibling.entry_cents, siblingCredited: sibling.credited, siblingStandingTarget: sibling.active_order?.target_cents ?? null, clauses: normalizedClauses };
    leg.last_placement_inputs = placementInputs;
    const atomicReceiptDecision = (isV47 || isTradeTruthVariant) && normalizedClauses.same_tick_arm ? policy.decideReceipt({ ...placementInputs, currentJoinLevel: joinLevelBeforeReceipt, residencySeconds: row.ts - leg.current_bid_since }) : null;
    if (atomicReceiptDecision) ensure(atomicReceiptDecision.effective_join_level_cents === leg.persistent_join_level, `V47 atomic join mismatch ${leg.leg_identity} ${row.receipt}`);
    if (isV49) {
      leg.evidenced_standing_level_cents = atomicReceiptDecision.next_evidenced_standing_level_cents;
      leg.evidenced_standing_authority = atomicReceiptDecision.next_evidenced_standing_authority ?? leg.evidenced_standing_authority;
    }
    const decision = atomicReceiptDecision ? { ...atomicReceiptDecision.decision, ...(isV49 ? { evidenced_standing: { enabled: atomicReceiptDecision.evidenced_level_standing_enabled, raised: atomicReceiptDecision.raised_to_evidenced_level, evidence: atomicReceiptDecision.evidence } } : {}) } : policy.decide(placementInputs);
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
      if (base.v52_flow_trace && (isV52ReadAuthority || wouldPost)) {
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
          ...((isV52f || isV52g || isV52h || isV52i) ? { pair_entry_conservation: decision.birth_license?.pair_entry_conservation ?? null } : {}),
          ...((isV52g || isV52h || isV52i) ? { joint_target_conservation: decision.birth_license?.joint_target_conservation ?? null } : {}),
          ...((isV52h || isV52i) ? { clause_4_market_proof_precondition: decision.birth_license?.clause_4_market_proof_precondition ?? null } : {}),
          ...(isV52i ? { depth_informed_level_selection: decision.birth_license?.level?.depth_informed_level_selection ?? decision.depth_informed_level_selection ?? null } : {}),
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
        if (isV52eExam) {
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
    applyRestDecision(leg, sibling, row, decision, combined.state, detail, actions, base, leg.leg_identity);
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
    if (normalizedClauses.deep_gap_guard) reevaluateV42WithSiblingBook(sibling, leg, row, actions, base);
  }
  for (const leg of Object.values(event.legs)) {
    leg.resting_target_at_edge_cents = leg.credited ? null : (leg.active_order?.target_cents ?? null);
    leg.first_action_timestamp_epoch = leg.first_action?.timestamp_epoch ?? null;
    if (!leg.credited) leg.terminal_reason = leg.decision_count === 0 ? "NO_TWO_SIDED_BOOK_DECISION_INSIDE_V36_EDGE" : leg.active_order ? "REST_UNFILLED_AT_HARD_PREBELL_EDGE" : "NO_LAWFUL_REST_AT_HARD_PREBELL_EDGE";
    leg.final_state = leg.credited ? "CREDITED" : leg.active_order ? "RESTING_UNFILLED" : "NEVER_PLACED_OR_CANCELLED";
    leg.persistent_join_book_last_trade_receipts = leg.persistent_join_level === null ? 0 : (leg.book_last_trade_hits_by_level.get(leg.persistent_join_level) || 0);
    leg.persistent_join_certified_seller_aggressed_prints = leg.persistent_join_level === null ? 0 : (leg.seller_hits_by_level.get(leg.persistent_join_level) || 0);
    delete leg.active_order; delete leg.prior_book; delete leg.directional; delete leg.pulse_visits; delete leg.recent_trade_rows; delete leg.exact_bid_first_receipt; delete leg.first_action; delete leg.seller_hits_by_level; delete leg.book_last_trade_hits_by_level; delete leg.downward_evidence_rows; delete leg.last_placement_inputs; delete leg.deep_gap_withhold_active; delete leg.post_onset_read_state; delete leg.pair_budget_record;
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
    every_post_has_four_license_fields: { violations: postActions.filter((row) => !(row.birth_license?.onset?.passed && row.birth_license?.read?.passed && ((isV52h || isV52i) ? row.birth_license?.diary && row.birth_license?.coherence?.disagreement_clear : row.birth_license?.diary?.passed && row.birth_license?.coherence?.lows_under_par && row.birth_license?.coherence?.disagreement_clear))).map((row) => `${row.leg_identity}@${row.receipt}`) },
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
    const base = { event_id: span.event_id, category: span.category, starting_price_split: span.starting_price_split, bell_confidence: span.precision_class, edge_source_field: span.edge_source_field, left: span.w1_left_epoch, right: span.w1_right_epoch, scheduled, actual_bell: actualBell, v52_flow_trace: isV52eExam || (isV52 && Boolean(v52ShortEvent(span.event_id))), legs: {} };
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
  const v52bCensusBytes = isV52b ? gitShow(REFLEX_CENSUS_COMMIT, ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json") : null;
  let v52bCohort = isV52b ? buildV52bCohort(baseByEvent, v52bCensusBytes) : null;
  const v52cCensusBytes = isV52c ? gitShow(REFLEX_CENSUS_COMMIT, ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json") : null;
  const v52cPriorCohortBytes = isV52c ? gitShow(V52B_COMMIT, ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812/COHORT_SELECTION_RECEIPT.json") : null;
  const v52cCohort = isV52c ? buildV52cCohort(baseByEvent, v52cCensusBytes, v52cPriorCohortBytes) : null;
  const v52dCensusBytes = isV52d ? gitShow(REFLEX_CENSUS_COMMIT, ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json") : null;
  const v52dPriorBCohortBytes = isV52d ? gitShow(V52B_COMMIT, ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812/COHORT_SELECTION_RECEIPT.json") : null;
  const v52dPriorCCohortBytes = isV52d ? gitShow(V52C_COMMIT, ".claude/window1_live_v4_replay/v52c_full_post_onset_read_20260812/COHORT_SELECTION_RECEIPT.json") : null;
  const v52dCohort = isV52d ? buildV52dCohort(baseByEvent, v52dCensusBytes, v52dPriorBCohortBytes, v52dPriorCCohortBytes) : null;
  const v52eCensusBytes = isV52e && !isV52eExam ? gitShow(REFLEX_CENSUS_COMMIT, ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json") : null;
  const v52ePriorReceipts = isV52e && !isV52eExam ? [
    { iteration: "V52B", commit: V52B_COMMIT, path: ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52B_COMMIT, ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812/COHORT_SELECTION_RECEIPT.json") },
    { iteration: "V52C", commit: V52C_COMMIT, path: ".claude/window1_live_v4_replay/v52c_full_post_onset_read_20260812/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52C_COMMIT, ".claude/window1_live_v4_replay/v52c_full_post_onset_read_20260812/COHORT_SELECTION_RECEIPT.json") },
    { iteration: "V52D", commit: V52D_COMMIT, path: ".claude/window1_live_v4_replay/v52d_disagreement_referee_20260812/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52D_COMMIT, ".claude/window1_live_v4_replay/v52d_disagreement_referee_20260812/COHORT_SELECTION_RECEIPT.json") },
    ...((isV52f || isV52g || isV52h || isV52i) ? [{ iteration: "V52E", commit: V52E_COMMIT, path: ".claude/window1_live_v4_replay/v52e_palantir_wiring_20260812/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52E_COMMIT, ".claude/window1_live_v4_replay/v52e_palantir_wiring_20260812/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...((isV52g || isV52h || isV52i) ? [{ iteration: "V52F", commit: V52F_COMMIT, path: ".claude/window1_live_v4_replay/v52f_pair_entry_conservation_20260813/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52F_COMMIT, ".claude/window1_live_v4_replay/v52f_pair_entry_conservation_20260813/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...((isV52h || isV52i) ? [{ iteration: "V52G", commit: V52G_COMMIT, path: ".claude/window1_live_v4_replay/v52g_joint_target_conservation_20260813/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52G_COMMIT, ".claude/window1_live_v4_replay/v52g_joint_target_conservation_20260813/COHORT_SELECTION_RECEIPT.json") }] : []),
    ...(isV52i ? [{ iteration: "V52H", commit: V52H_COMMIT, path: ".claude/window1_live_v4_replay/v52h_remove_pair_lows_precondition_20260813/COHORT_SELECTION_RECEIPT.json", bytes: gitShow(V52H_COMMIT, ".claude/window1_live_v4_replay/v52h_remove_pair_lows_precondition_20260813/COHORT_SELECTION_RECEIPT.json") }] : []),
  ] : null;
  const v52eCohort = isV52e && !isV52eExam ? (isV52i ? buildV52iCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52h ? buildV52hCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52g ? buildV52gCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : isV52f ? buildV52fCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts) : buildV52eCohort(baseByEvent, v52eCensusBytes, v52ePriorReceipts)) : null;
  if (isV52c) v52bCohort = v52cCohort; // compatibility alias for the shared receipt block only
  if (isV52d) v52bCohort = v52dCohort; // compatibility alias for the shared receipt block only
  if (isV52e && !isV52eExam) v52bCohort = v52eCohort; // compatibility alias for the shared receipt block only
  const activeReadCohort = isV52eExam ? null : isV52e ? v52eCohort : isV52d ? v52dCohort : isV52c ? v52cCohort : v52bCohort;
  if (isV52ReadAuthority && !isV52eExam) {
    const selected = new Set(v52hNamedOnly ? [activeReadCohort.named_reused_observation.event_id] : activeReadCohort.combined_30.map((row) => row.event_id));
    for (const base of baseByEvent.values()) base.v52_flow_trace = selected.has(base.event_id);
  }
  const machineSpecs = isV52eExam ? [
    { name: "V52E_DISPOSITION_804", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, judgment_gate: true, scavenger: false, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true } },
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
  const examTraceNormalizer = isV52eExam ? makeLosslessTraceNormalizer() : null;
  const examTraceWriter = isV52eExam ? makeTraceChunkWriter(output, 8, null) : null;
  const examTraceStats = { rows: 0, palantir_consumption_rows: 0, continuous_rows: 0, priors_gate_true_rows: 0, N2_rows: 0, N4_rows: 0, N5_rows: 0, N4_grid_rows: 0, N4_rescue_rows: 0, N5_adjudication_rows: 0, by_block_reason: {}, by_category_x_block_reason: {}, provenance_asset_ids: new Set() };
  if (isV52eExam) { activeExamTraceNormalizer = examTraceNormalizer; activeExamTraceStats = examTraceStats; }
  const examSpanCloseRows = [];
  let index = 0;
  const v52ReadEventIds = isV52ReadAuthority && !isV52eExam ? new Set(activeReadCohort.combined_30.map((row) => row.event_id)) : null;
  if (v52hNamedOnly) { v52ReadEventIds.clear(); v52ReadEventIds.add(activeReadCohort.named_reused_observation.event_id); }
  const replayBases = [...baseByEvent.values()].filter((base) => !isV52 || (isV52eExam ? true : isV52ReadAuthority ? v52ReadEventIds.has(base.event_id) : stage === "full" || v52ShortEvent(base.event_id))).sort((a, b) => a.event_id.localeCompare(b.event_id));
  for (const base of replayBases) {
    index += 1; if (index % 50 === 0) process.stderr.write(`${isV52 ? "V52x2" : isV49b ? "V49bx2" : isV49 ? "V49x2" : isV48 ? "V48x5" : isV47 ? "V47x2" : isV46 ? "V46x2" : isV45 ? "V45x2" : isV43 ? "V43x8" : isV42 ? "V42" : isV41 ? "V41" : isV40 ? "V40" : isV39 ? "V39" : "V38"} replay ${index}/${replayBases.length}\n`);
    const tapes = new Map(), prints = new Map();
    for (const [id, leg] of Object.entries(base.legs)) {
      const loaded = loadTape(leg.ticker); tapeHashes[leg.ticker] = { sha256: loaded.sha256, bytes: loaded.bytes };
      tapes.set(id, loaded.rows); prints.set(id, printLoad.byTicker.get(leg.ticker));
    }
    if (isV52) {
      const onsets = onsetPolicy.computeEventOnsets(base, tapes, prints);
      for (const id of Object.keys(base.legs)) base.legs[id].v52_onset = onsets[id];
    }
    for (const spec of machineSpecs) {
      const marketMode = spec.market_mode || "MARKET_UNION_REACH";
      // Strict-ruler decisions are scored but never exported as a second receipt diary.
      // Suppressing that duplicate trace is serializer/memory hygiene only.
      const strictBase = (isV52eExam || isV52ReadAuthority) ? { ...base, v52_flow_trace: false } : base;
      const run = machineRuns.get(spec.name), market = simulate(base, tapes, prints, marketMode, spec.clauses), strict = simulate(strictBase, tapes, prints, "STRICT_PRINT_CROSS", spec.clauses);
      run.marketEvents.push(market.event); run.strictEvents.push(strict.event);
      for (const row of market.joinQualifications) run.joinQualifications.push({ machine: spec.name, ...row });
      for (const row of strict.joinQualifications) run.joinQualifications.push({ machine: spec.name, ...row });
      for (const row of market.actions) run.actions.push({ machine: spec.name, mode: marketMode, ...row });
      for (const row of strict.actions) run.actions.push({ machine: spec.name, mode: "STRICT_PRINT_CROSS", ...row });
      if (isV52eExam) {
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
  const examTraceChunks = isV52eExam ? await examTraceWriter.finish() : null;
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
  if (isV52ReadAuthority && !isV52eExam) {
    const iterationLabel = isV52i ? "V52I_ITERATION8" : isV52h ? "V52H_ITERATION7" : isV52g ? "V52G_ITERATION6" : isV52f ? "V52F_ITERATION5" : isV52e ? "V52E_ITERATION4" : isV52d ? "V52D_ITERATION3" : isV52c ? "V52C_ITERATION2" : "V52B_ITERATION1";
    const authorizedClause = isV52i ? "CLAUSE_3_N4_DEPTH_INFORMED_LEVEL_SELECTION_ONLY" : isV52h ? "CLAUSE_4_MARKET_PROOF_PRECONDITION_REMOVAL_ONLY" : isV52g ? "CLAUSE_6_ORDER_FREE_JOINT_TARGET_CONSERVATION_ONLY" : isV52f ? "CLAUSE_5_PAIR_ENTRY_CONSERVATION_ONLY" : isV52e ? "N9_CLEAN_PALANTIR_WIRING_ONLY" : isV52d ? "CLAUSE_4_DISAGREEMENT_REFEREE_ONLY" : isV52c ? "CLAUSE_2_EVIDENCE_HORIZON_ONLY" : "CLAUSE_3_LEVEL_AUTHORITY_ONLY";
    const baselineName = isV52i ? "V52H_FROZEN_BASELINE" : isV52h ? "V52G_FROZEN_BASELINE" : isV52g ? "V52F_FROZEN_BASELINE" : isV52f ? "V52E_FROZEN_BASELINE" : isV52e ? "V52D_FROZEN_BASELINE" : isV52d ? "V52C_FROZEN_BASELINE" : isV52c ? "V52B_FROZEN_BASELINE" : "V52_FROZEN_BASELINE";
    const candidateName = isV52i ? "V52I_DEPTH_INFORMED_LEVEL_SELECTION" : isV52h ? "V52H_REMOVE_PAIR_LOWS_PRECONDITION" : isV52g ? "V52G_JOINT_TARGET_CONSERVATION" : isV52f ? "V52F_PAIR_ENTRY_CONSERVATION" : isV52e ? "V52E_PALANTIR_WIRING" : isV52d ? "V52D_DISAGREEMENT_REFEREE" : isV52c ? "V52C_FULL_POST_ONSET_READ" : "V52B_READ_LEVEL_AUTHORITY";
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
    const onsetLawFields = (value) => value ? ({ passed: value.passed, selected_candidate: value.selected_candidate, timestamp_epoch: value.timestamp_epoch, t_minus_scheduled_seconds: value.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: value.t_minus_actual_bell_seconds, candidates: value.candidates }) : null;
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
        ...(isV52i ? {
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
        } : (isV52f || isV52g || isV52h) ? {
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
        if ((isV52g || isV52h || isV52i) && Number.isInteger(firstAuthorizedIndex) && candidateIndex >= firstAuthorizedIndex) downstreamFrozenInputDivergences.push({ ...receipt, classification: isV52i ? "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_3_DEPTH_SELECTION" : isV52h ? "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_4_PRECONDITION_REMOVAL" : "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_6" });
        else frozenClauseDiffs.push(receipt);
      }
      const decisionView = (row, includeDepth) => ({
        gate_verdict: row.gate_verdict,
        blocked_clause: row.blocked_clause,
        final_action: row.final_action,
        final_target_cents: row.final_target_cents,
        reason: row.reason,
        ...(isV52i ? {
          frozen_machine_read_authorized: row.level?.machine_read?.authorized ?? null,
          frozen_machine_read_target_cents: row.level?.machine_read?.target_cents ?? null,
          ...(includeDepth && row.depth_informed_level_selection?.target_changed ? { depth_informed_level_selection: row.depth_informed_level_selection } : {}),
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
    const checkedClauses = isV52i ? ["clause_1_onset", "clause_2_read", "clause_4_coherence", "clause_5_function_identity", "clause_6_function_identity", "clause_4_market_proof_function_identity", "frozen_upstream_function_identity", "scavenger"] : (isV52f || isV52g || isV52h) ? ["clause_1_onset", "clause_2_read", "clause_3_machine_read_input", "clause_4_coherence", "N9_palantir", "frozen_clause_function_identity", "scavenger"] : isV52e ? ["clause_1_onset", "clause_2_read", "frozen_clause_function_identity", "scavenger"] : isV52d ? ["clause_1_onset", "clause_2_read", "clause_3_policy_function_identity", "scavenger"] : isV52c ? ["clause_1_onset", "clause_4_coherence", "scavenger"] : ["clause_1_onset", "clause_2_read", "clause_4_coherence", "scavenger"];
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
    const fourStateCensus = {
      baseline: { states: countBy(baselineFourStateRows, (row) => row.state), rows: baselineFourStateRows.length },
      candidate: { states: countBy(candidateFourStateRows, (row) => row.state), rows: candidateFourStateRows.length },
      conservation: { expected: 30, baseline_sum: baselineFourStateRows.length, candidate_sum: candidateFourStateRows.length, pass: baselineFourStateRows.length === 30 && candidateFourStateRows.length === 30 },
    };
    const pairBudgetRecords = (isV52g || isV52h || isV52i) ? candidateRun.marketEvents.map((event) => event.pair_budget_record) : [];
    const pairBudgetRecordSummary = (isV52g || isV52h || isV52i) ? {
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
    const sandanPin = (isV52g || isV52h || isV52i) ? pinComparisons.find((row) => row.code === "26JUL13SANDAN") : null;
    const smiilaNamedRoot = path.join(repo, ".claude/window1_live_v4_replay/v52h_smiila_named_observation_20260813");
    const smiilaObservation = isV52h ? JSON.parse(fs.readFileSync(path.join(smiilaNamedRoot, "SMIILA_NAMED_OBSERVATION.json"), "utf8")) : null;
    const newOneSidedExposureRows = (isV52h || isV52i) ? candidateFourStateRows.filter((row) => row.state === "PARTIAL_FOR_REASON").flatMap((row) => {
      const before = baselineFourStateRows.find((item) => item.event_id === row.event_id);
      const beforeIds = (before?.credited_legs ?? []).map((leg) => leg.leg_identity).sort().join("|");
      const afterIds = row.credited_legs.map((leg) => leg.leg_identity).sort().join("|");
      if (before?.state === "PARTIAL_FOR_REASON" && beforeIds === afterIds) return [];
      const event = candidateRun.marketEvents.find((item) => item.event_id === row.event_id);
      const credited = Object.values(event.legs).find((leg) => leg.credited), missing = Object.values(event.legs).find((leg) => !leg.credited);
      const edge = baseByEvent.get(row.event_id).right;
      return [{ event_id: row.event_id, category: row.category, price_region: row.price_region, baseline_state: before?.state ?? null, credited_leg: credited.leg_identity, credited_entry_cents: credited.entry_cents, credited_timestamp_epoch: credited.fill_timestamp_epoch, missing_leg: missing.leg_identity, missing_terminal_reason: missing.terminal_reason, exposure_to_window_edge_seconds: Number.isFinite(credited.fill_timestamp_epoch) ? edge - credited.fill_timestamp_epoch : null, second_side_never_kissed: true }];
    }) : [];
    const frozenV52hOneSided = isV52i ? JSON.parse(gitShow(V52H_COMMIT, ".claude/window1_live_v4_replay/v52h_remove_pair_lows_precondition_20260813/NEW_ONE_SIDED_EXPOSURE_RECEIPT.json")) : null;
    const oneSidedExposureSummary = (isV52h || isV52i) ? {
      newly_created_partials: newOneSidedExposureRows.length,
      duration_seconds: distribution(newOneSidedExposureRows.map((row) => row.exposure_to_window_edge_seconds)),
      rows: newOneSidedExposureRows,
      ...(isV52i ? { V52h_baseline: { newly_created_partials: frozenV52hOneSided.newly_created_partials, duration_seconds: frozenV52hOneSided.duration_seconds }, requested_baseline_count_six: frozenV52hOneSided.newly_created_partials === 6 } : {}),
    } : null;
    const offerCensus = isV52i ? JSON.parse(gitShow("22441e05", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/POST_ONSET_OFFER_CENSUS.json")) : null;
    const offerByTicker = isV52i ? new Map(offerCensus.rows.flatMap((game) => Object.values(game.legs ?? {}).map((leg) => [`${game.code}|${leg.ticker.split("-").at(-1)}`, { ...leg, game_code: game.code, offer_class: game.cls, offer_margin_cents: game.margin, pair_floor_cents: game.pair_floor_sel }]))) : new Map();
    const entryFloorRowsFor = (run, variantName) => isV52i ? run.marketEvents.flatMap((event) => Object.values(event.legs).filter((leg) => leg.credited).map((leg) => {
      const offer = offerByTicker.get(`${event.event_id.split("-").at(-1)}|${leg.leg_identity.split("|").at(-1)}`) ?? null;
      return { variant: variantName, event_id: event.event_id, leg_identity: leg.leg_identity, category: event.category, price_region: leg.price_region, entry_cents: leg.entry_cents, post_onset_offer_floor_cents: offer?.floor_sel ?? null, entry_minus_later_floor_cents: Number.isInteger(offer?.floor_sel) ? leg.entry_cents - offer.floor_sel : null, offer_class: offer?.offer_class ?? null, offer_margin_cents: offer?.offer_margin_cents ?? null };
    })) : [];
    const baselineEntryFloorRows = entryFloorRowsFor(baselineRun, "V52H");
    const candidateEntryFloorRows = entryFloorRowsFor(candidateRun, "V52I");
    const gapSummary = (rows) => ({ credited_legs: rows.length, floor_available: rows.filter((row) => Number.isInteger(row.entry_minus_later_floor_cents)).length, signed_entry_minus_later_floor_cents: distribution(rows.map((row) => row.entry_minus_later_floor_cents)), bought_above_later_floor_only: distribution(rows.filter((row) => row.entry_minus_later_floor_cents > 0).map((row) => row.entry_minus_later_floor_cents)) });
    const entryLaterFloorComparison = isV52i ? {
      floor_source: { commit: "22441e05", path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/POST_ONSET_OFFER_CENSUS.json", law: "PER_LEG_POST_ONSET_FLOOR_SEL" },
      baseline: gapSummary(baselineEntryFloorRows), candidate: gapSummary(candidateEntryFloorRows),
      pre_stated_claim: { bought_above_later_floor_depth_shifts_toward_zero: null, adjudication: "OBSERVATION_ONLY; NO_BEHAVIORAL_REPAIR_PERMITTED" },
    } : null;
    if (entryLaterFloorComparison) {
      const before = entryLaterFloorComparison.baseline.bought_above_later_floor_only;
      const after = entryLaterFloorComparison.candidate.bought_above_later_floor_only;
      entryLaterFloorComparison.pre_stated_claim.bought_above_later_floor_depth_shifts_toward_zero = before.n > 0 && after.n > 0 && after.median <= before.median && after.p75 <= before.p75;
    }
    const perGameOutcomeTable = isV52i ? candidateRun.marketEvents.map((event) => {
      const outcome = candidateFourStateRows.find((row) => row.event_id === event.event_id);
      const firstLeg = Object.values(event.legs)[0];
      const offer = offerByTicker.get(`${event.event_id.split("-").at(-1)}|${firstLeg.leg_identity.split("|").at(-1)}`) ?? null;
      return { event_id: event.event_id, category: event.category, price_region: event.starting_price_split, state: outcome.state, combined_entry_cents: event.completed_pair ? event.combined_entry_cents : null, credited_legs: outcome.credited_legs, combined_entry_minus_100_cents: event.completed_pair ? event.combined_entry_cents - 100 : null, locked_delta_vs_100_cents: event.completed_pair ? 100 - event.combined_entry_cents : null, offer_class: offer?.offer_class ?? null, offer_margin_cents: offer?.offer_margin_cents ?? null, offer_census_source_commit: "22441e05" };
    }).sort((a, b) => a.event_id.localeCompare(b.event_id)) : null;
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
      ...(isV52i ? {
        depth_under_validation_receipts: palantirRows.filter((row) => row.palantir?.N4?.depth_candidates_under_validation).length,
        depth_target_changed_receipts: candidateFlow.trace.filter((row) => row.depth_informed_level_selection?.target_changed).length,
        under_validation_candidate_ids: n9Binding.store.boot_assertion.under_validation_loaded_ids,
      } : {}),
      pin_comparisons: pinComparisons,
      pins_unharmed: pinComparisons.every((row) => row.unharmed),
    } : null;
    const v52bAssertions = {
      flow_assertions: candidateFlow.assertions,
      clause_1_CODEX_INTERIM: { violations: candidateFlow.trace.filter((row) => row.onset?.binding_status !== "CODEX-INTERIM").map(traceKey) },
      machine_read_evidence_on_every_post: { violations: candidateMutations.filter((row) => row.birth_license?.level?.machine_read?.authorized !== true || !row.birth_license?.level?.machine_read?.evidence?.evaluation_receipt || !row.birth_license?.level?.machine_read?.evidence?.directional_evidence_receipt).map((row) => `${row.leg_identity}@${row.receipt}`) },
      diary_demoted_not_removed: { violations: candidateMutations.filter((row) => row.birth_license?.diary?.role !== "RECORDED_REFERENCE_INPUT_NOT_SOLE_LEVEL_AUTHORITY").map((row) => `${row.leg_identity}@${row.receipt}`) },
      REFLEX_POST_zero: { observed: candidateMutations.filter((row) => row.birth_license?.read?.passed !== true).length, expected: 0 },
      ...((isV52c || isV52d || isV52e) ? {
        every_post_binds_full_post_onset_read_span: { violations: candidateMutations.filter((row) => row.birth_license?.read?.full_post_onset_evidence?.fixed_horizon_seconds !== null || row.birth_license?.read?.full_post_onset_evidence?.replacement_tuning_constant !== null || !Number.isInteger(row.birth_license?.read?.full_post_onset_evidence?.consulted?.evidence_receipts)).map((row) => `${row.leg_identity}@${row.receipt}`) },
        ...(isV52e ? {
          clauses_1_through_4_and_scavenger_mechanics_frozen: { violations: frozenClauseDiffs.map((row) => row.key) },
          CLEAN_store_boot_assertion: { pass: n9Binding.store.boot_assertion.passed && n9Binding.store.boot_assertion.unvalidated_loaded === 0 && n9Binding.store.boot_assertion.quarantined_loaded === 0 && n9Binding.store.boot_assertion.superseded_loaded === 0 && n9Binding.store.boot_assertion.fallback_loads === 0 && (!isV52i || (n9Binding.store.boot_assertion.canonical_clean_store_unchanged === true && n9Binding.store.boot_assertion.under_validation_loaded === 2)) },
          every_decision_receipt_consumes_N2_N4_N5_continuously: { violations: candidateFlow.trace.filter((row) => !(row.palantir?.continuous_at_decision_time && row.palantir?.N2?.node === "N2" && row.palantir?.N4?.node === "N4" && row.palantir?.N5?.node === "N5")).map(traceKey) },
          every_prior_has_CLEAN_provenance: { violations: palantirRows.filter((row) => [row.palantir.N2, row.palantir.N4, row.palantir.N5].some((node) => !Array.isArray(node.provenance) || node.provenance.some((asset) => !["VALIDATED", "VALID-NARROW"].includes(asset.status) || !(asset.source_sha256 ? /^[0-9a-f]{64}$/.test(asset.source_sha256) : Array.isArray(asset.source_sha256s) && asset.source_sha256s.length > 0 && asset.source_sha256s.every((sha) => /^[0-9a-f]{64}$/.test(sha)))))).map(traceKey) },
          priors_inform_never_gate: { violations: candidateFlow.trace.filter((row) => {
            const before = baselineTrace.get(traceKey(row));
            const candidateIndex = candidateTraceIndex.get(traceKey(row)), firstAuthorizedIndex = firstAuthorizedIndexByEvent.get(row.event_id);
            const frozen_same_input_scope = !(isV52h || isV52i) || !Number.isInteger(firstAuthorizedIndex) || candidateIndex <= firstAuthorizedIndex;
            return row.palantir?.priors_gate !== false || (frozen_same_input_scope && before?.level?.machine_read?.authorized === true && row.level?.machine_read?.authorized !== true);
          }).map(traceKey) },
          ...(isV52i ? {
            frozen_N9_continuous_consumption_preserved: { pass: palantirConsumptionSummary.all_receipts_continuous },
            exact_two_depth_candidates_under_validation: { pass: n9Binding.store.boot_assertion.under_validation_loaded === 2 && canonical(n9Binding.store.boot_assertion.under_validation_loaded_ids) === canonical(["G_GRID_LEVEL_DISCOUNT", "G3_DIP_RECOVERY_GRADIENT"]) },
            every_depth_consultation_records_candidate_provenance: { violations: candidateFlow.trace.filter((row) => row.palantir?.N4?.depth_candidates_under_validation && (row.palantir.N4.depth_candidates_under_validation.provenance?.length !== 2 || row.palantir.N4.depth_candidates_under_validation.provenance.some((asset) => asset.status !== "UNDER-VALIDATION_V52I" || !asset.source_sha256))).map(traceKey) },
            depth_priors_never_create_or_withdraw_live_authority: { violations: candidateFlow.trace.filter((row) => row.depth_informed_level_selection && (row.depth_informed_level_selection.live_authority_retained !== true || row.depth_informed_level_selection.priors_gate !== false || (row.depth_informed_level_selection.applicable && row.depth_informed_level_selection.frozen_machine_read?.authorized !== true))).map(traceKey) },
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
          pins_unharmed: { violations: pinComparisons.filter((row) => !row.unharmed).map((row) => row.event_id) },
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
    const eventFor = (label) => {
      const matches = candidateRun.marketEvents.filter((event) => event.event_id.includes(label));
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
    const merDroFormationPrints6 = Object.values(merDroBase.legs).flatMap((leg) => (printLoad.byTicker.get(leg.ticker) || []).filter((row) => row.price === 6 && row.ts < leg.v52_onset.selected.timestamp_epoch).map((row) => ({ leg_identity: leg.leg_identity, timestamp_epoch: row.ts, receipt: row.receipt, trade_id: row.trade_id, price_cents: row.price, size: row.size, onset_timestamp_epoch: leg.v52_onset.selected.timestamp_epoch })));
    const merDroFillActions = candidateRun.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && row.event_id === merDroEvent.event_id && row.kind === "FILL");
    const merDroFormationReceipts = new Set(merDroFormationPrints6.map((row) => row.receipt));
    const merDroPostOnsetCredits = merDroFillActions.map((row) => {
      const leg = merDroBase.legs[row.leg_identity.split("|").at(-1)];
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
      ...(isV52h ? {
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
      const beforeSha = shaBytes(Buffer.from(canonical(before))), afterSha = shaBytes(Buffer.from(canonical(after)));
      if (beforeSha !== afterSha) streamDiffs.push({ event_id: event.event_id, leg_identity: leg.leg_identity, before_sha256: beforeSha, after_sha256: afterSha, first_difference: decisionDiffs.find((row) => row.leg_identity === leg.leg_identity) ?? null });
      const beforeBehavior = before.map(behaviorFields), afterBehavior = after.map(behaviorFields);
      const beforeBehaviorSha = shaBytes(Buffer.from(canonical(beforeBehavior))), afterBehaviorSha = shaBytes(Buffer.from(canonical(afterBehavior)));
      if (beforeBehaviorSha !== afterBehaviorSha) {
        const count = Math.max(beforeBehavior.length, afterBehavior.length);
        let firstIndex = 0; while (firstIndex < count && canonical(beforeBehavior[firstIndex] ?? null) === canonical(afterBehavior[firstIndex] ?? null)) firstIndex += 1;
        const firstBound = candidateFlow.trace.find((row) => row.event_id === event.event_id && (isV52i ? row.depth_informed_level_selection?.target_changed === true : isV52h ? baselineTrace.get(traceKey(row))?.blocked_clause === "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR" && row.blocked_clause !== "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR" : isV52g ? row.joint_target_conservation?.target_changed === true : row.pair_entry_conservation?.target_changed === true)) ?? null;
        const changedCandidates = [beforeBehavior[firstIndex], afterBehavior[firstIndex]].filter(Boolean);
        const firstChangedTimestamp = changedCandidates.length ? Math.min(...changedCandidates.map((row) => row.timestamp_epoch)) : null;
        behaviorStreamDiffs.push({ event_id: event.event_id, leg_identity: leg.leg_identity, attribution_grain: "PAIR_IS_ENTRY_UNIT", before_sha256: beforeBehaviorSha, after_sha256: afterBehaviorSha, first_difference_index: firstIndex, before: beforeBehavior[firstIndex] ?? null, after: afterBehavior[firstIndex] ?? null, first_authorized_bound_receipt_in_game: firstBound ? { leg_identity: firstBound.leg_identity, timestamp_epoch: firstBound.timestamp_epoch, receipt: firstBound.receipt, authorized_clause: isV52i ? firstBound.depth_informed_level_selection : isV52h ? firstBound.clause_4_market_proof_precondition : isV52g ? firstBound.joint_target_conservation : firstBound.pair_entry_conservation } : null, first_behavior_difference_timestamp_epoch: firstChangedTimestamp, first_behavior_difference_not_before_authorized_clause: Boolean(firstBound && Number.isFinite(firstChangedTimestamp) && firstChangedTimestamp >= firstBound.timestamp_epoch) });
      }
    }
    if (isV52f || isV52g || isV52h || isV52i) ensure(behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause), `${iterationLabel} behavior changed before authorized clause ${behaviorStreamDiffs.find((row) => !row.first_behavior_difference_not_before_authorized_clause)?.leg_identity}`);
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
    if (isV52f || isV52g || isV52h || isV52i) {
      const frozenV52eBytes = gitShow(V52E_COMMIT, "arb-executor/analysis/window1_v52e_palantir_wiring.js");
      ensure(shaBytes(frozenV52eBytes) === fileHash(path.join(repo, "arb-executor/analysis/window1_v52e_palantir_wiring.js")), "frozen V52e policy bytes changed");
      ensure(policy.machineReadLevel === frozenV52ePolicy.machineReadLevel && policy.tradeTruthCredit === frozenV52ePolicy.tradeTruthCredit && (isV52i || policy.continuousConsultation === frozenV52ePolicy.continuousConsultation), "later iteration changed a frozen V52e clause function");
    }
    if (isV52g || isV52h || isV52i) {
      const frozenV52fBytes = gitShow(V52F_COMMIT, "arb-executor/analysis/window1_v52f_pair_entry_conservation.js");
      ensure(shaBytes(frozenV52fBytes) === fileHash(path.join(repo, "arb-executor/analysis/window1_v52f_pair_entry_conservation.js")), "frozen V52f policy bytes changed");
      ensure(policy.fullPostOnsetRead === frozenV52fPolicy.fullPostOnsetRead && policy.tradeTruthCredit === frozenV52fPolicy.tradeTruthCredit, "V52g changed frozen V52f upstream functions");
    }
    if (isV52h || isV52i) {
      const frozenV52gBytes = gitShow(V52G_COMMIT, "arb-executor/analysis/window1_v52g_joint_target_conservation.js");
      ensure(shaBytes(frozenV52gBytes) === fileHash(path.join(repo, "arb-executor/analysis/window1_v52g_joint_target_conservation.js")), "frozen V52g policy bytes changed");
      ensure(policy.jointTargetConservation === frozenV52gPolicy.jointTargetConservation, "V52h changed V52g joint target conservation");
    }
    if (isV52i) {
      const frozenV52hBytes = gitShow(V52H_COMMIT, "arb-executor/analysis/window1_v52h_remove_pair_lows_precondition.js");
      ensure(shaBytes(frozenV52hBytes) === fileHash(path.join(repo, "arb-executor/analysis/window1_v52h_remove_pair_lows_precondition.js")), "frozen V52h policy bytes changed");
      ensure(policy.marketProofReceipt === frozenV52hPolicy.marketProofReceipt && policy.settlementIdentity === frozenV52hPolicy.settlementIdentity && policy.jointTargetConservation === frozenV52hPolicy.jointTargetConservation && policy.tradeTruthCredit === frozenV52hPolicy.tradeTruthCredit, "V52i changed a frozen V52h clause function");
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
    const clauseReceipt = isV52i ? {
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
      ...((isV52f || isV52g || isV52h || isV52i) ? {
        "arb-executor/analysis/window1_v52f_pair_entry_conservation.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52f_pair_entry_conservation.js")), role: "CLAUSE_5_ONLY_POLICY" },
        "arb-executor/analysis/build_window1_v52f_pair_entry_conservation.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52f_pair_entry_conservation.js")), role: "DETERMINISTIC_ENTRYPOINT" },
        "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js")), role: "CLAUSE_5_UNIT_TEST" },
        "arb-executor/tests/test_window1_v52f_pair_entry_conservation_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52f_pair_entry_conservation_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
      } : {}),
      ...((isV52g || isV52h || isV52i) ? {
        "arb-executor/analysis/window1_v52g_joint_target_conservation.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52g_joint_target_conservation.js")), role: "CLAUSE_6_ONLY_POLICY" },
        "arb-executor/analysis/build_window1_v52g_joint_target_conservation.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52g_joint_target_conservation.js")), role: "DETERMINISTIC_ENTRYPOINT" },
        "arb-executor/analysis/build_window1_v52g_provenance_repairs.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52g_provenance_repairs.js")), role: "RECEIPTS_ONLY_PROVENANCE_REPAIR_BUILDER" },
        "arb-executor/tests/test_window1_v52g_joint_target_conservation.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52g_joint_target_conservation.js")), role: "CLAUSE_6_UNIT_TEST" },
        "arb-executor/tests/test_window1_v52g_joint_target_conservation_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52g_joint_target_conservation_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
        "arb-executor/tests/test_window1_v52g_provenance_repairs.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52g_provenance_repairs.js")), role: "RECEIPTS_ONLY_PROVENANCE_REPAIR_TEST" },
      } : {}),
      ...((isV52h || isV52i) ? {
        "arb-executor/analysis/window1_v52h_remove_pair_lows_precondition.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52h_remove_pair_lows_precondition.js")), role: "CLAUSE_4_MARKET_PROOF_PRECONDITION_REMOVAL_ONLY_POLICY" },
        "arb-executor/analysis/build_window1_v52h_remove_pair_lows_precondition.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52h_remove_pair_lows_precondition.js")), role: "DETERMINISTIC_ENTRYPOINT" },
        "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js")), role: "CLAUSE_UNIT_TEST" },
        "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
      } : {}),
      ...(isV52i ? {
        "arb-executor/analysis/window1_v52i_under_validation_store.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52i_under_validation_store.js")), role: "EXACT_TWO_CANDIDATE_VALIDATION_ADAPTER" },
        "arb-executor/analysis/window1_v52i_depth_informed_level_selection.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v52i_depth_informed_level_selection.js")), role: "CLAUSE_3_N4_DEPTH_SELECTION_ONLY_POLICY" },
        "arb-executor/analysis/build_window1_v52i_depth_informed_level_selection.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52i_depth_informed_level_selection.js")), role: "DETERMINISTIC_ENTRYPOINT" },
        "arb-executor/tests/test_window1_v52i_depth_informed_level_selection.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52i_depth_informed_level_selection.js")), role: "CLAUSE_UNIT_TEST" },
        "arb-executor/tests/test_window1_v52i_depth_informed_level_selection_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52i_depth_informed_level_selection_package.js")), role: "PACKAGE_INTEGRITY_TEST" },
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
    const observationScore = { baseline: observationSummary(baselineRun.marketEvents), candidate: observationSummary(candidateRun.marketEvents), adjudication: null, role: "OBSERVATION_ONLY_30_GAME_FLOW_COHORT" };
    const onsetRows = replayBases.flatMap((base) => Object.values(base.legs).map((leg) => ({ event_id: base.event_id, leg_identity: leg.leg_identity, onset: leg.v52_onset })));
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
    const clauseNumber = isV52i ? "3_N4_DEPTH" : isV52h ? "4_MARKET_PROOF" : isV52g ? "6" : isV52f ? "5" : isV52e ? "N9" : isV52d ? "4" : isV52c ? "2" : "3";
    const parentCommit = isV52i ? V52H_COMMIT : isV52h ? V52G_COMMIT : isV52g ? V52F_COMMIT : isV52f ? V52F_PARENT_COMMIT : isV52e ? V52D_COMMIT : isV52d ? V52D_PARENT_COMMIT : isV52c ? V52B_COMMIT : V52_COMMIT;
    const branch = isV52i ? "codex/window1-v52i-depth-informed-level-selection-20260813" : isV52h ? "codex/window1-v52h-remove-pair-lows-precondition-20260813" : isV52g ? "codex/window1-v52g-joint-target-conservation-20260813" : isV52f ? "codex/window1-v52f-pair-entry-conservation-20260813" : isV52e ? "codex/window1-v52e-palantir-wiring-20260812" : isV52d ? "codex/window1-v52d-iteration3-20260812" : isV52c ? "codex/window1-v52c-iteration2-20260812" : "codex/window1-v52b-iteration1-20260812";
    const baselinePrefix = isV52i ? "V52H" : isV52h ? "V52G" : isV52g ? "V52F" : isV52f ? "V52E" : isV52e ? "V52D" : isV52d ? "V52C" : isV52c ? "V52B" : "V52";
    const candidatePrefix = isV52i ? "V52I" : isV52h ? "V52H" : isV52g ? "V52G" : isV52f ? "V52F" : isV52e ? "V52E" : isV52d ? "V52D" : isV52c ? "V52C" : "V52B";
    const core = {
      "REPORT.md": isV52i ? v52iReport : isV52h ? v52hReport : isV52g ? v52gReport : isV52f ? v52fReport : isV52e ? v52eReport : isV52d ? v52dReport : isV52c ? v52cReport : report,
      "CONTROL_BINDING.json": canonical({ parent_commit: parentCommit, branch, scope: "FIVE_PINS_PLUS_FRESH_25_ONLY", score_or_disposition_804_run: false, outcome_adjudication: null }),
      "COHORT_SELECTION_RECEIPT.json": canonical(activeReadCohort),
      [isV52e && !isV52f && !isV52g && !isV52h && !isV52i ? "N9_WIRING_RECEIPT.json" : `CLAUSE_${clauseNumber}_CORRECTION_RECEIPT.json`]: canonical(clauseReceipt),
      "FLOW_ASSERTIONS.json": canonical(v52bAssertions),
      "BEFORE_AFTER_DIFFERENTIAL_RECEIPT.json": canonical({ changed_decision_receipts: decisionDiffs.length, license_or_metadata_changed_leg_streams: streamDiffs.length, behavior_changed_leg_streams: behaviorStreamDiffs.length, every_behavior_change_starts_at_or_after_authorized_clause: (isV52f || isV52g || isV52h || isV52i) ? behaviorStreamDiffs.every((row) => row.first_behavior_difference_not_before_authorized_clause) : null, frozen_clause_differences: frozenClauseDiffs.length, all_behavior_changes_authorized_by: authorizedClause }),
      [`${baselinePrefix}_BASELINE_FLOW_OUTCOMES_OBSERVATION_ONLY.json`]: canonical(baselineFlow.outcomes),
      [`${candidatePrefix}_FLOW_OUTCOMES_OBSERVATION_ONLY.json`]: canonical(candidateFlow.outcomes),
      "NAMED_CHECKS_OBSERVATION_ONLY.json": canonical({ checks: namedChecks, rows: namedRows, adjudication: null }),
      "OUTCOME_OBSERVATIONS_30.json": canonical(observationScore),
      ...((isV52f || isV52g || isV52h || isV52i) ? { "FOUR_STATE_OBSERVATION_30.json": canonical(fourStateCensus) } : {}),
      ...(isV52f ? { "PRE_STATED_CLAIM_RECEIPT.json": canonical(v52fPreStatedClaim) } : {}),
      ...(isV52g ? { "PRIOR_AT_LOSS_REATTESTATION.json": canonical(v52gPriorLossReattestation), "PAIR_BUDGET_RECORD_SUMMARY.json": canonical(pairBudgetRecordSummary), "PIN_REGRESSION_RECEIPT_V52G.json": canonical({ comparisons: pinComparisons, pins_unharmed: pinComparisons.every((row) => row.unharmed), SANDAN_at_or_better: sandanPin?.at_or_better ?? false }) } : {}),
      ...(isV52h ? { "PAIR_BUDGET_RECORD_SUMMARY.json": canonical(pairBudgetRecordSummary), "PIN_REGRESSION_RECEIPT_V52H.json": canonical({ comparisons: pinComparisons, pins_unharmed: pinComparisons.every((row) => row.unharmed) }), "SMIILA_NAMED_OBSERVATION.json": canonical(smiilaObservation), "NEW_ONE_SIDED_EXPOSURE_RECEIPT.json": canonical(oneSidedExposureSummary) } : {}),
      ...(isV52i ? { "PAIR_BUDGET_RECORD_SUMMARY.json": canonical(pairBudgetRecordSummary), "PIN_REGRESSION_RECEIPT_V52I.json": canonical({ comparisons: pinComparisons, pins_unharmed: pinComparisons.every((row) => row.unharmed) }), "NEW_ONE_SIDED_EXPOSURE_RECEIPT.json": canonical(oneSidedExposureSummary), "ENTRY_LATER_FLOOR_COMPARISON.json": canonical(entryLaterFloorComparison), "PER_GAME_OUTCOME_TABLE.json": canonical(perGameOutcomeTable), "DEPTH_UNDER_VALIDATION_BOOT_RECEIPT.json": canonical(n9Binding.store.boot_assertion) } : {}),
      ...(isV52g ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_6", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...(isV52h ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_4_PRECONDITION_REMOVAL", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_authorized_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...(isV52i ? { "AUTHORIZED_DOWNSTREAM_INPUT_DIVERGENCE_RECEIPT.json": canonical({ rows: downstreamFrozenInputDivergences.length, classification: "AUTHORIZED_DOWNSTREAM_STATE_INPUT_DIVERGENCE_AFTER_CLAUSE_3_DEPTH_SELECTION", receipt_keys: downstreamFrozenInputDivergences.map((row) => row.key), frozen_pre_authorized_clause_differences: frozenClauseDiffs.length }) } : {}),
      ...((isV52c || isV52d || isV52e) ? { "PER_LEG_BLOCK_REASON_HISTOGRAM_SUMMARY.json": canonical({ definition: blockReasonHistogram.definition, aggregate: blockReasonHistogram.aggregate }) } : {}),
      ...(isV52d ? { "DISAGREEMENT_REFEREE_SUMMARY.json": canonical(refereeSummary), "PRE_STATED_CLAIM_DISCREPANCY_RECEIPT.json": canonical({ operator_stated_ARSMAR_blocks: 127, frozen_V52c_actual_row_grain_blocks: refereeSummary.frozen_V52c_actual_ARSMAR_block_rows, resolution: "FROZEN_TRACE_CONTROLS; COUNT_NOT_COERCED", behavior_spec_ambiguity: false }) } : {}),
      ...(isV52e ? { "STEP0_REUSE_INVENTORY.json": canonical(step0ReuseInventory), "CLEAN_STORE_BOOT_ASSERTION.json": canonical(n9Binding.store.boot_assertion), "CLEAN_SOURCE_BINDING.json": canonical({ manifest: { commit: n9Binding.store.manifest_commit, sha256: n9Binding.store.manifest_sha256 }, assets: Object.fromEntries(Object.entries(n9Binding.store.loaded).map(([id, asset]) => [id, { manifest_entry: asset.entry, sources: asset.sources }])) }), "PALANTIR_CONSUMPTION_SUMMARY.json": canonical(palantirConsumptionSummary), "N4_ABSTENTION_RECEIPT.json": canonical({ baseline_grid_covered_abstentions: baselineGridAbstentionKeys.size, candidate_same_receipt_abstentions: candidateGridAbstentionKeys.size, delta: candidateGridAbstentionKeys.size - baselineGridAbstentionKeys.size, n4_rescues: n4RescueRows.length, pre_stated_claim_pass: baselineGridAbstentionKeys.size > 0 && candidateGridAbstentionKeys.size < baselineGridAbstentionKeys.size }), "PIN_REGRESSION_RECEIPT.json": canonical({ pins: pinComparisons, unharmed: pinComparisons.every((row) => row.unharmed) }) } : {}),
      "SOURCE_HASH_MANIFEST.json": canonical(sourceManifest),
      ...(isV52e ? { "TEST_RESULTS.json": canonical({ status: "PASS", test_files: isV52h ? 17 : isV52g ? 15 : isV52f ? 12 : 10, assertions: isV52h ? 522 : isV52g ? 456 : isV52f ? 355 : 286, failures: 0, omissions: 0, deselections: 0, suites: [
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
        ...(isV52h ? [
          { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation.js", assertions: 27 },
          { file: "arb-executor/tests/test_window1_v52f_pair_entry_conservation_package.js", assertions: 42 },
          { file: "arb-executor/tests/test_window1_v52g_provenance_repairs.js", assertions: 31 },
          { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation.js", assertions: 31 },
          { file: "arb-executor/tests/test_window1_v52g_joint_target_conservation_package.js", assertions: 39 },
          { file: "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition.js", assertions: 24 },
          { file: "arb-executor/tests/test_window1_v52h_remove_pair_lows_precondition_package.js", assertions: 42 },
        ] : []),
      ] }) } : {}),
      "FORBIDDEN_ACCESS_RECEIPT.json": canonical({ holdout: false, live: false, network_runtime: false, orders: false, positions: false, deployment: false, full_804_run: false, scavenger: false }),
      "CONSTRUCTION_STATUS.json": canonical({ status: v52bAssertions.pass ? "MECHANICAL_PASS_OBSERVATIONS_ONLY_DISPOSITION_804_REMAINS_GATED" : "BLOCKED_MECHANICAL_ASSERTION", [`behavioral_edits_beyond_${isV52i ? "clause_3_N4_depth_informed_level_selection" : isV52h ? "clause_4_market_proof_precondition_removal" : isV52g ? "clause_6_joint_target_conservation" : isV52f ? "clause_5_pair_entry_conservation" : isV52e ? "N9_clean_prior_wiring" : `clause_${clauseNumber}`}`]: false, named_outcomes_are_observations: true }),
    };
    for (const [name, bytes] of Object.entries(core)) write(name, bytes);
    await writeGzipRowsFile(path.join(output, "BEFORE_AFTER_DECISION_DIFFERENTIAL.jsonl.gz"), decisionDiffs);
    await writeGzipRowsFile(path.join(output, "CHANGED_LEG_STREAMS.jsonl.gz"), streamDiffs);
    if (isV52f || isV52g || isV52h || isV52i) await writeGzipRowsFile(path.join(output, isV52i ? "CLAUSE_3_N4_DEPTH_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : isV52h ? "CLAUSE_4_MARKET_PROOF_REMOVAL_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : isV52g ? "CLAUSE_6_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz" : "CLAUSE_5_BEHAVIOR_CHANGED_LEG_STREAMS.jsonl.gz"), behaviorStreamDiffs);
    await writeGzipRowsFile(path.join(output, "STABILITY_ONSET_LEDGER.jsonl.gz"), onsetRows);
    if (isV52f || isV52g || isV52h || isV52i) {
      const writeCohortTraceChunks = async (prefix, rows) => {
        const eventIds = [...new Set(rows.map((row) => row.event_id))].sort();
        const chunks = [];
        for (let start = 0; start < eventIds.length; start += 5) {
          const ids = eventIds.slice(start, start + 5), idSet = new Set(ids);
          const chunkRows = rows.filter((row) => idSet.has(row.event_id));
          const name = `${prefix}_CHUNK_${String(chunks.length + 1).padStart(3, "0")}.jsonl.gz`;
          await writeGzipRowsFile(path.join(output, name), chunkRows);
          chunks.push({ name, event_ids: ids, events: ids.length, rows: chunkRows.length, sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size });
        }
        ensure(chunks.length === 6 && chunks.reduce((sum, row) => sum + row.events, 0) === 30 && chunks.reduce((sum, row) => sum + row.rows, 0) === rows.length, `${prefix} trace chunk conservation failed`);
        return { format: "FULL_RECEIPT_GRAIN_JSONL_GZIP_CHUNKS", chunk_event_count: 5, events: 30, rows: rows.length, chunks, conservation_pass: true };
      };
      const baselineTraceManifest = await writeCohortTraceChunks(`${baselinePrefix}_BASELINE_FULL_DECISION_TRACE_30_GAMES`, baselineCompactTrace);
      const candidateTraceManifest = await writeCohortTraceChunks(`${candidatePrefix}_FULL_DECISION_TRACE_30_GAMES`, candidateCompactTrace);
      write("FULL_DECISION_TRACE_MANIFEST.json", canonical({ baseline: baselineTraceManifest, candidate: candidateTraceManifest, every_receipt_retained: true }));
      if (isV52h) fs.copyFileSync(path.join(smiilaNamedRoot, "SMIILA_NAMED_BEFORE_AFTER_TRACE.jsonl.gz"), path.join(output, "SMIILA_NAMED_BEFORE_AFTER_TRACE.jsonl.gz"));
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
    if (isV52f || isV52g || isV52h || isV52i) {
      await writeGzipRowsFile(path.join(output, `${baselinePrefix}_${candidatePrefix}_FOUR_STATE_EVENT_LEDGER_30.jsonl.gz`), baselineFourStateRows.map((row) => ({ variant: baselinePrefix, ...row })).concat(candidateFourStateRows.map((row) => ({ variant: candidatePrefix, ...row }))));
      if (isV52f) await writeGzipRowsFile(path.join(output, "PAIR_ENTRY_CONSERVATION_LICENSE_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.pair_entry_conservation?.reached || row.final_target_cents !== null).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, final_action: row.final_action, final_target_cents: row.final_target_cents, pair_entry_conservation: row.pair_entry_conservation, level: row.level })));
      if (isV52g || isV52h || isV52i) {
        await writeGzipRowsFile(path.join(output, "JOINT_TARGET_CONSERVATION_LICENSE_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.joint_target_conservation?.reached || row.final_target_cents !== null).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, final_action: row.final_action, final_target_cents: row.final_target_cents, joint_target_conservation: row.joint_target_conservation, level: row.level })));
        await writeGzipRowsFile(path.join(output, "PAIR_BUDGET_RECORDS.jsonl.gz"), pairBudgetRecords);
        await writeGzipRowsFile(path.join(output, "PAIR_JOINT_TARGET_TIME_SERIES.jsonl.gz"), pairBudgetRecords.flatMap((record) => record.revisions.map((revision) => ({ event_id: record.event_id, born_at: record.born_at, ...revision }))));
      }
      if (isV52h) await writeGzipRowsFile(path.join(output, "MARKET_PROOF_PRECONDITION_REMOVAL_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.clause_4_market_proof_precondition).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, gate_verdict: row.gate_verdict, blocked_clause: row.blocked_clause, coherence: row.coherence, clause_4_market_proof_precondition: row.clause_4_market_proof_precondition, final_action: row.final_action, final_target_cents: row.final_target_cents })));
      if (isV52i) {
        await writeGzipRowsFile(path.join(output, "DEPTH_PRIOR_CONSUMPTION_LEDGER.jsonl.gz"), candidateCompactTrace.filter((row) => row.palantir?.N4?.depth_candidates_under_validation).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, depth_candidates_under_validation: row.palantir.N4.depth_candidates_under_validation, depth_informed_level_selection: row.depth_informed_level_selection, final_action: row.final_action, final_target_cents: row.final_target_cents })));
        await writeGzipRowsFile(path.join(output, "ENTRY_LATER_FLOOR_LEDGER.jsonl.gz"), baselineEntryFloorRows.concat(candidateEntryFloorRows));
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
