"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v53_riser_arming_law.js");

policy.configureArmingLaw("A2_FIRST_TRUE_DIVOT_AND_RESUME");
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
assert.equal(state.riser_arm.armed, true);
assert.equal(state.riser_arm.armed_receipt, "resume-1");

const rising = policy.stance(state);
assert.equal(rising.value, "EARLY_FLOOR_SIDE");
assert.equal(rising.armed, true);
assert.equal(rising.arming_law.id, "A2_FIRST_TRUE_DIVOT_AND_RESUME");
assert.equal(rising.arming_law.proxy_instrument_consumed, false);
assert.equal(rising.arming_law.shape_offset_aim_consumed, false);
assert.equal(rising.arming_law.latchcal_consumed, false);

policy.configureArmingLaw("A0_CONTROL_PROXY_SECOND_VISIT");
const control = policy.emptyLegState(100);
assert.equal(control.riser_arm.armed, true);
assert.equal(control.riser_arm.arm_reason, "FROZEN_V52L_CHAMPION_BYTE_EQUAL");

policy.configureArmingLaw("A1_PROXY_FIRST_VISIT");
const proxy = policy.emptyLegState(100);
policy.observeRiserBook(proxy, { kind: "BOOK", ts: 101, receipt: "proxy-0", bid: 58, ask: 60 }, null, "RISING");
policy.observeRiserBook(proxy, { kind: "BOOK", ts: 102, receipt: "proxy-1", bid: 57, ask: 59 }, { bid: 58, ask: 60 }, "RISING");
assert.equal(proxy.riser_arm.armed, false, "the proxy trough is not a visit until the ask returns");
policy.observeRiserBook(proxy, { kind: "BOOK", ts: 103, receipt: "proxy-resume", bid: 58, ask: 60 }, { bid: 57, ask: 59 }, "RISING");
assert.equal(proxy.riser_arm.armed_receipt, "proxy-resume");
assert.equal(proxy.riser_arm.qualified_proxy_visits.length, 1);

policy.configureArmingLaw("A3_FIRST_SELLER_HIT");
const seller = policy.emptyLegState(100);
policy.observeRiserPrint(seller, { kind: "PRINT", ts: 101, receipt: "seller", trade_id: "seller", price: 58, size: 5, taker_side: "no", taker_book_side: "bid" }, ownBook, siblingBook, "RISING");
assert.equal(seller.riser_arm.armed_receipt, "seller");

policy.configureArmingLaw("A4_BID_PERSISTENCE_300S");
const persist = policy.emptyLegState(100);
policy.observeRiserBook(persist, { kind: "BOOK", ts: 101, receipt: "persist-0", bid: 58, ask: 60 }, null, "RISING");
policy.observeRiserBook(persist, { kind: "BOOK", ts: 400, receipt: "persist-299", bid: 58, ask: 60 }, { bid: 58, ask: 60 }, "RISING");
assert.equal(persist.riser_arm.armed, false);
policy.observeRiserBook(persist, { kind: "BOOK", ts: 401, receipt: "persist-300", bid: 58, ask: 60 }, { bid: 58, ask: 60 }, "RISING");
assert.equal(persist.riser_arm.armed_receipt, "persist-300");

policy.configureArmingLaw("A5_FIRST_TWO_SIDED_BOOK");
const firstBook = policy.emptyLegState(100);
policy.observeRiserBook(firstBook, { kind: "BOOK", ts: 101, receipt: "book-first", bid: 58, ask: 60 }, null, "SETTLED");
assert.equal(firstBook.riser_arm.armed_receipt, "book-first");

policy.configureArmingLaw("A2_FIRST_TRUE_DIVOT_AND_RESUME");

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
