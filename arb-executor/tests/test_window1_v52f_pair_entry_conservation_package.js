#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52f_pair_entry_conservation_20260813");
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
  for (const chunk of manifest.chunks) {
    const value = await scan(chunk.name); count += value.count; for (const event of value.events) events.add(event);
  }
  assert.equal(count, manifest.rows); assert.equal(events.size, manifest.events); assert.equal(manifest.conservation_pass, true);
  return { count, events };
}

async function main() {
  assert(fs.existsSync(root));
  const cohort = json("COHORT_SELECTION_RECEIPT.json");
  assert.equal(cohort.pins.length, 5); assert.equal(cohort.fresh_25.length, 25); assert.equal(cohort.combined_30.length, 30); assert.equal(cohort.pre_stated_claim_cases.length, 4);
  for (const key of ["prior_V52B_fresh25_overlap_count", "prior_V52C_fresh25_overlap_count", "prior_V52D_fresh25_overlap_count", "prior_V52E_fresh25_overlap_count"]) assert.equal(cohort.exclusions[key], 0);
  const receipt = json("CLAUSE_5_CORRECTION_RECEIPT.json");
  assert.equal(receipt.authorized_change, "CLAUSE_5_PAIR_ENTRY_CONSERVATION_ONLY"); assert.equal(receipt.settlement_identity.tuned_constant, false); assert.equal(receipt.crediting.status, "FROZEN_TRADES_AS_TRUTH"); assert.equal(receipt.scavenger.enabled, false);
  assert.equal(receipt.clause_1.receipt_differences, 0); assert.equal(receipt.clause_2.receipt_differences, 0); assert.equal(receipt.clause_3.receipt_differences, 0); assert.equal(receipt.clause_4.receipt_differences, 0); assert.equal(receipt.N9.palantir_receipt_differences, 0);
  const claim = json("PRE_STATED_CLAIM_RECEIPT.json");
  assert.equal(claim.named_cases.length, 4); assert.equal(claim.all_four_convert_from_COMPLETE_AT_LOSS, true); assert.equal(claim.zero_new_COMPLETE_AT_LOSS, true); assert.equal(claim.pass, true);
  const states = json("FOUR_STATE_OBSERVATION_30.json");
  assert.equal(states.baseline.rows, 30); assert.equal(states.candidate.rows, 30); assert.equal(states.conservation.pass, true); assert.equal(states.candidate.states.COMPLETE_AT_LOSS || 0, 0);
  const assertions = json("FLOW_ASSERTIONS.json");
  assert.equal(assertions.pass, true); assert.equal(assertions.REFLEX_POST_zero.observed, 0); assert.equal(assertions.clauses_1_through_4_and_scavenger_mechanics_frozen.pass, true); assert.equal(assertions.clause_5_recorded_on_every_rest_mutation.pass, true); assert.equal(assertions.clause_5_strict_integer_identity_on_every_post_credit_rest.pass, true);
  const trace = await scanTrace("candidate"); assert.equal(trace.events.size, 30); assert(trace.count > 0);
  const licenses = await scan("PAIR_ENTRY_CONSERVATION_LICENSE_LEDGER.jsonl.gz", (row) => { if (row.pair_entry_conservation?.applicable && row.final_target_cents !== null) assert(row.final_target_cents + row.pair_entry_conservation.credited_sibling_entry_cents < 100); });
  assert(licenses.count > 0);
  const det = json("DETERMINISM_RECEIPT.json"); assert.equal(det.clean_builds, 2); assert.equal(det.byte_identical, true);
  const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json"); assert.equal(forbidden.full_804_run, false); assert.equal(forbidden.live, false); assert.equal(forbidden.holdout, false);
  console.log(JSON.stringify({ tests: 42, pass: true, trace_rows: trace.count, license_rows: licenses.count }));
}

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
