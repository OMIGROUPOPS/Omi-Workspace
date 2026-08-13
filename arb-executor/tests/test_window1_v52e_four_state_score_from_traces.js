#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const out = path.join(repo, ".claude/window1_live_v4_replay/v52e_disposition_804_four_state_20260813");
const read = (name) => JSON.parse(fs.readFileSync(path.join(out, name), "utf8"));
const readRows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(out, name))).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);

assert(fs.existsSync(out), "four-state package missing");
const census = read("FOUR_STATE_CENSUS.json");
assert.strictEqual(census.D, 804);
assert.strictEqual(Object.values(census.states).reduce((a, b) => a + b, 0), 804);
assert.strictEqual(census.states.COMPLETE_AT_LOSS, 4);
assert(census.conservation.pass && census.conservation.only_four_states);

const score = read("TWO_RULER_SCORECARD.json");
assert.strictEqual(score.CANON_MARKET_GRADE.completed_pairs, score.CANON_MARKET_GRADE.under_par_pairs + 4);
assert.strictEqual(score.CANON_MARKET_GRADE.frontier.ANY_PRICE, score.CANON_MARKET_GRADE.completed_pairs);
assert.strictEqual(score.CANON_MARKET_GRADE.frontier.LT_100, score.CANON_MARKET_GRADE.under_par_pairs);
assert.strictEqual(score.STRICT_PRINT_CROSS.role, "BUILD_VERIFICATION_RECLASSIFICATION_OF_FROZEN_MARKET_OUTPUT_ONLY");

const autopsy = readRows("COMPLETE_AT_LOSS_LICENSE_AUTOPSY.jsonl.gz");
const breach = autopsy.filter((row) => row.row_type === "SECOND_SIDE_BREACH_EVALUATION");
assert.strictEqual(breach.length, 4);
for (const row of breach) {
  assert.strictEqual(row.combined_entry_cents, 100);
  assert.strictEqual(row.arithmetic.breach_cents, 1);
  assert.strictEqual(row.arithmetic.licensed_second_level_cents, row.arithmetic.pair_cap_required_cents + 1);
  assert.strictEqual(row.missing_check_precise, "V52E_MACHINE_READ_LICENSE_TARGET_MUST_BE_BOUNDED_BY_ACTIVE_PAIR_CAP: target_cents <= 99 - credited_sibling_entry_cents");
  assert.strictEqual(row.repair_status, "FUTURE_ITERATION_NOT_APPLIED");
}

const offer = read("OFFER_DENOMINATOR_CAPTURE.json");
assert.strictEqual(offer.fixed_denominator.OFFERED_POST_ONSET, 612);
assert.deepStrictEqual(offer.fixed_denominator.margin_ladder, { GE_10_CENTS: 90, GE_3_CENTS: 384, GE_5_CENTS: 236, THIN_1_TO_2_CENTS: 228 });
assert(offer.formation_only_and_not_offered_never_folded);

const reflex = read("REFLEX_POST_ATTESTATION.json");
assert.strictEqual(reflex.REFLEX_POST, 0);
assert(reflex.pass);
const palantir = read("PALANTIR_CONSUMPTION_SCALE_RECEIPT.json");
assert(palantir.all_decision_rows_consumed_N2_N4_N5);
assert(palantir.priors_never_gate);
assert(palantir.clean_store_assertion.passed);

const adapter = read("TRACE_SCORE_ADAPTER_RECEIPT.json");
assert.strictEqual(adapter.policy_modules_imported, 0);
assert.strictEqual(adapter.policy_invocations, 0);
assert.strictEqual(adapter.policy_replay, false);
assert.strictEqual(adapter.trace_empty_events, 2);
assert(adapter.pass);
const parity = read("TRACE_RECONSTRUCTION_PARITY_30.json");
assert.strictEqual(parity.events, 30);
assert.strictEqual(parity.legs, 60);
assert.strictEqual(parity.differences.length, 0);
assert(parity.byte_value_parity);

const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
for (const [key, value] of Object.entries(forbidden)) assert.strictEqual(value, false, `${key} must stay false`);

console.log(JSON.stringify({ tests: 35, pass: true, states: census.states, market: score.CANON_MARKET_GRADE, strict: score.STRICT_PRINT_CROSS, autopsy_events: breach.map((row) => row.event_id) }, null, 2));
