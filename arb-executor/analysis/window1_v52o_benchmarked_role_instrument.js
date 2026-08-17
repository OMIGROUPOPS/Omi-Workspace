"use strict";

// V52o supersedes the V52m/n classification bindings without deleting their
// observation paths.  Its only behavioral capability over adopted V52l is the
// taxonomy benchmark's published early-role instrument:
//   last causal true print - post-formation open >= +2c => ROLE_UP
//   last causal true print - post-formation open <= -2c => ROLE_DOWN
//   otherwise                                      => ABSTAIN
// No completed path, right edge, family classifier, or fitted confidence gate
// participates in this decision-time role call.

const v52n = require("./window1_v52n_recognition_confidence_gates.js");
const v52h = require("./window1_v52h_remove_pair_lows_precondition.js");

const BENCHMARK_ROLE_RULE_COMMIT = "e269779b0ec025d55f67d576e3cfb0cb575d5890";
const BENCHMARK_ROLE_THRESHOLD_CENTS = 2;
const DOWN_FAMILY_SUFFIX = "_DOWN";

function ensure(value, message) { if (!value) throw new Error(message); }
function finite(value) { return Number.isFinite(value); }
function lawfulCent(value) { return Number.isInteger(value) && value >= 1 && value <= 99; }

function configureShapeLibrary(value) {
  const configured = v52n.configureShapeLibrary(value);
  const benchmark = v52n.requiredLibrary().taxonomy?.benchmark;
  ensure(benchmark?.classifier === "early-window drift alone: last in-span print before the receipt minus post-formation open; >=+2c CLIMBER, <=-2c FALLER, else ABSTAIN", "V52o benchmark classifier text mismatch");
  ensure(value.taxonomy_provenance?.commit === BENCHMARK_ROLE_RULE_COMMIT, "V52o benchmark rule commit mismatch");
  for (const category of ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"]) {
    ensure(downDepthAggregate(category)?.component_rows?.length > 0, `V52o down-depth aggregate absent ${category}`);
  }
  return { ...configured, benchmark_role_rule_bound: true, threshold_cents: BENCHMARK_ROLE_THRESHOLD_CENTS };
}

function classifyShapeState(state, evaluation = {}) {
  if (evaluation.role_instrument_enabled !== true) return v52n.classifyShapeState(state, evaluation);
  const timestamp = evaluation.timestamp_epoch;
  ensure(finite(timestamp), "V52o evaluation timestamp absent");
  const sampled = v52n.sampleCausalPath(state, timestamp);
  if (!sampled) return {
    status: "ABSTAIN_NO_POST_FORMATION_TRUE_PRINT",
    role: "ABSTAIN",
    signable: false,
    drift_cents: null,
    post_formation_open_cents: null,
    last_causal_print_cents: null,
    evaluation_timestamp_epoch: timestamp,
    evaluation_receipt: evaluation.receipt ?? null,
    maximum_consumed_timestamp_epoch: null,
    causal: true,
    right_edge_consumed: false,
    full_span_fit: false,
    rule: benchmarkRuleReceipt(),
  };
  const open = sampled.prints[0];
  const last = sampled.prints.at(-1);
  const drift = last.price_cents - open.price_cents;
  const role = drift >= BENCHMARK_ROLE_THRESHOLD_CENTS
    ? "ROLE_UP"
    : drift <= -BENCHMARK_ROLE_THRESHOLD_CENTS
      ? "ROLE_DOWN"
      : "ABSTAIN";
  return {
    status: role === "ABSTAIN" ? "ABSTAIN_DRIFT_INSIDE_PUBLISHED_PLUS_MINUS_2C" : "BENCHMARK_ROLE_BOUND",
    role,
    signable: role !== "ABSTAIN",
    drift_cents: drift,
    post_formation_open_cents: open.price_cents,
    post_formation_open_receipt: open.receipt,
    last_causal_print_cents: last.price_cents,
    last_causal_print_receipt: last.receipt,
    true_print_count: sampled.prints.length,
    evaluation_timestamp_epoch: timestamp,
    evaluation_receipt: evaluation.receipt ?? null,
    maximum_consumed_timestamp_epoch: last.timestamp_epoch,
    causal: true,
    right_edge_consumed: false,
    full_span_fit: false,
    rule: benchmarkRuleReceipt(),
  };
}

function benchmarkRuleReceipt() {
  const configured = v52n.requiredLibrary();
  return {
    name: "SHAPE_TAXONOMY_BUILD1_EXACT_EARLY_ROLE_RULE",
    expression: "drift=last_true_print_at_or_before_receipt-post_formation_open; drift>=2=>ROLE_UP; drift<=-2=>ROLE_DOWN; else ABSTAIN",
    threshold_cents: BENCHMARK_ROLE_THRESHOLD_CENTS,
    taxonomy_commit: BENCHMARK_ROLE_RULE_COMMIT,
    taxonomy_sha256: configured.taxonomy_provenance.sha256,
    benchmark_classifier_literal: configured.taxonomy.benchmark.classifier,
    new_constants: 0,
  };
}

function downDepthAggregate(category) {
  const configured = v52n.requiredLibrary();
  const componentRows = configured.rows
    .filter((row) => row.category === category && row.family.endsWith(DOWN_FAMILY_SUFFIX) && finite(row.depth_below_open_c?.med) && Number.isInteger(row.legs) && row.legs > 0)
    .sort((a, b) => a.family.localeCompare(b.family));
  if (!componentRows.length) return null;
  const weight = componentRows.reduce((sum, row) => sum + row.legs, 0);
  const weightedNumerator = componentRows.reduce((sum, row) => sum + row.legs * row.depth_below_open_c.med, 0);
  return {
    row_identity: `ROLE_DOWN_AGGREGATE|${category}`,
    category,
    method: "FREQUENCY_WEIGHTED_MEAN_OF_EXISTING_CATEGORY_DOWN_FAMILY_MEDIAN_DEPTHS",
    component_rows: componentRows.map((row) => ({ row_identity: `${row.family}|${row.category}`, family: row.family, legs: row.legs, median_depth_below_open_cents: row.depth_below_open_c.med })),
    total_frequency_weight: weight,
    weighted_numerator: weightedNumerator,
    depth_below_open_cents: weightedNumerator / weight,
    omitted_category_rows: v52n.FAMILY_ORDER.filter((family) => family.endsWith(DOWN_FAMILY_SUFFIX) && !componentRows.some((row) => row.family === family)),
    borrowed_from: null,
    interpolation: false,
    provenance: configured.floor_table_provenance,
  };
}

function pairCap(inputs) {
  const counterpart = inputs?.siblingCredited === true ? inputs.siblingEntryCents : inputs?.siblingStandingTarget;
  return Number.isInteger(counterpart) ? 99 - counterpart : null;
}

function roleDepthSelection(license, incumbent, inputs = {}) {
  const recognition = license?.level?.macro_recognition ?? null;
  const frozen = v52h.machineReadLevel(license, incumbent);
  const base = {
    clause: "CLAUSE_3_V52O_BENCHMARKED_ROLE_INSTRUMENT",
    benchmark_role: recognition,
    frozen_v52l_machine_read: frozen,
    selected_target_cents: frozen.target_cents ?? null,
    target_changed: false,
    priors_gate: false,
  };
  if (!recognition || recognition.role === "ABSTAIN") return {
    ...base,
    applicable: false,
    reason: recognition?.status ?? "BENCHMARK_ROLE_ABSENT",
    level_policy: "V52L_DEFAULT_EVIDENCE_BACKED_LEVEL",
  };
  if (recognition.role === "ROLE_UP") return {
    ...base,
    applicable: false,
    reason: "ROLE_UP_IMMEDIATE_EVIDENCE_BACKED_LEVEL_PRESERVED",
    level_policy: "V52L_DEFAULT_EVIDENCE_BACKED_LEVEL_CATCH_EARLY",
  };
  ensure(recognition.role === "ROLE_DOWN", `V52o unexpected role ${recognition.role}`);
  const aggregate = downDepthAggregate(inputs.category);
  const open = recognition.post_formation_open_cents;
  const ask = inputs.book?.ask;
  const cap = pairCap(inputs);
  if (!aggregate || !lawfulCent(open) || !lawfulCent(ask)) return {
    ...base,
    applicable: false,
    reason: "DOWN_AGGREGATE_OR_CAUSAL_OPEN_OR_TOUCH_ABSENT",
    down_depth_row_consumed: aggregate,
    level_policy: "V52L_DEFAULT_EVIDENCE_BACKED_LEVEL",
  };
  const raw = Math.round(open - aggregate.depth_below_open_cents);
  const bounded = Math.min(raw, ask - 1, Number.isInteger(cap) ? cap : 99);
  const applicable = lawfulCent(bounded);
  return {
    ...base,
    applicable,
    reason: applicable ? "ROLE_DOWN_CATEGORY_WEIGHTED_DEPTH_CONSUMED" : "ROLE_DOWN_TARGET_OUTSIDE_LAWFUL_CENT_RANGE",
    level_policy: applicable ? "ROLE_DOWN_FREQUENCY_WEIGHTED_DOWN_SHAPE_DEPTH" : "V52L_DEFAULT_EVIDENCE_BACKED_LEVEL",
    down_depth_row_consumed: aggregate,
    arithmetic: `${open}-${aggregate.depth_below_open_cents}=${open - aggregate.depth_below_open_cents};round=${raw};min(${raw},${ask}-1,${Number.isInteger(cap) ? cap : 99})=${bounded}`,
    causal_open_cents: open,
    current_touch_ask_cents: ask,
    clause_6_cap_cents: Number.isInteger(cap) ? cap : null,
    selected_target_cents: applicable ? bounded : frozen.target_cents ?? null,
    target_changed: applicable && bounded !== frozen.target_cents,
    current_touch_above_bound_applied: true,
    joint_law_bound_applied: Number.isInteger(cap),
    provenance: { taxonomy: v52n.requiredLibrary().taxonomy_provenance, floor_depth_table: v52n.requiredLibrary().floor_table_provenance },
  };
}

function normalizedClauses(value = {}) {
  const clauses = v52n.normalizedClauses(value);
  return value.benchmarked_role_instrument ? { ...clauses, benchmarked_role_instrument: true } : clauses;
}

function adjustedIncumbent(incumbent, selection) {
  const result = {
    ...incumbent,
    target_cents: selection.selected_target_cents,
    placement: { ...(incumbent?.placement ?? {}), target_cents: selection.selected_target_cents, macro_recognition_target_source: "V52O_BENCHMARKED_ROLE_DOWN_AGGREGATE" },
  };
  delete result.unguarded_decision;
  return result;
}

function roleGateDecision(inputs, incumbent) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.benchmarked_role_instrument) return v52n.decide({ ...inputs, clauses });
  const selection = roleDepthSelection(inputs.birthLicense, incumbent, inputs);
  const adjustedLicense = {
    ...inputs.birthLicense,
    level: { ...inputs.birthLicense?.level, proposed_target_cents: selection.selected_target_cents, macro_recognition: selection.benchmark_role, benchmarked_role_instrument: selection },
  };
  const decision = selection.applicable
    ? v52h.gateDecision({ ...inputs, clauses: { ...clauses, macro_recognition: false, recognition_confidence_gate: false, benchmarked_role_instrument: false }, birthLicense: adjustedLicense }, adjustedIncumbent(incumbent, selection))
    : v52h.gateDecision({ ...inputs, clauses: { ...clauses, macro_recognition: false, recognition_confidence_gate: false, benchmarked_role_instrument: false }, birthLicense: adjustedLicense }, incumbent);
  const licensed = decision.judgment_gate?.failure == null && ["PLACE_REST", "REPRICE_REST", "HOLD_REST"].includes(decision.action);
  const consumed = selection.applicable && licensed && decision.target_cents === selection.selected_target_cents;
  const stamped = {
    ...selection,
    candidate_target_differs_from_v52l: selection.target_changed,
    target_changed: consumed && selection.selected_target_cents !== selection.frozen_v52l_machine_read?.target_cents,
    level_policy_consumed: consumed,
    final_licensed_target_cents: decision.target_cents ?? null,
  };
  return v52n.restoreGuardTerminationReceipt({
    ...decision,
    birth_license: decision.birth_license ? { ...decision.birth_license, level: { ...decision.birth_license.level, macro_recognition: selection.benchmark_role, benchmarked_role_instrument: stamped } } : null,
    macro_recognition: selection.benchmark_role,
    benchmarked_role_instrument: stamped,
  }, inputs);
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.benchmarked_role_instrument) return v52n.decideReceipt({ ...inputs, clauses });
  const atomic = v52h.decideReceipt({ ...inputs, clauses: { ...clauses, benchmarked_role_instrument: false, macro_recognition: false, recognition_confidence_gate: false } });
  return { ...atomic, decision: roleGateDecision({ ...inputs, clauses }, atomic.decision.unguarded_decision ?? atomic.decision), benchmarked_role_instrument_enabled: true };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.benchmarked_role_instrument) return v52n.decide({ ...inputs, clauses });
  const incumbent = v52h.decide({ ...inputs, clauses: { ...clauses, benchmarked_role_instrument: false, macro_recognition: false, recognition_confidence_gate: false } });
  return roleGateDecision({ ...inputs, clauses }, incumbent.unguarded_decision ?? incumbent);
}

module.exports = {
  ...v52n,
  BENCHMARK_ROLE_RULE_COMMIT,
  BENCHMARK_ROLE_THRESHOLD_CENTS,
  configureShapeLibrary,
  classifyShapeState,
  benchmarkRuleReceipt,
  downDepthAggregate,
  roleDepthSelection,
  normalizedClauses,
  roleGateDecision,
  decideReceipt,
  decide,
};
