#!/usr/bin/env node
"use strict";
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const repo = path.resolve(__dirname, "../..");
const gate = JSON.parse(fs.readFileSync(path.join(repo, ".claude/window1_live_v4_replay/entry_honesty_dependency_20260801/DECISION_GATE_RECEIPT.json")));
assert.strictEqual(gate.score_free, true);
assert.strictEqual(gate.dependencies.honest_fill_model, "LANDED");
assert.strictEqual(gate.dependencies.fee_aware_take_rule, "BLOCKED_EXPECTED_CLOSE_NOT_BOUND");
assert.strictEqual(gate.five_game_replay_run, false);
assert.strictEqual(gate.population_804_policy_run, false);
assert.strictEqual(gate.scorer_invocations, 0);
assert.strictEqual(gate.performance_metrics, null);
assert(!fs.existsSync(path.join(repo, ".claude/window1_live_v4_replay/entry_honesty_dependency_20260801/results")));
process.stdout.write("window1 entry-honesty dependency gate: 8 assertions passed\n");
