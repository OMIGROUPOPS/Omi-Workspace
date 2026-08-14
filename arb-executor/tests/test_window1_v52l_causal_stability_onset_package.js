#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52l_causal_stability_onset_20260814");
const json = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
let assertions = 0;
const equal = (actual, expected, message) => { assertions += 1; assert.deepStrictEqual(actual, expected, message); };
const check = (value, message) => { assertions += 1; assert(value, message); };

check(fs.existsSync(root), "V52l package root absent");
const control = json("CONTROL_BINDING.json");
equal(control.parent_commit, "fc17d0d3ec3db4795d2e25a986bb9bfa1806714b");
equal(control.branch, "codex/window1-v52l-causal-onset-20260814");
equal(control.score_or_disposition_804_run, false);

const cohort = json("COHORT_SELECTION_RECEIPT.json");
equal(cohort.pins.length, 5);
equal(cohort.fresh_25.length, 25);
equal(cohort.combined_30.length, 30);
for (const key of Object.keys(cohort.exclusions).filter((key) => key.endsWith("fresh25_overlap_count"))) equal(cohort.exclusions[key], 0, key);

const receipt = json("CLAUSE_1_CAUSAL_ONSET_CORRECTION_RECEIPT.json");
equal(receipt.authorized_change, "CLAUSE_1_CAUSAL_STABILITY_ONSET_ONLY");
equal(receipt.right_edge_independence.pass, true);
equal(receipt.right_edge_independence.rows.length, 30);
equal(receipt.onset_timing_shifts.conservation.pass, true);
equal(receipt.frozen_clauses.clause_2, true);
equal(receipt.frozen_clauses.clause_3, true);
equal(receipt.frozen_clauses.clause_4_and_referee, true);
equal(receipt.frozen_clauses.clause_5, true);
equal(receipt.frozen_clauses.clause_6, true);
equal(receipt.frozen_clauses.crediting, "TRADES_AS_TRUTH_UNCHANGED");
equal(receipt.lineage_disposition, "OBSERVATION_ONLY; ADOPT_OR_HOLD_RESERVED_TO_OPERATOR_AT_DOCK");

const edge = json("RIGHT_EDGE_INDEPENDENCE_RECEIPT.json");
equal(edge.pass, true);
check(edge.rows.every((row) => row.identical_onsets && row.pass));

const flow = json("FLOW_ASSERTIONS.json");
equal(flow.pass, true);
equal(flow.REFLEX_POST_zero.observed, 0);
equal(flow.clause_1_V52L_CAUSAL_PREFIX.violations.length, 0);
equal(flow.no_full_span_or_right_edge_input_in_clause_1.violations.length, 0);
equal(flow.clauses_2_through_6_function_identity.pass, true);
equal(flow.clause_6_zero_joint_target_sum_above_99.violations.length, 0);
equal(flow.pins_lawful_not_outcome_bound.pass, true);

const ground = json("GROUND_TRUTH_GRADING_BINDING.json");
equal(ground.binding.source_commit, "c0056976c446afcb4d9603796a2e06c068ee94d6");
equal(ground.binding.sha256, "f7bc71d8e615859db272d841e125bc4836a685d82bb2d6769762c9bc19e56729");
equal(ground.cohort.rows, 30);
equal(ground.cohort.gradeable + ground.cohort.unknown_bell, 30);

const four = json("FOUR_STATE_OBSERVATION_30.json");
equal(four.grading_binding.sha256, ground.binding.sha256);
equal(four.conservation.pass, true);
equal(Object.values(four.candidate.states).reduce((sum, value) => sum + value, 0), 30);

const outcomes = json("PER_GAME_OUTCOME_TABLE.json");
equal(outcomes.length, 30);
equal(new Set(outcomes.map((row) => row.event_id)).size, 30);
check(outcomes.every((row) => Object.prototype.hasOwnProperty.call(row, "window_scoring_class")));
check(outcomes.every((row) => Object.keys(row.leg_onsets).length === 2));

const diff = json("BEFORE_AFTER_DIFFERENTIAL_RECEIPT.json");
equal(diff.frozen_clause_differences, 0);
equal(diff.every_behavior_change_starts_at_or_after_authorized_clause, true);
equal(diff.all_behavior_changes_authorized_by, "CLAUSE_1_CAUSAL_STABILITY_ONSET_ONLY");

const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json");
equal(forbidden.holdout, false);
equal(forbidden.live, false);
equal(forbidden.network_runtime, false);
equal(forbidden.full_804_run, false);

process.stdout.write(`${JSON.stringify({ assertions, failures: 0, omissions: 0, deselections: 0 })}\n`);
