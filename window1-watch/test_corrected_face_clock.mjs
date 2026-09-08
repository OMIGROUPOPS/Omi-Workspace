import { test } from "node:test";
import assert from "node:assert/strict";
import { correctedBenchProjection } from "./face_contract.mjs";
import { applyRulerDisplayClock } from "./grade_rulers.mjs";
import { microMeasurements } from "./grade_measurements.mjs";

test("rebasing selects only a bench receipt already made, not the future same-numbered gate", () => {
  const named = { first_tick: { epoch: 1000, mtb_first: 60 }, gates: {
    30: { minutes_to_bell: 30, status: "older" },
    15: { minutes_to_bell: 15, status: "future" },
  } };
  const row = correctedBenchProjection(named, 4000, 15, {});
  assert.equal(row.status, "older");
  assert.equal(row.clock.source_receipt_epoch, 2800);
  assert.equal(row.minutes_to_bell, 20);
  assert.equal(row.clock.carried_age_minutes, 5);
  assert.equal(correctedBenchProjection(named, 4000, 30, {}), null);
});

test("ruler display clock preserves original origin, OS fields and original X deadline", () => {
  const face = { legs: ["A"], bell: { timestamp_epoch: 1000, t: 1 }, os: [{ stored: "unchanged" }],
    truth: { status: "OK", bell_epoch: 1100, span_start_epoch: 100, span_end_epoch: 1050,
      legs: { A: { status: "OK", floor_cents: 20, floor_epoch: 500 } } } };
  const original = face.bell.timestamp_epoch-face.bell.t*3600;
  assert.equal(applyRulerDisplayClock(face, face.truth), true);
  assert.ok(Math.abs(face.bell.timestamp_epoch-face.bell.t*3600-original) <= Number.EPSILON*Math.abs(original));
  assert.deepEqual(face.os, [{ stored: "unchanged" }]);
  assert.equal(applyRulerDisplayClock(face, face.truth), false);
  const grade = microMeasurements(face, [{ epoch: 200, receipt: "first", forecasts: { A: {
    status: "RESOLVED", has_sentence: true, q50: 21, floor_mtb: 10, formation_end: 100,
  } } }], { legs: { A: [{ epoch: 500, price: 20 }] } });
  assert.equal(grade.legs.A.first_eligible_full_span.deadline_epoch, 400);
  assert.equal(grade.clock.trace_bell_epoch, 1000);
});
