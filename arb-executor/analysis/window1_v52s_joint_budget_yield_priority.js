"use strict";

// V52s is a receipt-local allocation rule.  Incumbent V52l targets are
// senior.  A depth lift may consume only the residual of the 99-cent pair
// budget and therefore yields before either incumbent target can move.

const MARKET_TICK_CENTS = 1;
const PAIR_BUDGET_CENTS = 99;

function lawfulCent(value) {
  return Number.isInteger(value) && value >= 1 && value <= 99;
}

function sideDefault(side) {
  if (side.state === "BOUGHT_SIDE") return side.entry_cents;
  if (side.state === "STANDING_SIDE") return side.default_target_cents;
  return null;
}

function desiredDepthTarget(side) {
  if (side.state !== "STANDING_SIDE" || !lawfulCent(side.default_target_cents)
      || !lawfulCent(side.post_onset_session_low_cents)) return null;
  const bounds = [side.post_onset_session_low_cents + MARKET_TICK_CENTS];
  if (lawfulCent(side.best_ask_cents)) bounds.push(side.best_ask_cents - MARKET_TICK_CENTS);
  if (lawfulCent(side.pair_cap_cents)) bounds.push(side.pair_cap_cents);
  const desired = Math.min(...bounds);
  return lawfulCent(desired) && desired > side.default_target_cents ? desired : null;
}

function allocate(sides, { allow_lifts = true } = {}) {
  if (!Array.isArray(sides) || sides.length !== 2) throw new Error("V52s requires exactly two sides");
  const ordered = sides.map((side) => ({ ...side })).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity));
  const defaults = ordered.map(sideDefault);
  const defaultsKnown = defaults.every(Number.isInteger);
  const defaultSum = defaultsKnown ? defaults[0] + defaults[1] : null;
  if (Number.isInteger(defaultSum) && defaultSum > PAIR_BUDGET_CENTS) {
    throw new Error(`V52s senior target invariant violated: ${defaultSum}`);
  }
  let slack = Number.isInteger(defaultSum) ? PAIR_BUDGET_CENTS - defaultSum : null;
  const allocations = [];
  for (const side of ordered) {
    const defaultTarget = sideDefault(side);
    const desired = allow_lifts ? desiredDepthTarget(side) : null;
    let target = defaultTarget;
    let lift = 0;
    if (side.state === "STANDING_SIDE" && Number.isInteger(desired) && Number.isInteger(slack) && slack > 0) {
      lift = Math.min(desired - defaultTarget, slack);
      target = defaultTarget + lift;
      slack -= lift;
    }
    allocations.push({
      leg_identity: side.leg_identity,
      state: side.state,
      default_target_cents: defaultTarget,
      post_onset_session_low_cents: side.post_onset_session_low_cents ?? null,
      desired_depth_target_cents: desired,
      allocated_target_cents: target,
      lift_cents: lift,
      lift_active: lift > 0,
    });
  }
  const knownTargets = allocations.map((row) => row.allocated_target_cents).filter(Number.isInteger);
  const joint = knownTargets.length === 2 ? knownTargets[0] + knownTargets[1] : null;
  if (Number.isInteger(joint) && joint > PAIR_BUDGET_CENTS) throw new Error(`V52s allocation crossed par guard: ${joint}`);
  return {
    law: "V52S_JOINT_BUDGET_INVARIANT_WITH_YIELD_PRIORITY_DEPTH",
    market_tick_cents: MARKET_TICK_CENTS,
    market_tick_role: "KALSHI_INTEGER_TAPE_UNIT_NOT_A_FITTED_CONSTANT",
    pair_budget_cents: PAIR_BUDGET_CENTS,
    seniority: "INCUMBENT_V52L_DEFAULT_TARGETS_SENIOR_DEPTH_LIFTS_JUNIOR",
    deterministic_tie_order: "LEG_IDENTITY_ASCENDING_ONLY_WHEN_BOTH_JUNIOR_LIFTS_COMPETE",
    default_joint_sum_cents: defaultSum,
    slack_before_lifts_cents: Number.isInteger(defaultSum) ? PAIR_BUDGET_CENTS - defaultSum : null,
    slack_after_lifts_cents: slack,
    allocations,
    joint_target_sum_cents: joint,
    invariant_pass: joint === null || joint <= PAIR_BUDGET_CENTS,
  };
}

module.exports = { MARKET_TICK_CENTS, PAIR_BUDGET_CENTS, lawfulCent, desiredDepthTarget, allocate };
