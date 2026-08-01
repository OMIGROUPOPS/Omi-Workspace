"use strict";

const assert = require("assert");
const { evaluateDescentVerdict } = require("../analysis/window1_quote_shape_descent_verdict_v5.js");

const fittedThree = { signing_ordinal_after_a_descent_is_observed: 3 };
assert.deepStrictEqual(evaluateDescentVerdict({ baseVerdict: "FLOOR", observedNewLowDescents: 1, fittedDistribution: fittedThree }), {
  verdict: "LOWER", descent_adjustment: "FITTED_DESCENT_ORDINAL_NOT_REACHED", observed_new_low_descents: 1, required_new_low_descents: 3,
});
assert.strictEqual(evaluateDescentVerdict({ baseVerdict: "FLOOR", observedNewLowDescents: 3, fittedDistribution: fittedThree }).verdict, "FLOOR");
assert.strictEqual(evaluateDescentVerdict({ baseVerdict: "LOWER", observedNewLowDescents: 1, fittedDistribution: fittedThree }).verdict, "LOWER");
assert.strictEqual(evaluateDescentVerdict({ baseVerdict: "FLOOR", observedNewLowDescents: 0, fittedDistribution: null }).verdict, "FLOOR");
assert.strictEqual(evaluateDescentVerdict({ baseVerdict: "FLOOR", observedNewLowDescents: 1, fittedDistribution: { signing_ordinal_after_a_descent_is_observed: null } }).verdict, "UNKNOWN");
assert.throws(() => evaluateDescentVerdict({ baseVerdict: "FLOOR", observedNewLowDescents: 1.5, fittedDistribution: fittedThree }), /exact non-negative integer/);
assert.throws(() => evaluateDescentVerdict({ baseVerdict: "FLOOR", observedNewLowDescents: -1, fittedDistribution: fittedThree }), /exact non-negative integer/);

console.log("PASS test_window1_quote_shape_descent_verdict_v5 (7 assertions)");
