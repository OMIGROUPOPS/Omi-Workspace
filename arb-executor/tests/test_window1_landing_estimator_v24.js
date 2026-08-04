#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const {
  MIN_TRAINING_N,
  estimateLanding,
  mirrorAim,
  pairCap,
  pathFamily,
  readSideDecision,
} = require("../analysis/window1_landing_estimator_v24_policy.js");
const { releaseFromOwnDecline } = require("../analysis/build_window1_landing_estimator_v24.js");

function test(name, fn) {
  try { fn(); process.stdout.write(`PASS ${name}\n`); }
  catch (error) { process.stderr.write(`FAIL ${name}: ${error.stack}\n`); process.exitCode = 1; }
}

const samples = Array.from({ length: MIN_TRAINING_N }, (_, i) => ({
  event_id: `TRAIN-${i}`,
  category: "ATP_MAIN",
  path_family: "INTERIM_PATH_01",
  close_ts: 100 + i,
  close_minus_live_ask_cents: i % 3,
}));

test("path family comes only from causal shape identifiers", () => {
  assert.equal(pathFamily(["ATP_MAIN_26_50_INTERIM_PATH_01_ORD_0_1"]), "INTERIM_PATH_01");
  assert.equal(pathFamily([]), null);
});

test("walk-forward estimate excludes future labels and emits q25 q50 q75", () => {
  const estimate = estimateLanding([...samples, { ...samples[0], event_id: "FUTURE", close_ts: 9999, close_minus_live_ask_cents: 99 }], {
    event_id: "DECISION", category: "ATP_MAIN", path_family: "INTERIM_PATH_01", decision_ts: 1000, current_ask_cents: 40, identity_unresolved: false,
  });
  assert.equal(estimate.state, "BOUND");
  assert(estimate.max_training_close_ts < 1000);
  assert.deepEqual([estimate.q25, estimate.q50, estimate.q75], [40, 41, 42]);
});

test("339 identity-unresolved class abstains without veto semantics", () => {
  const result = estimateLanding(samples, { event_id: "X", category: "ATP_MAIN", path_family: "INTERIM_PATH_01", decision_ts: 1000, current_ask_cents: 40, identity_unresolved: true });
  assert.equal(result.reason, "LANDING_IDENTITY_UNRESOLVED_339");
});

test("read side places only strictly below q50 central landing", () => {
  assert.equal(readSideDecision({ liveBid: 38, liveAsk: 39, displayedAskSize: 5, estimate: { state: "BOUND", q50: 40 } }).state, "PLACE");
  assert.equal(readSideDecision({ liveBid: 39, liveAsk: 40, displayedAskSize: 5, estimate: { state: "BOUND", q50: 40 } }).state, "ABSTAIN");
});

test("mirror aim is one integer cent below central landing estimate", () => {
  assert.deepEqual(mirrorAim({ state: "BOUND", q50: 55 }), { state: "HOLD", reason: "MIRROR_AIM_ARMED_AWAITING_OWN_DECLINE_ORDINAL", aim_cents: 54 });
});

test("pair cap consumes credited first fill and never chases below live bid", () => {
  assert.equal(pairCap({ aimCents: 60, firstFillCents: 45, liveBid: 53, liveAsk: 55 }).selected_cents, 54);
  assert.equal(pairCap({ aimCents: 50, firstFillCents: 55, liveBid: 45, liveAsk: 46 }).state, "ABSTAIN");
});

test("mirror release requires own strictly later qualified decline and coherent ordinal", () => {
  const shape = { shape_id: "S", usable_for_signing: true, descent_to_final_reachable_low: { min: 1, max: 1 } };
  const rows = [
    { ts: 100, receipt: "a", bid: 50, ask: 52, asks: [[52, 5]] },
    { ts: 101, receipt: "b", bid: 49, ask: 51, asks: [[51, 5]] },
    { ts: 111, receipt: "c", bid: 49, ask: 51, asks: [[51, 5]] },
  ];
  const result = releaseFromOwnDecline(rows, 100, ["S"], new Map([["S", shape]]));
  assert.equal(result.state, "RELEASE");
  assert.equal(result.row.ts, 111);
});

test("policy source contains no elapsed-time or wall-clock release input", () => {
  const source = fs.readFileSync(path.join(__dirname, "../analysis/window1_landing_estimator_v24_policy.js"), "utf8");
  assert(!/elapsed|minutes_since|hours_since|wall_clock/i.test(source));
});

test("frozen package conserves exactly 1608 miss addresses when present", () => {
  const file = path.join(__dirname, "../../.claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804/MISS_LEDGER_1608.jsonl.gz");
  if (!fs.existsSync(file)) return;
  const rows = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);
  assert.equal(rows.length, 1608);
  assert.equal(new Set(rows.map((row) => row.leg_identity)).size, 1608);
  assert(rows.every((row) => row.address === "CAPTURED" || row.address.startsWith("DIED_")));
});

if (!process.exitCode) process.stdout.write("PASS 9/9 V24 focused tests\n");
