#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const repo = path.resolve(__dirname, "../..");
execFileSync(process.execPath, [path.join(repo, "arb-executor/analysis/build_window1_hur_quiet_faller_walk.js"), repo], { stdio: "pipe", timeout: 120000 });
const receipt = JSON.parse(fs.readFileSync(path.join(repo, ".claude/window1_live_v4_replay/hur_quiet_faller_walk_20260731/HUR_ASK_WALK.json")));

assert.strictEqual(receipt.descriptive_only, true);
assert.strictEqual(receipt.policy_changed, false);
assert.strictEqual(receipt.placement.same_tick_observation.bid, 47);
assert.strictEqual(receipt.placement.same_tick_observation.ask, 48);
assert.strictEqual(receipt.placement.same_tick_observation.spread, 1);
assert.strictEqual(receipt.placement.selected_price_cents, 47);
assert.strictEqual(receipt.placement.arithmetic, "min(bid 47, ask 48-1)=47");
assert.strictEqual(receipt.placement.in_window_prior_book_rows, 0);
assert.strictEqual(receipt.placement.ask_dwell_at_action_seconds, 0);
assert.strictEqual(receipt.placement.true_prints_observed_before_action, 0);
assert.strictEqual(receipt.placement.hold_support_verdict, "NO_OBSERVABLE_SUPPORT_AT_ACTION");
assert.ok(receipt.first_lawful_true_print.ts > receipt.placement.action_ts);
assert.strictEqual(receipt.ask_episode_count, 35);
assert.strictEqual(receipt.zero_dwell_episodes, 4);
assert.strictEqual(receipt.ask_episodes[0].ask_cents, 48);
assert.strictEqual(receipt.ask_episodes[0].contains_action, true);
assert.strictEqual(receipt.ask_episodes[2].ask_cents, 46);
assert.strictEqual(receipt.ask_episodes[2].contains_fill_evidence, true);
assert.strictEqual(Math.min(...receipt.ask_episodes.map((row) => row.ask_cents)), 37);
assert.strictEqual(receipt.conclusion.contemporaneous_hold_evidence, "NONE");

process.stdout.write("PASS test_window1_hur_quiet_faller_walk (20 assertions)\n");
