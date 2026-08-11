"use strict";

// V49 changes one V47 placement choice.  The universal V43 +1-cent loosen is
// removed.  A tracking rest may instead stand at the current best bid P only
// after this leg's own tape has causally named P: either a strictly earlier
// true trade printed at-or-below P, or the own best bid continuously stood at
// that exact level for V47's already-frozen 300-second persistence interval.
// A historical sighting is not "standing" evidence.  Joins, WTA holds, guards, caps, post-only sanity,
// same-receipt arming, credit laws, and the hard edge remain V47.

const v47 = require("./window1_v47_same_tick_arm.js");

function normalizedClauses(value = {}) {
  return {
    ...v47.normalizedClauses(value),
    evidenced_level_standing: Boolean(value.evidenced_level_standing),
    trades_as_truth: Boolean(value.trades_as_truth),
  };
}

function evidencedLevel(inputs) {
  const p = inputs.book?.bid;
  if (!v47.lawfulCent(p)) return { evidenced: false, level_cents: null, sources: [] };
  const sources = [];
  if (v47.lawfulCent(inputs.priorTrueTradeLow) && inputs.priorTrueTradeLow <= p) {
    sources.push({ source: "PRIOR_TRUE_TRADE_AT_OR_BELOW_P", price_cents: inputs.priorTrueTradeLow, receipt: inputs.priorTrueTradeLowReceipt ?? null });
  }
  if (
    inputs.priorExactBidEvidence?.level_cents === p
    && Number.isFinite(inputs.residencySeconds)
    && inputs.residencySeconds >= v47.PERSISTENT_LEVEL_SECONDS
  ) {
    sources.push({
      source: "OWN_BEST_BID_P_CONTINUOUSLY_STANDING",
      price_cents: p,
      receipt: inputs.priorExactBidEvidence.receipt ?? null,
      timestamp_epoch: inputs.priorExactBidEvidence.timestamp_epoch ?? null,
      residency_seconds: inputs.residencySeconds,
      inherited_persistence_seconds: v47.PERSISTENT_LEVEL_SECONDS,
    });
  }
  return { evidenced: sources.length > 0, level_cents: p, sources };
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.evidenced_level_standing) {
    const incumbent = v47.decideReceipt({ ...inputs, clauses });
    return { ...incumbent, evidence: { evidenced: false, level_cents: null, sources: [] }, evidenced_level_standing_enabled: false, universal_loosen_enabled: clauses.loosen_one_cent, raised_to_evidenced_level: false, next_evidenced_standing_level_cents: inputs.evidencedStandingLevel ?? null };
  }
  const evidence = evidencedLevel(inputs);
  const levels = [inputs.evidencedStandingLevel, evidence.evidenced ? evidence.level_cents : null].filter(v47.lawfulCent);
  const standingLevel = levels.length ? Math.max(...levels) : null;
  const standingEvidence = evidence.evidenced && evidence.level_cents === standingLevel
    ? evidence
    : inputs.evidencedStandingAuthority ?? evidence;
  // Compute the incumbent atomic join on the real current book first.  The
  // standing level can then affect only the placement target; it cannot arm or
  // rewrite a join, state read, or sibling rule.
  const atomic = v47.decideReceipt({ ...inputs, clauses: { ...clauses, loosen_one_cent: false } });
  const trackerAuthorities = new Set([
    "V41_V36_FALLING_NO_CHASE",
    "V41_V36_SETTLED_BID_MINUS_ONE_TRACKER",
    "V41_RISING_TRACKER_UNTIL_PERSISTENT_JOIN_ARMS",
    "V41_WTA_HOLD_ABSTAINS_TO_INCUMBENT_TRACKER",
  ]);
  let decision = atomic.decision;
  if (v47.lawfulCent(standingLevel) && trackerAuthorities.has(decision.placement?.authority)) {
    decision = v47.decide({
      ...inputs,
      book: { ...inputs.book, bid: standingLevel },
      persistentJoinLevel: atomic.effective_join_level_cents,
      clauses: { ...clauses, loosen_one_cent: true },
    });
  }
  const boundedStanding = v47.lawfulCent(standingLevel) ? v47.postOnlyBound(standingLevel, inputs.book, inputs.pairCap) : null;
  const raisedToEvidence = Boolean(
    v47.lawfulCent(standingLevel)
    && decision.target_cents === boundedStanding
    && boundedStanding === standingLevel
    && trackerAuthorities.has(decision.placement?.V41_placement?.authority ?? decision.placement?.authority)
  );
  return {
    ...atomic,
    decision,
    evidence: standingEvidence,
    evidenced_level_standing_enabled: true,
    universal_loosen_enabled: false,
    raised_to_evidenced_level: raisedToEvidence,
    next_evidenced_standing_level_cents: standingLevel,
    next_evidenced_standing_authority: standingEvidence,
  };
}

function tradeTruthCredit(order, print) {
  return Boolean(order)
    && v47.lawfulCent(order.target_cents)
    && print?.kind === "PRINT"
    && Number.isFinite(print.ts)
    && print.ts > order.action_ts
    && typeof print.trade_id === "string"
    && print.trade_id.length > 0
    && Number.isInteger(print.price)
    && print.price <= order.target_cents;
}

module.exports = {
  ...v47,
  normalizedClauses,
  evidencedLevel,
  decideReceipt,
  tradeTruthCredit,
};
