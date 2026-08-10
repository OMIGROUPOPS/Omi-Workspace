"use strict";

// V46 adds one receipt-local credit source to operative V45.  A >=3-cent
// single-receipt ask gap may move a FALLING rest down to one cent below the
// new ask only after the sibling is already credited.  Without sibling
// credit, V45 remains byte-for-byte authoritative.

const v45 = require("./window1_v45_guard_release_sibling_credit.js");

const ASK_GAP_CREDIT_MIN_CENTS = 3;

function normalizedClauses(value = {}) {
  return {
    ...v45.normalizedClauses(value),
    pair_gated_gap_credit: Boolean(value.pair_gated_gap_credit),
  };
}

function gapCreditTarget({ book, pairCap = null }) {
  if (!Number.isInteger(book?.ask)) return null;
  let target = book.ask - 1;
  if (Number.isInteger(pairCap)) target = Math.min(target, pairCap);
  return v45.lawfulCent(target) ? target : null;
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const incumbent = v45.decide({ ...inputs, clauses });
  const gap = Number(inputs.askGapCents);
  const eligible = clauses.pair_gated_gap_credit &&
    inputs.state === "FALLING" &&
    Number.isFinite(gap) && gap >= ASK_GAP_CREDIT_MIN_CENTS &&
    v45.lawfulCent(inputs.activeTarget);
  if (!eligible) return incumbent;
  if (!inputs.siblingCredited) {
    return {
      ...incumbent,
      gap_credit: {
        eligible: true,
        authorized: false,
        reason: "V46_GAP_CREDIT_REFUSED_SIBLING_NOT_CREDITED",
        ask_gap_cents: gap,
      },
    };
  }
  const target = gapCreditTarget(inputs);
  if (!v45.lawfulCent(target) || target >= inputs.activeTarget) {
    return {
      ...incumbent,
      gap_credit: {
        eligible: true,
        authorized: false,
        reason: "V46_GAP_CREDIT_NO_LAWFUL_REPRICE_DOWN",
        ask_gap_cents: gap,
        candidate_target_cents: target,
      },
    };
  }
  return {
    ...incumbent,
    action: "REPRICE_REST",
    target_cents: target,
    direction: "DOWN",
    reason: "V46_PAIR_GATED_SINGLE_TICK_ASK_GAP_CREDIT_REPRICE_DOWN",
    gap_credit: {
      eligible: true,
      authorized: true,
      reason: "OTHER_EXPRESSION_ALREADY_CREDITED_HEDGE_COMPLETION_ONLY",
      ask_gap_cents: gap,
      prior_ask_cents: inputs.priorAsk,
      current_ask_cents: inputs.book.ask,
      candidate_target_cents: target,
      pair_cap_cents: inputs.pairCap,
      sibling_entry_cents: inputs.siblingEntryCents,
    },
  };
}

module.exports = {
  ...v45,
  ASK_GAP_CREDIT_MIN_CENTS,
  normalizedClauses,
  gapCreditTarget,
  decide,
};
