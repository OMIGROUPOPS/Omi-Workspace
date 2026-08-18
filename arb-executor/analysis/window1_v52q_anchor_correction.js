"use strict";

// V52q changes one input binding over V52p.  The role anchor is the
// spread-settle midpoint at formation end and the causal print series begins
// at formation end.  Ripeness, depth selection, all six judgment clauses,
// referee, crediting, and REFLEX_POST remain V52p/V52l behavior.

const v52p = require("./window1_v52p_ripeness_gated_role_binding.js");

const ANCHOR_METHOD_COMMIT = "e269779b0ec025d55f67d576e3cfb0cb575d5890";
const ANCHOR_DISCREPANCY_COMMIT = "620fe4c1";
const GROUND_TRUTH_COMMIT = "c0056976c446afcb4d9603796a2e06c068ee94d6";
let anchorBinding = null;

function ensure(value, message) { if (!value) throw new Error(message); }
function finite(value) { return Number.isFinite(value); }
function lawfulCent(value) { return Number.isInteger(value) && value >= 1 && value <= 99; }

function configureAnchorCorrection(value) {
  ensure(value?.method?.commit === ANCHOR_METHOD_COMMIT, "V52q anchor method commit mismatch");
  ensure(value?.method?.name === "SPREAD_SETTLE_MID_AT_FORMATION_END", "V52q anchor method name mismatch");
  ensure(value?.ground_truth?.commit === GROUND_TRUTH_COMMIT, "V52q ground-truth commit mismatch");
  ensure(value?.discrepancy?.commit?.startsWith(ANCHOR_DISCREPANCY_COMMIT), "V52q discrepancy commit mismatch");
  ensure(value?.series_floor === "FORMATION_END_INCLUSIVE", "V52q price-series floor mismatch");
  anchorBinding = value;
  return { bound: true, method: value.method, series_floor: value.series_floor };
}

function requiredAnchorCorrection() {
  ensure(anchorBinding, "V52q anchor correction not configured");
  return anchorBinding;
}

function benchmarkRuleReceipt() {
  const binding = requiredAnchorCorrection();
  return {
    name: "SHAPE_TAXONOMY_BUILD1_EXACT_EARLY_ROLE_RULE_ANCHOR_CORRECTED",
    expression: "drift=last_true_print_at_or_before_receipt_and_at_or_after_formation_end-spread_settle_mid_at_formation_end; drift>=2=>ROLE_UP; drift<=-2=>ROLE_DOWN; else ROLE_STILL_candidate",
    threshold_cents: v52p.BENCHMARK_ROLE_THRESHOLD_CENTS,
    anchor_method: binding.method,
    series_floor: binding.series_floor,
    ground_truth: binding.ground_truth,
    discrepancy: binding.discrepancy,
    new_constants: 0,
  };
}

function abstention(raw, evaluation, status) {
  const categoryGate = v52p.CATEGORY_GATES[evaluation.category] ?? null;
  ensure(categoryGate !== null, `V52q category gate absent ${evaluation.category}`);
  return {
    ...raw,
    status,
    role: "ABSTAIN",
    bound_role: null,
    candidate_role: null,
    signable: false,
    drift_cents: null,
    post_formation_open_cents: evaluation.published_anchor_cents ?? null,
    post_formation_open_receipt: evaluation.published_anchor_receipt ?? null,
    formation_end_epoch: evaluation.formation_end_epoch ?? null,
    last_causal_print_cents: null,
    last_causal_print_receipt: null,
    true_print_count: 0,
    evaluation_timestamp_epoch: evaluation.timestamp_epoch,
    evaluation_receipt: evaluation.receipt ?? null,
    maximum_consumed_timestamp_epoch: null,
    causal: true,
    right_edge_consumed: false,
    full_span_fit: false,
    anchor_correction: {
      anchor_cents: evaluation.published_anchor_cents ?? null,
      anchor_receipt: evaluation.published_anchor_receipt ?? null,
      formation_end_epoch: evaluation.formation_end_epoch ?? null,
      method: requiredAnchorCorrection().method,
      ground_truth: requiredAnchorCorrection().ground_truth,
      series_floor: requiredAnchorCorrection().series_floor,
    },
    ripeness: {
      verified_span_f: v52p.fraction(evaluation.timestamp_epoch, evaluation.formation_end_epoch, evaluation.verified_span_end_epoch),
      scheduled_span_f_live_proxy: v52p.fraction(evaluation.timestamp_epoch, evaluation.formation_end_epoch, evaluation.scheduled_span_end_epoch),
      class_gate_f: null,
      category_gate_f: categoryGate,
      effective_gate_f: null,
      verified_binding: false,
      scheduled_proxy_binding: false,
      binding_decision_diverges: false,
      decision_basis: "VERIFIED_PRE_MATCH_SPAN",
      live_proxy_basis: "SCHEDULED_START_SPAN_TELEMETRY_ONLY",
      source: v52p.requiredRipeness().provenance,
      new_constants: 0,
    },
    rule: benchmarkRuleReceipt(),
  };
}

function classifyShapeState(state, evaluation = {}) {
  if (evaluation.anchor_correction_enabled !== true) return v52p.classifyShapeState(state, evaluation);
  ensure(finite(evaluation.timestamp_epoch), "V52q evaluation timestamp absent");
  const base = { evaluation_timestamp_epoch: evaluation.timestamp_epoch, evaluation_receipt: evaluation.receipt ?? null };
  if (!finite(evaluation.formation_end_epoch) || !lawfulCent(evaluation.published_anchor_cents)) {
    return abstention(base, evaluation, "ABSTAIN_PUBLISHED_ANCHOR_UNAVAILABLE");
  }
  if (evaluation.timestamp_epoch < evaluation.formation_end_epoch) return abstention(base, evaluation, "ABSTAIN_FORMATION_NOT_COMPLETE");
  const prints = state.prints.filter((row) => row.timestamp_epoch >= evaluation.formation_end_epoch && row.timestamp_epoch <= evaluation.timestamp_epoch);
  if (!prints.length) return abstention(base, evaluation, "ABSTAIN_NO_POST_FORMATION_TRUE_PRINT");

  const last = prints.at(-1);
  const drift = last.price_cents - evaluation.published_anchor_cents;
  const candidateRole = drift >= v52p.BENCHMARK_ROLE_THRESHOLD_CENTS
    ? "ROLE_UP"
    : drift <= -v52p.BENCHMARK_ROLE_THRESHOLD_CENTS
      ? "ROLE_DOWN"
      : "ROLE_STILL";
  const classGate = v52p.CLASS_GATES[candidateRole];
  const categoryGate = v52p.CATEGORY_GATES[evaluation.category] ?? null;
  ensure(finite(classGate) && finite(categoryGate), `V52q ripeness gate absent ${candidateRole}/${evaluation.category}`);
  const effectiveGate = Math.max(classGate, categoryGate);
  const verifiedF = v52p.fraction(evaluation.timestamp_epoch, evaluation.formation_end_epoch, evaluation.verified_span_end_epoch);
  const scheduledF = v52p.fraction(evaluation.timestamp_epoch, evaluation.formation_end_epoch, evaluation.scheduled_span_end_epoch);
  const verifiedPass = finite(verifiedF) && verifiedF >= effectiveGate;
  const scheduledPass = finite(scheduledF) && scheduledF >= effectiveGate;
  const boundRole = verifiedPass ? candidateRole : null;
  return {
    status: verifiedPass ? `RIPENESS_BOUND_${candidateRole}` : "ABSTAIN_BELOW_EFFECTIVE_RIPENESS_GATE",
    role: boundRole === "ROLE_DOWN" ? "ROLE_DOWN" : boundRole === "ROLE_UP" ? "ROLE_UP" : "ABSTAIN",
    bound_role: boundRole,
    candidate_role: candidateRole,
    signable: boundRole !== null,
    drift_cents: drift,
    post_formation_open_cents: evaluation.published_anchor_cents,
    post_formation_open_receipt: evaluation.published_anchor_receipt ?? null,
    formation_end_epoch: evaluation.formation_end_epoch,
    last_causal_print_cents: last.price_cents,
    last_causal_print_receipt: last.receipt,
    true_print_count: prints.length,
    evaluation_timestamp_epoch: evaluation.timestamp_epoch,
    evaluation_receipt: evaluation.receipt ?? null,
    maximum_consumed_timestamp_epoch: last.timestamp_epoch,
    causal: true,
    right_edge_consumed: false,
    full_span_fit: false,
    anchor_correction: {
      anchor_cents: evaluation.published_anchor_cents,
      anchor_receipt: evaluation.published_anchor_receipt ?? null,
      formation_end_epoch: evaluation.formation_end_epoch,
      method: requiredAnchorCorrection().method,
      ground_truth: requiredAnchorCorrection().ground_truth,
      series_floor: requiredAnchorCorrection().series_floor,
    },
    ripeness: {
      verified_span_f: verifiedF,
      scheduled_span_f_live_proxy: scheduledF,
      class_gate_f: classGate,
      category_gate_f: categoryGate,
      effective_gate_f: effectiveGate,
      verified_binding: verifiedPass,
      scheduled_proxy_binding: scheduledPass,
      binding_decision_diverges: verifiedPass !== scheduledPass,
      decision_basis: "VERIFIED_PRE_MATCH_SPAN",
      live_proxy_basis: "SCHEDULED_START_SPAN_TELEMETRY_ONLY",
      source: v52p.requiredRipeness().provenance,
      new_constants: 0,
    },
    rule: benchmarkRuleReceipt(),
  };
}

function normalizedClauses(value = {}) {
  const clauses = v52p.normalizedClauses(value);
  return value.anchor_correction ? { ...clauses, anchor_correction: true } : clauses;
}

module.exports = {
  ...v52p,
  ANCHOR_METHOD_COMMIT,
  ANCHOR_DISCREPANCY_COMMIT,
  GROUND_TRUTH_COMMIT,
  configureAnchorCorrection,
  requiredAnchorCorrection,
  benchmarkRuleReceipt,
  classifyShapeState,
  normalizedClauses,
};
