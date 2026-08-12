#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52c_full_post_onset_read_20260812");
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
  assert.equal(new Set(cohort.combined_30.map((row) => row.event_id)).size, 30);

  const clause = json("CLAUSE_2_CORRECTION_RECEIPT.json");
  assert.equal(clause.authorized_change, "CLAUSE_2_EVIDENCE_HORIZON_ONLY");
  assert.equal(clause.clause_1.behavior_changed, false);
  assert.equal(clause.clause_3.behavior_changed, false);
  assert.equal(clause.clause_4.behavior_changed, false);
  assert.equal(clause.clause_2.fixed_replacement_constant, null);
  assert.equal(clause.crediting.status, "FROZEN_TRADES_AS_TRUTH");
  assert.equal(clause.scavenger.enabled, false);

  const assertions = json("FLOW_ASSERTIONS.json");
  assert.equal(assertions.pass, true);
  assert.equal(assertions.REFLEX_POST_zero.observed, 0);
  assert.equal(assertions.every_post_binds_full_post_onset_read_span.violations.length, 0);
  assert.equal(assertions.READ_ABSENT_falls_on_endogenous_thin_tapes.pass, true);

  const before = await scan("V52B_BASELINE_FULL_DECISION_TRACE_30_GAMES.jsonl.gz");
  const after = await scan("V52C_FULL_DECISION_TRACE_30_GAMES.jsonl.gz", (row) => {
    assert.equal(row.scavenger?.enabled, false);
    if (row.read?.full_post_onset_evidence) {
      assert.equal(row.read.full_post_onset_evidence.fixed_horizon_seconds, null);
      assert.equal(row.read.full_post_onset_evidence.replacement_tuning_constant, null);
      assert.equal(String(row.level?.machine_read_evidence?.direction_authority || "").includes("TRAILING_300S"), false);
    }
  });
  assert(before.count > 0 && after.count > 0);
  assert.equal(before.events.size, 30);
  assert.equal(after.events.size, 30);

  const blockRows = await scan("PER_LEG_BLOCK_REASON_HISTOGRAM.jsonl.gz");
  assert.equal(blockRows.count, 60);
  const mar = await scan("ARSMAR_MAR_GATE_TRACE.jsonl.gz", (row) => {
    assert(row.event_id.includes("ARSMAR"));
    assert(row.leg_identity.endsWith("|MAR"));
  });
  assert(mar.count > 0);

  const named = json("NAMED_CHECKS_OBSERVATION_ONLY.json");
  assert.equal(named.checks.MERDRO_formation_era_6c_prints_not_credited, true);
  assert.equal(named.checks.MERDRO_post_onset_judgment_credits_lawful, true);
  assert.equal(named.adjudication, null);

  const status = json("CONSTRUCTION_STATUS.json");
  assert.equal(status.behavioral_edits_beyond_clause_2, false);
  const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json");
  assert.equal(forbidden.full_804_run, false);
  assert.equal(forbidden.live, false);
  assert.equal(forbidden.holdout, false);
  const det = json("DETERMINISM_RECEIPT.json");
  assert.equal(det.clean_builds, 2);
  assert.equal(det.byte_identical, true);

  console.log(JSON.stringify({ tests: 40, pass: true, before_trace_rows: before.count, after_trace_rows: after.count, MAR_trace_rows: mar.count }));
}

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
