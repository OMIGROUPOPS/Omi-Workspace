"use strict";

// V52n changes exactly one clause over frozen V52m: a proposed causal family
// may bind clause 3 only after it clears that family's pinned early-call
// identifiability gate.  A failed gate is an abstention, so the inherited V52l
// evidence-backed level remains authoritative.  Classification is retried on
// every receipt by the replay loop; no timer or right edge is consumed here.

const v52m = require("./window1_v52m_macro_recognition.js");

// Both values are source-schema facts, not fitted here: the floor-depth table
// measures declaration at f=.25/.5 and defines a directional declaration as a
// 2-cent drift from open.  Requiring median declaration by the table's last
// early checkpoint is the table's own early-identifiability partition.
const PINNED_EARLY_CHECKPOINT_F = 0.5;
const PINNED_DIRECTIONAL_DECLARATION_CENTS = 2;

function finite(value) { return Number.isFinite(value); }

function earlyCallRow(family, category) {
  const binding = v52m.tableRowFor(family, category);
  return binding ? { ...binding, early_call: binding.row?.early_call ?? null } : null;
}

function confidenceGate(recognition, category) {
  const family = recognition?.family ?? null;
  const binding = family ? earlyCallRow(family, category) : null;
  const early = binding?.early_call ?? null;
  const net = recognition?.signature?.net_cents;
  const expectedSign = family?.endsWith("_DOWN") ? -1 : family?.endsWith("_UP") ? 1 : 0;
  const observedSignedDrift = finite(net) && expectedSign !== 0 ? expectedSign * net : null;
  const directional = early?.kind === "DIRECTIONAL" && expectedSign !== 0;
  const confidencePresent = finite(recognition?.confidence);
  const medianDeclarationByPinnedCheckpoint = directional
    && finite(early?.median_declare_f)
    && early.median_declare_f <= PINNED_EARLY_CHECKPOINT_F;
  const receiptHasPinnedDeclaration = directional
    && finite(observedSignedDrift)
    && observedSignedDrift >= PINNED_DIRECTIONAL_DECLARATION_CENTS;
  const passed = recognition?.signable === true
    && confidencePresent
    && medianDeclarationByPinnedCheckpoint
    && receiptHasPinnedDeclaration;
  return {
    passed,
    verdict: passed ? "BIND" : "ABSTAIN",
    proposed_family: family,
    taxonomy_family_accuracy_confidence: recognition?.confidence ?? null,
    gate: {
      source: "PER_SHAPE_FLOOR_DEPTH_TABLES.early_call",
      kind: early?.kind ?? null,
      pinned_early_checkpoint_f: PINNED_EARLY_CHECKPOINT_F,
      median_declare_f: early?.median_declare_f ?? null,
      declared_by_f025_pct: early?.declared_by_f025_pct ?? null,
      declared_by_f05_pct: early?.declared_by_f05_pct ?? null,
      still_within_2c_at_f025_pct: early?.still_within_2c_at_f025_pct ?? null,
      still_at_f05_pct: early?.still_at_f05_pct ?? null,
      required_directional_drift_cents: PINNED_DIRECTIONAL_DECLARATION_CENTS,
      observed_signed_directional_drift_cents: observedSignedDrift,
      confidence_present: confidencePresent,
      directional_family: directional,
      median_declaration_by_pinned_checkpoint: medianDeclarationByPinnedCheckpoint,
      receipt_has_pinned_directional_declaration: receiptHasPinnedDeclaration,
    },
    table_row_identity: binding ? `${binding.row.family}|${binding.row.category}` : null,
    borrowed_from: binding?.borrowed_from ?? null,
    reason: passed
      ? "PINNED_PER_FAMILY_EARLY_CALL_GATE_MET"
      : recognition?.signable !== true
        ? (recognition?.abstain_reason ?? recognition?.status ?? "V52M_CLASSIFICATION_NOT_SIGNABLE")
        : !directional
          ? "FAMILY_NOT_DIRECTIONALLY_IDENTIFIABLE_EARLY"
          : !medianDeclarationByPinnedCheckpoint
            ? "FAMILY_MEDIAN_DECLARATION_AFTER_PINNED_F05_CHECKPOINT"
            : !receiptHasPinnedDeclaration
              ? "RECEIPT_HAS_NOT_REACHED_PINNED_2C_DECLARATION"
              : "PINNED_FAMILY_CONFIDENCE_ABSENT",
  };
}

function classifyShapeState(state, evaluation = {}) {
  const proposed = v52m.classifyShapeState(state, evaluation);
  if (evaluation.confidence_gate_enabled !== true) return proposed;
  const gate = confidenceGate(proposed, evaluation.category);
  return {
    ...proposed,
    proposed_family: proposed.family,
    binding_family: gate.passed ? proposed.family : null,
    signable: gate.passed,
    classification_class: gate.passed ? "BOUND_FAMILY" : "ABSTAIN",
    status: gate.passed ? "CLASSIFIED_SIGNABLE_CONFIDENCE_GATE_MET" : "CLASSIFIED_ABSTAIN_BELOW_PINNED_EARLY_CALL_GATE",
    abstain_reason: gate.passed ? null : gate.reason,
    recognition_confidence_gate: gate,
  };
}

// Later inherited wrappers can retain guard=null while dropping V45's
// guard_authority_terminated receipt bit. Restore that receipt-only invariant;
// action, target, predicates, and all order-state behavior are untouched.
function restoreGuardTerminationReceipt(decision, inputs = {}) {
  const clauses = v52m.normalizedClauses(inputs.clauses ?? {});
  if (clauses.release_guard_on_sibling_credit && inputs.siblingCredited === true && decision?.guard === null && decision.guard_authority_terminated !== true) {
    return {
      ...decision,
      guard_authority: "TERMINATED_AT_SIBLING_CREDIT",
      guard_authority_terminated: true,
      receipt_only_inherited_guard_stamp_repair: true,
    };
  }
  return decision;
}

function decide(inputs) {
  return restoreGuardTerminationReceipt(v52m.decide(inputs), inputs);
}

module.exports = {
  ...v52m,
  PINNED_EARLY_CHECKPOINT_F,
  PINNED_DIRECTIONAL_DECLARATION_CENTS,
  earlyCallRow,
  confidenceGate,
  classifyShapeState,
  restoreGuardTerminationReceipt,
  decide,
};
