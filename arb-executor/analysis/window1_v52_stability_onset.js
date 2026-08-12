"use strict";

// V52 uses the neutral two-segment least-squares split documented by the
// 9eff493b stability-onset receipt.  It does not tune a threshold: each
// candidate is the arithmetic argmin of within-segment SSE.  Candidate A is
// valid only when both spread and cross-leg mid-sum deviation decrease after
// their splits.  Candidate B is valid only when trailing trade cadence rises.

const GRID_SECONDS = 60;
const TRADE_CADENCE_SECONDS = 3600;

function mean(values) {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function neutralTwoSegmentSplit(rows, field) {
  const values = rows.map((row) => row[field]);
  let best = null;
  for (let index = 1; index < values.length; index += 1) {
    const before = values.slice(0, index).filter(Number.isFinite);
    const after = values.slice(index).filter(Number.isFinite);
    if (!before.length || !after.length) continue;
    const beforeMean = mean(before), afterMean = mean(after);
    const sse = before.reduce((sum, value) => sum + (value - beforeMean) ** 2, 0)
      + after.reduce((sum, value) => sum + (value - afterMean) ** 2, 0);
    if (!best || sse < best.sse) {
      best = {
        field,
        index,
        shift_timestamp_epoch: rows[index].timestamp_epoch,
        before_mean: beforeMean,
        after_mean: afterMean,
        sse,
        before_n: before.length,
        after_n: after.length,
      };
    }
  }
  return best;
}

function latestAtOrBefore(rows, cursor, timestamp) {
  while (cursor.index + 1 < rows.length && rows[cursor.index + 1].ts <= timestamp) {
    cursor.index += 1;
  }
  return cursor.index >= 0 ? rows[cursor.index] : null;
}

function trailingPrintCount(rows, cursor, timestamp) {
  while (cursor.right < rows.length && rows[cursor.right].ts <= timestamp) cursor.right += 1;
  while (cursor.left < cursor.right && rows[cursor.left].ts < timestamp - TRADE_CADENCE_SECONDS) cursor.left += 1;
  return cursor.right - cursor.left;
}

function buildTrajectories(base, tapes, prints) {
  const ids = Object.keys(base.legs).sort();
  if (ids.length !== 2) throw new Error(`V52 onset requires paired event ${base.event_id}`);
  const bookCursors = new Map(ids.map((id) => [id, { index: -1 }]));
  const printCursors = new Map(ids.map((id) => [id, { left: 0, right: 0 }]));
  const rowsByLeg = new Map(ids.map((id) => [id, []]));
  for (let timestamp = base.left; timestamp <= base.right; timestamp += GRID_SECONDS) {
    const books = new Map();
    for (const id of ids) books.set(id, latestAtOrBefore(tapes.get(id), bookCursors.get(id), timestamp));
    const mids = ids.map((id) => {
      const book = books.get(id);
      return book && Number.isInteger(book.bid) && Number.isInteger(book.ask) ? (book.bid + book.ask) / 2 : null;
    });
    const midsumAbsDev = mids.every(Number.isFinite) ? Math.abs(mids[0] + mids[1] - 100) : null;
    for (const id of ids) {
      const book = books.get(id);
      if (!book) continue;
      rowsByLeg.get(id).push({
        timestamp_epoch: timestamp,
        spread: Number.isFinite(book.spread) ? book.spread : null,
        midsum_abs_dev: midsumAbsDev,
        trades_60min: trailingPrintCount(prints.get(id), printCursors.get(id), timestamp),
      });
    }
  }
  return rowsByLeg;
}

function computeLegOnset(rows) {
  const spread = neutralTwoSegmentSplit(rows, "spread");
  const midsum = neutralTwoSegmentSplit(rows, "midsum_abs_dev");
  const tradeCadence = neutralTwoSegmentSplit(rows, "trades_60min");
  const candidateAValid = Boolean(spread && midsum
    && spread.after_mean < spread.before_mean
    && midsum.after_mean < midsum.before_mean);
  const candidateA = candidateAValid ? {
    candidate: "A_SPREAD_COLLAPSE_PLUS_CROSS_LEG_MIDSUM_SETTLE",
    timestamp_epoch: Math.max(spread.shift_timestamp_epoch, midsum.shift_timestamp_epoch),
    components: { spread, midsum },
  } : null;
  const candidateBValid = Boolean(tradeCadence && tradeCadence.after_mean > tradeCadence.before_mean);
  const candidateB = candidateBValid ? {
    candidate: "B_SUSTAINED_TRADE_CADENCE_ARRIVAL",
    timestamp_epoch: tradeCadence.shift_timestamp_epoch,
    components: { trade_cadence: tradeCadence },
  } : null;
  const valid = [candidateA, candidateB].filter(Boolean).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.candidate.localeCompare(b.candidate));
  return {
    selected: valid[0] ?? null,
    candidates: { A: candidateA, B: candidateB },
    rejected: {
      A: candidateAValid ? null : "SPREAD_AND_MIDSUM_DID_NOT_BOTH_SETTLE",
      B: candidateBValid ? null : "TRADE_CADENCE_DID_NOT_INCREASE",
    },
    trajectory_rows: rows.length,
  };
}

function computeEventOnsets(base, tapes, prints) {
  const trajectories = buildTrajectories(base, tapes, prints);
  return Object.fromEntries([...trajectories].map(([id, rows]) => [id, computeLegOnset(rows)]));
}

module.exports = {
  GRID_SECONDS,
  TRADE_CADENCE_SECONDS,
  neutralTwoSegmentSplit,
  buildTrajectories,
  computeLegOnset,
  computeEventOnsets,
};
