#!/usr/bin/env node
"use strict";

// A stable same-price ask is not self-authenticating. It may sign only when
// contemporaneous, already-observed evidence shows that it is more than the
// first posted price. No count, elapsed-time, or fitted threshold is added.

function evaluateStableAskSigningSupport({ leg, sibling, inverseSiblingResolved }) {
  const atInitialLevelWithoutDescent = Boolean(
    leg?.last?.prefix?.ask_net === 0
      && leg.last.prefix.ask_dip === 0
  );
  if (!atInitialLevelWithoutDescent) {
    return { required: false, supported: true, support_type: "DEMONSTRATED_ASK_DESCENT" };
  }
  const persistentTopAskSize = leg?.last?.top_ask_size_ever_changed === false;
  const pulseBeyondSpread = leg?.resolved_direction === "UP"
    && Number.isFinite(leg?.last?.ask_peak_cents)
    && Number.isFinite(leg?.last?.confirmation_spread_cents)
    && leg.last.ask_peak_cents > leg.last.confirmation_spread_cents;
  const siblingDirection = sibling?.resolved_direction;
  const siblingNet = sibling?.last?.prefix?.ask_net;
  const siblingMovedInResolvedDirection = (siblingDirection === "UP" && siblingNet > 0)
    || (siblingDirection === "DOWN" && siblingNet < 0);
  const inverseSiblingTransition = Boolean(
    inverseSiblingResolved
      && sibling?.last?.ask_change_after_first_timestamp
      && siblingMovedInResolvedDirection
  );
  return {
    required: true,
    supported: persistentTopAskSize || pulseBeyondSpread || inverseSiblingTransition,
    support_type: persistentTopAskSize
      ? "TOP_ASK_PRICE_AND_SIZE_PERSISTED"
      : pulseBeyondSpread
        ? "ASK_PULSE_EXCEEDED_SPREAD_AND_RETURNED"
        : inverseSiblingTransition
        ? "RESOLVED_INVERSE_SIBLING_HAS_ASK_TRANSITION"
        : null,
    predicates: {
      top_ask_price_and_size_persisted: persistentTopAskSize,
      ask_pulse_exceeded_spread_and_returned: pulseBeyondSpread,
      resolved_inverse_sibling_has_ask_transition: inverseSiblingTransition,
    },
  };
}

module.exports = { evaluateStableAskSigningSupport };
