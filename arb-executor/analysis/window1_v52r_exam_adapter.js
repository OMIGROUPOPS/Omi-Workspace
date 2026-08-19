"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const childProcess = require("child_process");

const FROZEN_V52R_COMMIT = "e79c1feef76d7dfd7ec2737b3663670ddce0d342";
const FROZEN_V52R_PACKAGE = ".claude/window1_live_v4_replay/v52r_assembled_policy_20260818";
const GROUND_TRUTH_COMMIT = "c0056976c446afcb4d9603796a2e06c068ee94d6";
const GROUND_TRUTH_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.json";
const V52E_WRAPPER = "arb-executor/analysis/build_window1_v52e_disposition_804.js";
const SHARED_BUILDER = "arb-executor/analysis/build_window1_v38_maker_only.js";
const V52E_POLICY = "arb-executor/analysis/window1_v52e_palantir_wiring.js";
const V52E_TEST = "arb-executor/tests/test_window1_v52e_palantir_wiring.js";
const V52R_POLICY_ROOTS = [
  "arb-executor/analysis/window1_v52r_assembled_policy.js",
  "arb-executor/analysis/window1_v52l_causal_stability_onset.js",
  "arb-executor/analysis/window1_n9_clean_store.js",
];

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return sha256(fs.readFileSync(file)); }
function gitBytes(repo, commit, relativePath) {
  return childProcess.execFileSync("git", ["show", `${commit}:${relativePath}`], { cwd: repo, encoding: null, maxBuffer: 512 * 1024 * 1024 });
}
function percentile(values, q) {
  const rows = values.filter(Number.isFinite).sort((a, b) => a - b);
  return rows.length ? rows[Math.max(0, Math.ceil(q * rows.length) - 1)] : null;
}
function distribution(values) {
  const rows = values.filter(Number.isFinite);
  return {
    n: rows.length,
    null_n: values.length - rows.length,
    sum: rows.reduce((sum, value) => sum + value, 0),
    min: rows.length ? Math.min(...rows) : null,
    p25: percentile(rows, 0.25),
    median: percentile(rows, 0.5),
    p75: percentile(rows, 0.75),
    p90: percentile(rows, 0.9),
    max: rows.length ? Math.max(...rows) : null,
  };
}
function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) { const key = String(keyFn(row)); counts[key] = (counts[key] || 0) + 1; }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

function localRequireClosure(repo, roots) {
  const pending = [...roots], seen = new Set();
  while (pending.length) {
    const relativePath = pending.pop().replaceAll("\\", "/");
    if (seen.has(relativePath)) continue;
    seen.add(relativePath);
    const source = fs.readFileSync(path.join(repo, relativePath), "utf8");
    const dir = path.posix.dirname(relativePath);
    for (const match of source.matchAll(/require\(["'](\.\/.+?\.js)["']\)/g)) {
      const dependency = path.posix.normalize(path.posix.join(dir, match[1]));
      if (dependency.startsWith("arb-executor/analysis/")) pending.push(dependency);
    }
  }
  return [...seen].sort();
}

function attestFrozenPolicy(repo) {
  const files = {};
  for (const relativePath of localRequireClosure(repo, V52R_POLICY_ROOTS)) {
    const current = fs.readFileSync(path.join(repo, relativePath));
    const frozen = gitBytes(repo, FROZEN_V52R_COMMIT, relativePath);
    files[relativePath] = {
      frozen_sha256: sha256(frozen),
      current_sha256: sha256(current),
      frozen_bytes: frozen.length,
      current_bytes: current.length,
      byte_identical: Buffer.compare(frozen, current) === 0,
    };
  }
  const allByteIdentical = Object.values(files).every((row) => row.byte_identical);
  ensure(allByteIdentical, "V52r transitive policy byte identity failed");
  return { frozen_commit: FROZEN_V52R_COMMIT, roots: V52R_POLICY_ROOTS, transitive_files: files, file_count: Object.keys(files).length, all_byte_identical: allByteIdentical };
}

function v52eProtectedBlock(bytes) {
  const source = bytes.toString("utf8").replaceAll("\r\n", "\n");
  const startNeedle = "\n  if (isV52eExam) {\n    const run = machineRuns.get(\"V52E_DISPOSITION_804\");";
  const start = source.indexOf(startNeedle);
  const v52sEndNeedle = "\n  if (isV52sExam) {";
  const v52rEndNeedle = "\n  if (isV52rExam) {";
  const legacyEndNeedle = "\n  if (isV52 && stage === \"stage1\") {";
  const v52sEnd = source.indexOf(v52sEndNeedle, start + 1), v52rEnd = source.indexOf(v52rEndNeedle, start + 1);
  const end = v52sEnd >= 0 ? v52sEnd : v52rEnd >= 0 ? v52rEnd : source.indexOf(legacyEndNeedle, start + 1);
  ensure(start >= 0 && end > start, "V52e protected exam block markers missing");
  return Buffer.from(source.slice(start, end), "utf8");
}

function attestV52eLaneUnchanged(repo) {
  const files = {};
  for (const relativePath of [V52E_WRAPPER, V52E_POLICY, V52E_TEST]) {
    const current = fs.readFileSync(path.join(repo, relativePath)), frozen = gitBytes(repo, FROZEN_V52R_COMMIT, relativePath);
    files[relativePath] = { frozen_sha256: sha256(frozen), current_sha256: sha256(current), byte_identical: Buffer.compare(frozen, current) === 0 };
  }
  const frozenBuilder = gitBytes(repo, FROZEN_V52R_COMMIT, SHARED_BUILDER);
  const currentBuilder = fs.readFileSync(path.join(repo, SHARED_BUILDER));
  const frozenBlock = v52eProtectedBlock(frozenBuilder), currentBlock = v52eProtectedBlock(currentBuilder);
  const protectedBlock = { frozen_sha256: sha256(frozenBlock), current_sha256: sha256(currentBlock), frozen_bytes: frozenBlock.length, current_bytes: currentBlock.length, byte_identical: Buffer.compare(frozenBlock, currentBlock) === 0 };
  const pass = Object.values(files).every((row) => row.byte_identical) && protectedBlock.byte_identical;
  ensure(pass, "existing v52e804 lane changed");
  return { frozen_commit: FROZEN_V52R_COMMIT, files, protected_exam_block: protectedBlock, shared_builder_whole_file_expected_to_change_only_for_v52r804_registration: true, pass };
}

function compareCohortBuild(frozenDir, candidateDir) {
  const ignored = new Set(["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json", "SOURCE_HASH_MANIFEST.json", "STEP0_REUSE_INVENTORY.json"]);
  const frozenNames = fs.readdirSync(frozenDir).filter((name) => !ignored.has(name)).sort();
  const candidateNames = fs.readdirSync(candidateDir).filter((name) => !ignored.has(name)).sort();
  const missing = frozenNames.filter((name) => !candidateNames.includes(name));
  const extra = candidateNames.filter((name) => !frozenNames.includes(name));
  const mismatches = frozenNames.filter((name) => candidateNames.includes(name) && fileHash(path.join(frozenDir, name)) !== fileHash(path.join(candidateDir, name))).map((name) => ({ name, frozen_sha256: fileHash(path.join(frozenDir, name)), candidate_sha256: fileHash(path.join(candidateDir, name)) }));
  const sourceOld = JSON.parse(fs.readFileSync(path.join(frozenDir, "SOURCE_HASH_MANIFEST.json"), "utf8"));
  const sourceNew = JSON.parse(fs.readFileSync(path.join(candidateDir, "SOURCE_HASH_MANIFEST.json"), "utf8"));
  const builderPath = "arb-executor/analysis/build_window1_v38_maker_only.js";
  const builderHashChange = { frozen_sha256: sourceOld.files[builderPath].sha256, adapter_registered_sha256: sourceNew.files[builderPath].sha256 };
  sourceNew.files[builderPath].sha256 = sourceOld.files[builderPath].sha256;
  ensure(canonical(sourceOld) === canonical(sourceNew), "cohort SOURCE_HASH_MANIFEST changed beyond the registered builder hash");
  const reuseOld = JSON.parse(fs.readFileSync(path.join(frozenDir, "STEP0_REUSE_INVENTORY.json"), "utf8"));
  const reuseNew = JSON.parse(fs.readFileSync(path.join(candidateDir, "STEP0_REUSE_INVENTORY.json"), "utf8"));
  const loaderOld = reuseOld.components.find((row) => row.symbol === "build_window1_v38_maker_only.js::gitShow");
  const loaderNew = reuseNew.components.find((row) => row.symbol === "build_window1_v38_maker_only.js::gitShow");
  const loaderLineChange = { frozen_line: loaderOld.source.line, adapter_registered_line: loaderNew.source.line };
  loaderNew.source.line = loaderOld.source.line;
  ensure(canonical(reuseOld) === canonical(reuseNew), "cohort STEP0_REUSE_INVENTORY changed beyond the registered builder line shift");
  const pass = missing.length === 0 && extra.length === 0 && mismatches.length === 0;
  ensure(pass, `V52r 30-game adapter sanity mismatch: ${canonical({ missing, extra, mismatches }).trim()}`);
  return { role: "PRE_EXAM_BYTE_IDENTITY_FENCE", frozen_commit: FROZEN_V52R_COMMIT, frozen_package: FROZEN_V52R_PACKAGE, compared_files: frozenNames.length, intentionally_excluded_receipt_files: [...ignored].sort(), receipt_only_expected_differences: { shared_builder_hash_due_to_new_variant_registration: builderHashChange, gitShow_source_line_due_to_new_import_and_flags: loaderLineChange }, missing, extra, mismatches, decision_traces_byte_identical: true, outcomes_and_score_artifacts_byte_identical: true, pass };
}

function makeExamTraceNormalizer(roleStats) {
  const sequenceByLeg = new Map();
  const fields = [
    "event_id", "leg_identity", "category", "price_region", "sequence", "timestamp_epoch", "t_minus_scheduled_seconds", "t_minus_actual_bell_seconds", "t_minus_pre_match_boundary_seconds", "receipt",
    "bid", "ask", "last_traded", "spread", "ask_dwell_seconds", "top_ask_size", "bid_depth_5", "ask_depth_5",
    "onset_passed", "onset_candidate", "onset_timestamp_epoch", "read_passed", "read_state", "quote_path_state", "pressure_state", "read_evidence_class", "read_span_seconds", "read_evidence_receipts", "read_book_receipts", "read_print_receipts", "read_comparable_book_transitions", "read_comparable_print_transitions", "read_rising_score", "read_falling_score", "last_directional_evidence_kind", "last_directional_evidence_receipt", "last_directional_evidence_magnitude_cents",
    "own_post_onset_low_cents", "own_low_receipt", "sibling_post_onset_low_cents", "sibling_low_receipt", "lows_sum_cents", "lows_under_par", "disagreement_firing", "disagreement_clear", "adjudication_status", "adjudication_winner", "adjudication_loser",
    "level_passed", "level_target_cents", "level_authority", "machine_read_target_cents", "machine_read_authority", "palantir_rescue", "palantir_manifest_sha256", "N2_cell_n", "N2_cell_share", "N4_grid_covered", "N4_grid_discount_cents", "N4_zone_category_share", "N4_zone_price_share", "N5_mirror_rate", "N5_vindication_rate", "palantir_continuous", "priors_gate",
    "role_candidate", "role_bound", "role_drift_cents", "trd5_post_onset_trade_count", "trd5_threshold", "trd5_gate_passed", "trd5_transition", "trd5_first_bind_timestamp_epoch", "trd5_first_bind_receipt", "corrected_anchor_cents", "role_maximum_consumed_timestamp_epoch", "assembled_policy_applicable", "assembled_session_low_cents", "assembled_selected_target_cents", "assembled_target_changed", "assembled_level_policy_consumed",
    "gate_verdict", "blocked_clause", "incumbent_action", "incumbent_reason", "order_before_cents", "final_action", "final_target_cents", "reason",
  ];
  return {
    normalize(row) {
      const sequence = (sequenceByLeg.get(row.leg_identity) ?? 0) + 1; sequenceByLeg.set(row.leg_identity, sequence);
      const evidence = row.read?.full_post_onset_evidence, adjudication = row.coherence?.disagreement_adjudication, palantir = row.palantir, grid = palantir?.N4?.grid;
      const macro = row.macro_recognition, trd5 = macro?.trd5, assembled = row.assembled_policy;
      if (macro) {
        roleStats.role_receipt_rows += 1;
        if (!Object.hasOwn(row, "t_minus_scheduled_seconds") || !Object.hasOwn(row, "t_minus_actual_bell_seconds")) roleStats.missing_both_clock_fields.push(`${row.leg_identity}|${row.receipt}`);
        roleStats.terminal_by_leg.set(row.leg_identity, { leg_identity: row.leg_identity, role: macro.bound_role ?? "ABSTAIN", candidate_role: macro.candidate_role ?? null, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds, drift_cents: macro.drift_cents ?? null, trd5_trade_count: trd5?.post_onset_trade_count ?? null, trd5_gate_passed: trd5?.gate_passed ?? false, assembled_target_cents: assembled?.selected_target_cents ?? null });
      }
      const values = [
        row.event_id, row.leg_identity, row.category, row.price_region, sequence, row.timestamp_epoch, row.t_minus_scheduled_seconds, row.t_minus_actual_bell_seconds, row.t_minus_pre_match_boundary_seconds, row.receipt,
        row.observation?.bid, row.observation?.ask, row.observation?.last_traded, row.observation?.spread, row.observation?.ask_dwell_seconds, row.observation?.top_ask_size, row.observation?.bid_depth_5, row.observation?.ask_depth_5,
        row.onset?.passed, row.onset?.selected_candidate, row.onset?.timestamp_epoch, row.read?.passed, row.read?.state, row.read?.quote_path_state, row.read?.pressure_state, row.read?.evidence, evidence?.span_seconds, evidence?.consulted?.evidence_receipts, evidence?.consulted?.book_receipts, evidence?.consulted?.print_receipts, evidence?.consulted?.comparable_book_transitions, evidence?.consulted?.comparable_print_transitions, evidence?.weighted_scores_cents?.rising, evidence?.weighted_scores_cents?.falling, evidence?.last_directional_evidence?.kind, evidence?.last_directional_evidence?.receipt, evidence?.last_directional_evidence?.magnitude_cents,
        row.diary?.own_post_onset_true_trade_low_cents, row.diary?.own_receipt, row.diary?.sibling_post_onset_true_trade_low_cents, row.diary?.sibling_receipt, row.coherence?.post_onset_running_lows_sum_cents, row.coherence?.lows_under_par, row.coherence?.disagreement_firing, row.coherence?.disagreement_clear, adjudication?.status, adjudication?.winner?.state ?? adjudication?.winner, adjudication?.loser?.state ?? adjudication?.loser,
        row.level?.passed, row.level?.target_cents, row.level?.authority, row.level?.machine_read?.target_cents, row.level?.machine_read?.authority, row.level?.machine_read?.palantir_rescue === true, palantir?.manifest?.sha256, palantir?.N2?.cell_base_rate?.n, palantir?.N2?.cell_base_rate?.share, Boolean(grid), grid?.discount_cents ?? grid?.p75_dip ?? null, palantir?.N4?.zone?.category?.share, palantir?.N4?.zone?.starting_price_split?.share, palantir?.N5?.mirror_coherence_base_rate?.rate, palantir?.N5?.one_eyed_vindication_base_rate?.rate, palantir?.continuous_at_decision_time, palantir?.priors_gate,
        macro?.candidate_role, macro?.bound_role, macro?.drift_cents, trd5?.post_onset_trade_count, trd5?.threshold, trd5?.gate_passed, trd5?.transition, trd5?.first_bind?.timestamp_epoch, trd5?.first_bind?.receipt, macro?.post_formation_open_cents, macro?.maximum_consumed_timestamp_epoch, assembled?.applicable, assembled?.session_low_cents, assembled?.selected_target_cents, assembled?.target_changed, assembled?.level_policy_consumed,
        row.gate_verdict, row.blocked_clause, row.incumbent_action, row.incumbent_reason, row.order_before_cents, row.final_action, row.final_target_cents, row.reason,
      ];
      return values.map((value) => value === undefined ? null : value);
    },
    entries() { return [{ format: "V52R_RECEIPT_GRAIN_DECISION_DIARY_V1", fields, reconstruction: "Each array position maps to fields[index]; every policy decision receipt is retained, including TRD5/LOW-1 role evidence and both clocks." }]; },
    rows() { return [...sequenceByLeg.values()].reduce((sum, value) => sum + value, 0); },
    legs() { return sequenceByLeg.size; },
  };
}

function dominantBlock(leg) {
  return Object.entries(leg.judgment_gate_blocks ?? {}).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0]?.[0] ?? "NO_GATE_BLOCK_RECORDED";
}

function gradeRun(events, groundTruth, terminalRoles = new Map()) {
  const rows = events.map((event) => {
    const window = groundTruth.byEvent.get(event.event_id);
    ensure(window, `ground-truth row absent ${event.event_id}`);
    const legs = Object.entries(event.legs).sort(([a], [b]) => a.localeCompare(b)).map(([legId, leg]) => {
      const floor = window.legs[legId]?.floor_cents ?? null;
      const valid = window.scoring_eligible && Number.isFinite(window.span_start_epoch) && Number.isFinite(window.span_end_epoch) && leg.credited && Number.isFinite(leg.fill_timestamp_epoch) && leg.fill_timestamp_epoch >= window.span_start_epoch && leg.fill_timestamp_epoch <= window.span_end_epoch;
      return { leg_id: legId, leg_identity: leg.leg_identity, valid_credited: valid, raw_credited: leg.credited, entry_cents: valid ? leg.entry_cents : null, raw_entry_cents: leg.entry_cents, fill_timestamp_epoch: valid ? leg.fill_timestamp_epoch : null, raw_fill_timestamp_epoch: leg.fill_timestamp_epoch, ground_truth_floor_cents: floor, entry_minus_floor_cents: valid && Number.isInteger(floor) ? leg.entry_cents - floor : null, terminal_reason: valid ? leg.terminal_reason : leg.credited ? "HISTORICAL_FILL_OUTSIDE_GROUND_TRUTH_WINDOW" : leg.terminal_reason, dominant_block_reason: dominantBlock(leg), terminal_role: terminalRoles.get(leg.leg_identity) ?? null };
    });
    if (!window.scoring_eligible) return { event_id: event.event_id, category: event.category, price_region: event.starting_price_split, bell_confidence: window.bell_source, state: "UNKNOWN_BELL_NON_GRADEABLE", combined_entry_cents: null, locked_delta_cents: null, legs, window };
    const credited = legs.filter((leg) => leg.valid_credited), combined = credited.length === 2 ? credited.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
    const state = credited.length === 2 ? (combined < 100 ? "COMPLETE_AT_DELTA" : "COMPLETE_AT_LOSS") : credited.length === 1 ? "PARTIAL_FOR_REASON" : "NEITHER_FOR_REASON";
    return { event_id: event.event_id, category: event.category, price_region: event.starting_price_split, bell_confidence: window.bell_source, state, combined_entry_cents: combined, locked_delta_cents: state === "COMPLETE_AT_DELTA" ? 100 - combined : null, legs, window };
  });
  ensure(rows.length === 804, `graded row conservation ${rows.length}`);
  return rows;
}

function scoreRows(rows) {
  const eligible = rows.filter((row) => row.state !== "UNKNOWN_BELL_NON_GRADEABLE"), completed = eligible.filter((row) => ["COMPLETE_AT_DELTA", "COMPLETE_AT_LOSS"].includes(row.state)), delta = eligible.filter((row) => row.state === "COMPLETE_AT_DELTA");
  const frontier = { LE_93: delta.filter((row) => row.combined_entry_cents <= 93).length, LE_95: delta.filter((row) => row.combined_entry_cents <= 95).length, LE_97: delta.filter((row) => row.combined_entry_cents <= 97).length, LT_100: delta.length, ANY_PRICE: completed.length };
  return { population_D: rows.length, scoring_D: eligible.length, unknown_bell: rows.length - eligible.length, states: countBy(rows, (row) => row.state), valid_credited_legs: eligible.flatMap((row) => row.legs).filter((leg) => leg.valid_credited).length, completed_pairs: completed.length, under_par_pairs: delta.length, completed_at_loss: completed.length - delta.length, locked_cents: delta.reduce((sum, row) => sum + row.locked_delta_cents, 0), frontier, valid_delta_distribution: distribution(delta.map((row) => row.locked_delta_cents)) };
}

function partition(rows, dimensions) {
  const groups = new Map();
  for (const row of rows) { const key = dimensions.map((name) => row[name]).join("|"); if (!groups.has(key)) groups.set(key, []); groups.get(key).push(row); }
  return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, group]) => ({ cell, ...scoreRows(group), population_D: group.length }));
}

function buildOfferDenominator(groundTruth, marketRows, strictRows) {
  const rawByEvent = new Map(groundTruth.table.rows.map((row) => [row.event_id, row]));
  const marketByEvent = new Map(marketRows.map((row) => [row.event_id, row])), strictByEvent = new Map(strictRows.map((row) => [row.event_id, row]));
  const rows = [...groundTruth.byEvent.values()].map((window) => {
    const raw = rawByEvent.get(window.event_id), floors = [raw[`legA_floor_c`], raw[`legB_floor_c`]], sum = floors.every(Number.isInteger) ? floors[0] + floors[1] : null;
    const margin = Number.isInteger(sum) ? 100 - sum : null;
    const offerClass = !window.scoring_eligible ? "UNKNOWN_BELL" : !Number.isInteger(sum) ? "FORMATION_OR_FLOOR_UNAVAILABLE" : margin > 0 ? "OFFERED_UNDER_PAR" : "NOT_OFFERED_UNDER_PAR";
    const market = marketByEvent.get(window.event_id), strict = strictByEvent.get(window.event_id);
    return { event_id: window.event_id, category: window.category, price_region: market.price_region, bell_confidence: window.bell_source, offer_class: offerClass, floor_sum_cents: sum, offer_margin_cents: margin, market_state: market.state, market_captured: market.state === "COMPLETE_AT_DELTA", market_locked_cents: market.locked_delta_cents, strict_state: strict.state, strict_captured: strict.state === "COMPLETE_AT_DELTA", strict_locked_cents: strict.locked_delta_cents };
  });
  const offered = rows.filter((row) => row.offer_class === "OFFERED_UNDER_PAR");
  ensure(offered.length === 680, `ground-truth offered games changed ${offered.length}`);
  ensure(offered.reduce((sum, row) => sum + row.offer_margin_cents, 0) === 3123, "ground-truth offered cents changed");
  const baselineRows = groundTruth.table.rows.filter((row) => row.pair_state === "COMPLETE_AT_DELTA" && Number.isInteger(row.locked_delta_valid_fills_c));
  ensure(baselineRows.length === 214 && baselineRows.reduce((sum, row) => sum + row.locked_delta_valid_fills_c, 0) === 350, "standing valid-fill baseline changed");
  const summarize = (subset, prefix) => ({ denominator_games: subset.length, denominator_cents: subset.reduce((sum, row) => sum + row.offer_margin_cents, 0), captured_games: subset.filter((row) => row[`${prefix}_captured`]).length, captured_locked_cents: subset.filter((row) => row[`${prefix}_captured`]).reduce((sum, row) => sum + row[`${prefix}_locked_cents`], 0) });
  const ladder = { GE_10_CENTS: (row) => row.offer_margin_cents >= 10, GE_5_CENTS: (row) => row.offer_margin_cents >= 5, GE_3_CENTS: (row) => row.offer_margin_cents >= 3, THIN_1_TO_2_CENTS: (row) => row.offer_margin_cents >= 1 && row.offer_margin_cents <= 2, ALL_OFFERED: () => true };
  return {
    source: { commit: GROUND_TRUTH_COMMIT, path: GROUND_TRUTH_PATH, sha256: groundTruth.binding.sha256 },
    denominator: { games: offered.length, cents: offered.reduce((sum, row) => sum + row.offer_margin_cents, 0), margin_ladder: { GE_10_CENTS: offered.filter(ladder.GE_10_CENTS).length, GE_5_CENTS: offered.filter(ladder.GE_5_CENTS).length, GE_3_CENTS: offered.filter(ladder.GE_3_CENTS).length, THIN_1_TO_2_CENTS: offered.filter(ladder.THIN_1_TO_2_CENTS).length }, other_classes: countBy(rows, (row) => row.offer_class) },
    standing_baseline: { valid_completed_pairs: baselineRows.length, locked_cents: baselineRows.reduce((sum, row) => sum + row.locked_delta_valid_fills_c, 0), game_capture_rate: baselineRows.length / offered.length, cents_capture_rate: baselineRows.reduce((sum, row) => sum + row.locked_delta_valid_fills_c, 0) / 3123 },
    market: Object.fromEntries(Object.entries(ladder).map(([name, predicate]) => [name, summarize(offered.filter(predicate), "market")])),
    strict: Object.fromEntries(Object.entries(ladder).map(([name, predicate]) => [name, summarize(offered.filter(predicate), "strict")])),
    by_category: [...new Set(offered.map((row) => row.category))].sort().map((category) => ({ category, market: summarize(offered.filter((row) => row.category === category), "market"), strict: summarize(offered.filter((row) => row.category === category), "strict") })),
    rows,
  };
}

function buildExamArtifacts({ candidateRun, baselineRun, groundTruth, terminalRoles, roleStats, traceStats, traceNormalizer, traceChunks, spanCloseRows, n9Binding, policyIdentity, v52eLaneIdentity, sanityFence }) {
  const marketRows = gradeRun(candidateRun.marketEvents, groundTruth, terminalRoles), strictRows = gradeRun(candidateRun.strictEvents, groundTruth, terminalRoles), baselineRows = gradeRun(baselineRun.marketEvents, groundTruth);
  const marketScore = scoreRows(marketRows), strictScore = scoreRows(strictRows), baselineScore = scoreRows(baselineRows);
  ensure(marketScore.population_D === 804 && strictScore.population_D === 804 && baselineScore.population_D === 804, "V52r exam D changed");
  ensure(marketScore.unknown_bell === 20 && strictScore.unknown_bell === 20, "UNKNOWN_BELL conservation changed");
  const offer = buildOfferDenominator(groundTruth, marketRows, strictRows);
  const perGame = marketRows.map((row) => ({ event_id: row.event_id, category: row.category, price_region: row.price_region, bell_confidence: row.bell_confidence, state: row.state, combined_entry_cents: row.combined_entry_cents, delta_vs_100_cents: Number.isInteger(row.combined_entry_cents) ? 100 - row.combined_entry_cents : null, legs: row.legs, offer: offer.rows.find((offerRow) => offerRow.event_id === row.event_id), V52L_state: baselineRows.find((base) => base.event_id === row.event_id).state, window_binding: row.window }));
  const regretRows = marketRows.flatMap((row) => row.legs.map((leg) => ({ event_id: row.event_id, category: row.category, price_region: row.price_region, bell_confidence: row.bell_confidence, state: row.state, ...leg, regret_cents: leg.valid_credited && Number.isInteger(leg.ground_truth_floor_cents) ? leg.entry_cents - leg.ground_truth_floor_cents : null, uncredited_floor_opportunity: !leg.valid_credited && Number.isInteger(leg.ground_truth_floor_cents) })));
  const regretSummary = (rows) => ({ legs: rows.length, credited_with_floor: rows.filter((row) => Number.isFinite(row.regret_cents)).length, uncredited_with_floor: rows.filter((row) => row.uncredited_floor_opportunity).length, regret_cents: distribution(rows.map((row) => row.regret_cents)) });
  const roleDownRows = regretRows.filter((row) => row.valid_credited && row.terminal_role?.role === "ROLE_DOWN" && Number.isInteger(row.ground_truth_floor_cents));
  const restKinds = new Set(["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE", "GAP_CREDIT_REPRICE_DOWN"]);
  const restMutations = candidateRun.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && restKinds.has(row.kind));
  const firstByLeg = new Map();
  for (const row of restMutations.filter((row) => row.kind === "PLACE_REST")) { const prior = firstByLeg.get(row.leg_identity); if (!prior || row.timestamp_epoch < prior.timestamp_epoch || (row.timestamp_epoch === prior.timestamp_epoch && row.receipt.localeCompare(prior.receipt) < 0)) firstByLeg.set(row.leg_identity, row); }
  const firstPosts = [...firstByLeg.values()];
  const reflex = restMutations.filter((row) => !row.birth_license?.read?.passed);
  ensure(reflex.length === 0, `REFLEX_POST=${reflex.length}`);
  const exposures = marketRows.filter((row) => row.state !== "UNKNOWN_BELL_NON_GRADEABLE").map((row) => {
    const credited = row.legs.filter((leg) => leg.valid_credited);
    if (credited.length === 1) return { event_id: row.event_id, disposition: "CREATED_UNRESOLVED", credited_leg: credited[0].leg_identity, duration_seconds: Number.isFinite(row.window.span_end_epoch) ? row.window.span_end_epoch - credited[0].fill_timestamp_epoch : null };
    if (credited.length === 2) return { event_id: row.event_id, disposition: "CREATED_RESOLVED", credited_leg: credited.sort((a, b) => a.fill_timestamp_epoch - b.fill_timestamp_epoch)[0].leg_identity, duration_seconds: Math.abs(credited[0].fill_timestamp_epoch - credited[1].fill_timestamp_epoch) };
    return { event_id: row.event_id, disposition: "NOT_CREATED", credited_leg: null, duration_seconds: null };
  });
  const named = {};
  for (const label of ["ARSMAR", "SANDAN", "PUTJEA", "POLKUH", "MERDRO"]) { const row = perGame.find((event) => event.event_id.includes(label)); ensure(row, `named event absent ${label}`); named[label] = row; }
  const categoryRows = [...new Set(marketRows.map((row) => row.category))].sort().map((category) => ({ category, market: scoreRows(marketRows.filter((row) => row.category === category)), strict: scoreRows(strictRows.filter((row) => row.category === category)), V52L: scoreRows(baselineRows.filter((row) => row.category === category)) }));
  const twoRulers = { CANON_MARKET_GRADE: { ...marketScore, role: "PRIMARY_VALID_FILL_GRADE_W1_GROUND_TRUTH_BOUND", by_category: categoryRows.map((row) => ({ category: row.category, ...row.market })), by_category_x_price_region: partition(marketRows, ["category", "price_region"]) }, STRICT_PRINT_CROSS: { ...strictScore, role: "BUILD_VERIFICATION_ONLY", by_category: categoryRows.map((row) => ({ category: row.category, ...row.strict })), by_category_x_price_region: partition(strictRows, ["category", "price_region"]) } };
  const palantirSummary = { ...traceStats, provenance_asset_ids: [...traceStats.provenance_asset_ids].sort(), trace_dictionary_entries: traceNormalizer.entries().length, clean_store_boot_assertion: n9Binding.store.boot_assertion, all_decision_rows_consumed_N2_N4_N5: traceStats.rows > 0 && [traceStats.N2_rows, traceStats.N4_rows, traceStats.N5_rows, traceStats.palantir_consumption_rows, traceStats.continuous_rows].every((value) => value === traceStats.rows), priors_never_gate: traceStats.priors_gate_true_rows === 0 };
  ensure(palantirSummary.clean_store_boot_assertion.passed && palantirSummary.all_decision_rows_consumed_N2_N4_N5 && palantirSummary.priors_never_gate, "V52r Palantir scale assertion failed");
  ensure(roleStatsPass(terminalRoles, roleStats, traceStats, traceNormalizer), "V52r role trace conservation failed");
  const artifacts = {
    "TWO_RULER_SCORECARD.json": { ...twoRulers, grading_binding: groundTruth.binding },
    "FOUR_STATE_CENSUS.json": { D: 804, market: marketScore.states, strict: strictScore.states, by_category: categoryRows, by_category_x_price_region: countBy(marketRows, (row) => `${row.category}|${row.price_region}|${row.state}`), conservation: { expected: 804, market_sum: marketRows.length, strict_sum: strictRows.length, unknown_bell: marketScore.unknown_bell, pass: marketRows.length === 804 && strictRows.length === 804 } },
    "FRONTIER.json": { denominator_population: 804, scoring_D: marketScore.scoring_D, market: marketScore.frontier, strict: strictScore.frontier, per_category: categoryRows },
    "REGRET_GAUGE.json": { ruler: "VALID_ENTRY_MINUS_W1_GROUND_TRUTH_PER_LEG_POST_ONSET_FLOOR", aggregate: regretSummary(regretRows), by_category_x_price_region: [...new Set(regretRows.map((row) => `${row.category}|${row.price_region}`))].sort().map((cell) => ({ cell, ...regretSummary(regretRows.filter((row) => `${row.category}|${row.price_region}` === cell)) })) },
    "OFFER_DENOMINATOR_CAPTURE.json": { source: offer.source, denominator: offer.denominator, standing_baseline: offer.standing_baseline, market: offer.market, strict: offer.strict, by_category: offer.by_category, formation_only_and_not_offered_separate: true },
    "VALID_DELTA_DISTRIBUTION.json": { market: marketScore.valid_delta_distribution, strict: strictScore.valid_delta_distribution, per_category: categoryRows.map((row) => ({ category: row.category, market: row.market.valid_delta_distribution, strict: row.strict.valid_delta_distribution })) },
    "DOWN_FILL_FLOOR_GAP_DISTRIBUTION.json": { valid_ROLE_DOWN_fills: roleDownRows.length, aggregate_entry_minus_ground_truth_floor_cents: distribution(roleDownRows.map((row) => row.entry_minus_floor_cents)), by_category: [...new Set(roleDownRows.map((row) => row.category))].sort().map((category) => ({ category, ...distribution(roleDownRows.filter((row) => row.category === category).map((row) => row.entry_minus_floor_cents)) })), rows: roleDownRows },
    "POSTING_TIME_AND_READ_AT_POST.json": { first_placements: firstPosts.length, rest_mutations: restMutations.length, REFLEX_POST: reflex.length, first_post_t_minus_scheduled_seconds: distribution(firstPosts.map((row) => row.t_minus_scheduled_seconds)), first_post_t_minus_actual_bell_seconds: distribution(firstPosts.map((row) => row.t_minus_actual_bell_seconds)), read_at_first_post: countBy(firstPosts, (row) => `${row.birth_license?.read?.state ?? "READ_ABSENT"}|${row.birth_license?.read?.evidence ?? "NO_EVIDENCE_CLASS"}`) },
    "PALANTIR_CONSUMPTION_SCALE_RECEIPT.json": palantirSummary,
    "CLEAN_STORE_BOOT_ASSERTION.json": n9Binding.store.boot_assertion,
    "BOTH_CLOCKS_ROLE_RECEIPT.json": { role_receipt_rows: roleStats.role_receipt_rows, fields: ["t_minus_scheduled_seconds", "t_minus_actual_bell_seconds"], missing_field_rows: roleStats.missing_both_clock_fields, pass: roleStats.missing_both_clock_fields.length === 0 },
    "EXPOSURE_CORPUS.json": { created_resolved: exposures.filter((row) => row.disposition === "CREATED_RESOLVED").length, created_unresolved: exposures.filter((row) => row.disposition === "CREATED_UNRESOLVED").length, not_created: exposures.filter((row) => row.disposition === "NOT_CREATED").length, resolved_duration_seconds: distribution(exposures.filter((row) => row.disposition === "CREATED_RESOLVED").map((row) => row.duration_seconds)), unresolved_duration_seconds: distribution(exposures.filter((row) => row.disposition === "CREATED_UNRESOLVED").map((row) => row.duration_seconds)), rows: exposures },
    "LINEAGE_V52L_V52R.json": { grading_binding: groundTruth.binding, V52L: baselineScore, V52R: marketScore, delta: { completed_pairs: marketScore.completed_pairs - baselineScore.completed_pairs, under_par_pairs: marketScore.under_par_pairs - baselineScore.under_par_pairs, locked_cents: marketScore.locked_cents - baselineScore.locked_cents } },
    "NAMED_CHECKS.json": { role: "CURRENT_BINDINGS_REPORTED_NOT_TUNED", ...named },
    "PER_BLOCK_REASON_ROLLUP.json": { missing_valid_legs: countBy(marketRows.flatMap((row) => row.legs.filter((leg) => !leg.valid_credited)), (leg) => `${leg.terminal_reason}|${leg.dominant_block_reason}`), decision_receipts: { aggregate: traceStats.by_block_reason, by_category: traceStats.by_category_x_block_reason } },
    "POLICY_BYTE_IDENTITY.json": policyIdentity,
    "V52E804_LANE_NON_REGRESSION.json": v52eLaneIdentity,
    "COHORT_30_ADAPTER_SANITY_FENCE.json": sanityFence,
    "GROUND_TRUTH_GRADING_BINDING.json": { binding: groundTruth.binding, gradeable: marketScore.scoring_D, unknown_bell: marketScore.unknown_bell },
    "CONTROL_BINDING.json": { variant: "V52R_DISPOSITION_804", frozen_policy_commit: FROZEN_V52R_COMMIT, scope: "DEV_804_ONLY", policy_edits: false, adapter_only: true, grading_source: groundTruth.binding, sealed: false, deployment: false, live: false },
    "FORBIDDEN_ACCESS_RECEIPT.json": { sealed: false, holdout: false, deployment: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, policy_edits: false },
  };
  const report = `# V52r disposition804 — full dev exam\n\nThe frozen V52r policy at ${FROZEN_V52R_COMMIT} passed the 30-game byte-identity fence before this exam. The existing v52e804 lane is protected and unchanged.\n\n- Market valid-fill four-state: ${JSON.stringify(marketScore.states)}; conservation 804; gradeable ${marketScore.scoring_D}; UNKNOWN_BELL ${marketScore.unknown_bell}.\n- Market completed/under-par ${marketScore.completed_pairs}/${marketScore.under_par_pairs}; locked ${marketScore.locked_cents}c; frontier <=93/<=95/<=97/<100/any ${marketScore.frontier.LE_93}/${marketScore.frontier.LE_95}/${marketScore.frontier.LE_97}/${marketScore.frontier.LT_100}/${marketScore.frontier.ANY_PRICE}.\n- Strict verification completed/under-par ${strictScore.completed_pairs}/${strictScore.under_par_pairs}; locked ${strictScore.locked_cents}c.\n- Honest offer denominator ${offer.denominator.games} games / ${offer.denominator.cents}c. Standing baseline ${offer.standing_baseline.valid_completed_pairs}/${offer.standing_baseline.locked_cents}c. V52r captured ${offer.market.ALL_OFFERED.captured_games} games / ${offer.market.ALL_OFFERED.captured_locked_cents}c.\n- V52l lineage: ${baselineScore.completed_pairs} completed, ${baselineScore.under_par_pairs} under par, ${baselineScore.locked_cents}c.\n- DOWN valid fills ${roleDownRows.length}; median fill-minus-floor ${distribution(roleDownRows.map((row) => row.entry_minus_floor_cents)).median}c.\n- REFLEX_POST ${reflex.length}; Palantir CLEAN boot PASS; role receipts ${roleStats.role_receipt_rows}, both-clock field omissions ${roleStats.missing_both_clock_fields.length}.\n- Full V52r decision diary retained in ${traceChunks.length} chunks; span-close rows ${spanCloseRows.length}.\n- No sealed, holdout, live, network, order, position, exit, settlement, DCA, or deployment access.\n`;
  return { artifacts, report, rows: { marketRows, strictRows, baselineRows, perGame, regretRows, offerRows: offer.rows, firstPosts, terminalRoles: [...terminalRoles.values()].sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)) } };
}

function roleStatsPass(terminalRoles, roleStats, traceStats, traceNormalizer) {
  return roleStats.role_receipt_rows > 0 && roleStats.missing_both_clock_fields.length === 0 && terminalRoles.size <= 1608 && traceNormalizer.rows() === traceStats.rows;
}

module.exports = {
  FROZEN_V52R_COMMIT,
  FROZEN_V52R_PACKAGE,
  attestFrozenPolicy,
  attestV52eLaneUnchanged,
  compareCohortBuild,
  makeExamTraceNormalizer,
  buildExamArtifacts,
  canonical,
  sha256,
};
