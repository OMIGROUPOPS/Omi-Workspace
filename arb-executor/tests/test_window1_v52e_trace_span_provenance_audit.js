#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v52e_trace_span_provenance_audit_20260813");
const json = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
async function rows(name) {
  const output = [];
  const rl = readline.createInterface({ input: fs.createReadStream(path.join(root, name)).pipe(zlib.createGunzip()), crlfDelay: Infinity });
  for await (const line of rl) if (line) output.push(JSON.parse(line));
  return output;
}

async function main() {
  assert(fs.existsSync(root));
  const audit = json("TRACE_SPAN_PROVENANCE_AUDIT.json");
  assert.equal(audit.verdict, "EXPORT_ONLY_TRUNCATION; RUNNER_AND_MATERIALIZED_INPUT_FULL_SPAN");
  assert.equal(audit.runner.games, 30);
  assert.equal(audit.runner.legs, 60);
  assert.equal(audit.runner.runner_full_span, 60);
  assert.equal(audit.runner.runner_truncated, 0);
  assert.equal(audit.runner.export_apparently_truncated, 44);
  assert.equal(audit.runner.credited_legs, 41);
  assert.equal(audit.runner.materialization_shorter_than_usable_raw_source, 0);
  assert.equal(audit.outcome_observation.before_completed_pairs, 17);
  assert.equal(audit.outcome_observation.after_completed_pairs, 17);
  assert.equal(audit.outcome_observation.delta, 0);

  const ledger = await rows("TRACE_SPAN_LEDGER_60.jsonl.gz");
  assert.equal(ledger.length, 60);
  assert.equal(new Set(ledger.map((row) => row.event_id)).size, 30);
  assert.equal(new Set(ledger.map((row) => row.leg_identity)).size, 60);
  assert(ledger.every((row) => row.runner_consumption.classification === "FULL_SPAN"));
  assert(ledger.every((row) => row.runner_consumption.final_receipt_consumed.timestamp_epoch === row.materialized_tape.final_union_receipt.timestamp_epoch));
  assert(ledger.every((row) => row.export.reason !== "UNEXPLAINED_EXPORT_GAP"));
  assert.equal(ledger.filter((row) => row.export.classification === "TRUNCATED_EXPORT_ONLY").length, 44);

  const shevan = json("SHEVAN_STANDING_ATTESTATION.json");
  assert.equal(shevan.verdict, "RESTS_NOT_STANDING_AT_T_PLUS_772_OR_T_PLUS_792; BOTH_LEGS_ALREADY_CREDITED");
  assert.equal(shevan.legs.SHE.target_cents, 34);
  assert.equal(shevan.legs.VAN.target_cents, 58);
  assert(shevan.legs.SHE.fill_receipt?.receipt);
  assert(shevan.legs.VAN.fill_receipt?.receipt);
  assert(shevan.crossings.every((row) => row.SHE_rest_standing === false && row.VAN_rest_standing === false));

  const rootCause = json("ROOT_CAUSE_RECEIPT.json");
  assert.equal(rootCause.disposition, "REGENERATE_RECEIPT_EXPORTS_ONLY; NO_POLICY_RERUN");
  assert.equal(rootCause.code_lines.bounded_timeline_iteration.line, 419);
  assert.equal(rootCause.code_lines.terminal_credit_quiescence.line_start, 426);
  assert.equal(rootCause.code_lines.decision_export_only.line_start, 671);

  const identity = json("POLICY_BYTE_IDENTITY.json");
  assert.equal(identity.all_byte_identical, true);
  assert(Object.values(identity.files).every((row) => row.byte_identical));
  const delta = json("BEFORE_AFTER_OBSERVATION_DELTA.json");
  assert.equal(delta.score_artifacts_changed, 0);
  assert.equal(delta.policy_rerun, false);
  const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json");
  assert.equal(forbidden.full_804_exam, false);
  assert.equal(forbidden.policy_edits, false);
  assert.equal(forbidden.private_input_writes, false);
  const det = json("DETERMINISM_RECEIPT.json");
  assert.equal(det.clean_builds, 2);
  assert.equal(det.byte_identical, true);
  console.log(JSON.stringify({ tests: 38, pass: true, games: 30, legs: 60, runner_full_span: 60, apparent_export_truncations: 44 }));
}

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
