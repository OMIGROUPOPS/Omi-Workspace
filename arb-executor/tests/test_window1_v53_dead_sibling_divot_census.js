"use strict";

const assert = require("assert");
const {
  enumerateTrueDivots,
  classifyDeadSibling,
  orderAfterDecision,
} = require("../analysis/window1_v53_dead_sibling_divot_census.js");

const book = (timestamp_epoch, receipt, bid_cents, ask_cents) => ({ timestamp_epoch, receipt, bid_cents, ask_cents, last_traded_cents: bid_cents, spread_cents: ask_cents - bid_cents });
const trace = (timestamp_epoch, receipt, state, order, action = "HOLD_REST", target = null) => ({ timestamp_epoch, receipt, read: { state, quote_path_state: state, pressure_state: state }, order_before_cents: order, final_action: action, final_target_cents: target, reason: "SYNTHETIC", joint_license: { complete: true } });
const print = (timestamp_epoch, receipt, price_cents) => ({ timestamp_epoch, receipt, trade_id: receipt, price_cents, size: 5, taker_side: "no", taker_book_side: "bid" });

assert.strictEqual(orderAfterDecision(trace(1, "a", "RISING", 39, "REPRICE_REST", 40)), 40);
assert.strictEqual(orderAfterDecision(trace(1, "a", "RISING", 39, "CANCEL_REST", null)), null);

const common = {
  ownBooks: [book(1, "own-1", 40, 41), book(3, "own-3", 40, 41), book(5, "own-5", 40, 41)],
  siblingBooks: [book(1, "sib-1", 58, 59), book(3, "sib-3", 58, 59), book(5, "sib-5", 58, 59)],
  decisionRows: [trace(1, "d-1", "RISING", 38), trace(3, "d-3", "RISING", 38), trace(5, "d-5", "RISING", 38)],
  siblingCredit: { entry_cents: 58, fill_timestamp_epoch: 1.5, fill_class: "SYNTHETIC" },
};
const convertible = enumerateTrueDivots({ ...common, prints: [print(1.2, "high", 45), print(2, "trough", 40), print(4, "resume", 42), print(6, "later", 40)] });
assert.strictEqual(convertible.length, 1);
assert.strictEqual(convertible[0].trough.receipt, "trough");
assert.strictEqual(convertible[0].recognition.receipt, "resume");
assert.strictEqual(convertible[0].slide_counterfactual.would_slide_to_best_bid_trade, true);
assert.strictEqual(classifyDeadSibling(convertible), "DIVOTS_EXISTED_REST_ELSEWHERE");

const noDivot = enumerateTrueDivots({ ...common, prints: [print(1.2, "only", 45), print(2, "up", 46)] });
assert.strictEqual(classifyDeadSibling(noDivot), "ZERO_TRUE_DIVOTS");

const capBlocked = enumerateTrueDivots({
  ...common,
  siblingCredit: { entry_cents: 62, fill_timestamp_epoch: 1.5, fill_class: "SYNTHETIC" },
  prints: [print(1.2, "high", 45), print(2, "trough", 40), print(4, "resume", 42), print(6, "later", 40)],
});
assert.strictEqual(capBlocked.length, 1);
assert.strictEqual(capBlocked[0].slide_counterfactual.cap_lawful, false);
assert.strictEqual(classifyDeadSibling(capBlocked), "DIVOTS_EXISTED_SLIDE_WOULD_NOT_TRADE");

console.log("window1_v53_dead_sibling_divot_census: PASS");
