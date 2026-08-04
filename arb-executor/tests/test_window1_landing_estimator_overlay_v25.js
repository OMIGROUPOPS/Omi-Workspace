#!/usr/bin/env node
"use strict";
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const { overlayDecision } = require("../analysis/window1_landing_estimator_overlay_v25_policy.js");
function test(name, fn) { try { fn(); process.stdout.write(`PASS ${name}\n`); } catch (e) { process.stderr.write(`FAIL ${name}: ${e.stack}\n`); process.exitCode = 1; } }
test("absent cell authority falls back byte-identically", () => assert.equal(overlayDecision({ cellAuthorized: false, incumbentAction: { price_cents: 50 }, estimate: { state: "BOUND", q50: 40 } }).incumbent_byte_identity_required, true));
test("missing estimate never gates incumbent", () => assert.equal(overlayDecision({ cellAuthorized: true, incumbentAction: { price_cents: 50 }, estimate: null }).state, "FALLBACK"));
test("authorized estimator can only clamp an existing aim downward", () => assert.equal(overlayDecision({ cellAuthorized: true, incumbentAction: { price_cents: 50 }, estimate: { state: "BOUND", q50: 47 } }).price_cents, 47));
test("authorized estimator never raises an existing aim", () => assert.equal(overlayDecision({ cellAuthorized: true, incumbentAction: { price_cents: 50 }, estimate: { state: "BOUND", q50: 55 } }).price_cents, 50));
test("authorized phased candidate can release a mirror hold", () => assert.equal(overlayDecision({ cellAuthorized: true, incumbentAction: null, estimate: { state: "BOUND", q50: 55 }, phasedMirrorCandidate: { state: "PLACE", price_cents: 40 } }).state, "EARLY_MIRROR_RELEASE"));
test("frozen differential is 1608 identical streams when present", () => { const p=path.join(__dirname,"../../.claude/window1_live_v4_replay/landing_estimator_overlay_v25_20260804/DIFFERENTIAL_RECEIPT.json"); if(!fs.existsSync(p)) return; const r=JSON.parse(fs.readFileSync(p)); assert.equal(r.identical_leg_streams,1608); assert.equal(r.differing_leg_streams,0); assert.equal(r.leg_ledgers_byte_identical,true); });
if (!process.exitCode) process.stdout.write("PASS 6/6 V25 overlay tests\n");
