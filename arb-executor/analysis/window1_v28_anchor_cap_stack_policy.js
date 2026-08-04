"use strict";

// V28 is deliberately only the ratified Fix-1 stream plus the isolated
// Fix-2 cap re-arm.  The inherited 10-second/five-contract micro-micro law
// remains authoritative; this module adds no numeric parameter.
const {
  DWELL_SECONDS,
  QUANTITY,
  qualifiedAsk,
  findCapRearm,
} = require("./window1_v23_isolated_rearm_policies_v27.js");

function capFromTrace(traceRow) {
  const values = traceRow?.first_flag?.values_compared;
  const cap = values?.pair_cap_v23?.pair_cap_cents ?? values?.pair_cap_cents ?? values?.cap_cents ?? values?.pair_cap;
  if (!Number.isInteger(cap)) throw new Error(`missing integer pair cap for ${traceRow?.leg_identity || "UNKNOWN"}`);
  return cap;
}

function capRearmReceipt(traceRow, rows) {
  if (traceRow?.first_flag?.layer !== "PLACEMENT_CAP") throw new Error("cap re-arm requires PLACEMENT_CAP first flag");
  const cap = capFromTrace(traceRow);
  const afterTs = traceRow.first_flag.timestamp?.epoch;
  if (!Number.isFinite(afterTs)) throw new Error("cap re-arm requires finite flag timestamp");
  const row = findCapRearm(rows, { afterTs, capCents: cap });
  return {
    leg_identity: traceRow.leg_identity,
    original_flag_timestamp_epoch: afterTs,
    cap_cents: cap,
    cap_formula: "99 - already_credited_sibling_fill_cents",
    abstention_is_state_not_terminal: true,
    no_chase: true,
    rearm: row ? {
      receipt: row.receipt,
      timestamp_epoch: row.ts,
      bid: row.bid,
      ask: row.ask,
      spread: row.spread,
      ask_dwell_seconds: row.ask_dwell_seconds,
      top_ask_size: row.top_ask_size,
    } : null,
    outcome: row ? "CAP_REARMED_ON_QUALIFYING_ASK_AT_OR_BELOW_CAP" : "NO_QUALIFYING_RETURN_TO_CAP",
  };
}

module.exports = {
  DWELL_SECONDS,
  QUANTITY,
  qualifiedAsk,
  findCapRearm,
  capFromTrace,
  capRearmReceipt,
};
