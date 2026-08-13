#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52d_disagreement_referee_20260812");
const json = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
async function scan(name, visit = () => {}) {
  const lines = readline.createInterface({ input: fs.createReadStream(path.join(root, name)).pipe(zlib.createGunzip()), crlfDelay: Infinity });
  let count = 0;
  const events = new Set();
  for await (const line of lines) {
    if (!line) continue;
    const row = JSON.parse(line);
    visit(row);
    count += 1;
    if (row.event_id) events.add(row.event_id);
  }
  return { count, events };
}

async function main() {
  assert(fs.existsSync(root));
  const cohort = json("COHORT_SELECTION_RECEIPT.json");
  assert.equal(cohort.pins.length, 5);
  assert.equal(cohort.fresh_25.length, 25);
  assert.equal(cohort.combined_30.length, 30);
  assert.equal(cohort.exclusions.prior_V52b_fresh25_overlap_count, 0);
  assert.equal(cohort.exclusions.prior_V52c_fresh25_overlap_count, 0);
  assert.equal(new Set(cohort.combined_30.map((row) => row.event_id)).size, 30);

  const clause = json("CLAUSE_4_CORRECTION_RECEIPT.json");
  assert.equal(clause.authorized_change, "CLAUSE_4_DISAGREEMENT_REFEREE_ONLY");
  assert.equal(clause.clause_1.behavior_changed, false);
  assert.equal(clause.clause_2.behavior_changed, false);
  assert.equal(clause.clause_3.behavior_changed, false);
  assert.equal(clause.clause_4.pair_under_par_check_changed, false);
  assert.equal(clause.clause_4.palantir_priors_consumed, false);
  assert.equal(clause.clause_4.N9_post_bell_consumed, false);
  assert.equal(clause.crediting.status, "FROZEN_TRADES_AS_TRUTH");
  assert.equal(clause.scavenger.enabled, false);

  const assertions = json("FLOW_ASSERTIONS.json");
  assert.equal(assertions.pass, true);
  assert.equal(assertions.REFLEX_POST_zero.observed, 0);
  assert.equal(assertions.clauses_1_2_3_and_scavenger_frozen.violations.length, 0);
  assert.equal(assertions.referee_records_every_firing_disagreement.violations.length, 0);
  assert.equal(assertions.referee_uses_no_palantir_N9_or_historical_inputs.violations.length, 0);
  assert.equal(assertions.adjudications_occur_and_order_masked_burden_falls.pass, true);

  const summary = json("DISAGREEMENT_REFEREE_SUMMARY.json");
  assert(summary.recorded_adjudications > 0);
  assert(summary.resolved_strictly_stronger > 0);
  assert(summary.candidate_order_masked_disagreement_blocks < summary.baseline_order_masked_disagreement_blocks);
  assert(summary.ARSMAR.candidate_recorded_adjudications > 0);
  const discrepancy = json("PRE_STATED_CLAIM_DISCREPANCY_RECEIPT.json");
  assert.equal(discrepancy.operator_stated_ARSMAR_blocks, 127);
  assert.equal(discrepancy.frozen_V52c_actual_row_grain_blocks, summary.ARSMAR.baseline_order_masked_blocks);

  const before = await scan("V52C_BASELINE_FULL_DECISION_TRACE_30_GAMES.jsonl.gz");
  const after = await scan("V52D_FULL_DECISION_TRACE_30_GAMES.jsonl.gz", (row) => assert.equal(row.scavenger?.enabled, false));
  assert.equal(before.events.size, 30);
  assert.equal(after.events.size, 30);
  const adjudications = await scan("DISAGREEMENT_ADJUDICATION_LEDGER.jsonl.gz", (row) => {
    const receipt = row.coherence.disagreement_adjudication;
    assert.equal(receipt.firing, true);
    assert.equal(receipt.palantir_priors_consumed, false);
    assert.equal(receipt.N9_post_bell_consumed, false);
    assert.equal(receipt.historical_inputs_consumed, false);
  });
  assert.equal(adjudications.count, summary.recorded_adjudications);
  const ars = await scan("ARSMAR_DISAGREEMENT_ADJUDICATION_TRACE.jsonl.gz", (row) => assert(row.event_id.includes("ARSMAR")));
  assert(ars.count > 0);

  const status = json("CONSTRUCTION_STATUS.json");
  assert.equal(status.behavioral_edits_beyond_clause_4, false);
  const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json");
  assert.equal(forbidden.full_804_run, false);
  assert.equal(forbidden.live, false);
  assert.equal(forbidden.holdout, false);
  const det = json("DETERMINISM_RECEIPT.json");
  assert.equal(det.clean_builds, 2);
  assert.equal(det.byte_identical, true);

  console.log(JSON.stringify({ tests: 41, pass: true, before_trace_rows: before.count, after_trace_rows: after.count, adjudication_rows: adjudications.count, ARSMAR_rows: ars.count }));
}

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
