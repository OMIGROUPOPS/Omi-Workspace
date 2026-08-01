#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");

const DWELL_SECONDS = 10;
const REQUIRED_QUANTITY = 5;
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function integer(value) { const number = Number(value); return Number.isInteger(number) ? number : null; }
function positive(value) { const number = Number(value); return Number.isFinite(number) && number > 0 ? number : null; }

function parseEt(value) {
  const m = value.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!m) throw new Error(`bad tick timestamp ${value}`);
  let hour = Number(m[4]); if (m[7] === "AM" && hour === 12) hour = 0; if (m[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(hour).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}

async function scanOne(source, ticksRoot) {
  const file = path.join(ticksRoot, `${source.ticker}.csv.gz`);
  const stat = fs.statSync(file), hash = crypto.createHash("sha256"), input = fs.createReadStream(file);
  input.on("data", (chunk) => hash.update(chunk));
  const lines = readline.createInterface({ input: input.pipe(zlib.createGunzip()), crlfDelay: Infinity });
  let headers = null, sourceRow = 1, last = null, best = null, malformedRows = 0;
  const since = Array(100).fill(null), left = Number(source.left_ts), right = Number(source.right_ts);
  const inspect = (book, evidenceTs, endpoint = false) => {
    if (!Number.isInteger(book.bid) || !Number.isInteger(book.ask) || book.bid <= 0 || book.ask > 99 || book.bid > book.ask) return;
    for (let limit = 1; limit < book.ask; limit += 1) since[limit] = null;
    for (let limit = book.ask; limit <= 99; limit += 1) if (since[limit] === null) since[limit] = book.ts;
    let cumulative = 0, levelIndex = 0;
    for (let limit = book.ask; limit <= 99; limit += 1) {
      while (levelIndex < book.asks.length && book.asks[levelIndex][0] <= limit) cumulative += book.asks[levelIndex++][1];
      if (cumulative < REQUIRED_QUANTITY || evidenceTs - since[limit] < DWELL_SECONDS) continue;
      if (!best || limit < best.limit_cents || (limit === best.limit_cents && evidenceTs < best.evidence_ts)) best = { limit_cents: limit, evidence_ts: evidenceTs, dwell_seconds: evidenceTs - since[limit], displayed_capacity: cumulative, top_five_asks: book.asks, source_receipt: `${path.basename(file)}#row-${book.sourceRow}${endpoint ? "; right-endpoint-carry" : ""}` };
      break;
    }
  };
  for await (const line of lines) {
    sourceRow += 1;
    if (!headers) { headers = line.replace(/\r$/, "").split(","); sourceRow = 1; continue; }
    const values = line.replace(/\r$/, "").split(",");
    if (values.length !== headers.length) { malformedRows += 1; continue; }
    const get = (name) => values[headers.indexOf(name)];
    const ts = parseEt(get("ts_et")); if (ts < left || ts > right) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bid = integer(get(`bid_${level}`)), bidSize = positive(get(`bid_${level}_sz`)), ask = integer(get(`ask_${level}`)), askSize = positive(get(`ask_${level}_sz`));
      if (bid !== null && bidSize !== null) bids.push([bid, bidSize]); if (ask !== null && askSize !== null) asks.push([ask, askSize]);
    }
    asks.sort((a, b) => a[0] - b[0]);
    const book = { ts, bid: bids.length ? Math.max(...bids.map((row) => row[0])) : null, ask: asks.length ? asks[0][0] : null, asks, sourceRow };
    inspect(book, ts); last = book;
  }
  if (last && last.ts < right) inspect(last, right, true);
  return { event_id: source.event_id, leg_id: source.leg, ticker: source.ticker, category: source.category, window1_open_cents: integer(source.window1_open_cents), window1_close_cents: integer(source.window1_close_cents), ask_reachable_low_10s_cents: integer(source.quote_10s_floor_limit_cents), capacity_proven_floor: best, malformed_source_rows_rejected: malformedRows, source: { file: path.basename(file), bytes: stat.size, sha256: hash.digest("hex") } };
}

async function workerMain() {
  const rows = [];
  for (const source of workerData.sources) rows.push(await scanOne(source, workerData.ticksRoot));
  parentPort.postMessage(rows);
}

async function main() {
  const args = process.argv.slice(2), value = (name, fallback = null) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : fallback; };
  const repo = path.resolve(value("--repo", "."));
  const privateRoot = path.resolve(value("--private-root", "C:/Users/omigr/OMI-Window1-private"));
  const output = path.resolve(value("--output"));
  const workerCount = Number(value("--workers", "8"));
  const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
  const raw = fs.readFileSync(quotePath, "utf8").trimEnd().split(/\r?\n/), headers = raw.shift().split(",");
  const sources = raw.map((line) => Object.fromEntries(line.split(",").map((entry, index) => [headers[index], entry])));
  const buckets = Array.from({ length: workerCount }, () => []); sources.forEach((source, index) => buckets[index % workerCount].push(source));
  const workers = buckets.map((bucket) => new Promise((resolve, reject) => {
    const worker = new Worker(__filename, { workerData: { sources: bucket, ticksRoot: path.join(privateRoot, "fit-local/ticks") } });
    worker.once("message", resolve); worker.once("error", reject); worker.once("exit", (code) => { if (code !== 0) reject(new Error(`capacity worker exit ${code}`)); });
  }));
  const rows = (await Promise.all(workers)).flat().sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_id.localeCompare(b.leg_id));
  const result = { schema_version: "WINDOW1_ASK_CAPACITY_FLOOR_SCAN_V1", law: { side: "ASK_ONLY", dwell_seconds: DWELL_SECONDS, required_displayed_contracts: REQUIRED_QUANTITY }, source_quote_ledger: { path: path.relative(repo, quotePath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(quotePath)) }, row_count: rows.length, rows };
  fs.mkdirSync(path.dirname(output), { recursive: true }); fs.writeFileSync(output, canonical(result));
  process.stdout.write(canonical({ status: "BUILT", rows: rows.length, sha256: sha256(Buffer.from(canonical(result))) }));
}

if (isMainThread) main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; }); else workerMain().catch((error) => { throw error; });
