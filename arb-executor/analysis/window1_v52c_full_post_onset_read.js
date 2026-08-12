"use strict";

// V52c changes exactly V52b clause 2. The read consumes every post-onset
// exchange print and book receipt available at evaluation time. Recency is
// expressed by causal receipt rank, so every observation retains positive
// weight and no replacement wall-clock horizon or tuning constant exists.

const v52b = require("./window1_v52b_read_level_authority.js");

function normalizedClauses(value = {}) {
  const clauses = v52b.normalizedClauses(value);
  return value.full_post_onset_evidence_horizon ? { ...clauses, full_post_onset_evidence_horizon: true } : clauses;
}

function emptyReadState(onsetTimestampEpoch) {
  return {
    onset_timestamp_epoch: onsetTimestampEpoch,
    evidence_receipts: 0,
    book_receipts: 0,
    print_receipts: 0,
    comparable_book_transitions: 0,
    comparable_print_transitions: 0,
    cross_source_comparisons: 0,
    rising_weighted_cents: 0,
    falling_weighted_cents: 0,
    first_evidence: null,
    last_evidence: null,
    last_directional_evidence: null,
    last_book: null,
    last_print: null,
  };
}

function finiteCent(value) { return Number.isInteger(value) && value >= 0 && value <= 100; }

function addDirection(state, direction, magnitude, row, rank, kind) {
  if (!(magnitude > 0)) return;
  const weighted = magnitude * rank;
  if (direction === "RISING") state.rising_weighted_cents += weighted;
  else if (direction === "FALLING") state.falling_weighted_cents += weighted;
  else return;
  state.last_directional_evidence = { timestamp_epoch: row.ts, receipt: row.receipt, kind, direction, magnitude_cents: magnitude, causal_rank: rank, rank_weighted_cents: weighted };
}

function observePostOnsetEvidence(state, row) {
  if (!state || !Number.isFinite(state.onset_timestamp_epoch)) throw new Error("post-onset read state requires onset");
  if (!row || !Number.isFinite(row.ts) || row.ts < state.onset_timestamp_epoch) return state;
  if (!['BOOK', 'PRINT'].includes(row.kind)) throw new Error(`unsupported post-onset evidence ${row.kind}`);
  const rank = state.evidence_receipts + 1;
  const evidence = { timestamp_epoch: row.ts, receipt: row.receipt, kind: row.kind, causal_rank: rank };
  state.evidence_receipts = rank;
  state.first_evidence ||= evidence;
  state.last_evidence = evidence;
  if (row.kind === "BOOK") {
    state.book_receipts += 1;
    if (state.last_book) {
      state.comparable_book_transitions += 1;
      for (const [field, current, prior] of [["BID", row.bid, state.last_book.bid], ["ASK", row.ask, state.last_book.ask]]) {
        if (!finiteCent(current) || !finiteCent(prior)) continue;
        const delta = current - prior;
        addDirection(state, delta > 0 ? "RISING" : "FALLING", Math.abs(delta), row, rank, `POST_ONSET_${field}_${delta > 0 ? "UP" : "DOWN"}`);
      }
    }
    state.last_book = { timestamp_epoch: row.ts, receipt: row.receipt, bid: row.bid, ask: row.ask, spread: row.spread, bid_dwell_seconds: row.bid_dwell_seconds, ask_dwell_seconds: row.ask_dwell_seconds, top_bid_size: row.top_bid_size, top_ask_size: row.top_ask_size, depth_ratio: row.depth_ratio };
    return state;
  }
  state.print_receipts += 1;
  if (state.last_print && finiteCent(row.price) && finiteCent(state.last_print.price)) {
    state.comparable_print_transitions += 1;
    const delta = row.price - state.last_print.price;
    addDirection(state, delta > 0 ? "RISING" : "FALLING", Math.abs(delta), row, rank, `POST_ONSET_PRINT_${delta > 0 ? "UP" : "DOWN"}`);
  } else if (state.last_book && finiteCent(row.price)) {
    state.cross_source_comparisons += 1;
    if (row.price <= state.last_book.bid) addDirection(state, "FALLING", Math.max(1, state.last_book.bid - row.price), row, rank, "POST_ONSET_PRINT_AT_OR_BELOW_BID");
    else if (row.price >= state.last_book.ask) addDirection(state, "RISING", Math.max(1, row.price - state.last_book.ask), row, rank, "POST_ONSET_PRINT_AT_OR_ABOVE_ASK");
  }
  state.last_print = { timestamp_epoch: row.ts, receipt: row.receipt, price: row.price, size: row.size, trade_id: row.trade_id };
  return state;
}

function fullPostOnsetRead(state, evaluationRow) {
  if (!state || !evaluationRow || !Number.isFinite(evaluationRow.ts)) throw new Error("read state and evaluation receipt required");
  const comparable = state.comparable_book_transitions + state.comparable_print_transitions + state.cross_source_comparisons;
  const support = comparable > 0;
  const stateName = !support ? "SETTLED" : state.rising_weighted_cents > state.falling_weighted_cents ? "RISING" : state.falling_weighted_cents > state.rising_weighted_cents ? "FALLING" : "SETTLED";
  const span = state.first_evidence ? evaluationRow.ts - state.first_evidence.timestamp_epoch : null;
  return {
    state: stateName,
    receipt: support ? evaluationRow.receipt : null,
    evidence: support ? "FULL_POST_ONSET_PRINT_AND_BOOK_HISTORY_RECENCY_WEIGHTED_BY_CAUSAL_RANK" : "POST_ONSET_EVIDENCE_GENUINELY_INSUFFICIENT_NO_COMPARABLE_TRANSITION",
    full_post_onset_evidence: {
      sufficient: support,
      onset_timestamp_epoch: state.onset_timestamp_epoch,
      evaluation_timestamp_epoch: evaluationRow.ts,
      evaluation_receipt: evaluationRow.receipt,
      first_evidence: state.first_evidence,
      last_evidence: state.last_evidence,
      last_directional_evidence: state.last_directional_evidence,
      span_seconds: span,
      consulted: {
        evidence_receipts: state.evidence_receipts,
        book_receipts: state.book_receipts,
        print_receipts: state.print_receipts,
        comparable_book_transitions: state.comparable_book_transitions,
        comparable_print_transitions: state.comparable_print_transitions,
        cross_source_comparisons: state.cross_source_comparisons,
      },
      weighted_scores_cents: { rising: state.rising_weighted_cents, falling: state.falling_weighted_cents },
      weighting_law: "CAUSAL_RECEIPT_RANK_1_THROUGH_N; ALL_POST_ONSET_EVIDENCE_RETAINS_POSITIVE_WEIGHT; NO_TIME_CUTOFF",
      insufficiency_law: "READ_ABSENT_ONLY_UNTIL_A_CAUSAL_TRANSITION_OR_PRINT_TO_BOOK_COMPARISON_EXISTS",
      fixed_horizon_seconds: null,
      replacement_tuning_constant: null,
    },
  };
}

function fullPostOnsetAuthority(combined) {
  if (!combined || typeof combined !== "object") throw new Error("combined state required");
  if (combined.disagreement) return "FULL_POST_ONSET_HISTORY_VS_JUL6_PRESSURE_DISAGREE";
  if (combined.authority === "QUOTE_PATH_AND_JUL6_PRESSURE_AGREE") return "FULL_POST_ONSET_HISTORY_AND_JUL6_PRESSURE_AGREE";
  return "FULL_POST_ONSET_HISTORY_PRIMARY";
}

module.exports = { ...v52b, normalizedClauses, emptyReadState, observePostOnsetEvidence, fullPostOnsetRead, fullPostOnsetAuthority };
