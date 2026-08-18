"use strict";

const v52o = require("./window1_v52o_benchmarked_role_instrument.js");

const RIPENESS_COMMIT = "41c1f724";
const CLASS_GATES = Object.freeze({ ROLE_UP: 0.023, ROLE_DOWN: 0.448, ROLE_STILL: 0.650 });
const CATEGORY_GATES = Object.freeze({ WTA_MAIN: 0.206, ATP_MAIN: 0.351, ATP_CHALL: 0.703, WTA_CHALL: 0.964 });
let ripenessBinding = null;

function ensure(value, message) { if (!value) throw new Error(message); }
function configureRipeness(value) {
  ensure(value?.artifact?.LABEL === "RECOGNITION_OPERATING_POINT_RECONCILIATION", "V52p ripeness label mismatch");
  const rows = new Map(value.artifact.ripeness.map((row) => [row.class, row.ripe_f]));
  const expected = { UP_SHAPES: 0.023, DOWN_SHAPES: 0.448, STILL_SHAPES: 0.650, WTA_MAIN: 0.206, ATP_MAIN: 0.351, ATP_CHALL: 0.703, WTA_CHALL: 0.964 };
  for (const [key, gate] of Object.entries(expected)) ensure(rows.get(key) === gate, `V52p ripeness value mismatch ${key}`);
  ensure(value.provenance?.commit?.startsWith(RIPENESS_COMMIT), "V52p ripeness commit mismatch");
  ripenessBinding = value;
  return { bound: true, class_gates: CLASS_GATES, category_gates: CATEGORY_GATES };
}
function requiredRipeness() { ensure(ripenessBinding, "V52p ripeness not configured"); return ripenessBinding; }
function fraction(timestamp, start, end) { return Number.isFinite(timestamp) && Number.isFinite(start) && Number.isFinite(end) && end > start ? (timestamp - start) / (end - start) : null; }

function classifyShapeState(state, evaluation = {}) {
  if (evaluation.ripeness_role_binding_enabled !== true) return v52o.classifyShapeState(state, evaluation);
  const raw = v52o.classifyShapeState(state, { ...evaluation, role_instrument_enabled: true });
  const candidateRole = raw.drift_cents === null ? null : raw.drift_cents >= 2 ? "ROLE_UP" : raw.drift_cents <= -2 ? "ROLE_DOWN" : "ROLE_STILL";
  const classGate = candidateRole ? CLASS_GATES[candidateRole] : null;
  const categoryGate = CATEGORY_GATES[evaluation.category] ?? null;
  ensure(categoryGate !== null, `V52p category gate absent ${evaluation.category}`);
  const effectiveGate = candidateRole ? Math.max(classGate, categoryGate) : null;
  const verifiedF = fraction(evaluation.timestamp_epoch, evaluation.formation_end_epoch, evaluation.verified_span_end_epoch);
  const scheduledF = fraction(evaluation.timestamp_epoch, evaluation.formation_end_epoch, evaluation.scheduled_span_end_epoch);
  const verifiedPass = candidateRole !== null && Number.isFinite(verifiedF) && verifiedF >= effectiveGate;
  const scheduledPass = candidateRole !== null && Number.isFinite(scheduledF) && scheduledF >= effectiveGate;
  const boundRole = verifiedPass ? candidateRole : null;
  return {
    ...raw,
    status: candidateRole === null ? "ABSTAIN_NO_POST_FORMATION_TRUE_PRINT" : verifiedPass ? `RIPENESS_BOUND_${candidateRole}` : "ABSTAIN_BELOW_EFFECTIVE_RIPENESS_GATE",
    role: boundRole === "ROLE_DOWN" ? "ROLE_DOWN" : boundRole === "ROLE_UP" ? "ROLE_UP" : "ABSTAIN",
    bound_role: boundRole,
    candidate_role: candidateRole,
    signable: boundRole !== null,
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
      source: requiredRipeness().provenance,
      new_constants: 0,
    },
  };
}

function normalizedClauses(value = {}) {
  const clauses = v52o.normalizedClauses(value);
  return value.ripeness_role_binding ? { ...clauses, benchmarked_role_instrument: true, ripeness_role_binding: true } : clauses;
}

module.exports = { ...v52o, RIPENESS_COMMIT, CLASS_GATES, CATEGORY_GATES, configureRipeness, requiredRipeness, fraction, classifyShapeState, normalizedClauses };
