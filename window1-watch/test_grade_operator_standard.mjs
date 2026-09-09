import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { operatorGrade, floorCallGrade } from "./grade_operator_standard.mjs";
const rubric = JSON.parse(fs.readFileSync(new URL("./grade_rubric.json", import.meta.url)));
const S = "STORE SILENT";
function fixture() {
  const face = { legs: ["UP", "DOWN"], truth: { status: "OK", span_start_epoch: 100, span_end_epoch: 900, bell_epoch: 900,
    effective_row: { legA: "UP", legB: "DOWN", legA_open_postformation_c: 55, legA_close_c: 61, legB_open_postformation_c: 45, legB_close_c: 39 },
    legs: { UP: { floor_cents: 54, floor_epoch: 200 }, DOWN: { floor_cents: 38, floor_epoch: 800 } } } };
  const d = (epoch, a, b) => ({ epoch, receipt: String(epoch), roles: {
    UP: { first_bind: a, first_bind_epoch: epoch, current_role: a, flip_count: 0 },
    DOWN: { first_bind: b, first_bind_epoch: epoch, current_role: b, flip_count: 0 } } });
  const decisions = [d(150, "CLIMBER", "FALLER"), d(400, "CLIMBER", "FALLER")];
  const fill = (c, floor, epoch) => ({ filled: true, cents: c, vs_floor_cents: c-floor, fill_epoch: epoch, valid_span_fill: true });
  const sections = { sentence: { named_tokens_found: [] }, macro: {}, micro: { legs: Object.fromEntries(face.legs.map((l) => [l, {
    first_eligible_full_span: { q50: face.truth.legs[l].floor_cents, target_floor_cents: face.truth.legs[l].floor_cents, floor_error_cents: 0, receipt: "first" } }])) },
    hands: { actions: [], rest_age_at_fill_minutes: [], same_second_fills: 0, observed_post_only_violations: 0, observed_pre_formation_placements: 0,
      fill_age_uncheckable: 0, post_only_uncheckable: 0, formation_uncheckable: 0 },
    outcome: { legs: { UP: fill(55,54,600), DOWN: fill(39,38,850) }, valid_pair_completed: true, pair_sum: 94, captured_cents: 6, best_capturable_cents: 8, capture_ratio: .75 } };
  return { face, decisions, sections };
}
const run = (f, r=rubric) => operatorGrade(f.face, f.decisions, f.sections, r);
test("point boundaries and bounded range: no wide-band escape or later-Q selection", () => {
  for (const [e, expected] of [[1,"A"],[2,"B"],[3,"C"],[4,"F"]]) {
    assert.equal(floorCallGrade({ q50: 50+e, target_floor_cents: 50, floor_error_cents: e }, rubric.sections.MICRO,rubric).letter, expected);
  }
  const call = { q50:54, q25:50, q75:54, target_floor_cents:50, floor_error_cents:4 };
  assert.equal(floorCallGrade(call,rubric.sections.MICRO,rubric).letter,"B");
  assert.equal(floorCallGrade({...call,q75:56},rubric.sections.MICRO,rubric).letter,"C");
  assert.equal(floorCallGrade({...call,q75:57},rubric.sections.MICRO,rubric).letter,"F");
  assert.equal(floorCallGrade({...call,q25:51},rubric.sections.MICRO,rubric).letter,"F");
  assert.equal(floorCallGrade({...call,q25:55},rubric.sections.MICRO,rubric).range_letter,S);
  assert.equal(floorCallGrade({reason:"NO_ELIGIBLE_FORECAST"},rubric.sections.MICRO,rubric).letter,"F");
  assert.equal(floorCallGrade({},rubric.sections.MICRO,rubric).letter,S);
});
test("no capture uplift; pair fraction boundaries, not an absolute 97/99 sum", () => {
  const f=fixture(); assert.equal(run(f).letter,"A");
  f.sections.micro.legs.UP.first_eligible_full_span.floor_error_cents=2;
  assert.equal(run(f).letter,"B");
  for(const [ratio,expected] of [[.75,"A"],[.5,"B"],[.49,"C"]]) {
    f.sections.outcome.capture_ratio=ratio;
    assert.equal(run(f).grades.PAIR.letter,expected);
  }
  f.sections.outcome.pair_sum=100;f.sections.outcome.captured_cents=0;
  assert.equal(run(f).grades.PAIR.letter,"D");
  f.sections.outcome.pair_sum=101;
  assert.equal(run(f).letter,"F");
});
test("both fills must be near; past floor premium remains, no extra penalty", () => {
  const f=fixture();f.sections.outcome.legs.UP.vs_floor_cents=2;
  assert.equal(run(f).grades.TRADE.letter,"B");
  assert.equal(run(f).trade.legs.UP.floor_printed_before_fill,true);
  f.face.truth.legs.UP.floor_epoch=700;
  assert.equal(run(f).grades.TRADE.letter,"B");
  f.sections.outcome.legs.DOWN.vs_floor_cents=4;
  assert.equal(run(f).grades.TRADE.letter,"D");
  f.sections.outcome.legs.DOWN={filled:false,valid_span_fill:false};
  f.sections.outcome.valid_pair_completed=false;
  assert.equal(run(f).grades.TRADE.letter,"D");assert.equal(run(f).letter,"F");
});
test("initial call frozen; flips not automatically bad; post-fill correction cannot rescue", () => {
  const f=fixture();f.decisions[1].roles.UP.flip_count=3;
  assert.equal(run(f).grades.MACRO.letter,"A");
  f.decisions[0].roles.UP.first_bind="FALLER";
  assert.equal(run(f).grades.MACRO.letter,"C");
  f.decisions[0].roles.DOWN.first_bind="CLIMBER";
  assert.equal(run(f).grades.MACRO.letter,"F");
  f.decisions[0].roles.UP=null;f.decisions[1].roles.UP=null;
  assert.equal(run(f).grades.MACRO.letter,S);
});
test("quiet direction uses corrected close/open, not stale net_travel or an inferred role", () => {
  const f=fixture();f.face.truth.effective_row.legB_close_c=45;
  f.face.truth.effective_row.legB_net_travel_c=-15;
  for(const r of f.decisions) r.roles.DOWN={first_bind:null,current_role:"NOT_CALLABLE",flip_count:0};
  assert.equal(run(f).grades.MACRO.letter,"A");
});
test("no offer is not F or a success; safety and named tokens still override", () => {
  const f=fixture();f.sections.outcome.best_capturable_cents=0;
  assert.equal(run(f).letter,"NOT OFFERED");
  f.sections.sentence.named_tokens_found=["NAMED"];
  assert.equal(run(f).letter,"F");
  f.sections.sentence.named_tokens_found=[];f.sections.hands.same_second_fills=1;
  assert.equal(run(f).letter,"F");
  f.sections.hands.same_second_fills=0;f.sections.outcome.legs.UP.valid_span_fill=false;
  assert.equal(run(f).letter,"F");
});
test("oracle mean and timing stay diagnostic; missing safety never becomes A", () => {
  const f=fixture();f.face.oracle={legs:{UP:{mean_absolute_gap_cents:999}}};
  f.sections.micro.legs.UP.first_eligible_full_span.timing_error_minutes=9999;
  assert.equal(run(f).letter,"A");
  f.sections.hands.fill_age_uncheckable=1;
  assert.equal(run(f).letter,S);
});
