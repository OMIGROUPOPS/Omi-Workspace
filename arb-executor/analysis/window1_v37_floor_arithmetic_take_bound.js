"use strict";

const v36 = require("./window1_v36_state_directional_rest_mature_floor.js");

function floorArithmeticTakeBound({ entryCents, otherRunningPrintBackedFloor = null }) {
  if (!Number.isInteger(entryCents)) throw new Error("integer entryCents required");
  if (entryCents < 1 || entryCents > 99) throw new Error("lawful entryCents required");
  if (otherRunningPrintBackedFloor !== null && !Number.isInteger(otherRunningPrintBackedFloor)) {
    throw new Error("otherRunningPrintBackedFloor must be integer or null");
  }
  const otherExpressionUnderParBudget = 100 - entryCents;
  if (otherRunningPrintBackedFloor === null) {
    return {
      authority: false,
      permitted: true,
      reason: "OTHER_EXPRESSION_RUNNING_PRINT_BACKED_FLOOR_NOT_YET_BOUND_V36_UNCHANGED",
      entry_cents: entryCents,
      other_expression_under_par_budget_cents: otherExpressionUnderParBudget,
      other_expression_running_print_backed_floor_cents: null,
      comparison: null,
    };
  }
  const permitted = otherExpressionUnderParBudget > otherRunningPrintBackedFloor;
  return {
    authority: true,
    permitted,
    reason: permitted
      ? "FLOOR_ARITHMETIC_LEAVES_STRICT_UNDER_PAR_ROOM"
      : "TAKE_FORBIDDEN_OTHER_EXPRESSION_CANNOT_COMPLETE_STRICTLY_UNDER_PAR_AT_RUNNING_PRINT_BACKED_FLOOR",
    entry_cents: entryCents,
    other_expression_under_par_budget_cents: otherExpressionUnderParBudget,
    other_expression_running_print_backed_floor_cents: otherRunningPrintBackedFloor,
    comparison: `${otherExpressionUnderParBudget} > ${otherRunningPrintBackedFloor}`,
  };
}

function decide(args) {
  const incumbent = v36.decide(args);
  if (incumbent.action !== "TAKE") return incumbent;
  const bound = floorArithmeticTakeBound({
    entryCents: incumbent.target_cents,
    otherRunningPrintBackedFloor: args.otherRunningPrintBackedFloor ?? null,
  });
  if (bound.permitted) {
    return {
      ...incumbent,
      floor_arithmetic_take_bound: bound,
    };
  }
  if (!Number.isInteger(args.activeTarget)) throw new Error("forbidden take requires incumbent resting target");
  const incumbentWithoutTake = v36.decide({ ...args, floorMature: false });
  if (incumbentWithoutTake.action === "TAKE") throw new Error("V36 no-take fallback unexpectedly took");
  return {
    ...incumbentWithoutTake,
    reason: incumbentWithoutTake.action === "HOLD_REST" ? bound.reason : incumbentWithoutTake.reason,
    floor_arithmetic_take_bound: bound,
    incumbent_v36_take: {
      action: incumbent.action,
      target_cents: incumbent.target_cents,
      reason: incumbent.reason,
    },
  };
}

module.exports = {
  ...v36,
  floorArithmeticTakeBound,
  decide,
};
