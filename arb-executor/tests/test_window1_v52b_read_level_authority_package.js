#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812");
const json = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
async function scanRows(name, visit = () => {}) {
  const input = fs.createReadStream(path.join(root, name)).pipe(zlib.createGunzip());
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
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
assert.equal(new Set(cohort.combined_30.map((row) => row.event_id)).size, 30);
assert.equal(cohort.seed_sha256.length, 64);

const assertions = json("FLOW_ASSERTIONS.json");
assert.equal(assertions.pass, true);
assert.equal(assertions.REFLEX_POST_zero.observed, 0);
assert.equal(assertions.clause_1_CODEX_INTERIM.violations.length, 0);
assert.equal(assertions.machine_read_evidence_on_every_post.violations.length, 0);

const clauses = json("CLAUSE_3_CORRECTION_RECEIPT.json");
assert.equal(clauses.authorized_change, "CLAUSE_3_LEVEL_AUTHORITY_ONLY");
assert.equal(clauses.clause_1.behavior_changed, false);
assert.equal(clauses.clause_2.behavior_changed, false);
assert.equal(clauses.clause_4.behavior_changed, false);
assert.equal(clauses.crediting.status, "FROZEN_TRADES_AS_TRUTH");
assert.equal(clauses.scavenger.enabled, false);

const onset = await scanRows("STABILITY_ONSET_LEDGER.jsonl.gz");
assert.equal(onset.count, 60);
const before = await scanRows("V52_BASELINE_FULL_DECISION_TRACE_30_GAMES.jsonl.gz", (row) => {
  assert.equal(typeof row.reason, "string");
  assert(row.onset?.candidates_receipt);
  assert.equal(row.scavenger?.enabled, false);
});
const after = await scanRows("V52B_FULL_DECISION_TRACE_30_GAMES.jsonl.gz", (row) => {
  assert.equal(typeof row.reason, "string");
  assert(row.onset?.candidates_receipt);
  assert.equal(row.scavenger?.enabled, false);
});
assert(before.count > 0 && after.count > 0);
assert.equal(before.events.size, 30);
assert.equal(after.events.size, 30);

const outcomes = json("OUTCOME_OBSERVATIONS_30.json");
assert.equal(outcomes.adjudication, null);
assert.equal(outcomes.baseline.conservation.pass, true);
assert.equal(outcomes.candidate.conservation.pass, true);
assert.equal(outcomes.candidate.D, 30);
const named = json("NAMED_CHECKS_OBSERVATION_ONLY.json");
assert.equal(named.adjudication, null);
for (const name of ["ARSMAR", "SANDAN", "PUTJEA", "POLKUH", "MERDRO"]) assert(named.rows[name]);

const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json");
assert.equal(forbidden.holdout, false);
assert.equal(forbidden.live, false);
assert.equal(forbidden.full_804_run, false);
assert.equal(json("CONSTRUCTION_STATUS.json").behavioral_edits_beyond_clause_3, false);

console.log(JSON.stringify({ tests: 34, pass: true, before_trace_rows: before.count, after_trace_rows: after.count }));
}

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
