"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(process.argv[2] || ".");
const dir = path.join(repo, ".claude/window1_live_v4_replay/v51_continuity_of_standing_20260812");
const read = (name) => JSON.parse(fs.readFileSync(path.join(dir, name), "utf8"));
const sha = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const control = read("CONTROL_BINDING.json");
const score = read("ATTRIBUTION_SCORECARD.json");
const census = read("THREE_STATE_CENSUS.json");
const named = read("NAMED_CONTINUITY_CHECKS.json");
const status = read("CONSTRUCTION_STATUS.json");
const manifest = read("ARTIFACT_HASH_MANIFEST.json");

assert.strictEqual(control.base, "47b51fd20f3b0b821d27b63b15a576e36103562e");
assert.strictEqual(control.architecture.time_discipline_only, true);
assert.strictEqual(control.architecture.price_transform, "NONE");
assert.strictEqual(control.architecture.never_creates_a_rest, true);
assert.strictEqual(control.architecture.pair_cap_never_waived, true);
assert.strictEqual(control.architecture.elevated_flow.strict_threshold_lots, 10000);
assert.strictEqual(score.acceptance.baseline_reproduction.pass, true);
assert.strictEqual(score.acceptance.changed_legs_outside_355_target, 0);
assert.strictEqual(score.acceptance.conversions, 1);
assert.strictEqual(score.acceptance.falling_knife_cost_cents.sum, 0);
assert.strictEqual(score.rows[0].MARKET.completed_pairs, 405);
assert.strictEqual(score.rows[1].MARKET.completed_pairs, 406);
assert.strictEqual(score.rows[0].FULL_BOOK.true_book_net_cents, 1778);
assert.strictEqual(score.rows[1].FULL_BOOK.true_book_net_cents, 1779);
assert.strictEqual(score.rows[0].STRICT_PRINT_CROSS.completed_pairs, 330);
assert.strictEqual(score.rows[1].STRICT_PRINT_CROSS.completed_pairs, 330);
assert.strictEqual(Object.values(census.states).reduce((a, b) => a + b, 0), 355);
assert.strictEqual(census.states.CONVERTED_BY_CONTINUITY, 1);
assert.strictEqual(named.rows[0].leg_identity, "KXATPMATCH-26JUL18HEIFEL|HEI");
assert.strictEqual(named.rows[0].candidate_entry_cents, 58);
assert.strictEqual(named.rows[0].traded_floor_cents, 58);
assert.strictEqual(status.status, "PASS_MEASURED_NOT_RATIFIED");
assert.strictEqual(status.operative_candidate, "V49B_47B51FD2");
for (const [name, receipt] of Object.entries(manifest.files)) {
  const file = path.join(dir, name);
  assert.strictEqual(fs.statSync(file).size, receipt.bytes, `${name} byte size`);
  assert.strictEqual(sha(file), receipt.sha256, `${name} hash`);
}

console.log(JSON.stringify({ status: "PASS", assertions: 23, manifest_files: Object.keys(manifest.files).length }));
