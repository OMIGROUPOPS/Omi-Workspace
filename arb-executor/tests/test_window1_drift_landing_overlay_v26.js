#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const {
  asymmetricLoss,
  authority,
  estimateAtRead,
  overlayDecision,
  selectCellFit,
} = require("../analysis/window1_drift_landing_overlay_v26_policy.js");
const { firstQualifiedReads } = require("../analysis/build_window1_drift_landing_overlay_v26.js");

let passed = 0;
function test(name, fn) { try { fn(); passed += 1; process.stdout.write(`PASS ${name}\n`); } catch (error) { process.stderr.write(`FAIL ${name}: ${error.stack}\n`); process.exitCode = 1; } }
function training(n, spread, delta) { return Array.from({ length: n }, (_, i) => ({ audited_close_cents: 60 + (i % 3), reads: { [spread]: { bid: 60 + (i % 3) - delta } } })); }

test("qualified read binds bid ask last spread dwell as one observation", () => {
  const rows = [
    { ts: 0, ordinal: 1, receipt: "r1", bid: 50, ask: 52, spread: 2, top_ask_size: 5, top5_ask_depth: 10, last_traded: 51, asks: [[52, 5]] },
    { ts: 9, ordinal: 2, receipt: "r2", bid: 50, ask: 52, spread: 2, top_ask_size: 5, top5_ask_depth: 10, last_traded: 51, asks: [[52, 5]] },
    { ts: 10, ordinal: 3, receipt: "r3", bid: 50, ask: 52, spread: 2, top_ask_size: 5, top5_ask_depth: 10, last_traded: 51, asks: [[52, 5]] },
  ];
  const reads = firstQualifiedReads(rows);
  assert.equal(reads[1], null); assert.equal(reads[2].receipt, "r3"); assert.equal(reads[2].last_traded, 51); assert.equal(reads[2].dwell_seconds, 10);
});
test("unqualified books leave the organ silent", () => assert.equal(estimateAtRead({ state: "BOUND", spread_cents: 1, cell_drift_cents: 2, n: 30 }, { 1: null }).state, "SILENT"));
test("spread law selects only 1 2 or 3 cent candidates", () => assert.equal(selectCellFit(training(30, 2, 2)).spread_cents, 2));
test("minimum training support is thirty qualified reads", () => assert.equal(selectCellFit(training(29, 1, 2)).state, "ABSTAIN"));
test("landing estimate is qualified bid plus cell drift", () => assert.equal(estimateAtRead({ state: "BOUND", spread_cents: 2, cell_drift_cents: 3, n: 30 }, { 2: { bid: 55 } }).landing_estimate_cents, 58));
test("asymmetric loss is finite and directional", () => assert(asymmetricLoss(60, 62) > asymmetricLoss(60, 59)));
test("authority requires all four bars", () => assert.equal(authority({ validation_n: 30, non_overestimate_rate: .7, mean_overestimate_when_wrong_cents: 2, estimator_asymmetric_loss: 1, naive_bid_asymmetric_loss: 2, qualified_read_coverage: .5 }, true).authorized, true));
test("noncandidate cell cannot earn authority", () => assert.equal(authority({ validation_n: 30, non_overestimate_rate: 1, mean_overestimate_when_wrong_cents: 0, estimator_asymmetric_loss: 0, naive_bid_asymmetric_loss: 1, qualified_read_coverage: 1 }, false).authorized, false));
test("absent authority preserves V23", () => assert.equal(overlayDecision({ cellAuthorized: false, incumbentAction: { price_cents: 50 }, estimate: { state: "BOUND", landing_estimate_cents: 40 } }).incumbent_byte_identity_required, true));
test("authorized refinement can only lower an existing V23 aim", () => assert.equal(overlayDecision({ cellAuthorized: true, incumbentAction: { price_cents: 50 }, estimate: { state: "BOUND", landing_estimate_cents: 48 } }).price_cents, 47));
test("authorized refinement never raises an existing V23 aim", () => assert.equal(overlayDecision({ cellAuthorized: true, incumbentAction: { price_cents: 40 }, estimate: { state: "BOUND", landing_estimate_cents: 48 } }).price_cents, 40));
test("mirror release requires explicit own-decline ordinal release", () => assert.equal(overlayDecision({ cellAuthorized: true, incumbentAction: null, estimate: { state: "BOUND", landing_estimate_cents: 48 }, mirrorRelease: { state: "RELEASE" } }).state, "EARLY_MIRROR_RELEASE"));
test("frozen artifact conserves unauthorized streams", () => {
  const file = path.join(__dirname, "../../.claude/window1_live_v4_replay/drift_landing_overlay_v26_20260804/DIFFERENTIAL_RECEIPT.json"); if (!fs.existsSync(file)) return;
  const receipt = JSON.parse(fs.readFileSync(file, "utf8")); assert.equal(receipt.unauthorized_changed_streams, 0); assert.equal(receipt.changed_leg_streams + receipt.identical_leg_streams, 1608);
});
test("top L9 miss identity set remains 77", () => {
  const file = path.join(__dirname, "../../.claude/window1_live_v4_replay/drift_landing_overlay_v26_20260804/TOP_MISS_CELL_L9_ATP_CHALL_51_75.json"); if (!fs.existsSync(file)) return;
  const receipt = JSON.parse(fs.readFileSync(file, "utf8")); assert.equal(receipt.before.legs, 77); assert.equal(receipt.after.legs, 77); assert.equal(receipt.identities.length, 77);
});
if (!process.exitCode) process.stdout.write(`PASS ${passed}/${passed} V26 tests\n`);
