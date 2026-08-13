#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52h_remove_pair_lows_precondition_20260813");
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
  assert.equal(cohort.named_reused_observation.code, "26JUL14SMIILA"); assert.equal(cohort.named_reused_observation.prior_iteration, "V52B");
  for (const key of ["prior_V52B_fresh25_overlap_count", "prior_V52C_fresh25_overlap_count", "prior_V52D_fresh25_overlap_count", "prior_V52E_fresh25_overlap_count", "prior_V52F_fresh25_overlap_count", "prior_V52G_fresh25_overlap_count"]) assert.equal(cohort.exclusions[key], 0);
  const receipt = json("CLAUSE_4_MARKET_PROOF_CORRECTION_RECEIPT.json");
  assert.equal(receipt.authorized_change, "CLAUSE_4_MARKET_PROOF_PRECONDITION_REMOVAL_ONLY");
  assert.equal(receipt.burden_transfer.tuned_constant, false); assert.equal(receipt.disagreement_referee.status, "FROZEN_FULLY_INTACT");
  assert.equal(receipt.crediting.status, "FROZEN_TRADES_AS_TRUTH"); assert.equal(receipt.scavenger.enabled, false); assert.equal(receipt.REFLEX_POST.observed, 0);
  const states = json("FOUR_STATE_OBSERVATION_30.json");
  assert.equal(states.conservation.pass, true); assert.equal(states.candidate.states.COMPLETE_AT_LOSS || 0, 0);
  const smiila = json("SMIILA_NAMED_OBSERVATION.json");
  assert.equal(smiila.pair_par_block_converted, true); assert(smiila.baseline_pair_lows_block_receipts > 0); assert.equal(smiila.candidate_pair_lows_block_receipts, 0); assert(smiila.candidate_posts_authorized_with_market_proof_false > 0);
  const exposure = json("NEW_ONE_SIDED_EXPOSURE_RECEIPT.json");
  assert.equal(exposure.rows.length, exposure.newly_created_partials); assert.equal(exposure.duration_seconds.n, exposure.newly_created_partials);
  assert(exposure.rows.every((row) => row.second_side_never_kissed === true && Number.isFinite(row.exposure_to_window_edge_seconds)));
  const assertions = json("FLOW_ASSERTIONS.json");
  assert.equal(assertions.pass, true); assert.equal(assertions.REFLEX_POST_zero.observed, 0);
  assert.equal(assertions.clause_4_market_proof_removal_recorded_on_every_rest_mutation.pass, true);
  assert.equal(assertions.clause_4_disagreement_referee_intact.pass, true); assert.equal(assertions.zero_COMPLETE_AT_LOSS.pass, true);
  assert.equal(assertions.SMIILA_pair_par_block_converts.pass, true); assert.equal(assertions.pins_unharmed.pass, true);
  assert.equal(assertions.clause_6_zero_joint_target_sum_above_99.pass, true); assert.equal(assertions.pair_budget_record_one_per_game_complete_revision_chain.pass, true);
  const pair = json("PAIR_BUDGET_RECORD_SUMMARY.json");
  assert.equal(pair.records, 30); assert.equal(pair.joint_sum_violations.length, 0); assert.equal(pair.pass, true);
  const removal = await scan("MARKET_PROOF_PRECONDITION_REMOVAL_LEDGER.jsonl.gz", (row) => {
    assert.equal(row.clause_4_market_proof_precondition.removed_from_licensing, true);
    assert.equal(row.clause_4_market_proof_precondition.recorded_as_telemetry, true);
  });
  assert(removal.count > 0);
  const differential = json("BEFORE_AFTER_DIFFERENTIAL_RECEIPT.json");
  assert.equal(differential.every_behavior_change_starts_at_or_after_authorized_clause, true); assert.equal(differential.frozen_clause_differences, 0);
  const pins = json("PIN_REGRESSION_RECEIPT_V52H.json"); assert.equal(pins.pins_unharmed, true); assert.equal(pins.comparisons.length, 5);
  const trace = await scanTrace("candidate"); assert.equal(trace.events.size, 30); assert(trace.count > 0);
  const det = json("DETERMINISM_RECEIPT.json"); assert.equal(det.clean_builds, 2); assert.equal(det.byte_identical, true);
  const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json"); assert.equal(forbidden.full_804_run, false); assert.equal(forbidden.live, false); assert.equal(forbidden.holdout, false); assert.equal(forbidden.deployment, false);
  console.log(JSON.stringify({ tests: 42, pass: true, trace_rows: trace.count, removal_rows: removal.count, new_partials: exposure.newly_created_partials }));
}

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
