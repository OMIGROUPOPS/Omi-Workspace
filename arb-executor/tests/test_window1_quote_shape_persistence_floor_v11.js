"use strict";

const assert = require("assert");
const { evaluatePersistenceFloorOverride } = require("../analysis/window1_quote_shape_persistence_floor_v11.js");

const complete = {
  unanimousLower: true,
  currentAskAtObservedLow: true,
  freshOwnReceipt: true,
  strictlyLaterSamePriceAskReceipt: true,
  askDwellSeconds: 10,
  dwellSeconds: 10,
  topAskSize: 5,
  quantity: 5,
  ownMicroPositionObserved: true,
  inverseSiblingResolved: true,
  stableSigningSupported: true,
  fittedPersistenceExhausted: true,
  fittedOrdinalUnavailable: true,
  zeroFutureQualifiedLowerSupport: true,
};

assert.deepStrictEqual(evaluatePersistenceFloorOverride(complete).verdict, "FLOOR");
for (const key of ["unanimousLower", "currentAskAtObservedLow", "freshOwnReceipt", "strictlyLaterSamePriceAskReceipt", "ownMicroPositionObserved", "inverseSiblingResolved", "stableSigningSupported", "fittedPersistenceExhausted", "fittedOrdinalUnavailable", "zeroFutureQualifiedLowerSupport"]) {
  assert.strictEqual(evaluatePersistenceFloorOverride({ ...complete, [key]: false }).verdict, "LOWER", key);
}
assert.strictEqual(evaluatePersistenceFloorOverride({ ...complete, askDwellSeconds: 9 }).verdict, "LOWER");
assert.strictEqual(evaluatePersistenceFloorOverride({ ...complete, topAskSize: 4 }).verdict, "LOWER");
assert.throws(() => evaluatePersistenceFloorOverride({ ...complete, askDwellSeconds: Infinity }), /finite/);
process.stdout.write("test_window1_quote_shape_persistence_floor_v11: PASS\n");
