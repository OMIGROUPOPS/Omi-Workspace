"use strict";

const QUANTITY = 5;
const DWELL_SECONDS = 10;

function exactCent(value, name) {
  if (!Number.isInteger(value) || value < 1 || value > 99) throw new Error(`${name} must be an integer cent in [1,99]`);
  return value;
}

function pairCapDecision({ firstFillCents, originalSecondBidCents, liveBidCents, liveAskCents }) {
  const first = exactCent(firstFillCents, "firstFillCents");
  const original = exactCent(originalSecondBidCents, "originalSecondBidCents");
  const bid = exactCent(liveBidCents, "liveBidCents");
  const ask = exactCent(liveAskCents, "liveAskCents");
  if (bid > ask) throw new Error("crossed live book");
  const cap = 99 - first;
  if (cap < 1) return { state: "ABSTAIN", reason: "PAIR_CAP_BELOW_ONE_CENT", cap_cents: cap, selected_bid_cents: null };
  if (original <= cap) return { state: "UNCHANGED", reason: "ORIGINAL_LEG2_BID_ALREADY_STRICTLY_UNDER_PAR", cap_cents: cap, selected_bid_cents: original };
  if (cap < bid) return { state: "ABSTAIN", reason: "PAIR_CAP_BELOW_CURRENT_LIVE_BID_UNREACHABLE_WITHOUT_CHASING", cap_cents: cap, selected_bid_cents: null };
  if (cap >= ask) throw new Error("binding pair cap unexpectedly crosses live ask");
  return { state: "PLACE", reason: "PAIR_CAP_AT_OR_ABOVE_LIVE_BID_MAKER_RESTING_NO_CHASE", cap_cents: cap, selected_bid_cents: cap };
}

function capacityAtOrBelow(row, target) {
  if (!Array.isArray(row.asks)) return 0;
  return row.asks.filter(([price]) => price <= target).reduce((sum, [, size]) => sum + size, 0);
}

function findStrictlyLaterReach(rows, { actionTs, targetCents, actionReceipt }) {
  let episodeAsk = null;
  let episodeStart = null;
  for (const row of rows) {
    if (episodeAsk === null || row.ask !== episodeAsk) {
      episodeAsk = row.ask;
      episodeStart = row.ts;
    }
    const dwell = row.ts - episodeStart;
    const capacity = capacityAtOrBelow(row, targetCents);
    if (row.ts > actionTs && row.receipt !== actionReceipt && row.ask <= targetCents && dwell >= DWELL_SECONDS && capacity >= QUANTITY) {
      return {
        evidence_ts: row.ts,
        evidence_receipt: row.receipt,
        ask_cents: row.ask,
        ask_dwell_seconds: dwell,
        displayed_capacity_at_or_below_target: capacity,
      };
    }
  }
  return null;
}

module.exports = { QUANTITY, DWELL_SECONDS, pairCapDecision, findStrictlyLaterReach };
