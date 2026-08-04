"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { pairCapDecision, findStrictlyLaterReach } = require("../analysis/window1_pair_cap_v23_policy.js");

function test(name, fn) {
  try { fn(); process.stdout.write(`PASS ${name}\n`); }
  catch (error) { process.stderr.write(`FAIL ${name}: ${error.stack}\n`); process.exitCode = 1; }
}

test("non-binding cap preserves the A price", () => {
  assert.deepStrictEqual(pairCapDecision({ firstFillCents: 40, originalSecondBidCents: 58, liveBidCents: 57, liveAskCents: 58 }), {
    state: "UNCHANGED", reason: "ORIGINAL_LEG2_BID_ALREADY_STRICTLY_UNDER_PAR", cap_cents: 59, selected_bid_cents: 58,
  });
});

test("100-cent A pair becomes a maker bid at the live bid", () => {
  assert.deepStrictEqual(pairCapDecision({ firstFillCents: 40, originalSecondBidCents: 60, liveBidCents: 59, liveAskCents: 60 }), {
    state: "PLACE", reason: "PAIR_CAP_AT_OR_ABOVE_LIVE_BID_MAKER_RESTING_NO_CHASE", cap_cents: 59, selected_bid_cents: 59,
  });
});

test("cap below the current bid abstains instead of chasing", () => {
  assert.deepStrictEqual(pairCapDecision({ firstFillCents: 40, originalSecondBidCents: 61, liveBidCents: 60, liveAskCents: 61 }), {
    state: "ABSTAIN", reason: "PAIR_CAP_BELOW_CURRENT_LIVE_BID_UNREACHABLE_WITHOUT_CHASING", cap_cents: 59, selected_bid_cents: null,
  });
});

test("same receipt cannot credit the new capped bid", () => {
  const rows = [
    { ts: 100, receipt: "r1", ask: 59, asks: [[59, 5]] },
    { ts: 111, receipt: "r2", ask: 59, asks: [[59, 5]] },
  ];
  assert.strictEqual(findStrictlyLaterReach(rows, { actionTs: 100, targetCents: 59, actionReceipt: "r1" }).evidence_receipt, "r2");
});

test("dwell and exact-five displayed capacity are both required", () => {
  const rows = [
    { ts: 100, receipt: "r0", ask: 59, asks: [[59, 4]] },
    { ts: 111, receipt: "r1", ask: 59, asks: [[59, 4]] },
    { ts: 112, receipt: "r2", ask: 59, asks: [[59, 5]] },
  ];
  assert.strictEqual(findStrictlyLaterReach(rows, { actionTs: 100, targetCents: 59, actionReceipt: "action" }).evidence_receipt, "r2");
});

test("no later reach returns null and never reprices", () => {
  const rows = [
    { ts: 100, receipt: "r0", ask: 60, asks: [[60, 100]] },
    { ts: 120, receipt: "r1", ask: 60, asks: [[60, 100]] },
  ];
  assert.strictEqual(findStrictlyLaterReach(rows, { actionTs: 100, targetCents: 59, actionReceipt: "action" }), null);
});

const artifactIndex = process.argv.indexOf("--artifact");
if (artifactIndex >= 0) test("frozen V23 artifact conserves population, audited ruler, and Phase-0 identities", () => {
  const artifact = path.resolve(process.argv[artifactIndex + 1]);
  const readJson = (name) => JSON.parse(fs.readFileSync(path.join(artifact, name), "utf8"));
  const readRows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(artifact, name))).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);
  const comparison = readJson("V23_VS_A.json"), regrade = readJson("AUDITED_CLOSE_REGRADE.json"), phase0 = readJson("PHASE0_25_PAR_FAILURE_DISPOSITION.json"), spec = readJson("V22_PHASE1_LANDING_ESTIMATOR_SPEC.json");
  assert.strictEqual(comparison.V23_PAIR_CAP_IMMEDIATE.D, 804);
  assert.strictEqual(readRows("V23_LEG_LEDGER.jsonl.gz").length, 1608);
  assert.strictEqual(regrade.audited_close_rows, 1608);
  assert.strictEqual(regrade.replay_close_null_audit_recovers, 250);
  assert.strictEqual(regrade.no_in_window_print, 51);
  assert.strictEqual(phase0.count, 25);
  assert.deepStrictEqual(phase0.A_combined_cost_distribution, { 100: 18, 101: 7 });
  assert.strictEqual(spec.current_shape_surface.numeric_own_close_landing_coverage_legs, 0);
  assert.strictEqual(spec.identity_unresolved_hole.climber_first_identity_unresolved, 339);
});

if (process.exitCode) process.exit(process.exitCode);
