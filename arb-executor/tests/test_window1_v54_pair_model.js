"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v54_pair_model.js");
const v53 = require("../analysis/window1_v53_understanding_organ.js");

const makeState = (onset, prices) => {
  const state = policy.emptyLegState(onset);
  prices.forEach((price, index) => policy.observePostOnset(state, { ts: onset + index, receipt: `p-${price}-${index}`, kind: "PRINT", price }));
  return state;
};

const states = {
  A: makeState(100, [50, 52, 54, 55, 56]),
  B: makeState(100, [50, 48, 46, 45, 44]),
};
const context = {
  event_id: "TEST",
  category: "ATP_MAIN",
  row: { ts: 106, receipt: "book-eval", kind: "BOOK", bid: 55, ask: 57 },
  states,
  shape_taxonomy_commit: "taxonomy",
  shape_taxonomy_path: "taxonomy.json",
  trd5_commit: "trd5",
  formation_anchors: {
    A: { value_cents: 50, formation_end_epoch: 100, source_receipt: "l16-A" },
    B: { value_cents: 50, formation_end_epoch: 100, source_receipt: "l16-B" },
  },
  joint_reads: {
    A: { state: "RISING", pressure_state: "RISING", quote_path_state: "RISING", receipt: "book-eval" },
    B: { state: "FALLING", pressure_state: "FALLING", quote_path_state: "FALLING", receipt: "book-eval" },
  },
  machine_states: { A: "RISING", B: "FALLING" },
  positions: { A: {}, B: {} },
};

const gameView = policy.buildGameView(states, context);
const plan = policy.buildPlan(gameView, context);
assert.equal(plan.licensed, true);
assert.equal(plan.polarity.tag, "DECIDED");
assert.equal(plan.polarity.strengthening_leg_id, "A");
assert.equal(plan.polarity.fading_leg_id, "B");
assert.notEqual(plan.polarity.strengthening_leg_id, plan.polarity.fading_leg_id);
assert.deepEqual(plan.windows, { A: "EARLY", B: "LATE" });
assert.equal(plan.l16_anchor_targets_cents.A, 50);
assert.equal(plan.l16_anchor_targets_cents.B, 50);

const conflictContext = {
  ...context,
  joint_reads: { ...context.joint_reads, A: { ...context.joint_reads.A, pressure_state: "FALLING" } },
};
const conflictPlan = policy.buildPlan(policy.buildGameView(states, conflictContext), conflictContext);
assert.equal(conflictPlan.polarity.tag, "UNDECIDED");
assert.equal(conflictPlan.polarity.strengthening_leg_id, null);
assert.equal(conflictPlan.polarity.fading_leg_id, null);
assert.match(conflictPlan.polarity.reason, /DISAGREES/);

const lineage = { action: "PLACE_REST", target_cents: 42, reason: "LINEAGE" };
const decision = { action: "PLACE_REST", target_cents: 50, reason: "V54" };
const license = policy.jointLicense({ legId: "A", siblingCredited: false, siblingStandingTarget: null, book: { receipt: "book-eval" } }, plan, lineage, decision);
assert.equal(license.complete, true);
assert.equal(license.budget_split.sum_cents, 99);
assert.equal(license.budget_split.sibling_cents, 49);
assert.match(license.sentence, /A is STRENGTHENING/);
assert.match(license.sentence, /B is FADING/);
assert.match(license.sentence, /EARLY/);
assert.match(license.sentence, /LATE/);
assert.match(license.sentence, /ACTION=PLACE_REST; TARGET_CENTS=50; ACTIVE_TARGET_BEFORE_CENTS=NONE\./);
assert.equal(license.sentence_action_assertion.hard_assert, true);
assert.equal(license.sentence_action_assertion.equal, true);

const repriceLicense = policy.jointLicense({ legId: "A", activeTarget: 42, siblingCredited: false, siblingStandingTarget: null, book: { receipt: "book-eval" } }, plan, lineage, { action: "REPRICE_REST", target_cents: 50, reason: "V54" });
assert.match(repriceLicense.sentence, /ACTION=REPRICE_REST; TARGET_CENTS=50; ACTIVE_TARGET_BEFORE_CENTS=42\./);
assert.equal(repriceLicense.sentence_action_assertion.equal, true);

const undecidedLicense = policy.jointLicense({ legId: "A", siblingCredited: false, siblingStandingTarget: null, book: { receipt: "book-eval" } }, conflictPlan, lineage, lineage);
assert.equal(undecidedLicense.complete, true);
assert.equal(undecidedLicense.polarity.tag, "UNDECIDED");
assert.match(undecidedLicense.sentence, /frozen champion owns both levels/);
assert.equal(undecidedLicense.sentence_action_assertion.equal, true);

const impossible = { tag: "DECIDED", strengthening_leg_id: "A", fading_leg_id: "A" };
const malformed = policy.jointLicense({ legId: "A", siblingCredited: false, book: { receipt: "book-eval" } }, { ...plan, polarity: impossible }, lineage, decision);
assert.equal(malformed.complete, false);

const fractionalAnchorContext = {
  ...context,
  formation_anchors: { ...context.formation_anchors, A: { value_cents: 50.5, formation_end_epoch: 100, source_receipt: "l16-A-half" } },
};
const fractionalAnchorView = policy.buildGameView(states, fractionalAnchorContext);
assert.equal(fractionalAnchorView.legs.A.l16_formation_anchor.raw_value_cents, 50.5);
assert.equal(fractionalAnchorView.legs.A.l16_formation_anchor.value_cents, 50);
assert.equal(fractionalAnchorView.legs.A.l16_formation_anchor.integerization, "L16_SERIES_FLOORED_AT_FORMATION_END");

// The dense-replay cache is value-equivalent to the original prefix scans.
const cached = policy.emptyLegState(200);
[
  { ts: 200, receipt: "b0", kind: "BOOK", bid: 40, ask: 44, last_trade: null },
  { ts: 201, receipt: "b1", kind: "BOOK", bid: 41, ask: 45, last_trade: null },
  { ts: 202, receipt: "p0", kind: "PRINT", price: 47 },
  { ts: 203, receipt: "b2", kind: "BOOK", bid: null, ask: null, last_trade: null },
  { ts: 204, receipt: "p1", kind: "PRINT", price: 39 },
].forEach((row) => policy.observePostOnset(cached, row));
const cachedRefs = cached.observations.map((row) => row.reference_cents).filter(Number.isInteger);
let slowAdjacentMaxStep = 0;
cached.observations.slice(1).forEach((row, index) => {
  const prior = cached.observations[index].reference_cents;
  if (Number.isInteger(row.reference_cents) && Number.isInteger(prior)) slowAdjacentMaxStep = Math.max(slowAdjacentMaxStep, Math.abs(row.reference_cents - prior));
});
assert.equal(cached.running_reference_min_cents, Math.min(...cachedRefs));
assert.equal(cached.running_reference_max_cents, Math.max(...cachedRefs));
assert.equal(cached.adjacent_reference_max_step_cents, slowAdjacentMaxStep);
const cachedView = v53.legView(cached, { category: "ATP_MAIN" });
assert.equal(cachedView.travel.min_cents, Math.min(...cachedRefs));
assert.equal(cachedView.travel.max_cents, Math.max(...cachedRefs));
assert.equal(cachedView.travel.value_cents, Math.max(...cachedRefs) - Math.min(...cachedRefs));

console.log("window1_v54_pair_model: PASS");
