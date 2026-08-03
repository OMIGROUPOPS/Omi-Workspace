#!/usr/bin/env node
"use strict";

const assert = require("assert");
const { microRepairV14 } = require("../analysis/window1_interim_elimination_v13.js");

const usable = (id, min, max) => ({ shape_id: id, usable_for_signing: true, descent_to_final_reachable_low: { min, max, support_n: 20, counts: { [min]: 20 } } });
const unusable = (id) => ({ shape_id: id, usable_for_signing: false, descent_to_final_reachable_low: { min: null, max: null, support_n: 0, counts: {} } });

let result = microRepairV14([unusable("U")], 0);
assert.strictEqual(result.mode, "RESOLVED_MACRO_CARRY_AFTER_MICRO_ABSTENTION");
assert.strictEqual(result.verdict, "FLOOR");
assert.deepStrictEqual(result.abstaining_unusable_shape_ids, ["U"]);

result = microRepairV14([usable("A", 0, 0), unusable("U")], 0);
assert.strictEqual(result.mode, "USABLE_MICRO_VOTE_WITH_UNUSABLE_ABSTENTIONS");
assert.strictEqual(result.verdict, "FLOOR");
assert.deepStrictEqual(result.usable_shape_ids, ["A"]);

result = microRepairV14([usable("A", 0, 0), usable("B", 2, 3)], 0);
assert.strictEqual(result.verdict, "UNKNOWN");
assert.strictEqual(result.reason, "ORDINAL_HYPOTHESES_STILL_NARROWING");

result = microRepairV14([usable("A", 0, 0), usable("B", 2, 3)], 2);
assert.deepStrictEqual(result.contradicted_shape_ids, ["A"]);
assert.deepStrictEqual(result.usable_shape_ids, ["B"]);
assert.strictEqual(result.verdict, "UNKNOWN");

result = microRepairV14([usable("A", 0, 0), usable("B", 2, 3)], 3);
assert.deepStrictEqual(result.contradicted_shape_ids, ["A"]);
assert.strictEqual(result.verdict, "FLOOR");

result = microRepairV14([usable("A", 0, 0)], 1);
assert.strictEqual(result.mode, "ALL_COHERENT_MICRO_HYPOTHESES_CAUSALLY_CONTRADICTED");
assert.strictEqual(result.verdict, "UNKNOWN");

console.log(JSON.stringify({ status: "PASS", assertions: 16, macro_taxonomy_changed: false, micro_micro_changed: false }));
