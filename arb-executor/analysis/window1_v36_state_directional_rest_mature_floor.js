"use strict";

const v35 = require("./window1_v35_living_rest_evidence_gate.js");
const v32 = require("./window1_v32_no_chase_state_machine.js");

function stateDirectionalRestTarget({ state, bid, activeTarget = null, pairCap = null }) {
  if (!["FALLING", "RISING", "SETTLED"].includes(state)) throw new Error("valid state required");
  if (state === "FALLING") {
    return v32.fallingRestTarget({ bid, previousTarget: activeTarget, pairCap });
  }
  return v35.livingRestTarget({ bid, pairCap });
}

function matureFloorTakePermission({
  book,
  pairCap = null,
  activeEvidenceFloor = null,
  floorFirstFlickerLive = false,
  floorMature = false,
}) {
  const incumbent = v35.evidenceTakePermission({
    book,
    pairCap,
    activeEvidenceFloor,
    floorFirstFlickerLive,
  });
  if (!incumbent.permitted) return incumbent;
  if (!floorMature) {
    return {
      permitted: false,
      reason: "ACTIVE_EVIDENCE_FLOOR_NOT_MATURE_NEW_LOW_INSIDE_TRAILING_HORIZON",
    };
  }
  return {
    permitted: true,
    reason: "MATURE_EVIDENCE_FLOOR_NO_NEW_LOW_INSIDE_TRAILING_HORIZON",
  };
}

function matureDirectionalEvidenceFloor({
  state,
  runningEvidenceFloor = null,
  receiptLocalEvidenceFloor = null,
  reformedQualifyingAskFloor = null,
  reformedQualifyingAskAuthority = false,
  floorMature = false,
}) {
  if (!["FALLING", "RISING", "SETTLED"].includes(state)) throw new Error("valid state required");
  if (state === "FALLING") return Number.isInteger(runningEvidenceFloor) ? runningEvidenceFloor : null;
  if (Number.isInteger(receiptLocalEvidenceFloor)) return receiptLocalEvidenceFloor;
  if (floorMature && reformedQualifyingAskAuthority && Number.isInteger(reformedQualifyingAskFloor)) {
    return reformedQualifyingAskFloor;
  }
  return Number.isInteger(runningEvidenceFloor) ? runningEvidenceFloor : null;
}

function decide({
  state,
  book,
  activeTarget = null,
  pairCap = null,
  activeEvidenceFloor = null,
  floorFirstFlickerLive = false,
  floorMature = false,
}) {
  if (!["FALLING", "RISING", "SETTLED"].includes(state)) throw new Error("valid state required");
  const restTarget = stateDirectionalRestTarget({
    state,
    bid: book.bid,
    activeTarget,
    pairCap,
  });
  if (activeTarget === null) {
    return {
      action: restTarget === null ? "HOLD_REST" : "PLACE_REST",
      target_cents: restTarget,
      reason: restTarget === null
        ? "NO_LAWFUL_ONE_CENT_UNDER_BID_TARGET"
        : state === "FALLING"
          ? "FIRST_TWO_SIDED_BOOK_FALLING_NO_CHASE_REST_ONE_CENT_UNDER_BID"
          : "FIRST_TWO_SIDED_BOOK_LIVING_REST_ONE_CENT_UNDER_BID",
      take_permission: null,
    };
  }
  const take = matureFloorTakePermission({
    book,
    pairCap,
    activeEvidenceFloor,
    floorFirstFlickerLive,
    floorMature,
  });
  if (take.permitted) {
    return {
      action: "TAKE",
      target_cents: book.ask,
      reason: "MATURE_EVIDENCE_FLOOR_TAKE",
      take_permission: take,
    };
  }
  if (restTarget === null) {
    return {
      action: "CANCEL_REST",
      target_cents: null,
      reason: "NO_LAWFUL_ONE_CENT_UNDER_BID_OR_PAIR_CAP_LEVEL",
      take_permission: take,
    };
  }
  if (restTarget !== activeTarget) {
    return {
      action: "REPRICE_REST",
      target_cents: restTarget,
      direction: restTarget > activeTarget ? "UP" : "DOWN",
      reason: state === "FALLING"
        ? "FALLING_REST_ONE_CENT_UNDER_BEST_BID_NO_UPWARD_CHASE"
        : "LIVING_REST_REANCHOR_EVERY_BOOK_RECEIPT",
      take_permission: take,
    };
  }
  return {
    action: "HOLD_REST",
    target_cents: activeTarget,
    reason: take.reason,
    take_permission: take,
  };
}

module.exports = {
  ...v35,
  stateDirectionalRestTarget,
  matureDirectionalEvidenceFloor,
  matureFloorTakePermission,
  decide,
};
