"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const dir = path.join(repo, ".claude/window1_live_v4_replay/v29r3_standing_floor_release_20260805");
const read = (name) => JSON.parse(fs.readFileSync(path.join(dir, name)));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(dir, name))).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);

const score = read("SCORECARD.json"), census = read("STANDING_ARM_CENSUS.json"), arn = read("ARNROM_ARN_REGRESSION_RECEIPT.json"), dispositions = read("ARMED_LEG_DISPOSITION.json"), diff = read("DIFFERENTIAL_RECEIPT.json"), trace = read("DECISION_TRACE_1608.json"), ceiling = read("INDEPENDENT_CEILING_COMPARISON.json"), forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json"), manifest = read("ARTIFACT_HASH_MANIFEST.json"), receipts = rows("MIRROR_ARM_RECEIPTS.jsonl.gz"), events = rows("EVENT_LEDGER.jsonl.gz"), legs = rows("LEG_LEDGER.jsonl.gz");
assert.strictEqual(score.V29R2_floor.joint_objective_pairs, 68);
assert.strictEqual(score.V29R3_score.D, 804);
assert.strictEqual(score.joint_non_regression, true);
assert.strictEqual(events.length, 804);
assert.strictEqual(legs.length, 1608);
assert.strictEqual(trace.rows.length, 1608);
assert.strictEqual(receipts.length, 371);
assert.strictEqual(dispositions.target_legs, 371);
assert.strictEqual(census.R2_defect_population, 128);
assert.strictEqual(census.standing_qualifying_floor_at_or_below_aim_at_arm + census.truly_never_offered_at_or_below_aim, 128);
assert.strictEqual(census.conservation_exact, true);
assert.strictEqual(arn.leg_identity, "KXATPCHALLENGERMATCH-26JUL12ARNROM|ARN");
assert.strictEqual(arn.before.disposition, "NEVER_RELEASED");
assert.strictEqual(arn.before.binding_reason, "OWN_ASK_NEVER_AT_OR_BELOW_AIM");
assert.strictEqual(arn.after.disposition, "RELEASED_AND_FILLED");
assert.strictEqual(arn.after.aim_cents, 56);
assert.strictEqual(arn.after.standing_book.ask, 56);
assert(arn.after.standing_book.ask_dwell_seconds >= 10);
assert.strictEqual(arn.after.release.decision.release_origin, "STANDING_AT_ARM");
assert.strictEqual(diff.changed_leg_streams + diff.unchanged_leg_streams, 1608);
assert.strictEqual(diff.all_other_leg_streams_semantic_hash_equal, true);
assert.strictEqual(ceiling.side_by_side.completion_mirror_FN_class.independent_convertible_ceiling, 29);
assert.strictEqual(ceiling.side_by_side.carried_class.independent_convertible_ceiling, 119);
assert.strictEqual(forbidden.holdout, false);
assert.strictEqual(forbidden.live, false);
for (const receipt of receipts.filter((x) => x.release?.decision?.release_origin === "STANDING_AT_ARM")) {
  assert.strictEqual(receipt.release.action_timestamp_epoch, receipt.arm_clock.timestamp_epoch);
  assert(receipt.release.row.ask <= receipt.arm.aim_cents);
  assert(receipt.release.row.ask_dwell_seconds >= 10);
  assert(receipt.release.row.top_ask_size >= 5 || receipt.release.decision.crossed_or_locked_maximal_urgency);
  assert(receipt.release.row.spread <= 1 || receipt.release.row.bid >= receipt.release.row.ask);
}
for (const [name, expected] of Object.entries(manifest.files)) {
  const bytes = fs.readFileSync(path.join(dir, name));
  assert.strictEqual(crypto.createHash("sha256").update(bytes).digest("hex"), expected.sha256, `artifact hash ${name}`);
  assert.strictEqual(bytes.length, expected.bytes, `artifact bytes ${name}`);
}

process.stdout.write("window1 V29-R3 package tests: PASS (arm census, ARN regression, scoring, differential, and hashes)\n");
