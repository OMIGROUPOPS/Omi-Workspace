"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..");
const out = path.join(root, ".claude/window1_live_v4_replay/v34_prebell_close_regrade_20260805");
const read = (name) => JSON.parse(fs.readFileSync(path.join(out, name), "utf8"));
const score = read("SCORECARD_TWO_COLUMN.json"), binding = read("PREBELL_CLOSE_AND_OFFER_BINDING.json"), identity = read("FROZEN_FILL_IDENTITY_RECEIPT.json"), forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json"), determinism = read("DETERMINISM_RECEIPT.json"), fence = read("CLAIM_FENCE.json");

assert.strictEqual(score.grading_only, true);
assert.strictEqual(score.fill_source, "b430bcfff51f89c9466e77b798d4ac5d9fff15ea");
assert.strictEqual(score.R3_joint_floor, 68);
assert.strictEqual(binding.close.commit, "50ce0f4940c461cf0b6fa1b79000d96b335cd601");
assert.strictEqual(binding.close.rows, 1608);
assert.strictEqual(binding.close.available, 1557);
assert.strictEqual(binding.close.unavailable, 51);
assert.deepStrictEqual(binding.recut_offer.expected_summary, { LE_93: 59, LE_95: 104, LE_97: 217, LT_100: 390 });
assert.strictEqual(binding.recut_offer.mismatches, 0);
assert.strictEqual(identity.policy_replay_invocations, 0);
assert.strictEqual(identity.action_changes, 0);
assert.strictEqual(identity.fill_changes, 0);
assert.strictEqual(score.STRICT_LAW.aggregate.D, 804);
assert.strictEqual(score.CENSUS_PRICED.aggregate.D, 804);
assert.strictEqual(fence.fill_admissibility_not_revisited, true);
assert.strictEqual(forbidden.private_input_reads, 0);
assert.strictEqual(forbidden.live_accesses, 0);
assert.strictEqual(determinism.builds, 2);
assert.strictEqual(determinism.byte_identical, true);

console.log("PASS test_window1_v34_prebell_close_regrade");
