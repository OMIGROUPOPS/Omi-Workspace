#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52i_depth_informed_level_selection_20260813");
const json = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
let tests = 0;
const check = (value, message) => { tests += 1; assert(value, message); };
const equal = (actual, expected, message) => { tests += 1; assert.deepStrictEqual(actual, expected, message); };
async function scan(name, visit = () => {}) {
  const lines = readline.createInterface({ input: fs.createReadStream(path.join(root, name)).pipe(zlib.createGunzip()), crlfDelay: Infinity });
  let count = 0; const events = new Set();
  for await (const line of lines) { if (!line) continue; const row = JSON.parse(line); visit(row); count += 1; if (row.event_id) events.add(row.event_id); }
  return { count, events };
}

async function main() {
  check(fs.existsSync(root));
  const cohort = json("COHORT_SELECTION_RECEIPT.json");
  equal(cohort.pins.length, 5); equal(cohort.fresh_25.length, 25); equal(cohort.combined_30.length, 30);
  for (const key of ["prior_V52B_fresh25_overlap_count", "prior_V52C_fresh25_overlap_count", "prior_V52D_fresh25_overlap_count", "prior_V52E_fresh25_overlap_count", "prior_V52F_fresh25_overlap_count", "prior_V52G_fresh25_overlap_count", "prior_V52H_fresh25_overlap_count"]) equal(cohort.exclusions[key], 0);
  const receipt = json("CLAUSE_3_N4_DEPTH_CORRECTION_RECEIPT.json");
  equal(receipt.authorized_change, "CLAUSE_3_N4_DEPTH_INFORMED_LEVEL_SELECTION_ONLY");
  equal(receipt.assets.G3.status_before, "UNVALIDATED-CANDIDATE"); equal(receipt.assets.G3.status_this_run, "UNDER-VALIDATION_V52I");
  equal(receipt.clean_store.canonical_manifest_unchanged, true); equal(receipt.clean_store.exact_under_validation_aliases.length, 2);
  equal(receipt.crediting, undefined);
  const boot = json("DEPTH_UNDER_VALIDATION_BOOT_RECEIPT.json");
  equal(boot.canonical_clean_store_unchanged, true); equal(boot.under_validation_loaded, 2); equal(boot.unvalidated_loaded, 0);
  const assertions = json("FLOW_ASSERTIONS.json");
  equal(assertions.pass, true); equal(assertions.REFLEX_POST_zero.observed, 0);
  equal(assertions.exact_two_depth_candidates_under_validation.pass, true);
  equal(assertions.every_depth_consultation_records_candidate_provenance.pass, true);
  equal(assertions.depth_priors_never_create_or_withdraw_live_authority.pass, true);
  equal(assertions.clauses_4_5_6_and_referee_frozen.pass, true);
  equal(assertions.pins_unharmed.pass, true);
  const differential = json("BEFORE_AFTER_DIFFERENTIAL_RECEIPT.json");
  equal(differential.frozen_clause_differences, 0); equal(differential.every_behavior_change_starts_at_or_after_authorized_clause, true);
  const states = json("FOUR_STATE_OBSERVATION_30.json");
  equal(states.conservation.pass, true); equal(states.candidate.states.COMPLETE_AT_LOSS || 0, 0);
  const outcomes = json("PER_GAME_OUTCOME_TABLE.json");
  equal(outcomes.length, 30); equal(new Set(outcomes.map((row) => row.event_id)).size, 30);
  check(outcomes.every((row) => ["COMPLETE_AT_DELTA", "PARTIAL_FOR_REASON", "NEITHER_FOR_REASON"].includes(row.state)));
  check(outcomes.every((row) => Object.prototype.hasOwnProperty.call(row, "offer_margin_cents")));
  const gaps = json("ENTRY_LATER_FLOOR_COMPARISON.json");
  check(gaps.baseline.credited_legs >= 0); check(gaps.candidate.credited_legs >= 0);
  const exposure = json("NEW_ONE_SIDED_EXPOSURE_RECEIPT.json");
  equal(exposure.V52h_baseline.newly_created_partials, 6); equal(exposure.requested_baseline_count_six, true);
  const consumption = await scan("DEPTH_PRIOR_CONSUMPTION_LEDGER.jsonl.gz", (row) => {
    equal(row.depth_candidates_under_validation.provenance.length, 2);
    check(row.depth_candidates_under_validation.provenance.every((asset) => asset.status === "UNDER-VALIDATION_V52I"));
  });
  check(consumption.count > 0);
  const traces = json("FULL_DECISION_TRACE_MANIFEST.json");
  equal(traces.baseline.events, 30); equal(traces.candidate.events, 30); equal(traces.candidate.chunk_event_count, 2); equal(traces.candidate.chunks.length, 15);
  check(traces.candidate.chunks.every((row) => row.bytes < 100000000));
  const det = json("DETERMINISM_RECEIPT.json"); equal(det.clean_builds, 2); equal(det.byte_identical, true);
  const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json"); equal(forbidden.full_804_run, false); equal(forbidden.live, false); equal(forbidden.holdout, false); equal(forbidden.deployment, false);
  console.log(JSON.stringify({ tests, pass: true, depth_receipts: consumption.count }));
}
main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
