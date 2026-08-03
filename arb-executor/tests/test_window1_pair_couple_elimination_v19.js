#!/usr/bin/env node
"use strict";

const assert = require("assert");
const { familyOf, narrowBySignableCouples } = require("../analysis/window1_pair_couple_elimination_v19.js");
const h1 = "ATP_CHALL_51_75_INTERIM_PATH_01_ORD_0_1", h2 = "ATP_CHALL_51_75_INTERIM_PATH_02_ORD_2_3";
const l1 = "ATP_CHALL_26_50_INTERIM_PATH_01_ORD_0_1", l2 = "ATP_CHALL_26_50_INTERIM_PATH_02_ORD_2";
assert.strictEqual(familyOf(h1), "ATP_CHALL|INTERIM_PATH_01");
const abstain = narrowBySignableCouples({ group: { couples: [{ high_shape_id: h1, low_shape_id: l1, usable_for_signing: false }] }, highShapes: [h1, h2], lowShapes: [l1, l2] });
assert.strictEqual(abstain.status, "NO_SIGNABLE_PAIR_COUPLE_ABSTAIN_TO_V11");
assert.deepStrictEqual(abstain.high_shapes, [h1, h2]); assert.deepStrictEqual(abstain.low_shapes, [l1, l2]);
const narrowed = narrowBySignableCouples({ group: { couples: [{ pair_couple_id: "C1", high_shape_id: h1, low_shape_id: l1, usable_for_signing: true, authority: "DIRECT_EXACT_COUPLE" }] }, highShapes: [h1, h2], lowShapes: [l1, l2] });
assert.strictEqual(narrowed.status, "SIGNABLE_PAIR_COUPLES_NARROWED_BOTH_LEG_SETS");
assert.deepStrictEqual(narrowed.high_shapes, [h1]); assert.deepStrictEqual(narrowed.low_shapes, [l1]);
assert.deepStrictEqual(narrowed.removed_high_shapes, [h2]); assert.deepStrictEqual(narrowed.removed_low_shapes, [l2]);
console.log("test_window1_pair_couple_elimination_v19: PASS");
