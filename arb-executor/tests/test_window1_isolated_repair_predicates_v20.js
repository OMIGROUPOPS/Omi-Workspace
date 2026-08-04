"use strict";

const assert = require("assert");
const {
  evaluateAnchorFreshnessA,
  advanceLowerSettlementC,
} = require("../analysis/window1_isolated_repair_predicates_v20.js");

function test(name, fn) {
  try { fn(); process.stdout.write(`PASS ${name}\n`); }
  catch (error) { process.stderr.write(`FAIL ${name}: ${error.stack}\n`); process.exitCode = 1; }
}

test("Fix A re-arms one cent above observed low on a fresh own receipt", () => {
  const result = evaluateAnchorFreshnessA({ currentAsk: 69, observedLow: 68, toleranceCents: 1, freshOwnBookReceipt: true });
  assert.strictEqual(result.placeable, true);
  assert.strictEqual(result.gap_cents, 1);
});

test("Fix A refuses a stale book even inside tolerance", () => {
  const result = evaluateAnchorFreshnessA({ currentAsk: 69, observedLow: 68, toleranceCents: 1, freshOwnBookReceipt: false });
  assert.deepStrictEqual(result, { placeable: false, reason: "NO_FRESH_OWN_BOOK_RECEIPT", gap_cents: 1 });
});

test("Fix A tracks the live ask and refuses outside the re-armed anchor", () => {
  const result = evaluateAnchorFreshnessA({ currentAsk: 70, observedLow: 68, toleranceCents: 1, freshOwnBookReceipt: true });
  assert.strictEqual(result.placeable, false);
  assert.strictEqual(result.reason, "CURRENT_ASK_OUTSIDE_REARMED_OBSERVED_LOW_ANCHOR");
});

test("Fix A rejects fractional values", () => {
  assert.throws(() => evaluateAnchorFreshnessA({ currentAsk: 68.5, observedLow: 68, toleranceCents: 1, freshOwnBookReceipt: true }), /finite integer/);
});

test("Fix C first qualified LOWER receipt establishes an anchor", () => {
  const result = advanceLowerSettlementC({ priorRefusal: null, currentAsk: 40, observedLow: 40, timestamp: 100, receiptId: "r1", dwellSeconds: 10, displayedAskSize: 5, requiredDwellSeconds: 10, requiredQuantity: 5, freshOwnBookReceipt: true, upperLevelsResolved: true });
  assert.strictEqual(result.settled, false);
  assert.strictEqual(result.anchor.receipt_id, "r1");
});

test("Fix C later same-price qualified receipt settles LOWER", () => {
  const result = advanceLowerSettlementC({ priorRefusal: { refused_ask: 40, timestamp: 100, receipt_id: "r1" }, currentAsk: 40, observedLow: 40, timestamp: 101, receiptId: "r2", dwellSeconds: 11, displayedAskSize: 5, requiredDwellSeconds: 10, requiredQuantity: 5, freshOwnBookReceipt: true, upperLevelsResolved: true });
  assert.strictEqual(result.settled, true);
  assert.strictEqual(result.settlement.refusal_receipt_id, "r1");
  assert.strictEqual(result.settlement.settlement_receipt_id, "r2");
});

test("Fix C never settles from the trigger receipt itself", () => {
  const result = advanceLowerSettlementC({ priorRefusal: { refused_ask: 40, timestamp: 100, receipt_id: "r1" }, currentAsk: 40, observedLow: 40, timestamp: 100, receiptId: "r1", dwellSeconds: 100, displayedAskSize: 50, requiredDwellSeconds: 10, requiredQuantity: 5, freshOwnBookReceipt: true, upperLevelsResolved: true });
  assert.strictEqual(result.settled, false);
  assert.strictEqual(result.reason, "LOWER_SETTLEMENT_REQUIRES_LATER_RECEIPT");
});

test("Fix C does not bypass an unresolved upper level", () => {
  const result = advanceLowerSettlementC({ priorRefusal: { refused_ask: 40, timestamp: 100, receipt_id: "r1" }, currentAsk: 40, observedLow: 40, timestamp: 101, receiptId: "r2", dwellSeconds: 100, displayedAskSize: 50, requiredDwellSeconds: 10, requiredQuantity: 5, freshOwnBookReceipt: true, upperLevelsResolved: false });
  assert.strictEqual(result.settled, false);
  assert.strictEqual(result.reason, "LOWER_SETTLEMENT_SUPPORT_NOT_ESTABLISHED");
});

if (process.exitCode) process.exit(process.exitCode);
