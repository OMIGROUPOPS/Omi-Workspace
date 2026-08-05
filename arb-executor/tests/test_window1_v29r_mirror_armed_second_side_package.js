"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const dir = path.join(repo, ".claude/window1_live_v4_replay/v29r_mirror_armed_second_side_20260804");
const read = (name) => JSON.parse(fs.readFileSync(path.join(dir, name)));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(dir, name))).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);

const score = read("SCORECARD.json");
const frontier = read("FRONTIER.json");
const trace = read("DECISION_TRACE_1608.json");
const diff = read("DIFFERENTIAL_RECEIPT.json");
const cadence = read("CONTINUOUS_EVALUATION_RECEIPT.json");
const ceiling = read("INDEPENDENT_CEILING_COMPARISON.json");
const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
const artifactManifest = read("ARTIFACT_HASH_MANIFEST.json");
const receipts = rows("MIRROR_ARM_RECEIPTS.jsonl.gz");
const events = rows("EVENT_LEDGER.jsonl.gz");
const legs = rows("LEG_LEDGER.jsonl.gz");

assert.strictEqual(score.V28_floor.joint_objective_pairs, 65);
assert.strictEqual(score.V29R_score.D, 804);
assert.strictEqual(events.length, 804);
assert.strictEqual(legs.length, 1608);
assert.strictEqual(trace.rows.length, 1608);
assert.strictEqual(new Set(trace.rows.map((x) => x.leg_identity)).size, 1608);
assert.strictEqual(diff.changed_leg_streams + diff.unchanged_leg_streams, 1608);
assert.strictEqual(diff.all_other_leg_streams_semantic_hash_equal, true);
assert.strictEqual(cadence.polling_interval_seconds, null);
assert.deepStrictEqual(cadence.wall_clock_policy_inputs, []);
assert.strictEqual(ceiling.side_by_side.completion_mirror_FN_class.independent_convertible_ceiling, 29);
assert.strictEqual(ceiling.side_by_side.carried_class.independent_convertible_ceiling, 119);
assert.strictEqual(forbidden.audited_close_as_policy_input, false);
assert.strictEqual(forbidden.wall_clock_pair_input, false);
assert.strictEqual(forbidden.holdout, false);
assert.strictEqual(forbidden.live, false);
assert.strictEqual(frontier.fixed_denominator, 804);
for (const [name, expected] of Object.entries(artifactManifest.files)) {
  const bytes = fs.readFileSync(path.join(dir, name));
  const actual = require("crypto").createHash("sha256").update(bytes).digest("hex");
  assert.strictEqual(actual, expected.sha256, `artifact hash ${name}`);
  assert.strictEqual(bytes.length, expected.bytes, `artifact bytes ${name}`);
}
for (const receipt of receipts) {
  assert.deepStrictEqual(receipt.evaluation.elapsed_time_policy_inputs, []);
  assert.strictEqual(receipt.arm.close_bar, undefined, `close bar leaked into arm ${receipt.armed_leg_identity}`);
  if (receipt.arm.state === "HOLD") assert.strictEqual(receipt.arm.aim_formula, "min(99 - first_fill_cents, own_live_ask_cents_at_arm)");
  if (!receipt.release) continue;
  assert(receipt.release.row.ts > receipt.arm_clock.timestamp_epoch);
  assert(receipt.release.row.ask <= receipt.arm.aim_cents);
  assert(receipt.release.row.ask <= receipt.arm.pair_cap_cents);
  assert(receipt.release.row.spread <= 1);
  assert(receipt.release.row.ask_dwell_seconds >= 10);
  assert(receipt.release.row.top_ask_size >= 5);
}
assert.strictEqual(score.V29R_score.completed_pairs, events.filter((event) => Object.values(event.legs).every((leg) => leg.credited)).length);

process.stdout.write("window1 V29-R package tests: PASS (package conservation plus per-release invariants)\n");
