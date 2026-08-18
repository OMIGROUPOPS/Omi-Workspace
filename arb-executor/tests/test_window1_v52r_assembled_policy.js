#!/usr/bin/env node
"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v52r_assembled_policy.js");

let assertions = 0;
const equal = (actual, expected, message) => { assertions += 1; assert.deepStrictEqual(actual, expected, message); };
const check = (value, message) => { assertions += 1; assert(value, message); };

const anchor = {
  method: { name: "SPREAD_SETTLE_MID_AT_FORMATION_END", commit: policy.ANCHOR_METHOD_COMMIT, path: "METHOD.json", sha256: "a".repeat(64), literal: "first mid with spread<=10c holding <=20c for 30min" },
  ground_truth: { commit: policy.GROUND_TRUTH_COMMIT, sha256: "b".repeat(64) },
  discrepancy: { commit: `${policy.ANCHOR_DISCREPANCY_COMMIT}abcdef`, sha256: "c".repeat(64) },
  series_floor: "FORMATION_END_INCLUSIVE",
};
equal(policy.configureAnchorCorrection(anchor).bound, true);
equal(policy.configureTRD5({ artifact: { LABEL: "GATE_POLICY_EVALUATION_LIVE_COORDINATES", grid: { TRD5: { cfg: { mt: 5 } } }, binding_rule: "bind at first gate crossing with a directional call; hold unless the instrument itself flips" }, provenance: { commit: policy.TRD5_COMMIT, path: "TRD5.json", sha256: "d".repeat(64) } }).bound, true);
equal(policy.configureLOW1({ artifact: { LABEL: "DOWN_TARGET_FRONTIER", rules: { "LOW-1": { delta: 1 } } }, provenance: { commit: policy.LOW1_COMMIT, path: "LOW1.json", sha256: "e".repeat(64) } }).bound, true);
equal(policy.TRD5_MIN_POST_ONSET_TRADES, 5);
equal(policy.LOW1_DELTA_CENTS, 1);
equal(policy.recognitionReceipt().new_constants, 0);

const state = policy.emptyShapeState();
const push = (ts, ordinal, price) => policy.observeTruePrint(state, { kind: "PRINT", ts, ordinal, price, receipt: `P${ordinal}` });
push(90, 1, 80); // excluded by coordinate zero
for (const [index, price] of [51, 51, 52, 52].entries()) push(110 + index * 10, index + 2, price);
const baseEvaluation = { timestamp_epoch: 140, receipt: "E4", category: "ATP_MAIN", assembled_policy_enabled: true, anchor_correction_enabled: true, post_onset_epoch: 105, formation_end_epoch: 100, published_anchor_cents: 50, published_anchor_receipt: "GROUND#LEG" };
let result = policy.classifyShapeState(state, baseEvaluation);
equal(result.status, "ABSTAIN_TRD5_NOT_MET");
equal(result.true_print_count, 4);
equal(result.bound_role, null);
equal(result.candidate_role, "ROLE_UP");
equal(result.coordinate_zero_epoch, 105);
equal(result.maximum_consumed_timestamp_epoch, 140);
equal(result.anchor_correction.method.sha256, "a".repeat(64));

push(150, 6, 53);
result = policy.classifyShapeState(state, { ...baseEvaluation, timestamp_epoch: 150, receipt: "E5" });
equal(result.bound_role, "ROLE_UP");
equal(result.role, "ROLE_UP");
equal(result.trd5.transition, "FIRST_BIND");
equal(result.trd5.first_bind.trade_count, 5);
equal(result.trd5.flip_count, 0);
equal(result.trd5.provenance.commit, policy.TRD5_COMMIT);

push(160, 7, 50);
result = policy.classifyShapeState(state, { ...baseEvaluation, timestamp_epoch: 160, receipt: "E6" });
equal(result.candidate_role, "ROLE_STILL");
equal(result.bound_role, "ROLE_UP");
equal(result.trd5.transition, "HELD_THROUGH_STILL");

push(170, 8, 47);
result = policy.classifyShapeState(state, { ...baseEvaluation, timestamp_epoch: 170, receipt: "E7" });
equal(result.candidate_role, "ROLE_DOWN");
equal(result.bound_role, "ROLE_DOWN");
equal(result.trd5.transition, "INSTRUMENT_FLIP_REBIND");
equal(result.trd5.flip_count, 1);
equal(result.trd5.last_flip.from, "ROLE_UP");
equal(result.trd5.last_flip.to, "ROLE_DOWN");

const machineReadEvidence = { evaluation_timestamp_epoch: 170, directional_evidence_timestamp_epoch: 170, evaluation_receipt: "E7", directional_evidence_receipt: "P8", post_onset_observation_bounds: { min_cents: 40, max_cents: 60 } };
const incumbent = { action: "PLACE_REST", target_cents: 49, reason: "V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY", placement: { target_cents: 49, authority: "V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY" } };
const license = { onset: { passed: true, timestamp_epoch: 105 }, read: { passed: true }, coherence: { lows_under_par: true, disagreement_clear: true }, diary: { own_post_onset_true_trade_low_cents: 47, own_receipt: "P8" }, level: { macro_recognition: result, machine_read_evidence: machineReadEvidence } };
let selected = policy.low1Selection(license, incumbent, { book: { ask: 55 }, siblingCredited: true, siblingEntryCents: 52 });
equal(selected.applicable, true);
equal(selected.session_low_cents, 47);
equal(selected.delta_cents, 1);
equal(selected.selected_target_cents, 46);
equal(selected.clause_6_cap_cents, 47);
equal(selected.arithmetic, "47-1=46;min(46,55-1,47)=46");
equal(selected.low1_identity, "TRAIL1_IDENTICAL_TO_LOW_1_ON_INTEGER_TAPE");
equal(selected.provenance.commit, policy.LOW1_COMMIT);

selected = policy.low1Selection({ ...license, diary: { own_post_onset_true_trade_low_cents: 57, own_receipt: "P9" } }, incumbent, { book: { ask: 55 }, siblingCredited: true, siblingEntryCents: 52 });
equal(selected.selected_target_cents, 47);
equal(selected.current_touch_above_bound_applied, true);
equal(selected.joint_law_bound_applied, true);

const upRecognition = { ...result, role: "ROLE_UP", bound_role: "ROLE_UP" };
selected = policy.low1Selection({ ...license, level: { ...license.level, macro_recognition: upRecognition } }, incumbent, { book: { ask: 55 } });
equal(selected.applicable, false);
equal(selected.selected_target_cents, 49);
equal(selected.level_policy, "V52L_DEFAULT_EVIDENCE_BACKED_LEVEL");

const clauses = policy.normalizedClauses({ assembled_policy: true });
equal(clauses.assembled_policy, true);
equal(clauses.anchor_correction, true);
equal(clauses.ripeness_role_binding, false);
equal(clauses.remove_pair_lows_precondition, undefined);
check(policy.classifyShapeState !== policy.familyFromSignature);
check(policy.floorDepthSelection === policy.low1Selection);

process.stdout.write(`${JSON.stringify({ assertions, failures: 0, omissions: 0, deselections: 0, fitted_constants: 0 })}\n`);
