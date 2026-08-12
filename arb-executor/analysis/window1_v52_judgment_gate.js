"use strict";

// V52 is a birth-license gate over frozen V49b.  V49b supplies all incumbent
// walk, guard, cap, and trades-as-truth behavior.  V52 alone decides whether
// a post/repost may be born and names its diary level.

const v49b = require("./window1_v49b_faithful_stand_at_p.js");

function normalizedClauses(value = {}) {
  return {
    ...v49b.normalizedClauses(value),
    judgment_gate: Boolean(value.judgment_gate),
    scavenger: false,
  };
}

function firstFailure(license) {
  if (!license?.onset?.passed) return "STABILITY_ONSET_NOT_REACHED";
  if (!license?.read?.passed) return "NO_TAPE_MACHINE_READ_ABSENT";
  if (!license?.diary?.passed) return "POST_ONSET_TRUE_TRADE_LOW_ABSENT";
  if (!license?.coherence?.lows_under_par) return "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR";
  if (!license?.coherence?.disagreement_clear) return "FIRING_DISAGREEMENT_ACTIVE";
  if (!v49b.lawfulCent(license?.level?.target_cents)) return "NO_LAWFUL_DIARY_POST_LEVEL";
  return null;
}

function gateDecision(inputs, incumbent) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.judgment_gate) return incumbent;
  const license = inputs.birthLicense;
  const failure = firstFailure(license);
  const active = v49b.lawfulCent(inputs.activeTarget) ? inputs.activeTarget : null;

  // Incumbent cancellation/guard behavior remains lawful only after a
  // licensed rest exists.  A guard cannot become an extra pre-birth gate.
  if (active !== null && ["CANCEL_REST"].includes(incumbent.action)) {
    return { ...incumbent, birth_license: license, judgment_gate: { enabled: true, verdict: "INCUMBENT_LICENSED_REST_GUARD", failure: null } };
  }

  if (failure) {
    return {
      action: "HOLD_REST",
      target_cents: active,
      reason: `V52_BIRTH_BLOCKED_${failure}`,
      placement: incumbent.placement ?? null,
      guard: active === null ? null : incumbent.guard ?? null,
      unguarded_decision: incumbent,
      birth_license: license,
      judgment_gate: { enabled: true, verdict: "BLOCKED", failure },
    };
  }

  const target = license.level.target_cents;
  const action = active === null ? "PLACE_REST" : active === target ? "HOLD_REST" : "REPRICE_REST";
  return {
    action,
    target_cents: target,
    ...(action === "REPRICE_REST" ? { direction: target > active ? "UP" : "DOWN" } : {}),
    reason: action === "HOLD_REST" ? "V52_LICENSED_DIARY_LEVEL_ALREADY_STANDING" : "V52_LICENSED_DIARY_LEVEL_POST",
    placement: {
      target_cents: target,
      unbounded_target_cents: license.diary.own_post_onset_true_trade_low_cents,
      authority: "V52_POST_ONSET_TRUE_TRADE_LOW_DIARY",
      displayed_bid_consumed: false,
    },
    guard: active === null ? null : incumbent.guard ?? null,
    unguarded_decision: incumbent,
    birth_license: license,
    judgment_gate: { enabled: true, verdict: action === "HOLD_REST" ? "LICENSED_HOLD" : "POST", failure: null },
  };
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const atomic = v49b.decideReceipt({ ...inputs, clauses });
  return { ...atomic, decision: gateDecision({ ...inputs, clauses }, atomic.decision), judgment_gate_enabled: clauses.judgment_gate };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  return gateDecision({ ...inputs, clauses }, v49b.decide({ ...inputs, clauses }));
}

module.exports = { ...v49b, normalizedClauses, firstFailure, gateDecision, decideReceipt, decide };
