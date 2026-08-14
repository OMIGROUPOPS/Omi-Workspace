#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const adapter = require("../analysis/window1_ground_truth_window_adapter.js");

const repo = path.resolve(__dirname, "../..");
const pkg = path.join(repo, ".claude/window1_live_v4_replay/v52h_ground_truth_grading_binding_20260814");
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const read = (name) => JSON.parse(fs.readFileSync(path.join(pkg, name), "utf8"));

const ground = adapter.loadGroundTruthTable(repo);
assert.strictEqual(ground.binding.source_commit, adapter.GROUND_TRUTH_COMMIT);
assert.strictEqual(ground.binding.sha256, adapter.GROUND_TRUTH_SHA256);
assert.strictEqual(ground.byEvent.size, 804);
assert.strictEqual([...ground.byEvent.values()].filter((row) => !row.scoring_eligible).length, 20);

const decision = read("DECISION_STREAM_REEMISSION_MANIFEST.json");
assert.strictEqual(decision.pass, true);
assert.strictEqual(decision.input_events, 30);
assert.strictEqual(decision.decision_stream_differences, 0);
assert.strictEqual(decision.receipt_key_differences, 0);
assert.strictEqual(decision.policy_field_differences, 0);
assert.strictEqual(decision.reemitted_rows, decision.frozen_rows);

const binding = read("WINDOW_SOURCE_BINDING.json");
assert.strictEqual(binding.binding.sha256, adapter.GROUND_TRUTH_SHA256);
assert.strictEqual(binding.uses.decisions, "FROZEN_HISTORICAL_WINDOWS_UNTOUCHED");
assert.strictEqual(binding.scoring_D, 29);
assert.strictEqual(binding.unknown_bell_event_ids.length, 1);

const four = read("BOUND_FOUR_STATE_OBSERVATION_30.json");
assert.strictEqual(four.D, 29);
assert.strictEqual(four.UNKNOWN_BELL, 1);
assert.strictEqual(Object.values(four.states).reduce((a, b) => a + b, 0), 30);
assert.strictEqual(four.conservation.pass, true);

const deterministic = read("DETERMINISM_RECEIPT.json");
assert.strictEqual(deterministic.clean_builds, 2);
assert.strictEqual(deterministic.byte_identical, true);
assert.strictEqual(deterministic.policy_replay_invocations, 0);

const manifest = read("ARTIFACT_HASH_MANIFEST.json");
for (const [name, receipt] of Object.entries(manifest.files)) {
  assert.strictEqual(hash(path.join(pkg, name)), receipt.sha256, name);
  assert.strictEqual(fs.statSync(path.join(pkg, name)).size, receipt.bytes, name);
}

process.stdout.write(`${JSON.stringify({ tests: 27 + Object.keys(manifest.files).length * 2, failures: 0, decision_stream_differences: 0, UNKNOWN_BELL: 1 })}\n`);
