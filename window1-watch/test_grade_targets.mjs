import { test } from "node:test";
import assert from "node:assert/strict";
import { remainingTargets, microMeasurements, measureRestAges } from "./grade_measurements.mjs";
import { applyFiledCorrections, readGradeRulers } from "./grade_rulers.mjs";
import { fileURLToPath } from "node:url";
const repo = fileURLToPath(new URL("..", import.meta.url));

const truth = {
  status: "OK", span_start_epoch: 100, span_end_epoch: 900, bell_epoch: 950,
  legs: { A: { status: "OK", floor_cents: 20, floor_epoch: 150 } },
};
const prints = [
  { epoch: 150, price: 20, receipt: "old" },
  { epoch: 300, price: 30, receipt: "at-receipt" },
  { epoch: 450, price: 35, receipt: "later" },
  { epoch: 600, price: 35, receipt: "tie" },
  { epoch: 900, price: 10, receipt: "at-end" },
];
test("carry is a receipt-time target, not a future print; span end excluded; tie uses first", () => {
  const t = remainingTargets(prints, 300, truth);
  assert.equal(t.remaining_path.kind, "CARRIED_GATE_STATE_NOT_A_FUTURE_PRINT");
  assert.equal(t.remaining_path.floor_cents, 30);
  assert.equal(t.remaining_path.floor_epoch, 300);
  assert.equal(t.executable_future_print.floor_cents, 35);
  assert.equal(t.executable_future_print.floor_epoch, 450);
  assert.equal(remainingTargets(prints, 700, truth).executable_future_print.status, "STORE SILENT");
});
test("receipt eligibility never uses target outcomes; corrected clock never shifts deadline", () => {
  const face = { legs: ["A"], truth, bell: { timestamp_epoch: 1000 } };
  const forecast = { has_sentence: true, status: "RESOLVED", q50: 31, floor_mtb: 10,
    formation_end: 100, q_author: "POOL_BASE", x_author: "POOL_BASE_FLOOR_MTB" };
  const rows = [
    { epoch: 99, receipt: "pre", forecasts: { A: forecast } },
    { epoch: 250, receipt: "unresolved", forecasts: { A: { ...forecast, status: "INSUFFICIENT_EVIDENCE" } } },
    { epoch: 300, receipt: "first", forecasts: { A: forecast } },
    { epoch: 450, receipt: "better-later", forecasts: { A: { ...forecast, q50: 20 } } },
    { epoch: 900, receipt: "end", forecasts: { A: forecast } },
  ];
  const m = microMeasurements(face, rows, { legs: { A: prints } });
  const first = m.legs.A.first_eligible_full_span;
  assert.equal(first.receipt, "first");
  assert.equal(first.floor_error_cents, 11);
  assert.equal(first.deadline_epoch, 400);
  assert.equal(first.timing_error_minutes, (400 - 150) / 60);
  assert.equal(first.floor_already_observed_at_call, true);
  assert.equal(m.receipt_calls[2].targets.executable_future_print.floor_cents, 35);
  assert.equal(m.receipt_calls[4].eligible, false);
});
test("lineage survives repricing; unchanged price does not reset age; removal ends both", () => {
  const action = (kind, epoch, cents, receipt) => ({ leg: "A", kind, timestamp_epoch: epoch, new_cents: cents, receipt });
  const rows = [action("PLACE", 100, 30, "place"), action("REPRICE", 200, 29, "price"),
    action("REPRICE", 250, 29, "same-price"), action("FILL", 300, null, "fill"),
    action("PLACE", 400, 35, "second-place"), action("REMOVE", 450, null, "remove"),
    action("FILL", 500, null, "unbound-fill")];
  const ages = measureRestAges(rows), fill = ages.get(rows[3]);
  assert.equal(fill.order_lineage_age_minutes, 200 / 60);
  assert.equal(fill.current_price_age_minutes, 100 / 60);
  assert.equal(fill.current_price_receipt, "price");
  assert.equal(ages.get(rows[6]).current_price_age_minutes, "STORE SILENT");
});
test("same-second fill uses latest changed-price timestamp, not initial PLACE", () => {
  const rows = [{ leg: "A", kind: "PLACE", timestamp_epoch: 100, new_cents: 30 },
    { leg: "A", kind: "REPRICE", timestamp_epoch: 200.1, new_cents: 31 },
    { leg: "A", kind: "FILL", timestamp_epoch: 200.9 }];
  assert.equal(measureRestAges(rows).get(rows[2]).same_second_fill, true);
});
test("all correction fields overlay in ledger order without mutating original rows", () => {
  const face = { provenance: { event_id: "TEST" }, legs: ["A", "B"], bell: { timestamp_epoch: 999 } };
  const table = { rows: [{ values: { event_id: "TEST", verified_span: "OK", legA: "A", legB: "B", bell_epoch: 900,
    span_start_epoch: 100, span_end_epoch: 900, legA_floor_c: 30, legA_floor_epoch: 150,
    legB_floor_c: 40, legB_floor_epoch: 500, legA_open_postformation_c: 60, legB_open_postformation_c: 40 } }] };
  const before = JSON.stringify(table);
  const records = [{ correction_id: "one", after: { bell_epoch: 700, span_end_epoch: 700, span_start_epoch: 110,
    legA_A: { floor_c: 31, floor_epoch: 160, close_c: 35, us_fill_stamp: "POST_BELL_INVALID" } } },
  { correction_id: "two", after: { bell_source: "CORRECTED", legB_B: { floor_c: 41, floor_epoch: 510 },
    offered_under_par: { floor_sum_c: 72, margin_c: 28 } } }];
  const out = applyFiledCorrections(face, table, records.map((value) => ({ value, raw: JSON.stringify(value) })));
  assert.equal(JSON.stringify(table), before);
  assert.equal(out.bell_epoch, 700);
  assert.equal(out.span_start_epoch, 110);
  assert.equal(out.legs.A.floor_cents, 31);
  assert.equal(out.effective_row.legA_us_fill_stamp, "POST_BELL_INVALID");
  assert.equal(out.pair.discount_cents, 28);
  assert.equal(out.applied_corrections.length, 2);
});
test("filed corrections apply to every matching loaded game, not a typed special case", () => {
  for (const [event, legs, floors, sum] of [
    ["KXATPCHALLENGERMATCH-26JUL12GIUBAR", ["BAR", "GIU"], [27, 66], 93],
    ["KXATPCHALLENGERMATCH-26JUL14URSPAL", ["PAL", "URS"], [39, 57], 96],
  ]) {
    const r = readGradeRulers(repo, event, { provenance: { event_id: event }, legs, bell: { timestamp_epoch: 0 } });
    assert.deepEqual(legs.map((l) => r.effective_truth.legs[l].floor_cents), floors);
    assert.equal(r.effective_truth.pair.sum_cents, sum);
    assert.ok(r.original_table.row_csv);
    assert.ok(r.restated_rows.every((x) => x.original_correction && x.row_jsonl && x.row_sha256));
  }
});
