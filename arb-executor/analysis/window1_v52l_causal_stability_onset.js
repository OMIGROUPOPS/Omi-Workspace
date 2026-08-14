"use strict";

// V52l replaces only clause 1.  It preserves the two V52 onset candidates but
// recognizes them online: each prefix is evaluated using receipts at or before
// that prefix's evaluation timestamp.  The first prefix that supports a
// candidate fixes the recognition time.  base.right is deliberately unread.

const GRID_SECONDS = 60;
const TRADE_CADENCE_SECONDS = 3600;

function ensure(value, message) { if (!value) throw new Error(message); }
function finite(value) { return Number.isFinite(value); }

function neutralTwoSegmentSplit(rows, field) {
  const values = rows.map((row) => finite(row[field]) ? row[field] : null);
  const prefixN = [0], prefixSum = [0], prefixSq = [0];
  for (const value of values) {
    prefixN.push(prefixN.at(-1) + (value === null ? 0 : 1));
    prefixSum.push(prefixSum.at(-1) + (value === null ? 0 : value));
    prefixSq.push(prefixSq.at(-1) + (value === null ? 0 : value * value));
  }
  const totalN = prefixN.at(-1), totalSum = prefixSum.at(-1), totalSq = prefixSq.at(-1);
  let best = null;
  for (let index = 1; index < values.length; index += 1) {
    const beforeN = prefixN[index], afterN = totalN - beforeN;
    if (!beforeN || !afterN) continue;
    const beforeSum = prefixSum[index], afterSum = totalSum - beforeSum;
    const beforeMean = beforeSum / beforeN, afterMean = afterSum / afterN;
    const beforeSse = prefixSq[index] - beforeSum * beforeSum / beforeN;
    const afterSse = totalSq - prefixSq[index] - afterSum * afterSum / afterN;
    const sse = Math.max(0, beforeSse) + Math.max(0, afterSse);
    if (!best || sse < best.sse) best = { field, index, shift_timestamp_epoch: rows[index].timestamp_epoch, before_mean: beforeMean, after_mean: afterMean, sse, before_n: beforeN, after_n: afterN };
  }
  return best;
}

function candidateFromPrefix(rows) {
  const spread = neutralTwoSegmentSplit(rows, "spread");
  const midsum = neutralTwoSegmentSplit(rows, "midsum_abs_dev");
  const tradeCadence = neutralTwoSegmentSplit(rows, "trades_60min");
  const candidateAValid = Boolean(spread && midsum && spread.after_mean < spread.before_mean && midsum.after_mean < midsum.before_mean);
  const candidateBValid = Boolean(tradeCadence && tradeCadence.after_mean > tradeCadence.before_mean);
  const candidateA = candidateAValid ? { candidate: "A_SPREAD_COLLAPSE_PLUS_CROSS_LEG_MIDSUM_SETTLE", inferred_shift_timestamp_epoch: Math.max(spread.shift_timestamp_epoch, midsum.shift_timestamp_epoch), components: { spread, midsum } } : null;
  const candidateB = candidateBValid ? { candidate: "B_SUSTAINED_TRADE_CADENCE_ARRIVAL", inferred_shift_timestamp_epoch: tradeCadence.shift_timestamp_epoch, components: { trade_cadence: tradeCadence } } : null;
  return { candidates: { A: candidateA, B: candidateB }, rejected: { A: candidateAValid ? null : "SPREAD_AND_MIDSUM_DID_NOT_BOTH_SETTLE_ON_AVAILABLE_PREFIX", B: candidateBValid ? null : "TRADE_CADENCE_DID_NOT_INCREASE_ON_AVAILABLE_PREFIX" } };
}

function latestAtOrBefore(rows, cursor, timestamp) {
  while (cursor.index + 1 < rows.length && rows[cursor.index + 1].ts <= timestamp) cursor.index += 1;
  return cursor.index >= 0 ? rows[cursor.index] : null;
}

function trailingPrintCount(rows, cursor, timestamp) {
  while (cursor.right < rows.length && rows[cursor.right].ts <= timestamp) cursor.right += 1;
  while (cursor.left < cursor.right && rows[cursor.left].ts < timestamp - TRADE_CADENCE_SECONDS) cursor.left += 1;
  return cursor.right - cursor.left;
}

function computeEventOnsets(base, tapes, prints) {
  const ids = Object.keys(base.legs).sort();
  ensure(ids.length === 2, `V52l onset requires paired event ${base.event_id}`);
  const allRows = ids.flatMap((id) => [...(tapes.get(id) || []), ...(prints.get(id) || [])]);
  const sourceEnd = allRows.reduce((max, row) => finite(row.ts) ? Math.max(max, row.ts) : max, base.left);
  const bookCursors = new Map(ids.map((id) => [id, { index: -1 }]));
  const printCursors = new Map(ids.map((id) => [id, { left: 0, right: 0 }]));
  const trajectories = new Map(ids.map((id) => [id, []]));
  const results = new Map(ids.map((id) => [id, null]));
  for (let timestamp = base.left; timestamp <= sourceEnd && [...results.values()].some((row) => row === null); timestamp += GRID_SECONDS) {
    const books = new Map(ids.map((id) => [id, latestAtOrBefore(tapes.get(id) || [], bookCursors.get(id), timestamp)]));
    const mids = ids.map((id) => { const book = books.get(id); return book && Number.isInteger(book.bid) && Number.isInteger(book.ask) ? (book.bid + book.ask) / 2 : null; });
    const midsumAbsDev = mids.every(finite) ? Math.abs(mids[0] + mids[1] - 100) : null;
    for (const id of ids) {
      if (results.get(id)) continue;
      const book = books.get(id);
      if (!book) continue;
      const trajectory = trajectories.get(id);
      trajectory.push({ timestamp_epoch: timestamp, spread: finite(book.spread) ? book.spread : null, midsum_abs_dev: midsumAbsDev, trades_60min: trailingPrintCount(prints.get(id) || [], printCursors.get(id), timestamp) });
      if (trajectory.length < 2) continue;
      const evaluated = candidateFromPrefix(trajectory);
      const valid = Object.values(evaluated.candidates).filter(Boolean).sort((a, b) => a.inferred_shift_timestamp_epoch - b.inferred_shift_timestamp_epoch || a.candidate.localeCompare(b.candidate));
      if (!valid.length) continue;
      const selected = { ...valid[0], timestamp_epoch: timestamp, causal_recognition_timestamp_epoch: timestamp };
      results.set(id, { selected, candidates: evaluated.candidates, rejected: evaluated.rejected, trajectory_rows: trajectory.length, causal_prefix_receipt_law: "EVERY_VALUE_FROM_RECEIPTS_AT_OR_BEFORE_CAUSAL_RECOGNITION", maximum_consumed_timestamp_epoch: timestamp, right_edge_consumed: false, full_span_fit: false });
    }
  }
  return Object.fromEntries(ids.map((id) => [id, results.get(id) ?? { selected: null, candidates: { A: null, B: null }, rejected: { A: "NO_CAUSAL_PREFIX_SUPPORTED_A", B: "NO_CAUSAL_PREFIX_SUPPORTED_B" }, trajectory_rows: trajectories.get(id).length, causal_prefix_receipt_law: "EVERY_VALUE_FROM_RECEIPTS_AT_OR_BEFORE_EACH_EVALUATION", maximum_consumed_timestamp_epoch: trajectories.get(id).at(-1)?.timestamp_epoch ?? null, right_edge_consumed: false, full_span_fit: false }]));
}

function assertRightEdgeIndependence(base, tapes, prints) {
  const variants = [base.right, base.right - 86400, base.right + 86400].map((right) => computeEventOnsets({ ...base, right }, tapes, prints));
  const canonical = (value) => JSON.stringify(value);
  ensure(variants.every((value) => canonical(value) === canonical(variants[0])), `right-edge independence failed ${base.event_id}`);
  return { event_id: base.event_id, perturbations_seconds: [0, -86400, 86400], pass: true, identical_onsets: true };
}

module.exports = { GRID_SECONDS, TRADE_CADENCE_SECONDS, neutralTwoSegmentSplit, candidateFromPrefix, computeEventOnsets, assertRightEdgeIndependence };
