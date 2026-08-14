#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52k_library_backed_evidence_20260814");
const namedRoot = path.join(repo, ".claude/window1_live_v4_replay/v52k_guegom_named_observation_20260814");
const measurement = process.argv.includes("--measure-first-build");
const json = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
const sha = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
let tests = 0;
const check = (value, message) => { tests += 1; assert(value, message); };
const equal = (actual, expected, message) => { tests += 1; assert.deepStrictEqual(actual, expected, message); };
async function scan(name, visit = () => {}) {
  const lines = readline.createInterface({ input: fs.createReadStream(path.join(root, name)).pipe(zlib.createGunzip()), crlfDelay: Infinity });
  let count = 0;
  const events = new Set();
  for await (const line of lines) {
    if (!line) continue;
    const row = JSON.parse(line);
    visit(row);
    count += 1;
    if (row.event_id) events.add(row.event_id);
  }
  return { count, events };
}

async function main() {
  check(fs.existsSync(root), "V52k package root missing");
  check(fs.existsSync(namedRoot), "V52k named root missing");
  const control = json("CONTROL_BINDING.json");
  equal(control.parent_commit, "604ab3e730efe5c649b7820a3daa3a34bec2033d");
  equal(control.branch, "codex/window1-v52k-library-backed-evidence-20260814");
  equal(control.scope, "FIVE_PINS_PLUS_FRESH_25_ONLY");
  equal(control.score_or_disposition_804_run, false);

  const cohort = json("COHORT_SELECTION_RECEIPT.json");
  equal(cohort.pins.length, 5);
  equal(cohort.fresh_25.length, 25);
  equal(cohort.combined_30.length, 30);
  equal(new Set(cohort.combined_30).size, 30);
  check(/^[0-9a-f]{40}$/.test(cohort.source_implementation_commit));
  equal(cohort.seed_derivation_law, "SHA256('V52K_ITERATION10_COHORT25|' + source_implementation_commit)");
  for (const key of ["prior_V52B_fresh25_overlap_count", "prior_V52C_fresh25_overlap_count", "prior_V52D_fresh25_overlap_count", "prior_V52E_fresh25_overlap_count", "prior_V52F_fresh25_overlap_count", "prior_V52G_fresh25_overlap_count", "prior_V52H_fresh25_overlap_count", "prior_V52I_fresh25_overlap_count", "prior_V52J_fresh25_overlap_count"]) equal(cohort.exclusions[key], 0, key);
  equal(cohort.exclusions.named_observation_excluded_from_fresh_25, true);

  const receipt = json("CLAUSE_3_LIBRARY_EVIDENCE_CORRECTION_RECEIPT.json");
  equal(receipt.authorized_change, "CLAUSE_3_LIBRARY_BACKED_LEVEL_EVIDENCE_ONLY");
  equal(receipt.behavioral_base.policy, "V52H");
  equal(receipt.behavioral_base.direct_import, true);
  equal(receipt.reverted_non_validating_iterations.inherited_behavior, false);
  equal(receipt.constants_added, 0);
  equal(receipt.timing_rules_added, 0);
  equal(receipt.authority_union.post_onset_tape, true);
  equal(receipt.authority_union.validated_library, true);
  equal(receipt.authority_union.library_can_create_clause_3_authority, true);
  equal(receipt.authority_union.library_can_bypass_clause_2_read, false);
  equal(receipt.authority_union.current_touch_upper_bound, true);
  equal(receipt.authority_union.library_floor_lower_bound, true);
  equal(receipt.authority_union.clause_6_joint_sum, true);
  equal(receipt.frozen_clauses.clause_1, true);
  equal(receipt.frozen_clauses.clause_2, true);
  equal(receipt.frozen_clauses.clause_4_and_referee, true);
  equal(receipt.frozen_clauses.clause_5, true);
  equal(receipt.frozen_clauses.clause_6, true);
  equal(receipt.frozen_clauses.crediting, "TRADES_AS_TRUTH_UNCHANGED");
  equal(receipt.frozen_clauses.scavenger, false);
  equal(receipt.floor_basis.status, "CURRENT_PRE_RE-CUT");

  const boot = json("DEPTH_UNDER_VALIDATION_BOOT_RECEIPT.json");
  equal(boot.canonical_clean_store_unchanged, true);
  equal(boot.under_validation_loaded, 2);
  equal(boot.under_validation_loaded_ids, ["G_GRID_LEVEL_DISCOUNT", "G3_DIP_RECOVERY_GRADIENT"]);
  equal(boot.unvalidated_loaded, 0);
  equal(boot.quarantined_loaded, 0);
  equal(boot.superseded_loaded, 0);
  equal(boot.fallback_loads, 0);

  const assertions = json("FLOW_ASSERTIONS.json");
  if (measurement) equal(Object.entries(assertions).filter(([key, value]) => key !== "pass" && key !== "flow_assertions" && value?.pass === false).map(([key]) => key), ["no_library_backed_level_below_library_floor_or_at_above_touch"]);
  else equal(assertions.pass, true);
  equal(assertions.REFLEX_POST_zero.observed, 0);
  equal(assertions.clauses_4_5_6_and_referee_frozen.violations.length, 0);
  equal(assertions.V52i_and_V52j_behavior_reverted_direct_V52h_parent.pass, true);
  equal(assertions.library_authority_never_bypasses_clause_2_read.violations.length, 0);
  equal(assertions.every_library_consultation_records_candidate_provenance.violations.length, 0);
  equal(assertions.every_library_backed_level_binds_identity_value_and_SHA.violations.length, 0);
  if (measurement) check(assertions.no_library_backed_level_below_library_floor_or_at_above_touch.violations.length > 0);
  else equal(assertions.no_library_backed_level_below_library_floor_or_at_above_touch.violations.length, 0);
  equal(assertions.clause_6_zero_joint_target_sum_above_99.violations.length, 0);
  equal(assertions.zero_COMPLETE_AT_LOSS.pass, true);

  const differential = json("BEFORE_AFTER_DIFFERENTIAL_RECEIPT.json");
  equal(differential.frozen_clause_differences, 0);
  equal(differential.every_behavior_change_starts_at_or_after_authorized_clause, true);
  equal(differential.all_behavior_changes_authorized_by, "CLAUSE_3_LIBRARY_BACKED_LEVEL_EVIDENCE_ONLY");

  const states = json("FOUR_STATE_OBSERVATION_30.json");
  equal(states.conservation.pass, true);
  equal(states.candidate.states.COMPLETE_AT_LOSS || 0, 0);
  const outcomes = json("PER_GAME_OUTCOME_TABLE.json");
  equal(outcomes.length, 30);
  equal(new Set(outcomes.map((row) => row.event_id)).size, 30);
  check(outcomes.every((row) => ["COMPLETE_AT_DELTA", "PARTIAL_FOR_REASON", "NEITHER_FOR_REASON"].includes(row.state)));
  check(outcomes.every((row) => row.legs.length === 2));
  check(outcomes.every((row) => row.legs.every((leg) => Object.prototype.hasOwnProperty.call(leg, "level_evidence_authority_at_entry_or_terminal") && Object.prototype.hasOwnProperty.call(leg, "library_supported_floor_cents") && Object.prototype.hasOwnProperty.call(leg, "fill_t_minus_scheduled_seconds") && Object.prototype.hasOwnProperty.call(leg, "floor_t_minus_scheduled_seconds"))));

  const summary = json("LIBRARY_BACKED_EVIDENCE_SUMMARY.json");
  check(summary.evaluation_receipts > 0);
  check(summary.applicable_library_receipts > 0);
  equal(summary.pre_stated_claims.library_backed_levels_actually_stand_below_shown_range, summary.library_backed_stands_below_shown_range.receipts > 0);
  equal(summary.pre_stated_claims.new_one_sided_exposure_counted_both_ways_per_game, true);
  equal(summary.pre_stated_claims.REFLEX_POST_zero, true);
  check(Array.isArray(summary.faller_side_fills.rows));
  check(Array.isArray(summary.climber_completion_preservation.rows));
  check(Array.isArray(summary.one_sided_exposure_changes.created));
  check(Array.isArray(summary.one_sided_exposure_changes.resolved));

  const evidenceViolations = { provenance: 0, status: 0, lower: 0, touch: 0, read: 0 };
  const evidence = await scan("LIBRARY_BACKED_LEVEL_EVIDENCE_LEDGER.jsonl.gz", (row) => {
    const item = row.library_backed_level_evidence;
    if (!item?.applicable) return;
    if (item.prior_provenance?.length !== 2 || item.prior_provenance.some((asset) => !asset.asset_id || !/^[0-9a-f]{64}$/.test(asset.source_sha256))) evidenceViolations.provenance += 1;
    if (item.prior_provenance?.some((asset) => asset.status !== "UNDER-VALIDATION_V52I")) evidenceViolations.status += 1;
    if (Number.isInteger(row.final_target_cents) && row.final_target_cents < item.library_supported_floor_cents) evidenceViolations.lower += 1;
    if (Number.isInteger(row.final_target_cents) && row.final_target_cents >= item.current_touch_ask_cents) evidenceViolations.touch += 1;
    if (item.frozen_clause_2_read_passed !== true && !(measurement && item.frozen_clause_2_read_passed === undefined)) evidenceViolations.read += 1;
  });
  check(evidence.count > 0);
  equal(evidenceViolations.provenance, 0);
  equal(evidenceViolations.status, 0);
  equal(evidenceViolations.lower, 0);
  equal(evidenceViolations.touch, 0);
  equal(evidenceViolations.read, 0);

  const prior = await scan("LIBRARY_PRIOR_CONSUMPTION_LEDGER.jsonl.gz");
  check(prior.count > 0);
  const pairBudget = await scan("PAIR_BUDGET_RECORDS.jsonl.gz");
  equal(pairBudget.events.size, 30);
  const trace = json("FULL_DECISION_TRACE_MANIFEST.json");
  equal(trace.baseline.events, 30);
  equal(trace.candidate.events, 30);
  equal(trace.baseline.conservation_pass, true);
  equal(trace.candidate.conservation_pass, true);
  equal(new Set(trace.candidate.chunks.flatMap((row) => row.event_ids)).size, 30);
  check(trace.candidate.chunks.every((row) => row.bytes < 100000000));

  const named = json("GUEGOM_NAMED_OBSERVATION.json");
  check(named.event_id.includes("GUEGOM"));
  const namedManifest = json("GUEGOM_NAMED_BEFORE_AFTER_TRACE_MANIFEST.json");
  equal(namedManifest.conservation_pass, true);
  check(namedManifest.chunks.every((row) => row.bytes < 100000000));

  const source = json("SOURCE_HASH_MANIFEST.json");
  for (const name of ["arb-executor/analysis/window1_v52k_library_backed_evidence.js", "arb-executor/analysis/build_window1_v52k_library_backed_evidence.js", "arb-executor/analysis/build_window1_v52k_guegom_named_observation.js", "arb-executor/tests/test_window1_v52k_library_backed_evidence.js", "arb-executor/tests/test_window1_v52k_library_backed_evidence_package.js"]) {
    const bytes = fs.readFileSync(path.join(repo, name));
    if (measurement && ["arb-executor/analysis/window1_v52k_library_backed_evidence.js", "arb-executor/tests/test_window1_v52k_library_backed_evidence_package.js"].includes(name)) check(/^[0-9a-f]{64}$/.test(source.files[name].sha256), `${name} disposable manifest hash form`);
    else equal(source.files[name].sha256, sha(bytes), name);
  }

  const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json");
  equal(forbidden.full_804_run, false);
  equal(forbidden.holdout, false);
  equal(forbidden.live, false);
  equal(forbidden.network_runtime, false);
  equal(forbidden.orders, false);
  equal(forbidden.deployment, false);
  equal(forbidden.scavenger, false);
  const construction = json("CONSTRUCTION_STATUS.json");
  equal(construction.behavioral_edits_beyond_clause_3_library_backed_level_evidence, false);

  const det = json("DETERMINISM_RECEIPT.json");
  equal(det.clean_builds, measurement ? 1 : 2);
  equal(det.byte_identical, measurement ? null : true);
  if (measurement) {
    const pending = json("TEST_RESULTS_PENDING_MEASUREMENT.json");
    equal(pending.status, "NOT_RUN");
    equal(pending.assertions, null);
  } else {
    const result = json("TEST_RESULTS.json");
    equal(result.status, "PASS");
    check(result.suites.some((row) => row.file === "arb-executor/tests/test_window1_v52k_library_backed_evidence_package.js"));
  }
  console.log(JSON.stringify({ tests, pass: true, library_receipts: evidence.count, below_shown_range_receipts: summary.library_backed_stands_below_shown_range.receipts }));
}

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
