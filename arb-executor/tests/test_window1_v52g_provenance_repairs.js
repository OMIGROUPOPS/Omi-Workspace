#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const pkg = path.join(repo, ".claude/window1_live_v4_replay/v52g_provenance_repairs_20260813");
const read = (name) => JSON.parse(fs.readFileSync(path.join(pkg, name), "utf8"));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(pkg, name))).toString("utf8").trim().split("\n").filter(Boolean).map(JSON.parse);

assert.ok(fs.existsSync(pkg), "provenance repair package missing");
const onset = read("ONSET_INPUT_GRAIN_UNIFICATION_RECEIPT.json");
assert.strictEqual(onset.repair_class, "RECEIPTS_ONLY_NO_POLICY_OR_SCORE_CHANGE");
assert.strictEqual(onset.canonical_choice.behavior_changed, false);
assert.strictEqual(onset.conservation.divergent_legs_reattested, 27);
assert.strictEqual(onset.conservation.total, 226);
assert.strictEqual(onset.conservation.pass, true);
assert.deepStrictEqual(onset.sleeper_offers.become_reachable_under_canonical_runtime_input, []);
assert.strictEqual(onset.sleeper_offers.become_reachable_only_under_rejected_fit_grid_counterfactual.length, 11);

const divergent = rows("ONSET_DIVERGENT_27_REATTESTATION.jsonl.gz");
assert.strictEqual(divergent.length, 27);
assert.ok(divergent.every((row) => row.reattested && row.behavior_changed === false));
assert.strictEqual(new Set(divergent.map((row) => `${row.code}|${row.leg}`)).size, 27);

const sleeper = read("SLEEPER_OFFER_REACHABILITY_RECEIPT.json");
assert.strictEqual(sleeper.rows.length, 11);
assert.strictEqual(sleeper.conservation.canonical_reachable, 0);
assert.strictEqual(sleeper.conservation.rejected_grid_counterfactual_reachable, 11);
assert.ok(sleeper.rows.every((row) => row.canonical_sleep_seconds > 0));

const repair = read("MATMOR_CORSAC_MISSING_GATE_BLOCK_REPAIR.json");
assert.strictEqual(repair.root_cause.policy_evaluation_occurred, false);
assert.strictEqual(repair.repair.behavior_changed, false);
assert.strictEqual(repair.repair.scores_changed, false);
assert.strictEqual(repair.conservation.pass, true);
const repairedRows = rows("MATMOR_CORSAC_REEMITTED_GATE_BLOCK_ROWS.jsonl.gz");
assert.strictEqual(repairedRows.length, 4);
assert.strictEqual(new Set(repairedRows.map((row) => row.leg_identity)).size, 4);
assert.ok(repairedRows.every((row) => row.gate_verdict === "NO_GATE_EVALUATION"));
assert.ok(repairedRows.every((row) => row.blocked_clause === "PRE_MATCH_SPAN_INVALID_LEFT_AFTER_RIGHT"));
assert.ok(repairedRows.every((row) => row.compared_values.w1_left_epoch > row.compared_values.w1_right_epoch));

const control = read("CONTROL_BINDING.json");
assert.strictEqual(control.policy_changed, false);
assert.strictEqual(control.score_changed, false);
assert.strictEqual(control.V52g_iteration_6_executed, false);
const determinism = read("DETERMINISM_RECEIPT.json");
assert.strictEqual(determinism.clean_builds, 2);
assert.strictEqual(determinism.byte_identical, true);

process.stdout.write("test_window1_v52g_provenance_repairs: PASS (31 assertions)\n");
