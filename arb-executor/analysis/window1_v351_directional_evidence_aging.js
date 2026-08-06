"use strict";

const v35 = require("./window1_v35_living_rest_evidence_gate.js");

function livingRestTarget({ bid, pairCap = null }) {
  if (!Number.isInteger(bid)) throw new Error("bid integer required");
  let target = bid - 1;
  if (Number.isInteger(pairCap)) target = Math.min(target, pairCap);
  return v35.lawfulCent(target) ? target : null;
}

function displayedAskHasEvidenceCapacity(book) {
  return Number.isInteger(book?.bid) && Number.isInteger(book?.ask) &&
    Number.isFinite(book.ask_dwell_seconds) && book.ask_dwell_seconds >= v35.QUALIFIED_DWELL_MIN_SECONDS &&
    Number.isFinite(book.top_ask_size) && book.top_ask_size >= v35.QUALIFIED_SIZE_MIN;
}

function qualifyingAskEvidence(book) {
  if (!displayedAskHasEvidenceCapacity(book)) return false;
  if (book.bid >= book.ask) return true;
  return Number.isInteger(book.spread) && book.spread >= 0 && book.spread <= v35.QUALIFIED_SPREAD_MAX_CENTS;
}

function directionallyAgedEvidenceFloor({ state, runningEvidenceFloor = null, receiptLocalEvidenceFloor = null, reformedQualifyingAskFloor = null, qualifyingAskFloorReformedNow = false }) {
  if (!["FALLING", "RISING", "SETTLED"].includes(state)) throw new Error("valid state required");
  if (state === "FALLING" && v35.lawfulCent(runningEvidenceFloor)) return runningEvidenceFloor;
  if (v35.lawfulCent(receiptLocalEvidenceFloor)) return receiptLocalEvidenceFloor;
  if (state !== "FALLING" && v35.lawfulCent(reformedQualifyingAskFloor)) {
    if (!v35.lawfulCent(runningEvidenceFloor) || runningEvidenceFloor >= reformedQualifyingAskFloor) return reformedQualifyingAskFloor;
    if (qualifyingAskFloorReformedNow) return reformedQualifyingAskFloor;
    return runningEvidenceFloor;
  }
  return null;
}

function evidenceTakePermission({ book, pairCap = null, activeEvidenceFloor = null, floorFirstFlickerLive = false }) {
  if (!displayedAskHasEvidenceCapacity(book)) {
    return { permitted: false, reason: "DISPLAYED_ASK_NOT_DWELL_AND_FIVE_LOT_QUALIFIED" };
  }
  if (Number.isInteger(pairCap) && book.ask > pairCap) {
    return { permitted: false, reason: "DISPLAYED_ASK_ABOVE_PAIR_CAP" };
  }
  if (!v35.lawfulCent(activeEvidenceFloor)) {
    return { permitted: false, reason: "NO_ACTIVE_DISCOUNT_EVIDENCE_FLOOR" };
  }
  if (book.ask > activeEvidenceFloor) {
    return { permitted: false, reason: "UNABSORBED_DOWNWARD_EVIDENCE_ASK_ABOVE_FLOOR" };
  }
  if (floorFirstFlickerLive) {
    return { permitted: false, reason: "CURRENT_ASK_CREATED_FLOOR_WHILE_DOWNWARD_SEQUENCE_UNABSORBED" };
  }
  return { permitted: true, reason: "ASK_AT_OR_BELOW_ACTIVE_EVIDENCE_FLOOR" };
}

function decide({ state, book, activeTarget = null, pairCap = null, activeEvidenceFloor = null, floorFirstFlickerLive = false }) {
  if (!["FALLING", "RISING", "SETTLED"].includes(state)) throw new Error("valid state required");
  const restTarget = livingRestTarget({ bid: book.bid, pairCap });
  if (activeTarget === null) {
    return {
      action: restTarget === null ? "HOLD_REST" : "PLACE_REST",
      target_cents: restTarget,
      reason: restTarget === null ? "NO_LAWFUL_ONE_CENT_UNDER_BID_TARGET" : "FIRST_TWO_SIDED_BOOK_LIVING_REST_ONE_CENT_UNDER_BID",
      take_permission: null,
    };
  }
  const take = evidenceTakePermission({ book, pairCap, activeEvidenceFloor, floorFirstFlickerLive });
  if (take.permitted) {
    return {
      action: "TAKE",
      target_cents: book.ask,
      reason: "EVIDENCE_FLOOR_TAKE_STATE_LABEL_IGNORED",
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
  if (restTarget !== null && restTarget !== activeTarget) {
    return {
      action: "REPRICE_REST",
      target_cents: restTarget,
      direction: restTarget > activeTarget ? "UP" : "DOWN",
      reason: "LIVING_REST_REANCHOR_EVERY_BOOK_RECEIPT",
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
  livingRestTarget,
  displayedAskHasEvidenceCapacity,
  qualifyingAskEvidence,
  directionallyAgedEvidenceFloor,
  evidenceTakePermission,
  decide,
};
