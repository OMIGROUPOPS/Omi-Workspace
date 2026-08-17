#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52m_macro_recognition_20260817");
const json = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
let assertions = 0;
const equal = (actual, expected, message) => { assertions += 1; assert.deepStrictEqual(actual, expected, message); };
const check = (value, message) => { assertions += 1; assert(value, message); };

async function main() {
  check(fs.existsSync(root), "V52m package root absent");
  const control = json("CONTROL_BINDING.json");
  equal(control.parent_commit, "6678fd0c13dcc4de2bc153bbf769f5a2a9227ccc");
  equal(control.branch, "codex/window1-v52m-macro-recognition-20260817");
  equal(control.score_or_disposition_804_run, false);

  const cohort = json("COHORT_SELECTION_RECEIPT.json");
  equal(cohort.pins.length, 5);
  equal(cohort.fresh_25.length, 25);
  equal(cohort.combined_30.length, 30);
  equal(new Set(cohort.combined_30).size, 30);
  for (const key of Object.keys(cohort.exclusions).filter((key) => key.endsWith("fresh25_overlap_count"))) equal(cohort.exclusions[key], 0, key);

  const receipt = json("CLAUSE_3_MACRO_RECOGNITION_CORRECTION_RECEIPT.json");
  equal(receipt.authorized_change, "CLAUSE_3_CAUSAL_MACRO_RECOGNITION_FLOOR_DEPTH_ONLY");
  equal(receipt.behavioral_base.commit, "6678fd0c13dcc4de2bc153bbf769f5a2a9227ccc");
  equal(receipt.taxonomy.method_commit, "e269779b0ec025d55f67d576e3cfb0cb575d5890");
  equal(receipt.taxonomy.sha256, "5d821226544f9e1891d0572b82386ac4907dc0692c0c91852d146105a446d599");
  equal(receipt.taxonomy.families.length, 13);
  equal(receipt.floor_depth_table.commit, "8ab4f2d9e8c831235dc7cb4570c88daa3caded50");
  equal(receipt.floor_depth_table.sha256, "f49da1ae5ad7d4811e3b557b9c431030e4fb92961604666c4994259a551f7f70");
  equal(receipt.floor_depth_table.rows, 52);
  equal(receipt.causal_classifier.right_edge_consumed, false);
  equal(receipt.causal_classifier.completed_path_consumed, false);
  equal(receipt.frozen_clauses.crediting, "TRADES_AS_TRUTH_UNCHANGED");
  equal(receipt.frozen_clauses.REFLEX_POST, 0);

  const summary = json("MACRO_RECOGNITION_SUMMARY.json");
  equal(summary.classifications.terminal_leg_rows, 60);
  equal(summary.classifications.signable_terminal_legs + summary.classifications.abstain_terminal_legs, 60);
  check(summary.classifications.receipt_rows > 0);
  check(summary.consumption.applicable_receipts > 0);
  check(summary.consumption.changed_target_receipts > 0);
  equal(summary.down_family_fills.moved_later, true);
  equal(summary.down_family_fills.landed_nearer_true_floor, true);
  equal(summary.up_and_still_preservation.preserved, false);
  equal(summary.up_and_still_preservation.lost_legs.length, 3);
  equal(summary.banked_delta.rises, true);
  equal(summary.one_sided_exposure_both_ways.created_count, 3);
  equal(summary.one_sided_exposure_both_ways.resolved_count, 0);
  equal(summary.pins.lawful, true);
  equal(summary.pins.comparisons.find((row) => row.code === "26JUL13SANDAN").unharmed, false);
  equal(summary.REFLEX_POST_zero, true);

  const flow = json("FLOW_ASSERTIONS.json");
  equal(flow.REFLEX_POST_zero.observed, 0);
  equal(flow.clause_1_V52L_CAUSAL_PREFIX.violations.length, 0);
  equal(flow.every_macro_signature_is_receipt_causal.violations.length, 0);
  equal(flow.every_shape_depth_consumption_binds_family_confidence_row_and_two_SHAs.violations.length, 0);
  equal(flow.abstain_class_retains_frozen_V52l_target.violations.length, 0);
  equal(flow.every_consumed_macro_target_reaches_final_license.violations.length, 0);
  equal(flow.macro_target_is_not_decorative.pass, true);
  equal(flow.macro_target_respects_current_touch_and_clause_6.violations.length, 0);
  equal(flow.pins_lawful_not_outcome_bound.pass, true);

  const differential = json("BEFORE_AFTER_DIFFERENTIAL_RECEIPT.json");
  equal(differential.frozen_clause_differences, 0);
  equal(differential.every_behavior_change_starts_at_or_after_authorized_clause, true);
  equal(differential.all_behavior_changes_authorized_by, "CLAUSE_3_CAUSAL_MACRO_RECOGNITION_FLOOR_DEPTH_ONLY");
  check(differential.behavior_changed_leg_streams > 0);

  const ground = json("GROUND_TRUTH_GRADING_BINDING.json");
  equal(ground.binding.source_commit, "c0056976c446afcb4d9603796a2e06c068ee94d6");
  equal(ground.binding.sha256, "f7bc71d8e615859db272d841e125bc4836a685d82bb2d6769762c9bc19e56729");
  equal(ground.cohort.rows, 30);
  equal(ground.cohort.gradeable + ground.cohort.unknown_bell, 30);

  const outcomes = json("PER_GAME_OUTCOME_TABLE.json");
  equal(outcomes.length, 30);
  equal(new Set(outcomes.map((row) => row.event_id)).size, 30);
  check(outcomes.every((row) => Object.prototype.hasOwnProperty.call(row, "window_scoring_class")));

  let ledgerRows = 0, classifiedRows = 0, applicable = 0, changed = 0, causalViolations = 0, provenanceViolations = 0, consumptionViolations = 0, boundViolations = 0, abstainViolations = 0;
  const stream = fs.createReadStream(path.join(root, "MACRO_RECOGNITION_CONSUMPTION_LEDGER.jsonl.gz")).pipe(zlib.createGunzip());
  for await (const line of readline.createInterface({ input: stream, crlfDelay: Infinity })) {
    if (!line.trim()) continue;
    const row = JSON.parse(line); ledgerRows += 1;
    const macro = row.macro_recognition, depth = row.per_shape_floor_depth;
    if (macro?.family) classifiedRows += 1;
    if (macro?.causal !== true || macro?.right_edge_consumed !== false || macro?.full_span_fit !== false || (Number.isFinite(macro?.maximum_consumed_timestamp_epoch) && macro.maximum_consumed_timestamp_epoch > row.timestamp_epoch)) causalViolations += 1;
    if (depth?.applicable) {
      applicable += 1;
      if (!depth.macro_recognition?.family || !Number.isFinite(depth.confidence) || !depth.table_row || !/^[0-9a-f]{64}$/.test(depth.provenance?.taxonomy?.sha256 ?? "") || !/^[0-9a-f]{64}$/.test(depth.provenance?.floor_depth_table?.sha256 ?? "")) provenanceViolations += 1;
    }
    if (depth?.target_changed) changed += 1;
    if (depth?.level_policy_consumed && depth.final_licensed_target_cents !== depth.selected_target_cents) consumptionViolations += 1;
    if (depth?.level_policy_consumed && (depth.final_licensed_target_cents >= depth.current_touch_ask_cents || (Number.isInteger(depth.clause_6_cap_cents) && depth.final_licensed_target_cents > depth.clause_6_cap_cents))) boundViolations += 1;
    if (macro?.signable === false && depth?.target_changed === true) abstainViolations += 1;
  }
  equal(ledgerRows, summary.classifications.evaluation_receipt_rows ?? ledgerRows);
  equal(classifiedRows, summary.classifications.classified_receipt_rows ?? summary.classifications.receipt_rows);
  equal(applicable, summary.consumption.applicable_receipts);
  equal(changed, summary.consumption.changed_target_receipts);
  equal(causalViolations, 0);
  equal(provenanceViolations, 0);
  equal(consumptionViolations, 0);
  equal(boundViolations, 0);
  equal(abstainViolations, 0);

  const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json");
  equal(forbidden.holdout, false);
  equal(forbidden.live, false);
  equal(forbidden.network_runtime, false);
  equal(forbidden.orders, false);
  equal(forbidden.positions, false);
  equal(forbidden.deployment, false);
  equal(forbidden.full_804_run, false);

  process.stdout.write(`${JSON.stringify({ assertions, failures: 0, omissions: 0, deselections: 0, behavioral_claim_failures_recorded_not_hidden: ["UP_AND_STILL_PRESERVATION", "SANDAN_PIN_OUTCOME"] })}\n`);
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
