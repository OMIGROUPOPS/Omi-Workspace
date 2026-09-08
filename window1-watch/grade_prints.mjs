// Stream the existing custody print tape once. Read-only; never use book last as a print.
import fs from "node:fs";
import readline from "node:readline";
import crypto from "node:crypto";

export async function readGradePrints(file, games) {
  const tickers = new Map(games.flatMap((g) => g.legs.map((leg) => [`${g.event}-${leg}`, { event: g.event, leg }])));
  const events = Object.fromEntries(games.map((g) => [g.event, { legs: Object.fromEntries(g.legs.map((l) => [l, []])) }]));
  const input = fs.createReadStream(file), digest = crypto.createHash("sha256");
  input.on("data", (bytes) => digest.update(bytes));
  const before = fs.statSync(file);
  let sourceRows = 0, accepted = 0, duplicates = 0, invalid = 0;
  const seen = new Map();
  for await (const line of readline.createInterface({ input, crlfDelay: Infinity })) {
    if (!line) continue;
    sourceRows++;
    const row = JSON.parse(line), target = tickers.get(row.ticker);
    if (!target) continue;
    const epoch = Date.parse(row.exchange_ts) / 1000;
    if (row.true_print !== true || !Number.isFinite(row.price_cents) ||
        !Number.isFinite(row.size) || row.size <= 0 || !Number.isFinite(epoch) || !(row.receipt_id ?? row.trade_id)) {
      invalid++; continue;
    }
    const receipt = row.receipt_id ?? row.trade_id, key = `${row.ticker}:${receipt}`;
    const signature = JSON.stringify([epoch, row.price_cents, row.size]);
    if (seen.has(key)) {
      if (seen.get(key) !== signature) throw new Error(`Conflicting custody print identity ${key}`);
      duplicates++; continue;
    }
    seen.set(key, signature);
    events[target.event].legs[target.leg].push({
      epoch, price: row.price_cents, receipt, source_row: sourceRows,
    });
    accepted++;
  }
  const after = fs.statSync(file);
  if (before.size !== after.size || before.mtimeMs !== after.mtimeMs) throw new Error("Custody print source changed during grading");
  const provenance = {
    path: file, sha256: digest.digest("hex"), bytes: after.size, source_rows: sourceRows,
    selected_rows: accepted, duplicate_receipt_rows: duplicates, invalid_selected_rows: invalid,
    rule: "Existing fit-local/prints.jsonl: true_print=true, finite price/time, positive size, receipt_id or trade_id. Duplicate identities per ticker are counted once; conflicting duplicates fail. exchange_ts uses the existing replay Date.parse millisecond clock; equal timestamps retain file order. No book last, interpolation, or synthetic print.",
  };
  for (const value of Object.values(events)) {
    for (const rows of Object.values(value.legs)) rows.sort((a, b) => a.epoch - b.epoch || a.source_row - b.source_row);
    value.provenance = { ...provenance, leg_rows: Object.fromEntries(Object.entries(value.legs).map(([l, rows]) => [l, rows.length])) };
  }
  return events;
}
