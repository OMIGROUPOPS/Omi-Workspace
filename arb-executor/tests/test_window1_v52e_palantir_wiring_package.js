#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52e_palantir_wiring_20260812");
const json = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
async function scan(name, visit = () => {}) {
  const lines = readline.createInterface({ input: fs.createReadStream(path.join(root, name)).pipe(zlib.createGunzip()), crlfDelay: Infinity });
  let count = 0; const events = new Set();
  for await (const line of lines) { if (!line) continue; const row = JSON.parse(line); visit(row); count += 1; if (row.event_id) events.add(row.event_id); }
  return { count, events };
}

async function main() {
  assert(fs.existsSync(root));
  const cohort = json("COHORT_SELECTION_RECEIPT.json");
  assert.equal(cohort.pins.length, 5); assert.equal(cohort.fresh_25.length, 25); assert.equal(cohort.combined_30.length, 30);
  assert.equal(cohort.exclusions.prior_V52B_fresh25_overlap_count, 0); assert.equal(cohort.exclusions.prior_V52C_fresh25_overlap_count, 0); assert.equal(cohort.exclusions.prior_V52D_fresh25_overlap_count, 0);
  const boot = json("CLEAN_STORE_BOOT_ASSERTION.json");
  assert.equal(boot.passed, true); assert.equal(boot.unvalidated_loaded, 0); assert.equal(boot.quarantined_loaded, 0); assert.equal(boot.superseded_loaded, 0); assert.equal(boot.fallback_loads, 0);
  const reuse = json("STEP0_REUSE_INVENTORY.json");
  assert.equal(reuse.parallel_loader_built, false); assert(reuse.components.every((row) => ["REUSED", "RE-POINTED", "RETIRED-WITH-REASON"].includes(row.disposition)));
  const wiring = json("N9_WIRING_RECEIPT.json");
  assert.equal(wiring.authorized_change, "N9_CLEAN_PALANTIR_WIRING_ONLY"); assert.equal(wiring.crediting.status, "FROZEN_TRADES_AS_TRUTH"); assert.equal(wiring.scavenger.enabled, false);
  const assertions = json("FLOW_ASSERTIONS.json");
  assert.equal(assertions.pass, true); assert.equal(assertions.REFLEX_POST_zero.observed, 0); assert.equal(assertions.CLEAN_store_boot_assertion.pass, true); assert.equal(assertions.consumption_receipts_are_behavioral_not_decorative.pass, true); assert.equal(assertions.N4_grid_covered_abstentions_fall.pass, true); assert.equal(assertions.pins_unharmed.pass, true);
  const summary = json("PALANTIR_CONSUMPTION_SUMMARY.json");
  assert.equal(summary.all_receipts_continuous, true); assert.equal(summary.priors_gate, false); assert(summary.consumption_receipts > 0); assert(summary.N4_prior_informed_live_evidence_rescues + summary.N5_frozen_tie_resolutions > 0);
  const before = await scan("V52D_BASELINE_FULL_DECISION_TRACE_30_GAMES.jsonl.gz");
  const after = await scan("V52E_FULL_DECISION_TRACE_30_GAMES.jsonl.gz", (row) => { assert.equal(row.palantir.continuous_at_decision_time, true); assert.equal(row.palantir.priors_gate, false); });
  const consumption = await scan("PALANTIR_CONSUMPTION_LEDGER.jsonl.gz", (row) => assert(row.palantir.N2 && row.palantir.N4 && row.palantir.N5));
  assert.equal(before.events.size, 30); assert.equal(after.events.size, 30); assert.equal(consumption.count, after.count);
  const det = json("DETERMINISM_RECEIPT.json"); assert.equal(det.clean_builds, 2); assert.equal(det.byte_identical, true);
  const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json"); assert.equal(forbidden.full_804_run, false); assert.equal(forbidden.live, false); assert.equal(forbidden.holdout, false);
  const status = json("CONSTRUCTION_STATUS.json"); assert.equal(status.behavioral_edits_beyond_N9_clean_prior_wiring, false);
  console.log(JSON.stringify({ tests: 39, pass: true, baseline_trace_rows: before.count, candidate_trace_rows: after.count, consumption_rows: consumption.count }));
}

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
