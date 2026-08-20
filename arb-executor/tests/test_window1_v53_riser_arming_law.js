"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v53_riser_arming_law.js");

const state = policy.emptyLegState(100);
policy.observeMachineState(state, "RISING", { receipt: "book-0" });
const ownBook = { bid: 59, ask: 61, receipt: "own-book" };
const siblingBook = { bid: 39, ask: 41, receipt: "sibling-book" };
const print = (ts, receipt, price) => policy.observeRiserPrint(state, { kind: "PRINT", ts, receipt, price, size: 5, trade_id: receipt }, ownBook, siblingBook, "RISING");

print(101, "high-1", 60);
print(102, "trough-1", 58);
assert.equal(state.riser_arm.qualified_divots.length, 0, "a trough is not yet a causal divot");
print(103, "resume-1", 60);
assert.equal(state.riser_arm.qualified_divots.length, 1);
assert.equal(state.riser_arm.armed, false);
print(104, "trough-2", 59);
assert.equal(state.riser_arm.armed, false, "second trough still needs its later resume");
print(105, "resume-2", 61);
assert.equal(state.riser_arm.qualified_divots.length, 2);
assert.equal(state.riser_arm.armed, true);
assert.equal(state.riser_arm.armed_receipt, "resume-2");

const rising = policy.stance(state);
assert.equal(rising.value, "EARLY_FLOOR_SIDE");
assert.equal(rising.armed, true);
assert.equal(rising.arming_law.id, "T1_SECOND_TRUE_DIVOT_VISIT");
assert.equal(rising.arming_law.proxy_instrument_consumed, false);
assert.equal(rising.arming_law.shape_offset_aim_consumed, false);
assert.equal(rising.arming_law.latchcal_consumed, false);

policy.observeMachineState(state, "FALLING", { receipt: "book-falling" });
assert.equal(policy.stance(state).value, "LATE_FLOOR_SIDE");
policy.observeMachineState(state, "SETTLED", { receipt: "book-settled" });
assert.equal(policy.stance(state).value, "CLASSIFICATION_ABSENT");

const siblingState = policy.emptyLegState(100);
const view = policy.buildGameView({ A: state, B: siblingState }, { event_id: "TEST", category: "ATP_MAIN", row: { ts: 106, receipt: "eval", kind: "BOOK", bid: 59, ask: 61 }, states: { A: state, B: siblingState }, shape_taxonomy_commit: "taxonomy", shape_taxonomy_path: "path", trd5_commit: "trd5" });
const plan = policy.buildPlan(view, { row: { receipt: "eval" } });
assert.equal(plan.licensed, true);
assert.equal(plan.reason, "L23_ONE_GAME_ONE_JOINT_LICENSE");
assert.deepEqual(Object.keys(plan.stances), ["A", "B"]);
assert.equal(plan.split_authority, "FROZEN_CLAUSE_5_AND_CLAUSE_6_INPUTS_BYTE_EQUAL");

const inputs = { siblingCredited: true, siblingEntryCents: 44, siblingStandingTarget: 43, pairCap: 55 };
assert.deepEqual(policy.conservationInputs(inputs), { sibling_credited: true, sibling_entry_cents: 44, sibling_standing_target_cents: 43, pair_cap_cents: 55 });

process.stdout.write("window1_v53_riser_arming_law: PASS\n");
