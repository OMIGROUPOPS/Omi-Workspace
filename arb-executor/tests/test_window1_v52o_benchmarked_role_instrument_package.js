#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52o_benchmarked_role_instrument_20260817");
const json = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
let assertions = 0;
const equal = (actual, expected, message) => { assertions += 1; assert.deepStrictEqual(actual, expected, message); };
const check = (value, message) => { assertions += 1; assert(value, message); };

async function main() {
  check(fs.existsSync(root), "V52o package absent");
  const control = json("CONTROL_BINDING.json");
  equal(control.parent_commit, "74a702c8b100dedcba69a3637531ce6d77896eb2");
  equal(control.branch, "codex/window1-v52o-benchmarked-role-instrument-20260817");
  equal(control.score_or_disposition_804_run, false);

  const cohort = json("COHORT_SELECTION_RECEIPT.json");
  equal(cohort.pins.length, 5);
  equal(cohort.fresh_25.length, 25);
  equal(cohort.combined_30.length, 30);
  equal(new Set(cohort.combined_30.map((row) => row.event_id)).size, 30);
  for (const key of Object.keys(cohort.exclusions).filter((key) => key.endsWith("fresh25_overlap_count"))) equal(cohort.exclusions[key], 0, key);

  const receipt = json("CLAUSE_3_BENCHMARKED_ROLE_INSTRUMENT_CORRECTION_RECEIPT.json");
  equal(receipt.authorized_change, "CLAUSE_3_BENCHMARKED_EARLY_ROLE_INSTRUMENT_ONLY");
  equal(receipt.parent.commit, "74a702c8b100dedcba69a3637531ce6d77896eb2");
  equal(receipt.behavioral_lineage.commit, "6678fd0c13dcc4de2bc153bbf769f5a2a9227ccc");
  equal(receipt.role_rule.rule.threshold_cents, 2);
  equal(receipt.role_rule.rule.new_constants, 0);
  equal(receipt.role_rule.rule.taxonomy_commit, "e269779b0ec025d55f67d576e3cfb0cb575d5890");
  equal(receipt.role_rule.source_csv_sha256, "3e99b58929e05e71c1190f432671bbfc718e48019f1bc246ee7c426955d5c330");
  equal(receipt.depth_derivation.length, 4);
  check(receipt.depth_derivation.every((row) => row.component_rows.length > 0 && row.borrowed_from === null && row.interpolation === false));
  equal(receipt.frozen_clauses.crediting, "TRADES_AS_TRUTH_UNCHANGED");
  equal(receipt.frozen_clauses.scavenger, false);
  equal(receipt.frozen_clauses.REFLEX_POST, 0);

  const summary = json("BENCHMARKED_ROLE_INSTRUMENT_SUMMARY.json");
  equal(summary.terminal_roles.length, 60);
  equal(summary.coverage.terminal_legs, 60);
  check(summary.coverage.called_all_legs > 0);
  check(summary.coverage.called_truth_role_legs > 0);
  check(summary.accuracy.called_truth_role_legs > 0);
  check(summary.accuracy.accuracy >= 0 && summary.accuracy.accuracy <= 1);
  equal(summary.rule_binding.new_constants, 0);
  equal(summary.rule_binding.exact_literal_reinterpreted, false);
  equal(summary.down_depth_aggregate_derivation.length, 4);
  equal(summary.ROLE_DOWN_fills.rows.filter((row) => Number.isInteger(row.entry_minus_ground_truth_floor_cents)).length, summary.ROLE_DOWN_fills.floor_gap_cents.n);
  equal(summary.one_sided_exposure_both_ways.created.length, summary.one_sided_exposure_both_ways.created_count);
  equal(summary.one_sided_exposure_both_ways.resolved.length, summary.one_sided_exposure_both_ways.resolved_count);
  equal(summary.pins.lawful, true);
  equal(summary.REFLEX_POST_zero, true);

  const aggregates = json("ROLE_DOWN_DEPTH_AGGREGATE.json");
  equal(aggregates.rows.length, 4);
  equal(aggregates.source.commit, "8ab4f2d9e8c831235dc7cb4570c88daa3caded50");
  equal(aggregates.source.sha256, "f49da1ae5ad7d4811e3b557b9c431030e4fb92961604666c4994259a551f7f70");
  check(aggregates.rows.every((row) => Number.isFinite(row.depth_below_open_cents)));

  const controls = json("V52M_V52N_OBSERVATION_CONTROLS.json");
  equal(Object.keys(controls).sort(), ["V52M_OBSERVATION_CONTROL", "V52N_OBSERVATION_CONTROL"]);
  equal(controls.V52M_OBSERVATION_CONTROL.rows.length, 30);
  equal(controls.V52N_OBSERVATION_CONTROL.rows.length, 30);

  const flow = json("FLOW_ASSERTIONS.json");
  equal(flow.REFLEX_POST_zero.observed, 0);
  equal(flow.every_macro_signature_is_receipt_causal.violations.length, 0);
  equal(flow.exact_benchmark_role_rule_on_every_evaluation.violations.length, 0);
  equal(flow.role_matches_literal_drift_arithmetic.violations.length, 0);
  equal(flow.every_ROLE_DOWN_consumption_binds_aggregate_and_two_SHAs.violations.length, 0);
  equal(flow.ROLE_UP_and_ABSTAIN_preserve_V52l_level.violations.length, 0);
  equal(flow.every_consumed_ROLE_DOWN_target_reaches_final_license.violations.length, 0);
  equal(flow.role_depth_target_respects_touch_and_clause_6.violations.length, 0);
  equal(flow.role_depth_target_is_not_decorative.pass, true);
  equal(flow.role_re_evaluated_as_evidence_accrues.pass, true);
  equal(flow.pins_lawful_not_outcome_bound.pass, true);
  equal(flow.pass, true);

  const differential = json("BEFORE_AFTER_DIFFERENTIAL_RECEIPT.json");
  equal(differential.frozen_clause_differences, 0);
  equal(differential.every_behavior_change_starts_at_or_after_authorized_clause, true);
  equal(differential.all_behavior_changes_authorized_by, "CLAUSE_3_BENCHMARKED_EARLY_ROLE_INSTRUMENT_ONLY");
  check(differential.behavior_changed_leg_streams > 0);

  const outcomes = json("PER_GAME_OUTCOME_TABLE.json");
  equal(outcomes.length, 30);
  equal(new Set(outcomes.map((row) => row.event_id)).size, 30);
  check(outcomes.every((row) => row.leg_macro_recognition && Object.keys(row.leg_macro_recognition).length === 2));
  check(outcomes.every((row) => Object.values(row.leg_macro_recognition).every((leg) => Object.prototype.hasOwnProperty.call(leg, "role_at_entry_or_terminal"))));

  let rows = 0, roleRows = 0, badArithmetic = 0, badProvenance = 0;
  const stream = fs.createReadStream(path.join(root, "BENCHMARKED_ROLE_CONSUMPTION_LEDGER.jsonl.gz")).pipe(zlib.createGunzip());
  for await (const line of readline.createInterface({ input: stream, crlfDelay: Infinity })) {
    if (!line.trim()) continue;
    const row = JSON.parse(line); rows += 1;
    if (!row.role) continue;
    roleRows += 1;
    const expected = row.drift_cents === null ? "ABSTAIN" : row.drift_cents >= 2 ? "ROLE_UP" : row.drift_cents <= -2 ? "ROLE_DOWN" : "ABSTAIN";
    if (row.role !== expected) badArithmetic += 1;
    if (row.rule?.taxonomy_commit !== "e269779b0ec025d55f67d576e3cfb0cb575d5890" || row.rule?.threshold_cents !== 2) badProvenance += 1;
  }
  equal(rows, summary.role_receipt_count);
  equal(roleRows, rows);
  equal(badArithmetic, 0);
  equal(badProvenance, 0);

  const ground = json("GROUND_TRUTH_GRADING_BINDING.json");
  equal(ground.binding.source_commit, "c0056976c446afcb4d9603796a2e06c068ee94d6");
  equal(ground.cohort.rows, 30);
  equal(ground.cohort.gradeable + ground.cohort.unknown_bell, 30);
  const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json");
  for (const key of ["holdout", "live", "network_runtime", "orders", "positions", "deployment", "full_804_run", "scavenger"]) equal(forbidden[key], false, key);
  const deterministic = json("DETERMINISM_RECEIPT.json");
  equal(deterministic.clean_builds, 2);
  equal(deterministic.byte_identical, true);
  equal(deterministic.mismatches.length, 0);

  process.stdout.write(`${JSON.stringify({ assertions, failures: 0, omissions: 0, deselections: 0 })}\n`);
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
