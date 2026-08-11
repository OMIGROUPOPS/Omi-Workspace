#!/usr/bin/env node
"use strict";

// Policy-free reconstruction of deterministic top-five tapes from the sealed
// websocket recorder archive.  This is the Node streaming equivalent of the
// receipted Python materializer; it exists so the 12.2 GB expanded archive can
// be processed off the one-core recorder host without altering policy inputs.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { once } = require("events");

const HEADER = ["ts_et"];
for (let level = 1; level <= 5; level += 1) HEADER.push(`bid_${level}`, `bid_${level}_sz`);
for (let level = 1; level <= 5; level += 1) HEADER.push(`ask_${level}`, `ask_${level}_sz`);
HEADER.push("mid", "bid_depth_5", "ask_depth_5", "depth_ratio", "last_trade");

function parseArgs(argv) {
  const out = {};
  for (let index = 0; index < argv.length; index += 2) {
    if (!argv[index].startsWith("--") || argv[index + 1] === undefined) {
      throw new Error(`invalid argument at ${argv[index] || "<end>"}`);
    }
    out[argv[index].slice(2).replaceAll("-", "_")] = argv[index + 1];
  }
  for (const key of ["registry", "raw_dir", "source_member_list", "output"]) {
    if (!out[key]) throw new Error(`missing --${key.replaceAll("_", "-")}`);
  }
  return out;
}

function sorted(value) {
  if (Array.isArray(value)) return value.map(sorted);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sorted(value[key])]));
  }
  return value;
}

function canonical(value) {
  return `${JSON.stringify(sorted(value), null, 2)}\n`;
}

function compact(value) {
  return JSON.stringify(sorted(value));
}

function shaFile(file) {
  const digest = crypto.createHash("sha256");
  const descriptor = fs.openSync(file, "r");
  const buffer = Buffer.allocUnsafe(1024 * 1024);
  try {
    for (;;) {
      const count = fs.readSync(descriptor, buffer, 0, buffer.length, null);
      if (!count) break;
      digest.update(buffer.subarray(0, count));
    }
  } finally {
    fs.closeSync(descriptor);
  }
  return digest.digest("hex");
}

function cent(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return null;
  const result = Math.round(number < 1 ? number * 100 : number);
  return result >= 0 && result <= 100 ? result : null;
}

function quantity(value) {
  const result = Number(value);
  return Number.isFinite(result) && result > 0 ? result : null;
}

function sourceEpoch(row) {
  const result = Number(row.t);
  return Number.isFinite(result) ? result : null;
}

function timestampEt(epoch) {
  const iso = new Date((epoch - 4 * 3600) * 1000).toISOString();
  const date = iso.slice(0, 10);
  const hour24 = Number(iso.slice(11, 13));
  const hour12 = hour24 % 12 || 12;
  const suffix = hour24 < 12 ? "AM" : "PM";
  return `${date} ${String(hour12).padStart(2, "0")}:${iso.slice(14, 19)} ${suffix}`;
}

function numberCell(value) {
  if (!Number.isFinite(value)) return "";
  if (Number.isInteger(value)) return String(value);
  return Number(value.toPrecision(10)).toString();
}

class TapeWriter {
  constructor(file) {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    this.file = file;
    this.output = fs.createWriteStream(file, { flags: "wx" });
    this.gzip = zlib.createGzip({ level: 9, mtime: 0 });
    this.gzip.pipe(this.output);
    this.gzip.write(`${HEADER.join(",")}\n`);
    this.rows = 0;
  }

  async write(cells) {
    const line = `${cells.map((cell) => cell === null || cell === undefined ? "" : String(cell)).join(",")}\n`;
    this.rows += 1;
    if (!this.gzip.write(line)) await once(this.gzip, "drain");
  }

  async close() {
    this.gzip.end();
    await once(this.output, "close");
  }
}

function loadRegistry(file) {
  const events = fs.readFileSync(file, "utf8").split(/\r?\n/).filter(Boolean).map(JSON.parse);
  const targets = new Set();
  for (const event of events) for (const ticker of event.tickers || []) targets.add(String(ticker));
  return { events, targets };
}

function applyBook(message, books) {
  const kind = message.type;
  const body = message.msg;
  if (!body || typeof body !== "object") return [null, false];
  const ticker = body.market_ticker;
  if (!ticker) return [null, false];
  const snapshot = kind === "orderbook_snapshot";
  if (snapshot) {
    const book = { yes: new Map(), no: new Map() };
    for (const side of ["yes", "no"]) {
      const levels = body[`${side}_dollars_fp`] || body[side] || [];
      for (const level of levels) {
        if (!Array.isArray(level) || level.length < 2) continue;
        const price = cent(level[0]);
        const size = quantity(level[1]);
        if (price !== null && size !== null) book[side].set(price, size);
      }
    }
    books.set(ticker, book);
  } else if (kind === "orderbook_delta") {
    const side = body.side;
    const price = cent(body.price_dollars ?? body.price);
    const delta = Number(body.delta_fp ?? body.delta);
    if (!["yes", "no"].includes(side) || price === null || !Number.isFinite(delta)) return [null, false];
    if (!books.has(ticker)) books.set(ticker, { yes: new Map(), no: new Map() });
    const levels = books.get(ticker)[side];
    const current = (levels.get(price) || 0) + delta;
    if (current > 0) levels.set(price, current);
    else levels.delete(price);
  } else {
    return [null, false];
  }
  return [String(ticker), snapshot];
}

function tapeRow(epoch, book, lastTrade) {
  const bids = [...book.yes].sort((left, right) => right[0] - left[0]).slice(0, 5);
  const asks = [...book.no].map(([price, size]) => [100 - price, size]).sort((left, right) => left[0] - right[0]).slice(0, 5);
  if (!bids.length || !asks.length) return null;
  const cells = [timestampEt(epoch)];
  for (const levels of [bids, asks]) {
    for (let index = 0; index < 5; index += 1) {
      if (index < levels.length) cells.push(levels[index][0], numberCell(levels[index][1]));
      else cells.push("", "");
    }
  }
  const bidDepth = bids.reduce((sum, level) => sum + level[1], 0);
  const askDepth = asks.reduce((sum, level) => sum + level[1], 0);
  const denominator = bidDepth + askDepth;
  cells.push(
    numberCell((bids[0][0] + asks[0][0]) / 2),
    numberCell(bidDepth),
    numberCell(askDepth),
    denominator ? numberCell(bidDepth / denominator) : "",
    lastTrade ?? "",
  );
  return cells;
}

async function processArchive(file, onLine) {
  const source = fs.createReadStream(file).pipe(zlib.createGunzip());
  source.setEncoding("utf8");
  let tail = "";
  for await (const chunk of source) {
    tail += chunk;
    let offset = 0;
    for (;;) {
      const newline = tail.indexOf("\n", offset);
      if (newline < 0) break;
      if (newline > offset) await onLine(tail.slice(offset, newline));
      offset = newline + 1;
    }
    tail = tail.slice(offset);
  }
  if (tail.trim()) await onLine(tail);
}

async function run(args) {
  const registry = path.resolve(args.registry);
  const rawDir = path.resolve(args.raw_dir);
  const memberList = path.resolve(args.source_member_list);
  const output = path.resolve(args.output);
  const tapeDir = path.join(output, "tapes");
  if (fs.existsSync(output)) throw new Error(`output already exists: ${output}`);
  fs.mkdirSync(output, { recursive: true });
  const { events, targets } = loadRegistry(registry);
  const expectedNames = fs.readFileSync(memberList, "utf8").split(/\r?\n/).filter(Boolean).map((value) => path.basename(value));
  const foundNames = fs.readdirSync(rawDir).filter((value) => value.startsWith("ws_") && value.endsWith(".jsonl.gz")).sort();
  if (JSON.stringify(foundNames) !== JSON.stringify(expectedNames)) {
    throw new Error(`filtered raw member conservation failed found=${foundNames.length} expected=${expectedNames.length}`);
  }

  const books = new Map();
  const lastTrade = new Map();
  const writers = new Map();
  const stats = new Map([...targets].sort().map((ticker) => [ticker, {
    ticker,
    snapshot_seen: false,
    first_snapshot_epoch: null,
    first_raw_epoch: null,
    last_raw_epoch: null,
    formed_rows: 0,
    formed_rows_after_snapshot: 0,
    trade_messages: 0,
  }]));
  let rawRows = 0;
  let targetRows = 0;
  let firstArchiveEpoch = null;
  let lastArchiveEpoch = null;

  for (let fileIndex = 0; fileIndex < foundNames.length; fileIndex += 1) {
    const name = foundNames[fileIndex];
    await processArchive(path.join(rawDir, name), async (line) => {
      rawRows += 1;
      const row = JSON.parse(line);
      const epoch = sourceEpoch(row);
      if (epoch !== null) {
        firstArchiveEpoch = firstArchiveEpoch === null ? epoch : Math.min(firstArchiveEpoch, epoch);
        lastArchiveEpoch = lastArchiveEpoch === null ? epoch : Math.max(lastArchiveEpoch, epoch);
      }
      const message = row.m;
      if (!message || typeof message !== "object") return;
      const body = message.msg;
      const tickerValue = body && typeof body === "object" ? body.market_ticker : null;
      if (!targets.has(tickerValue)) return;
      targetRows += 1;
      const ticker = String(tickerValue);
      const stat = stats.get(ticker);
      if (epoch !== null) {
        stat.first_raw_epoch = stat.first_raw_epoch === null ? epoch : Math.min(stat.first_raw_epoch, epoch);
        stat.last_raw_epoch = stat.last_raw_epoch === null ? epoch : Math.max(stat.last_raw_epoch, epoch);
      }
      if (message.type === "trade") {
        const price = cent(body.yes_price_dollars ?? body.yes_price);
        if (price !== null) lastTrade.set(ticker, price);
        stat.trade_messages += 1;
        return;
      }
      const [changed, snapshot] = applyBook(message, books);
      if (changed !== ticker || epoch === null) return;
      if (snapshot) {
        stat.snapshot_seen = true;
        stat.first_snapshot_epoch = stat.first_snapshot_epoch === null ? epoch : Math.min(stat.first_snapshot_epoch, epoch);
      }
      const values = tapeRow(epoch, books.get(ticker), lastTrade.get(ticker));
      if (!values) return;
      if (!writers.has(ticker)) writers.set(ticker, new TapeWriter(path.join(tapeDir, `${ticker}.csv.gz`)));
      await writers.get(ticker).write(values);
      stat.formed_rows += 1;
      if (stat.snapshot_seen) stat.formed_rows_after_snapshot += 1;
    });
    process.stdout.write(`${compact({ stage: "archive", index: fileIndex + 1, total: foundNames.length, name, raw_rows: rawRows, target_rows: targetRows })}\n`);
  }

  await Promise.all([...writers.values()].map((writer) => writer.close()));
  const tickerRows = [];
  for (const ticker of [...targets].sort()) {
    const tape = path.join(tapeDir, `${ticker}.csv.gz`);
    const row = stats.get(ticker);
    tickerRows.push({
      ...row,
      tape_exists: fs.existsSync(tape),
      tape_sha256: fs.existsSync(tape) ? shaFile(tape) : null,
      tape_bytes: fs.existsSync(tape) ? fs.statSync(tape).size : 0,
      authoritative_from_snapshot: Boolean(row.snapshot_seen && row.formed_rows_after_snapshot > 0),
    });
  }
  const manifest = {
    schema_version: "window1-v47-exam-capture-materialization-v1-node-streaming",
    policy_invocations: 0,
    score_rows: 0,
    registry: { path: registry, sha256: shaFile(registry), events: events.length, tickers: targets.size },
    raw_archive: {
      directory: rawDir,
      files: foundNames.length,
      raw_rows: rawRows,
      target_rows: targetRows,
      first_epoch: firstArchiveEpoch,
      last_epoch: lastArchiveEpoch,
      first_file: foundNames[0],
      last_file: foundNames.at(-1),
      source_member_list_sha256: shaFile(memberList),
      source_member_list_bytes: fs.statSync(memberList).size,
    },
    tickers: tickerRows,
    admission_note: "Only formed rows after an observed retained-archive snapshot are authoritative; delta-only prefixes are excluded.",
  };
  fs.writeFileSync(path.join(output, "CAPTURE_MATERIALIZATION_MANIFEST.json"), canonical(manifest));
  fs.writeFileSync(path.join(output, "CAPTURE_MATERIALIZATION_TICKERS.jsonl"), `${tickerRows.map(compact).join("\n")}\n`);
  process.stdout.write(`${compact({ registry_events: events.length, tickers: targets.size, authoritative: tickerRows.filter((row) => row.authoritative_from_snapshot).length, raw_rows: rawRows, target_rows: targetRows })}\n`);
}

run(parseArgs(process.argv.slice(2))).catch((error) => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exitCode = 1;
});
