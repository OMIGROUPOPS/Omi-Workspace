#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const base = path.join(repo, ".claude/window1_live_v4_replay/five_exact_stable_signer_v4_20260801");
const replay = JSON.parse(fs.readFileSync(path.join(base, "FIVE_GAME_STABLE_SIGNER_V4_REPLAY.json")));
const gate = JSON.parse(fs.readFileSync(path.join(base, "FIVE_GAME_HONEST_GATE.json")));

assert.strictEqual(replay.schema_version, "WINDOW1_QUOTE_SHAPE_STABLE_SIGNER_REPLAY_V4");
assert.strictEqual(replay.cold, true);
assert.strictEqual(replay.outcome_knowledge_consumed, false);
assert.strictEqual(gate.event_count, 5);
assert.strictEqual(gate.leg_count, 10);
assert.deepStrictEqual(gate.honest_fill_class_counts, { PROVEN_MAKER: 0, PROVEN_TAKER: 9, UNPROVEN: 1 });
assert.strictEqual(gate.honest_completed_pair_count, 4);
assert.strictEqual(gate.objective_gate_pass_count, 2);
assert.strictEqual(gate.five_game_gate_passed, false);
assert.strictEqual(gate.population_804_run, false);

const leg = (suffix, legId) => replay.events.find((event) => event.event_id.endsWith(suffix)).legs[legId];
assert.strictEqual(leg("HURBIG", "BIG").placement.stable_signing_support.support_type, "TOP_ASK_PRICE_AND_SIZE_PERSISTED");
assert.strictEqual(leg("HURBIG", "HUR").placement.action_ts, leg("HURBIG", "HUR").placement.own_book_ts_at_action);
assert.strictEqual(leg("NIKVRB", "VRB").placement.stable_signing_support.support_type, "ASK_PULSE_EXCEEDED_SPREAD_AND_RETURNED");
assert.strictEqual(leg("LAJVAN", "LAJ").entry_cents, 49);
assert.strictEqual(leg("BRAVED", "VED").entry_cents, 58);
assert.strictEqual(leg("KORJIM", "KOR").placement.stable_signing_support.support_type, "TOP_ASK_PRICE_AND_SIZE_PERSISTED");
assert.strictEqual(leg("KORJIM", "JIM").entry_cents, 32);

console.log("PASS test_window1_five_exact_stable_signer_v4 (17 assertions; 804 gate closed)");
