#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const dir = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_elimination_big_walk_20260731");
const diagnosis = JSON.parse(fs.readFileSync(path.join(dir, "BIG_ELIMINATION_DIAGNOSIS.json")));
const csv = fs.readFileSync(path.join(dir, "BIG_EVERY_JOINT_TICK_ELIMINATION_WALK.csv"), "utf8").trimEnd().split(/\r?\n/);
const headers = csv.shift().split(",");
const rows = csv.map((line) => Object.fromEntries(line.split(",").map((value, index) => [headers[index], value])));

assert.strictEqual(diagnosis.diagnostic_only, true);
assert.strictEqual(diagnosis.gate_changed, false);
assert.strictEqual(diagnosis.event_id, "KXATPCHALLENGERMATCH-26JUL19HURBIG");
assert.strictEqual(diagnosis.leg_id, "BIG");
assert.strictEqual(diagnosis.joint_ticks, 3645);
assert.strictEqual(rows.length, diagnosis.joint_ticks);
assert.strictEqual(diagnosis.material_state_changes_match_frozen_replay, true);
assert.deepStrictEqual(diagnosis.self_check_mismatches, []);
assert.strictEqual(diagnosis.first_observed_floor.ask, 55);
assert.strictEqual(diagnosis.first_observed_floor.dwell_seconds, 0);
assert.strictEqual(diagnosis.first_observed_floor.reason, "NO_PRIOR_IN_WINDOW_BOOK");
assert.strictEqual(diagnosis.first_floor_consensus.ask, 55);
assert.strictEqual(diagnosis.first_floor_consensus.dwell_seconds, 330);
assert.strictEqual(diagnosis.first_floor_consensus.survivors, "ATP_CHALL_51_75_UP_CONTINUATION:FLOOR");
assert.strictEqual(diagnosis.first_floor_consensus.reason, "FLOOR_CONSENSUS_BUT_OWN_MICRO_POSITION_UNOBSERVED");
assert.strictEqual(diagnosis.first_sibling_direction_observed.big_ask, 55);
assert.strictEqual(diagnosis.first_sibling_direction_observed.big_ask_dwell_seconds, 13459);
assert.strictEqual(diagnosis.first_sibling_direction_observed.hur_direction, "DOWN");
assert.strictEqual(diagnosis.first_sibling_direction_observed.pair_tuple_count, 1);
assert.strictEqual(diagnosis.first_sibling_direction_observed.reason, "FLOOR_CONSENSUS_BUT_OWN_MICRO_POSITION_UNOBSERVED");
assert.strictEqual(diagnosis.ask55_joint_ticks, 417);
assert.strictEqual(diagnosis.ask55_max_continuous_dwell_seconds, 14807);
assert.strictEqual(diagnosis.ask55_last_observed.ask, 55);
assert.strictEqual(diagnosis.ask55_last_observed.dwell_seconds, 14807);
assert.strictEqual(diagnosis.first_own_later_ask_transition.ask, 57);
assert.strictEqual(diagnosis.first_own_later_ask_transition.reason, "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW");
assert.strictEqual(diagnosis.states.PLACE, undefined);
assert.strictEqual(diagnosis.states.INSUFFICIENT_EVIDENCE, 3484);
assert.strictEqual(diagnosis.states.HOLD, 161);
assert.strictEqual(diagnosis.conclusion, "SINGLE_VISIT_FLOOR_STRUCTURAL_WEAKNESS");
assert.strictEqual(rows.every((row) => row.big_bid !== "" && row.big_ask !== "" && row.big_spread !== "" && row.big_ask_dwell_seconds !== "" && row.big_surviving_shapes !== "" && row.big_reason !== ""), true);
assert.strictEqual(rows.some((row) => row.big_state === "PLACE"), false);

process.stdout.write("PASS test_hurbig_big_elimination_tick_walk_v1 (32 assertions; diagnostic only; no gate change)\n");
