#!/usr/bin/env node
"use strict";

const assert = require("assert");
const child = require("child_process");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const run = child.spawnSync(
  process.execPath,
  ["arb-executor/analysis/build_nikvrb_decision_tree_reference.js", ".", "--check"],
  { cwd: repo, encoding: "utf8" }
);
assert.strictEqual(run.status, 0, run.stderr || run.stdout);
const summary = JSON.parse(run.stdout);
assert.strictEqual(summary.status, "CHECK_PASS");
assert.strictEqual(summary.raw_clock_rows, 13123);
assert.strictEqual(summary.repeated_nondecisions, 6408);
assert.strictEqual(summary.ask_68_visits, 9);
assert.strictEqual(summary.population_scored, false);

const dir = path.join(
  repo,
  ".claude/window1_live_v4_replay/nikvrb_decision_tree_20260731"
);
const cf = JSON.parse(fs.readFileSync(path.join(dir, "NIKVRB_COUNTERFACTUAL_BRANCHES.json"), "utf8"));
const joint = JSON.parse(fs.readFileSync(path.join(dir, "NIKVRB_JOINT_TREE.json"), "utf8"));
assert.strictEqual(cf.consultations.length, 5);
assert.strictEqual(cf.single_junction.time_et, "2026-07-19T07:13:58-04:00");
assert.strictEqual(cf.single_junction.causal_gap_seconds_before_ask_68_visit_2, 84);
assert.strictEqual(cf.consultations[2].preliminary_target_cents, 69);
assert.strictEqual(cf.consultations[2].actual_ATLAS_target_cents, 67);
assert.strictEqual(cf.ask_68_visit_branches[2].actual, "REST_65__QUIET_STAIRCASE_HOLD");
assert.strictEqual(cf.ask_68_visit_branches[2].orientation_riser_strict_ask_credit_first, "ALREADY_FILLED_AT_69__NO_RESTING_ENTRY");
assert.strictEqual(cf.ask_68_visit_branches[8].orientation_riser_cancel_first, "REST_67__NOT_68_OR_69");
assert.strictEqual(joint.decisive_snapshot.totals.bid, 97);
assert.strictEqual(joint.decisive_snapshot.totals.proposed_resting_pair_orientation_path, 95);
assert.strictEqual(joint.sibling_read_map.find((r) => r.path === "pair_verdict").reads_actual_sibling, false);
assert.strictEqual(joint.sibling_read_map.find((r) => r.path === "orientation_prior").consumed_by_final_signer, false);

const liveBlob = child.execFileSync(
  "git", ["hash-object", "arb-executor/live_v4.py"], { cwd: repo, encoding: "utf8" }
).trim();
assert.strictEqual(liveBlob, "01534495161a9f8f53477794a9e30d4483ebe39f");

process.stdout.write("PASS test_nikvrb_decision_tree_reference (19 assertions; one game; no scorer/live execution)\n");
