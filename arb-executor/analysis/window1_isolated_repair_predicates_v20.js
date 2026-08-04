"use strict";

function finiteInteger(name, value) {
  if (!Number.isFinite(value) || !Number.isInteger(value)) {
    throw new Error(`${name} must be a finite integer`);
  }
  return value;
}

function evaluateAnchorFreshnessA({
  currentAsk,
  observedLow,
  toleranceCents,
  freshOwnBookReceipt,
}) {
  finiteInteger("currentAsk", currentAsk);
  finiteInteger("observedLow", observedLow);
  finiteInteger("toleranceCents", toleranceCents);
  if (toleranceCents < 0) throw new Error("toleranceCents must be non-negative");
  const gapCents = currentAsk - observedLow;
  if (!freshOwnBookReceipt) {
    return {
      placeable: false,
      reason: "NO_FRESH_OWN_BOOK_RECEIPT",
      gap_cents: gapCents,
    };
  }
  if (gapCents > toleranceCents) {
    return {
      placeable: false,
      reason: "CURRENT_ASK_OUTSIDE_REARMED_OBSERVED_LOW_ANCHOR",
      gap_cents: gapCents,
    };
  }
  return {
    placeable: true,
    reason: gapCents === 0
      ? "CURRENT_ASK_AT_OBSERVED_LOW"
      : "CURRENT_ASK_WITHIN_REARMED_OBSERVED_LOW_ANCHOR",
    gap_cents: gapCents,
  };
}

function advanceLowerSettlementC({
  priorRefusal,
  currentAsk,
  observedLow,
  timestamp,
  receiptId,
  dwellSeconds,
  displayedAskSize,
  requiredDwellSeconds,
  requiredQuantity,
  freshOwnBookReceipt,
  upperLevelsResolved,
}) {
  finiteInteger("currentAsk", currentAsk);
  finiteInteger("observedLow", observedLow);
  finiteInteger("dwellSeconds", dwellSeconds);
  finiteInteger("displayedAskSize", displayedAskSize);
  finiteInteger("requiredDwellSeconds", requiredDwellSeconds);
  finiteInteger("requiredQuantity", requiredQuantity);
  if (!Number.isFinite(timestamp)) throw new Error("timestamp must be finite");
  const supportQualified = freshOwnBookReceipt
    && upperLevelsResolved
    && dwellSeconds >= requiredDwellSeconds
    && displayedAskSize >= requiredQuantity;
  if (!priorRefusal) {
    if (!supportQualified || currentAsk !== observedLow) return { anchor: null, settled: false, reason: "LOWER_SETTLEMENT_SUPPORT_NOT_ESTABLISHED" };
    return {
      anchor: {
        refused_ask: currentAsk,
        timestamp,
        receipt_id: receiptId,
      },
      settled: false,
      reason: "LOWER_REFUSAL_ANCHOR_ESTABLISHED",
    };
  }
  if (currentAsk < priorRefusal.refused_ask) {
    if (!supportQualified || currentAsk !== observedLow) return { anchor: priorRefusal, settled: false, reason: "LOWER_SETTLEMENT_SUPPORT_NOT_ESTABLISHED" };
    return {
      anchor: {
        refused_ask: currentAsk,
        timestamp,
        receipt_id: receiptId,
      },
      settled: false,
      reason: "LOWER_REFUSAL_ANCHOR_MOVED_DOWN",
    };
  }
  if (!supportQualified) {
    return {
      anchor: priorRefusal,
      settled: false,
      reason: "LOWER_SETTLEMENT_SUPPORT_NOT_ESTABLISHED",
    };
  }
  const strictlyLater = timestamp > priorRefusal.timestamp
    || (timestamp === priorRefusal.timestamp && receiptId !== priorRefusal.receipt_id);
  if (!strictlyLater) {
    return {
      anchor: priorRefusal,
      settled: false,
      reason: "LOWER_SETTLEMENT_REQUIRES_LATER_RECEIPT",
    };
  }
  return {
    anchor: priorRefusal,
    settled: true,
    reason: "LOWER_VERDICT_SETTLED_BY_LATER_QUALIFIED_ASK_AT_OR_ABOVE_REFUSAL",
    settlement: {
      refusal_receipt_id: priorRefusal.receipt_id,
      refusal_timestamp: priorRefusal.timestamp,
      refused_ask: priorRefusal.refused_ask,
      settlement_receipt_id: receiptId,
      settlement_timestamp: timestamp,
      settlement_ask: currentAsk,
      dwell_seconds: dwellSeconds,
      displayed_ask_size: displayedAskSize,
    },
  };
}

module.exports = {
  evaluateAnchorFreshnessA,
  advanceLowerSettlementC,
};
