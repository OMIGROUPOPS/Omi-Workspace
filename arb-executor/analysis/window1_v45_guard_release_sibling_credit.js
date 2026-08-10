"use strict";

// V45 adds one scoped authority rule to operative V43: once the other
// expression is credited, the pre-fill deep-gap question is settled and may
// no longer withhold this leg's hedge. All target, cap, sanity, state, fill,
// and edge laws remain V43.

const v43 = require("./window1_v43_composed_machine.js");

function normalizedClauses(value = {}) {
  return {
    ...v43.normalizedClauses(value),
    release_guard_on_sibling_credit: Boolean(value.release_guard_on_sibling_credit),
  };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!(clauses.release_guard_on_sibling_credit && inputs.siblingCredited)) {
    return v43.decide({ ...inputs, clauses });
  }
  const incumbent = v43.decide({ ...inputs, clauses: { ...clauses, deep_gap_guard: false } });
  return {
    ...incumbent,
    reason: incumbent.reason,
    guard: null,
    guard_authority: "TERMINATED_AT_SIBLING_CREDIT",
    guard_authority_terminated: true,
  };
}

module.exports = {
  ...v43,
  normalizedClauses,
  decide,
};
