"use strict";

// Recorder book rows are stamped at whole-second grain while exchange prints
// carry their true fractional exchange time.  The recorder's last_trade field
// supplies the causal watermark inside each second: book rows before a
// last-trade transition precede that print; the first row carrying the new
// last-trade value follows the matching exchange receipt.  This is an input
// ordering repair only.  It neither invents a price nor changes policy.

function kindRank(row) { return row.kind === "PRINT" ? 0 : row.kind === "BOOK" ? 1 : 2; }
function sourceIndex(row) {
  if (Number.isInteger(row.source_row_index)) return row.source_row_index;
  const match = String(row.receipt ?? "").match(/#row-(\d+)$/);
  return match ? Number(match[1]) : Number.MAX_SAFE_INTEGER;
}
function sourceTimestamp(row) {
  return Number.isFinite(row.source_timestamp_epoch) ? row.source_timestamp_epoch : row.timestamp_epoch;
}
function compareCausalRows(a, b) {
  return a.timestamp_epoch - b.timestamp_epoch
    || kindRank(a) - kindRank(b)
    || sourceIndex(a) - sourceIndex(b)
    || String(a.receipt).localeCompare(String(b.receipt));
}
function compareLegacyRows(a, b) {
  const rank = (row) => row.kind === "BOOK" ? 0 : row.kind === "PRINT" ? 1 : 2;
  return sourceTimestamp(a) - sourceTimestamp(b)
    || rank(a) - rank(b)
    || String(a.receipt).localeCompare(String(b.receipt));
}

function assignBookTimesForLeg(rows) {
  const result = [];
  const bySecond = new Map();
  for (const row of rows) {
    const sourceEpoch = sourceTimestamp(row);
    const second = Math.floor(sourceEpoch);
    if (!bySecond.has(second)) bySecond.set(second, []);
    bySecond.get(second).push({ ...row, source_timestamp_epoch: sourceEpoch });
  }
  let priorLastTrade = null;
  for (const [second, secondRows] of [...bySecond.entries()].sort((a, b) => a[0] - b[0])) {
    const prints = secondRows.filter((row) => row.kind === "PRINT")
      .sort((a, b) => sourceTimestamp(a) - sourceTimestamp(b) || String(a.receipt).localeCompare(String(b.receipt)));
    const books = secondRows.filter((row) => row.kind === "BOOK")
      .sort((a, b) => sourceIndex(a) - sourceIndex(b) || String(a.receipt).localeCompare(String(b.receipt)));
    result.push(...prints.map((row) => ({
      ...row,
      timestamp_epoch: sourceTimestamp(row),
      causal_clock: {
        source_timestamp_epoch: sourceTimestamp(row),
        effective_timestamp_epoch: sourceTimestamp(row),
        relation: "TRUE_FRACTIONAL_EXCHANGE_PRINT",
        matched_print_receipt: row.receipt,
      },
    })));
    let printWatermarkIndex = -1;
    let offsetWithinWatermark = 0;
    books.forEach((row, bookIndex) => {
      const lastTrade = Number.isInteger(row.last_trade_cents) && row.last_trade_cents > 0 ? row.last_trade_cents : null;
      let relation = "SOURCE_SEQUENCE_BEFORE_FIRST_LOCAL_PRINT";
      let matchedPrint = null;
      if (lastTrade !== null && lastTrade !== priorLastTrade) {
        const matchIndex = prints.findIndex((print, index) => index > printWatermarkIndex && print.price_cents === lastTrade);
        if (matchIndex >= 0) {
          printWatermarkIndex = matchIndex;
          offsetWithinWatermark = 0;
          matchedPrint = prints[matchIndex];
          relation = "AFTER_MATCHED_TRUE_PRINT_LAST_TRADE_TRANSITION";
        } else {
          relation = "SOURCE_SEQUENCE_LAST_TRADE_CHANGE_WITHOUT_LOCAL_PRINT";
        }
        priorLastTrade = lastTrade;
      } else if (printWatermarkIndex >= 0) {
        matchedPrint = prints[printWatermarkIndex];
        relation = "AFTER_CURRENT_TRUE_PRINT_WATERMARK";
      }
      offsetWithinWatermark += 1;
      // One microsecond preserves recorder row order without crossing any
      // independently timestamped exchange receipt in the named tape.
      const effective = matchedPrint
        ? sourceTimestamp(matchedPrint) + offsetWithinWatermark / 1_000_000
        : second + (bookIndex + 1) / 1_000_000;
      result.push({
        ...row,
        timestamp_epoch: effective,
        causal_clock: {
          source_timestamp_epoch: sourceTimestamp(row),
          effective_timestamp_epoch: effective,
          relation,
          matched_print_receipt: matchedPrint?.receipt ?? null,
          source_row_index: sourceIndex(row),
          local_print_count: prints.length,
        },
      });
    });
  }
  return result;
}

function materializeCausalClock(rows) {
  const byLeg = new Map();
  for (const row of rows) {
    if (!byLeg.has(row.leg_id)) byLeg.set(row.leg_id, []);
    byLeg.get(row.leg_id).push(row);
  }
  return [...byLeg.values()].flatMap(assignBookTimesForLeg).sort(compareCausalRows);
}

module.exports = {
  compareCausalRows,
  compareLegacyRows,
  materializeCausalClock,
};
