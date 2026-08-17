"use strict";

// V52m changes one capability over the adopted V52l/V52h decision stack:
// clause 3 may consume a causally recognized shape-family depth target.  The
// classifier sees only true prints already processed at the evaluation
// receipt.  It never reads a right edge, a completed path, or ex-post floors.

const v52h = require("./window1_v52h_remove_pair_lows_precondition.js");

const SAMPLE_POINTS = 17;
const FAMILY_ORDER = [
  "SLEEPER", "ROUND_TRIP", "QUIET_WOBBLE", "LATE_BREAK_DOWN",
  "LATE_BREAK_UP", "EARLY_SET_DOWN", "EARLY_SET_UP", "ONE_STEP_DOWN",
  "ONE_STEP_UP", "GRIND_WOBBLE_DOWN", "GRIND_WOBBLE_UP", "DRIFT_DOWN",
  "DRIFT_UP",
];
const DIRECTIONAL_FAMILIES = new Set(FAMILY_ORDER.filter((family) => family.endsWith("_DOWN") || family.endsWith("_UP")));
const ABSTAIN_FAMILIES = new Set(["SLEEPER", "GRIND_WOBBLE_DOWN", "GRIND_WOBBLE_UP"]);

let library = null;

function ensure(value, message) { if (!value) throw new Error(message); }
function finite(value) { return Number.isFinite(value); }
function lawfulCent(value) { return Number.isInteger(value) && value >= 1 && value <= 99; }

function parsePercent(value) {
  if (typeof value !== "string" || !value.endsWith("%")) return null;
  const parsed = Number(value.slice(0, -1));
  return finite(parsed) ? parsed / 100 : null;
}

function configureShapeLibrary(value) {
  ensure(value?.taxonomy?.LABEL === "SHAPE_TAXONOMY_BUILD1", "V52m taxonomy label mismatch");
  ensure(value?.floor_tables?.LABEL === "PER_SHAPE_FLOOR_DEPTH_TABLES", "V52m floor table label mismatch");
  ensure(value?.taxonomy_provenance?.commit === "e269779b0ec025d55f67d576e3cfb0cb575d5890", "V52m taxonomy commit mismatch");
  ensure(value?.floor_table_provenance?.commit === "8ab4f2d9e8c831235dc7cb4570c88daa3caded50", "V52m floor-table commit mismatch");
  const taxonomyFamilies = new Set(Object.keys(value.taxonomy.families || {}));
  ensure(FAMILY_ORDER.every((family) => taxonomyFamilies.has(family)), "V52m taxonomy does not contain all 13 families");
  const rows = value.floor_tables.rows || [];
  ensure(rows.length === 52 && rows.every((row) => FAMILY_ORDER.includes(row.family)), "V52m floor table row conservation failed");
  const confidenceByFamily = Object.fromEntries(FAMILY_ORDER.map((family) => [family, parsePercent(value.taxonomy.benchmark?.by_family_acc?.[family]) ]));
  library = { ...value, rows, confidenceByFamily };
  return { configured: true, families: FAMILY_ORDER.length, rows: rows.length };
}

function requiredLibrary() { ensure(library, "V52m shape library not configured"); return library; }

function emptyShapeState() { return { prints: [] }; }

function observeTruePrint(state, row) {
  ensure(state?.prints && row?.kind === "PRINT", "V52m true-print state input invalid");
  ensure(finite(row.ts) && lawfulCent(row.price) && typeof row.receipt === "string", "V52m true-print receipt invalid");
  const prior = state.prints.at(-1);
  ensure(!prior || row.ts > prior.timestamp_epoch || (row.ts === prior.timestamp_epoch && row.ordinal >= prior.ordinal), "V52m print state not chronological");
  state.prints.push({ timestamp_epoch: row.ts, ordinal: row.ordinal, price_cents: row.price, receipt: row.receipt, trade_id: row.trade_id ?? null });
}

function sampleCausalPath(state, evaluationTimestampEpoch) {
  const prints = state.prints.filter((row) => row.timestamp_epoch <= evaluationTimestampEpoch);
  if (!prints.length) return null;
  const start = prints[0].timestamp_epoch;
  const duration = Math.max(0, evaluationTimestampEpoch - start);
  const points = [];
  let cursor = 0;
  for (let index = 0; index < SAMPLE_POINTS; index += 1) {
    const timestamp = start + duration * index / (SAMPLE_POINTS - 1);
    while (cursor + 1 < prints.length && prints[cursor + 1].timestamp_epoch <= timestamp) cursor += 1;
    points.push(prints[cursor].price_cents);
  }
  return { prints, points, start_timestamp_epoch: start, evaluation_timestamp_epoch: evaluationTimestampEpoch };
}

function sign(value) { return value > 0 ? 1 : value < 0 ? -1 : 0; }

function signatureFromPath(sampled) {
  const path = sampled.points;
  const steps = path.slice(1).map((value, index) => value - path[index]);
  const nonzeroSigns = steps.map(sign).filter(Boolean);
  let reversals = 0;
  for (let index = 1; index < nonzeroSigns.length; index += 1) if (nonzeroSigns[index] !== nonzeroSigns[index - 1]) reversals += 1;
  const open = path[0], terminal = path.at(-1), net = terminal - open;
  const travel = Math.max(...path) - Math.min(...path);
  const maxStep = Math.max(0, ...steps.map(Math.abs));
  const earlyNet = path[4] - open;
  const lateNet = terminal - path[12];
  const postQ1MaxDeviation = Math.max(...path.slice(4).map((value) => Math.abs(value - path[4])));
  return {
    sample_points: SAMPLE_POINTS,
    open_cents: open,
    terminal_cents: terminal,
    net_cents: net,
    travel_cents: travel,
    max_step_cents: maxStep,
    big_step_share_of_abs_net: Math.abs(net) ? maxStep / Math.abs(net) : null,
    first_quarter_net_cents: earlyNet,
    last_quarter_net_cents: lateNet,
    post_first_quarter_max_deviation_cents: postQ1MaxDeviation,
    reversal_count: reversals,
    true_print_count: sampled.prints.length,
    first_true_print_receipt: sampled.prints[0].receipt,
    last_true_print_receipt: sampled.prints.at(-1).receipt,
    maximum_consumed_timestamp_epoch: sampled.prints.at(-1).timestamp_epoch,
  };
}

function familyFromSignature(signature) {
  const { true_print_count: n, travel_cents: travel, net_cents: net, first_quarter_net_cents: early, last_quarter_net_cents: late, max_step_cents: maxStep, reversal_count: reversals, post_first_quarter_max_deviation_cents: postQ1Deviation } = signature;
  if (n < 3 || travel < 3) return "SLEEPER";
  if (Math.abs(net) < 5) return travel >= 10 ? "ROUND_TRIP" : "QUIET_WOBBLE";
  const direction = net < 0 ? "DOWN" : "UP";
  if (sign(late) === sign(net) && Math.abs(late) >= 0.7 * Math.abs(net)) return `LATE_BREAK_${direction}`;
  if (sign(early) === sign(net) && Math.abs(early) >= 0.7 * Math.abs(net) && postQ1Deviation <= 0.3 * Math.abs(net)) return `EARLY_SET_${direction}`;
  if (maxStep >= 0.6 * Math.abs(net)) return `ONE_STEP_${direction}`;
  if (reversals >= 4 && travel >= 2 * Math.abs(net)) return `GRIND_WOBBLE_${direction}`;
  return `DRIFT_${direction}`;
}

function classifyShapeState(state, evaluation = {}) {
  const configured = requiredLibrary();
  const timestamp = evaluation.timestamp_epoch;
  ensure(finite(timestamp), "V52m evaluation timestamp absent");
  const sampled = sampleCausalPath(state, timestamp);
  if (!sampled) return {
    status: "ABSTAIN_NO_TRUE_PRINT",
    family: null,
    confidence: null,
    signable: false,
    evaluation_timestamp_epoch: timestamp,
    evaluation_receipt: evaluation.receipt ?? null,
    maximum_consumed_timestamp_epoch: null,
    causal: true,
    right_edge_consumed: false,
    full_span_fit: false,
    taxonomy_provenance: configured.taxonomy_provenance,
  };
  const signature = signatureFromPath(sampled);
  const family = familyFromSignature(signature);
  const confidence = configured.confidenceByFamily[family];
  const signable = !ABSTAIN_FAMILIES.has(family) && finite(confidence);
  return {
    status: signable ? "CLASSIFIED_SIGNABLE" : "CLASSIFIED_ABSTAIN_FAMILY",
    family,
    confidence,
    signable,
    abstain_reason: signable ? null : "FAMILY_HAS_NO_PINNED_EARLY_CALL_ACCURACY_AUTHORITY",
    evaluation_timestamp_epoch: timestamp,
    evaluation_receipt: evaluation.receipt ?? null,
    signature,
    sampled_path_cents: sampled.points,
    maximum_consumed_timestamp_epoch: signature.maximum_consumed_timestamp_epoch,
    causal: true,
    right_edge_consumed: false,
    full_span_fit: false,
    taxonomy_provenance: configured.taxonomy_provenance,
  };
}

function tableRowFor(family, category) {
  const configured = requiredLibrary();
  const exact = configured.rows.find((row) => row.family === family && row.category === category);
  const parent = configured.rows.find((row) => row.family === family && row.category === "ALL");
  return exact ? { row: exact, borrowed_from: null } : parent ? { row: parent, borrowed_from: `${family}|ALL` } : null;
}

function pairCap(inputs) {
  const counterpart = inputs?.siblingCredited === true ? inputs.siblingEntryCents : inputs?.siblingStandingTarget;
  return Number.isInteger(counterpart) ? 99 - counterpart : null;
}

function floorDepthSelection(license, incumbent, inputs = {}) {
  const configured = requiredLibrary();
  const recognition = license?.level?.macro_recognition ?? null;
  const frozen = v52h.machineReadLevel(license, incumbent);
  if (!recognition?.signable || !recognition.family) return {
    clause: "CLAUSE_3_V52M_MACRO_RECOGNITION",
    applicable: false,
    reason: recognition?.status ?? "MACRO_RECOGNITION_ABSENT",
    macro_recognition: recognition,
    frozen_machine_read: frozen,
    selected_target_cents: frozen.target_cents ?? null,
    target_changed: false,
  };
  const binding = tableRowFor(recognition.family, inputs.category);
  const depth = binding?.row?.depth_below_open_c?.med;
  const open = recognition.signature?.open_cents;
  const ask = inputs.book?.ask;
  const cap = pairCap(inputs);
  if (!binding || !finite(depth) || !lawfulCent(open) || !lawfulCent(ask)) return {
    clause: "CLAUSE_3_V52M_MACRO_RECOGNITION",
    applicable: false,
    reason: "SHAPE_TABLE_ROW_OR_CAUSAL_OPEN_OR_TOUCH_ABSENT",
    macro_recognition: recognition,
    table_binding: binding,
    frozen_machine_read: frozen,
    selected_target_cents: frozen.target_cents ?? null,
    target_changed: false,
  };
  const rawTarget = Math.round(open - depth);
  const boundedTarget = Math.min(rawTarget, ask - 1, Number.isInteger(cap) ? cap : 99);
  const applicable = lawfulCent(boundedTarget);
  return {
    clause: "CLAUSE_3_V52M_MACRO_RECOGNITION",
    applicable,
    reason: applicable ? "CAUSAL_FAMILY_DEPTH_TARGET_CONSUMED" : "FAMILY_TARGET_OUTSIDE_LAWFUL_CENT_RANGE",
    macro_recognition: recognition,
    confidence: recognition.confidence,
    table_row: binding.row,
    table_borrowed_from: binding.borrowed_from,
    provenance: {
      taxonomy: configured.taxonomy_provenance,
      floor_depth_table: configured.floor_table_provenance,
    },
    arithmetic: `${open}-${depth}=${rawTarget};min(${rawTarget},${ask}-1,${Number.isInteger(cap) ? cap : 99})=${boundedTarget}`,
    causal_open_cents: open,
    median_depth_below_open_cents: depth,
    raw_family_target_cents: rawTarget,
    current_touch_ask_cents: ask,
    clause_6_cap_cents: Number.isInteger(cap) ? cap : null,
    selected_target_cents: applicable ? boundedTarget : frozen.target_cents ?? null,
    frozen_machine_read: frozen,
    target_changed: applicable && boundedTarget !== frozen.target_cents,
    current_touch_above_bound_applied: true,
    joint_law_bound_applied: Number.isInteger(cap),
    priors_gate: false,
  };
}

function normalizedClauses(value = {}) {
  const clauses = v52h.normalizedClauses(value);
  return value.macro_recognition ? { ...clauses, macro_recognition: true } : clauses;
}

function incumbentWithSelectedTarget(incumbent, selection) {
  const adjusted = {
    ...incumbent,
    target_cents: selection.selected_target_cents,
    placement: {
      ...(incumbent?.placement ?? {}),
      target_cents: selection.selected_target_cents,
      macro_recognition_target_source: "V52M_CAUSAL_SHAPE_FLOOR_DEPTH_TABLE",
    },
  };
  // Every inherited level reader intentionally follows an unguarded decision
  // first.  Once V52m has lawfully replaced the level, retaining that pointer
  // would silently resurrect V52l's target and make this organ decorative.
  delete adjusted.unguarded_decision;
  return adjusted;
}

function gateDecision(inputs, incumbent) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.macro_recognition) return v52h.gateDecision({ ...inputs, clauses }, incumbent);
  const selection = floorDepthSelection(inputs.birthLicense, incumbent, inputs);
  if (!selection.applicable) {
    const frozen = v52h.gateDecision({ ...inputs, clauses: { ...clauses, macro_recognition: false } }, incumbent);
    const stamped = { ...selection, final_licensed_target_cents: frozen.target_cents ?? null };
    return {
      ...frozen,
      birth_license: frozen.birth_license ? { ...frozen.birth_license, level: { ...frozen.birth_license.level, macro_recognition: selection.macro_recognition, per_shape_floor_depth: stamped } } : null,
      macro_recognition: selection.macro_recognition,
      per_shape_floor_depth: stamped,
    };
  }
  const adjustedLicense = {
    ...inputs.birthLicense,
    level: { ...inputs.birthLicense?.level, proposed_target_cents: selection.selected_target_cents, macro_recognition: selection.macro_recognition, per_shape_floor_depth: selection },
  };
  const adjustedIncumbent = incumbentWithSelectedTarget(incumbent, selection);
  const decision = v52h.gateDecision({ ...inputs, clauses: { ...clauses, macro_recognition: false }, birthLicense: adjustedLicense }, adjustedIncumbent);
  const licensed = decision.judgment_gate?.failure == null && ["PLACE_REST", "REPRICE_REST", "HOLD_REST"].includes(decision.action);
  const consumed = licensed && decision.target_cents === selection.selected_target_cents;
  const stamped = {
    ...selection,
    candidate_target_differs_from_frozen: selection.target_changed,
    target_changed: consumed && selection.selected_target_cents !== selection.frozen_machine_read?.target_cents,
    level_policy_consumed: consumed,
    final_licensed_target_cents: decision.target_cents ?? null,
  };
  return {
    ...decision,
    birth_license: decision.birth_license ? { ...decision.birth_license, level: { ...decision.birth_license.level, macro_recognition: selection.macro_recognition, per_shape_floor_depth: stamped } } : null,
    macro_recognition: selection.macro_recognition,
    per_shape_floor_depth: stamped,
  };
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const atomic = v52h.decideReceipt({ ...inputs, clauses: { ...clauses, macro_recognition: false } });
  return { ...atomic, decision: gateDecision({ ...inputs, clauses }, atomic.decision.unguarded_decision ?? atomic.decision), macro_recognition_enabled: Boolean(clauses.macro_recognition) };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const incumbent = v52h.decide({ ...inputs, clauses: { ...clauses, macro_recognition: false } });
  return gateDecision({ ...inputs, clauses }, incumbent.unguarded_decision ?? incumbent);
}

module.exports = {
  ...v52h,
  SAMPLE_POINTS,
  FAMILY_ORDER,
  DIRECTIONAL_FAMILIES,
  ABSTAIN_FAMILIES,
  configureShapeLibrary,
  requiredLibrary,
  emptyShapeState,
  observeTruePrint,
  sampleCausalPath,
  signatureFromPath,
  familyFromSignature,
  classifyShapeState,
  tableRowFor,
  pairCap,
  floorDepthSelection,
  normalizedClauses,
  incumbentWithSelectedTarget,
  gateDecision,
  decideReceipt,
  decide,
};
