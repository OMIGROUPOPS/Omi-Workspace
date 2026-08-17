#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52n_recognition_confidence_gates_20260817");
const json = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
let assertions = 0;
const equal = (actual, expected, message) => { assertions += 1; assert.deepStrictEqual(actual, expected, message); };
const check = (value, message) => { assertions += 1; assert(value, message); };

async function main() {
  check(fs.existsSync(root), "V52n package root absent");
  const control = json("CONTROL_BINDING.json");
  equal(control.parent_commit, "da4fd13b2c2ba068ceefc7ba10d6dee6c7667626");
  equal(control.branch, "codex/window1-v52n-recognition-confidence-gates-20260817");
  equal(control.score_or_disposition_804_run, false);

  const cohort = json("COHORT_SELECTION_RECEIPT.json");
  equal(cohort.pins.length, 5);
  equal(cohort.fresh_25.length, 25);
  equal(cohort.combined_30.length, 30);
  equal(new Set(cohort.combined_30).size, 30);
  for (const key of Object.keys(cohort.exclusions).filter((key) => key.endsWith("fresh25_overlap_count"))) equal(cohort.exclusions[key], 0, key);

  const receipt = json("CLAUSE_3_RECOGNITION_CONFIDENCE_GATE_CORRECTION_RECEIPT.json");
  equal(receipt.authorized_change, "CLAUSE_3_RECOGNITION_CONFIDENCE_GATE_ONLY");
  equal(receipt.behavioral_base.commit, "da4fd13b2c2ba068ceefc7ba10d6dee6c7667626");
  equal(receipt.behavioral_base.V52l_lineage, "6678fd0c13dcc4de2bc153bbf769f5a2a9227ccc");
  equal(receipt.behavioral_base.depth_targeting_on_bound_down_families_unchanged, true);
  equal(receipt.taxonomy.method_commit, "e269779b0ec025d55f67d576e3cfb0cb575d5890");
  equal(receipt.taxonomy.sha256, "5d821226544f9e1891d0572b82386ac4907dc0692c0c91852d146105a446d599");
  equal(receipt.floor_depth_table.commit, "8ab4f2d9e8c831235dc7cb4570c88daa3caded50");
  equal(receipt.floor_depth_table.sha256, "f49da1ae5ad7d4811e3b557b9c431030e4fb92961604666c4994259a551f7f70");
  equal(receipt.floor_depth_table.rows, 52);
  equal(receipt.confidence_gate.pinned_early_checkpoint_f, 0.5);
  equal(receipt.confidence_gate.pinned_directional_declaration_cents, 2);
  equal(receipt.confidence_gate.new_constants, 0);
  equal(receipt.confidence_gate.right_edge_consumed, false);
  equal(receipt.confidence_gate.full_span_fit_consumed, false);
  equal(receipt.frozen_clauses.crediting, "TRADES_AS_TRUTH_UNCHANGED");
  equal(receipt.frozen_clauses.scavenger, false);
  equal(receipt.frozen_clauses.REFLEX_POST, 0);

  const summary = json("MACRO_RECOGNITION_SUMMARY.json");
  equal(summary.classifications.terminal_leg_rows, 60);
  equal(summary.classifications.signable_terminal_legs + summary.classifications.abstain_terminal_legs, 60);
  check(summary.classifications.evaluation_receipt_rows > 0);
  check(summary.classifications.classified_receipt_rows > 0);
  check(summary.classifications.proposed_receipt_frequency.SLEEPER > 0);
  equal(summary.classifications.broad_match_adjudication, "REPORTED_NOT_FORCED; NO NUMERIC DISTANCE BAR INVENTED");
  check(summary.consumption.applicable_receipts > 0);
  check(summary.consumption.changed_target_receipts > 0);
  equal(summary.down_family_fills.retained_at_or_near_one_cent, false);
  equal(summary.pins.lawful, true);
  equal(summary.REFLEX_POST_zero, true);
  equal(summary.one_sided_exposure_both_ways.created.length, summary.one_sided_exposure_both_ways.created_count);
  equal(summary.one_sided_exposure_both_ways.resolved.length, summary.one_sided_exposure_both_ways.resolved_count);

  const flow = json("FLOW_ASSERTIONS.json");
  equal(flow.REFLEX_POST_zero.observed, 0);
  equal(flow.every_macro_signature_is_receipt_causal.violations.length, 0);
  equal(flow.every_shape_depth_consumption_binds_family_confidence_row_and_two_SHAs.violations.length, 0);
  equal(flow.abstain_class_retains_frozen_V52l_target.violations.length, 0);
  equal(flow.every_consumed_macro_target_reaches_final_license.violations.length, 0);
  equal(flow.macro_target_respects_current_touch_and_clause_6.violations.length, 0);
  equal(flow.every_classification_receipts_confidence_vs_pinned_gate.violations.length, 0);
  equal(flow.below_gate_abstains_to_V52l.violations.length, 0);
  equal(flow.bound_family_meets_pinned_f05_and_2c_declaration.violations.length, 0);
  equal(flow.recognition_is_reattempted_as_evidence_accrues.pass, true);
  equal(flow.pins_lawful_not_outcome_bound.pass, true);
  equal(flow.pass, true);

  const differential = json("BEFORE_AFTER_DIFFERENTIAL_RECEIPT.json");
  equal(differential.frozen_clause_differences, 0);
  equal(differential.every_behavior_change_starts_at_or_after_authorized_clause, true);
  equal(differential.all_behavior_changes_authorized_by, "CLAUSE_3_RECOGNITION_CONFIDENCE_GATE_ONLY");
  check(differential.behavior_changed_leg_streams > 0);

  const ground = json("GROUND_TRUTH_GRADING_BINDING.json");
  equal(ground.binding.source_commit, "c0056976c446afcb4d9603796a2e06c068ee94d6");
  equal(ground.binding.sha256, "f7bc71d8e615859db272d841e125bc4836a685d82bb2d6769762c9bc19e56729");
  equal(ground.cohort.rows, 30);
  equal(ground.cohort.gradeable + ground.cohort.unknown_bell, 30);

  const outcomes = json("PER_GAME_OUTCOME_TABLE.json");
  equal(outcomes.length, 30);
  equal(new Set(outcomes.map((row) => row.event_id)).size, 30);
  check(outcomes.every((row) => row.leg_macro_recognition && Object.keys(row.leg_macro_recognition).length === 2));
  check(outcomes.every((row) => Object.values(row.leg_macro_recognition).every((leg) => Object.prototype.hasOwnProperty.call(leg, "confidence_gate"))));

  let rows = 0, gateRows = 0, passRows = 0, abstainRows = 0, gateViolations = 0, abstainTargetViolations = 0;
  const stream = fs.createReadStream(path.join(root, "MACRO_RECOGNITION_CONSUMPTION_LEDGER.jsonl.gz")).pipe(zlib.createGunzip());
  for await (const line of readline.createInterface({ input: stream, crlfDelay: Infinity })) {
    if (!line.trim()) continue;
    const row = JSON.parse(line); rows += 1;
    const gate = row.macro_recognition?.recognition_confidence_gate;
    if (!gate) continue;
    gateRows += 1;
    if (gate.passed) {
      passRows += 1;
      if (!gate.gate?.median_declaration_by_pinned_checkpoint || !gate.gate?.receipt_has_pinned_directional_declaration || row.macro_recognition?.signable !== true) gateViolations += 1;
    } else {
      abstainRows += 1;
      if (row.macro_recognition?.signable !== false || row.per_shape_floor_depth?.target_changed === true) abstainTargetViolations += 1;
    }
  }
  equal(rows, summary.classifications.evaluation_receipt_rows);
  equal(gateRows, summary.classifications.evaluation_receipt_rows);
  check(passRows > 0);
  check(abstainRows > 0);
  equal(gateViolations, 0);
  equal(abstainTargetViolations, 0);

  const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json");
  equal(forbidden.holdout, false);
  equal(forbidden.live, false);
  equal(forbidden.network_runtime, false);
  equal(forbidden.orders, false);
  equal(forbidden.positions, false);
  equal(forbidden.deployment, false);
  equal(forbidden.full_804_run, false);

  const deterministic = json("DETERMINISM_RECEIPT.json");
  equal(deterministic.clean_builds, 2);
  equal(deterministic.byte_identical, true);
  equal(deterministic.mismatches.length, 0);

  process.stdout.write(`${JSON.stringify({ assertions, failures: 0, omissions: 0, deselections: 0, behavioral_claims_reported_not_forced: true })}\n`);
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
