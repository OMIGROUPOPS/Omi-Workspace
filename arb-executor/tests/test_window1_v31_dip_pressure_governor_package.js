"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const dir = path.join(repo, ".claude/window1_live_v4_replay/v31_dip_pressure_governor_20260805");
const read = (name) => JSON.parse(fs.readFileSync(path.join(dir, name)));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(dir, name))).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
const score = read("SCORECARD.json"), fit = read("GOVERNOR_AUTHORITY_FIT.json"), dispositions = read("GOVERNOR_DISPOSITION.json"), risk = read("DEMOTE_RISK_RECEIPT.json"), verdict = read("VERDICT_RECEIPT.json"), arn = read("ARNROM_ROM_REGRESSION_RECEIPT.json"), diff = read("DIFFERENTIAL_RECEIPT.json"), trace = read("DECISION_TRACE_1608.json"), band = read("BAND_SPEC_BINDING.json"), forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json"), determinism = read("DETERMINISM_RECEIPT.json"), manifest = read("ARTIFACT_HASH_MANIFEST.json");
const events = rows("EVENT_LEDGER.jsonl.gz"), legs = rows("LEG_LEDGER.jsonl.gz"), samples = rows("GOVERNOR_SAMPLE_LEDGER.jsonl.gz");
assert.strictEqual(score.R3_floor.joint_objective_pairs, 68);
assert.strictEqual(score.V31_score.D, 804);
assert.strictEqual(events.length, 804);
assert.strictEqual(legs.length, 1608);
assert.strictEqual(trace.rows.length, 1608);
assert.strictEqual(dispositions.legs, 1608);
assert.strictEqual(samples.length, score.R3_floor.acted_legs);
assert.strictEqual(fit.no_current_or_future_outcome_in_decision, true);
assert.strictEqual(band.commit, "e64b0837e04e3ea7dd58fbbba907816b3fdbdcb2");
assert.strictEqual(band.frozen_spec.halflife_seconds, 120);
assert.strictEqual(band.frozen_spec.training_dip_horizon_seconds, 600);
assert.strictEqual(band.frozen_spec.combined_walkforward_auc, .777);
assert.strictEqual(arn.leg_identity, "KXATPCHALLENGERMATCH-26JUL12ARNROM|ROM");
assert.strictEqual(arn.action_matches_named_case, true);
assert.strictEqual(diff.changed_leg_streams + diff.unchanged_leg_streams, 1608);
assert.strictEqual(diff.all_no_authority_and_low_pressure_streams_semantic_hash_equal, true);
assert.strictEqual(risk.net_joint_delta, risk.joint_gained - risk.joint_lost);
assert.strictEqual(verdict.verdict, "REJECTED_JOINT_REGRESSION_DO_NOT_PROMOTE");
assert.strictEqual(verdict.operative_baseline_after_build, "V29R3_STANDING_FLOOR_RELEASE");
assert.strictEqual(forbidden.holdout, false);
assert.strictEqual(forbidden.live, false);
assert.strictEqual(forbidden.wall_clock_policy_input, false);
assert.strictEqual(forbidden.future_floor_policy_input, false);
assert.strictEqual(determinism.clean_builds, 2);
assert.strictEqual(determinism.byte_identical, true);
for (const [name, expected] of Object.entries(manifest.files)) {
  const bytes = fs.readFileSync(path.join(dir, name));
  assert.strictEqual(crypto.createHash("sha256").update(bytes).digest("hex"), expected.sha256, name);
  assert.strictEqual(bytes.length, expected.bytes, name);
}
for (const row of dispositions.rows.filter((candidate) => candidate.disposition !== "UNTOUCHED")) {
  assert.strictEqual(row.authority_earned, true);
  assert.strictEqual(row.pressure_state, "HIGH");
  assert(row.target_cents < row.original_buy_price_cents);
}

process.stdout.write("window1 V31 package tests: PASS (804/1608, authority, risk, ARN, trace, hashes, determinism)\n");
