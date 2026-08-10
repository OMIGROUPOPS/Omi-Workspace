"use strict";

// V47 is a pipeline-correctness wrapper around frozen operative V45.  It does
// not change the persistence gate, target, guard, cap, sanity, fill, or edge
// laws.  The join qualification and the placement decision are evaluated as
// one receipt-local operation so no scheduler turn can sit between them.

const v45 = require("./window1_v45_guard_release_sibling_credit.js");

function normalizedClauses(value = {}) {
  return {
    ...v45.normalizedClauses(value),
    same_tick_arm: Boolean(value.same_tick_arm),
  };
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const join = v45.persistenceJoinUpdate({
    state: inputs.state,
    bid: inputs.book?.bid,
    residencySeconds: inputs.residencySeconds,
    currentJoinLevel: inputs.currentJoinLevel,
    clauses,
  });
  const effectiveJoinLevel = join.armed && join.changed
    ? join.level_cents
    : inputs.currentJoinLevel;
  const decision = v45.decide({
    ...inputs,
    persistentJoinLevel: effectiveJoinLevel,
    clauses,
  });
  return {
    join,
    effective_join_level_cents: effectiveJoinLevel,
    decision,
    atomic_receipt: inputs.book?.receipt ?? null,
    same_tick_arm_enabled: clauses.same_tick_arm,
  };
}

module.exports = {
  ...v45,
  normalizedClauses,
  decideReceipt,
};
