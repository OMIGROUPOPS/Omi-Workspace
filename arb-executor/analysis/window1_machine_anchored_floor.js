"use strict";

const QUALIFYING_ASK_DWELL_SECONDS = 10;
const QUALIFYING_ASK_SIZE_CONTRACTS = 5;

function lawfulCent(value) {
  return Number.isInteger(value) && value >= 1 && value <= 99;
}

function transitionKind(kind) {
  if (["PLACE_REST", "REPRICE_REST", "GAP_CREDIT_REPRICE_DOWN", "PAIR_CAP_REPRICE"].includes(kind)) return "OPEN";
  if (["CANCEL_REST", "PAIR_CAP_CANCEL"].includes(kind)) return "CLOSE";
  if (kind === "FILL") return "FILL";
  return null;
}

function buildStandingIntervals(actions, rightEdge) {
  const sorted = [...actions].sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || (a.trace_ordinal ?? 0) - (b.trace_ordinal ?? 0));
  const intervals = [];
  let active = null;
  function close(row, reason) {
    if (!active) return;
    intervals.push({ ...active, end_timestamp_epoch: row?.timestamp_epoch ?? rightEdge, end_receipt: row?.receipt ?? null, end_reason: reason });
    active = null;
  }
  for (const row of sorted) {
    const transition = transitionKind(row.kind);
    if (!transition) continue;
    if (transition === "OPEN") {
      if (!lawfulCent(row.target_cents)) throw new Error(`unlawful standing target ${row.leg_identity} ${row.kind} ${row.target_cents}`);
      close(row, "REPLACED_BY_NEW_REST");
      active = { target_cents: row.target_cents, start_timestamp_epoch: row.timestamp_epoch, start_receipt: row.receipt, start_kind: row.kind, start_reason: row.reason ?? null };
    } else if (transition === "CLOSE") close(row, row.kind);
    else if (transition === "FILL") close(row, "FILL");
  }
  if (active) close(null, "WINDOW_RIGHT_EDGE");
  return intervals.filter((row) => Number.isFinite(row.start_timestamp_epoch) && Number.isFinite(row.end_timestamp_epoch) && row.end_timestamp_epoch >= row.start_timestamp_epoch);
}

function intervalAt(intervals, timestamp) {
  return intervals.find((row) => timestamp > row.start_timestamp_epoch && timestamp <= row.end_timestamp_epoch) ?? null;
}

function makeIntervalCursor(intervals) {
  let index = 0;
  return (timestamp) => {
    while (index < intervals.length && timestamp > intervals[index].end_timestamp_epoch) index += 1;
    const row = intervals[index];
    return row && timestamp > row.start_timestamp_epoch && timestamp <= row.end_timestamp_epoch ? row : null;
  };
}

function qualifyingAsk(row) {
  return row?.kind === "BOOK"
    && lawfulCent(row.ask)
    && Number.isFinite(row.ask_dwell_seconds)
    && row.ask_dwell_seconds >= QUALIFYING_ASK_DWELL_SECONDS
    && Number.isFinite(row.top_ask_size)
    && row.top_ask_size >= QUALIFYING_ASK_SIZE_CONTRACTS;
}

function evidenceFloor(intervals, books, prints) {
  let trade = null;
  let quote = null;
  let marketTrade = null;
  const tradeInterval = makeIntervalCursor(intervals), quoteInterval = makeIntervalCursor(intervals);
  for (const row of prints) {
    if (!lawfulCent(row.price)) continue;
    if (!marketTrade || row.price < marketTrade.price_cents || (row.price === marketTrade.price_cents && row.ts < marketTrade.timestamp_epoch)) {
      marketTrade = { price_cents: row.price, timestamp_epoch: row.ts, receipt: row.receipt, trade_id: row.trade_id, size: row.size, taker_side: row.taker_side };
    }
    const interval = tradeInterval(row.ts);
    if (!interval || row.price > interval.target_cents) continue;
    if (!trade || row.price < trade.price_cents || (row.price === trade.price_cents && row.ts < trade.timestamp_epoch)) {
      trade = { price_cents: row.price, timestamp_epoch: row.ts, receipt: row.receipt, trade_id: row.trade_id, size: row.size, taker_side: row.taker_side, standing_target_cents: interval.target_cents, standing_start_timestamp_epoch: interval.start_timestamp_epoch, standing_start_receipt: interval.start_receipt };
    }
  }
  for (const row of books) {
    if (!qualifyingAsk(row)) continue;
    const interval = quoteInterval(row.ts);
    if (!interval || row.ask > interval.target_cents) continue;
    if (!quote || row.ask < quote.price_cents || (row.ask === quote.price_cents && row.ts < quote.timestamp_epoch)) {
      quote = { price_cents: row.ask, timestamp_epoch: row.ts, receipt: row.receipt, ask_dwell_seconds: row.ask_dwell_seconds, displayed_size: row.top_ask_size, bid_cents: row.bid, spread_cents: row.spread, standing_target_cents: interval.target_cents, standing_start_timestamp_epoch: interval.start_timestamp_epoch, standing_start_receipt: interval.start_receipt };
    }
  }
  const candidates = [trade && { channel: "TRUE_TRADE_WHILE_REST_STOOD", ...trade }, quote && { channel: "QUALIFYING_ASK_WHILE_REST_STOOD", ...quote }].filter(Boolean);
  candidates.sort((a, b) => a.price_cents - b.price_cents || a.timestamp_epoch - b.timestamp_epoch || a.channel.localeCompare(b.channel));
  return { machine_floor: candidates[0] ?? null, machine_trade_floor: trade, machine_quote_floor: quote, market_offered_trade_floor: marketTrade };
}

function percentile(values, q) {
  const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
  return sorted.length ? sorted[Math.max(0, Math.ceil(q * sorted.length) - 1)] : null;
}

function distribution(values) {
  const finite = values.filter(Number.isFinite);
  return { n: finite.length, null_n: values.length - finite.length, sum: finite.reduce((a, b) => a + b, 0), min: finite.length ? Math.min(...finite) : null, p25: percentile(finite, .25), median: percentile(finite, .5), p75: percentile(finite, .75), p90: percentile(finite, .9), max: finite.length ? Math.max(...finite) : null };
}

module.exports = { QUALIFYING_ASK_DWELL_SECONDS, QUALIFYING_ASK_SIZE_CONTRACTS, lawfulCent, transitionKind, buildStandingIntervals, intervalAt, makeIntervalCursor, qualifyingAsk, evidenceFloor, percentile, distribution };
