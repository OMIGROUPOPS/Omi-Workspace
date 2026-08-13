#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52g_joint_target_conservation_20260813");
const json = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
async function scan(name, visit = () => {}) {
  const input = fs.createReadStream(path.join(root, name)).pipe(zlib.createGunzip());
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  let count = 0; const events = new Set();
  for await (const line of lines) { if (!line) continue; const row = JSON.parse(line); visit(row); count += 1; if (row.event_id) events.add(row.event_id); }
  return { count, events };
}
async function scanTrace(side) {
  const manifest = json("FULL_DECISION_TRACE_MANIFEST.json")[side];
  let count = 0; const events = new Set();
  for (const chunk of manifest.chunks) { const value = await scan(chunk.name); count += value.count; for (const event of value.events) events.add(event); }
  assert.equal(count, manifest.rows); assert.equal(events.size, manifest.events); assert.equal(manifest.conservation_pass, true);
  return { count, events };
}

async function main() {
  assert(fs.existsSync(root));
  const cohort = json("COHORT_SELECTION_RECEIPT.json");
  assert.equal(cohort.pins.length, 5); assert.equal(cohort.fresh_25.length, 25); assert.equal(cohort.combined_30.length, 30);
  for (const key of ["prior_V52B_fresh25_overlap_count", "prior_V52C_fresh25_overlap_count", "prior_V52D_fresh25_overlap_count", "prior_V52E_fresh25_overlap_count", "prior_V52F_fresh25_overlap_count"]) assert.equal(cohort.exclusions[key], 0);
  const receipt = json("CLAUSE_6_CORRECTION_RECEIPT.json");
  assert.equal(receipt.authorized_change, "CLAUSE_6_ORDER_FREE_JOINT_TARGET_CONSERVATION_ONLY"); assert.equal(receipt.settlement_identity.tuned_constant, false); assert.equal(receipt.crediting.status, "FROZEN_TRADES_AS_TRUTH"); assert.equal(receipt.scavenger.enabled, false);
  assert.equal(receipt.pair_budget_record.one_per_game, true); assert.equal(receipt.pair_budget_record.goals, "ABSENT_BY_DESIGN"); assert.equal(receipt.pair_budget_record.predictions, "ABSENT_BY_DESIGN");
  const states = json("FOUR_STATE_OBSERVATION_30.json");
  assert.equal(states.conservation.pass, true); assert.equal(states.candidate.states.COMPLETE_AT_LOSS || 0, 0);
  const pairSummary = json("PAIR_BUDGET_RECORD_SUMMARY.json");
  assert.equal(pairSummary.records, 30); assert.equal(pairSummary.exactly_one_record_per_game, true); assert.equal(pairSummary.joint_sum_violations.length, 0); assert.equal(pairSummary.incomplete_revision_chains.length, 0); assert.equal(pairSummary.forbidden_plan_fields.length, 0); assert.equal(pairSummary.pass, true);
  const records = await scan("PAIR_BUDGET_RECORDS.jsonl.gz", (row) => { assert(!("goals" in row)); assert(!("predictions" in row)); assert(!("plan" in row)); for (const revision of row.revisions) { assert.equal(revision.joint_identity_pass, true); if (Number.isInteger(revision.joint_target_sum_cents)) assert(revision.joint_target_sum_cents <= 99); assert(revision.license_fields?.joint_target_conservation); } });
  assert.equal(records.count, 30);
  const series = await scan("PAIR_JOINT_TARGET_TIME_SERIES.jsonl.gz", (row) => { assert(row.revision >= 1); if (Number.isInteger(row.joint_target_sum_cents)) assert(row.joint_target_sum_cents <= 99); });
  assert.equal(series.count, pairSummary.revision_rows);
  const assertions = json("FLOW_ASSERTIONS.json");
  assert.equal(assertions.pass, true); assert.equal(assertions.REFLEX_POST_zero.observed, 0); assert.equal(assertions.clause_6_recorded_on_every_rest_mutation.pass, true); assert.equal(assertions.clause_6_zero_joint_target_sum_above_99.pass, true); assert.equal(assertions.pair_budget_record_one_per_game_complete_revision_chain.pass, true);
  const prior = json("PRIOR_AT_LOSS_REATTESTATION.json");
  assert.equal(prior.named_cases.length, 4); assert.equal(prior.pass, true); assert.equal(prior.zero_new_COMPLETE_AT_LOSS_in_fresh_30, true);
  const pins = json("PIN_REGRESSION_RECEIPT_V52G.json"); assert.equal(pins.pins_unharmed, true); assert.equal(pins.SANDAN_at_or_better, true);
  const trace = await scanTrace("candidate"); assert.equal(trace.events.size, 30); assert(trace.count > 0);
  const det = json("DETERMINISM_RECEIPT.json"); assert.equal(det.clean_builds, 2); assert.equal(det.byte_identical, true);
  const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json"); assert.equal(forbidden.full_804_run, false); assert.equal(forbidden.live, false); assert.equal(forbidden.holdout, false);
  console.log(JSON.stringify({ tests: 39, pass: true, trace_rows: trace.count, pair_revisions: series.count }));
}

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
