"use strict";

const assert = require("assert");
const { evaluateCausalDescentOrdinalVerdict } = require("../analysis/window1_quote_shape_descent_verdict_v10.js");

const fitted = { signing_ordinal_after_a_descent_is_observed: 3 };
assert.deepStrictEqual(evaluateCausalDescentOrdinalVerdict({ baseVerdict: "LOWER", observedNewLowDescents: 0, fittedDistribution: fitted }).verdict, "LOWER");
assert.deepStrictEqual(evaluateCausalDescentOrdinalVerdict({ baseVerdict: "FLOOR", observedNewLowDescents: 2, fittedDistribution: fitted }).verdict, "LOWER");
const lagRepair = evaluateCausalDescentOrdinalVerdict({ baseVerdict: "LOWER", observedNewLowDescents: 3, fittedDistribution: fitted });
assert.strictEqual(lagRepair.verdict, "FLOOR");
assert.strictEqual(lagRepair.descent_adjustment, "FITTED_DESCENT_ORDINAL_OVERRIDES_LAGGING_TEMPORAL_MEDOID");
assert.strictEqual(evaluateCausalDescentOrdinalVerdict({ baseVerdict: "UNKNOWN", observedNewLowDescents: 4, fittedDistribution: fitted }).verdict, "FLOOR");
assert.strictEqual(evaluateCausalDescentOrdinalVerdict({ baseVerdict: "FLOOR", observedNewLowDescents: 1, fittedDistribution: null }).verdict, "UNKNOWN");
assert.throws(() => evaluateCausalDescentOrdinalVerdict({ baseVerdict: "LOWER", observedNewLowDescents: 1.5, fittedDistribution: fitted }), /exact non-negative integer/);

process.stdout.write(`${JSON.stringify({ status: "PASS", assertions: 7 })}\n`);
