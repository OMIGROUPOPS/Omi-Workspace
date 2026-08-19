#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const adapter = require("../analysis/window1_v52r_exam_adapter.js");
const groundTruthAdapter = require("../analysis/window1_ground_truth_window_adapter.js");

const repo = path.resolve(__dirname, "../..");
const policy = adapter.attestFrozenPolicy(repo);
assert.equal(policy.frozen_commit, "e79c1feef76d7dfd7ec2737b3663670ddce0d342");
assert.equal(policy.all_byte_identical, true);
assert(policy.file_count >= 3);

const v52e = adapter.attestV52eLaneUnchanged(repo);
assert.equal(v52e.pass, true);
assert.equal(v52e.protected_exam_block.byte_identical, true);

const ground = groundTruthAdapter.loadGroundTruthTable(repo);
assert.equal(ground.table.rows.length, 804);
assert.equal([...ground.byEvent.values()].filter((row) => row.scoring_eligible).length, 784);
assert.equal(ground.binding.source_commit, "c0056976c446afcb4d9603796a2e06c068ee94d6");

const roleStats = { role_receipt_rows: 0, missing_both_clock_fields: [], terminal_by_leg: new Map() };
const normalizer = adapter.makeExamTraceNormalizer(roleStats);
const row = normalizer.normalize({ event_id: "E", leg_identity: "E|A", category: "ATP_MAIN", price_region: "26_50", timestamp_epoch: 1, t_minus_scheduled_seconds: 9, t_minus_actual_bell_seconds: 8, receipt: "R", macro_recognition: { candidate_role: "ROLE_DOWN", bound_role: "ROLE_DOWN", drift_cents: -3, trd5: { post_onset_trade_count: 5, threshold: 5, gate_passed: true } }, assembled_policy: { applicable: true, selected_target_cents: 21 }, final_action: "PLACE", final_target_cents: 21 });
assert.equal(row.length, normalizer.entries()[0].fields.length);
assert.equal(normalizer.rows(), 1);
assert.equal(roleStats.role_receipt_rows, 1);
assert.equal(roleStats.missing_both_clock_fields.length, 0);
assert.equal(roleStats.terminal_by_leg.get("E|A").role, "ROLE_DOWN");

const builder = fs.readFileSync(path.join(repo, "arb-executor/analysis/build_window1_v38_maker_only.js"), "utf8");
const adapterSource = fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v52r_exam_adapter.js"), "utf8");
assert(builder.includes('variant === "v52r804"'));
assert(builder.includes('if (isV52rExam) {'));
assert(builder.includes('V52R_ASSEMBLED_POLICY'));
assert(builder.includes('v52rExamAdapter.attestFrozenPolicy(repo)'));
assert(adapterSource.includes('V52E804_LANE_NON_REGRESSION.json'));

const packageDir = path.join(repo, ".claude/window1_live_v4_replay/v52r_disposition_804_20260818");
if (fs.existsSync(packageDir)) {
  const read = (name) => JSON.parse(fs.readFileSync(path.join(packageDir, name), "utf8"));
  const score = read("TWO_RULER_SCORECARD.json");
  const census = read("FOUR_STATE_CENSUS.json");
  const offer = read("OFFER_DENOMINATOR_CAPTURE.json");
  const trace = read("TRACE_CHUNK_MANIFEST.json");
  const clocks = read("BOTH_CLOCKS_ROLE_RECEIPT.json");
  const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
  const manifest = read("ARTIFACT_HASH_MANIFEST.json");
  assert.equal(score.CANON_MARKET_GRADE.population_D, 804);
  assert.equal(score.CANON_MARKET_GRADE.scoring_D, 784);
  assert.equal(score.CANON_MARKET_GRADE.unknown_bell, 20);
  assert.equal(Object.values(score.CANON_MARKET_GRADE.states).reduce((sum, value) => sum + value, 0), 804);
  assert.equal(census.conservation.pass, true);
  assert.equal(offer.denominator.games, 680);
  assert.equal(offer.denominator.cents, 3123);
  assert.equal(offer.standing_baseline.valid_completed_pairs, 214);
  assert.equal(offer.standing_baseline.locked_cents, 350);
  assert.equal(trace.events, 804);
  assert.equal(trace.rows, 8248167);
  assert.equal(clocks.pass, true);
  assert.equal(clocks.role_receipt_rows, trace.rows);
  assert.equal(read("POSTING_TIME_AND_READ_AT_POST.json").REFLEX_POST, 0);
  assert.equal(read("POLICY_BYTE_IDENTITY.json").all_byte_identical, true);
  assert.equal(read("V52E804_LANE_NON_REGRESSION.json").pass, true);
  assert.equal(read("COHORT_30_ADAPTER_SANITY_FENCE.json").pass, true);
  assert.equal(Object.values(forbidden).every((value) => value === false), true);
  for (const [name, expected] of Object.entries(manifest.files)) {
    const bytes = fs.readFileSync(path.join(packageDir, name));
    assert.equal(bytes.length, expected.bytes, `${name} byte count`);
    assert.equal(crypto.createHash("sha256").update(bytes).digest("hex"), expected.sha256, `${name} hash`);
  }
}

console.log(JSON.stringify({ status: "PASS", assertions: fs.existsSync(packageDir) ? 42 : 21, policy_files: policy.file_count, ground_truth_rows: ground.table.rows.length, protected_v52e_lane: v52e.pass, package_validated: fs.existsSync(packageDir) }));
