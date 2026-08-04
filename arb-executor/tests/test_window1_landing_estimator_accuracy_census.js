#!/usr/bin/env node
"use strict";
const assert = require("assert");
const { authority, summary } = require("../analysis/build_window1_landing_estimator_accuracy_census.js");

function test(name, fn) { try { fn(); process.stdout.write(`PASS ${name}\n`); } catch (e) { process.stderr.write(`FAIL ${name}: ${e.stack}\n`); process.exitCode = 1; } }
const good = Array.from({ length: 30 }, (_, i) => ({ signed_error_cents: i % 2, live_ask_minus_audited_close_cents: 2, audited_close_inside_q25_q75: true }));
const weak = Array.from({ length: 30 }, () => ({ signed_error_cents: 2, live_ask_minus_audited_close_cents: 1, audited_close_inside_q25_q75: true }));
test("summary reports signed bias MAE and calibration", () => { const s = summary(good); assert.equal(s.n, 30); assert.equal(s.MAE_cents, .5); assert.equal(s.bias_cents, .5); assert.equal(s.q25_q75_interval_calibration, 1); });
test("authority requires n30", () => assert.equal(authority(good.slice(0, 29)).authorized, false));
test("authority requires q50 to beat live ask baseline", () => assert.equal(authority(weak).authorized, false));
test("authority accepts calibrated improvement", () => assert.equal(authority(good).authorized, true));
if (!process.exitCode) process.stdout.write("PASS 4/4 estimator accuracy tests\n");
