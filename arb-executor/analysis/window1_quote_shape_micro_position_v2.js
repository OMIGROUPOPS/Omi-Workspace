#!/usr/bin/env node
"use strict";

// Narrow V2 micro-position seam. This module does not select a shape, target,
// price, or fill. It only recognizes what proves that the current own ask has
// been observed at a causally later receipt.

function directionObserved(leg, direction) {
  if (!leg?.last || !leg.last.ask_change_after_first_timestamp) return false;
  const net = leg.last.prefix.ask_net;
  return direction === "UP" ? net > 0 : direction === "DOWN" ? net < 0 : direction === "FLAT" ? net === 0 : false;
}

function inverseDirection(direction) {
  return direction === "UP" ? "DOWN" : direction === "DOWN" ? "UP" : direction;
}

function evaluateMicroPositionEvidence({ leg, sibling, dwellSeconds }) {
  if (!Number.isFinite(dwellSeconds) || dwellSeconds < 0) throw new Error("invalid dwellSeconds");
  const transitioned = Boolean(leg?.last?.ask_change_after_first_timestamp);
  const stableSamePriceReceipt = Boolean(
    leg?.last?.strictly_later_same_price_ask_receipt
      && Number.isFinite(leg.last.ask_dwell_seconds)
      && leg.last.ask_dwell_seconds >= dwellSeconds
      && Number.isFinite(leg.last.top_ask_size)
      && leg.last.top_ask_size > 0
  );
  const inverseSiblingResolved = Boolean(
    leg?.resolved_direction
      && sibling?.independent_direction
      && inverseDirection(leg.resolved_direction) === sibling.independent_direction
      && directionObserved(sibling, sibling.independent_direction)
  );
  return {
    own_micro_position_observed: transitioned || stableSamePriceReceipt,
    evidence_type: transitioned ? "ASK_PRICE_TRANSITION" : stableSamePriceReceipt ? "STRICTLY_LATER_SAME_PRICE_ASK_RECEIPT" : null,
    stable_same_price_receipt: stableSamePriceReceipt,
    inverse_sibling_resolved: inverseSiblingResolved,
  };
}

module.exports = { evaluateMicroPositionEvidence };
