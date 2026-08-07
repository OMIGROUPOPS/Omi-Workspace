"use strict";

// Exact bounded-memory pattern used by the V32/V35/V36 builders: encode one
// JSONL row at a time and pipeline it through deterministic gzip to disk.
const fs = require("fs");
const stream = require("stream/promises");
const zlib = require("zlib");

async function writeGzipRowsFile(file, rows) {
  async function* encodedRows() {
    for await (const row of rows) yield `${JSON.stringify(row)}\n`;
  }
  await stream.pipeline(
    encodedRows(),
    zlib.createGzip({ level: 9, mtime: 0 }),
    fs.createWriteStream(file),
  );
}

module.exports = { writeGzipRowsFile };
